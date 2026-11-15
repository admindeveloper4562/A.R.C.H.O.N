"""Supervisor/recovery monitor is read-only, honest about absent telemetry, and redacted."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from jarvis_v2.monitor import render, snapshot

SCHEMA = """
CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE tasks(
 id TEXT PRIMARY KEY,spec TEXT NOT NULL,status TEXT NOT NULL,
 architecture_sha TEXT NOT NULL,attempt INTEGER NOT NULL,
 branch TEXT NOT NULL,last_run TEXT,base_sha TEXT NOT NULL DEFAULT '',
 candidate_sha TEXT NOT NULL DEFAULT '',last_error TEXT NOT NULL DEFAULT '',
 created_at TEXT NOT NULL,updated_at TEXT NOT NULL,project_id TEXT NOT NULL DEFAULT '');
CREATE TABLE runs(
 id TEXT PRIMARY KEY,task_id TEXT,attempt INTEGER,role TEXT,status TEXT,
 started_at TEXT,finished_at TEXT,model TEXT,tool_count INTEGER DEFAULT 0,
 error_code TEXT DEFAULT '');
CREATE TABLE events(
 run_id TEXT,task_id TEXT,time TEXT,stage TEXT,step TEXT,branch TEXT,
 tool_count INTEGER,result TEXT,attempt INTEGER);
"""


class SupervisorTelemetryTests(unittest.TestCase):
    def _fixture(self, path, *, extended):
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.executescript("PRAGMA journal_mode=WAL;" + SCHEMA)
        conn.execute("INSERT INTO settings VALUES (?,?)", ("source_sha", "a" * 40))
        conn.execute("INSERT INTO settings VALUES (?,?)", ("integration_sha", "b" * 40))
        conn.execute("INSERT INTO settings VALUES (?,?)", ("integration_branch", "develop"))
        conn.execute("INSERT INTO settings VALUES (?,?)", ("architecture_sha", "approved"))
        conn.execute("INSERT INTO settings VALUES (?,?)", ("approved_architecture_sha", "approved"))
        conn.execute(
            "INSERT INTO tasks(id,spec,status,architecture_sha,attempt,branch,last_run,created_at,updated_at,project_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("CORE-001", json.dumps({"objective": "Build queue", "acceptance": "secret=hidden123"}),
             "completed", "approved", 1, "", None, "2026-11-15T00:00:00Z",
             "2026-11-15T00:00:00Z", "ARCHON-JARVIS-V2"),
        )
        conn.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)", (
            "run1", "CORE-001", 1, "worker", "completed",
            "2026-11-15T00:00:00Z", "2026-11-15T00:00:05Z",
            "gpt-5.6-luna", 2, "",
        ))
        conn.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?)", (
            "run2", "CORE-001", 2, "repairer", "failed",
            "2026-11-15T00:00:00Z", "2026-11-15T00:00:05Z",
            "gpt-5.6-luna", 2, "qc_rejected:secret=hidden123",
        ))
        if extended:
            conn.executescript("""
              CREATE TABLE subtasks(
               id TEXT PRIMARY KEY,parent_id TEXT,project_id TEXT,status TEXT,
               evidence TEXT);
              CREATE TABLE project_queue(id TEXT PRIMARY KEY);
              CREATE TABLE pending_queue(id TEXT PRIMARY KEY);
              CREATE TABLE rebuild_queue(id TEXT PRIMARY KEY);
              CREATE TABLE review_queue(id TEXT PRIMARY KEY);
              CREATE TABLE merge_queue(id TEXT PRIMARY KEY);
              CREATE TABLE supervisor_cases(
               case_id TEXT PRIMARY KEY,parent_id TEXT,state TEXT,category TEXT,
               updated_at TEXT,raw_findings TEXT);
              CREATE TABLE supervisor_lanes(
               lane_id TEXT PRIMARY KEY,role TEXT,task_id TEXT,state TEXT,
               updated_at TEXT,private_context TEXT);
              CREATE TABLE upgrade_batches(
               batch_id TEXT PRIMARY KEY,state TEXT,candidate_sha TEXT,
               rollback_sha TEXT,updated_at TEXT,private_log TEXT);
            """)
            conn.execute("INSERT INTO subtasks VALUES (?,?,?,?,?)", (
                "CORE-001.S01", "CORE-001", "ARCHON-JARVIS-V2",
                "completed", "private evidence",
            ))
            conn.execute("INSERT INTO pending_queue VALUES ('CORE-002')")
            conn.execute("INSERT INTO supervisor_cases VALUES (?,?,?,?,?,?)", (
                "case-1", "CORE-003", "investigating", "qc_repeat",
                "2026-11-15T00:00:00Z", "password=private",
            ))
            conn.execute("INSERT INTO supervisor_lanes VALUES (?,?,?,?,?,?)", (
                "repair_1", "recovery_coder", "CORE-003", "coding",
                "2026-11-15T00:00:00Z", "token=private",
            ))
            conn.execute("INSERT INTO supervisor_lanes VALUES (?,?,?,?,?,?)", (
                "upgrade_auditor", "auditor", "", "reviewing",
                "2026-11-15T00:00:00Z", "secret=hidden",
            ))
            conn.execute("INSERT INTO upgrade_batches VALUES (?,?,?,?,?,?)", (
                "upgrade-1", "canary", "a" * 40, "b" * 40,
                "2026-11-15T00:00:00Z", "secret=private",
            ))
        conn.commit()
        return conn

    def test_legacy_astra_db_gracefully_reports_missing_lanes(self):
        with tempfile.TemporaryDirectory() as root:
            db_path = Path(root) / "sda.sqlite3"
            writer = self._fixture(db_path, extended=False)
            try:
                data = snapshot(db_path, source="astra")
                self.assertEqual(data["supervision"]["project"]["parents_recorded"], 1)
                self.assertIsNone(data["supervision"]["supervisor_cases"])
                self.assertIsNone(data["supervision"]["supervisor_lanes"])
                self.assertIsNone(data["supervision"]["queues"]["pending_queue"])
                output = render(data)
                self.assertIn("no active/idle inference", output)
                self.assertIn("not recorded", output)
            finally:
                writer.close()

    def test_new_lanes_queues_failures_and_upgrade_without_private_data(self):
        with tempfile.TemporaryDirectory() as root:
            db_path = Path(root) / "sda.sqlite3"
            writer = self._fixture(db_path, extended=True)
            try:
                before = writer.execute("SELECT COUNT(*) FROM supervisor_cases").fetchone()[0]
                data = snapshot(db_path, source="astra")
                panel = data["supervision"]
                self.assertEqual(panel["project"]["parents_recorded"], 1)
                self.assertEqual(panel["project"]["subtasks_recorded"], 1)
                self.assertEqual(panel["queues"]["pending_queue"], 1)
                self.assertEqual(panel["supervisor_cases"]["states"]["investigating"], 1)
                self.assertEqual(panel["supervisor_lanes"][0]["lane_id"], "repair_1")
                self.assertEqual(panel["upgrade_batch"]["state"], "canary")
                self.assertEqual(panel["run_totals"]["failed"], 1)
                self.assertTrue(panel["failure_codes"])
                view = json.dumps(data)
                for secret in ("hidden123", "password=private", "token=private", "private evidence"):
                    self.assertNotIn(secret, view)
                self.assertIn("SUPERVISOR REPAIR LANES", render(data))
                self.assertIn("SELF-UPGRADE BATCH", render(data))
                self.assertEqual(writer.execute("SELECT COUNT(*) FROM supervisor_cases").fetchone()[0], before)
            finally:
                writer.close()

    def test_unknown_event_and_failure_values_are_redacted(self):
        with tempfile.TemporaryDirectory() as root:
            db_path = Path(root) / "sda.sqlite3"
            writer = self._fixture(db_path, extended=False)
            try:
                writer.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?)", (
                    "run2", "CORE-001", "2026-11-15T00:00:05Z", "failed", "worker_failed",
                    "feature/core/CORE-001", 2, "secret-model-fragment", 2,
                ))
                writer.execute("UPDATE runs SET error_code=? WHERE id='run2'", ("token123",))
                writer.execute("UPDATE events SET result=?", ("secret-model-fragment",))
                writer.commit()
                data = snapshot(db_path, source="astra")
                self.assertNotIn("token123", json.dumps(data))
                self.assertNotIn("secret-model-fragment", json.dumps(data))
                self.assertEqual(data["recent_runs"][0]["error_code"], "redacted")
                self.assertEqual(data["events"][0]["result"], "redacted")
            finally:
                writer.close()


if __name__ == "__main__":
    unittest.main()
