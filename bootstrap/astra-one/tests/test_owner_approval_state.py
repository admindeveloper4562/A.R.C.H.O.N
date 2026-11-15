import hashlib
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import sys
import tempfile
import unittest

from astra_one.linux_sda import PROJECT_ID, SCHEMA, State, file_sha256


class OwnerApprovalStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "state"
        self.home.mkdir(mode=0o700)
        self.source = self.root / "source"
        (self.source / "docs" / "architecture").mkdir(parents=True)
        (self.source / "docs" / "architecture" / "JARVIS_V2_CONSOLIDATED.md").write_text(
            "# ten-module architecture\nBusiness excluded.\n", encoding="utf-8"
        )
        self.focus = self.home / "private" / "architecture-focus.md"
        self.focus.parent.mkdir(mode=0o700)
        self.focus.write_text("# bounded focus\n", encoding="utf-8")
        self.focus_sha = file_sha256(self.focus)
        self.full_sha = file_sha256(self.source / "docs" / "architecture" / "JARVIS_V2_CONSOLIDATED.md")
        self.parent_sha = "d" * 64
        self.source_sha = "e" * 40
        self.integration_sha = "f" * 40
        packet = self.home / "reports" / "BASE-008_OWNER_DECISION_PACKET.md"
        packet.parent.mkdir(mode=0o700)
        packet.write_text(
            "| Full architecture SHA-256 | `" + self.full_sha + "` |\n"
            "| Approved bounded focus SHA-256 | `" + self.focus_sha + "` |\n"
            "| Parent task payload SHA | `" + self.parent_sha + "` |\n"
            "| Live source SHA | `" + self.source_sha + "` |\n"
            "| Live integration SHA | `" + self.integration_sha + "` |\n",
            encoding="utf-8",
        )
        (packet.parent / "BASE-008_OWNER_DECISION_PACKET.sha256").write_text(
            f"{file_sha256(packet)}  BASE-008_OWNER_DECISION_PACKET.md\n", encoding="utf-8"
        )
        self.state = State(self.home)
        sqlite3.connect(self.state.database).close()
        with self.state.db() as db:
            db.executescript(SCHEMA)
            db.execute("PRAGMA user_version=3")
            db.executemany("INSERT INTO settings(key,value) VALUES(?,?)", [
                ("architecture_sha", self.focus_sha),
                ("approved_architecture_sha", self.focus_sha),
                ("source", str(self.source)),
                ("source_sha", self.source_sha),
                ("integration_sha", self.integration_sha),
            ])
            db.execute(
                "INSERT INTO projects(id,name,source_repository,integration_branch,parent_task_count,subtask_count,workers,model,reasoning,source_ref,source_commit,parent_plan_blob_sha,subtask_index_sha,payload_sha,status,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (PROJECT_ID, "test", "test", "develop", 2, 3, 1, "test", "low", "ref", self.source_sha, "a"*40, "b"*64, "c"*64, "pending", "now", "now"),
            )
            base_spec = json.dumps({"task_id": "BASE-001", "objective": "completed prerequisite", "depends_on": [], "acceptance": ["done"], "area": "base"})
            db.execute(
                "INSERT INTO tasks(id,spec,status,architecture_sha,created_at,updated_at,project_id,module,milestone,priority,owner_gate,payload_sha,enqueue_seq) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("BASE-001", base_spec, "completed", self.focus_sha, "now", "now", PROJECT_ID, "BASE", "M0", "P0", 0, "a"*64, 1),
            )
            spec = json.dumps({"task_id": "BASE-008", "objective": "Approve final architecture", "depends_on": ["BASE-001"], "acceptance": ["Signed architecture digest"], "area": "base"})
            db.execute(
                "INSERT INTO tasks(id,spec,status,architecture_sha,created_at,updated_at,project_id,module,milestone,priority,owner_gate,payload_sha,enqueue_seq) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("BASE-008", spec, "approval_required", self.focus_sha, "now", "now", PROJECT_ID, "BASE", "M0", "P0", 1, self.parent_sha, 2),
            )
            for sequence in range(1, 4):
                cid = f"BASE-008.S0{sequence}"
                child_spec = json.dumps({"id": cid, "sequence": sequence, "kind": "owner", "instruction": "verify", "deliverable": "receipt", "done_when": "recorded", "depends_on": []})
                db.execute(
                    "INSERT INTO subtasks(id,project_id,parent_id,sequence,spec,status,payload_sha,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (cid, PROJECT_ID, "BASE-008", sequence, child_spec, "waiting", "1" * 64, "now", "now"),
                )
        self.private_key = self.root / "owner_ed25519"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(self.private_key)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.allowed = self.home / "owner" / "allowed_signers"
        self.allowed.parent.mkdir(mode=0o700)
        self.allowed.write_text("owner " + self.private_key.with_name(self.private_key.name + ".pub").read_text(), encoding="utf-8")
        os.chmod(self.allowed, 0o600)

    def tearDown(self):
        self.temp.cleanup()

    def test_master_records_owner_and_three_child_receipts(self):
        request = self.state.owner_approval_request("BASE-008", "owner", allowed_signers=self.allowed)
        subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(self.private_key), "-n", "archon-owner-approval-v1", request["message"]],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chmod(Path(request["message"] + ".sig"), 0o600)
        result = self.state.approve_owner("BASE-008", owner_receipt=Path(request["receipt"]))
        self.assertEqual(result["status"], "completed")
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id='BASE-008'").fetchone()[0], "completed")
            self.assertEqual(db.execute("SELECT count(*) FROM owner_approval_receipts WHERE task_id='BASE-008'").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT count(*) FROM owner_subtask_receipts WHERE parent_id='BASE-008'").fetchone()[0], 3)
            self.assertEqual(db.execute("SELECT count(*) FROM subtasks WHERE parent_id='BASE-008' AND status='completed'").fetchone()[0], 3)

    def test_cli_request_and_approval_commands(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
        request = subprocess.run(
            [sys.executable, "-m", "astra_one.linux_cli", "--home", str(self.home),
             "owner-approval-request", "BASE-008", "--owner-id", "owner",
             "--allowed-signers", str(self.allowed)],
            cwd=str(Path(__file__).resolve().parents[1]), env=env,
            check=True, capture_output=True, text=True,
        )
        request_data = json.loads(request.stdout)
        subprocess.run(
            ["ssh-keygen", "-Y", "sign", "-f", str(self.private_key), "-n",
             "archon-owner-approval-v1", request_data["message"]],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        os.chmod(Path(request_data["message"] + ".sig"), 0o600)
        approved = subprocess.run(
            [sys.executable, "-m", "astra_one.linux_cli", "--home", str(self.home),
             "approve-owner", "BASE-008", "--owner-receipt", request_data["receipt"]],
            cwd=str(Path(__file__).resolve().parents[1]), env=env,
            check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(approved.stdout)["status"], "completed")

    def test_missing_owner_receipt_does_not_change_state(self):
        with self.assertRaisesRegex(ValueError, "authenticated owner receipt"):
            self.state.approve_owner("BASE-008", owner_receipt=None)
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id='BASE-008'").fetchone()[0], "approval_required")


if __name__ == "__main__":
    unittest.main()
