"""Linux SDA command-line control plane: no automatic startup on installation."""
from __future__ import annotations

import argparse
import contextlib
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid

from .linux_sda import (DEFAULT_HOME, EFFORT, MAX_FAILURES, MAX_WORKERS, MODEL, State,
                        TASK_EXECUTION_MODES, TASK_ID, assert_source, control_blocked,
                        file_sha256, git, task_spec)
from .linux_runtime import codex_call, ensure_integration, integrate, execute_claim, sandbox_status
from .full_plan import load_full_plan
from .supervisor import SupervisorController

LIVE_STATE = (Path.home() / ".local" / "state" / "archon-astra").resolve()
LIVE_SOURCE = (Path.home() / "Projects" / "ARCHON-astra-source").resolve()


def report(obj: object):
    print(json.dumps(obj,indent=2,ensure_ascii=False,default=str))


def diagnose(source: Path | None) -> dict:
    tools={x:bool(shutil.which(x)) for x in ("git","codex","python3","docker")}
    authenticated=False
    version="unavailable"
    if tools["codex"]:
        try:
            p=subprocess.run(["codex","--version"],capture_output=True,text=True,timeout=10)
            version=p.stdout.strip()[:100] if p.returncode==0 else "error"
            p=subprocess.run(["codex","login","status"],capture_output=True,text=True,timeout=12)
            authenticated=p.returncode==0
        except (OSError,subprocess.TimeoutExpired):pass
    answer={"platform":platform.system(),"tools":tools,"codex":version,"authenticated":authenticated,
            "requested_model":MODEL,"effort":EFFORT,"model_entitlement":"must be verified on target account",
            "max_workers":MAX_WORKERS,"ollama_required":False,"sandbox":sandbox_status()}
    if source:
        try:
            p,sha=assert_source(source)
            answer["source"]={"path":str(p),"sha":sha,"clean":True}
        except (OSError,ValueError) as ex:
            answer["source_error"]=str(ex)
    return answer


SUPERVISOR_POLICY_FILES = (
    "AGENTS.md",
    "SECURITY.md",
    "CODING_HANDBOOK.md",
    "docs/architecture/JARVIS_V2_CONSOLIDATED.md",
)


def inspect_repository(source: Path) -> dict:
    """Return bounded, hash-only citations for a clean pinned checkout."""
    root, source_sha = assert_source(source)
    tree_sha = git(root, "rev-parse", f"{source_sha}^{{tree}}")
    citations = []
    for relative in SUPERVISOR_POLICY_FILES:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError("supervisor_policy_missing")
        size = path.stat().st_size
        if size > 64_000:
            raise ValueError("supervisor_policy_too_large")
        citations.append({
            "path": relative,
            "blob_sha": git(root, "rev-parse", f"{source_sha}:{relative}"),
            "sha256": file_sha256(path),
            "bytes": size,
        })
    if git(root, "rev-parse", "HEAD") != source_sha or git(
            root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("repository_changed_during_inspection")
    citation_sha = hashlib.sha256(
        json.dumps(citations, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "read_only": True,
        "source_sha": source_sha,
        "tree_sha": tree_sha,
        "branch": git(root, "branch", "--show-current") or "detached",
        "citations": citations,
        "citation_sha256": citation_sha,
    }


def _bounded_requirement_text(value: object, *, name: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"requirements_{name}_invalid")
    return value


def parse_requirements(task: object) -> dict:
    """Normalize one parent/child packet without changing its acceptance text."""
    if not isinstance(task, dict):
        raise ValueError("requirements_invalid")
    task_id = task.get("task_id", task.get("id"))
    if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
        raise ValueError("requirements_task_id_invalid")
    objective = task.get("objective") or task.get("description") or task.get("title")
    objective = _bounded_requirement_text(objective, name="objective", limit=3_000)
    acceptance = task.get("acceptance")
    if isinstance(acceptance, str):
        acceptance = [acceptance]
    if (not isinstance(acceptance, list) or not 1 <= len(acceptance) <= 15
            or any(not isinstance(item, str) or not 5 <= len(item) <= 500 for item in acceptance)):
        raise ValueError("requirements_acceptance_invalid")
    dependencies = task.get("depends_on", task.get("dependencies", []))
    if (not isinstance(dependencies, list) or len(dependencies) > 20
            or any(not isinstance(item, str) or not TASK_ID.fullmatch(item) for item in dependencies)
            or len(set(dependencies)) != len(dependencies)):
        raise ValueError("requirements_dependencies_invalid")
    mode = task.get("execution_mode", "implementation")
    if mode not in TASK_EXECUTION_MODES:
        raise ValueError("requirements_execution_mode_invalid")
    scope_roots = task.get("suggested_scope_roots", [])
    if (not isinstance(scope_roots, list) or len(scope_roots) > 20
            or any(not isinstance(item, str) or not item or item.startswith(("/", "\\"))
                   or ".." in Path(item).parts or "\\" in item for item in scope_roots)):
        raise ValueError("requirements_scope_invalid")
    children = task.get("subtasks", []) or []
    if not isinstance(children, list) or len(children) > 40:
        raise ValueError("requirements_children_invalid")
    parsed_children = []
    sequences = []
    for child in children:
        if not isinstance(child, dict):
            raise ValueError("requirements_child_invalid")
        child_id = child.get("id", child.get("subtask_id"))
        if not isinstance(child_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,160}", child_id):
            raise ValueError("requirements_child_invalid")
        sequence = child.get("sequence")
        if type(sequence) is not int or sequence < 1:
            raise ValueError("requirements_child_invalid")
        child_dependencies = child.get("depends_on", [])
        if (not isinstance(child_dependencies, list)
                or any(not isinstance(item, str) for item in child_dependencies)):
            raise ValueError("requirements_child_invalid")
        parsed_children.append({
            "id": child_id,
            "sequence": sequence,
            "title": _bounded_requirement_text(child.get("title", child_id), name="child_title", limit=300),
            "instruction": _bounded_requirement_text(child.get("instruction", ""), name="child_instruction", limit=1_200),
            "deliverable": _bounded_requirement_text(child.get("deliverable", ""), name="child_deliverable", limit=500),
            "done_when": _bounded_requirement_text(child.get("done_when", ""), name="child_done_when", limit=500),
            "depends_on": child_dependencies,
        })
        sequences.append(sequence)
    if sequences and sorted(sequences) != list(range(1, len(sequences) + 1)):
        raise ValueError("requirements_child_order_invalid")
    payload = {
        "task_id": task_id,
        "objective": objective,
        "acceptance": acceptance,
        "depends_on": dependencies,
        "execution_mode": mode,
        "scope_roots": scope_roots,
        "priority": task.get("priority", ""),
        "module": task.get("module", task.get("area", "")),
        "owner_gate": bool(task.get("required_owner_gate", task.get("manual_owner_gate_required", False))),
        "subtasks": parsed_children,
    }
    payload["requirements_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return payload


def _task_requirements(state: State, task_id: str) -> dict:
    if not TASK_ID.fullmatch(task_id):
        raise ValueError("requirements_task_id_invalid")
    with state.db() as db:
        row = db.execute("SELECT spec FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise ValueError("supervisor_task_missing")
        task = json.loads(row[0])
        children = [json.loads(child[0]) for child in db.execute(
            "SELECT spec FROM subtasks WHERE parent_id=? ORDER BY sequence", (task_id,)
        )]
    if children:
        task["subtasks"] = children
    return parse_requirements(task)


def supervise(state: State, *, focus: str, count: int, output: Path, model: str, effort: str,
              task_id: str = ""):
    """Read-only model plan. Owner must explicitly enqueue output; never runs tasks."""
    state.ensure_approved()
    digest=state.get("architecture_sha")
    architecture=state.home/"private"/f"architecture-{digest[:16]}.md"
    if not architecture.is_file():
        raise ValueError("approved architecture file missing")
    body=architecture.read_text(encoding="utf-8")
    if len(body)>30_000:
        raise ValueError("architecture exceeds first-pass context budget; divide into focus sections before planning")
    if len(focus)>250 or count<1 or count>10:
        raise ValueError("invalid focus or task count")
    if output.exists():
        raise ValueError("output already exists; use a new path")
    source=Path(state.get("source"))
    inspection = inspect_repository(source)
    requirements = _task_requirements(state, task_id) if task_id else None
    context = {"repository": inspection, "requirements": requirements}
    prompt=("You are Astra One's read-only SDA Supervisor. Prepare a small ordered coding-task plan for the "
            "final architecture below. DO NOT edit files or invoke nested agents. "
            f"Focus: {focus or 'first safe foundation milestone'}; at most {count} tasks. "
            "Return ONLY a JSON array; each task MUST have task_id (ASTRA-NNN), objective (10..3000 chars), "
            "acceptance (1..15 strings), depends_on (list of preceding task IDs) and area. "
            "Tasks should be independent when feasible. Do not propose unapproved destructive operations.\n"
            "The repository citation and requirements packet below are pinned, read-only facts. "
            "Preserve the exact acceptance text; do not invent approval or source evidence.\n"
            + json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n"
            f"Architecture SHA256 {digest}\n"+body)
    candidate=state.home/"private"/("plan-"+uuid.uuid4().hex+".json")
    try:
        rc,_,reason=codex_call(worktree=source,prompt=prompt,home=state.home,state=state,model=model,effort=effort,
                               sandbox="read-only",timeout=900,output_file=candidate,role="supervisor")
        if rc or reason!="ok" or not candidate.is_file() or candidate.stat().st_size>25_000:
            raise ValueError("supervisor failed or output invalid")
        items=json.loads(candidate.read_text(encoding="utf-8"))
        if not isinstance(items,list) or not 1<=len(items)<=count:
            raise ValueError("invalid supervisor plan length")
        tasks=[task_spec(x) for x in items]
        ids=set()
        for t in tasks:
            if any(dep not in ids for dep in t["depends_on"]):
                raise ValueError("supervisor plan contains forward or unknown dependency")
            ids.add(t["task_id"])
        output.parent.mkdir(parents=True,exist_ok=True)
        # No model content becomes a queued task without subsequent owner enqueue.
        with output.open("x",encoding="utf-8") as f:
            json.dump(tasks,f,indent=2,ensure_ascii=False)
        os.chmod(output,0o600)
        post_inspection = inspect_repository(source)
        if post_inspection["source_sha"] != inspection["source_sha"]:
            raise ValueError("repository_changed_during_supervision")
        return {"proposal":str(output),"tasks":len(tasks),"queued":False,"architecture_sha":digest,
                "repository_inspection": inspection, "requirements": requirements}
    finally:
        candidate.unlink(missing_ok=True)


def _upgrade_audit_brief(task_id: str) -> str:
    """Return bounded, task-specific U1 context without exposing private artifacts."""
    if task_id == "BASE-015":
        return (
            "Investigate the BASE-015 failure pattern and the task-type preparation defect. Earlier generations "
            "attempted unrelated runtime source changes for a design task; a later generation succeeded after "
            "design-only repair guidance and design-aware QC. Verify the current implementation and identify the "
            "smallest tested runtime improvement."
        )
    if task_id == "WIN-002":
        return (
            "Investigate the WIN-002 task preparation and QC failure pattern. The parent is an implementation task "
            "with scope roots infra/windows/, src/jarvis_v2/backend/ and tests/. The first real worker wrote "
            "bootstrap/astra-one files outside scope; the next recovery wrote a secret-bearing .env artifact that "
            "the validator rejected; a later backend candidate passed deterministic tests but independent QC "
            "returned acceptance_gap, config_contract, correctness_risk, payload_exposure and test_gap. Inspect "
            "the current backend contract and tests, reproduce the preparation/validation defect in isolation, "
            "and identify the smallest tested improvement. Do not fabricate Windows/GPU evidence."
        )
    return (
        "Investigate the supplied task's recent bounded failure pattern in the current source and tests. Reproduce "
        "only a concrete runtime or task-preparation defect and identify the smallest tested improvement; do not "
        "infer success from model text or unavailable external evidence."
    )


def run_upgrade_audit(state: State, *, task_id: str, model: str, effort: str,
                      timeout: int) -> dict:
    """Run one bounded, read-only U1 investigation and persist sanitized evidence."""
    if not 60 <= timeout <= 3600 or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,80}", model):
        raise ValueError("invalid upgrade audit limits")
    if (state.home / "STOP").exists():
        raise ValueError("STOP prevents upgrade audit")
    supervisor = SupervisorController(state)
    supervisor.ensure_schema()
    lease = supervisor.claim_upgrade_audit(task_id, model=model)
    raw_path = state.home / "private" / "upgrade-audits" / ("." + lease["audit_id"] + ".model.json")
    final_path = state.home / "private" / "upgrade-audits" / (lease["audit_id"] + ".json")
    raw_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(raw_path.parent, 0o700)
    astra_root = Path(__file__).resolve().parents[1]
    repository = astra_root.parents[1]
    prompt = (
        "You are U1, Astra One's read-only upgrade auditor. Inspect the current ARCHON Astra One source and "
        "tests in this checkout; do not edit files, invoke agents, access the network, or print source, prompts, "
        "secrets, credentials, private paths, or raw logs. " + _upgrade_audit_brief(task_id) + " Return ONLY one JSON object "
        "with these keys: root_cause, reproduction, runtime_component, improvement, tests, risk. Values must be "
        "short bounded strings except tests, which is a list of at most 5 short strings. Explicitly distinguish "
        "observed, inferred and unknown facts. Do not claim a change was implemented unless it is present in the "
        "checkout.\n"
        f"Audit task: {task_id}\nAudit ID: {lease['audit_id']}\n"
        "Known safe categories: task_type_invalid, no_file_changes, qc_rejected, integration_patch_conflict, "
        "worker_runtime_error.\n"
    )
    try:
        rc, tools, reason = codex_call(
            worktree=repository, prompt=prompt, home=state.home, state=state,
            model=model, effort=effort, sandbox="read-only", timeout=timeout,
            output_file=raw_path, role="upgrade_auditor",
        )
        if rc or reason != "ok" or not raw_path.is_file() or raw_path.stat().st_size > 24_000:
            raise ValueError("audit_model_error")
        raw = raw_path.read_text(encoding="utf-8").strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("audit_output_invalid")
        required = ("root_cause", "reproduction", "runtime_component", "improvement", "tests", "risk")
        if set(parsed) != set(required) or not isinstance(parsed["tests"], list) or len(parsed["tests"]) > 5:
            raise ValueError("audit_output_invalid")
        secret_pattern = re.compile(r"(?i)(?:sk-[A-Za-z0-9]{12,}|gh[pousr]_[A-Za-z0-9]{12,}|AKIA[0-9A-Z]{12,}|BEGIN [A-Z ]*PRIVATE KEY)")
        def bounded(value: object, limit: int = 700) -> str:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("audit_output_invalid")
            value = " ".join(value.split())
            if len(value) > limit or secret_pattern.search(value):
                raise ValueError("audit_output_invalid")
            return value
        report = {
            "audit_id": lease["audit_id"], "task_id": task_id, "lane": "upgrade_auditor",
            "model": model, "effort": effort, "tools": int(tools),
            "root_cause": bounded(parsed["root_cause"]),
            "reproduction": bounded(parsed["reproduction"]),
            "runtime_component": bounded(parsed["runtime_component"], 240),
            "improvement": bounded(parsed["improvement"]),
            "tests": [bounded(item, 300) for item in parsed["tests"]],
            "risk": bounded(parsed["risk"], 400),
        }
        checks = []
        env = dict(os.environ)
        env["PYTHONPATH"] = str(astra_root)
        for name in ("test_supervisor_v3.py", "test_linux_sda.py"):
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", name, "-q"],
                cwd=astra_root, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False, timeout=600,
            )
            match = re.search(r"Ran\s+([0-9]+)\s+tests?", result.stdout)
            checks.append({"name": name, "exit_code": result.returncode,
                           "tests_observed": int(match.group(1)) if match else 0,
                           "status": "passed" if result.returncode == 0 and match else "failed"})
        if any(item["status"] != "passed" for item in checks):
            raise ValueError("audit_checks_failed")
        report["deterministic_checks"] = checks
        report["evidence_sha"] = hashlib.sha256(
            json.dumps(checks, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        encoded = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
        if len(encoded) > 12_000:
            raise ValueError("audit_output_invalid")
        final_path.write_bytes(encoded + b"\n")
        os.chmod(final_path, 0o600)
        report_sha = hashlib.sha256(final_path.read_bytes()).hexdigest()
        result = supervisor.finish_upgrade_audit(
            lease["audit_id"], run_id=lease["run_id"], status="completed",
            report_path=str(final_path), report_sha=report_sha,
            evidence_sha=report["evidence_sha"],
        )
        return {**result, "report_path": str(final_path), "checks": checks}
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        code = str(exc) if str(exc) in {"audit_model_error", "audit_output_invalid", "audit_checks_failed"} else "audit_failed"
        try:
            supervisor.finish_upgrade_audit(
                lease["audit_id"], run_id=lease["run_id"], status="failed", failure_code=code,
            )
        finally:
            raw_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
        raise
    finally:
        raw_path.unlink(missing_ok=True)


def run_master(state: State, *, workers: int, max_tasks: int, max_minutes: int, model: str, effort: str,
               test_image: str, test_command: list[str], auto_integrate: bool, max_repairs: int, timeout: int,
               danger_bypass: bool = False, batch_id: str | None = None,
               _schema_ready: bool = False) -> dict:
    if not 1<=workers<=MAX_WORKERS or not 1<=max_tasks<=1000 or not 1<=max_minutes<=1440 or not 60<=timeout<=7200:
        raise ValueError("invalid worker/task/time limits")
    if not 0<=max_repairs<=MAX_FAILURES-1:
        raise ValueError("invalid repair limit")
    if os.geteuid() == 0:
        raise ValueError("SDA master must run as a non-root Linux user")
    state.ensure_approved()
    if not test_image:
        raise ValueError("Docker test image required for independent QC")
    if danger_bypass:
        if state.home == LIVE_STATE or Path(state.get("source")).expanduser().resolve() == LIVE_SOURCE:
            raise ValueError("danger_bypass_forbidden_for_live_state")
        if os.environ.get("INVOCATION_ID") or os.environ.get("JOURNAL_STREAM"):
            raise ValueError("danger_bypass_forbidden_in_service")
    elif not sandbox_status()["available"]:
        raise ValueError("sandbox_unavailable")
    if control_blocked(state.home, "normal"):
        raise ValueError("STOP/PAUSE/PAUSED_QUOTA prevents master start")
    supervisor = SupervisorController(state)
    if not _schema_ready:
        supervisor.ensure_schema()
    attempted=0
    completed=0
    failed=0
    requeued=0
    terminal_failures=0
    blockers=[]

    def retry_decision(tid: str, result: dict) -> str:
        """Return an empty string when a failed task may receive one repair attempt."""
        if result.get("status") != "failed":
            return "not_retryable_state"
        with state.db() as db:
            row=db.execute("SELECT attempt FROM tasks WHERE id=?",(tid,)).fetchone()
        if not row or row[0] > max_repairs:
            return "retry_ceiling"
        codes=state.failure_codes(tid)
        if len(codes)>=2 and codes[-1]==codes[-2]:
            return "repeated_failure"
        return ""

    def maybe_requeue(tid: str, result: dict) -> str:
        nonlocal requeued, terminal_failures
        with state.db() as db:
            row = db.execute("SELECT attempt,base_sha,candidate_sha FROM tasks WHERE id=?", (tid,)).fetchone()
        if row:
            try:
                supervisor.triage_failure(
                    tid, result.get("error", "worker_runtime_error"), base_sha=row["base_sha"],
                    candidate_sha=row["candidate_sha"], generation=row["attempt"],
                )
            except ValueError:
                # The task failure remains durable even if a secondary case
                # record cannot be created; do not expose model text.
                pass
        markers=[x for x in ("STOP","PAUSE","PAUSED_QUOTA","PAUSE_NORMAL") if (state.home/x).exists()]
        if markers:
            blocker=result.get("error") or markers[0].lower()
            if blocker not in blockers:
                blockers.append(blocker)
            return "paused"
        decision=retry_decision(tid,result)
        if decision:
            terminal_failures+=1
            if result.get("error") and decision not in blockers:
                blockers.append(result["error"])
            return decision
        try:
            state.retry(tid)
        except ValueError as exc:
            # A concurrent recovery controller may have atomically leased the
            # failure after triage.  Leave that generation to recovery rather
            # than converting a valid ownership race into a terminal error.
            if str(exc) == "task has active recovery lease":
                return "recovery_claimed"
            raise
        requeued+=1
        return "requeued"

    # The file lock protects short ledger/checkpoint operations only.  Model
    # execution and Docker QC must run outside it so recovery lanes can make
    # progress concurrently under the same deterministic database.
    with contextlib.nullcontext():
        with state.master_lock(blocking=True):
            ensure_integration(state)
        deadline=time.monotonic()+max_minutes*60
        pending={}
        # Each task has its own worktree and subprocess; max 5 coding agents.
        with ThreadPoolExecutor(max_workers=workers,thread_name_prefix="astra-worker") as pool:
            try:
                while time.monotonic()<deadline:
                    stopped=(state.home/"STOP").exists()
                    paused=control_blocked(state.home, "normal")
                    while not stopped and not paused and len(pending)<workers and attempted<max_tasks:
                        with state.master_lock(blocking=True):
                            claim=state.claim(model=model, batch_id=batch_id, lane="normal")
                        if not claim:break
                        attempted+=1
                        slot=next(i for i in range(1,workers+1) if i not in pending.values())
                        fut=pool.submit(execute_claim,state,claim,slot=slot,model=model,effort=effort,
                                        timeout=timeout,test_image=test_image,test_command=test_command,
                                        auto_integrate=auto_integrate,danger_bypass=danger_bypass)
                        pending[fut]=slot
                    if not pending:
                        if stopped or paused or attempted>=max_tasks:break
                        with state.db() as db:
                            next_available=db.execute("SELECT MIN(available_at) FROM tasks WHERE status='queued' AND available_at>?",(int(time.time()),)).fetchone()[0]
                        if next_available and next_available<=int(time.time())+10:
                            time.sleep(1)
                            continue
                        break
                    done,_=wait(pending.keys(),timeout=1,return_when=FIRST_COMPLETED)
                    for fut in done:
                        pending.pop(fut)
                        result=fut.result()
                        tid=result["task_id"]
                        if result["status"]=="approved":
                            try:
                                with state.master_lock(blocking=True):
                                    integrate(state,tid,merger_model=model,merger_effort=effort,
                                              danger_bypass=danger_bypass, lane="normal")
                                completed+=1
                            except (ValueError,OSError,subprocess.SubprocessError) as ex:
                                error = getattr(ex, "failure_code", getattr(ex, "code", "merger_failed"))
                                with state.db() as db:
                                    row=db.execute("SELECT status FROM tasks WHERE id=?",(tid,)).fetchone()
                                if row and row[0]=="approved":
                                    state.set_task(tid,"failed",error=error)
                                result={"task_id":tid,"status":"failed","error":error}
                                failed+=1
                                maybe_requeue(tid,result)
                        elif result["status"]=="awaiting_review":
                            completed+=1
                        else:
                            failed+=1
                            maybe_requeue(tid,result)
                    if attempted % 5==0 or done:
                        state.sync(limit=25)
            except KeyboardInterrupt:
                # Signal active jobs to terminate; do not clear the owner's stop control.
                (state.home/"STOP").touch(exist_ok=True)
                print("Interrupted: STOP created; active Codex jobs will terminate.",file=sys.stderr)
                for fut in pending:fut.result()
            finally:
                if pending and time.monotonic()>=deadline:
                    (state.home/"STOP").touch(exist_ok=True)
                    print("Master runtime limit reached: STOP set for active workers.",file=sys.stderr)
                state.sync(limit=100)
    with state.db() as db:
        task_counts={row[0]:row[1] for row in db.execute("SELECT status,count(*) FROM tasks GROUP BY status")}
    markers={x for x in ("STOP","PAUSE","PAUSED_QUOTA","PAUSE_NORMAL") if (state.home/x).exists()}
    state_name=("paused_quota" if "PAUSED_QUOTA" in markers else
                "paused" if "PAUSE" in markers else
                "stopped" if "STOP" in markers or task_counts.get("stopped",0) else
                "failed" if terminal_failures else
                "queued" if task_counts.get("queued",0) else "idle")
    return {"attempts":attempted,"qc_passed":completed,"failures_or_conflicts":failed,
            "requeued":requeued,"terminal_failures":terminal_failures,
            "queued_remaining":task_counts.get("queued",0),"task_counts":task_counts,
            "blockers":blockers,"state":state_name,"worker_limit":workers,"engine":"stopped",
            "source_unchanged":True,"no_remote_git_push":True}


def run_recovery(state: State, *, limit: int, model: str, effort: str, test_image: str,
                 test_command: list[str], timeout: int, danger_bypass: bool = False,
                 _schema_ready: bool = False) -> dict:
    """Execute at most two durable recovery leases, serializing integration."""
    if not 1 <= limit <= 2 or not 60 <= timeout <= 7200:
        raise ValueError("invalid recovery limits")
    state.ensure_approved()
    if not test_image:
        raise ValueError("Docker test image required for independent QC")
    if control_blocked(state.home, "recovery"):
        return {"claimed": 0, "resolved": 0, "qc_pending": 0, "blocked": 0, "state": "paused"}
    supervisor = SupervisorController(state)
    if not _schema_ready:
        supervisor.ensure_schema()
    results = []
    with state.db() as db:
        cases = db.execute(
            "SELECT c.case_id,c.parent_id,c.state,t.status FROM supervisor_cases c "
            "JOIN tasks t ON t.id=c.parent_id WHERE c.state IN ('triaged','qc_rejected','merge_rejected') "
            "AND t.status IN ('failed','conflict','interrupted','stopped') "
            "ORDER BY c.updated_at,c.case_id LIMIT ?", (limit,)
        ).fetchall()
    for case in cases:
        lease = None
        item = None
        with state.db() as db:
            lane = db.execute(
                "SELECT lane_id FROM supervisor_lanes WHERE lane_id IN ('repair_1','repair_2') AND state='idle' "
                "ORDER BY lane_id LIMIT 1"
            ).fetchone()
        if not lane:
            break
        try:
            lease = supervisor.claim_recovery(case["case_id"], lane["lane_id"])
            item = state.claim_recovery_task(lease, model=model)
            slot = 1 if lease["lane_id"] == "repair_1" else 2
            # The recovery lease fences the task in SQLite.  Keep model
            # execution and QC outside the Master lock; only the Merger needs
            # the short serialized integration critical section below.
            result = execute_claim(
                state, item, slot=slot, model=model, effort=effort, timeout=timeout,
                test_image=test_image, test_command=test_command, auto_integrate=True,
                danger_bypass=danger_bypass,
            )
            if result.get("status") == "approved":
                with state.db() as db:
                    candidate_row = db.execute(
                        "SELECT candidate_sha FROM tasks WHERE id=?", (case["parent_id"],)
                    ).fetchone()
                candidate_sha = candidate_row[0] if candidate_row else ""
                supervisor.bind_recovery_candidate(
                    lease["lane_id"], lease["case_id"], lease_token=lease["lease_token"],
                    run_id=item["run_id"], generation=item["attempt"], candidate_sha=candidate_sha,
                )
                with state.master_lock(blocking=True):
                    result = integrate(state, case["parent_id"], merger_model=model,
                                       merger_effort=effort, danger_bypass=danger_bypass,
                                       lane="recovery")
            recovery_state = ("resolved" if result.get("status") in {"approved", "completed"} else
                              "qc_pending" if result.get("status") == "awaiting_review" else "blocked")
            with state.db() as db:
                task_row = db.execute(
                    "SELECT candidate_sha FROM tasks WHERE id=?", (case["parent_id"],)
                ).fetchone()
            supervisor.finish_recovery(
                lease["lane_id"], lease["case_id"], lease_token=lease["lease_token"],
                run_id=item["run_id"], generation=item["attempt"],
                candidate_sha=(task_row[0] if task_row else ""), state=recovery_state,
            )
            results.append({"case_id": case["case_id"], "task_id": case["parent_id"],
                            "lane_id": lease["lane_id"], "state": recovery_state,
                            "worker_status": result.get("status"), "error": result.get("error", "")})
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            # A claimed lane is always returned to the ledger; the failure is
            # bounded and the task remains failed for the next Supervisor tick.
            try:
                if lease is not None and item is not None:
                    supervisor.finish_recovery(
                        lease["lane_id"], lease["case_id"], lease_token=lease["lease_token"],
                        run_id=item["run_id"], generation=item["attempt"], state="blocked",
                    )
                elif lease is not None:
                    supervisor.release_unstarted_recovery(
                        lease["lane_id"], lease["case_id"], lease_token=lease["lease_token"],
                    )
            except (ValueError, OSError):
                pass
            if lease is None:
                # Normal dispatch may have reclaimed the task between the
                # snapshot and this lane claim.  It is neither a recovery
                # failure nor a blocked task.
                continue
            results.append({"case_id": case["case_id"], "task_id": case["parent_id"],
                            "state": "blocked", "error": type(exc).__name__})
    return {
        "claimed": len(results),
        "resolved": sum(item["state"] == "resolved" for item in results),
        "qc_pending": sum(item["state"] == "qc_pending" for item in results),
        "blocked": sum(item["state"] == "blocked" for item in results),
        "results": results,
        "state": "completed" if results else "idle",
    }


def _single_controller(function):
    """Hold one process-lifetime controller fence around each public runner."""
    @wraps(function)
    def guarded(state, *args, _controller_locked=False, **kwargs):
        if _controller_locked:
            return function(state, *args, **kwargs)
        with state.controller_lock():
            return function(state, *args, **kwargs)
    return guarded


run_master = _single_controller(run_master)
run_recovery = _single_controller(run_recovery)


def run_concurrent(state: State, *, workers: int, max_tasks: int, max_minutes: int,
                    model: str, effort: str, recovery_limit: int,
                    recovery_model: str, recovery_effort: str, test_image: str,
                    test_command: list[str], auto_integrate: bool,
                    max_repairs: int, timeout: int, batch_id: str | None = None) -> dict:
    """Run normal and recovery lanes under one process and one ledger fence."""
    # Schema migration is a single-writer operation.  Perform it once before
    # starting the lane threads; otherwise the normal and recovery entrypoints
    # can race on the non-blocking Master lock and one lane is rejected before
    # it can claim work.
    state.ensure_approved()
    SupervisorController(state).ensure_schema()
    with state.controller_lock():
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="astra-lane") as pool:
            normal_future = pool.submit(
                run_master, state, workers=workers, max_tasks=max_tasks, max_minutes=max_minutes,
                model=model, effort=effort, test_image=test_image, test_command=test_command,
                auto_integrate=auto_integrate, max_repairs=max_repairs, timeout=timeout,
                batch_id=batch_id, _schema_ready=True, _controller_locked=True,
            )
            recovery_future = pool.submit(
                run_recovery, state, limit=recovery_limit, model=recovery_model, effort=recovery_effort,
                test_image=test_image, test_command=test_command, timeout=timeout, _schema_ready=True,
                _controller_locked=True,
            )
            normal = normal_future.result()
            recovery = recovery_future.result()
    return {"normal": normal, "recovery": recovery, "engine": "stopped",
            "shared_master_lock": True, "no_remote_git_push": True}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(prog="python3 -m astra_one.linux_cli",description="Astra One Linux five-worker Codex SDA")
    parser.add_argument("--home",type=Path,default=DEFAULT_HOME)
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("doctor");p.add_argument("--source",type=Path)
    p=sub.add_parser("init");p.add_argument("--source",type=Path,required=True)
    p=sub.add_parser("architecture");p.add_argument("action",choices=["import","approve","status"]);p.add_argument("--file",type=Path);p.add_argument("--sha")
    p=sub.add_parser("supervise");p.add_argument("--focus",default="");p.add_argument("--task-id",default="");p.add_argument("--count",type=int,default=5);p.add_argument("--output",type=Path,required=True);p.add_argument("--model",default=MODEL);p.add_argument("--effort",default=EFFORT)
    p=sub.add_parser("enqueue");p.add_argument("--file",type=Path,required=True)
    p=sub.add_parser("validate-full-plan");p.add_argument("--parent-plan",type=Path,required=True);p.add_argument("--subtask-index",type=Path,required=True);p.add_argument("--subtask-dir",type=Path,required=True);p.add_argument("--source-ref",default="");p.add_argument("--source-commit",default="")
    p=sub.add_parser("import-full-plan");p.add_argument("--parent-plan",type=Path,required=True);p.add_argument("--subtask-index",type=Path,required=True);p.add_argument("--subtask-dir",type=Path,required=True);p.add_argument("--source-ref",default="");p.add_argument("--source-commit",default="")
    sub.add_parser("full-plan-status")
    sub.add_parser("status");sub.add_parser("tasks");sub.add_parser("sync")
    for name in ("stop","pause","resume","clear-quota","recover",
                 "pause-normal","pause-recovery","resume-normal","resume-recovery"):
        sub.add_parser(name)
    p=sub.add_parser("supervisor-block");p.add_argument("case_id");p.add_argument("--category",required=True);p.add_argument("--failure-code",default="")
    p=sub.add_parser("retry");p.add_argument("task_id")
    p=sub.add_parser("reopen");p.add_argument("task_ids",nargs="+")
    sub.add_parser("supervisor-status")
    p=sub.add_parser("supervisor-tick");p.add_argument("--limit",type=int,default=50)
    p=sub.add_parser("batch-start");p.add_argument("batch_id");p.add_argument("--limit",type=int,default=20)
    p=sub.add_parser("batch-status");p.add_argument("batch_id")
    p=sub.add_parser("batch-replenish");p.add_argument("batch_id");p.add_argument("--target",type=int,default=20)
    p=sub.add_parser("upgrade-create");p.add_argument("batch_id");p.add_argument("candidate_sha");p.add_argument("rollback_sha")
    p=sub.add_parser("upgrade-check");p.add_argument("batch_id");p.add_argument("stage",choices=["TESTED","BACKUP","CANARY","HEALTH"]);p.add_argument("artifact_sha")
    p=sub.add_parser("upgrade-transition");p.add_argument("batch_id");p.add_argument("state")
    p=sub.add_parser("upgrade-audit");p.add_argument("task_id");p.add_argument("--model",default="gpt-6.1-sol")
    p.add_argument("--effort",choices=["low","medium","high","xhigh"],default="high")
    p.add_argument("--max-seconds",type=int,default=900)
    p=sub.add_parser("supervisor-recover");p.add_argument("--limit",type=int,default=2)
    p.add_argument("--model",default=MODEL);p.add_argument("--effort",choices=["low","medium","high","xhigh"],default=EFFORT)
    p.add_argument("--test-image",default="");p.add_argument("--test-command-json",default='["python3","-m","unittest","discover","-s","tests","-p","test_*.py"]')
    p.add_argument("--max-seconds-per-task",type=int,default=1800)
    p=sub.add_parser("approve-task");p.add_argument("task_id")
    p=sub.add_parser("owner-approval-request");p.add_argument("task_id");p.add_argument("--owner-id",required=True)
    p.add_argument("--allowed-signers",type=Path);p.add_argument("--output",type=Path)
    p=sub.add_parser("approve-owner");p.add_argument("task_id");p.add_argument("--owner-receipt",type=Path,required=True)
    p=sub.add_parser("integrate");p.add_argument("task_id");p.add_argument("--confirm",action="store_true")
    p=sub.add_parser("run")
    p.add_argument("--workers",type=int,default=5);p.add_argument("--max-tasks",type=int,default=100)
    p.add_argument("--max-minutes",type=int,default=240);p.add_argument("--max-seconds-per-task",type=int,default=1800)
    p.add_argument("--model",default=MODEL);p.add_argument("--effort",choices=["low","medium","high","xhigh"],default=EFFORT)
    p.add_argument("--test-image",default="");p.add_argument("--test-command-json",default='["python3","-m","unittest","discover","-s","tests","-p","test_*.py"]')
    p.add_argument("--max-repairs",type=int,default=3);p.add_argument("--auto-integrate",action="store_true")
    p.add_argument("--batch-id",default=None,
                   help="restrict claims to admitted members of one v3 batch cohort")
    p.add_argument("--concurrent-recovery",action="store_true",
                   help="run the two bounded recovery lanes concurrently with normal workers")
    p.add_argument("--recovery-limit",type=int,default=2)
    p.add_argument("--recovery-model",default="gpt-6.1-sol")
    p.add_argument("--recovery-effort",choices=["low","medium","high","xhigh"],default="high")
    p.add_argument("--danger-bypass",action="store_true",
                   help="supervised disposable development only; rejected for live state and systemd")
    args=parser.parse_args(argv)
    state=State(args.home)
    try:
        if args.command=="doctor":report(diagnose(args.source));return 0
        if args.command=="init":report(state.init(args.source));return 0
        if args.command=="architecture":
            if args.action=="import":
                if not args.file:raise ValueError("architecture import needs --file")
                digest=state.import_architecture(args.file)
                report({"sha256":digest,"approved":False,"engine":"stopped"})
            elif args.action=="approve":
                if not args.sha:raise ValueError("architecture approve needs --sha")
                state.approve_architecture(args.sha);report({"approved":True,"engine":"not_started"})
            else:report({"sha256":state.get("architecture_sha"),"approved":state.get("approved_architecture_sha")==state.get("architecture_sha") and bool(state.get("architecture_sha"))})
        elif args.command=="supervise":report(supervise(state,focus=args.focus,task_id=args.task_id,count=args.count,output=args.output,model=args.model,effort=args.effort))
        elif args.command=="enqueue":report({"enqueued":state.add_tasks(json.loads(args.file.read_text(encoding="utf-8"))),"started":False})
        elif args.command in ("validate-full-plan", "import-full-plan"):
            plan=load_full_plan(args.parent_plan,args.subtask_index,args.subtask_dir,
                                source_ref=args.source_ref,source_commit=args.source_commit)
            if args.command=="validate-full-plan":
                report(plan.validation)
            else:
                report(state.import_full_plan(plan))
        elif args.command=="full-plan-status":report(state.full_plan_status())
        elif args.command=="status":report(state.overview())
        elif args.command=="tasks":report(state.list_tasks())
        elif args.command=="sync":report(state.sync(limit=500))
        elif args.command in ("stop","pause","pause-normal","pause-recovery"):
            marker_name = {
                "stop": "STOP", "pause": "PAUSE", "pause-normal": "PAUSE_NORMAL",
                "pause-recovery": "PAUSE_RECOVERY",
            }[args.command]
            marker=state.home/marker_name;marker.parent.mkdir(parents=True,exist_ok=True)
            marker.touch(exist_ok=True)
            report({"control":args.command,"marker":marker_name,
                    "existing_jobs":"stop terminates; lane pause drains only that lane"})
        elif args.command=="resume":
            for x in ("STOP","PAUSE"):(state.home/x).unlink(missing_ok=True)
            report({"controls":"owner_cleared","engine":"not_started"})
        elif args.command in ("resume-normal", "resume-recovery"):
            marker = "PAUSE_NORMAL" if args.command == "resume-normal" else "PAUSE_RECOVERY"
            (state.home / marker).unlink(missing_ok=True)
            report({"control":args.command,"marker":marker,"engine":"not_started"})
        elif args.command=="clear-quota":
            (state.home/"PAUSED_QUOTA").unlink(missing_ok=True)
            report({"quota_pause":"owner_cleared","engine":"not_started"})
        elif args.command=="recover":report({"interrupted_tasks":state.recover(),"auto_restart":False})
        elif args.command=="retry":state.retry(args.task_id);report({"queued":args.task_id})
        elif args.command=="reopen":report({"reopened":state.reopen_failed(args.task_ids),"history_preserved":True})
        elif args.command == "supervisor-block":
            report(SupervisorController(state).mark_external_blocker(args.case_id, args.category, args.failure_code))
        elif args.command == "supervisor-recover":
            command=json.loads(args.test_command_json)
            if not isinstance(command,list):
                raise ValueError("test command must be a JSON list")
            report(run_recovery(state,limit=args.limit,model=args.model,effort=args.effort,
                                test_image=args.test_image,test_command=command,
                                timeout=args.max_seconds_per_task))
        elif args.command == "upgrade-audit":
            report(run_upgrade_audit(state, task_id=args.task_id, model=args.model,
                                     effort=args.effort, timeout=args.max_seconds))
        elif args.command in {"supervisor-status", "supervisor-tick", "batch-start", "batch-status", "batch-replenish", "upgrade-create", "upgrade-check", "upgrade-transition"}:
            supervisor=SupervisorController(state)
            supervisor.ensure_schema()
            if args.command=="supervisor-status":
                report(supervisor.status())
            elif args.command=="supervisor-tick":
                report(supervisor.tick(args.limit))
            elif args.command=="batch-start":
                report(supervisor.start_batch(args.batch_id,args.limit))
            elif args.command=="batch-status":
                report(supervisor.batch_status(args.batch_id))
            elif args.command=="batch-replenish":
                report(supervisor.replenish_batch(args.batch_id,args.target))
            elif args.command=="upgrade-create":
                report(supervisor.create_upgrade(args.batch_id,args.candidate_sha,args.rollback_sha))
            elif args.command=="upgrade-check":
                report(supervisor.run_upgrade_check(args.batch_id,args.stage,args.artifact_sha))
            else:
                report(supervisor.transition_upgrade(args.batch_id,args.state))
        elif args.command=="approve-task":state.approve(args.task_id);report({"approved":args.task_id})
        elif args.command=="owner-approval-request":
            report(state.owner_approval_request(args.task_id, args.owner_id,
                                                allowed_signers=args.allowed_signers,
                                                output=args.output))
        elif args.command=="approve-owner":report(state.approve_owner(args.task_id, owner_receipt=args.owner_receipt))
        elif args.command=="integrate":
            if not args.confirm:raise ValueError("integration requires --confirm after diff review")
            with state.master_lock():report(integrate(state,args.task_id,merger_model=MODEL,merger_effort=EFFORT))
        elif args.command=="run":
            command=json.loads(args.test_command_json)
            if not isinstance(command,list):raise ValueError("test command must be a JSON list")
            if args.concurrent_recovery:
                result=run_concurrent(
                    state, workers=args.workers, max_tasks=args.max_tasks, max_minutes=args.max_minutes,
                    model=args.model, effort=args.effort, recovery_limit=args.recovery_limit,
                    recovery_model=args.recovery_model, recovery_effort=args.recovery_effort,
                    test_image=args.test_image, test_command=command, auto_integrate=args.auto_integrate,
                    max_repairs=args.max_repairs, timeout=args.max_seconds_per_task, batch_id=args.batch_id,
                )
                report(result)
                normal_result=result["normal"]
                return 1 if normal_result.get("terminal_failures") else 0
            result=run_master(state,workers=args.workers,max_tasks=args.max_tasks,max_minutes=args.max_minutes,
                              model=args.model,effort=args.effort,test_image=args.test_image,test_command=command,
                              auto_integrate=args.auto_integrate,max_repairs=args.max_repairs,
                              timeout=args.max_seconds_per_task,danger_bypass=args.danger_bypass,
                              batch_id=args.batch_id)
            report(result)
            return 1 if result.get("terminal_failures") else 0
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as ex:
        print("Astra Linux SDA refused: "+str(ex),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
