"""Linux SDA command-line control plane: no automatic startup on installation."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
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

from .linux_sda import DEFAULT_HOME, EFFORT, MAX_FAILURES, MAX_WORKERS, MODEL, State, assert_source, task_spec
from .linux_runtime import codex_call, ensure_integration, integrate, execute_claim, sandbox_status
from .full_plan import load_full_plan

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


def supervise(state: State, *, focus: str, count: int, output: Path, model: str, effort: str):
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
    prompt=("You are Astra One's read-only SDA Supervisor. Prepare a small ordered coding-task plan for the "
            "final architecture below. DO NOT edit files or invoke nested agents. "
            f"Focus: {focus or 'first safe foundation milestone'}; at most {count} tasks. "
            "Return ONLY a JSON array; each task MUST have task_id (ASTRA-NNN), objective (10..3000 chars), "
            "acceptance (1..15 strings), depends_on (list of preceding task IDs) and area. "
            "Tasks should be independent when feasible. Do not propose unapproved destructive operations.\n"
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
        return {"proposal":str(output),"tasks":len(tasks),"queued":False,"architecture_sha":digest}
    finally:
        candidate.unlink(missing_ok=True)


def run_master(state: State, *, workers: int, max_tasks: int, max_minutes: int, model: str, effort: str,
               test_image: str, test_command: list[str], auto_integrate: bool, max_repairs: int, timeout: int,
               danger_bypass: bool = False) -> dict:
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
    if any((state.home/x).exists() for x in ("STOP","PAUSE","PAUSED_QUOTA")):
        raise ValueError("STOP/PAUSE/PAUSED_QUOTA prevents master start")
    attempted=0
    completed=0
    failed=0
    requeued=0
    terminal_failures=0
    blockers=[]
    halt_after_current=False

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
        nonlocal requeued, terminal_failures, halt_after_current
        markers=[x for x in ("STOP","PAUSE","PAUSED_QUOTA") if (state.home/x).exists()]
        if markers:
            blocker=result.get("error") or markers[0].lower()
            if blocker not in blockers:
                blockers.append(blocker)
            return "paused"
        decision=retry_decision(tid,result)
        if decision:
            terminal_failures+=1
            halt_after_current=True
            if result.get("error") and decision not in blockers:
                blockers.append(result["error"])
            return decision
        with state.db() as db:
            db.execute("UPDATE tasks SET status='queued',available_at=?,updated_at=? WHERE id=?",
                       (int(time.time())+2, __import__('astra_one.linux_sda',fromlist=['now']).now(),tid))
        requeued+=1
        return "requeued"

    with state.master_lock():
        ensure_integration(state)
        deadline=time.monotonic()+max_minutes*60
        pending={}
        # Each task has its own worktree and subprocess; max 5 coding agents.
        with ThreadPoolExecutor(max_workers=workers,thread_name_prefix="astra-worker") as pool:
            try:
                while time.monotonic()<deadline:
                    stopped=(state.home/"STOP").exists()
                    paused=any((state.home/x).exists() for x in ("PAUSE","PAUSED_QUOTA"))
                    while not stopped and not paused and not halt_after_current and len(pending)<workers and attempted<max_tasks:
                        claim=state.claim(model=model)
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
                                integrate(state,tid,merger_model=model,merger_effort=effort,
                                          danger_bypass=danger_bypass)
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
                    if halt_after_current and not pending and not any(
                        (state.home/x).exists() for x in ("STOP", "PAUSE", "PAUSED_QUOTA")
                    ):
                        (state.home/"PAUSE").touch(exist_ok=True)
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
    markers={x for x in ("STOP","PAUSE","PAUSED_QUOTA") if (state.home/x).exists()}
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


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(prog="python3 -m astra_one.linux_cli",description="Astra One Linux five-worker Codex SDA")
    parser.add_argument("--home",type=Path,default=DEFAULT_HOME)
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("doctor");p.add_argument("--source",type=Path)
    p=sub.add_parser("init");p.add_argument("--source",type=Path,required=True)
    p=sub.add_parser("architecture");p.add_argument("action",choices=["import","approve","status"]);p.add_argument("--file",type=Path);p.add_argument("--sha")
    p=sub.add_parser("supervise");p.add_argument("--focus",default="");p.add_argument("--count",type=int,default=5);p.add_argument("--output",type=Path,required=True);p.add_argument("--model",default=MODEL);p.add_argument("--effort",default=EFFORT)
    p=sub.add_parser("enqueue");p.add_argument("--file",type=Path,required=True)
    p=sub.add_parser("validate-full-plan");p.add_argument("--parent-plan",type=Path,required=True);p.add_argument("--subtask-index",type=Path,required=True);p.add_argument("--subtask-dir",type=Path,required=True);p.add_argument("--source-ref",default="");p.add_argument("--source-commit",default="")
    p=sub.add_parser("import-full-plan");p.add_argument("--parent-plan",type=Path,required=True);p.add_argument("--subtask-index",type=Path,required=True);p.add_argument("--subtask-dir",type=Path,required=True);p.add_argument("--source-ref",default="");p.add_argument("--source-commit",default="")
    sub.add_parser("full-plan-status")
    sub.add_parser("status");sub.add_parser("tasks");sub.add_parser("sync")
    for name in ("stop","pause","resume","clear-quota","recover"):sub.add_parser(name)
    p=sub.add_parser("retry");p.add_argument("task_id")
    p=sub.add_parser("reopen");p.add_argument("task_ids",nargs="+")
    p=sub.add_parser("approve-task");p.add_argument("task_id")
    p=sub.add_parser("approve-owner");p.add_argument("task_id")
    p=sub.add_parser("integrate");p.add_argument("task_id");p.add_argument("--confirm",action="store_true")
    p=sub.add_parser("run")
    p.add_argument("--workers",type=int,default=5);p.add_argument("--max-tasks",type=int,default=100)
    p.add_argument("--max-minutes",type=int,default=240);p.add_argument("--max-seconds-per-task",type=int,default=1800)
    p.add_argument("--model",default=MODEL);p.add_argument("--effort",choices=["low","medium","high","xhigh"],default=EFFORT)
    p.add_argument("--test-image",default="");p.add_argument("--test-command-json",default='["python3","-m","unittest","discover","-s","tests","-p","test_*.py"]')
    p.add_argument("--max-repairs",type=int,default=3);p.add_argument("--auto-integrate",action="store_true")
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
        elif args.command=="supervise":report(supervise(state,focus=args.focus,count=args.count,output=args.output,model=args.model,effort=args.effort))
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
        elif args.command in ("stop","pause"):
            marker=state.home/args.command.upper();marker.parent.mkdir(parents=True,exist_ok=True)
            marker.touch(exist_ok=True);report({"control":args.command,"existing_jobs":"stop terminates, pause drains"})
        elif args.command=="resume":
            for x in ("STOP","PAUSE"):(state.home/x).unlink(missing_ok=True)
            report({"controls":"owner_cleared","engine":"not_started"})
        elif args.command=="clear-quota":
            (state.home/"PAUSED_QUOTA").unlink(missing_ok=True)
            report({"quota_pause":"owner_cleared","engine":"not_started"})
        elif args.command=="recover":report({"interrupted_tasks":state.recover(),"auto_restart":False})
        elif args.command=="retry":state.retry(args.task_id);report({"queued":args.task_id})
        elif args.command=="reopen":report({"reopened":state.reopen_failed(args.task_ids),"history_preserved":True})
        elif args.command=="approve-task":state.approve(args.task_id);report({"approved":args.task_id})
        elif args.command=="approve-owner":report(state.approve_owner(args.task_id))
        elif args.command=="integrate":
            if not args.confirm:raise ValueError("integration requires --confirm after diff review")
            with state.master_lock():report(integrate(state,args.task_id,merger_model=MODEL,merger_effort=EFFORT))
        elif args.command=="run":
            command=json.loads(args.test_command_json)
            if not isinstance(command,list):raise ValueError("test command must be a JSON list")
            result=run_master(state,workers=args.workers,max_tasks=args.max_tasks,max_minutes=args.max_minutes,
                              model=args.model,effort=args.effort,test_image=args.test_image,test_command=command,
                              auto_integrate=args.auto_integrate,max_repairs=args.max_repairs,
                              timeout=args.max_seconds_per_task,danger_bypass=args.danger_bypass)
            report(result)
            return 1 if result.get("terminal_failures") else 0
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as ex:
        print("Astra Linux SDA refused: "+str(ex),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
