import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

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
            result = collect_health(state_dir=state, repository=root)
            self.assertEqual(result["sqlite"]["integrity"], "ok")
            self.assertEqual(result["plan"]["parent_total"], 247)
            self.assertEqual(result["root_blockers"][0]["task_id"], "MIG-012")
            self.assertEqual(db_path.read_bytes(), before)

    def test_health_rejects_missing_canonical_database(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(HealthError, "database is unavailable"):
                collect_health(state_dir=Path(temp), repository=Path(temp))

    def test_cli_health_returns_structured_state(self):
        result = subprocess.run(
            ["/usr/bin/python3", "-m", "jarvis_v2.cli", "health", "--state", "/does/not/exist"],
            capture_output=True, text=True, env={"PYTHONPATH": "src"}, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("database is unavailable", result.stderr)


if __name__ == "__main__":
    unittest.main()
