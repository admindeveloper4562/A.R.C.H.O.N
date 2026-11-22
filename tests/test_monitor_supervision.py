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
              CREATE TABLE subtask_receipts(
               receipt_id TEXT PRIMARY KEY,parent_id TEXT,subtask_id TEXT,
               candidate_sha TEXT,verifier TEXT);
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
              CREATE TABLE upgrade_audits(
               audit_id TEXT PRIMARY KEY,task_id TEXT,lane_id TEXT,run_id TEXT,
               model TEXT,status TEXT,report_path TEXT,report_sha TEXT,
               evidence_sha TEXT,updated_at TEXT);
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
            conn.execute("INSERT INTO upgrade_audits VALUES (?,?,?,?,?,?,?,?,?,?)", (
                "U1-BASE-015-test", "BASE-015", "upgrade_auditor", "run-u1",
                "gpt-6.1-sol", "completed", "/private/report.json", "c" * 64,
                "d" * 64, "2026-11-15T00:00:01Z",
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
                self.assertEqual(
                    data["supervision"]["project"]["completion_evidence"],
                    "status_only_not_independently_verified",
                )
                self.assertIsNone(data["supervision"]["project"]["subtasks_with_independent_qc_receipts"])
                output = render(data)
                self.assertIn("coverage unavailable", output)
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
                self.assertEqual(panel["upgrade_audits"][0]["task_id"], "BASE-015")
                self.assertEqual(panel["upgrade_audits"][0]["report_sha"], "c" * 12)
                self.assertEqual(panel["run_totals"]["failed"], 1)
                self.assertTrue(panel["failure_codes"])
                view = json.dumps(data)
                for secret in ("hidden123", "password=private", "token=private", "private evidence"):
                    self.assertNotIn(secret, view)
                self.assertIn("SUPERVISOR REPAIR LANES", render(data))
                self.assertIn("SELF-UPGRADE BATCH", render(data))
                self.assertIn("U1 latest", render(data))
                self.assertEqual(writer.execute("SELECT COUNT(*) FROM supervisor_cases").fetchone()[0], before)
            finally:
                writer.close()


    def test_receipt_coverage_is_per_child_and_completion_accurate(self):
        with tempfile.TemporaryDirectory() as root:
            db_path = Path(root) / "sda.sqlite3"
            writer = self._fixture(db_path, extended=True)
            try:
                writer.execute("INSERT INTO subtasks VALUES (?,?,?,?,?)", (
                    "CORE-001.S02", "CORE-001", "ARCHON-JARVIS-V2",
                    "completed", "private evidence",
                ))
                writer.executemany(
                    "INSERT INTO subtask_receipts VALUES (?,?,?,?,?)",
                    [
                        ("r1", "CORE-001", "CORE-001.S01", "a" * 40, "independent_qc"),
                        ("r2", "CORE-001", "CORE-001.S01", "b" * 40, "independent_qc"),
                        ("r3", "CORE-001", "CORE-001.S02", "c" * 40, "worker"),
                        ("r4", "CORE-001", "CORE-001.S02", "", "independent_qc"),
                    ],
                )
                writer.commit()

                snapshot_data = snapshot(db_path, source="astra")
                panel = snapshot_data["supervision"]["project"]
                self.assertEqual(panel["verified_subtask_receipts"], 2)
                self.assertEqual(panel["subtasks_with_independent_qc_receipts"], 1)
                self.assertEqual(panel["subtasks_without_independent_qc_receipts"], 1)
                self.assertEqual(panel["completed_subtasks_without_independent_qc_receipts"], 1)
                self.assertEqual(
                    panel["completion_evidence"],
                    "completed_children_missing_independent_qc_receipts",
                )
                self.assertIn(
                    "2 independent-QC receipt rows; 1/2 children covered; 1 missing (1 completed)",
                    render(snapshot_data),
                )

                writer.execute("INSERT INTO subtask_receipts VALUES (?,?,?,?,?)", (
                    "r5", "CORE-001", "CORE-001.S02", "d" * 40, "independent_qc",
                ))
                writer.commit()
                panel = snapshot(db_path, source="astra")["supervision"]["project"]
                self.assertEqual(panel["verified_subtask_receipts"], 3)
                self.assertEqual(panel["subtasks_with_independent_qc_receipts"], 2)
                self.assertEqual(panel["subtasks_without_independent_qc_receipts"], 0)
                self.assertEqual(panel["completed_subtasks_without_independent_qc_receipts"], 0)
                self.assertEqual(
                    panel["completion_evidence"],
                    "all_recorded_children_have_independent_qc_receipts",
                )
            finally:
                writer.close()


    def test_legacy_subtask_schema_scopes_through_parent_project(self):
        with tempfile.TemporaryDirectory() as root:
            db_path = Path(root) / "sda.sqlite3"
            writer = self._fixture(db_path, extended=True)
            try:
                writer.execute(
                    "INSERT INTO tasks(id,spec,status,architecture_sha,attempt,branch,last_run,created_at,updated_at,project_id) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        "CORE-OTHER", json.dumps({"objective": "other project"}),
                        "completed", "approved", 1, "", None,
                        "2026-11-15T00:00:00Z", "2026-11-15T00:00:00Z", "OTHER",
                    ),
                )
                writer.execute("ALTER TABLE subtasks DROP COLUMN project_id")
                writer.execute("INSERT INTO subtasks VALUES (?,?,?,?)", (
                    "CORE-OTHER.S01", "CORE-OTHER", "completed", "other project",
                ))
                writer.execute("INSERT INTO subtask_receipts VALUES (?,?,?,?,?)", (
                    "r1", "CORE-001", "CORE-001.S01", "a" * 40, "independent_qc",
                ))
                writer.commit()

                snapshot_data = snapshot(db_path, source="astra")
                panel = snapshot_data["supervision"]["project"]
                self.assertEqual(panel["subtasks_recorded"], 1)
                self.assertEqual(panel["subtask_statuses"], {"completed": 1})
                self.assertEqual(panel["subtasks_with_independent_qc_receipts"], 1)
                self.assertEqual(panel["subtasks_without_independent_qc_receipts"], 0)
                self.assertEqual(panel["completed_subtasks_without_independent_qc_receipts"], 0)
                self.assertIn(
                    "1 independent-QC receipt rows; 1/1 children covered; 0 missing (0 completed)",
                    render(snapshot_data),
                )
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
