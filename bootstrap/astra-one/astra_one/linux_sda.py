"""Astra One Linux SDA: five bounded Codex workers, independent QC and serial integration.

Only intended for dedicated Linux development checkouts, not production hosts.
No daemon starts at import/install/init. All external actions require a CLI command.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

VERSION = "0.2.1"
MODEL = "gpt-5.6-luna"
EFFORT = "medium"
MAX_WORKERS = 5
MAX_FAILURES = 20
TASK_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,47}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SAFE = re.compile(r"^[a-z0-9_]{2,80}$")
STAGE = {"queued", "preflight", "coding", "verifying", "awaiting_review", "approved", "completed", "failed", "stopped", "interrupted"}
PROTECTED = {"AGENTS.md", "SECURITY.md", "DELETE-LOGS.md", ".env", ".gitignore", "CODEOWNERS"}
PROTECTED_PARTS = {".git", ".codex", ".github", ".ssh", ".aws", "node_modules", ".venv", "__pycache__"}
DEFAULT_HOME = Path.home() / ".local" / "state" / "astra-one-linux"
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(
  id TEXT PRIMARY KEY, spec TEXT NOT NULL, status TEXT NOT NULL, architecture_sha TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 0, available_at INTEGER NOT NULL DEFAULT 0,
  last_run TEXT, last_error TEXT NOT NULL DEFAULT '', candidate_sha TEXT NOT NULL DEFAULT '',
  branch TEXT NOT NULL DEFAULT '', worktree TEXT NOT NULL DEFAULT '',
  base_sha TEXT NOT NULL DEFAULT '', changed_files TEXT NOT NULL DEFAULT '[]',
  qc_evidence TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs(
  id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
  attempt INTEGER NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL,
  started_at TEXT NOT NULL, finished_at TEXT, model TEXT NOT NULL,
  tool_count INTEGER NOT NULL DEFAULT 0, error_code TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS events(
  event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, task_id TEXT NOT NULL,
  seq INTEGER NOT NULL, time TEXT NOT NULL, stage TEXT NOT NULL,step TEXT NOT NULL,
  branch TEXT NOT NULL,base_sha TEXT NOT NULL,tool_count INTEGER NOT NULL,
  result TEXT NOT NULL,elapsed_s INTEGER NOT NULL,attempt INTEGER NOT NULL,
  synced INTEGER NOT NULL DEFAULT 0,UNIQUE(run_id,seq));
CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status,available_at);
CREATE INDEX IF NOT EXISTS idx_event_sync ON events(synced,time);
"""

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")

def git(repo: Path, *args: str, timeout: int = 90) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            capture_output=True, timeout=timeout, check=False)
    if result.returncode:
        raise ValueError("Git " + (args[0] if args else "") + " failed (exit " + str(result.returncode) + ")")
    return result.stdout.strip()

def assert_source(source: Path) -> tuple[Path, str]:
    source = source.expanduser().resolve(strict=True)
    if not source.is_dir() or source == Path.home().resolve():
        raise ValueError("source must be a separate Git checkout, not HOME")
    if Path(git(source, "rev-parse", "--show-toplevel")).resolve() != source:
        raise ValueError("source is not a Git checkout root")
    if git(source, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("source dirty; preserve existing changes and use a clean separate clone")
    sha = git(source, "rev-parse", "HEAD")
    if not SHA.fullmatch(sha):
        raise ValueError("invalid source SHA")
    return source, sha

def task_spec(obj: object) -> dict:
    if not isinstance(obj, dict) or set(obj) - {"task_id", "objective", "acceptance", "depends_on", "area"}:
        raise ValueError("task has unknown fields")
    tid = obj.get("task_id")
    objective = obj.get("objective")
    acceptance = obj.get("acceptance")
    deps = obj.get("depends_on", [])
    area = obj.get("area", "foundation")
    if not isinstance(tid, str) or not TASK_ID.fullmatch(tid):
        raise ValueError("invalid task_id")
    if not isinstance(objective, str) or not 10 <= len(objective) <= 3000:
        raise ValueError("objective must have 10..3000 characters")
    if not isinstance(acceptance, list) or not 1 <= len(acceptance) <= 15 or any(not isinstance(x, str) or not 5 <= len(x) <= 500 for x in acceptance):
        raise ValueError("acceptance criteria must have 1..15 bounded strings")
    if not isinstance(deps, list) or len(deps) > 20 or any(not isinstance(x, str) or not TASK_ID.fullmatch(x) or x == tid for x in deps) or len(set(deps)) != len(deps):
        raise ValueError("invalid dependencies")
    if not isinstance(area, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,30}", area):
        raise ValueError("invalid area")
    return {"task_id": tid, "objective": objective, "acceptance": acceptance, "depends_on": deps, "area": area}

class State:
    def __init__(self, home: Path = DEFAULT_HOME):
        self.home = home.expanduser().resolve()
        self.database = self.home / "sda.sqlite3"
        self._write_lock = threading.RLock()

    @contextlib.contextmanager
    def db(self):
        if not self.database.is_file():
            raise ValueError("Linux SDA is not initialized")
        db = sqlite3.connect(self.database, timeout=20, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=20000")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
        finally:
            db.close()

    @contextlib.contextmanager
    def master_lock(self, blocking: bool = False):
        self.home.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(self.home / "master.lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            op = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
            try:
                fcntl.flock(fd, op)
            except BlockingIOError as ex:
                raise ValueError("another Astra Linux master is running") from ex
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def init(self, source: Path) -> dict:
        if sys.platform != "linux":
            raise ValueError("Linux SDA requires Linux")
        source, sha = assert_source(source)
        if self.database.exists():
            raise ValueError("existing SDA database; refusing to overwrite")
        if self.home == source or self.home in source.parents or source in self.home.parents:
            raise ValueError("state directory must be outside source checkout")
        for path in (self.home, self.home / "private", self.home / "worktrees", self.home / "reports"):
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(path, 0o700)
        db = sqlite3.connect(self.database)
        try:
            db.executescript("PRAGMA journal_mode=WAL;" + SCHEMA)
            cfg = {"source":str(source),"source_sha":sha,"integration_sha":sha,
                   "integration_branch":"feature/astra-linux-integration-" + uuid.uuid4().hex[:10],
                   "integration_path":str(self.home / "integration"),
                   "architecture_sha":"","approved_architecture_sha":"","version":VERSION}
            db.executemany("INSERT INTO settings VALUES(?,?)", cfg.items())
            db.commit()
        finally:
            db.close()
        os.chmod(self.database, 0o600)
        return {"source":str(source),"source_sha":sha,"state":str(self.home),"started":False,"workers":MAX_WORKERS}

    def get(self, key: str) -> str:
        with self.db() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return str(row[0]) if row else ""

    def put(self, key: str, value: str):
        with self.db() as db:
            db.execute("INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key,value))

    def import_architecture(self, file: Path) -> str:
        content = file.read_bytes()
        if not 20 <= len(content) <= 1_000_000 or b"\0" in content:
            raise ValueError("invalid architecture text size")
        content.decode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        name = self.home / "private" / f"architecture-{digest[:16]}.md"
        if not name.exists():
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(content)
        with self.master_lock():
            self.put("architecture_sha",digest)
            self.put("approved_architecture_sha","")
        return digest

    def approve_architecture(self, digest: str):
        if not digest or digest != self.get("architecture_sha"):
            raise ValueError("architecture SHA mismatch")
        with self.master_lock():
            self.put("approved_architecture_sha",digest)

    def ensure_approved(self):
        if not self.get("architecture_sha") or self.get("approved_architecture_sha") != self.get("architecture_sha"):
            raise ValueError("architecture not approved; SDA remains stopped")

    def add_tasks(self, values: object) -> list[str]:
        self.ensure_approved()
        items = values if isinstance(values,list) else [values]
        if not 1 <= len(items) <= 100:
            raise ValueError("plan requires 1..100 tasks")
        tasks = [task_spec(t) for t in items]
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            existing={r[0] for r in db.execute("SELECT id FROM tasks")}
            inserted=set()
            for t in tasks:
                if t["task_id"] in existing or t["task_id"] in inserted:
                    raise ValueError("duplicate task ID")
                if any(dep not in existing and dep not in inserted for dep in t["depends_on"]):
                    raise ValueError("task dependencies must already exist or precede task")
                db.execute("INSERT INTO tasks(id,spec,status,architecture_sha,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                           (t["task_id"],json.dumps(t,ensure_ascii=False),"queued",self.get("architecture_sha"),now(),now()))
                inserted.add(t["task_id"])
            db.execute("COMMIT")
        return [t["task_id"] for t in tasks]

    def list_tasks(self) -> list[dict]:
        with self.db() as db:
            return [dict(r) for r in db.execute("SELECT id,status,attempt,branch,base_sha,candidate_sha,last_error,updated_at FROM tasks ORDER BY created_at,id")]

    def claim(self, model: str = MODEL) -> dict | None:
        self.ensure_approved()
        if any((self.home / x).exists() for x in ("STOP","PAUSE","PAUSED_QUOTA")):
            return None
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            rows=db.execute("SELECT * FROM tasks WHERE status='queued' AND architecture_sha=? AND available_at<=? ORDER BY created_at,id",(self.get("approved_architecture_sha"),int(time.time()))).fetchall()
            for row in rows:
                t=json.loads(row["spec"])
                deps=t["depends_on"]
                if any((found:=db.execute("SELECT status FROM tasks WHERE id=?",(d,)).fetchone()) is None or found[0] != "completed" for d in deps):
                    continue
                attempt=row["attempt"]+1
                rid=str(uuid.uuid4())
                role="worker" if attempt==1 else "repairer"
                db.execute("""UPDATE tasks SET status='preflight',attempt=?,last_run=?,last_error='',
                           candidate_sha='',changed_files='[]',qc_evidence='',base_sha='',branch='',worktree='',updated_at=?
                           WHERE id=?""",(attempt,rid,now(),t["task_id"]))
                db.execute("INSERT INTO runs(id,task_id,attempt,role,status,started_at,model) VALUES (?,?,?,?,?,?,?)",
                           (rid,t["task_id"],attempt,role,"preflight",now(),model))
                db.execute("COMMIT")
                return {"task":t,"run_id":rid,"attempt":attempt,"role":role,"prior_error":row["last_error"]}
            db.execute("COMMIT")
        return None

    def set_task(self, tid: str, status: str, *, error: str = "", fields: dict | None = None):
        if status not in {"queued","preflight","coding","verifying","awaiting_review","approved","completed","failed","interrupted","conflict","stopped"}:
            raise ValueError("unknown task state")
        params = {"status":status,"updated_at":now()}
        error_code = ""
        if error:
            error_code = error[:160]
            params["last_error"] = error_code
        if fields:
            params.update(fields)
        columns=", ".join(f"{k}=?" for k in params)
        with self.db() as db:
            db.execute(f"UPDATE tasks SET {columns} WHERE id=?",tuple(params.values())+(tid,))
            terminal = int(status in {"awaiting_review","approved","completed","failed","interrupted","conflict","stopped"})
            db.execute("""UPDATE runs SET status=?,
                       error_code=CASE WHEN ? <> '' THEN ? ELSE error_code END,
                       finished_at=CASE WHEN ? THEN ? ELSE finished_at END
                       WHERE id=(SELECT last_run FROM tasks WHERE id=?)""",
                       (status,error_code,error_code,terminal,now(),tid))

    def failure_codes(self, tid: str) -> list[str]:
        """Return bounded failure codes in attempt order; never returns model text."""
        with self.db() as db:
            epoch = db.execute("SELECT value FROM settings WHERE key=?", (f"retry_epoch:{tid}",)).fetchone()
            if epoch:
                rows = db.execute(
                    "SELECT error_code FROM runs WHERE task_id=? AND error_code<>'' AND started_at>? "
                    "ORDER BY attempt,started_at", (tid, epoch[0])
                )
            else:
                rows = db.execute(
                    "SELECT error_code FROM runs WHERE task_id=? AND error_code<>'' ORDER BY attempt,started_at",
                    (tid,)
                )
            return [str(row[0])[:160] for row in rows]

    def emit(self, tid: str, run_id: str, *, stage: str, step: str, branch: str, base_sha: str,
             tools: int = 0, attempt: int = 1, elapsed: int = 0, result: str = ""):
        if stage not in STAGE or not SAFE.fullmatch(step) or not branch.startswith(("feature/", "feat/")) or not SHA.fullmatch(base_sha):
            raise ValueError("invalid progress event")
        for retry in range(4):
            try:
                with self.db() as db:
                    db.execute("BEGIN IMMEDIATE")
                    seq = db.execute("SELECT COALESCE(MAX(seq),0)+1 FROM events WHERE run_id=?",(run_id,)).fetchone()[0]
                    values = (str(uuid.uuid4()),run_id,tid,seq,now(),stage,step,branch[:100],base_sha,max(0,tools),result[:100],max(0,int(elapsed)),attempt)
                    db.execute("INSERT INTO events(event_id,run_id,task_id,seq,time,stage,step,branch,base_sha,tool_count,result,elapsed_s,attempt) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",values)
                    db.execute("COMMIT")
                break
            except sqlite3.OperationalError as ex:
                if "locked" not in str(ex).lower() or retry == 3:
                    raise
                time.sleep(0.05 * (2 ** retry))
        print(f"[{stage:<15}] {tid} {step}",flush=True)

    def sync(self, limit: int = 50) -> dict:
        url=os.environ.get("ASTRA_MONITOR_URL","").rstrip("/")
        token=os.environ.get("ASTRA_MONITOR_INGEST_TOKEN","")
        if not url:
            return {"configured":False,"sent":0}
        if not url.startswith("https://") or not token:
            raise ValueError("monitor requires HTTPS URL and ASTRA_MONITOR_INGEST_TOKEN")
        sent=0
        with self.db() as db:
            rows = db.execute("SELECT event_id,run_id,task_id,seq,time,stage,step,branch,base_sha,tool_count,result,elapsed_s,attempt FROM events WHERE synced=0 ORDER BY time,seq LIMIT ?",(limit,)).fetchall()
        for r in rows:
            event=dict(r)
            req=urllib.request.Request(url+"/api/events",method="POST",data=json.dumps(event).encode(),headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"Astra-One-Linux/0.2"})
            try:
                with urllib.request.urlopen(req,timeout=3) as resp:
                    if resp.status not in (200,201):
                        break
                with self.db() as db:
                    db.execute("UPDATE events SET synced=1 WHERE event_id=?",(r["event_id"],))
                sent+=1
            except (OSError,urllib.error.URLError,TimeoutError):
                break
        return {"configured":True,"sent":sent}

    def recover(self) -> list[str]:
        with self.master_lock():
            with self.db() as db:
                rows=db.execute("SELECT id FROM tasks WHERE status IN ('preflight','coding','verifying')").fetchall()
                for r in rows:
                    db.execute("UPDATE tasks SET status='interrupted',last_error='master_restart_review_required',updated_at=? WHERE id=?",(now(),r["id"]))
                    db.execute("UPDATE runs SET status='interrupted',finished_at=? WHERE id=(SELECT last_run FROM tasks WHERE id=?)",(now(),r["id"]))
                return [r["id"] for r in rows]

    def retry(self, tid: str):
        with self.db() as db:
            row=db.execute("SELECT status,attempt FROM tasks WHERE id=?",(tid,)).fetchone()
            if not row or row["status"] not in {"failed","interrupted","conflict","stopped"} or row["attempt"]>=MAX_FAILURES:
                raise ValueError("only failed/interrupted/conflict/stopped tasks below retry ceiling can retry")
            db.execute("UPDATE tasks SET status='queued',available_at=0,updated_at=? WHERE id=?",(now(),tid))

    def reopen_failed(self, task_ids: list[str]) -> list[str]:
        """Start an explicit new bounded repair generation without erasing history."""
        if not task_ids or len(task_ids) > 100 or len(set(task_ids)) != len(task_ids):
            raise ValueError("one or more task IDs required")
        with self.master_lock():
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                reopened = []
                epoch = now()
                for tid in task_ids:
                    row = db.execute("SELECT status FROM tasks WHERE id=?", (tid,)).fetchone()
                    if not row or row["status"] != "failed":
                        raise ValueError("only failed tasks can start a new repair generation")
                    db.execute(
                        "UPDATE tasks SET status='queued',attempt=0,available_at=0,last_error='',"
                        "candidate_sha='',changed_files='[]',qc_evidence='',base_sha='',branch='',worktree='',updated_at=? "
                        "WHERE id=?", (epoch, tid)
                    )
                    db.execute(
                        "INSERT INTO settings(key,value) VALUES(?,?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (f"retry_epoch:{tid}", epoch),
                    )
                    reopened.append(tid)
                db.execute("COMMIT")
                return reopened

    def approve(self, tid: str):
        with self.db() as db:
            row=db.execute("SELECT status,qc_evidence FROM tasks WHERE id=?",(tid,)).fetchone()
            if not row or row["status"]!="awaiting_review" or not row["qc_evidence"]:
                raise ValueError("task must pass independent QC before approval")
            db.execute("UPDATE tasks SET status='approved',updated_at=? WHERE id=?",(now(),tid))

    def overview(self) -> dict:
        with self.db() as db:
            counts={r[0]:r[1] for r in db.execute("SELECT status,count(*) FROM tasks GROUP BY status")}
            pending=db.execute("SELECT count(*) FROM events WHERE synced=0").fetchone()[0]
        return {"version":VERSION,"state_version":self.get("version"),"approved_architecture":bool(self.get("approved_architecture_sha")),"workers_max":MAX_WORKERS,"integration_sha":self.get("integration_sha"),"tasks":counts,"monitor_pending":pending,
                "stop":(self.home/"STOP").exists(),"pause":(self.home/"PAUSE").exists(),"quota_pause":(self.home/"PAUSED_QUOTA").exists()}
