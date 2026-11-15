"""Astra One command-line launcher. No autonomous start at installation."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.request

from .core import Store, validate_source
from .runner import Progress, execute_claim, publish_manual_state
from .planner import propose


def emit(value:object)->None:
    print(json.dumps(value,ensure_ascii=False,indent=2,default=str))


def doctor(store:Store,source:Path|None)->dict:
    tools={n:bool(shutil.which(n)) for n in ("git","python","codex","ollama","node","npm")}
    report={"engine":"not_started","state_initialized":store.database.exists(),"tools":tools,"model":"qwen3:8b","context":16384}
    if source:
        try:
            root,sha=validate_source(source)
            report["source"]={"root":str(root),"sha":sha,"clean":True}
        except (ValueError,FileNotFoundError) as exc:
            report["source_error"]=str(exc)
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/version",timeout=3) as resp:
            report["ollama_api_available"]=resp.status==200
    except OSError:
        report["ollama_api_available"]=False
    if store.database.exists():
        report["architecture_approved"]=bool(store.config("approved_architecture_sha"))
        report["stopped_marker"]=(store.home/"STOP").exists()
        report["paused_marker"]=(store.home/"PAUSE").exists()
    return report


def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(prog="python -m astra_one",description="Astra One local JARVIS SDA and Cloudflare monitor bridge")
    p.add_argument("--home",type=Path,default=None,help="override local private state directory")
    sub=p.add_subparsers(dest="command",required=True)
    cmd=sub.add_parser("doctor"); cmd.add_argument("--source",type=Path)
    cmd=sub.add_parser("init"); cmd.add_argument("--source",type=Path,required=True)
    cmd=sub.add_parser("architecture"); cmd.add_argument("action",choices=["import","approve","status"]); cmd.add_argument("--file",type=Path); cmd.add_argument("--sha256")
    cmd=sub.add_parser("enqueue"); cmd.add_argument("--file",type=Path,required=True)
    cmd=sub.add_parser("plan");cmd.add_argument("--focus",default="");cmd.add_argument("--count",type=int,default=4);cmd.add_argument("--model",default="qwen3:8b");cmd.add_argument("--output",type=Path)
    cmd=sub.add_parser("enqueue-plan");cmd.add_argument("--file",type=Path,required=True)
    sub.add_parser("status")
    sub.add_parser("tasks")
    cmd=sub.add_parser("run-once"); cmd.add_argument("--model",default="qwen3:8b"); cmd.add_argument("--context",type=int,default=16384); cmd.add_argument("--max-seconds",type=int,default=1800)
    cmd=sub.add_parser("start"); cmd.add_argument("--max-tasks",type=int,default=1); cmd.add_argument("--model",default="qwen3:8b"); cmd.add_argument("--context",type=int,default=16384)
    sub.add_parser("pause"); sub.add_parser("stop"); sub.add_parser("resume"); sub.add_parser("sync")
    cmd=sub.add_parser("approve-task"); cmd.add_argument("task_id")
    cmd=sub.add_parser("retry"); cmd.add_argument("task_id")
    cmd=sub.add_parser("integrate");cmd.add_argument("task_id");cmd.add_argument("--confirm",action="store_true")
    sub.add_parser("recover")
    args=p.parse_args(argv)
    store=Store(args.home) if args.home else Store()
    try:
        if args.command=="doctor": emit(doctor(store,args.source));return 0
        if args.command=="init": emit(store.init(args.source));return 0
        if args.command=="architecture":
            if args.action=="import":
                if not args.file:p.error("architecture import requires --file")
                emit(store.import_architecture(args.file))
            elif args.action=="approve":
                if not args.sha256:p.error("architecture approve requires --sha256")
                store.approve_architecture(args.sha256);emit({"architecture":"approved","sha256":args.sha256,"engine":"not_started"})
            else:emit({"sha256":store.config("architecture_sha"),"approved":store.config("approved_architecture_sha")==store.config("architecture_sha") and bool(store.config("architecture_sha"))})
            return 0
        if args.command=="enqueue":emit(store.add_task(json.loads(args.file.read_text(encoding="utf-8"))));return 0
        if args.command=="plan":emit(propose(store,args.focus,args.count,args.model,args.output));return 0
        if args.command=="enqueue-plan":emit(store.add_plan(json.loads(args.file.read_text(encoding="utf-8"))));return 0
        if args.command=="status":emit(store.overview());return 0
        if args.command=="tasks":emit(store.tasks());return 0
        if args.command in ("pause","stop"):
            marker=store.home/args.command.upper();marker.parent.mkdir(parents=True,exist_ok=True)
            marker.touch(exist_ok=True);emit({"marker":args.command,"message":"Owner control set; active Codex checked at next polling cycle"});return 0
        if args.command=="resume":
            # Explicit action, never bypass marker automatically.
            for name in ("STOP","PAUSE"):
                (store.home/name).unlink(missing_ok=True)
            emit({"controls":"cleared_by_owner","engine":"still_not_started"});return 0
        if args.command=="sync":emit(Progress(store).flush(limit=500));return 0
        if args.command=="approve-task":
            result=store.approve_task(args.task_id);publish_manual_state(store,args.task_id,"approved","owner_review_approved");emit(result);return 0
        if args.command=="retry":store.retry(args.task_id);emit({"task_id":args.task_id,"status":"queued","replay":"explicit"});return 0
        if args.command=="integrate":
            if not args.confirm:p.error("integrate needs --confirm after manual diff review")
            result=store.integrate(args.task_id);publish_manual_state(store,args.task_id,"completed","local_integration_committed");emit(result);return 0
        if args.command=="recover":emit({"interrupted_tasks":store.recover(),"replay":"disabled"});return 0
        if args.command in ("run-once","start"):
            Progress(store)  # Validate remote monitor settings BEFORE claiming a task.
            if args.context<8192 or args.context>40960:p.error("context must be 8192..40960")
            if args.command=="run-once" and not 60<=args.max_seconds<=7200:p.error("max-seconds must be 60..7200")
            count=args.max_tasks if args.command=="start" else 1
            if count<1 or count>20:p.error("max-tasks must be 1..20")
            finished=0
            for _ in range(count):
                claimed=store.claim()
                if not claimed:
                    print("No runnable tasks (queue empty, dependencies pending, architecture unapproved, or STOP/PAUSE).")
                    break
                rc=execute_claim(store,claimed,model=args.model,context=args.context,max_seconds=(args.max_seconds if args.command=="run-once" else 1800))
                finished+=1
                if rc:
                    emit({"tasks_attempted":finished,"last_exit_code":rc,"engine":"stopped"})
                    return rc
            emit({"tasks_attempted":finished,"engine":"stopped","no_background_process":True})
            return 0
    except (ValueError,FileNotFoundError,PermissionError,KeyError, json.JSONDecodeError) as exc:
        print(f"Astra One refused: {exc}",file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
