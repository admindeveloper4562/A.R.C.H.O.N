import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from astra_one.linux_sda import State, task_spec, git, assert_source
from astra_one.linux_runtime import (
    ChangeValidationError,
    DockerTestError,
    ReviewFailure,
    check_changes,
    codex_call,
    codex_command,
    docker_test,
    integrate,
    merger_review_result,
    _bounded_patch_preview,
    ensure_integration,
    independent_qc,
    make_prompt,
    review_failure_code,
    review_finding_codes,
    worker_failure_code,
)
from astra_one.linux_cli import run_master


def git_repo(root):
    root.mkdir()
    subprocess.run(["git","init","-q","-b","develop",str(root)],check=True)
    (root/"README.md").write_text("initial\n")
    (root/"tests").mkdir()
    (root/"tests"/"test_dummy.py").write_text("import unittest\nclass Test(unittest.TestCase):\n    def test_ok(self): assert True\n")
    subprocess.run(["git","-C",str(root),"add","."],check=True)
    subprocess.run(["git","-C",str(root),"-c","user.name=test","-c","user.email=test@local.invalid","commit","-qm","initial"],check=True)
    return root


def task(i, deps=None):
    return {"task_id":f"ASTRA-{i:03}","objective":"Build a tiny independent implementation slice", "acceptance":["Must have working tests"],"depends_on":deps or [],"area":"foundation"}


def audit_task(i=1):
    return {
        "task_id": f"BASE-{i:03}",
        "objective": "Capture bounded repository and host metadata",
        "acceptance": ["The report distinguishes facts from unknowns"],
        "area": "base",
        "execution_mode": "audit",
        "subtasks": [{
            "id": f"BASE-{i:03}.S01",
            "kind": "record",
            "sequence": 1,
            "depends_on": [],
            "instruction": "Write the bounded report.",
            "deliverable": "Versioned report",
            "done_when": "Facts and unknowns are explicit",
            "evidence_required": True,
        }],
    }

class LinuxSDATests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.repo=git_repo(self.base/"source")
        self.state=State(self.base/"state")
        self.state.init(self.repo)
        arch=self.base/"architecture.md"
        arch.write_text("# JARVIS v2 approved architecture\nSafe repository coding only.\n")
        self.sha=self.state.import_architecture(arch)
        self.state.approve_architecture(self.sha)

    def test_worker_failure_categories_are_bounded(self):
        self.assertEqual(worker_failure_code(sqlite3.OperationalError("database is locked")),"state_database_locked")
        self.assertEqual(worker_failure_code(KeyError("passed")),"worker_result_invalid")
        self.assertEqual(worker_failure_code(UnicodeDecodeError("utf-8",b"\\xff",0,1,"bad")),"worker_output_invalid")
        self.assertEqual(worker_failure_code(ValueError("unexpected detail")),"worker_input_invalid")
        self.assertEqual(worker_failure_code(DockerTestError("docker_access_denied")),"docker_access_denied")

    def test_review_rejections_keep_only_bounded_repair_categories(self):
        findings = [
            "private payload may be exposed",
            "test coverage does not prove the acceptance criteria",
            "ordering behavior is ambiguous",
        ]
        self.assertEqual(review_finding_codes(findings), ("acceptance_gap", "ordering_semantics", "payload_exposure", "test_gap"))
        code = review_failure_code("qc_rejected", findings)
        self.assertEqual(code, "qc_rejected:acceptance_gap,ordering_semantics,payload_exposure,test_gap")
        self.assertEqual(worker_failure_code(ReviewFailure(code)), code)
        self.assertLessEqual(len(code), 160)

    def test_repair_prompt_contains_only_bounded_guidance(self):
        prompt = make_prompt(
            task(1),
            "a" * 40,
            "b" * 64,
            "repairer",
            "merger_rejected:payload_exposure,source_provenance",
        )
        self.assertIn("Previous bounded failure categories", prompt)
        self.assertIn("never expose task payloads", prompt)
        self.assertIn("exact approved source identity", prompt)
        self.assertNotIn("private payload may be exposed", prompt)

    def test_repair_prompt_covers_merge_and_scope_failures(self):
        prompt = make_prompt(
            task(1),
            "a" * 40,
            "b" * 64,
            "repairer",
            "git_diff_check_failed;protected_file_modified",
        )
        self.assertIn("remove trailing whitespace", prompt)
        self.assertIn("do not modify protected policy files", prompt)

    def test_ci_local_only_prompt_preserves_quota_boundary(self):
        ci_task = task(1)
        ci_task["execution_mode"] = "ci_local_only"
        ci_task["task_id"] = "BASE-003"
        prompt = make_prompt(ci_task, "a" * 40, "b" * 64, "worker")
        self.assertIn("do not trigger GitHub Actions", prompt)
        self.assertIn("DEFERRED_QUOTA", prompt)
        self.assertIn("network-dependent downloads", prompt)
        self.assertIn("full immutable commit SHA", prompt)

    def test_task_specific_packaging_guidance_requires_manifest_update(self):
        packaging_task = task(1)
        packaging_task["task_id"] = "BASE-010"
        prompt = make_prompt(packaging_task, "a" * 40, "b" * 64, "repairer")
        self.assertIn("manifest hash for every new tracked package file", prompt)

    def test_audit_prompt_is_report_only_and_metadata_bounded(self):
        prompt = make_prompt(audit_task(), "a" * 40, "b" * 64, "worker")
        self.assertIn("Audit-mode contract", prompt)
        self.assertIn("candidate change is a versioned Markdown or JSON report below docs/", prompt)
        self.assertIn("Record inaccessible or unavailable evidence as unknown", prompt)
        self.assertIn("Do not add tools, tests, source", prompt)

    def test_source_dirty_refused(self):
        (self.repo/"README.md").write_text("modified\n")
        with self.assertRaisesRegex(ValueError,"dirty"):
            assert_source(self.repo)

    def test_architecture_approval_explicit(self):
        p=self.base/"another.md";p.write_text("# Other architecture\nChanged requirements.\n")
        self.state.import_architecture(p)
        with self.assertRaisesRegex(ValueError,"not approved"):
            self.state.add_tasks(task(1))

    def test_dependency_blocks_claim_until_integrated(self):
        self.state.add_tasks([task(1),task(2,["ASTRA-001"])])
        item=self.state.claim()
        self.assertEqual(item["task"]["task_id"],"ASTRA-001")
        self.assertIsNone(self.state.claim())
        self.state.set_task("ASTRA-001","completed")
        self.assertEqual(self.state.claim()["task"]["task_id"],"ASTRA-002")

    def test_stop_and_pause_gate(self):
        self.state.add_tasks(task(1))
        for marker in ("STOP","PAUSE","PAUSED_QUOTA"):
            (self.state.home/marker).touch()
            self.assertIsNone(self.state.claim())
            (self.state.home/marker).unlink()
        self.assertIsNotNone(self.state.claim())

    def test_recover_no_replay(self):
        self.state.add_tasks(task(1));self.state.claim()
        self.assertEqual(self.state.recover(),["ASTRA-001"])
        self.assertEqual(self.state.list_tasks()[0]["status"],"interrupted")
        self.state.retry("ASTRA-001")
        self.assertEqual(self.state.list_tasks()[0]["status"],"queued")

    def test_retry_claim_clears_stale_attempt_fields_but_keeps_history(self):
        self.state.add_tasks(task(1))
        first=self.state.claim()
        self.state.set_task("ASTRA-001","failed",error="no_file_changes",
                            fields={"candidate_sha":"a"*40,"changed_files":"[\"old.py\"]",
                                    "qc_evidence":"old-review","base_sha":"b"*40,
                                    "branch":"feat/core/old","worktree":"/old"})
        self.state.retry("ASTRA-001")
        second=self.state.claim()
        self.assertEqual(second["prior_error"],"no_file_changes")
        with self.state.db() as db:
            row=db.execute("SELECT last_error,candidate_sha,changed_files,qc_evidence,base_sha,branch,worktree FROM tasks WHERE id='ASTRA-001'").fetchone()
        self.assertEqual(tuple(row),("","","[]","","","",""))
        self.assertEqual(self.state.failure_codes("ASTRA-001"),["no_file_changes"])

    def test_failed_and_retried_tasks_leave_no_stale_review_or_merge_queue(self):
        self.state.add_tasks(task(1))
        self.state.claim()
        self.state.set_task("ASTRA-001", "awaiting_review", fields={
            "candidate_sha": "a" * 40,
            "changed_files": '["candidate.py"]',
            "qc_evidence": "reviewed",
            "project_id": "PROJECT-1",
        })
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM review_queue WHERE parent_id='ASTRA-001'").fetchone()[0], 1)
        self.state.set_task("ASTRA-001", "failed", error="git_diff_check_failed")
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM review_queue WHERE parent_id='ASTRA-001'").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM merge_queue WHERE parent_id='ASTRA-001'").fetchone()[0], 0)
        self.state.retry("ASTRA-001")
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM review_queue WHERE parent_id='ASTRA-001'").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT count(*) FROM merge_queue WHERE parent_id='ASTRA-001'").fetchone()[0], 0)

    def test_tool_count_is_persisted_on_run_transitions(self):
        self.state.add_tasks(task(1))
        self.state.claim()
        self.state.set_task("ASTRA-001", "verifying", fields={"tool_count": 7})
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT tool_count FROM runs WHERE task_id='ASTRA-001'").fetchone()[0], 7)
        self.state.set_task("ASTRA-001", "failed", error="no_file_changes", fields={"tool_count": 8})
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT tool_count FROM runs WHERE task_id='ASTRA-001'").fetchone()[0], 8)

    def test_reopen_failed_starts_new_generation_without_erasing_history(self):
        self.state.add_tasks(task(1))
        for code in ("qc_rejected:input_validation", "qc_rejected:permission_scope"):
            self.state.claim()
            self.state.set_task("ASTRA-001", "failed", error=code)
            if code != "qc_rejected:permission_scope":
                self.state.retry("ASTRA-001")

        self.assertEqual(self.state.reopen_failed(["ASTRA-001"]), ["ASTRA-001"])
        claim = self.state.claim()
        self.assertEqual(claim["attempt"], 1)
        self.assertEqual(claim["prior_error"], "")
        self.assertEqual(self.state.failure_codes("ASTRA-001"), [])
        with self.state.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM runs WHERE task_id='ASTRA-001'").fetchone()[0], 3)
        self.state.set_task("ASTRA-001", "failed", error="qc_rejected:permission_scope")
        self.assertEqual(self.state.failure_codes("ASTRA-001"), ["qc_rejected:permission_scope"])

    def test_plan_is_atomic(self):
        with self.assertRaisesRegex(ValueError,"dependencies"):
            self.state.add_tasks([task(1),task(2,["ASTRA-999"])])
        self.assertEqual(self.state.list_tasks(),[])

    def test_task_rejects_unknown_fields(self):
        obj=task(1);obj["api_key"]="secret"
        with self.assertRaises(ValueError):task_spec(obj)

    def test_model_cli_is_codex_cloud_not_oss(self):
        cmd=codex_command(self.repo,"gpt-5.6-luna","medium",None,"workspace-write")
        self.assertNotIn("--oss",cmd)
        self.assertIn("model_reasoning_effort=medium",cmd)
        self.assertIn("agents.enabled=false",cmd)
        self.assertIn("--ephemeral",cmd)

    def test_danger_bypass_is_explicit_and_omits_normal_sandbox(self):
        cmd=codex_command(self.repo,"gpt-5.6-luna","medium",None,"workspace-write",danger_bypass=True)
        self.assertIn("--dangerously-bypass-approvals-and-sandbox",cmd)
        self.assertNotIn("--sandbox",cmd)

    def test_static_change_accepts_valid_python(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"candidate.py").write_text("def f():\n    return 7\n")
        self.assertEqual(check_changes(self.repo,b),["candidate.py"])

    def test_static_change_accepts_multiple_files_within_limit(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"one.py").write_text("value = 1\n")
        (self.repo/"two.json").write_text('{"value": 2}\n')
        self.assertEqual(check_changes(self.repo,b),["one.py","two.json"])

    def test_static_change_accepts_javascript_module_files(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"worker.test.mjs").write_text("export const ok = true;\n")
        self.assertEqual(check_changes(self.repo,b),["worker.test.mjs"])

    def test_static_change_rejects_generated_artifact_paths(self):
        b=git(self.repo,"rev-parse","HEAD")
        output=self.repo/"ci-artifacts"/"report.json"
        output.parent.mkdir()
        output.write_text('{"status":"passed"}\n')
        with self.assertRaisesRegex(ChangeValidationError,"generated_artifact"):
            check_changes(self.repo,b)

    def test_static_change_rejects_zero_files_with_specific_code(self):
        b=git(self.repo,"rev-parse","HEAD")
        with self.assertRaises(ChangeValidationError) as caught:
            check_changes(self.repo,b)
        self.assertEqual(caught.exception.code,"no_file_changes")

    def test_static_change_rejects_file_limit_with_specific_code(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"one.py").write_text("value = 1\n")
        (self.repo/"two.py").write_text("value = 2\n")
        with patch("astra_one.linux_runtime.MAX_FILES",1):
            with self.assertRaises(ChangeValidationError) as caught:
                check_changes(self.repo,b)
        self.assertEqual(caught.exception.code,"changed_file_limit_exceeded")

    def test_static_change_parses_staged_and_unstaged_porcelain(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"staged.py").write_text("value = 1\n")
        git(self.repo,"add","--","staged.py")
        (self.repo/"staged.py").write_text("value = 2\n")
        self.assertEqual(check_changes(self.repo,b),["staged.py"])

    def test_static_change_rejects_trailing_whitespace_in_untracked_and_staged_files(self):
        b=git(self.repo,"rev-parse","HEAD")
        report=self.repo/"report.md"
        report.write_text("# report  \n")
        with self.assertRaises(ChangeValidationError) as caught:
            check_changes(self.repo,b)
        self.assertEqual(caught.exception.code,"git_diff_check_failed")

        git(self.repo,"add","--","report.md")
        with self.assertRaises(ChangeValidationError) as caught:
            check_changes(self.repo,b)
        self.assertEqual(caught.exception.code,"git_diff_check_failed")

    def test_static_change_rejects_delete(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"README.md").unlink()
        with self.assertRaisesRegex(ValueError,"delete"):
            check_changes(self.repo,b)

    def test_static_change_rejects_symlink(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"evil.py").symlink_to("/etc/passwd")
        with self.assertRaisesRegex(ValueError,"ordinary"):
            check_changes(self.repo,b)

    def test_static_change_rejects_policy(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"AGENTS.md").write_text("fake policy")
        with self.assertRaisesRegex(ValueError,"protected"):
            check_changes(self.repo,b)

    def test_scoped_ci_workflow_repair_can_change_only_workflow_yaml(self):
        b=git(self.repo,"rev-parse","HEAD")
        workflow=self.repo/".github"/"workflows"/"ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: local\n")
        scoped_task={
            "suggested_scope_roots":[".github/"],
            "subtasks":[{"kind":"repair"}],
        }
        self.assertEqual(check_changes(self.repo,b,task=scoped_task),[".github/workflows/ci.yml"])

    def test_scoped_ci_workflow_rejects_new_floating_action_ref(self):
        b=git(self.repo,"rev-parse","HEAD")
        workflow=self.repo/".github"/"workflows"/"ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n")
        scoped_task={
            "suggested_scope_roots":[".github/"],
            "subtasks":[{"kind":"repair"}],
        }
        with self.assertRaisesRegex(ChangeValidationError,"ci_workflow_unpinned_action"):
            check_changes(self.repo,b,task=scoped_task)

    def test_scoped_ci_workflow_accepts_immutable_action_ref(self):
        b=git(self.repo,"rev-parse","HEAD")
        workflow=self.repo/".github"/"workflows"/"ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@0123456789abcdef0123456789abcdef01234567\n")
        scoped_task={
            "suggested_scope_roots":[".github/"],
            "subtasks":[{"kind":"repair"}],
        }
        self.assertEqual(check_changes(self.repo,b,task=scoped_task),[".github/workflows/ci.yml"])

    def test_ci_workflow_scope_does_not_allow_other_hidden_paths(self):
        b=git(self.repo,"rev-parse","HEAD")
        policy=self.repo/".github"/"CODEOWNERS"
        policy.parent.mkdir(parents=True)
        policy.write_text("* @owner\n")
        scoped_task={
            "suggested_scope_roots":[".github/"],
            "subtasks":[{"kind":"repair"}],
        }
        with self.assertRaisesRegex(ValueError,"protected"):
            check_changes(self.repo,b,task=scoped_task)

    def test_audit_scope_accepts_only_documentation_receipts(self):
        b=git(self.repo,"rev-parse","HEAD")
        report=self.repo/"docs"/"tasks"/"BASE-001_AUDIT.md"
        report.parent.mkdir(parents=True)
        report.write_text("# bounded audit\n")
        self.assertEqual(check_changes(self.repo,b,task=audit_task()),["docs/tasks/BASE-001_AUDIT.md"])

    def test_audit_scope_rejects_executable_or_test_changes(self):
        b=git(self.repo,"rev-parse","HEAD")
        tool=self.repo/"tools"/"audit.py"
        tool.parent.mkdir(parents=True)
        tool.write_text("print('not an audit receipt')\n")
        with self.assertRaisesRegex(ChangeValidationError,"audit_report_only"):
            check_changes(self.repo,b,task=audit_task())

    def test_merger_preview_preserves_bounded_patch_tail(self):
        preview = _bounded_patch_preview(b"A" * 8_000 + b"TAIL-EVIDENCE", limit=8_000)
        self.assertIn("[middle of patch omitted]", preview)
        self.assertIn("TAIL-EVIDENCE", preview)
        self.assertLess(len(preview), 8_100)

    def test_audit_merger_prompt_accepts_explicit_unknowns(self):
        captured = {}

        def fake_merger_call(*, output_file, **kwargs):
            captured["prompt"] = kwargs["prompt"]
            output_file.write_text('{"verdict":"PASS","findings":[]}')
            return 0, 0, "ok"

        with patch("astra_one.linux_runtime.codex_call", side_effect=fake_merger_call):
            accepted, reason = merger_review_result(
                self.state, self.repo, "BASE-001", b"report\n" + b"x" * 20,
                model="gpt-5.6-luna", effort="medium", task=audit_task(),
            )
        self.assertTrue(accepted)
        self.assertEqual(reason, "merger_pass")
        self.assertIn("bounded Markdown or JSON evidence receipt", captured["prompt"])
        self.assertIn("Do not require the worker to invent main", captured["prompt"])

    def test_static_change_rejects_invalid_python(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"bad.py").write_text("def (")
        with self.assertRaises(ChangeValidationError) as caught:
            check_changes(self.repo,b)
        self.assertEqual(caught.exception.code,"invalid_changed_file")

    def test_codex_success_without_file_changes_is_not_a_worker_success(self):
        executable=self.base/"no-edit-codex"
        executable.write_text("""#!/usr/bin/env python3
import json
print(json.dumps({'type':'turn.completed'}))
""")
        executable.chmod(0o755)
        with patch.dict(os.environ,{"ASTRA_CODEX_BIN":str(executable)}), patch("astra_one.linux_runtime.sandbox_status",return_value={"available":True,"reason":"test"}):
            rc,tools,reason=codex_call(worktree=self.repo,prompt="do nothing",home=self.state.home,state=self.state,
                                       model="gpt-5.6-luna",effort="medium",sandbox="workspace-write",timeout=60)
        self.assertEqual((rc,tools,reason),(0,0,"ok"))
        with self.assertRaisesRegex(ChangeValidationError,"no_file_changes"):
            check_changes(self.repo,git(self.repo,"rev-parse","HEAD"))

    def test_independent_qc_receives_validated_untracked_paths(self):
        candidate = self.repo / "candidate.py"
        candidate.write_text("WORKER_ID = 'QUAL-001'\n")
        base = git(self.repo,"rev-parse","HEAD")
        changed = check_changes(self.repo,base)
        captured = {}

        def fake_qc_call(*, output_file, **kwargs):
            captured["prompt"] = kwargs["prompt"]
            output_file.write_text('{"verdict":"PASS","findings":[]}')
            return 0, 0, "ok"

        with patch("astra_one.linux_runtime.codex_call", side_effect=fake_qc_call):
            accepted, reason = independent_qc(
                self.state, self.repo, task(1), model="gpt-5.6-luna", effort="medium",
                changed_files=changed,
            )
        self.assertTrue(accepted)
        self.assertEqual(reason,"qc_pass")
        self.assertIn("candidate.py", captured["prompt"])
        self.assertIn("ordinary diff omits untracked files", captured["prompt"])

    def test_codex_failed_file_change_event_is_reported(self):
        executable=self.base/"failed-edit-codex"
        executable.write_text("""#!/usr/bin/env python3
import json
print(json.dumps({'type':'item.completed','item':{'type':'file_change','status':'failed'}}))
""")
        executable.chmod(0o755)
        with patch.dict(os.environ,{"ASTRA_CODEX_BIN":str(executable)}), patch("astra_one.linux_runtime.sandbox_status",return_value={"available":True,"reason":"test"}):
            rc,tools,reason=codex_call(worktree=self.repo,prompt="edit",home=self.state.home,state=self.state,
                                       model="gpt-5.6-luna",effort="medium",sandbox="workspace-write",timeout=60)
        self.assertEqual(rc,0)
        self.assertEqual(reason,"codex_file_change_failed")

    def test_codex_sandbox_failure_is_reported_before_process_start(self):
        with patch("astra_one.linux_runtime.sandbox_status",return_value={"available":False,"reason":"user_namespace_unavailable"}), patch("astra_one.linux_runtime.subprocess.Popen") as start:
            result=codex_call(worktree=self.repo,prompt="edit",home=self.state.home,state=self.state,
                              model="gpt-5.6-luna",effort="medium",sandbox="workspace-write",timeout=60)
        self.assertEqual(result,(126,0,"sandbox_unavailable"))
        start.assert_not_called()

    def test_docker_qc_stages_linked_worktree_with_private_git_index(self):
        candidate = self.base / "linked-candidate"
        candidate.mkdir()
        (candidate / ".git").write_text("gitdir: /outside/metadata\n")
        (candidate / "tests").mkdir()
        (candidate / "tests" / "test_candidate.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self): pass\n"
        )
        docker_calls = []
        real_run = subprocess.run

        def fake_run(args, *rest, **kwargs):
            if args and args[0] == "docker":
                docker_calls.append(list(args))
                if args[1:3] == ["image", "inspect"]:
                    return subprocess.CompletedProcess(args, 0, "", "")
                return subprocess.CompletedProcess(args, 0, "Ran 1 test in 0.01s\nOK\n", "")
            return real_run(args, *rest, **kwargs)

        with patch("astra_one.linux_runtime.subprocess.run", side_effect=fake_run):
            result = docker_test(candidate, "python:3.12-slim", ["python3", "-m", "unittest", "discover"])

        self.assertTrue(result["passed"])
        mount = docker_calls[1][docker_calls[1].index("--mount") + 1]
        staged = Path(mount.split(",", 2)[1].split("=", 1)[1])
        self.assertNotEqual(staged, candidate.resolve())
        self.assertFalse(staged.exists())
        self.assertIn("GIT_CONFIG_VALUE_0=/src", docker_calls[1])

    def test_five_worker_parallel_scheduler(self):
        self.state.add_tasks([task(i) for i in range(1,6)])
        lock=threading.Lock()
        current=[0]; peak=[0]
        def fake_execute(state,item,**kwargs):
            with lock:
                current[0]+=1;peak[0]=max(peak[0],current[0])
            time.sleep(0.16)
            state.set_task(item["task"]["task_id"],"awaiting_review")
            with lock:current[0]-=1
            return {"task_id":item["task"]["task_id"],"status":"awaiting_review"}
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":True,"reason":"test"}), patch("astra_one.linux_cli.execute_claim",side_effect=fake_execute):
            result=run_master(self.state,workers=5,max_tasks=5,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                              test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                              auto_integrate=False,max_repairs=0,timeout=60)
        self.assertEqual(peak[0],5)
        self.assertEqual(result["attempts"],5)
        self.assertEqual(result["qc_passed"],5)
        self.assertEqual(git(self.repo,"branch","--show-current"),"develop")

    def test_merger_safe_serial_integration(self):
        self.state.add_tasks(task(1))
        claim=self.state.claim()
        root=ensure_integration(self.state)
        branch="feature/astra-test-commit"
        candidate=self.state.home/"worktrees"/"candidate"
        git(self.repo,"worktree","add","-b",branch,str(candidate),self.state.get("integration_sha"))
        (candidate/"added.py").write_text("def foo():\n    return 'ok'\n")
        self.state.set_task("ASTRA-001","coding",fields={"worktree":str(candidate),"branch":branch,"base_sha":claim['task'] and self.state.get('integration_sha')})
        self.assertEqual(check_changes(candidate,self.state.get("integration_sha")),["added.py"])
        git(candidate,"add","--","added.py")
        git(candidate,"-c","user.name=as","-c","user.email=as@local.invalid","commit","-m","candidate")
        sha=git(candidate,"rev-parse","HEAD")
        self.state.set_task("ASTRA-001","awaiting_review",fields={"candidate_sha":sha,"qc_evidence":'[{"tests":"passed"}]'})
        self.state.approve("ASTRA-001")
        result=integrate(self.state,"ASTRA-001")
        self.assertEqual(result["status"],"completed")
        self.assertTrue((root/"added.py").exists())
        self.assertFalse((self.repo/"added.py").exists())
        self.assertEqual(git(self.repo,"branch","--show-current"),"develop")
        self.assertNotEqual(self.state.get("integration_sha"),self.state.get("source_sha"))

    def test_merger_rejection_fails_task_and_preserves_rebuild_queue(self):
        self.state.add_tasks(task(1))
        claim=self.state.claim()
        base=self.state.get("integration_sha")
        branch="feature/astra-test-merger-rejection"
        candidate=self.state.home/"worktrees"/"candidate-merger-rejection"
        git(self.repo,"worktree","add","-b",branch,str(candidate),base)
        (candidate/"added.py").write_text("VALUE = 1\n")
        changed=check_changes(candidate,base)
        git(candidate,"add","--",*changed)
        git(candidate,"-c","user.name=as","-c","user.email=as@local.invalid","commit","-m","candidate")
        sha=git(candidate,"rev-parse","HEAD")
        self.state.set_task("ASTRA-001","awaiting_review",fields={
            "worktree":str(candidate),"branch":branch,"base_sha":base,
            "candidate_sha":sha,"changed_files":json.dumps(changed),
            "qc_evidence":'{"independent_qc":"passed"}',
        })
        self.state.approve("ASTRA-001")
        with patch("astra_one.linux_runtime.merger_review_result",return_value=(False,"merger_rejected:payload_exposure")):
            with self.assertRaisesRegex(ReviewFailure,"merger_rejected:payload_exposure"):
                integrate(self.state,"ASTRA-001",merger_model="gpt-5.6-luna")
        row=self.state.list_tasks()[0]
        self.assertEqual(row["status"],"failed")
        self.assertEqual(row["last_error"],"merger_rejected:payload_exposure")
        with self.state.db() as db:
            self.assertIsNone(db.execute("SELECT 1 FROM merge_queue WHERE parent_id='ASTRA-001'").fetchone())

    def test_merger_rejects_candidate_trailing_whitespace_before_apply(self):
        self.state.add_tasks(task(1))
        claim=self.state.claim()
        base=self.state.get("integration_sha")
        branch="feature/astra-test-whitespace"
        candidate=self.state.home/"worktrees"/"candidate-whitespace"
        git(self.repo,"worktree","add","-b",branch,str(candidate),base)
        (candidate/"audit.md").write_text("# audit  \n")
        git(candidate,"add","--","audit.md")
        git(candidate,"-c","user.name=as","-c","user.email=as@local.invalid","commit","-m","candidate")
        sha=git(candidate,"rev-parse","HEAD")
        self.state.set_task("ASTRA-001","awaiting_review",fields={
            "worktree":str(candidate),"branch":branch,"base_sha":base,
            "candidate_sha":sha,"qc_evidence":"{\"independent_qc\":\"passed\"}",
        })
        self.state.approve("ASTRA-001")
        with self.assertRaisesRegex(ValueError,"git_diff_check_failed"):
            integrate(self.state,"ASTRA-001")
        self.assertEqual(self.state.list_tasks()[0]["status"],"failed")
        self.assertEqual(self.state.list_tasks()[0]["last_error"],"git_diff_check_failed")
        self.assertEqual(git(self.repo,"rev-parse","HEAD"),base)

    def test_integration_rejects_worktree_from_different_repository(self):
        other = git_repo(self.base/"other-source")
        self.state.put("integration_path",str(other))
        self.state.put("integration_branch",git(other,"branch","--show-current"))
        self.state.put("integration_sha",git(other,"rev-parse","HEAD"))
        with self.assertRaisesRegex(ValueError,"integration repository mismatch"):
            ensure_integration(self.state)

    def test_architecture_change_invalidates_old_queued_tasks(self):
        self.state.add_tasks(task(1))
        other=self.base/"updated-architecture.md"
        other.write_text("# Updated JARVIS v2 architecture\nDifferent instructions.\n")
        new_sha=self.state.import_architecture(other)
        self.state.approve_architecture(new_sha)
        self.assertIsNone(self.state.claim())
        self.state.add_tasks(task(2))
        self.assertEqual(self.state.claim()["task"]["task_id"],"ASTRA-002")

    def test_full_codex_pipeline_mocked_five_tasks(self):
        executable=self.base/"fake-codex"
        executable.write_text("""#!/usr/bin/env python3
import json, pathlib, re, sys
args=sys.argv[1:]
root=pathlib.Path(args[args.index('-C')+1])
prompt=sys.stdin.read()
if '--oss' in args:sys.exit(90)
if '--output-last-message' in args:
    pathlib.Path(args[args.index('--output-last-message')+1]).write_text(json.dumps({'verdict':'PASS','findings':[]}))
else:
    m=re.search(r'Task: (ASTRA-\\d+)',prompt)
    if not m:sys.exit(91)
    (root/(m.group(1).lower().replace('-','_')+'.py')).write_text('def value():\\n    return 42\\n')
print(json.dumps({'type':'item.completed','item':{'type':'file_change'}}))
""")
        executable.chmod(0o755)
        self.state.add_tasks([task(i) for i in range(1,6)])
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":True,"reason":"test"}), patch.dict(os.environ,{"ASTRA_CODEX_BIN":str(executable)}), patch("astra_one.linux_runtime.sandbox_status",return_value={"available":True,"reason":"test"}), patch("astra_one.linux_runtime.docker_test",return_value={"passed":True,"exit_code":0,"sandbox":"mock_docker"}):
            result=run_master(self.state,workers=5,max_tasks=5,max_minutes=2,model="gpt-5.6-luna",effort="medium",
                test_image="python:3.12-slim",test_command=["python3","-m","unittest"],auto_integrate=True,max_repairs=0,timeout=60)
        self.assertEqual(result["qc_passed"],5)
        self.assertEqual(result["failures_or_conflicts"],0)
        integrated=Path(self.state.get("integration_path"))
        self.assertEqual(len(list(integrated.glob("astra_*.py"))),5)
        self.assertTrue(all(t["status"]=="completed" for t in self.state.list_tasks()))
        self.assertEqual(git(self.repo,"branch","--show-current"),"develop")

    def test_repeated_worker_failure_stops_before_retry_ceiling(self):
        self.state.add_tasks(task(1))
        calls=[]
        def fake_execute(state,item,**kwargs):
            calls.append(item["attempt"])
            state.set_task(item["task"]["task_id"],"failed",error="no_file_changes")
            return {"task_id":item["task"]["task_id"],"status":"failed","error":"no_file_changes"}
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":True,"reason":"test"}), patch("astra_one.linux_cli.execute_claim",side_effect=fake_execute):
            result=run_master(self.state,workers=1,max_tasks=10,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                              test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                              auto_integrate=False,max_repairs=3,timeout=60)
        self.assertEqual(calls,[1,2])
        self.assertEqual(result["requeued"],1)
        self.assertEqual(result["terminal_failures"],1)
        self.assertEqual(result["state"],"paused")
        self.assertEqual(self.state.list_tasks()[0]["status"],"failed")
        self.assertEqual(self.state.failure_codes("ASTRA-001"),["no_file_changes","no_file_changes"])
        self.assertTrue((self.state.home/"PAUSE").is_file())

    def test_master_refuses_before_claim_when_sandbox_unavailable(self):
        self.state.add_tasks(task(1))
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":False,"reason":"user_namespace_unavailable"}):
            with self.assertRaisesRegex(ValueError,"sandbox_unavailable"):
                run_master(self.state,workers=1,max_tasks=1,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                           test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                           auto_integrate=False,max_repairs=0,timeout=60)
        self.assertEqual(self.state.list_tasks()[0]["status"],"queued")

    def test_danger_bypass_refuses_live_state(self):
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.LIVE_STATE",self.state.home):
            with self.assertRaisesRegex(ValueError,"danger_bypass_forbidden_for_live_state"):
                run_master(self.state,workers=1,max_tasks=1,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                           test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                           auto_integrate=False,max_repairs=0,timeout=60,danger_bypass=True)

    def test_worker_failure_can_recover_on_bounded_repair(self):
        self.state.add_tasks(task(1))
        calls=[]
        def fake_execute(state,item,**kwargs):
            calls.append(item["attempt"])
            if item["attempt"] == 1:
                state.set_task(item["task"]["task_id"],"failed",error="codex_file_change_failed")
                return {"task_id":item["task"]["task_id"],"status":"failed","error":"codex_file_change_failed"}
            state.set_task(item["task"]["task_id"],"awaiting_review")
            return {"task_id":item["task"]["task_id"],"status":"awaiting_review"}
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":True,"reason":"test"}), patch("astra_one.linux_cli.execute_claim",side_effect=fake_execute):
            result=run_master(self.state,workers=1,max_tasks=2,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                              test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                              auto_integrate=False,max_repairs=3,timeout=60)
        self.assertEqual(calls,[1,2])
        self.assertEqual(result["requeued"],1)
        self.assertEqual(result["terminal_failures"],0)
        self.assertEqual(result["qc_passed"],1)
        self.assertEqual(self.state.list_tasks()[0]["status"],"awaiting_review")

    def test_review_category_reaches_bounded_repair_prompt(self):
        self.state.add_tasks(task(1))
        prior_errors=[]
        def fake_execute(state,item,**kwargs):
            prior_errors.append(item["prior_error"])
            if item["attempt"] == 1:
                error="qc_rejected:security_boundary"
                state.set_task(item["task"]["task_id"],"failed",error=error)
                return {"task_id":item["task"]["task_id"],"status":"failed","error":error}
            state.set_task(item["task"]["task_id"],"awaiting_review")
            return {"task_id":item["task"]["task_id"],"status":"awaiting_review"}
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":True,"reason":"test"}), patch("astra_one.linux_cli.execute_claim",side_effect=fake_execute):
            result=run_master(self.state,workers=1,max_tasks=2,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                              test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                              auto_integrate=False,max_repairs=3,timeout=60)
        self.assertEqual(prior_errors,["", "qc_rejected:security_boundary"])
        self.assertEqual(result["queued_remaining"],0)
        self.assertEqual(self.state.list_tasks()[0]["status"],"awaiting_review")

    def test_repair_budget_can_drain_all_kickoff_tasks(self):
        self.state.add_tasks([task(i) for i in range(1,6)])
        calls=[]
        def fake_execute(state,item,**kwargs):
            tid=item["task"]["task_id"]
            attempt=item["attempt"]
            calls.append((tid,attempt))
            if attempt < 3:
                code="repairable_first" if attempt == 1 else "repairable_second"
                state.set_task(tid,"failed",error=code)
                return {"task_id":tid,"status":"failed","error":code}
            state.set_task(tid,"awaiting_review")
            return {"task_id":tid,"status":"awaiting_review"}
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.sandbox_status",return_value={"available":True,"reason":"test"}), patch("astra_one.linux_cli.execute_claim",side_effect=fake_execute):
            result=run_master(self.state,workers=5,max_tasks=15,max_minutes=1,model="gpt-5.6-luna",effort="medium",
                              test_image="python:3.12-slim",test_command=["python3","-m","unittest"],
                              auto_integrate=False,max_repairs=3,timeout=60)
        self.assertEqual(result["attempts"],15)
        self.assertEqual(result["requeued"],10)
        self.assertEqual(result["terminal_failures"],0)
        self.assertEqual(result["queued_remaining"],0)
        self.assertEqual(len(calls),15)
        self.assertTrue(all(t["status"]=="awaiting_review" for t in self.state.list_tasks()))

    def test_event_metadata_accepts_new_rebuild_branch_policy(self):
        self.state.add_tasks(task(1))
        claim = self.state.claim()
        sha = self.state.get("source_sha")
        # The v2 worker generates feat/<module>/<task-id>-... branch names.
        branch = "feat/core/CORE-301-implementation-a1-1234abcd"
        self.state.emit("ASTRA-001", claim["run_id"], stage="preflight",
                        step="worker_1_leased", branch=branch, base_sha=sha)
        with self.state.db() as db:
            row = db.execute("SELECT branch, stage, step FROM events").fetchone()
        self.assertEqual(tuple(row), (branch, "preflight", "worker_1_leased"))

    def test_event_metadata_rejects_unsafe_branch_prefix(self):
        self.state.add_tasks(task(1))
        claim = self.state.claim()
        sha = self.state.get("source_sha")
        with self.assertRaisesRegex(ValueError, "invalid progress event"):
            self.state.emit("ASTRA-001", claim["run_id"], stage="preflight",
                            step="worker_1_leased", branch="main", base_sha=sha)

    def test_event_metadata_schema(self):
        self.state.add_tasks(task(1));claim=self.state.claim()
        branch="feature/astra-test"
        sha=self.state.get("source_sha")
        self.state.emit("ASTRA-001",claim["run_id"],stage="coding",step="worker_1_codex_start",branch=branch,base_sha=sha)
        with self.state.db() as db:
            e=dict(db.execute("SELECT * FROM events").fetchone())
        self.assertEqual(e["step"],"worker_1_codex_start")
        self.assertNotIn("objective",json.dumps(e))
        self.assertNotIn("acceptance",json.dumps(e))

if __name__=="__main__":unittest.main()
