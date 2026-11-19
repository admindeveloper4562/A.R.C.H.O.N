import importlib.util
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest


def load_watchdog():
    path = Path(__file__).resolve().parents[1] / "tools" / "astra_watchdog.py"
    spec = importlib.util.spec_from_file_location("archon_astra_watchdog", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WatchdogTests(unittest.TestCase):
    def test_rollback_is_fenced_and_durable_pending_without_pointer(self):
        watchdog = load_watchdog()
        with tempfile.TemporaryDirectory() as root:
            state = Path(root) / "state"
            repo = Path(root) / "repo"
            state.mkdir()
            repo.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "develop", str(repo)], check=True)
            (repo / "README.md").write_text("checkpoint\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run([
                "git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@local.invalid",
                "commit", "-qm", "checkpoint",
            ], check=True)
            head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            db_path = state / "sda.sqlite3"
            with sqlite3.connect(db_path) as db:
                db.executescript("""
                    CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                    CREATE TABLE upgrade_batches(batch_id TEXT PRIMARY KEY,state TEXT,candidate_sha TEXT,rollback_sha TEXT,updated_at TEXT,created_at TEXT);
                    CREATE TABLE upgrade_rollbacks(rollback_id TEXT PRIMARY KEY,batch_id TEXT,state TEXT,rollback_sha TEXT,current_head TEXT,backup_path TEXT,backup_sha TEXT,created_at TEXT);
                """)
                db.executemany("INSERT INTO settings VALUES (?,?)", [
                    ("integration_path", str(repo)), ("integration_sha", head), ("schema_version", "3"),
                ])
                db.execute("INSERT INTO upgrade_batches VALUES (?,?,?,?,?,?)",
                           ("upgrade-1", "HEALTH_SOAK", head, head, "1", "1"))
            result = watchdog.rollback(state, "upgrade-1")
            self.assertEqual(result["state"], "ROLLBACK_PENDING")
            self.assertTrue(result["rollback_commit_verified"])
            self.assertTrue(Path(result["backup_path"]).is_file())
            with sqlite3.connect(db_path) as db:
                self.assertEqual(db.execute("SELECT state FROM upgrade_batches").fetchone()[0], "ROLLBACK_PENDING")
                self.assertEqual(db.execute("SELECT state FROM upgrade_rollbacks").fetchone()[0], "ROLLBACK_PENDING")

    def test_activation_fast_forwards_and_records_verified_receipt(self):
        watchdog = load_watchdog()
        with tempfile.TemporaryDirectory() as root:
            state = Path(root) / "state"
            repo = Path(root) / "repo"
            state.mkdir()
            repo.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "develop", str(repo)], check=True)
            (repo / "README.md").write_text("checkpoint\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run([
                "git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@local.invalid",
                "commit", "-qm", "checkpoint",
            ], check=True)
            previous = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            (repo / "README.md").write_text("activated\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run([
                "git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@local.invalid",
                "commit", "-qm", "candidate",
            ], check=True)
            candidate = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            subprocess.run(["git", "-C", str(repo), "reset", "--keep", previous], check=True)
            db_path = state / "sda.sqlite3"
            with sqlite3.connect(db_path) as db:
                db.executescript("""
                    CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                    CREATE TABLE tasks(id TEXT PRIMARY KEY,status TEXT NOT NULL);
                    CREATE TABLE upgrade_batches(batch_id TEXT PRIMARY KEY,state TEXT,candidate_sha TEXT,rollback_sha TEXT,updated_at TEXT,created_at TEXT);
                    CREATE TABLE upgrade_checks(batch_id TEXT,stage TEXT,result TEXT,artifact_sha TEXT,evidence_sha TEXT,recorded_at TEXT,verifier TEXT,PRIMARY KEY(batch_id,stage));
                """)
                db.executemany("INSERT INTO settings VALUES (?,?)", [
                    ("integration_path", str(repo)), ("integration_sha", previous), ("schema_version", "5"),
                ])
                db.execute("INSERT INTO upgrade_batches VALUES (?,?,?,?,?,?)",
                           ("upgrade-1", "HEALTH_SOAK", candidate, previous, "1", "1"))
                db.execute("INSERT INTO tasks VALUES (?,?)", ("pending-merge", "approved"))
                db.executemany("INSERT INTO upgrade_checks VALUES (?,?,?,?,?,?,?)",
                               (("upgrade-1", stage, "PASS", candidate if stage in {"TESTED", "CANARY"} else previous,
                                 "e" * 64, "1", "deterministic_controller")
                                for stage in ("TESTED", "BACKUP", "CANARY", "HEALTH")))
            result = watchdog.activate(state, "upgrade-1")
            self.assertEqual(result["state"], "COMMITTED")
            self.assertEqual(result["previous_sha"], previous)
            self.assertEqual(result["candidate_sha"], candidate)
            self.assertEqual(subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(), candidate)
            with sqlite3.connect(db_path) as db:
                self.assertEqual(db.execute("SELECT value FROM settings WHERE key='integration_sha'").fetchone()[0], candidate)
                self.assertEqual(db.execute("SELECT state FROM upgrade_batches").fetchone()[0], "COMMITTED")
                self.assertEqual(db.execute("SELECT result FROM upgrade_checks WHERE stage='ACTIVATION'").fetchone()[0], "PASS")
            self.assertTrue(Path(result["activation_receipt"]).is_file())

    def test_activation_refuses_control_marker_without_moving_head(self):
        watchdog = load_watchdog()
        with tempfile.TemporaryDirectory() as root:
            state = Path(root) / "state"
            repo = Path(root) / "repo"
            state.mkdir()
            repo.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "develop", str(repo)], check=True)
            (repo / "README.md").write_text("checkpoint\n")
            subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
            subprocess.run([
                "git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@local.invalid",
                "commit", "-qm", "checkpoint",
            ], check=True)
            previous = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            db_path = state / "sda.sqlite3"
            with sqlite3.connect(db_path) as db:
                db.executescript("""
                    CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                    CREATE TABLE upgrade_batches(batch_id TEXT PRIMARY KEY,state TEXT,candidate_sha TEXT,rollback_sha TEXT,updated_at TEXT,created_at TEXT);
                    CREATE TABLE upgrade_checks(batch_id TEXT,stage TEXT,result TEXT,artifact_sha TEXT,evidence_sha TEXT,recorded_at TEXT,verifier TEXT,PRIMARY KEY(batch_id,stage));
                """)
                db.executemany("INSERT INTO settings VALUES (?,?)", [
                    ("integration_path", str(repo)), ("integration_sha", previous), ("schema_version", "5"),
                ])
                db.execute("INSERT INTO upgrade_batches VALUES (?,?,?,?,?,?)",
                           ("upgrade-1", "HEALTH_SOAK", previous, previous, "1", "1"))
                db.executemany("INSERT INTO upgrade_checks VALUES (?,?,?,?,?,?,?)",
                               (("upgrade-1", stage, "PASS", previous, "e" * 64, "1", "deterministic_controller")
                                for stage in ("TESTED", "BACKUP", "CANARY", "HEALTH")))
            (state / "PAUSE").touch()
            with self.assertRaisesRegex(ValueError, "control marker blocks activation"):
                watchdog.activate(state, "upgrade-1")
            self.assertEqual(subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(), previous)


if __name__ == "__main__":
    unittest.main()
