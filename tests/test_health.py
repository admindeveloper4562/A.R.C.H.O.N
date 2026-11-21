import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jarvis_v2.backend.storage import StorageManager
from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.core.queue import TaskQueue
from jarvis_v2.health import HealthError, collect_health


class HealthTests(unittest.TestCase):
    def test_health_reads_without_creating_or_mutating_database(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / "state"
            state.mkdir()
            db_path = state / "sda.sqlite3"
            with sqlite3.connect(db_path) as db:
                db.executescript("""
                    CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                    CREATE TABLE projects(id TEXT PRIMARY KEY,parent_task_count INTEGER,subtask_count INTEGER,payload_sha TEXT);
                    CREATE TABLE tasks(id TEXT PRIMARY KEY,project_id TEXT,status TEXT,last_error TEXT,spec TEXT,candidate_sha TEXT,integrated_sha TEXT,updated_at TEXT);
                    CREATE TABLE subtasks(id TEXT PRIMARY KEY,parent_id TEXT,status TEXT);
                    CREATE TABLE project_queue(id INTEGER);
                    INSERT INTO settings VALUES ('schema_version','5'),('integration_sha','a'),('source_sha','b');
                    INSERT INTO projects VALUES ('ARCHON-JARVIS-V2',247,1359,'c');
                    INSERT INTO tasks VALUES ('MIG-012','ARCHON-JARVIS-V2','approval_required','','{"depends_on": []}','','','2026-11-18');
                """)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "health@test"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "health"], check=True)
            (root / "README").write_text("health", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "fixture"], check=True)
            before = db_path.read_bytes()
            with patch("jarvis_v2.health._systemd_state", side_effect=lambda unit: unit):
                result = collect_health(state_dir=state, repository=root)
            self.assertEqual(result["sqlite"]["integrity"], "ok")
            self.assertEqual(result["plan"]["parent_total"], 247)
            self.assertEqual(result["root_blockers"][0]["task_id"], "MIG-012")
            self.assertEqual(result["controller"], {
                "service": "archon-astra.service",
                "timer": "archon-astra.timer",
            })
            self.assertEqual(db_path.read_bytes(), before)

    def test_health_rejects_missing_canonical_database(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(HealthError, "database is unavailable"):
                collect_health(state_dir=Path(temp), repository=Path(temp))

    def test_health_reads_fresh_native_runtime_without_historical_ledger(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / "state"
            state.mkdir()
            with StorageManager(state / "runtime.sqlite3") as storage:
                storage.migrate()
            TaskQueue(state / "atlas.sqlite3").close()
            conversations = state / "conversations.sqlite3"
            with ConversationStore(conversations):
                pass
            conversations.chmod(0o600)
            subprocess.run(["git", "init", "-q", str(root / "repo")], check=True)
            repo = root / "repo"
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "health@test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "health"], check=True)
            (repo / "README").write_text("health", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "README"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "fixture"], check=True)
            result = collect_health(state_dir=state, repository=repo)
            self.assertEqual(result["status"], "healthy")
            self.assertEqual(result["mode"], "native_runtime")
            self.assertFalse(result["historical_ledger"]["loaded"])
            self.assertEqual(result["queue"]["total"], 0)
            self.assertEqual(result["sqlite"]["conversations"]["integrity"], "ok")
            conversations.chmod(0o644)
            with self.assertRaisesRegex(HealthError, "conversations database permissions"):
                collect_health(state_dir=state, repository=repo)

    def test_health_supports_installed_package_without_git_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state = root / "state"
            state.mkdir()
            with StorageManager(state / "runtime.sqlite3") as storage:
                storage.migrate()
            TaskQueue(state / "atlas.sqlite3").close()
            repo = root / "installed-package"
            repo.mkdir()
            with patch.dict(os.environ, {"ARCHON_SOURCE_SHA": "a" * 40}):
                result = collect_health(state_dir=state, repository=repo)
            self.assertEqual(result["status"], "healthy")
            self.assertEqual(result["git"]["checkout_sha"], "a" * 40)
            with patch.dict(os.environ, {"ARCHON_SOURCE_SHA": "unknown"}):
                result = collect_health(state_dir=state, repository=repo)
            self.assertEqual(result["git"]["checkout_sha"], "unknown")

    def test_cli_health_returns_structured_state(self):
        result = subprocess.run(
            ["/usr/bin/python3", "-m", "jarvis_v2.cli", "health", "--state", "/does/not/exist"],
            capture_output=True, text=True, env={"PYTHONPATH": "src"}, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("database is unavailable", result.stderr)


if __name__ == "__main__":
    unittest.main()
