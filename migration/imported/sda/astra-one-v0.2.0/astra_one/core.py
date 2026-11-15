"""Astra One deterministic local control plane (stdlib only).

No background actions are performed on import, init, task enqueue, or architecture import.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import uuid

SCHEMA_VERSION = 1
TASK_RE = re.compile(r"^[A-Z][A-Z0-9-]{2,48}$")
ALLOWED = {"queued", "blocked", "preflight", "coding", "verifying", "awaiting_review", "approved", "completed", "failed", "stopped", "interrupted"}
FINAL = {"awaiting_review", "approved", "completed", "failed", "stopped", "interrupted"}
DEFAULT_HOME = Path(os.environ.get("ASTRA_ONE_HOME") or (Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AstraOne"))
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks (
  task_id TEXT PRIMARY KEY, spec TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, attempt INTEGER NOT NULL DEFAULT 0,
  last_run_id TEXT, architecture_sha TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(task_id),
  status TEXT NOT NULL, branch TEXT NOT NULL, base_sha TEXT NOT NULL,
  worktree TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
  exit_code INTEGER, tool_count INTEGER NOT NULL DEFAULT 0,
  qc_result TEXT, error_code TEXT, attempt INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, task_id TEXT NOT NULL,
  seq INTEGER NOT NULL, time TEXT NOT NULL, stage TEXT NOT NULL, step TEXT NOT NULL,
  branch TEXT NOT NULL, base_sha TEXT NOT NULL, tool_count INTEGER NOT NULL,
  result TEXT NOT NULL, elapsed_s INTEGER NOT NULL DEFAULT 0, attempt INTEGER NOT NULL,
  synced INTEGER NOT NULL DEFAULT 0, UNIQUE(run_id,seq)
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status,created_at);
CREATE INDEX IF NOT EXISTS idx_events_unsynced ON events(synced,time);
CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id,started_at);
"""


def iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def validate_task(value: object) -> dict:
    if not isinstance(value, dict) or set(value) - {"task_id", "objective", "acceptance", "depends_on", "area"}:
        raise ValueError("task must use only task_id, objective, acceptance, depends_on and area")
    task_id = value.get("task_id")
    if not isinstance(task_id, str) or not TASK_RE.fullmatch(task_id):
        raise ValueError("invalid task_id (e.g. ASTRA-101)")
    objective = value.get("objective")
    if not isinstance(objective, str) or not 10 <= len(objective) <= 3000:
        raise ValueError("objective must be 10..3000 characters")
    acceptance = value.get("acceptance")
    if not isinstance(acceptance, list) or not 1 <= len(acceptance) <= 15 or any(not isinstance(x,str) or not 5 <= len(x) <= 500 for x in acceptance):
        raise ValueError("acceptance must contain 1..15 bounded strings")
    dependencies = value.get("depends_on", [])
    if not isinstance(dependencies,list) or len(dependencies)>20 or any(not isinstance(x,str) or not TASK_RE.fullmatch(x) or x == task_id for x in dependencies) or len(set(dependencies)) != len(dependencies):
        raise ValueError("depends_on must be unique valid other task IDs")
    area=value.get("area", "foundation")
    if not isinstance(area,str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,30}",area):
        raise ValueError("invalid area")
    return {"task_id":task_id,"objective":objective,"acceptance":acceptance,"depends_on":dependencies,"area":area}


def git(root: Path, *args: str, timeout: int = 20) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
    if result.returncode:
        raise ValueError(f"Git command failed: {args[0]}")
    return result.stdout.strip()


def validate_source(root: Path) -> tuple[Path,str]:
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir() or root == Path.home().resolve():
        raise ValueError("source must be a dedicated Git checkout, not home")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("source must be the Git repository root")
    if git(root,"status","--porcelain", "--untracked-files=all"):
        raise ValueError("source checkout is dirty; preserve changes before running SDA")
    sha=git(root,"rev-parse","HEAD")
    if not re.fullmatch(r"[a-f0-9]{40}",sha):
        raise ValueError("invalid source commit")
    return root,sha


class Store:
    def __init__(self, home: Path=DEFAULT_HOME):
        self.home=home.expanduser().resolve()
        self.database=self.home / "astra.sqlite3"

    @contextlib.contextmanager
    def db(self):
        if not self.database.is_file():
            raise ValueError("Astra One not initialized; run init")
        conn=sqlite3.connect(self.database,timeout=15, isolation_level=None)
        conn.row_factory=sqlite3.Row
        conn.execute("PRAGMA busy_timeout=15000")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
        finally:
            conn.close()

    def init(self,source:Path)->dict:
        source,sha=validate_source(source)
        if self.database.exists():
            raise ValueError("state already initialized; refusing to overwrite")
        self.home.mkdir(parents=True,exist_ok=True)
        for name in ("workspaces","codex-home","private","outbox"):
            (self.home/name).mkdir(exist_ok=True)
        conn=sqlite3.connect(self.database)
        try:
            conn.executescript("PRAGMA journal_mode=WAL;"+SCHEMA)
            conn.executemany("INSERT INTO config VALUES (?,?)", [("schema",str(SCHEMA_VERSION)),("source",str(source)),("source_sha",sha),("approved_architecture_sha",""),("architecture_sha",""),("enabled","0"),("integration_sha",sha),("integration_branch", "feature/astra-integration-"+uuid.uuid4().hex[:12]),("integration_path",str(self.home/"integration"))])
            conn.commit()
        finally:
            conn.close()
        return {"state":str(self.home),"source":str(source),"base_sha":sha,"engine":"stopped","architecture":"missing"}

    def config(self,key:str)->str:
        with self.db() as db:
            row=db.execute("SELECT value FROM config WHERE key=?",(key,)).fetchone()
            return row[0] if row else ""

    def set_config(self,key:str,value:str)->None:
        with self.db() as db:
            db.execute("INSERT INTO config(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(key,value))

    def import_architecture(self, path:Path)->dict:
        data=path.read_bytes()
        if not (20<=len(data)<=1_000_000):
            raise ValueError("architecture must be 20 bytes to 1 MB")
        if b"\0" in data:
            raise ValueError("architecture must be a text file")
        data.decode("utf-8")
        sha=hashlib.sha256(data).hexdigest()
        dest=self.home/"private"/f"architecture-{sha[:16]}.md"
        if not dest.exists():
            with dest.open("xb") as f:
                f.write(data)
        self.set_config("architecture_sha",sha)
        # Importing never auto-approves the architecture or starts SDA.
        self.set_config("approved_architecture_sha","")
        self.set_config("enabled","0")
        return {"sha256":sha,"private_path":str(dest),"approved":False,"engine":"stopped"}

    def approve_architecture(self, sha:str)->None:
        actual=self.config("architecture_sha")
        if not actual or actual != sha:
            raise ValueError("architecture sha mismatch; inspect the full file before approval")
        self.set_config("approved_architecture_sha",sha)

    def add_task(self, value:object)->dict:
        task=validate_task(value)
        sha=self.config("approved_architecture_sha")
        if not sha or sha!=self.config("architecture_sha"):
            raise ValueError("approve the imported final architecture before enqueuing tasks")
        with self.db() as db:
            for dep in task["depends_on"]:
                if not db.execute("SELECT 1 FROM tasks WHERE task_id=?",(dep,)).fetchone():
                    raise ValueError(f"unknown dependency {dep}; enqueue prerequisite first")
            now=iso()
            db.execute("INSERT INTO tasks(task_id,spec,status,created_at,updated_at,architecture_sha) VALUES (?,?,?,?,?,?)",(task["task_id"],json.dumps(task,ensure_ascii=False),"queued",now,now,sha))
        return {"task_id":task["task_id"],"status":"queued","dependencies":task["depends_on"]}

    def add_plan(self, tasks:object)->dict:
        """Atomically enqueue an approved ordered local planner proposal."""
        from .planner import validate_plan
        plan=validate_plan(tasks)
        sha=self.config('approved_architecture_sha')
        if not sha or sha!=self.config('architecture_sha'):
            raise ValueError('approve architecture before importing a plan')
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            existing={r[0] for r in db.execute('SELECT task_id FROM tasks')}
            proposed=set()
            now=iso()
            for task in plan:
                if task['task_id'] in existing:
                    raise ValueError('task ID already used: '+task['task_id'])
                if any(dep not in existing and dep not in proposed for dep in task['depends_on']):
                    raise ValueError('dependency missing or wrong order')
                db.execute('INSERT INTO tasks(task_id,spec,status,created_at,updated_at,architecture_sha) VALUES (?,?,?,?,?,?)',(task['task_id'],json.dumps(task,ensure_ascii=False),'queued',now,now,sha))
                proposed.add(task['task_id'])
            db.execute('COMMIT')
        return {'enqueued':len(plan),'task_ids':[task['task_id'] for task in plan],'engine':'not_started'}

    def tasks(self)->list[dict]:
        with self.db() as db:
            rows=db.execute("SELECT task_id,status,created_at,updated_at,attempt,last_run_id FROM tasks ORDER BY created_at,task_id").fetchall()
            return [dict(x) for x in rows]

    def claim(self)->dict|None:
        """SQLite serial claim. Refuse a second active worker and missing owner approval."""
        if (self.home/"STOP").exists() or (self.home/"PAUSE").exists():
            return None
        if not self.config("approved_architecture_sha") or self.config("approved_architecture_sha") != self.config("architecture_sha"):
            return None
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM tasks WHERE status IN ('preflight','coding','verifying') LIMIT 1").fetchone():
                db.execute("COMMIT")
                return None
            candidates=db.execute("SELECT * FROM tasks WHERE status='queued' ORDER BY created_at,task_id").fetchall()
            selected=None
            for row in candidates:
                task=json.loads(row["spec"])
                if all((status:=db.execute("SELECT status FROM tasks WHERE task_id=?",(dep,)).fetchone()) and status[0] == "completed" for dep in task["depends_on"]):
                    selected=row
                    break
            if not selected:
                db.execute("COMMIT")
                return None
            run_id=str(uuid.uuid4())
            attempt=int(selected["attempt"])+1
            db.execute("UPDATE tasks SET status='preflight',attempt=?,last_run_id=?,updated_at=? WHERE task_id=?",(attempt,run_id,iso(),selected["task_id"]))
            db.execute("COMMIT")
            return {"task":json.loads(selected["spec"]),"run_id":run_id,"attempt":attempt}

    def start_run(self,run_id:str,task_id:str,branch:str,sha:str,worktree:Path,attempt:int):
        with self.db() as db:
            db.execute("INSERT INTO runs(run_id,task_id,status,branch,base_sha,worktree,started_at,attempt) VALUES (?,?,?,?,?,?,?,?)",(run_id,task_id,"preflight",branch,sha,str(worktree),iso(),attempt))

    def update_status(self, task_id:str,run_id:str,stage:str,exit_code:int|None=None,qc_result:str|None=None,error_code:str|None=None,tool_count:int=0):
        if stage not in ALLOWED: raise ValueError("invalid stage")
        with self.db() as db:
            db.execute("UPDATE tasks SET status=?,updated_at=? WHERE task_id=?",(stage,iso(),task_id))
            db.execute("UPDATE runs SET status=?, exit_code=COALESCE(?,exit_code), qc_result=COALESCE(?,qc_result), error_code=COALESCE(?,error_code), tool_count=?,finished_at=CASE WHEN ? THEN ? ELSE finished_at END WHERE run_id=?",(stage,exit_code,qc_result,error_code,tool_count,int(stage in FINAL),iso(),run_id))

    def event(self,event:dict)->None:
        with self.db() as db:
            db.execute("INSERT OR IGNORE INTO events(event_id,run_id,task_id,seq,time,stage,step,branch,base_sha,tool_count,result,elapsed_s,attempt) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(event[key] for key in ("event_id","run_id","task_id","seq","time","stage","step","branch","base_sha","tool_count","result","elapsed_s","attempt")))

    def unsynced(self,limit:int=100)->list[dict]:
        with self.db() as db:
            return [dict(row) for row in db.execute("SELECT event_id,run_id,task_id,seq,time,stage,step,branch,base_sha,tool_count,result,elapsed_s,attempt FROM events WHERE synced=0 ORDER BY time,seq LIMIT ?",(limit,)).fetchall()]

    def synced(self,event_id:str)->None:
        with self.db() as db:
            db.execute("UPDATE events SET synced=1 WHERE event_id=?",(event_id,))

    def approve_task(self,task_id:str)->dict:
        with self.db() as db:
            row=db.execute("SELECT t.status,r.worktree,r.qc_result FROM tasks t JOIN runs r ON r.run_id=t.last_run_id WHERE t.task_id=?",(task_id,)).fetchone()
            if not row or row["status"]!="awaiting_review" or row["qc_result"]!="passed":
                raise ValueError("task must have passed QC and await review")
            # Explicit acknowledgement; no Git operations in this command.
            db.execute("UPDATE tasks SET status='approved',updated_at=? WHERE task_id=?",(iso(),task_id))
            db.execute("UPDATE runs SET status='approved' WHERE run_id=(SELECT last_run_id FROM tasks WHERE task_id=?)",(task_id,))
            return {"task_id":task_id,"status":"approved","worktree":row["worktree"],"warning":"No integration or push was performed."}

    def recover(self)->list[str]:
        """Mark possibly orphaned runs interrupted. No automatic replay or termination."""
        with self.db() as db:
            rows=db.execute("SELECT task_id,last_run_id FROM tasks WHERE status IN ('preflight','coding','verifying')").fetchall()
            for row in rows:
                db.execute("UPDATE tasks SET status='interrupted',updated_at=? WHERE task_id=?",(iso(),row["task_id"]))
                db.execute("UPDATE runs SET status='interrupted',finished_at=? WHERE run_id=?",(iso(),row["last_run_id"]))
            return [row["task_id"] for row in rows]

    def retry(self,task_id:str)->None:
        with self.db() as db:
            row=db.execute("SELECT status FROM tasks WHERE task_id=?",(task_id,)).fetchone()
            if not row or row[0] not in ("failed","stopped","interrupted"):
                raise ValueError("only failed/stopped/interrupted tasks can be explicitly retried")
            db.execute("UPDATE tasks SET status='queued',updated_at=? WHERE task_id=?",(iso(),task_id))

    @contextlib.contextmanager
    def integration_lock(self):
        """Single serial integrator, fail closed on stale lock (manual recovery)."""
        path=self.home/"integration.lock"
        try:
            fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError as exc:
            raise ValueError("integration already active or stale lock; inspect manually") from exc
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as handle:
                handle.write(str(os.getpid()))
            yield
        finally:
            path.unlink(missing_ok=True)

    def integrate(self,task_id:str)->dict:
        """Explicitly reviewed local integration. Never touches main/develop/remote."""
        if (self.home/"STOP").exists() or (self.home/"PAUSE").exists():
            raise ValueError("owner STOP/PAUSE prevents integration")
        with self.integration_lock():
            with self.db() as db:
                active=db.execute("SELECT 1 FROM tasks WHERE status IN ('preflight','coding','verifying') LIMIT 1").fetchone()
                if active: raise ValueError("coding worker still active; integration denied")
                row=db.execute("SELECT r.worktree,r.base_sha,r.branch,r.qc_result,t.status FROM tasks t JOIN runs r ON r.run_id=t.last_run_id WHERE t.task_id=?",(task_id,)).fetchone()
                if not row or row["status"]!="approved" or row["qc_result"]!="passed":
                    raise ValueError("integrate only an owner-approved task with passed static QC")
            root,source_sha=validate_source(Path(self.config("source")))
            if source_sha!=self.config("source_sha"):
                raise ValueError("original source checkout changed")
            candidate=Path(row["worktree"]).resolve(strict=True)
            if candidate.parent != (self.home/"workspaces").resolve():
                raise ValueError("candidate worktree must be in Astra-managed workspace")
            if git(candidate,"branch","--show-current")!=row["branch"]:
                raise ValueError("candidate worktree branch mismatch")
            if not git(candidate,"status","--porcelain","--untracked-files=all"):
                raise ValueError("candidate contains no changes to integrate")
            # Use identical static review restrictions before making the local commit.
            from .runner import changes_and_qc
            good,why=changes_and_qc(candidate)
            if not good:raise ValueError("candidate no longer passes static QC: "+why)
            # Git candidate branch and original source share the same local object DB.
            # This explicit operation commits ONLY the candidate, never main/develop.
            git(candidate,"add","--all")
            changed=git(candidate,"diff","--cached","--name-status")
            for line in changed.splitlines():
                if line.startswith(("D\t","R","C")):
                    raise ValueError("deletion, rename or copy operation not supported")
            git(candidate,"-c","user.name=Astra One","-c","user.email=astra-one@local.invalid","commit","-m",f"astra: integrate {task_id} reviewed candidate",timeout=90)
            candidate_sha=git(candidate,"rev-parse","HEAD")
            path=Path(self.config("integration_path"))
            branch=self.config("integration_branch")
            current_sha=self.config("integration_sha")
            if not path.exists():
                proc=subprocess.run(["git","-C",str(root),"worktree","add","-b",branch,str(path),current_sha],capture_output=True,text=True,timeout=60,check=False)
                if proc.returncode:
                    raise ValueError("could not create independent integration worktree")
            if path.is_symlink() or not path.is_dir() or git(path,"branch","--show-current")!=branch:
                raise ValueError("invalid local integration branch")
            if git(path,"rev-parse","HEAD")!=current_sha or git(path,"status","--porcelain","--untracked-files=all"):
                raise ValueError("integration branch changed or dirty; manual review required")
            applied=subprocess.run(["git","-C",str(path),"cherry-pick","--no-commit",candidate_sha],capture_output=True,text=True,timeout=90,check=False)
            if applied.returncode:
                raise ValueError("local cherry-pick conflict: resolve manually; do not auto reset, abort or force-push")
            staged=git(path,"diff","--cached","--name-status")
            if any(line.startswith(("D\t","R","C")) for line in staged.splitlines()):
                raise ValueError("integration contained forbidden deletion or rename; manual review required")
            git(path,"-c","user.name=Astra One","-c","user.email=astra-one@local.invalid","commit","-m",f"astra: {task_id} owner-approved local integration",timeout=90)
            final_sha=git(path,"rev-parse","HEAD")
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("UPDATE config SET value=? WHERE key='integration_sha'",(final_sha,))
                db.execute("UPDATE tasks SET status='completed',updated_at=? WHERE task_id=?",(iso(),task_id))
                db.execute("UPDATE runs SET status='completed',finished_at=? WHERE run_id=(SELECT last_run_id FROM tasks WHERE task_id=?)",(iso(),task_id))
                db.execute("COMMIT")
            return {"task_id":task_id,"status":"completed","integration_branch":branch,"integration_commit":final_sha,"source_main_develop_untouched":True,"remote_push":False}

    def overview(self)->dict:
        with self.db() as db:
            counts=dict(db.execute("SELECT status,count(*) FROM tasks GROUP BY status").fetchall())
            runs=[dict(x) for x in db.execute("SELECT run_id,task_id,status,branch,started_at,finished_at,exit_code,tool_count,qc_result,error_code FROM runs ORDER BY started_at DESC LIMIT 20")]
            unsynced=db.execute("SELECT count(*) FROM events WHERE synced=0").fetchone()[0]
            return {"name":"Astra One", "engine":"stopped" if (self.home/'STOP').exists() else "paused" if (self.home/'PAUSE').exists() else "working" if any(counts.get(x,0) for x in ("preflight","coding","verifying")) else "manual_start_only", "architecture_imported":bool(self.config("architecture_sha")), "architecture_approved":bool(self.config("approved_architecture_sha")), "integration_sha":self.config("integration_sha"),"task_counts":counts,"pending_monitor_events":unsynced,"runs":runs}
