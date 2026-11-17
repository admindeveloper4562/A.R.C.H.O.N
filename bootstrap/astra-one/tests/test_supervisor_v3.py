import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
import subprocess

from astra_one.full_plan import FullPlan, PROJECT_ID, payload_sha
from astra_one.linux_runtime import _write_receipt_artifact
from astra_one.linux_sda import State
from astra_one.supervisor import SupervisorController, classify_failure


def git_repo(root: Path) -> Path:
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "develop", str(root)], check=True)
    (root / "README.md").write_text("initial\n")
    (root / "tests").mkdir()
    (root / "tests" / "test_smoke.py").write_text("import unittest\nclass Smoke(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n")
    (root / "tests" / "test_monitor_supervision.py").write_text(
        "import unittest\nclass Monitor(unittest.TestCase):\n    def test_canary(self): self.assertTrue(True)\n"
    )
    (root / "src").mkdir()
    (root / "bootstrap" / "astra-one" / "tests").mkdir(parents=True)
    (root / "bootstrap" / "astra-one" / "astra_one").mkdir()
    (root / "bootstrap" / "astra-one" / "astra_one" / "__init__.py").write_text("")
    (root / "bootstrap" / "astra-one" / "astra_one" / "linux_cli.py").write_text(
        "import sys\nif __name__ == '__main__':\n    print('Astra canary')\n"
    )
    (root / "bootstrap" / "astra-one" / "tests" / "test_runtime.py").write_text(
        "import unittest\nclass Runtime(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n"
    )
    (root / "bootstrap" / "astra-one" / "tests" / "test_supervisor_v3.py").write_text(
        "import unittest\nclass Supervisor(unittest.TestCase):\n    def test_canary(self): self.assertTrue(True)\n"
    )
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run([
        "git", "-C", str(root), "-c", "user.name=test", "-c", "user.email=test@local.invalid",
        "commit", "-qm", "initial",
    ], check=True)
    return root


def plan() -> FullPlan:
    children = tuple({
        "id": f"V3-001.S0{n}", "sequence": n, "kind": "implement", "title": f"Child {n}",
        "assignee_role": "worker", "instruction": "Make the bounded change.",
        "deliverable": "A tested change.", "done_when": "Evidence is recorded.",
        "depends_on": ["V3-001.S01"] if n == 2 else [], "evidence_required": True,
        "remote_github_actions_allowed": False,
    } for n in (1, 2))
    spec = {
        "task_id": "V3-001", "objective": "Build a bounded v3 controller test slice.",
        "acceptance": ["The bounded implementation is tested."], "depends_on": [], "area": "sda",
        "project_id": PROJECT_ID, "module": "SDA", "milestone": "v3", "priority": "P0",
        "title": "Build v3 test slice", "required_owner_gate": False,
        "manual_owner_gate_required": False, "subtasks": list(children),
        "suggested_scope_roots": ["bootstrap/astra-one/"],
    }
    parent = {
        "task_id": "V3-001", "module": "SDA", "milestone": "v3", "priority": "P0",
        "owner_gate": False, "dependencies": [], "spec": spec,
        "payload_sha": payload_sha(spec), "children": list(children),
    }
    project = {
        "project_id": PROJECT_ID, "project_name": "JARVIS V2 Full Build",
        "source_repository": "admindeveloper4562/A.R.C.H.O.N", "integration_branch": "develop",
        "parent_task_count": 1, "subtask_count": 2, "workers": 5,
        "model": "gpt-5.6-luna", "reasoning": "medium", "source_ref": "test",
        "source_commit": "a" * 40, "parent_plan_blob_sha": "b" * 40,
        "subtask_index_sha256": "c" * 64, "architecture_modules": 10,
        "workstreams": ["SDA"], "business_module_active": False, "module_hashes": {},
    }
    return FullPlan(project, (parent,), {"V3-001": children}, "b" * 40, "c" * 64, {},
                    {"parent_count": 1, "subtask_count": 2})


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
    return test_receipt, {
        "verdict": "PASS", "findings": [], "reviewer": "independent_qc", "candidate_sha": candidate_sha,
        "qc_output_sha": "b" * 64, "qc_artifact_path": qc_path, "qc_artifact_sha": qc_artifact_sha,
        "contract_sha": contract_sha,
        "child_evidence_sha": hashlib.sha256(
            json.dumps(child_evidence, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "changed_files_sha": context["changed_files_sha"],
    }


class SupervisorV3Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = git_repo(root / "source")
        self.state = State(root / "state")
        self.state.init(self.repo)
        head = subprocess.check_output(["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()
        self.state.put("integration_path", str(self.repo))
        self.state.put("integration_sha", head)
        arch = root / "architecture.md"
        arch.write_text("# approved\nBounded local development.\n")
        digest = self.state.import_architecture(arch)
        self.state.approve_architecture(digest)
        self.state.import_full_plan(plan())
        self.supervisor = SupervisorController(self.state)

    def tearDown(self):
        self.tmp.cleanup()

    def test_child_completion_requires_candidate_bound_receipts(self):
        claim = self.state.claim()
        source_sha = self.state.get("integration_sha")
        self.state.set_task("V3-001", "coding", fields={"base_sha": source_sha, "candidate_sha": "d" * 40},
                            run_id=claim["run_id"], attempt=claim["attempt"])
        with self.assertRaisesRegex(ValueError, "subtask_evidence_incomplete"):
            self.state.set_task("V3-001", "completed", fields={"candidate_sha": "d" * 40})
        evidence = [
            {"subtask_id": "V3-001.S01", "status": "PASS", "evidence": "checked one"},
            {"subtask_id": "V3-001.S02", "status": "PASS", "evidence": "checked two"},
        ]
        changed = ["candidate.py"]
        test_receipt, qc_receipt = bound_receipts(
            self.state, "V3-001", claim["run_id"], claim["attempt"], source_sha,
            changed, "d" * 40, self.state.subtask_contract_sha("V3-001"), evidence,
        )
        unbound_test = dict(test_receipt)
        unbound_test.pop("artifact_path")
        unbound_test.pop("artifact_sha")
        with self.assertRaisesRegex(ValueError, "receipt artifact reference missing"):
            self.state.record_subtask_evidence(
                "V3-001", candidate_sha="d" * 40, source_sha=source_sha,
                changed_files=changed, test_receipt=unbound_test, qc_receipt=qc_receipt,
                child_evidence=evidence, run_id=claim["run_id"], attempt=claim["attempt"],
            )
        receipt = self.state.record_subtask_evidence(
            "V3-001", candidate_sha="d" * 40, source_sha=source_sha,
            changed_files=changed,
            test_receipt=test_receipt,
            qc_receipt=qc_receipt,
            child_evidence=evidence,
            run_id=claim["run_id"], attempt=claim["attempt"],
        )
        self.assertEqual(receipt["children"], 2)
        self.state.set_task("V3-001", "completed", fields={"candidate_sha": "d" * 40})
        self.assertEqual(self.state.full_plan_status()["verified_subtask_receipts"], 2)

    def test_failure_taxonomy_and_case_lane_lease_are_durable(self):
        self.assertEqual(classify_failure("no_file_changes"), "code_defect")
        self.assertEqual(classify_failure("quota_or_rate_limit"), "provider_quota")
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        case = self.supervisor.triage_failure("V3-001", "no_file_changes", generation=1)
        self.assertEqual(case["state"], "triaged")
        lease = self.supervisor.claim_recovery(case["case_id"], "repair_1")
        self.assertEqual(lease["task_id"], "V3-001")
        with self.assertRaisesRegex(ValueError, "active recovery lease"):
            self.state.retry("V3-001")
        recovery_item = self.state.claim_recovery_task(lease)
        self.state.set_task("V3-001", "failed", error="no_file_changes",
                            run_id=recovery_item["run_id"], attempt=recovery_item["attempt"])
        with self.assertRaisesRegex(ValueError, "lease mismatch"):
            self.supervisor.finish_recovery(
                "repair_1", case["case_id"], lease_token="0" * 24,
                run_id=recovery_item["run_id"], generation=recovery_item["attempt"], state="blocked"
            )
        done = self.supervisor.finish_recovery(
            "repair_1", case["case_id"], lease_token=lease["lease_token"],
            run_id=recovery_item["run_id"], generation=recovery_item["attempt"], state="blocked"
        )
        self.assertEqual(done["state"], "blocked")
        status = self.supervisor.status()
        self.assertEqual(status["lanes"][0]["state"], "idle")

    def test_self_doctor_creates_one_scoped_proposal_across_generations(self):
        claim = self.state.claim()
        self.state.set_task(
            "V3-001", "failed", error="no_file_changes",
            run_id=claim["run_id"], attempt=claim["attempt"],
        )
        first = self.supervisor.self_doctor(limit=10)
        self.assertEqual(len(first["proposals"]), 1)
        proposal = first["proposals"][0]
        self.assertFalse(proposal["deduplicated"])
        self.assertEqual(proposal["scope_roots"], ["bootstrap/astra-one/"])
        with self.state.db() as db:
            db.execute(
                "UPDATE tasks SET attempt=2,base_sha=?,candidate_sha=? WHERE id='V3-001'",
                ("a" * 40, "b" * 40),
            )
        second = self.supervisor.self_doctor(limit=10)
        self.assertEqual(len(second["proposals"]), 1)
        self.assertTrue(second["proposals"][0]["deduplicated"])
        self.assertEqual(second["proposals"][0]["case_id"], proposal["case_id"])
        self.assertEqual(second["proposals"][0]["fingerprint"], proposal["fingerprint"])
        self.assertEqual(second["deduplicated"], 1)
        with self.state.db() as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM supervisor_cases WHERE parent_id='V3-001'").fetchone()[0], 1
            )

    def test_tick_resolves_historical_case_only_after_task_completion(self):
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        case = self.supervisor.triage_failure("V3-001", "no_file_changes", generation=1)
        self.assertEqual(self.supervisor.status()["cases"], {"triaged": 1})
        head = self.state.get("integration_sha")
        candidate = "d" * 40
        with self.state.db() as db:
            db.execute(
                "UPDATE tasks SET status='completed',candidate_sha=?,integrated_sha=? WHERE id=?",
                (candidate, head, "V3-001"),
            )
        tick = self.supervisor.tick(limit=1)
        self.assertEqual(tick["resolved_cases"], [{
            "case_id": case["case_id"], "parent_id": "V3-001", "generation": 1,
            "candidate_sha": candidate, "integrated_sha": head,
        }])
        self.assertEqual(self.supervisor.status()["cases"], {"resolved": 1})

    def test_tick_releases_lane_when_recovery_finished_before_callback(self):
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        case = self.supervisor.triage_failure("V3-001", "no_file_changes", generation=1)
        lease = self.supervisor.claim_recovery(case["case_id"], "repair_1")
        self.state.claim_recovery_task(lease)
        head = self.state.get("integration_sha")
        with self.state.db() as db:
            db.execute(
                "UPDATE tasks SET status='completed',candidate_sha=?,integrated_sha=? WHERE id=?",
                ("d" * 40, head, "V3-001"),
            )
        tick = self.supervisor.tick(limit=1)
        self.assertEqual(len(tick["resolved_cases"]), 1)
        with self.state.db() as db:
            lane = db.execute(
                "SELECT state,task_id,case_id FROM supervisor_lanes WHERE lane_id='repair_1'"
            ).fetchone()
        self.assertEqual(dict(lane), {"state": "idle", "task_id": "", "case_id": ""})

    def test_patch_applied_merger_checkpoint_resolves_recovery(self):
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        case = self.supervisor.triage_failure("V3-001", "no_file_changes", generation=1)
        lease = self.supervisor.claim_recovery(case["case_id"], "repair_1")
        item = self.state.claim_recovery_task(lease)
        base = self.state.get("integration_sha")
        worktree = self.state.home / "worktrees" / "v3-candidate"
        worktree.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([
            "git", "-C", str(self.repo), "worktree", "add", "-b", "feature/v3-candidate",
            str(worktree), base,
        ], check=True, stdout=subprocess.DEVNULL)
        try:
            (worktree / "candidate.py").write_text("VALUE = 1\n")
            subprocess.run(["git", "-C", str(worktree), "add", "candidate.py"], check=True)
            subprocess.run([
                "git", "-C", str(worktree), "-c", "user.name=test", "-c",
                "user.email=test@local.invalid", "commit", "-qm", "candidate",
            ], check=True)
            candidate = subprocess.check_output(
                ["git", "-C", str(worktree), "rev-parse", "HEAD"], text=True,
            ).strip()
            with self.state.db() as db:
                db.execute(
                    "UPDATE tasks SET status='approved',base_sha=?,branch=?,worktree=?,candidate_sha=? "
                    "WHERE id=?",
                    (base, "feature/v3-candidate", str(worktree), candidate, "V3-001"),
                )
            self.supervisor.bind_recovery_candidate(
                "repair_1", case["case_id"], lease_token=lease["lease_token"],
                run_id=item["run_id"], generation=item["attempt"], candidate_sha=candidate,
            )
            patch = subprocess.check_output(
                ["git", "-C", str(worktree), "diff", "--binary", base, candidate],
            )
            subprocess.run(
                ["git", "-C", str(self.repo), "apply", "--index", "-"],
                input=patch, check=True,
            )
            subprocess.run([
                "git", "-C", str(self.repo), "-c", "user.name=test", "-c",
                "user.email=test@local.invalid", "commit", "-qm", "merger patch",
            ], check=True)
            integrated = subprocess.check_output(
                ["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True,
            ).strip()
            self.state.put("integration_sha", integrated)
            with self.state.db() as db:
                db.execute(
                    "UPDATE tasks SET status='completed',integrated_sha=?,last_run=?,attempt=? WHERE id=?",
                    (integrated, item["run_id"], item["attempt"], "V3-001"),
                )
            self.assertNotEqual(
                subprocess.run([
                    "git", "-C", str(self.repo), "merge-base", "--is-ancestor", candidate, integrated,
                ], check=False).returncode,
                0,
            )
            done = self.supervisor.finish_recovery(
                "repair_1", case["case_id"], lease_token=lease["lease_token"],
                run_id=item["run_id"], generation=item["attempt"],
                candidate_sha=candidate, state="resolved",
            )
            self.assertEqual(done["state"], "resolved")
            self.assertEqual(self.supervisor.status()["lanes"][0]["state"], "idle")
        finally:
            subprocess.run(
                ["git", "-C", str(self.repo), "worktree", "remove", "--force", str(worktree)],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )

    def test_external_blocker_fences_task_without_recovery_generation(self):
        self.state.set_task("V3-001", "failed", error="qc_rejected")
        case = self.supervisor.triage_failure("V3-001", "qc_rejected", generation=1)
        result = self.supervisor.mark_external_blocker(
            case["case_id"], "credential_required", "credential_required",
        )
        self.assertEqual(result["state"], "external_blocker")
        self.assertEqual(self.state.list_tasks()[0]["status"], "blocked")
        self.assertEqual(self.supervisor.status()["cases"], {"external_blocker": 1})
        with self.state.db() as db:
            self.assertIsNone(db.execute("SELECT 1 FROM rebuild_queue WHERE parent_id='V3-001'").fetchone())

    def test_external_resolution_never_reopens_windows_without_device_evidence(self):
        evidence = self.state.home / "private" / "win-002.json"
        evidence.write_text(json.dumps({"task_id": "WIN-002"}) + "\n", encoding="utf-8")
        os.chmod(evidence, 0o600)
        with self.assertRaisesRegex(ValueError, "real Windows device evidence"):
            self.supervisor.resolve_external("WIN-002", evidence)

    def test_research_external_evidence_binds_report_and_limits(self):
        report = self.state.home / "worktrees" / "res-015" / "benchmark.md"
        report.parent.mkdir(parents=True)
        report.write_text("live benchmark\n", encoding="utf-8")
        evidence = {
            "benchmark_status": "ready_for_qc",
            "known_limitations": ["chapter timestamps are not caption offsets"],
            "live_source_count": 2,
            "no_credentials_used": True,
            "report_path": str(report),
            "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            "source_ids": ["python_docs", "youtube"],
            "timestamped_source_count": 2,
        }
        self.supervisor._validate_research_benchmark_evidence(evidence)
        evidence["report_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.supervisor._validate_research_benchmark_evidence(evidence)

    def test_external_blocker_clears_stale_pending_claim_and_survives_refresh(self):
        with self.state.db() as db:
            db.execute(
                "INSERT INTO pending_queue(parent_id,project_id,enqueue_seq,available_at,created_at) "
                "SELECT id,project_id,1,0,? FROM tasks WHERE id='V3-001' "
                "ON CONFLICT(parent_id) DO UPDATE SET available_at=excluded.available_at",
                ("2026-01-01T00:00:00+00:00",),
            )
            db.execute("UPDATE subtasks SET status='running' WHERE id='V3-001.S01'")
        case = self.supervisor.triage_failure("V3-001", "credential_required", generation=1)
        with self.state.db() as db:
            db.execute("UPDATE tasks SET status='pending',last_error='credential_required' WHERE id='V3-001'")
        result = self.supervisor.mark_external_blocker(
            case["case_id"], "credential_required", "credential_required",
        )
        self.assertEqual(result["state"], "external_blocker")
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id='V3-001'").fetchone()[0], "blocked")
            self.assertIsNone(db.execute("SELECT 1 FROM pending_queue WHERE parent_id='V3-001'").fetchone())
            self.assertEqual(db.execute("SELECT status FROM subtasks WHERE id='V3-001.S01'").fetchone()[0], "waiting")
            db.execute("UPDATE tasks SET status='pending' WHERE id='V3-001'")
            self.state._refresh_project_queues_db(db, "ARCHON-JARVIS-V2")
            self.assertEqual(db.execute("SELECT status FROM tasks WHERE id='V3-001'").fetchone()[0], "blocked")
            self.assertIsNone(db.execute("SELECT 1 FROM pending_queue WHERE parent_id='V3-001'").fetchone())

    def test_reopen_failed_readmits_stale_batch_member_without_erasing_case(self):
        batch = self.supervisor.start_batch("ARCHON-V3-TRIAL-001", limit=1)
        self.assertEqual(batch["admitted"], ["V3-001"])
        for member_state in ("external_blocker", "running"):
            self.state.set_task("V3-001", "failed", error="quota_or_rate_limit")
            case = self.supervisor.triage_failure("V3-001", "quota_or_rate_limit", generation=1)
            with self.state.db() as db:
                db.execute(
                    "UPDATE batch_members SET state=? WHERE batch_id=? AND parent_id=?",
                    (member_state, "ARCHON-V3-TRIAL-001", "V3-001"),
                )

            self.assertEqual(self.state.reopen_failed(["V3-001"]), ["V3-001"])
            with self.state.db() as db:
                task_row = db.execute("SELECT status FROM tasks WHERE id='V3-001'").fetchone()
                case_row = db.execute(
                    "SELECT state FROM supervisor_cases WHERE case_id=?", (case["case_id"],)
                ).fetchone()
                member_row = db.execute(
                    "SELECT state FROM batch_members WHERE batch_id=? AND parent_id=?",
                    ("ARCHON-V3-TRIAL-001", "V3-001"),
                ).fetchone()
                queue_row = db.execute("SELECT 1 FROM pending_queue WHERE parent_id='V3-001'").fetchone()
            self.assertEqual(task_row["status"], "pending")
            self.assertEqual(case_row["state"], "reopened")
            self.assertEqual(member_row["state"], "admitted")
            self.assertIsNotNone(queue_row)

    def test_expired_recovery_lease_is_fenced_after_process_loss(self):
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        case = self.supervisor.triage_failure("V3-001", "no_file_changes", generation=1)
        lease = self.supervisor.claim_recovery(case["case_id"], "repair_1")
        recovery_item = self.state.claim_recovery_task(lease)
        with self.state.db() as db:
            db.execute(
                "UPDATE supervisor_lanes SET updated_at=? WHERE lane_id='repair_1'",
                ("2000-01-01T00:00:00+00:00",),
            )
        expired = self.supervisor.reconcile_recovery_leases(60)
        self.assertEqual(expired["count"], 1)
        with self.state.db() as db:
            task = db.execute("SELECT status,last_run FROM tasks WHERE id='V3-001'").fetchone()
            lane = db.execute("SELECT state FROM supervisor_lanes WHERE lane_id='repair_1'").fetchone()
        self.assertEqual(dict(task), {"status": "interrupted", "last_run": ""})
        self.assertEqual(lane[0], "idle")
        with self.assertRaisesRegex(ValueError, "stale_worker_lease"):
            self.state.set_task(
                "V3-001", "failed", error="worker_runtime_error",
                run_id=recovery_item["run_id"], attempt=recovery_item["attempt"],
            )

    def test_stale_worker_cannot_write_after_retry_generation_changes(self):
        first = self.state.claim()
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        self.state.retry("V3-001")
        second = self.state.claim()
        self.assertNotEqual(first["run_id"], second["run_id"])
        with self.assertRaisesRegex(ValueError, "stale_worker_lease"):
            self.state.set_task(
                "V3-001", "failed", error="worker_runtime_error",
                run_id=first["run_id"], attempt=first["attempt"],
            )

    def test_resolved_recovery_rejects_empty_unbound_candidate(self):
        self.state.set_task("V3-001", "failed", error="no_file_changes")
        case = self.supervisor.triage_failure("V3-001", "no_file_changes", generation=1)
        lease = self.supervisor.claim_recovery(case["case_id"], "repair_1")
        recovery_item = self.state.claim_recovery_task(lease)
        head = self.state.get("integration_sha")
        with self.state.db() as db:
            db.execute(
                "UPDATE tasks SET status='completed',candidate_sha=?,integrated_sha=? WHERE id=?",
                ("d" * 40, head, "V3-001"),
            )
        with self.assertRaisesRegex(ValueError, "bound candidate"):
            self.supervisor.finish_recovery(
                "repair_1", case["case_id"], lease_token=lease["lease_token"],
                run_id=recovery_item["run_id"], generation=recovery_item["attempt"],
                candidate_sha="", state="resolved",
            )

    def test_active_batch_excludes_members_from_a_second_batch(self):
        first = self.supervisor.start_batch("ARCHON-V3-TRIAL-001", limit=1)
        second = self.supervisor.start_batch("ARCHON-V3-TRIAL-002", limit=1)
        self.assertEqual(first["admitted"], ["V3-001"])
        self.assertNotIn("V3-001", second["admitted"])

    def test_upgrade_candidate_without_tests_is_rejected(self):
        repo = self.repo
        subprocess.run(["git", "-C", str(repo), "rm", "-qr", "tests"], check=True)
        subprocess.run([
            "git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@local.invalid",
            "commit", "-qm", "remove test suite",
        ], check=True)
        candidate = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        with self.assertRaisesRegex(ValueError, "upgrade test suite unavailable"):
            self.supervisor._run_candidate_tests(repo, candidate)

    def test_batch_and_upgrade_checkpoints_are_not_model_authority(self):
        batch = self.supervisor.start_batch("ARCHON-V3-TRIAL-001", limit=1)
        self.assertEqual(batch["admitted"], ["V3-001"])
        self.assertEqual(self.supervisor.batch_status("ARCHON-V3-TRIAL-001")["completed_count"], 0)
        self.assertEqual(self.state.claim(batch_id="ARCHON-V3-TRIAL-001")["task"]["task_id"], "V3-001")
        head = self.state.get("integration_sha")
        upgrade = self.supervisor.create_upgrade("upgrade-1", head, head)
        self.assertEqual(upgrade["state"], "PROPOSED")
        self.supervisor.transition_upgrade("upgrade-1", "PATCH_IN_ISOLATION")
        self.supervisor.run_upgrade_check("upgrade-1", "TESTED", head)
        self.supervisor.transition_upgrade("upgrade-1", "TESTED")
        self.supervisor.run_upgrade_check("upgrade-1", "BACKUP", head)
        self.supervisor.transition_upgrade("upgrade-1", "DRAIN_NEW_CLAIMS")
        self.supervisor.run_upgrade_check("upgrade-1", "CANARY", head)
        self.supervisor.transition_upgrade("upgrade-1", "STAGED_CANARY")
        self.supervisor.run_upgrade_check("upgrade-1", "HEALTH", head)
        self.supervisor.transition_upgrade("upgrade-1", "HEALTH_SOAK")
        with self.assertRaisesRegex(ValueError, "invalid upgrade state"):
            self.supervisor.transition_upgrade("upgrade-1", "COMMITTED")


if __name__ == "__main__":
    unittest.main()
