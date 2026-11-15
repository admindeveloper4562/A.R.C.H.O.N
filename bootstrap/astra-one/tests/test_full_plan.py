import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from astra_one.full_plan import FullPlan, PROJECT_ID, payload_sha
from astra_one.linux_runtime import _write_receipt_artifact, make_prompt
from astra_one.linux_sda import State


def git_repo(root: Path) -> Path:
    import subprocess
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "develop", str(root)], check=True)
    (root / "README.md").write_text("initial\n")
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run([
        "git", "-C", str(root), "-c", "user.name=test", "-c",
        "user.email=test@local.invalid", "commit", "-qm", "initial",
    ], check=True)
    return root


def child(cid: str, sequence: int, depends_on: list[str] | None = None) -> dict:
    return {
        "id": cid,
        "sequence": sequence,
        "kind": "implement",
        "title": f"Implement {cid}",
        "assignee_role": "worker",
        "instruction": "Make the bounded implementation and inspect the current contract.",
        "deliverable": "A tested source change.",
        "done_when": "The acceptance evidence is recorded.",
        "depends_on": depends_on or [],
        "evidence_required": True,
        "remote_github_actions_allowed": False,
    }


def bound_receipts(state: State, task_id: str, run_id: str, attempt: int, source_sha: str,
                   changed_files: list[str], candidate_sha: str, contract_sha: str,
                   child_evidence: list[dict]) -> tuple[dict, dict]:
    context = {
        "task_id": task_id, "run_id": run_id, "attempt": attempt, "source_sha": source_sha,
        "candidate_sha": candidate_sha,
        "changed_files_sha": hashlib.sha256(
            json.dumps(changed_files, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "contract_sha": contract_sha,
    }
    test_payload = {"passed": True, "exit_code": 0, "sandbox": "docker_no_network", "tests_detected": True}
    test_path, test_artifact_sha = _write_receipt_artifact(
        state.home / "private" / "test-receipts", kind="docker_test_receipt",
        context=context, payload=test_payload,
    )
    test_receipt = dict(test_payload)
    test_receipt["receipt_sha"] = hashlib.sha256(
        json.dumps(test_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    test_receipt.update({"artifact_path": test_path, "artifact_sha": test_artifact_sha})
    qc_payload = {"verdict": "PASS", "findings": [], "child_evidence": child_evidence}
    qc_path, qc_artifact_sha = _write_receipt_artifact(
        state.home / "private" / "qc-receipts", kind="independent_qc_receipt",
        context=context, payload=qc_payload, extra={"source_output_sha": "b" * 64},
    )
    qc_receipt = {
        "verdict": "PASS", "findings": [], "reviewer": "independent_qc", "candidate_sha": candidate_sha,
        "qc_output_sha": "b" * 64, "qc_artifact_path": qc_path, "qc_artifact_sha": qc_artifact_sha,
        "contract_sha": contract_sha,
        "child_evidence_sha": hashlib.sha256(
            json.dumps(child_evidence, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "changed_files_sha": context["changed_files_sha"],
    }
    return test_receipt, qc_receipt


def parent(pid: str, module: str, dependencies: list[str] | None = None,
           owner_gate: bool = False, priority: str = "P1") -> dict:
    children = [child(f"{pid}.S01", 1), child(f"{pid}.S02", 2, [f"{pid}.S01"])]
    spec = {
        "task_id": pid,
        "objective": f"Build {pid} without changing protected policy files.",
        "acceptance": ["The bounded implementation is tested and reviewable."],
        "depends_on": dependencies or [],
        "area": module.lower(),
        "project_id": PROJECT_ID,
        "module": module,
        "milestone": "test milestone",
        "priority": priority,
        "title": f"Build {pid}",
        "required_owner_gate": owner_gate,
        "manual_owner_gate_required": owner_gate,
        "subtasks": children,
    }
    return {
        "task_id": pid,
        "module": module,
        "milestone": "test milestone",
        "priority": priority,
        "owner_gate": owner_gate,
        "dependencies": dependencies or [],
        "spec": spec,
        "payload_sha": payload_sha(spec),
        "children": children,
    }


class FullPlanImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.repo = git_repo(self.base / "source")
        self.state = State(self.base / "state")
        self.state.init(self.repo)
        architecture = self.base / "architecture.md"
        architecture.write_text("# approved architecture\nSafe repository coding only.\n")
        sha = self.state.import_architecture(architecture)
        self.state.approve_architecture(sha)

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self):
        parents = (
            parent("FULL-001", "BASE"),
            parent("FULL-002", "SDA", ["FULL-001"]),
            parent("FULL-003", "REL", owner_gate=True, priority="P2"),
        )
        project = {
            "project_id": PROJECT_ID,
            "project_name": "JARVIS V2 Full Build",
            "source_repository": "admindeveloper4562/A.R.C.H.O.N",
            "integration_branch": "develop",
            "parent_task_count": 3,
            "subtask_count": 6,
            "workers": 5,
            "model": "gpt-5.6-luna",
            "reasoning": "medium",
            "source_ref": "test-ref",
            "source_commit": "a" * 40,
            "parent_plan_blob_sha": "b" * 40,
            "subtask_index_sha256": "c" * 64,
            "architecture_modules": 10,
            "workstreams": ["BASE", "SDA", "REL"],
            "business_module_active": False,
            "module_hashes": {},
        }
        validation = {"parent_count": 3, "subtask_count": 6, "source_ref": "test-ref"}
        return FullPlan(project, parents, {p["task_id"]: tuple(p["children"]) for p in parents},
                        "b" * 40, "c" * 64, {}, validation)

    def test_import_attaches_children_and_populates_only_eligible_queue(self):
        result = self.state.import_full_plan(self.plan())
        self.assertEqual(result["inserted_parents"], 3)
        self.assertEqual(result["inserted_children"], 6)
        self.assertEqual(result["parent_status"], {"approval_required": 1, "pending": 1, "waiting": 1})
        self.assertEqual(result["child_status"], {"pending": 1, "waiting": 5})
        self.assertEqual(result["queues"]["project_queue"], 1)
        self.assertEqual(result["queues"]["pending_queue"], 1)
        self.assertEqual(result["queues"]["rebuild_queue"], 0)
        claim = self.state.claim()
        self.assertEqual(claim["task"]["task_id"], "FULL-001")
        self.assertEqual(len(claim["task"]["subtasks"]), 2)
        prompt = make_prompt(claim["task"], "a" * 40, "b" * 64, "worker")
        self.assertIn("Ordered child execution packet", prompt)
        self.assertIn("FULL-001.S02", prompt)

    def test_completion_promotes_dependent_parent_and_children(self):
        self.state.import_full_plan(self.plan())
        claim = self.state.claim()
        source_sha = self.state.get("integration_sha")
        self.state.set_task("FULL-001", "coding", fields={"base_sha": source_sha, "candidate_sha": "d" * 40},
                            run_id=claim["run_id"], attempt=claim["attempt"])
        evidence = [
            {"subtask_id": "FULL-001.S01", "status": "PASS", "evidence": "criterion checked"},
            {"subtask_id": "FULL-001.S02", "status": "PASS", "evidence": "criterion checked"},
        ]
        changed = ["candidate.py"]
        test_receipt, qc_receipt = bound_receipts(
            self.state, "FULL-001", claim["run_id"], claim["attempt"], source_sha,
            changed, "d" * 40, self.state.subtask_contract_sha("FULL-001"), evidence,
        )
        self.state.record_subtask_evidence(
            "FULL-001", candidate_sha="d" * 40, source_sha=source_sha,
            changed_files=changed,
            test_receipt=test_receipt,
            qc_receipt=qc_receipt,
            child_evidence=evidence,
            run_id=claim["run_id"], attempt=claim["attempt"],
        )
        self.state.set_task("FULL-001", "completed", fields={"candidate_sha": "d" * 40})
        status = self.state.full_plan_status()
        self.assertEqual(status["parent_status"], {"approval_required": 1, "completed": 1, "pending": 1})
        self.assertEqual(status["child_status"], {"completed": 2, "pending": 1, "waiting": 3})
        self.assertEqual(self.state.claim()["task"]["task_id"], "FULL-002")

    def test_import_is_idempotent_and_conflicts_are_not_overwritten(self):
        plan = self.plan()
        first = self.state.import_full_plan(plan)
        second = self.state.import_full_plan(plan)
        self.assertFalse(first["idempotent"])
        self.assertTrue(second["idempotent"])
        conflicting = self.plan()
        conflicting_parent = dict(conflicting.parents[0])
        conflicting_spec = dict(conflicting_parent["spec"])
        conflicting_spec["objective"] = "conflicting payload that must not overwrite history"
        conflicting_parent["spec"] = conflicting_spec
        conflicting_parent["payload_sha"] = payload_sha(conflicting_spec)
        conflicting = FullPlan(conflicting.project, (conflicting_parent,) + conflicting.parents[1:],
                               conflicting.children, conflicting.parent_plan_blob_sha,
                               conflicting.subtask_index_sha, conflicting.module_hashes,
                               conflicting.validation)
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.state.import_full_plan(conflicting)
        with self.state.db() as db:
            stored = json.loads(db.execute("SELECT spec FROM tasks WHERE id='FULL-001'").fetchone()[0])
        self.assertEqual(stored["objective"], plan.parents[0]["spec"]["objective"])

    def test_owner_gate_requires_authenticated_release(self):
        self.state.import_full_plan(self.plan())
        self.assertEqual(self.state.full_plan_status()["parent_status"]["approval_required"], 1)
        with self.assertRaisesRegex(ValueError, "authenticated owner receipt"):
            self.state.approve_owner("FULL-003")
        self.assertEqual(self.state.full_plan_status()["parent_status"]["approval_required"], 1)


if __name__ == "__main__":
    unittest.main()
