import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from astra_one.linux_sda import State, task_spec, git, assert_source
from astra_one.linux_runtime import check_changes, codex_command, integrate, ensure_integration
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

    def test_static_change_accepts_valid_python(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"candidate.py").write_text("def f():\n    return 7\n")
        self.assertEqual(check_changes(self.repo,b),["candidate.py"])

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

    def test_static_change_rejects_invalid_python(self):
        b=git(self.repo,"rev-parse","HEAD")
        (self.repo/"bad.py").write_text("def (")
        with self.assertRaises(SyntaxError):
            check_changes(self.repo,b)

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
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch("astra_one.linux_cli.execute_claim",side_effect=fake_execute):
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
        with patch("astra_one.linux_cli.os.geteuid",return_value=1000), patch.dict(os.environ,{"ASTRA_CODEX_BIN":str(executable)}), patch("astra_one.linux_runtime.docker_test",return_value={"passed":True,"exit_code":0,"sandbox":"mock_docker"}):
            result=run_master(self.state,workers=5,max_tasks=5,max_minutes=2,model="gpt-5.6-luna",effort="medium",
                test_image="python:3.12-slim",test_command=["python3","-m","unittest"],auto_integrate=True,max_repairs=0,timeout=60)
        self.assertEqual(result["qc_passed"],5)
        self.assertEqual(result["failures_or_conflicts"],0)
        integrated=Path(self.state.get("integration_path"))
        self.assertEqual(len(list(integrated.glob("astra_*.py"))),5)
        self.assertTrue(all(t["status"]=="completed" for t in self.state.list_tasks()))
        self.assertEqual(git(self.repo,"branch","--show-current"),"develop")

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
