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


if __name__ == "__main__":
    unittest.main()
