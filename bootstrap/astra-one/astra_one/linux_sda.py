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

from .full_plan import (FullPlan, PROJECT_ID, payload_sha, render_task_markdown,
                        validate_task_markdown)
from .owner_approval import OwnerApprovalError, prepare_receipt, verify_receipt

VERSION = "0.3.0"
SCHEMA_VERSION = 5
MODEL = "gpt-5.6-luna"
EFFORT = "medium"
MAX_WORKERS = 5
MAX_FAILURES = 20
QUEUE_NAMES = ("project_queue", "pending_queue", "rebuild_queue", "review_queue", "merge_queue")
TASK_EXECUTION_MODES = frozenset({
    "worker", "implementation", "audit", "verification", "migration", "design",
    "owner_gate", "ci_local_only",
})
TASK_ID = re.compile(r"^[A-Z][A-Z0-9-]{2,47}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE = re.compile(r"^[a-z0-9_]{2,80}$")
EVENT_RESULT = re.compile(r"^[A-Za-z0-9_.:=/,-]{0,100}$")
STAGE = {"queued", "preflight", "coding", "verifying", "awaiting_review", "approved", "completed", "failed", "stopped", "interrupted"}
PROTECTED = {"AGENTS.md", "SECURITY.md", "DELETE-LOGS.md", ".env", ".gitignore", "CODEOWNERS"}
PROTECTED_PARTS = {".git", ".codex", ".github", ".ssh", ".aws", "node_modules", ".venv", "__pycache__"}
DEFAULT_HOME = Path.home() / ".local" / "state" / "archon-astra"
BUILDER_SESSION = re.compile(r"^[A-Za-z0-9_.:-]{1,120}$")
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(
  id TEXT PRIMARY KEY, spec TEXT NOT NULL, status TEXT NOT NULL, architecture_sha TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 0, available_at INTEGER NOT NULL DEFAULT 0,
  last_run TEXT, last_error TEXT NOT NULL DEFAULT '', candidate_sha TEXT NOT NULL DEFAULT '',
  integrated_sha TEXT NOT NULL DEFAULT '',
  branch TEXT NOT NULL DEFAULT '', worktree TEXT NOT NULL DEFAULT '',
  base_sha TEXT NOT NULL DEFAULT '', changed_files TEXT NOT NULL DEFAULT '[]',
  qc_evidence TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  project_id TEXT NOT NULL DEFAULT '', module TEXT NOT NULL DEFAULT '',
  milestone TEXT NOT NULL DEFAULT '', priority TEXT NOT NULL DEFAULT 'P4',
  owner_gate INTEGER NOT NULL DEFAULT 0, payload_sha TEXT NOT NULL DEFAULT '',
  enqueue_seq INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS runs(
  id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
  attempt INTEGER NOT NULL, role TEXT NOT NULL, status TEXT NOT NULL,
  started_at TEXT NOT NULL, finished_at TEXT, model TEXT NOT NULL,
  tool_count INTEGER NOT NULL DEFAULT 0, error_code TEXT NOT NULL DEFAULT '',
  thread_id TEXT NOT NULL DEFAULT '', input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0, tool_effects TEXT NOT NULL DEFAULT '[]',
  error_category TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS events(
  event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL, task_id TEXT NOT NULL,
  seq INTEGER NOT NULL, time TEXT NOT NULL, stage TEXT NOT NULL,step TEXT NOT NULL,
  branch TEXT NOT NULL,base_sha TEXT NOT NULL,tool_count INTEGER NOT NULL,
  result TEXT NOT NULL,elapsed_s INTEGER NOT NULL,attempt INTEGER NOT NULL,
  synced INTEGER NOT NULL DEFAULT 0,UNIQUE(run_id,seq));
CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status,available_at);
CREATE INDEX IF NOT EXISTS idx_event_sync ON events(synced,time);
CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS projects(
  id TEXT PRIMARY KEY, name TEXT NOT NULL, source_repository TEXT NOT NULL,
  integration_branch TEXT NOT NULL, parent_task_count INTEGER NOT NULL,
  subtask_count INTEGER NOT NULL, workers INTEGER NOT NULL, model TEXT NOT NULL,
  reasoning TEXT NOT NULL, source_ref TEXT NOT NULL, source_commit TEXT NOT NULL,
  parent_plan_blob_sha TEXT NOT NULL, subtask_index_sha TEXT NOT NULL,
  payload_sha TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS project_queue(
  project_id TEXT PRIMARY KEY REFERENCES projects(id), status TEXT NOT NULL,
  enqueue_seq INTEGER NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS subtasks(
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
  parent_id TEXT NOT NULL REFERENCES tasks(id), sequence INTEGER NOT NULL,
  spec TEXT NOT NULL, status TEXT NOT NULL, payload_sha TEXT NOT NULL,
  evidence TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  UNIQUE(parent_id,sequence));
CREATE TABLE IF NOT EXISTS pending_queue(
  parent_id TEXT PRIMARY KEY REFERENCES tasks(id), project_id TEXT NOT NULL,
  enqueue_seq INTEGER NOT NULL, available_at INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rebuild_queue(
  parent_id TEXT PRIMARY KEY REFERENCES tasks(id), project_id TEXT NOT NULL,
  generation INTEGER NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS review_queue(
  parent_id TEXT PRIMARY KEY REFERENCES tasks(id), project_id TEXT NOT NULL,
  candidate_sha TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS merge_queue(
  parent_id TEXT PRIMARY KEY REFERENCES tasks(id), project_id TEXT NOT NULL,
  candidate_sha TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS candidate_submissions(
  submission_id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL REFERENCES tasks(id),
  run_id TEXT NOT NULL,
  attempt INTEGER NOT NULL,
  builder_session_id TEXT NOT NULL,
  base_sha TEXT NOT NULL,
  candidate_sha TEXT NOT NULL,
  branch TEXT NOT NULL,
  worktree TEXT NOT NULL,
  changed_files TEXT NOT NULL,
  test_evidence TEXT NOT NULL,
  acceptance_evidence TEXT NOT NULL,
  status TEXT NOT NULL,
  failure_code TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(task_id,attempt,candidate_sha));
CREATE INDEX IF NOT EXISTS idx_candidate_submissions_status
  ON candidate_submissions(status,created_at);
CREATE TABLE IF NOT EXISTS candidate_quarantine(
  quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id TEXT NOT NULL REFERENCES tasks(id),
  attempt INTEGER NOT NULL,
  candidate_sha TEXT NOT NULL DEFAULT '',
  branch TEXT NOT NULL DEFAULT '',
  worktree TEXT NOT NULL DEFAULT '',
  failure_code TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(task_id,attempt,candidate_sha,failure_code)
);
CREATE INDEX IF NOT EXISTS idx_candidate_quarantine_task
  ON candidate_quarantine(task_id,attempt,created_at);
CREATE TABLE IF NOT EXISTS subtask_receipts(
  receipt_id TEXT PRIMARY KEY,
  subtask_id TEXT NOT NULL REFERENCES subtasks(id),
  parent_id TEXT NOT NULL REFERENCES tasks(id),
  generation INTEGER NOT NULL,
  source_sha TEXT NOT NULL,
  candidate_sha TEXT NOT NULL,
  changed_files TEXT NOT NULL,
  test_ref TEXT NOT NULL,
  test_artifact_sha TEXT NOT NULL DEFAULT '',
  qc_receipt TEXT NOT NULL,
  qc_artifact_sha TEXT NOT NULL DEFAULT '',
  evidence_sha TEXT NOT NULL,
  contract_sha TEXT NOT NULL,
  verifier TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(subtask_id,candidate_sha));
CREATE INDEX IF NOT EXISTS idx_subtask_receipts_parent ON subtask_receipts(parent_id,candidate_sha);
CREATE TABLE IF NOT EXISTS owner_approval_receipts(
  receipt_id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL REFERENCES tasks(id),
  decision TEXT NOT NULL CHECK(decision IN ('APPROVE','REJECT','DEFER')),
  packet_sha256 TEXT NOT NULL,
  full_architecture_sha256 TEXT NOT NULL,
  bounded_focus_sha256 TEXT NOT NULL,
  parent_payload_sha256 TEXT NOT NULL,
  source_sha TEXT NOT NULL,
  integration_sha TEXT NOT NULL,
  owner_identity TEXT NOT NULL,
  receipt_path TEXT NOT NULL,
  receipt_sha256 TEXT NOT NULL,
  allowed_signers_sha256 TEXT NOT NULL,
  signature_algorithm TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(task_id,receipt_sha256));
CREATE INDEX IF NOT EXISTS idx_owner_approval_receipts_task ON owner_approval_receipts(task_id,created_at);
CREATE TABLE IF NOT EXISTS owner_subtask_receipts(
  receipt_id TEXT PRIMARY KEY,
  subtask_id TEXT NOT NULL REFERENCES subtasks(id),
  parent_id TEXT NOT NULL REFERENCES tasks(id),
  generation INTEGER NOT NULL,
  owner_receipt_sha256 TEXT NOT NULL,
  evidence_sha256 TEXT NOT NULL,
  verifier TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(subtask_id,owner_receipt_sha256));
CREATE INDEX IF NOT EXISTS idx_owner_subtask_receipts_parent ON owner_subtask_receipts(parent_id,owner_receipt_sha256);
CREATE TABLE IF NOT EXISTS supervisor_cases(
  case_id TEXT PRIMARY KEY,
  parent_id TEXT NOT NULL REFERENCES tasks(id),
  generation INTEGER NOT NULL,
  state TEXT NOT NULL,
  category TEXT NOT NULL,
  failure_fingerprint TEXT NOT NULL,
  failure_code TEXT NOT NULL,
  base_sha TEXT NOT NULL DEFAULT '',
  candidate_sha TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(parent_id,generation,failure_fingerprint));
CREATE INDEX IF NOT EXISTS idx_supervisor_cases_state ON supervisor_cases(state,updated_at);
CREATE TABLE IF NOT EXISTS external_resolution_receipts(
  receipt_id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL REFERENCES supervisor_cases(case_id),
  task_id TEXT NOT NULL REFERENCES tasks(id),
  category TEXT NOT NULL,
  evidence_path TEXT NOT NULL,
  evidence_sha256 TEXT NOT NULL,
  backup_path TEXT NOT NULL,
  backup_sha256 TEXT NOT NULL,
  source_sha TEXT NOT NULL,
  integration_sha TEXT NOT NULL,
  verifier TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(case_id,evidence_sha256));
CREATE INDEX IF NOT EXISTS idx_external_resolution_task ON external_resolution_receipts(task_id,created_at);
CREATE TABLE IF NOT EXISTS supervisor_lanes(
  lane_id TEXT PRIMARY KEY CHECK(lane_id IN ('repair_1','repair_2','upgrade_auditor')),
  role TEXT NOT NULL,
  task_id TEXT NOT NULL DEFAULT '',
  case_id TEXT NOT NULL DEFAULT '',
  state TEXT NOT NULL,
  lease_token TEXT NOT NULL DEFAULT '',
  generation INTEGER NOT NULL DEFAULT 0,
  run_id TEXT NOT NULL DEFAULT '',
  candidate_sha TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS upgrade_batches(
  batch_id TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  candidate_sha TEXT NOT NULL DEFAULT '',
  rollback_sha TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL,
  created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS upgrade_checks(
  batch_id TEXT NOT NULL REFERENCES upgrade_batches(batch_id),
  stage TEXT NOT NULL,
  result TEXT NOT NULL,
  artifact_sha TEXT NOT NULL,
  evidence_sha TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  verifier TEXT NOT NULL,
  PRIMARY KEY(batch_id,stage));
CREATE TABLE IF NOT EXISTS upgrade_rollbacks(
  rollback_id TEXT PRIMARY KEY,
  batch_id TEXT NOT NULL REFERENCES upgrade_batches(batch_id),
  state TEXT NOT NULL,
  rollback_sha TEXT NOT NULL,
  current_head TEXT NOT NULL,
  backup_path TEXT NOT NULL,
  backup_sha TEXT NOT NULL,
  created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS upgrade_audits(
  audit_id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL REFERENCES tasks(id),
  lane_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  model TEXT NOT NULL,
  status TEXT NOT NULL,
  report_path TEXT NOT NULL DEFAULT '',
  report_sha TEXT NOT NULL DEFAULT '',
  evidence_sha TEXT NOT NULL DEFAULT '',
  failure_code TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS batch_epochs(
  batch_id TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  admitted_count INTEGER NOT NULL DEFAULT 0,
  completed_count INTEGER NOT NULL DEFAULT 0,
  target_count INTEGER NOT NULL DEFAULT 20,
  updated_at TEXT NOT NULL,
  created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS batch_members(
  batch_id TEXT NOT NULL REFERENCES batch_epochs(batch_id),
  parent_id TEXT NOT NULL REFERENCES tasks(id),
  ordinal INTEGER NOT NULL,
  state TEXT NOT NULL,
  admitted_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY(batch_id,parent_id));
CREATE INDEX IF NOT EXISTS idx_batch_members_parent ON batch_members(parent_id,batch_id);
CREATE INDEX IF NOT EXISTS idx_pending_queue ON pending_queue(available_at,enqueue_seq);
CREATE INDEX IF NOT EXISTS idx_subtasks_parent ON subtasks(parent_id,sequence);
CREATE INDEX IF NOT EXISTS idx_project_tasks ON tasks(project_id,status,enqueue_seq);
"""

LEGACY_TASK_COLUMNS = {
    "project_id": "TEXT NOT NULL DEFAULT ''",
    "module": "TEXT NOT NULL DEFAULT ''",
    "milestone": "TEXT NOT NULL DEFAULT ''",
    "priority": "TEXT NOT NULL DEFAULT 'P4'",
    "owner_gate": "INTEGER NOT NULL DEFAULT 0",
    "payload_sha": "TEXT NOT NULL DEFAULT ''",
    "enqueue_seq": "INTEGER NOT NULL DEFAULT 0",
    "integrated_sha": "TEXT NOT NULL DEFAULT ''",
}


def _full_plan_ddl() -> tuple[str, ...]:
    """DDL for the additive v2 task-plan schema migration."""
    return tuple(statement.strip() for statement in SCHEMA.split(";")
                 if statement.strip() and not statement.strip().startswith("PRAGMA"))


def _ensure_v3_columns(db: sqlite3.Connection) -> None:
    """Apply only additive columns needed when a v3 table predates this build."""
    receipt_columns = {row[1] for row in db.execute("PRAGMA table_info(subtask_receipts)")}
    if receipt_columns and "contract_sha" not in receipt_columns:
        db.execute("ALTER TABLE subtask_receipts ADD COLUMN contract_sha TEXT NOT NULL DEFAULT ''")
    if receipt_columns and "test_artifact_sha" not in receipt_columns:
        db.execute("ALTER TABLE subtask_receipts ADD COLUMN test_artifact_sha TEXT NOT NULL DEFAULT ''")
    if receipt_columns and "qc_artifact_sha" not in receipt_columns:
        db.execute("ALTER TABLE subtask_receipts ADD COLUMN qc_artifact_sha TEXT NOT NULL DEFAULT ''")
    batch_columns = {row[1] for row in db.execute("PRAGMA table_info(batch_epochs)")}
    if batch_columns and "target_count" not in batch_columns:
        db.execute("ALTER TABLE batch_epochs ADD COLUMN target_count INTEGER NOT NULL DEFAULT 20")
    check_columns = {row[1] for row in db.execute("PRAGMA table_info(upgrade_checks)")}
    if check_columns and "evidence_sha" not in check_columns:
        db.execute("ALTER TABLE upgrade_checks ADD COLUMN evidence_sha TEXT NOT NULL DEFAULT ''")
    lane_columns = {row[1] for row in db.execute("PRAGMA table_info(supervisor_lanes)")}
    if lane_columns:
        if "generation" not in lane_columns:
            db.execute("ALTER TABLE supervisor_lanes ADD COLUMN generation INTEGER NOT NULL DEFAULT 0")
        if "run_id" not in lane_columns:
            db.execute("ALTER TABLE supervisor_lanes ADD COLUMN run_id TEXT NOT NULL DEFAULT ''")
        if "candidate_sha" not in lane_columns:
            db.execute("ALTER TABLE supervisor_lanes ADD COLUMN candidate_sha TEXT NOT NULL DEFAULT ''")

def _ensure_codex_receipt_columns(db: sqlite3.Connection) -> None:
    """Add bounded Codex receipt fields without rewriting existing run history."""
    run_columns = {row[1] for row in db.execute("PRAGMA table_info(runs)")}
    additions = {
        "thread_id": "TEXT NOT NULL DEFAULT ''",
        "input_tokens": "INTEGER NOT NULL DEFAULT 0",
        "output_tokens": "INTEGER NOT NULL DEFAULT 0",
        "tool_effects": "TEXT NOT NULL DEFAULT '[]'",
        "error_category": "TEXT NOT NULL DEFAULT ''",
    }
    for name, declaration in additions.items():
        if run_columns and name not in run_columns:
            db.execute(f"ALTER TABLE runs ADD COLUMN {name} {declaration}")

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")

def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _checkpoint_value(value: object) -> object:
    """Normalize SQLite values before hashing without retaining their contents."""
    if isinstance(value, bytes):
        return {"bytes_sha256": hashlib.sha256(value).hexdigest(), "bytes": len(value)}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _database_state_digest(db: sqlite3.Connection) -> str:
    """Hash every persisted row so a restore drill proves state, not just schema."""
    digest = hashlib.sha256()
    tables = [row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]
    for name in tables:
        identifier = name.replace('"', '""')
        digest.update(_canonical_json({"table": name}))
        for row in db.execute(f'SELECT * FROM "{identifier}" ORDER BY rowid'):
            digest.update(_canonical_json([_checkpoint_value(value) for value in row]))
    return digest.hexdigest()

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
    allowed = {"task_id", "objective", "acceptance", "depends_on", "area", "execution_mode", "subtasks"}
    if not isinstance(obj, dict) or set(obj) - allowed:
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
    result = {"task_id": tid, "objective": objective, "acceptance": acceptance,
              "depends_on": deps, "area": area}
    if "execution_mode" in obj:
        result["execution_mode"] = obj["execution_mode"]
    if "subtasks" in obj:
        result["subtasks"] = obj["subtasks"]
    if "execution_mode" in result or "subtasks" in result:
        validate_task_type(result)
    return result


def validate_task_type(task: object) -> str:
    """Validate the persisted task packet before assigning any worker lane."""
    if not isinstance(task, dict):
        raise ValueError("task_type_invalid")
    mode = task.get("execution_mode", "worker")
    if mode not in TASK_EXECUTION_MODES:
        raise ValueError("task_type_invalid")
    children = task.get("subtasks", [])
    if children is None:
        children = []
    if not isinstance(children, list):
        raise ValueError("task_type_invalid")
    if children:
        sequences = []
        identifiers = set()
        for child in children:
            if not isinstance(child, dict):
                raise ValueError("task_type_invalid")
            child_id = child.get("id")
            sequence = child.get("sequence")
            if (not isinstance(child_id, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,160}", child_id)
                    or child_id in identifiers or type(sequence) is not int or sequence < 1):
                raise ValueError("task_type_invalid")
            if any(not isinstance(child.get(key), str) or not child.get(key)
                   for key in ("instruction", "deliverable", "done_when")):
                raise ValueError("task_type_invalid")
            deps = child.get("depends_on", [])
            if not isinstance(deps, list) or any(not isinstance(dep, str) or not dep for dep in deps):
                raise ValueError("task_type_invalid")
            identifiers.add(child_id)
            sequences.append(sequence)
        if sorted(sequences) != list(range(1, len(sequences) + 1)):
            raise ValueError("task_type_invalid")
        if any(dep not in identifiers or dep == child_id
               for child in children for dep in child.get("depends_on", [])
               for child_id in (child.get("id"),)):
            raise ValueError("task_type_invalid")
    roots = task.get("suggested_scope_roots", [])
    if roots is not None:
        if (not isinstance(roots, list) or len(roots) > 20
                or any(not isinstance(root, str) or not root or root.startswith(("/", "\\"))
                       or ".." in Path(root).parts or "\\" in root for root in roots)):
            raise ValueError("task_type_invalid")
    if mode == "design" and not children:
        raise ValueError("task_type_invalid")
    return mode


def control_blocked(home: Path, lane: str) -> bool:
    """Return whether deterministic controls block a new claim for one lane."""
    if lane not in {"normal", "recovery"}:
        raise ValueError("invalid control lane")
    global_markers = ("STOP", "PAUSE", "PAUSED_QUOTA")
    lane_marker = "PAUSE_NORMAL" if lane == "normal" else "PAUSE_RECOVERY"
    return any((home / marker).exists() for marker in (*global_markers, lane_marker))


def builder_branch(task: dict, attempt: int, run_id: str) -> str:
    """Keep builder branches identical to the established task convention."""
    prefixes = {"core": "CORE", "sda": "SDA", "backend": "BACK", "guardian": "GUARD",
                "migration": "MIG", "runtime": "RUN", "research": "RES", "tws": "TWS",
                "wic": "WIC", "finance": "FIN", "automation": "AUTO"}
    area = task.get("area", "foundation")
    if prefixes.get(area) and str(task.get("task_id", "")).startswith(prefixes[area] + "-"):
        return f"feat/{area}/{task['task_id']}-implementation-a{attempt}-{run_id[:8]}"
    return f"feature/astra-{str(task['task_id']).lower()}-a{attempt}-{run_id[:8]}"


def _bounded_evidence(value: object, name: str) -> str:
    """Store bounded metadata only; model prose and raw logs are not receipts."""
    if not isinstance(value, list) or len(value) > 40:
        raise ValueError(f"{name} must be a bounded JSON list")
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(raw.encode("utf-8")) > 16_000:
        raise ValueError(f"{name} exceeds the receipt limit")
    forbidden = re.compile(r"(?i)(secret|credential|token|password|prompt|model.?output|raw.?log|private.?key)")
    def inspect(item: object) -> None:
        if isinstance(item, str):
            if len(item) > 500 or forbidden.search(item):
                raise ValueError(f"{name} contains unbounded or sensitive text")
        elif isinstance(item, list):
            for child in item:
                inspect(child)
        elif isinstance(item, dict):
            if len(item) > 20:
                raise ValueError(f"{name} contains too many fields")
            for key, child in item.items():
                if not isinstance(key, str) or len(key) > 80 or forbidden.search(key):
                    raise ValueError(f"{name} contains a sensitive field")
                inspect(child)
        elif item is not None and not isinstance(item, (bool, int, float)):
            raise ValueError(f"{name} contains unsupported metadata")
    inspect(value)
    return raw


def _validate_builder_child_evidence(child_ids: list[str], value: object) -> None:
    """Reject an incomplete child envelope before it reaches the QC queue."""
    if (not isinstance(value, list) or len(value) != len(child_ids)
            or {item.get("subtask_id") for item in value if isinstance(item, dict)} != set(child_ids)):
        raise ValueError("invalid_builder_child_evidence")
    for item in value:
        if (not isinstance(item, dict) or item.get("status") != "PASS"
                or not isinstance(item.get("evidence"), str)
                or not 1 <= len(item["evidence"]) <= 240):
            raise ValueError("invalid_builder_child_evidence")

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
    def master_lock(self, blocking: bool = False, timeout: float = 30.0):
        if timeout <= 0 or timeout > 300:
            raise ValueError("invalid master lock timeout")
        self.home.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(self.home / "master.lock", os.O_CREAT | os.O_RDWR, 0o600)
        try:
            deadline = time.monotonic() + timeout
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError as ex:
                    if not blocking or time.monotonic() >= deadline:
                        raise ValueError("another Astra Linux master is running") from ex
                    time.sleep(0.05)
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    @contextlib.contextmanager
    def controller_lock(self, blocking: bool = False, timeout: float = 30.0):
        """Fence one long-lived SDA controller; kernel flock owns liveness."""
        if timeout <= 0 or timeout > 300:
            raise ValueError("invalid controller lock timeout")
        self.home.mkdir(mode=0o700, parents=True, exist_ok=True)
        lock_path = self.home / "controller.lock"
        owner_path = self.home / "controller.owner.json"
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        acquired = False
        owner = {"pid": os.getpid(), "started_at": now()}
        try:
            deadline = time.monotonic() + timeout
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    acquired = True
                    break
                except BlockingIOError as ex:
                    if not blocking or time.monotonic() >= deadline:
                        raise ValueError("another Astra One controller is running") from ex
                    time.sleep(0.05)
            if owner_path.is_symlink():
                raise ValueError("controller owner metadata is a symlink")
            owner_path.write_text(json.dumps(owner, separators=(",", ":")) + "\n", encoding="utf-8")
            yield
        finally:
            if acquired:
                try:
                    if not owner_path.is_symlink() and owner_path.is_file():
                        current = json.loads(owner_path.read_text(encoding="utf-8"))
                        if current == owner:
                            owner_path.unlink(missing_ok=True)
                except (OSError, UnicodeError, json.JSONDecodeError):
                    pass
                fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def ensure_full_plan_schema(self) -> dict:
        """Apply only the additive, reversible full-plan schema migration."""
        with self.master_lock():
            with self.db() as db:
                current = int(db.execute("PRAGMA user_version").fetchone()[0])
                if current > SCHEMA_VERSION:
                    raise ValueError("database schema is newer than this Astra One runtime")
                if current == SCHEMA_VERSION:
                    for statement in _full_plan_ddl():
                        db.execute(statement)
                    _ensure_v3_columns(db)
                    _ensure_codex_receipt_columns(db)
                    db.executemany(
                        "INSERT OR IGNORE INTO supervisor_lanes(lane_id,role,state,updated_at) VALUES(?,?,?,?)",
                        (("repair_1", "recovery_coder", "idle", now()),
                         ("repair_2", "recovery_coder", "idle", now()),
                         ("upgrade_auditor", "upgrade_auditor", "idle", now())),
                    )
                    db.execute(
                        "INSERT INTO settings(key,value) VALUES('version',?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (VERSION,),
                    )
                    return {"schema_version": current, "migrated": False}
                db.execute("BEGIN IMMEDIATE")
                columns = {row[1] for row in db.execute("PRAGMA table_info(tasks)")}
                for name, declaration in LEGACY_TASK_COLUMNS.items():
                    if name not in columns:
                        db.execute(f"ALTER TABLE tasks ADD COLUMN {name} {declaration}")
                for statement in _full_plan_ddl():
                    db.execute(statement)
                _ensure_v3_columns(db)
                _ensure_codex_receipt_columns(db)
                db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
                db.execute(
                    "INSERT INTO settings(key,value) VALUES('schema_version',?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (str(SCHEMA_VERSION),),
                )
                db.execute(
                    "INSERT INTO settings(key,value) VALUES('version',?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (VERSION,),
                )
                db.execute(
                    "INSERT OR IGNORE INTO schema_migrations(version,applied_at) VALUES(?,?)",
                    (SCHEMA_VERSION, now()),
                )
                db.executemany(
                    "INSERT OR IGNORE INTO supervisor_lanes(lane_id,role,state,updated_at) VALUES(?,?,?,?)",
                    (("repair_1", "recovery_coder", "idle", now()),
                     ("repair_2", "recovery_coder", "idle", now()),
                     ("upgrade_auditor", "upgrade_auditor", "idle", now())),
                )
                db.execute("COMMIT")
                return {"schema_version": SCHEMA_VERSION, "migrated": True}

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
            db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            cfg = {"source":str(source),"source_sha":sha,"integration_sha":sha,
                   "integration_branch":"feature/astra-linux-integration-" + uuid.uuid4().hex[:10],
                   "integration_path":str(self.home / "integration"),
                   "architecture_sha":"","approved_architecture_sha":"","version":VERSION,
                   "schema_version":str(SCHEMA_VERSION)}
            db.executemany("INSERT INTO settings VALUES(?,?)", cfg.items())
            db.execute("INSERT OR IGNORE INTO schema_migrations(version,applied_at) VALUES(?,?)",
                       (SCHEMA_VERSION, now()))
            db.executemany(
                "INSERT OR IGNORE INTO supervisor_lanes(lane_id,role,state,updated_at) VALUES(?,?,?,?)",
                (("repair_1", "recovery_coder", "idle", now()),
                 ("repair_2", "recovery_coder", "idle", now()),
                 ("upgrade_auditor", "upgrade_auditor", "idle", now())),
            )
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

    def _checkpoint_snapshot(self, db: sqlite3.Connection) -> dict:
        """Return bounded metadata; the SQLite backup remains the source of truth."""
        settings = dict(db.execute(
            "SELECT key,value FROM settings WHERE key IN "
            "('source','source_sha','integration_path','integration_sha','integration_branch',"
            "'architecture_sha','approved_architecture_sha','version','schema_version')"
        ).fetchall())
        counts = {}
        for table in ("tasks", "runs", "events", "subtasks", "subtask_receipts",
                      "owner_approval_receipts", "candidate_submissions", "review_queue",
                      "merge_queue", "pending_queue", "rebuild_queue"):
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone():
                counts[table] = int(db.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0])
        counts["task_status"] = {
            str(row[0]): int(row[1])
            for row in db.execute("SELECT status,count(*) FROM tasks GROUP BY status ORDER BY status")
        }
        leases = []
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='supervisor_lanes'").fetchone():
            leases.extend(dict(row) for row in db.execute(
                "SELECT lane_id,task_id,case_id,state,generation,run_id,candidate_sha "
                "FROM supervisor_lanes WHERE state<>'idle' ORDER BY lane_id"
            ))
        leases.extend(dict(row) for row in db.execute(
            "SELECT id AS task_id,status,attempt,last_run AS run_id,base_sha,candidate_sha "
            "FROM tasks WHERE status IN ('preflight','coding','verifying','awaiting_review','approved') "
            "ORDER BY id"
        ))
        return {
            "settings": settings,
            "schema_version": int(db.execute("PRAGMA user_version").fetchone()[0]),
            "counts": counts,
            "active_leases": leases,
            "controls": {
                marker: (self.home / marker).is_file()
                for marker in ("STOP", "PAUSE", "PAUSED_QUOTA", "PAUSE_NORMAL", "PAUSE_RECOVERY")
            },
        }

    def export_checkpoint(self, destination: Path | None = None) -> dict:
        """Create an immutable, SQLite-API backup without changing canonical state."""
        root = (self.home / "checkpoints").resolve()
        if destination is None:
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            destination = root / f"checkpoint-{stamp}-{uuid.uuid4().hex[:12]}"
        else:
            destination = destination.expanduser()
            if not destination.is_absolute():
                destination = self.home / destination
            destination = destination.resolve(strict=False)
        try:
            destination.relative_to(self.home.resolve())
        except ValueError as exc:
            raise ValueError("checkpoint destination outside state directory") from exc
        if destination.exists() or destination.is_symlink():
            raise ValueError("checkpoint destination already exists")
        destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(destination.parent, 0o700)
        destination.mkdir(mode=0o700)
        database_path = destination / "sda.sqlite3"
        temporary = destination / f".sda.sqlite3.{uuid.uuid4().hex}.tmp"
        try:
            with self.master_lock(blocking=True):
                with sqlite3.connect(self.database) as source:
                    source.row_factory = sqlite3.Row
                    source.execute("PRAGMA busy_timeout=20000")
                    if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("canonical database integrity check failed")
                    snapshot = self._checkpoint_snapshot(source)
                    snapshot["state_digest"] = _database_state_digest(source)
                    with sqlite3.connect(temporary) as target:
                        source.backup(target)
                        if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                            raise ValueError("checkpoint backup integrity check failed")
                        if _database_state_digest(target) != snapshot["state_digest"]:
                            raise ValueError("checkpoint state digest mismatch")
                    os.chmod(temporary, 0o600)
                    os.replace(temporary, database_path)
            manifest = {
                "format": "astra-one-state-checkpoint-v1",
                "created_at": now(),
                "database_file": database_path.name,
                "database_sha256": file_sha256(database_path),
                "snapshot": snapshot,
            }
            body = _canonical_json(manifest)
            manifest["manifest_sha256"] = hashlib.sha256(body).hexdigest()
            manifest_path = destination / "manifest.json"
            temporary_manifest = destination / f".manifest.{uuid.uuid4().hex}.tmp"
            temporary_manifest.write_bytes(_canonical_json(manifest))
            os.chmod(temporary_manifest, 0o600)
            os.replace(temporary_manifest, manifest_path)
            return {
                "checkpoint": str(destination),
                "manifest": str(manifest_path),
                "database": str(database_path),
                "database_sha256": manifest["database_sha256"],
                "state_digest": snapshot["state_digest"],
                "integrity": "ok",
                "controls_preserved": True,
            }
        finally:
            temporary.unlink(missing_ok=True)

    def _read_checkpoint(self, checkpoint: Path) -> tuple[Path, dict]:
        checkpoint = checkpoint.expanduser().resolve(strict=True)
        try:
            checkpoint.relative_to((self.home / "checkpoints").resolve())
        except ValueError as exc:
            raise ValueError("checkpoint is outside state checkpoints") from exc
        if not checkpoint.is_dir() or checkpoint.is_symlink():
            raise ValueError("checkpoint directory is unsafe")
        manifest_path = checkpoint / "manifest.json"
        if manifest_path.is_symlink() or not manifest_path.is_file():
            raise ValueError("checkpoint manifest unavailable")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("checkpoint manifest invalid") from exc
        if not isinstance(manifest, dict) or manifest.get("format") != "astra-one-state-checkpoint-v1":
            raise ValueError("checkpoint format invalid")
        provided = manifest.pop("manifest_sha256", "")
        if not isinstance(provided, str) or hashlib.sha256(_canonical_json(manifest)).hexdigest() != provided:
            raise ValueError("checkpoint manifest digest mismatch")
        database_name = manifest.get("database_file")
        if database_name != "sda.sqlite3":
            raise ValueError("checkpoint database path invalid")
        snapshot = manifest.get("snapshot")
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get("state_digest"), str):
            raise ValueError("checkpoint snapshot invalid")
        database_path = checkpoint / database_name
        if database_path.is_symlink() or not database_path.is_file():
            raise ValueError("checkpoint database unavailable")
        if file_sha256(database_path) != manifest.get("database_sha256"):
            raise ValueError("checkpoint database digest mismatch")
        with sqlite3.connect(database_path) as source:
            if source.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("checkpoint database integrity check failed")
            expected = snapshot["state_digest"]
            if not isinstance(expected, str) or _database_state_digest(source) != expected:
                raise ValueError("checkpoint state digest mismatch")
        return database_path, {**manifest, "manifest_sha256": provided}

    def restore_checkpoint(self, checkpoint: Path, destination: Path) -> dict:
        """Restore only to a new disposable DB; never overwrite canonical state."""
        destination = destination.expanduser()
        if not destination.is_absolute():
            destination = self.home / destination
        destination = destination.resolve(strict=False)
        try:
            destination.relative_to(self.home.resolve())
        except ValueError as exc:
            raise ValueError("restore destination outside state directory") from exc
        if destination == self.database.resolve() or destination.exists() or destination.is_symlink():
            raise ValueError("restore destination must be new and non-canonical")
        destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(destination.parent, 0o700)
        source_path, manifest = self._read_checkpoint(checkpoint)
        temporary = destination.parent / f".{destination.name}.{uuid.uuid4().hex}.tmp"
        try:
            with self.master_lock(blocking=True):
                with sqlite3.connect(source_path) as source, sqlite3.connect(temporary) as target:
                    source.backup(target)
                    if target.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("restored database integrity check failed")
                    expected = manifest["snapshot"]["state_digest"]
                    restored_digest = _database_state_digest(target)
                    if restored_digest != expected:
                        raise ValueError("restored database state digest mismatch")
                os.chmod(temporary, 0o600)
                os.replace(temporary, destination)
            return {
                "restored": str(destination),
                "checkpoint": str(Path(checkpoint).expanduser().resolve()),
                "database_sha256": file_sha256(destination),
                "state_digest": manifest["snapshot"]["state_digest"],
                "integrity": "ok",
                "canonical_unchanged": True,
                "controls_not_modified": True,
            }
        finally:
            temporary.unlink(missing_ok=True)

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
            next_enqueue = db.execute("SELECT COALESCE(MAX(enqueue_seq), 0) FROM tasks").fetchone()[0]
            inserted=set()
            for t in tasks:
                if t["task_id"] in existing or t["task_id"] in inserted:
                    raise ValueError("duplicate task ID")
                if any(dep not in existing and dep not in inserted for dep in t["depends_on"]):
                    raise ValueError("task dependencies must already exist or precede task")
                next_enqueue += 1
                db.execute("INSERT INTO tasks(id,spec,status,architecture_sha,created_at,updated_at,enqueue_seq) VALUES(?,?,?,?,?,?,?)",
                           (t["task_id"],json.dumps(t,ensure_ascii=False),"queued",self.get("architecture_sha"),now(),now(),next_enqueue))
                inserted.add(t["task_id"])
            db.execute("COMMIT")
        return [t["task_id"] for t in tasks]

    @staticmethod
    def _refresh_project_queues_db(db: sqlite3.Connection, project_id: str) -> None:
        """Reconcile dependency-ready parents into the canonical pending queue."""
        rows = db.execute(
            "SELECT * FROM tasks WHERE project_id=? ORDER BY enqueue_seq,id", (project_id,)
        ).fetchall()
        by_id = {row["id"]: row for row in rows}
        external_blockers = {
            row[0] for row in db.execute(
                "SELECT parent_id FROM supervisor_cases WHERE state='external_blocker'"
            )
        }
        active = {"preflight", "coding", "verifying", "awaiting_review", "approved"}
        terminal = {"completed", "archived"}
        for row in rows:
            current = row["status"]
            if current in active or current in terminal or current == "failed":
                continue
            spec = json.loads(row["spec"])
            dependencies = spec.get("depends_on", [])
            dependency_statuses = [by_id.get(dep, {"status": "blocked"})["status"] for dep in dependencies]
            if row["id"] in external_blockers:
                # An explicit external blocker is a durable fence.  It must
                # win over dependency readiness so a stale pending row cannot
                # silently hand the task back to a coding worker.
                desired = "blocked"
            elif any(status in {"failed", "blocked", "stopped", "interrupted"} for status in dependency_statuses):
                desired = "blocked"
            elif row["owner_gate"]:
                desired = "approval_required"
            elif all(status == "completed" for status in dependency_statuses):
                desired = "pending"
            else:
                desired = "waiting"
            if current != desired:
                db.execute("UPDATE tasks SET status=?,updated_at=? WHERE id=?", (desired, now(), row["id"]))
            if desired == "pending":
                db.execute(
                    "INSERT INTO pending_queue(parent_id,project_id,enqueue_seq,available_at,created_at) "
                    "VALUES(?,?,?,?,?) ON CONFLICT(parent_id) DO UPDATE SET available_at=excluded.available_at",
                    (row["id"], project_id, row["enqueue_seq"], 0, now()),
                )
                child_rows = db.execute(
                    "SELECT id,sequence,spec,status FROM subtasks WHERE parent_id=? ORDER BY sequence",
                    (row["id"],),
                ).fetchall()
                first_incomplete = next((child for child in child_rows
                                         if child["status"] not in {"completed", "archived"}), None)
                if first_incomplete and first_incomplete["status"] not in {"running", "pending"}:
                    child_spec = json.loads(first_incomplete["spec"])
                    child_statuses = {child["id"]: child["status"] for child in child_rows}
                    if all(child_statuses.get(dep) == "completed"
                           for dep in child_spec.get("depends_on", [])):
                        db.execute("UPDATE subtasks SET status='pending',updated_at=? WHERE id=?",
                                   (now(), first_incomplete["id"]))
            else:
                db.execute("DELETE FROM pending_queue WHERE parent_id=?", (row["id"],))

    def import_full_plan(self, plan: FullPlan) -> dict:
        """Idempotently import the reviewed 247-parent/1,359-child plan."""
        self.ensure_approved()
        self.ensure_full_plan_schema()
        project = plan.project
        project_payload = payload_sha({"project": project, "validation": plan.validation})
        inserted_parents = 0
        inserted_children = 0
        with self.master_lock():
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                existing_project = db.execute(
                    "SELECT payload_sha FROM projects WHERE id=?", (PROJECT_ID,)
                ).fetchone()
                if existing_project and existing_project[0] != project_payload:
                    db.execute("ROLLBACK")
                    raise ValueError("full-build project exists with a conflicting payload; reconciliation required")
                timestamp = now()
                if not existing_project:
                    db.execute(
                        "INSERT INTO projects(id,name,source_repository,integration_branch,parent_task_count,"
                        "subtask_count,workers,model,reasoning,source_ref,source_commit,parent_plan_blob_sha,"
                        "subtask_index_sha,payload_sha,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (PROJECT_ID, project["project_name"], project["source_repository"],
                         project["integration_branch"], project["parent_task_count"], project["subtask_count"],
                         project["workers"], project["model"], project["reasoning"], project["source_ref"],
                         project["source_commit"], project["parent_plan_blob_sha"], project["subtask_index_sha256"],
                         project_payload, "pending", timestamp, timestamp),
                    )
                    db.execute(
                        "INSERT INTO project_queue(project_id,status,enqueue_seq,created_at,updated_at) VALUES(?,?,?,?,?)",
                        (PROJECT_ID, "pending", 0, timestamp, timestamp),
                    )
                else:
                    db.execute("UPDATE projects SET updated_at=? WHERE id=?", (timestamp, PROJECT_ID))

                architecture_sha = db.execute(
                    "SELECT value FROM settings WHERE key='approved_architecture_sha'"
                ).fetchone()[0]
                for enqueue_seq, parent in enumerate(plan.parents, start=1):
                    pid = parent["task_id"]
                    spec_json = json.dumps(parent["spec"], ensure_ascii=False, sort_keys=True)
                    existing = db.execute(
                        "SELECT project_id,payload_sha FROM tasks WHERE id=?", (pid,)
                    ).fetchone()
                    if existing:
                        if existing[0] != PROJECT_ID or existing[1] != parent["payload_sha"]:
                            db.execute("ROLLBACK")
                            raise ValueError(f"parent task {pid} conflicts with existing history")
                    else:
                        owner_gate = int(parent["owner_gate"])
                        initial = "approval_required" if owner_gate else (
                            "waiting" if parent["dependencies"] else "pending"
                        )
                        db.execute(
                            "INSERT INTO tasks(id,spec,status,architecture_sha,available_at,created_at,updated_at,"
                            "project_id,module,milestone,priority,owner_gate,payload_sha,enqueue_seq) "
                            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (pid, spec_json, initial, architecture_sha, 0, timestamp, timestamp, PROJECT_ID,
                             parent["module"], parent["milestone"], parent["priority"], owner_gate,
                             parent["payload_sha"], enqueue_seq),
                        )
                        inserted_parents += 1
                    for child in parent["children"]:
                        child_id = child["id"]
                        child_json = json.dumps(child, ensure_ascii=False, sort_keys=True)
                        child_hash = payload_sha(child)
                        child_existing = db.execute(
                            "SELECT project_id,parent_id,payload_sha FROM subtasks WHERE id=?", (child_id,)
                        ).fetchone()
                        if child_existing:
                            if (child_existing[0], child_existing[1], child_existing[2]) != (
                                PROJECT_ID, pid, child_hash
                            ):
                                db.execute("ROLLBACK")
                                raise ValueError(f"child task {child_id} conflicts with existing history")
                            continue
                        parent_row = db.execute("SELECT status FROM tasks WHERE id=?", (pid,)).fetchone()
                        child_status = "pending" if parent_row[0] == "pending" and child["sequence"] == 1 else "waiting"
                        db.execute(
                            "INSERT INTO subtasks(id,project_id,parent_id,sequence,spec,status,payload_sha,created_at,updated_at) "
                            "VALUES(?,?,?,?,?,?,?,?,?)",
                            (child_id, PROJECT_ID, pid, child["sequence"], child_json, child_status,
                             child_hash, timestamp, timestamp),
                        )
                        inserted_children += 1
                self._refresh_project_queues_db(db, PROJECT_ID)
                db.execute("UPDATE projects SET updated_at=? WHERE id=?", (now(), PROJECT_ID))
                db.execute("COMMIT")
        return self.full_plan_status() | {
            "project_id": PROJECT_ID,
            "idempotent": inserted_parents == 0 and inserted_children == 0,
            "inserted_parents": inserted_parents,
            "inserted_children": inserted_children,
            "source_ref": project["source_ref"],
            "source_commit": project["source_commit"],
            "parent_plan_blob_sha": project["parent_plan_blob_sha"],
            "subtask_index_sha256": project["subtask_index_sha256"],
        }

    def _owner_binding(self, row: sqlite3.Row, db: sqlite3.Connection) -> dict:
        """Build the exact receipt fields from live state and immutable files."""
        tid = row["id"]
        spec = json.loads(row["spec"])
        if tid != "BASE-008":
            return {
                "task_id": tid,
                "decision": "APPROVE",
                "scope": str(spec.get("objective") or spec.get("title") or tid),
                "evidence": {
                    "architecture_sha256": row["architecture_sha"],
                    "parent_payload_sha256": row["payload_sha"],
                },
                "packet_sha256": "",
                "full_architecture_sha256": "",
                "bounded_focus_sha256": row["architecture_sha"],
                "parent_payload_sha256": row["payload_sha"],
                "source_sha": self.get("source_sha"),
                "integration_sha": self.get("integration_sha"),
            }
        packet = self.home / "reports" / "BASE-008_OWNER_DECISION_PACKET.md"
        packet_digest = self.home / "reports" / "BASE-008_OWNER_DECISION_PACKET.sha256"
        source_value = self.get("source")
        source = Path(source_value).expanduser().resolve()
        architecture = source / "docs" / "architecture" / "JARVIS_V2_CONSOLIDATED.md"
        focus_sha = self.get("architecture_sha")
        approved_focus_sha = self.get("approved_architecture_sha")
        if not packet.is_file() or not packet_digest.is_file() or not architecture.is_file():
            raise ValueError("BASE-008 approval evidence file is missing")
        actual_packet_sha = file_sha256(packet)
        declared_packet_sha = packet_digest.read_text(encoding="utf-8").split()[0]
        if declared_packet_sha != actual_packet_sha:
            raise ValueError("BASE-008 owner packet digest mismatch")
        packet_text = packet.read_text(encoding="utf-8")
        full_architecture_sha = file_sha256(architecture)
        if not SHA256.fullmatch(focus_sha) or focus_sha != approved_focus_sha:
            raise ValueError("BASE-008 bounded architecture is not approved consistently")
        if not SHA256.fullmatch(full_architecture_sha):
            raise ValueError("BASE-008 full architecture digest is invalid")
        parent_payload_sha = row["payload_sha"]
        if not SHA256.fullmatch(parent_payload_sha):
            raise ValueError("BASE-008 parent payload digest is invalid")
        source_sha = self.get("source_sha")
        integration_sha = self.get("integration_sha")
        if not SHA.fullmatch(source_sha) or not SHA.fullmatch(integration_sha):
            raise ValueError("BASE-008 source or integration checkpoint is invalid")
        packet_values = {
            "Full architecture SHA-256": full_architecture_sha,
            "Approved bounded focus SHA-256": focus_sha,
            "Parent task payload SHA": parent_payload_sha,
            "Live source SHA": source_sha,
            "Live integration SHA": integration_sha,
        }
        for label, value in packet_values.items():
            if f"| {label} | `{value}` |" not in packet_text:
                raise ValueError(f"BASE-008 packet binding mismatch: {label}")
        return {
            "task_id": tid,
            "decision": "APPROVE",
            "scope": "ten active modules; Business excluded/archived; no release/deployment/cutover",
            "evidence": {
                "packet_sha256": actual_packet_sha,
                "full_architecture_sha256": full_architecture_sha,
                "bounded_focus_sha256": focus_sha,
                "parent_payload_sha256": parent_payload_sha,
                "source_sha": source_sha,
                "integration_sha": integration_sha,
            },
            "packet_sha256": actual_packet_sha,
            "full_architecture_sha256": full_architecture_sha,
            "bounded_focus_sha256": focus_sha,
            "parent_payload_sha256": parent_payload_sha,
            "source_sha": source_sha,
            "integration_sha": integration_sha,
        }

    def owner_approval_request(self, tid: str, owner_identity: str,
                               *, allowed_signers: Path | None = None,
                               output: Path | None = None) -> dict:
        """Prepare, but never approve, a digest-bound owner signing request."""
        self.ensure_full_plan_schema()
        with self.db() as db:
            row = db.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
            if not row or row["project_id"] != PROJECT_ID or not row["owner_gate"]:
                raise ValueError("task is not an imported owner-gated parent")
            if row["status"] != "approval_required":
                raise ValueError("owner-gated task is not awaiting approval")
            spec = json.loads(row["spec"])
            statuses = [db.execute("SELECT status FROM tasks WHERE id=?", (dep,)).fetchone()[0]
                        for dep in spec.get("depends_on", [])]
            if any(status != "completed" for status in statuses):
                raise ValueError("owner-gated task dependencies are not complete")
            binding = self._owner_binding(row, db)
        allowed = (allowed_signers or (self.home / "owner" / "allowed_signers")).expanduser()
        if not allowed.is_absolute():
            allowed = allowed.absolute()
        receipt = (output or (self.home / "private" / "owner-approvals" / tid / f"{tid}.json")).expanduser()
        payload = dict(binding)
        payload["owner_identity"] = owner_identity
        payload["decided_at_utc"] = now().replace("+00:00", "Z")
        result = prepare_receipt(
            payload, receipt_path=receipt, allowed_signers=allowed,
            message_file=f"{tid}.message", signature_file=f"{tid}.message.sig",
            trusted_root=self.home,
        )
        return {"prepared": True, "task_id": tid, "payload": payload,
                "receipt": result["receipt"], "message": result["message"],
                "allowed_signers": str(allowed),
                "allowed_signers_sha256": result["allowed_signers_sha256"],
                "sign_command": f"ssh-keygen -Y sign -f <OWNER_PRIVATE_KEY> -n archon-owner-approval-v1 {result['message']}"}

    def _record_base008_owner_children(self, db: sqlite3.Connection, row: sqlite3.Row,
                                       receipt_sha: str, verified: dict, timestamp: str) -> list[str]:
        binding = verified["payload"]
        evidence = {
            "BASE-008.S01": (
                f"Packet {binding['packet_sha256']} and full architecture {binding['full_architecture_sha256']} "
                f"are bound to focus {binding['bounded_focus_sha256']}."),
            "BASE-008.S02": (
                "BASE-001 dependency is completed; packet/focus/architecture digests match live state; "
                "the deterministic DB checkpoint and existing rollback evidence remain intact."),
            "BASE-008.S03": (
                f"Signed APPROVE receipt verified for owner principal {verified['principal']} "
                f"at {binding['decided_at_utc']}; scope excludes Business and release/cutover."),
        }
        child_ids = [row[0] for row in db.execute(
            "SELECT id FROM subtasks WHERE parent_id=? ORDER BY sequence", (row["id"],)
        )]
        if child_ids != ["BASE-008.S01", "BASE-008.S02", "BASE-008.S03"]:
            raise ValueError("BASE-008 child packet differs from the approved three-step contract")
        recorded = []
        for cid in child_ids:
            item = {"subtask_id": cid, "status": "PASS", "evidence": evidence[cid]}
            evidence_sha = hashlib.sha256(_canonical_json(item)).hexdigest()
            receipt_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO owner_subtask_receipts(receipt_id,subtask_id,parent_id,generation,"
                "owner_receipt_sha256,evidence_sha256,verifier,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (receipt_id, cid, row["id"], row["attempt"], receipt_sha, evidence_sha,
                 "deterministic_master", timestamp),
            )
            db.execute(
                "UPDATE subtasks SET status='completed',evidence=?,updated_at=? WHERE id=?",
                (json.dumps({"receipt_id": receipt_id, "owner_receipt_sha256": receipt_sha,
                             "evidence_sha256": evidence_sha}, separators=(",", ":")), timestamp, cid),
            )
            recorded.append(receipt_id)
        return recorded

    def approve_owner(self, tid: str, *, owner_receipt: Path | None = None) -> dict:
        """Verify a signed owner receipt, then transact the owner-gate release."""
        self.ensure_full_plan_schema()
        with self.master_lock():
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
                if not row or row["project_id"] != PROJECT_ID or not row["owner_gate"]:
                    db.execute("ROLLBACK")
                    raise ValueError("task is not an imported owner-gated parent")
                if row["status"] != "approval_required":
                    db.execute("ROLLBACK")
                    raise ValueError("owner-gated task is not awaiting approval")
                spec = json.loads(row["spec"])
                statuses = [db.execute("SELECT status FROM tasks WHERE id=?", (dep,)).fetchone()[0]
                            for dep in spec.get("depends_on", [])]
                if any(status != "completed" for status in statuses):
                    db.execute("ROLLBACK")
                    raise ValueError("owner-gated task dependencies are not complete")
                if owner_receipt is None:
                    db.execute("ROLLBACK")
                    raise ValueError("authenticated owner receipt is required")
                receipt_path = owner_receipt.expanduser()
                if not receipt_path.is_absolute():
                    receipt_path = receipt_path.absolute()
                receipt_root = (self.home / "private" / "owner-approvals").resolve()
                try:
                    receipt_path.resolve().relative_to(receipt_root)
                except ValueError as exc:
                    db.execute("ROLLBACK")
                    raise ValueError("owner receipt must be inside private/owner-approvals") from exc
                binding = self._owner_binding(row, db)
                try:
                    verified = verify_receipt(
                        receipt_path,
                        allowed_signers=(self.home / "owner" / "allowed_signers"),
                        expected=binding,
                        trusted_root=self.home,
                    )
                except (OSError, OwnerApprovalError, subprocess.SubprocessError) as exc:
                    db.execute("ROLLBACK")
                    raise ValueError(f"owner receipt rejected: {exc}") from exc
                receipt_sha = file_sha256(receipt_path)
                payload = verified["payload"]
                timestamp = now()
                db.execute(
                    "INSERT INTO owner_approval_receipts(receipt_id,task_id,decision,packet_sha256,"
                    "full_architecture_sha256,bounded_focus_sha256,parent_payload_sha256,source_sha,"
                    "integration_sha,owner_identity,receipt_path,receipt_sha256,allowed_signers_sha256,"
                    "signature_algorithm,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (str(uuid.uuid4()), tid, payload["decision"], payload.get("packet_sha256", ""),
                     payload.get("full_architecture_sha256", ""), payload["bounded_focus_sha256"],
                     payload["parent_payload_sha256"], payload["source_sha"], payload["integration_sha"],
                     verified["principal"], str(receipt_path), receipt_sha,
                     verified["allowed_signers_sha256"], verified["signature_algorithm"], timestamp),
                )
                if tid == "BASE-008":
                    child_receipts = self._record_base008_owner_children(
                        db, row, receipt_sha, verified, timestamp)
                    db.execute(
                        "UPDATE tasks SET status='completed',qc_evidence=?,updated_at=? WHERE id=?",
                        (json.dumps({"owner_receipt_sha256": receipt_sha,
                                     "owner_identity": verified["principal"],
                                     "child_receipts": child_receipts}, separators=(",", ":")),
                         timestamp, tid),
                    )
                    for queue in ("pending_queue", "rebuild_queue", "review_queue", "merge_queue"):
                        db.execute(f"DELETE FROM {queue} WHERE parent_id=?", (tid,))
                    self._refresh_project_queues_db(db, PROJECT_ID)
                    db.execute("COMMIT")
                    return {"approved": tid, "status": "completed", "owner_receipt_sha256": receipt_sha,
                            "child_receipts": child_receipts, "owner_identity": verified["principal"]}
                db.execute("UPDATE tasks SET status='pending',updated_at=? WHERE id=?", (timestamp, tid))
                db.execute(
                    "INSERT INTO pending_queue(parent_id,project_id,enqueue_seq,available_at,created_at) "
                    "VALUES(?,?,?,?,?) ON CONFLICT(parent_id) DO UPDATE SET available_at=excluded.available_at",
                    (tid, PROJECT_ID, row["enqueue_seq"], 0, timestamp),
                )
                db.execute("COMMIT")
        return {"approved": tid, "status": "pending", "owner_approval_required": True}

    def full_plan_status(self) -> dict:
        with self.db() as db:
            if int(db.execute("PRAGMA user_version").fetchone()[0]) < SCHEMA_VERSION:
                return {"imported": False, "schema_ready": False,
                        "queues": {name: 0 for name in QUEUE_NAMES}}
            project = db.execute("SELECT * FROM projects WHERE id=?", (PROJECT_ID,)).fetchone()
            if not project:
                return {"imported": False, "schema_ready": True,
                        "queues": {name: 0 for name in QUEUE_NAMES}}
            task_counts = {row[0]: row[1] for row in db.execute(
                "SELECT status,count(*) FROM tasks WHERE project_id=? GROUP BY status", (PROJECT_ID,)
            )}
            child_counts = {row[0]: row[1] for row in db.execute(
                "SELECT status,count(*) FROM subtasks WHERE project_id=? GROUP BY status", (PROJECT_ID,)
            )}
            verified_receipts = db.execute(
                "SELECT count(*) FROM subtask_receipts WHERE parent_id IN "
                "(SELECT id FROM tasks WHERE project_id=?) AND verifier='independent_qc'",
                (PROJECT_ID,),
            ).fetchone()[0]
            queues = {}
            for name in QUEUE_NAMES:
                queues[name] = db.execute(f"SELECT count(*) FROM {name} WHERE "
                                          f"{'project_id=?' if name != 'project_queue' else 'project_id=?'}",
                                          (PROJECT_ID,)).fetchone()[0]
            return {
                "imported": True,
                "schema_ready": True,
                "project_id": PROJECT_ID,
                "project_status": project["status"],
                "parent_count": project["parent_task_count"],
                "subtask_count": project["subtask_count"],
                "parent_status": task_counts,
                "child_status": child_counts,
                "verified_subtask_receipts": verified_receipts,
                "child_evidence_mode": "receipt_backed",
                "queues": queues,
                "payload_sha": project["payload_sha"],
            }

    def _task_markdown_records(self, db: sqlite3.Connection) -> tuple[dict, list[dict], dict[str, str]]:
        project_row = db.execute("SELECT * FROM projects WHERE id=?", (PROJECT_ID,)).fetchone()
        if not project_row:
            raise ValueError("full-build project is not imported")
        project = dict(project_row)
        project.update({"project_id": project["id"], "project_name": project["name"],
                        "subtask_index_sha256": project["subtask_index_sha"]})
        parents = []
        statuses = {}
        task_rows = db.execute(
            "SELECT id,spec,status,module,milestone,priority,owner_gate,payload_sha "
            "FROM tasks WHERE project_id=? ORDER BY enqueue_seq,id", (PROJECT_ID,)
        ).fetchall()
        for row in task_rows:
            spec = json.loads(row["spec"])
            child_rows = db.execute(
                "SELECT id,sequence,spec,payload_sha FROM subtasks WHERE parent_id=? ORDER BY sequence",
                (row["id"],),
            ).fetchall()
            children = []
            for child_row in child_rows:
                child = json.loads(child_row["spec"])
                child["id"] = child_row["id"]
                child["sequence"] = child_row["sequence"]
                child["payload_sha"] = child_row["payload_sha"]
                children.append(child)
            parents.append({
                "task_id": row["id"], "module": row["module"],
                "milestone": row["milestone"], "priority": row["priority"],
                "owner_gate": bool(row["owner_gate"]), "dependencies": list(spec.get("depends_on", [])),
                "spec": spec, "payload_sha": row["payload_sha"], "children": children,
            })
            statuses[row["id"]] = row["status"]
        return project, parents, statuses

    def export_task_markdown(self, output: Path | None = None) -> dict:
        """Export the current ledger as a validated, non-authoritative TASK.md view."""
        output = (output or (self.home / "reports" / "TASK.md")).expanduser().resolve()
        with self.db() as db:
            project, parents, statuses = self._task_markdown_records(db)
        text = render_task_markdown(project, parents, statuses=statuses,
                                    source_path=str(self.database))
        validation = validate_task_markdown(text, project, parents)
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(text, encoding="utf-8")
            os.chmod(temporary, 0o600)
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
        return {
            **validation,
            "path": str(output),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "bytes": len(text.encode("utf-8")),
            "authoritative": "sqlite",
        }

    def validate_task_markdown_file(self, source: Path) -> dict:
        source = source.expanduser().resolve()
        try:
            raw = source.read_bytes()
        except OSError as exc:
            raise ValueError("cannot read TASK.md") from exc
        if len(raw) > 5_000_000:
            raise ValueError("TASK.md exceeds the size limit")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("TASK.md is not UTF-8") from exc
        with self.db() as db:
            project, parents, _ = self._task_markdown_records(db)
        result = validate_task_markdown(text, project, parents)
        return {**result, "path": str(source),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw), "authoritative": "sqlite"}

    def list_tasks(self) -> list[dict]:
        with self.db() as db:
            return [dict(r) for r in db.execute(
                "SELECT id,status,attempt,project_id,module,priority,owner_gate,branch,base_sha,"
                "candidate_sha,worktree,last_error,updated_at FROM tasks ORDER BY created_at,id"
            )]

    def claim(self, model: str = MODEL, *, batch_id: str | None = None, lane: str = "normal") -> dict | None:
        self.ensure_approved()
        if control_blocked(self.home, lane):
            return None
        if batch_id is not None and not re.fullmatch(r"[A-Z0-9_.-]{3,80}", batch_id):
            raise ValueError("invalid batch id")
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            approved_architecture = db.execute(
                "SELECT value FROM settings WHERE key='approved_architecture_sha'"
            ).fetchone()[0]
            query = (
                "SELECT * FROM tasks WHERE status IN ('queued','pending') AND architecture_sha=? "
                "AND available_at<=?"
            )
            query_params: list[object] = [approved_architecture, int(time.time())]
            if batch_id is not None:
                query += (
                    " AND id IN (SELECT parent_id FROM batch_members "
                    "WHERE batch_id=? AND state IN ('admitted','running'))"
                )
                query_params.append(batch_id)
            else:
                # An active fixed cohort is authoritative. The ordinary
                # full-queue runner cannot consume its members behind the
                # cohort controller's back.
                query += (
                    " AND NOT EXISTS (SELECT 1 FROM batch_members bm "
                    "JOIN batch_epochs be ON be.batch_id=bm.batch_id "
                    "WHERE bm.parent_id=tasks.id AND be.state IN ('running','draining'))"
                )
            # A recovery lease owns the failed generation. Normal dispatch must
            # not claim the same parent while R1/R2 is repairing it. Keep
            # direct legacy callers compatible until the additive migration is
            # applied.
            if db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='supervisor_lanes'"
            ).fetchone():
                query += (
                    " AND NOT EXISTS (SELECT 1 FROM supervisor_lanes sl "
                    "WHERE sl.task_id=tasks.id AND sl.state<>'idle')"
                )
            query += (
                " ORDER BY CASE priority WHEN 'P0' THEN 0 WHEN 'P1' THEN 1 "
                "WHEN 'P2' THEN 2 WHEN 'P3' THEN 3 WHEN 'P4' THEN 4 ELSE 5 END, "
                "enqueue_seq,created_at,id"
            )
            rows=db.execute(query, tuple(query_params)).fetchall()
            for row in rows:
                t=json.loads(row["spec"])
                try:
                    validate_task_type(t)
                except ValueError:
                    # Do not assign malformed packets. Make the defect visible
                    # to Supervisor triage and continue with unrelated work.
                    db.execute(
                        "UPDATE tasks SET status='failed',last_error='task_type_invalid',updated_at=? WHERE id=?",
                        (now(), row["id"]),
                    )
                    db.execute("DELETE FROM pending_queue WHERE parent_id=?", (row["id"],))
                    db.execute("DELETE FROM rebuild_queue WHERE parent_id=?", (row["id"],))
                    continue
                deps=t["depends_on"]
                if any((found:=db.execute("SELECT status FROM tasks WHERE id=?",(d,)).fetchone()) is None or found[0] != "completed" for d in deps):
                    continue
                if row["owner_gate"]:
                    continue
                if row["project_id"]:
                    t["subtasks"] = [json.loads(child["spec"]) for child in db.execute(
                        "SELECT spec FROM subtasks WHERE parent_id=? ORDER BY sequence", (row["id"],)
                    )]
                attempt=row["attempt"]+1
                rid=str(uuid.uuid4())
                role="worker" if attempt==1 else "repairer"
                db.execute("""UPDATE tasks SET status='preflight',attempt=?,last_run=?,last_error='',
                           candidate_sha='',integrated_sha='',changed_files='[]',qc_evidence='',base_sha='',branch='',worktree='',updated_at=?
                           WHERE id=?""",(attempt,rid,now(),t["task_id"]))
                db.execute("DELETE FROM pending_queue WHERE parent_id=?", (t["task_id"],))
                db.execute("DELETE FROM rebuild_queue WHERE parent_id=?", (t["task_id"],))
                if row["project_id"]:
                    # A new candidate generation must earn a fresh receipt for
                    # every child; prior receipts remain historical evidence.
                    db.execute(
                        "UPDATE subtasks SET status='waiting',evidence='',updated_at=? WHERE parent_id=?",
                        (now(), t["task_id"]),
                    )
                    db.execute(
                        "UPDATE subtasks SET status='running',updated_at=? WHERE parent_id=? "
                        "AND sequence=(SELECT MIN(sequence) FROM subtasks WHERE parent_id=?)",
                        (now(), t["task_id"], t["task_id"]),
                    )
                db.execute("INSERT INTO runs(id,task_id,attempt,role,status,started_at,model) VALUES (?,?,?,?,?,?,?)",
                           (rid,t["task_id"],attempt,role,"preflight",now(),model))
                if batch_id is not None:
                    db.execute(
                        "UPDATE batch_members SET state='running',updated_at=? WHERE batch_id=? AND parent_id=?",
                        (now(), batch_id, t["task_id"]),
                    )
                db.execute("COMMIT")
                return {"task":t,"run_id":rid,"attempt":attempt,"role":role,"prior_error":row["last_error"]}
            db.execute("COMMIT")
        return None

    def builder_claim(self, *, model: str = MODEL, batch_id: str | None = None) -> dict | None:
        """Claim and prepare one isolated worktree for the sole Main Codex builder."""
        self.ensure_full_plan_schema()
        with self.master_lock(blocking=True):
            item = self.claim(model=model, batch_id=batch_id, lane="normal")
            if not item:
                return None
        task = item["task"]
        run_id = item["run_id"]
        attempt = item["attempt"]
        source = Path(self.get("source"))
        branch = builder_branch(task, attempt, run_id)
        worktree = self.home / "worktrees" / (task["task_id"].lower() + "-" + run_id[:8])
        base_sha = self.get("integration_sha")
        try:
            assert_source(source)
            worktree.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            git(source, "worktree", "add", "-b", branch, str(worktree), base_sha)
            self.set_task(task["task_id"], "coding", fields={
                "base_sha": base_sha, "branch": branch, "worktree": str(worktree),
            }, run_id=run_id, attempt=attempt)
            self.emit(task["task_id"], run_id, stage="coding", step="builder_claimed",
                      branch=branch, base_sha=base_sha, attempt=attempt)
        except Exception as exc:
            try:
                self.set_task(task["task_id"], "failed", error="builder_preparation_failed",
                              run_id=run_id, attempt=attempt)
            except Exception:
                pass
            raise ValueError("builder_preparation_failed") from exc
        return {"task": task, "run_id": run_id, "attempt": attempt, "role": "main_builder",
                "base_sha": base_sha, "branch": branch, "worktree": str(worktree)}

    def submit_candidate(self, *, task_id: str, run_id: str, attempt: int,
                         builder_session_id: str, base_sha: str, candidate_sha: str,
                         branch: str, worktree: str, changed_files: list[str],
                         test_evidence: list, acceptance_evidence: list) -> dict:
        """Atomically hand a real Main Codex commit to the review queue."""
        if not TASK_ID.fullmatch(task_id) or not BUILDER_SESSION.fullmatch(builder_session_id):
            raise ValueError("invalid builder submission identity")
        if not re.fullmatch(r"[a-f0-9-]{20,80}", run_id) or attempt < 1:
            raise ValueError("invalid builder run identity")
        if not SHA.fullmatch(base_sha) or not SHA.fullmatch(candidate_sha):
            raise ValueError("invalid builder submission SHA")
        if not branch.startswith(("feature/", "feat/")) or len(branch) > 180:
            raise ValueError("invalid builder branch")
        if not isinstance(worktree, str) or len(worktree) > 500:
            raise ValueError("invalid builder worktree")
        if not isinstance(changed_files, list) or not 1 <= len(changed_files) <= 30:
            raise ValueError("invalid builder changed files")
        if any(not isinstance(path, str) or not path or len(path) > 250 for path in changed_files):
            raise ValueError("invalid builder changed files")
        test_json = _bounded_evidence(test_evidence, "test_evidence")
        acceptance_json = _bounded_evidence(acceptance_evidence, "acceptance_evidence")

        with self.db() as db:
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row or not row["project_id"]:
            raise ValueError("builder submission requires an imported project task")
        child_ids: list[str] = []
        if row["project_id"]:
            with self.db() as db:
                child_ids = [item[0] for item in db.execute(
                    "SELECT id FROM subtasks WHERE parent_id=? ORDER BY sequence", (task_id,)
                )]
        if child_ids:
            _validate_builder_child_evidence(child_ids, acceptance_evidence)
        if row["last_run"] != run_id or row["attempt"] != attempt:
            raise ValueError("stale_worker_lease")
        if row["status"] not in {"coding", "verifying"}:
            existing = None
            with self.db() as db:
                existing = db.execute(
                    "SELECT * FROM candidate_submissions WHERE task_id=? AND attempt=? AND candidate_sha=?",
                    (task_id, attempt, candidate_sha),
                ).fetchone()
            if existing:
                return {"submission_id": existing["submission_id"], "task_id": task_id,
                        "candidate_sha": candidate_sha, "status": existing["status"], "idempotent": True}
            raise ValueError("task is not owned by the Main Codex builder")
        if row["base_sha"] != base_sha or row["branch"] != branch or row["worktree"] != worktree:
            raise ValueError("builder checkpoint mismatch")

        candidate_path = Path(worktree).expanduser()
        worktrees = (self.home / "worktrees").resolve()
        if candidate_path.is_symlink() or not candidate_path.exists():
            raise ValueError("candidate worktree unavailable")
        candidate_path = candidate_path.resolve(strict=True)
        if candidate_path.parent != worktrees:
            raise ValueError("candidate worktree outside isolated worktrees")
        if git(candidate_path, "branch", "--show-current") != branch:
            raise ValueError("candidate branch mismatch")
        from .linux_runtime import check_candidate_changes
        task_packet = json.loads(row["spec"])
        if row["project_id"]:
            with self.db() as db:
                task_packet["subtasks"] = [json.loads(child["spec"]) for child in db.execute(
                    "SELECT spec FROM subtasks WHERE parent_id=? ORDER BY sequence", (task_id,)
                )]
        actual_files = check_candidate_changes(candidate_path, base_sha, candidate_sha, task=task_packet)
        if sorted(actual_files) != sorted(changed_files):
            raise ValueError("candidate changed-file manifest mismatch")
        changed_json = json.dumps(actual_files, separators=(",", ":"))

        with self.master_lock(blocking=True):
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                current = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
                if not current or current["last_run"] != run_id or current["attempt"] != attempt:
                    db.execute("ROLLBACK")
                    raise ValueError("stale_worker_lease")
                existing = db.execute(
                    "SELECT * FROM candidate_submissions WHERE task_id=? AND attempt=? AND candidate_sha=?",
                    (task_id, attempt, candidate_sha),
                ).fetchone()
                if existing:
                    db.execute("COMMIT")
                    return {"submission_id": existing["submission_id"], "task_id": task_id,
                            "candidate_sha": candidate_sha, "status": existing["status"], "idempotent": True}
                other = db.execute(
                    "SELECT 1 FROM candidate_submissions WHERE task_id=? AND attempt=? AND candidate_sha<>?",
                    (task_id, attempt, candidate_sha),
                ).fetchone()
                if other:
                    db.execute("ROLLBACK")
                    raise ValueError("candidate already submitted for this generation")
                submission_id = str(uuid.uuid4())
                timestamp = now()
                db.execute(
                    "INSERT INTO candidate_submissions(submission_id,task_id,run_id,attempt,builder_session_id,"
                    "base_sha,candidate_sha,branch,worktree,changed_files,test_evidence,acceptance_evidence,status,created_at,updated_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (submission_id, task_id, run_id, attempt, builder_session_id, base_sha, candidate_sha,
                     branch, str(candidate_path), changed_json, test_json, acceptance_json, "queued",
                     timestamp, timestamp),
                )
                db.execute(
                    "UPDATE tasks SET status='awaiting_review',candidate_sha=?,changed_files=?,qc_evidence=?,updated_at=? WHERE id=?",
                    (candidate_sha, changed_json, json.dumps({"submission_id": submission_id, "state": "queued"}),
                     timestamp, task_id),
                )
                db.execute(
                    "UPDATE runs SET status='awaiting_review',finished_at=? WHERE id=?",
                    (timestamp, run_id),
                )
                db.execute(
                    "INSERT INTO review_queue(parent_id,project_id,candidate_sha,created_at) VALUES(?,?,?,?) "
                    "ON CONFLICT(parent_id) DO UPDATE SET candidate_sha=excluded.candidate_sha,created_at=excluded.created_at",
                    (task_id, current["project_id"], candidate_sha, timestamp),
                )
                db.execute("COMMIT")
        return {"submission_id": submission_id, "task_id": task_id, "candidate_sha": candidate_sha,
                "status": "queued", "idempotent": False}

    def update_candidate_submission(self, submission_id: str, status: str, *,
                                    failure_code: str = "") -> None:
        """Record one bounded QC/Merger outcome without changing task history."""
        if not re.fullmatch(r"[a-f0-9-]{20,80}", submission_id):
            raise ValueError("invalid submission ID")
        if status not in {"queued", "qc_running", "passed", "rejected", "blocked", "merged", "merge_conflict"}:
            raise ValueError("invalid submission status")
        if len(failure_code) > 160 or (failure_code and not re.fullmatch(r"[A-Za-z0-9_:-]+", failure_code)):
            raise ValueError("invalid submission failure code")
        with self.master_lock(blocking=True):
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT submission_id FROM candidate_submissions WHERE submission_id=?",
                                 (submission_id,)).fetchone()
                if not row:
                    db.execute("ROLLBACK")
                    raise ValueError("unknown candidate submission")
                db.execute(
                    "UPDATE candidate_submissions SET status=?,failure_code=?,updated_at=? WHERE submission_id=?",
                    (status, failure_code, now(), submission_id),
                )
                db.execute("COMMIT")

    def claim_recovery_task(self, lease: dict, *, model: str = MODEL) -> dict:
        """Atomically transfer one failed generation to a leased recovery lane."""
        lane_id = str(lease.get("lane_id", ""))
        case_id = str(lease.get("case_id", ""))
        token = str(lease.get("lease_token", ""))
        if lane_id not in {"repair_1", "repair_2"} or not re.fullmatch(r"[a-f0-9]{24}", token):
            raise ValueError("invalid recovery lease")
        with self.master_lock(blocking=True):
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                if control_blocked(self.home, "recovery"):
                    db.execute("ROLLBACK")
                    raise ValueError("recovery_lane_paused")
                lane = db.execute(
                    "SELECT task_id,case_id,state,lease_token FROM supervisor_lanes WHERE lane_id=?", (lane_id,)
                ).fetchone()
                if (not lane or lane["case_id"] != case_id or lane["state"] != "leased"
                        or lane["lease_token"] != token):
                    db.execute("ROLLBACK")
                    raise ValueError("recovery lease mismatch")
                row = db.execute("SELECT * FROM tasks WHERE id=?", (lane["task_id"],)).fetchone()
                if not row or row["status"] not in {"failed", "conflict", "interrupted", "stopped"}:
                    db.execute("ROLLBACK")
                    raise ValueError("recovery task is not claimable")
                if row["attempt"] >= MAX_FAILURES:
                    db.execute("ROLLBACK")
                    raise ValueError("recovery retry ceiling reached")
                task = json.loads(row["spec"])
                validate_task_type(task)
                if row["project_id"]:
                    task["subtasks"] = [json.loads(child["spec"]) for child in db.execute(
                        "SELECT spec FROM subtasks WHERE parent_id=? ORDER BY sequence", (row["id"],)
                    )]
                attempt = row["attempt"] + 1
                run_id = str(uuid.uuid4())
                timestamp = now()
                db.execute(
                    "UPDATE tasks SET status='preflight',attempt=?,last_run=?,last_error='',candidate_sha='',integrated_sha='',"
                    "changed_files='[]',qc_evidence='',base_sha='',branch='',worktree='',updated_at=? WHERE id=?",
                    (attempt, run_id, timestamp, row["id"]),
                )
                if row["project_id"]:
                    db.execute("UPDATE subtasks SET status='waiting',evidence='',updated_at=? WHERE parent_id=?",
                               (timestamp, row["id"]))
                    db.execute(
                        "UPDATE subtasks SET status='running',updated_at=? WHERE parent_id=? "
                        "AND sequence=(SELECT MIN(sequence) FROM subtasks WHERE parent_id=?)",
                        (timestamp, row["id"], row["id"]),
                    )
                db.execute(
                    "INSERT INTO runs(id,task_id,attempt,role,status,started_at,model) VALUES (?,?,?,?,?,?,?)",
                    (run_id, row["id"], attempt, "recovery", "preflight", timestamp, model),
                )
                db.execute(
                    "UPDATE supervisor_lanes SET generation=?,run_id=?,candidate_sha='',updated_at=? "
                    "WHERE lane_id=? AND case_id=? AND lease_token=?",
                    (attempt, run_id, timestamp, lane_id, case_id, token),
                )
                db.execute("COMMIT")
                return {"task": task, "run_id": run_id, "attempt": attempt,
                        "role": "repairer", "prior_error": row["last_error"],
                        "recovery_lane": lane_id, "recovery_case": case_id, "recovery_token": token}

    def set_task(self, tid: str, status: str, *, error: str = "", fields: dict | None = None,
                 run_id: str | None = None, attempt: int | None = None):
        if status not in {"queued","waiting","blocked","approval_required","pending","running",
                          "paused_quota","preflight","coding","verifying","awaiting_review",
                          "approved","completed","failed","interrupted","conflict","stopped","archived"}:
            raise ValueError("unknown task state")
        params = {"status":status,"updated_at":now()}
        error_code = ""
        if error:
            error_code = error[:160]
            params["last_error"] = error_code
        run_tool_count = None
        if fields:
            fields = dict(fields)
            if "tool_count" in fields:
                run_tool_count = fields.pop("tool_count")
                if not isinstance(run_tool_count, int) or run_tool_count < 0:
                    raise ValueError("tool_count must be a non-negative integer")
            params.update(fields)
        columns=", ".join(f"{k}=?" for k in params)
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT last_run,attempt FROM tasks WHERE id=?", (tid,)).fetchone()
            if not current:
                db.execute("ROLLBACK")
                raise ValueError("unknown task")
            if run_id is not None and (current["last_run"] != run_id or
                                       (attempt is not None and current["attempt"] != attempt)):
                db.execute("ROLLBACK")
                raise ValueError("stale_worker_lease")
            db.execute(f"UPDATE tasks SET {columns} WHERE id=?",tuple(params.values())+(tid,))
            row = db.execute("SELECT * FROM tasks WHERE id=?", (tid,)).fetchone()
            terminal = int(status in {"awaiting_review","approved","completed","failed","interrupted","conflict","stopped","archived"})
            db.execute("""UPDATE runs SET status=?,
                       error_code=CASE WHEN ? <> '' THEN ? ELSE error_code END,
                       tool_count=COALESCE(?,tool_count),
                       finished_at=CASE WHEN ? THEN ? ELSE finished_at END
                       WHERE id=(SELECT last_run FROM tasks WHERE id=?)""",
                       (status,error_code,error_code,run_tool_count,terminal,now(),tid))
            if status == "failed":
                # Keep failed candidate identity after retry clears the live task
                # pointer; the worktree remains preserved for inspection.
                db.execute("""CREATE TABLE IF NOT EXISTS candidate_quarantine(
                    quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL REFERENCES tasks(id),
                    attempt INTEGER NOT NULL,
                    candidate_sha TEXT NOT NULL DEFAULT '',
                    branch TEXT NOT NULL DEFAULT '',
                    worktree TEXT NOT NULL DEFAULT '',
                    failure_code TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(task_id,attempt,candidate_sha,failure_code)
                )""")
                db.execute(
                    "INSERT INTO candidate_quarantine(task_id,attempt,candidate_sha,branch,worktree,failure_code,source,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?) "
                    "ON CONFLICT(task_id,attempt,candidate_sha,failure_code) DO UPDATE SET "
                    "branch=excluded.branch,worktree=excluded.worktree,source=excluded.source,created_at=excluded.created_at",
                    (tid, row["attempt"], row["candidate_sha"] or "", row["branch"] or "",
                     row["worktree"] or "", error_code or "failure_unclassified", "task_failure", now()),
                )
            if row and row["project_id"]:
                project_id = row["project_id"]
                if status == "completed":
                    child_count = db.execute(
                        "SELECT count(*) FROM subtasks WHERE parent_id=?", (tid,)
                    ).fetchone()[0]
                    receipt_count = 0
                    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='subtask_receipts'").fetchone():
                        receipt_count = db.execute(
                            "SELECT count(*) FROM subtask_receipts WHERE parent_id=? AND candidate_sha=? "
                            "AND verifier='independent_qc'",
                            (tid, row["candidate_sha"]),
                        ).fetchone()[0]
                    incomplete = db.execute(
                        "SELECT count(*) FROM subtasks WHERE parent_id=? "
                        "AND status NOT IN ('completed','archived')", (tid,)
                    ).fetchone()[0]
                    if child_count and (incomplete or receipt_count != child_count):
                        db.execute("ROLLBACK")
                        raise ValueError("subtask_evidence_incomplete")
                    for queue in ("pending_queue", "rebuild_queue", "review_queue", "merge_queue"):
                        db.execute(f"DELETE FROM {queue} WHERE parent_id=?", (tid,))
                    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='batch_members'").fetchone():
                        db.execute(
                            "UPDATE batch_members SET state='completed',updated_at=? WHERE parent_id=?",
                            (now(), tid),
                        )
                        db.execute(
                            "UPDATE batch_epochs SET completed_count=(SELECT count(*) FROM batch_members "
                            "WHERE batch_id=batch_epochs.batch_id AND state='completed'),updated_at=? "
                            "WHERE batch_id IN (SELECT batch_id FROM batch_members WHERE parent_id=?)",
                            (now(), tid),
                        )
                        db.execute(
                            "UPDATE batch_epochs SET state='drained',updated_at=? "
                            "WHERE admitted_count >= target_count AND completed_count >= target_count "
                            "AND batch_id IN (SELECT batch_id FROM batch_members WHERE parent_id=?)",
                            (now(), tid),
                        )
                    self._refresh_project_queues_db(db, project_id)
                elif status == "failed":
                    db.execute(
                        "UPDATE subtasks SET status='failed',updated_at=? WHERE parent_id=? AND status='running'",
                        (now(), tid),
                    )
                    for queue in ("review_queue", "merge_queue"):
                        db.execute(f"DELETE FROM {queue} WHERE parent_id=?", (tid,))
                    db.execute(
                        "INSERT INTO rebuild_queue(parent_id,project_id,generation,reason,created_at) VALUES(?,?,?,?,?) "
                        "ON CONFLICT(parent_id) DO UPDATE SET generation=excluded.generation,reason=excluded.reason,created_at=excluded.created_at",
                        (tid, project_id, row["attempt"], error_code[:160], now()),
                    )
                elif status == "awaiting_review":
                    db.execute(
                        "INSERT INTO review_queue(parent_id,project_id,candidate_sha,created_at) VALUES(?,?,?,?) "
                        "ON CONFLICT(parent_id) DO UPDATE SET candidate_sha=excluded.candidate_sha",
                        (tid, project_id, row["candidate_sha"], now()),
                    )
                elif status == "approved":
                    db.execute("DELETE FROM review_queue WHERE parent_id=?", (tid,))
                    db.execute(
                        "INSERT INTO merge_queue(parent_id,project_id,candidate_sha,created_at) VALUES(?,?,?,?) "
                        "ON CONFLICT(parent_id) DO UPDATE SET candidate_sha=excluded.candidate_sha",
                        (tid, project_id, row["candidate_sha"], now()),
                    )
                elif status in {"queued", "pending"}:
                    self._refresh_project_queues_db(db, project_id)
            db.execute("COMMIT")

    def record_codex_receipt(self, run_id: str, *, thread_id: str = "",
                             input_tokens: int = 0, output_tokens: int = 0,
                             tool_count: int = 0, tool_effects: list[dict] | None = None,
                             error_category: str = "") -> None:
        """Persist bounded JSONL metadata while excluding model payloads and commands."""
        if not re.fullmatch(r"[a-f0-9-]{20,80}", run_id):
            raise ValueError("invalid run ID")
        if not isinstance(thread_id, str) or len(thread_id) > 160 or not thread_id.isprintable():
            raise ValueError("invalid thread ID")
        if any(not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 1_000_000_000
               for value in (input_tokens, output_tokens, tool_count)):
            raise ValueError("invalid Codex usage")
        if not isinstance(error_category, str) or len(error_category) > 80 or (
                error_category and not re.fullmatch(r"[A-Za-z0-9_:-]+", error_category)):
            raise ValueError("invalid error category")
        safe_effects = []
        for effect in list(tool_effects or [])[:128]:
            if not isinstance(effect, dict):
                continue
            item = {}
            for key in ("type", "status", "error_category"):
                value = effect.get(key, "")
                if isinstance(value, str) and len(value) <= 80 and (not value or re.fullmatch(r"[A-Za-z0-9_.:-]+", value)):
                    if value:
                        item[key] = value
            exit_code = effect.get("exit_code")
            if isinstance(exit_code, int) and not isinstance(exit_code, bool) and 0 <= exit_code <= 255:
                item["exit_code"] = exit_code
            if item:
                safe_effects.append(item)
        effects_json = json.dumps(safe_effects, sort_keys=True, separators=(",", ":"))
        if len(effects_json) > 16_000:
            raise ValueError("Codex tool receipt exceeds bound")
        with self.master_lock(blocking=True):
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                if not db.execute("SELECT 1 FROM runs WHERE id=?", (run_id,)).fetchone():
                    db.execute("ROLLBACK")
                    raise ValueError("unknown run")
                db.execute(
                    "UPDATE runs SET thread_id=?,input_tokens=?,output_tokens=?,tool_count=?,"
                    "tool_effects=?,error_category=? WHERE id=?",
                    (thread_id, input_tokens, output_tokens, tool_count, effects_json, error_category, run_id),
                )
                db.execute("COMMIT")

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

    def subtask_contract_sha(self, tid: str) -> str:
        """Hash the exact persisted child packet used for independent QC."""
        with self.db() as db:
            children = []
            for child in db.execute(
                "SELECT id,sequence,spec,payload_sha FROM subtasks WHERE parent_id=? ORDER BY sequence", (tid,)
            ):
                children.append({"id": child["id"], "sequence": child["sequence"],
                                 "spec": json.loads(child["spec"]), "payload_sha": child["payload_sha"]})
        if not children:
            raise ValueError("task has no imported subtasks")
        return payload_sha({"parent_id": tid, "children": children})

    def _read_receipt_artifact(self, receipt: dict, *, kind: str, task_id: str,
                               run_id: str, attempt: int, source_sha: str,
                               payload: dict | None = None,
                               candidate_sha: str | None = None) -> dict:
        """Read a bounded receipt written by the controlled runtime.

        The ledger never treats a caller-provided hash as execution evidence:
        the referenced regular file must exist below this state's private
        artifact directory, match its digest, carry the exact task lease
        context, and contain the expected bounded payload.
        """
        path_value = receipt.get("artifact_path") or receipt.get("qc_artifact_path")
        artifact_sha = receipt.get("artifact_sha") or receipt.get("qc_artifact_sha")
        if (not isinstance(path_value, str)
                or not re.fullmatch(r"[0-9a-f]{64}", str(artifact_sha))):
            raise ValueError("receipt artifact reference missing")
        raw = Path(path_value).expanduser()
        private = (self.home / "private").resolve()
        if raw.is_symlink() or not raw.is_file():
            raise ValueError("receipt artifact unavailable")
        resolved = raw.resolve(strict=True)
        try:
            resolved.relative_to(private)
        except ValueError as exc:
            raise ValueError("receipt artifact outside private state") from exc
        if resolved.stat().st_size > 64_000:
            raise ValueError("receipt artifact exceeds size limit")
        raw_bytes = resolved.read_bytes()
        if hashlib.sha256(raw_bytes).hexdigest() != artifact_sha:
            raise ValueError("receipt artifact hash mismatch")
        try:
            artifact = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("receipt artifact is not bounded JSON") from exc
        if not isinstance(artifact, dict) or artifact.get("kind") != kind:
            raise ValueError("receipt artifact kind mismatch")
        context = artifact.get("context")
        if (not isinstance(context, dict) or context.get("task_id") != task_id
                or context.get("run_id") != run_id or context.get("attempt") != attempt
                or context.get("source_sha") != source_sha):
            raise ValueError("receipt artifact lease mismatch")
        if candidate_sha is not None and context.get("candidate_sha") != candidate_sha:
            raise ValueError("receipt artifact candidate binding mismatch")
        if payload is not None and artifact.get("payload") != payload:
            raise ValueError("receipt artifact payload mismatch")
        artifact["artifact_sha"] = artifact_sha
        return artifact

    def validate_execution_artifacts(self, tid: str, *, source_sha: str, candidate_sha: str,
                                     changed_files: list[str], test_receipt: dict,
                                     qc_receipt: dict, run_id: str, attempt: int) -> dict:
        """Validate Docker and independent-QC artifacts for every accepted run."""
        if not SHA.fullmatch(candidate_sha) or not SHA.fullmatch(source_sha):
            raise ValueError("invalid execution artifact SHA")
        if not isinstance(changed_files, list) or not 1 <= len(changed_files) <= 30:
            raise ValueError("invalid execution artifact changed files")
        if (not isinstance(test_receipt, dict) or test_receipt.get("passed") is not True
                or test_receipt.get("exit_code") != 0
                or test_receipt.get("tests_detected") is not True
                or test_receipt.get("sandbox") != "docker_no_network"
                or not re.fullmatch(r"[0-9a-f]{64}", str(test_receipt.get("receipt_sha", "")))):
            raise ValueError("test receipt did not pass")
        test_payload = dict(test_receipt)
        provided_test_sha = test_payload.pop("receipt_sha")
        expected_test_sha = hashlib.sha256(
            json.dumps({key: value for key, value in test_payload.items()
                        if key not in {"artifact_path", "artifact_sha"}},
                       sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if provided_test_sha != expected_test_sha:
            raise ValueError("test receipt provenance mismatch")
        test_artifact = self._read_receipt_artifact(
            test_receipt, kind="docker_test_receipt", task_id=tid,
            run_id=run_id, attempt=attempt, source_sha=source_sha,
            payload={key: value for key, value in test_payload.items()
                     if key not in {"artifact_path", "artifact_sha"}},
            candidate_sha=candidate_sha,
        )
        expected_files_sha = hashlib.sha256(
            json.dumps(changed_files, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if test_artifact["context"].get("changed_files_sha") != expected_files_sha:
            raise ValueError("test artifact changed-file binding mismatch")
        if (not isinstance(qc_receipt, dict) or qc_receipt.get("verdict") != "PASS"
                or qc_receipt.get("reviewer") != "independent_qc"
                or qc_receipt.get("candidate_sha") != candidate_sha
                or not re.fullmatch(r"[0-9a-f]{64}", str(qc_receipt.get("qc_output_sha", "")))):
            raise ValueError("QC receipt did not pass")
        qc_artifact = self._read_receipt_artifact(
            qc_receipt, kind="independent_qc_receipt", task_id=tid,
            run_id=run_id, attempt=attempt, source_sha=source_sha,
            candidate_sha=candidate_sha,
        )
        qc_result = qc_artifact.get("payload")
        if (not isinstance(qc_result, dict)
                or qc_result.get("verdict") != qc_receipt.get("verdict")
                or qc_result.get("findings") != qc_receipt.get("findings")
                or qc_artifact.get("source_output_sha") != qc_receipt.get("qc_output_sha")
                or qc_artifact["context"].get("changed_files_sha") != expected_files_sha):
            raise ValueError("QC artifact provenance mismatch")
        return {"test_artifact_sha": test_artifact["artifact_sha"],
                "qc_artifact_sha": qc_artifact["artifact_sha"]}

    def subtask_evidence_ready(self, tid: str, candidate_sha: str) -> bool:
        """Return whether one candidate has a receipt for every required child."""
        with self.db() as db:
            has_receipts = db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='subtask_receipts'"
            ).fetchone()
            row = db.execute(
                "SELECT count(*) AS children, "
                "sum(CASE WHEN status IN ('completed','archived') THEN 1 ELSE 0 END) AS complete, "
                "? AS receipts "
                "FROM subtasks WHERE parent_id=?",
                (0, tid),
            ).fetchone()
            if has_receipts:
                row = dict(row)
                row["receipts"] = db.execute(
                    "SELECT count(*) FROM subtask_receipts r WHERE r.parent_id=? "
                    "AND r.candidate_sha=? AND r.verifier='independent_qc'",
                    (tid, candidate_sha),
                ).fetchone()[0]
            return (not row["children"] or
                    (row["children"] == row["complete"] == row["receipts"]))

    def record_subtask_evidence(
        self,
        tid: str,
        *,
        candidate_sha: str,
        source_sha: str,
        changed_files: list[str],
        test_receipt: dict,
        qc_receipt: dict,
        child_evidence: list[dict],
        locked: bool = False,
        run_id: str | None = None,
        attempt: int | None = None,
    ) -> dict:
        """Record one bounded receipt per child after independent QC.

        Model prose is untrusted input and is reduced to a hash. The live
        ledger retains bounded receipt metadata only; parent completion requires
        these exact candidate-bound receipts.
        """
        if not SHA.fullmatch(candidate_sha) or not SHA.fullmatch(source_sha):
            raise ValueError("invalid receipt SHA")
        if not run_id or attempt is None or attempt < 1:
            raise ValueError("receipt run binding required")
        if not isinstance(changed_files, list) or not 1 <= len(changed_files) <= 30:
            raise ValueError("invalid receipt changed files")
        if any(not isinstance(path, str) or not path or len(path) > 250 for path in changed_files):
            raise ValueError("invalid receipt path")
        if (not isinstance(test_receipt, dict) or test_receipt.get("passed") is not True
                or test_receipt.get("exit_code") != 0
                or test_receipt.get("tests_detected") is not True
                or test_receipt.get("sandbox") != "docker_no_network"
                or not re.fullmatch(r"[0-9a-f]{64}", str(test_receipt.get("receipt_sha", "")))):
            raise ValueError("test receipt did not pass")
        test_payload = dict(test_receipt)
        provided_test_sha = test_payload.pop("receipt_sha", "")
        expected_test_sha = hashlib.sha256(
            json.dumps({key: value for key, value in test_payload.items()
                        if key not in {"artifact_path", "artifact_sha"}},
                       sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if provided_test_sha != expected_test_sha:
            raise ValueError("test receipt provenance mismatch")
        test_artifact = self._read_receipt_artifact(
            test_receipt, kind="docker_test_receipt", task_id=tid,
            run_id=run_id, attempt=attempt, source_sha=source_sha,
            payload={key: value for key, value in test_payload.items()
                     if key not in {"artifact_path", "artifact_sha"}},
            candidate_sha=candidate_sha,
        )
        if (not isinstance(qc_receipt, dict) or qc_receipt.get("verdict") != "PASS"
                or qc_receipt.get("reviewer") != "independent_qc"
                or qc_receipt.get("candidate_sha") != candidate_sha
                or not re.fullmatch(r"[0-9a-f]{64}", str(qc_receipt.get("qc_output_sha", "")))):
            raise ValueError("QC receipt did not pass")
        if not isinstance(child_evidence, list) or len(child_evidence) > 2000:
            raise ValueError("invalid child evidence")

        test_ref = hashlib.sha256(
            json.dumps(test_receipt, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        by_id: dict[str, dict] = {}
        for item in child_evidence:
            if not isinstance(item, dict) or set(item) != {"subtask_id", "status", "evidence"}:
                raise ValueError("invalid child evidence item")
            cid = item["subtask_id"]
            if not isinstance(cid, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,160}", cid):
                raise ValueError("invalid child evidence ID")
            if item["status"] != "PASS" or not isinstance(item["evidence"], str) or not 1 <= len(item["evidence"]) <= 240:
                raise ValueError("child evidence is not accepted")
            if cid in by_id:
                raise ValueError("duplicate child evidence")
            by_id[cid] = item

        lock_context = self.master_lock() if not locked else contextlib.nullcontext()
        with lock_context:
            with self.db() as db:
                db.execute("BEGIN IMMEDIATE")
                task = db.execute(
                    "SELECT project_id,attempt,last_run,status,base_sha,candidate_sha FROM tasks WHERE id=?", (tid,)
                ).fetchone()
                if not task or not task["project_id"]:
                    db.execute("ROLLBACK")
                    raise ValueError("task has no imported subtasks")
                if run_id is not None and (task["last_run"] != run_id or
                                           (attempt is not None and task["attempt"] != attempt)):
                    db.execute("ROLLBACK")
                    raise ValueError("stale_worker_lease")
                if not task["base_sha"] or source_sha != task["base_sha"]:
                    db.execute("ROLLBACK")
                    raise ValueError("receipt source checkpoint mismatch")
                if task["candidate_sha"] != candidate_sha:
                    db.execute("ROLLBACK")
                    raise ValueError("receipt candidate checkpoint mismatch")
                children = db.execute(
                    "SELECT id FROM subtasks WHERE parent_id=? ORDER BY sequence", (tid,)
                ).fetchall()
                ids = [row[0] for row in children]
                if set(ids) != set(by_id) or len(ids) != len(by_id):
                    db.execute("ROLLBACK")
                    raise ValueError("child evidence does not cover every child")
                contract_payload = []
                for child in db.execute(
                    "SELECT id,sequence,spec,payload_sha FROM subtasks WHERE parent_id=? ORDER BY sequence", (tid,)
                ):
                    contract_payload.append({"id": child["id"], "sequence": child["sequence"],
                                             "spec": json.loads(child["spec"]), "payload_sha": child["payload_sha"]})
                contract_sha = payload_sha({"parent_id": tid, "children": contract_payload})
                expected_child_sha = hashlib.sha256(
                    json.dumps(child_evidence, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()
                expected_files_sha = hashlib.sha256(
                    json.dumps(changed_files, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()
                if test_artifact["context"].get("changed_files_sha") != expected_files_sha:
                    db.execute("ROLLBACK")
                    raise ValueError("test artifact changed-file binding mismatch")
                if (qc_receipt.get("contract_sha") != contract_sha
                        or qc_receipt.get("child_evidence_sha") != expected_child_sha
                        or qc_receipt.get("changed_files_sha") != expected_files_sha):
                    db.execute("ROLLBACK")
                    raise ValueError("QC receipt provenance mismatch")
                qc_artifact = self._read_receipt_artifact(
                    qc_receipt, kind="independent_qc_receipt", task_id=tid,
                    run_id=run_id, attempt=attempt, source_sha=source_sha,
                    candidate_sha=candidate_sha,
                )
                qc_result = qc_artifact["payload"]
                if (qc_result.get("verdict") != qc_receipt.get("verdict")
                        or qc_result.get("findings") != qc_receipt.get("findings")
                        or qc_artifact.get("source_output_sha") != qc_receipt.get("qc_output_sha")
                        or qc_artifact["context"].get("contract_sha") != contract_sha
                        or qc_artifact["context"].get("changed_files_sha") != expected_files_sha):
                    db.execute("ROLLBACK")
                    raise ValueError("QC artifact provenance mismatch")
                qc_ref = hashlib.sha256(
                    json.dumps(qc_receipt, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest()
                timestamp = now()
                for cid in ids:
                    item = by_id[cid]
                    evidence_sha = hashlib.sha256(
                        json.dumps(item, sort_keys=True, separators=(",", ":")).encode()
                    ).hexdigest()
                    receipt_id = str(uuid.uuid4())
                    db.execute(
                        "INSERT INTO subtask_receipts(receipt_id,subtask_id,parent_id,generation,source_sha,candidate_sha,"
                        "changed_files,test_ref,test_artifact_sha,qc_receipt,qc_artifact_sha,evidence_sha,contract_sha,verifier,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                        "ON CONFLICT(subtask_id,candidate_sha) DO UPDATE SET receipt_id=excluded.receipt_id,"
                        "generation=excluded.generation,source_sha=excluded.source_sha,changed_files=excluded.changed_files,"
                        "test_ref=excluded.test_ref,test_artifact_sha=excluded.test_artifact_sha,qc_receipt=excluded.qc_receipt,"
                        "qc_artifact_sha=excluded.qc_artifact_sha,evidence_sha=excluded.evidence_sha,"
                        "verifier=excluded.verifier,created_at=excluded.created_at",
                        (receipt_id, cid, tid, task["attempt"], source_sha, candidate_sha,
                        json.dumps(changed_files, separators=(",", ":")), test_ref, test_artifact["artifact_sha"], qc_ref,
                         qc_artifact["artifact_sha"], evidence_sha, contract_sha, "independent_qc", timestamp),
                    )
                    db.execute(
                        "UPDATE subtasks SET status='completed',evidence=?,updated_at=? WHERE id=?",
                        (json.dumps({"receipt_id": receipt_id, "candidate_sha": candidate_sha,
                                     "test_ref": test_ref, "qc_receipt": qc_ref}, separators=(",", ":")),
                         timestamp, cid),
                    )
                db.execute("COMMIT")
        return {"parent_id": tid, "candidate_sha": candidate_sha, "children": len(ids), "test_ref": test_ref}

    def emit(self, tid: str, run_id: str, *, stage: str, step: str, branch: str, base_sha: str,
             tools: int = 0, attempt: int = 1, elapsed: int = 0, result: str = ""):
        if (stage not in STAGE or not SAFE.fullmatch(step)
                or not branch.startswith(("feature/", "feat/")) or not SHA.fullmatch(base_sha)
                or not isinstance(result, str) or not EVENT_RESULT.fullmatch(result)):
            raise ValueError("invalid progress event")
        for retry in range(4):
            try:
                with self.db() as db:
                    db.execute("BEGIN IMMEDIATE")
                    lease = db.execute(
                        "SELECT last_run,attempt FROM tasks WHERE id=?", (tid,)
                    ).fetchone()
                    if not lease or lease["last_run"] != run_id or lease["attempt"] != attempt:
                        db.execute("ROLLBACK")
                        raise ValueError("stale_worker_lease")
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
                rows=db.execute("SELECT id,last_run FROM tasks WHERE status IN ('preflight','coding','verifying')").fetchall()
                for r in rows:
                    db.execute("UPDATE runs SET status='interrupted',finished_at=? WHERE id=?",(now(),r["last_run"]))
                    db.execute("UPDATE tasks SET status='interrupted',last_run='',last_error='master_restart_review_required',updated_at=? WHERE id=?",(now(),r["id"]))
                return [r["id"] for r in rows]

    def _write_breakdown_report(self, db: sqlite3.Connection, tid: str, reason: str) -> dict:
        """Persist one bounded, immutable failure summary before a retry ceiling stops work."""
        if not re.fullmatch(r"[a-z0-9_:-]{2,64}", reason):
            raise ValueError("invalid breakdown report reason")
        task = db.execute(
            "SELECT id,status,attempt,last_error,base_sha,candidate_sha,integrated_sha,branch,worktree "
            "FROM tasks WHERE id=?", (tid,)
        ).fetchone()
        if not task:
            raise ValueError("unknown task")
        report_dir = self.home / "reports" / "breakdown"
        report_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        report_path = report_dir / f"{tid.lower()}-{reason}-attempt-{task['attempt']}.json"

        def verify_existing(path: Path) -> dict:
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
                digest = document.pop("report_sha256")
                body = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                if hashlib.sha256(body.encode("utf-8")).hexdigest() != digest:
                    raise ValueError("breakdown report digest mismatch")
                if document.get("task_id") != tid or document.get("reason") != reason:
                    raise ValueError("breakdown report identity mismatch")
                return {"path": str(path), "sha256": digest, "immutable": True}
            except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise ValueError("existing breakdown report is invalid") from exc

        if report_path.exists():
            return verify_existing(report_path)

        run_rows = db.execute(
            "SELECT id,attempt,role,status,started_at,finished_at,model,tool_count,error_code "
            "FROM runs WHERE task_id=? ORDER BY attempt,started_at LIMIT 100", (tid,)
        ).fetchall()
        submission_rows = db.execute(
            "SELECT attempt,base_sha,candidate_sha,branch,worktree,status,failure_code "
            "FROM candidate_submissions WHERE task_id=? ORDER BY attempt,created_at LIMIT 100", (tid,)
        ).fetchall()
        quarantine_rows = []
        if db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='candidate_quarantine'"
        ).fetchone():
            quarantine_rows = db.execute(
                "SELECT attempt,candidate_sha,branch,worktree,failure_code,source "
                "FROM candidate_quarantine WHERE task_id=? ORDER BY attempt,created_at LIMIT 100", (tid,)
            ).fetchall()
        settings = dict(db.execute(
            "SELECT key,value FROM settings WHERE key IN ('source_sha','integration_sha','integration_branch')"
        ).fetchall())
        payload = {
            "format": "astra-one-breakdown-v1",
            "task_id": tid,
            "reason": reason,
            "ceiling_attempt": task["attempt"],
            "max_attempts": MAX_FAILURES,
            "generated_at": now(),
            "source_sha": settings.get("source_sha", ""),
            "integration_sha": settings.get("integration_sha", ""),
            "integration_branch": settings.get("integration_branch", ""),
            "task": {key: task[key] or "" for key in (
                "status", "attempt", "last_error", "base_sha", "candidate_sha",
                "integrated_sha", "branch", "worktree",
            )},
            "runs": [dict(item) for item in run_rows],
            "candidate_submissions": [dict(item) for item in submission_rows],
            "candidate_quarantine": [dict(item) for item in quarantine_rows],
        }
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if len(body.encode("utf-8")) > 100_000:
            raise ValueError("breakdown report exceeds bound")
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        document = {**payload, "report_sha256": digest}
        text = json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        try:
            fd = os.open(report_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
        except FileExistsError:
            return verify_existing(report_path)
        return {"path": str(report_path), "sha256": digest, "immutable": True}

    def retry(self, tid: str):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT status,attempt,project_id,owner_gate,last_error FROM tasks WHERE id=?",(tid,)).fetchone()
            if not row or row["status"] not in {"failed","interrupted","conflict","stopped"}:
                db.execute("ROLLBACK")
                raise ValueError("only failed/interrupted/conflict/stopped tasks below retry ceiling can retry")
            if row["last_error"] == "codex_effects_uncertain":
                db.execute("ROLLBACK")
                raise ValueError("uncertain tool effects require reconciliation before retry")
            if row["attempt"] >= MAX_FAILURES:
                report = self._write_breakdown_report(db, tid, "retry_ceiling")
                db.execute("COMMIT")
                raise ValueError("retry ceiling reached; breakdown report is immutable")
            if db.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='supervisor_lanes'"
            ).fetchone() and db.execute(
                "SELECT 1 FROM supervisor_lanes WHERE task_id=? AND state<>'idle'", (tid,)
            ).fetchone():
                db.execute("ROLLBACK")
                raise ValueError("task has active recovery lease")
            status = "pending" if row["project_id"] and not row["owner_gate"] else "queued"
            db.execute("UPDATE tasks SET status=?,available_at=0,last_run='',integrated_sha='',updated_at=? WHERE id=?",(status,now(),tid))
            if row["project_id"]:
                for queue in ("review_queue", "merge_queue"):
                    db.execute(f"DELETE FROM {queue} WHERE parent_id=?", (tid,))
                db.execute(
                    "INSERT INTO pending_queue(parent_id,project_id,enqueue_seq,available_at,created_at) "
                    "SELECT id,project_id,enqueue_seq,0,? FROM tasks WHERE id=? "
                    "ON CONFLICT(parent_id) DO UPDATE SET available_at=excluded.available_at",
                    (now(), tid),
                )
            db.execute("COMMIT")

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
                    row = db.execute("SELECT status,project_id,owner_gate FROM tasks WHERE id=?", (tid,)).fetchone()
                    if not row or row["status"] != "failed":
                        raise ValueError("only failed tasks can start a new repair generation")
                    if row["project_id"] and db.execute(
                        "SELECT 1 FROM supervisor_lanes WHERE task_id=? AND state<>'idle'", (tid,)
                    ).fetchone():
                        raise ValueError("task has active recovery lease")
                    status = "approval_required" if row["owner_gate"] else ("pending" if row["project_id"] else "queued")
                    prior_attempt = db.execute(
                        "SELECT COALESCE(MAX(attempt),0) FROM runs WHERE task_id=?", (tid,)
                    ).fetchone()[0]
                    db.execute(
                        "UPDATE tasks SET status=?,attempt=?,available_at=0,last_run='',last_error='',"
                        "candidate_sha='',integrated_sha='',changed_files='[]',qc_evidence='',base_sha='',branch='',worktree='',updated_at=? "
                        "WHERE id=?", (status, prior_attempt, epoch, tid)
                    )
                    db.execute(
                        "INSERT INTO settings(key,value) VALUES(?,?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (f"retry_epoch:{tid}", epoch),
                    )
                    if row["project_id"] and not row["owner_gate"]:
                        db.execute(
                            "UPDATE subtasks SET status='waiting',evidence='',updated_at=? WHERE parent_id=?",
                            (epoch, tid),
                        )
                        db.execute(
                            "INSERT INTO pending_queue(parent_id,project_id,enqueue_seq,available_at,created_at) "
                            "SELECT id,project_id,enqueue_seq,0,? FROM tasks WHERE id=? "
                            "ON CONFLICT(parent_id) DO UPDATE SET available_at=excluded.available_at",
                            (epoch, tid),
                        )
                        # An explicit reopen is the authorized transition out
                        # of a stale batch classification. Preserve the case
                        # and cohort history, but make the current generation
                        # claimable again.
                        db.execute(
                            "UPDATE supervisor_cases SET state='reopened',updated_at=? "
                            "WHERE parent_id=? AND state='external_blocker'",
                            (epoch, tid),
                        )
                        db.execute(
                            "UPDATE batch_members SET state='admitted',updated_at=? "
                            "WHERE parent_id=? AND state IN ('external_blocker','running') "
                            "AND batch_id IN (SELECT batch_id FROM batch_epochs "
                            "WHERE state IN ('running','draining'))",
                            (epoch, tid),
                        )
                    reopened.append(tid)
                db.execute("COMMIT")
                return reopened

    def approve(self, tid: str, *, run_id: str | None = None, attempt: int | None = None):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute(
                "SELECT status,qc_evidence,project_id,candidate_sha,last_run,attempt FROM tasks WHERE id=?", (tid,)
            ).fetchone()
            if not row or row["status"]!="awaiting_review" or not row["qc_evidence"]:
                db.execute("ROLLBACK")
                raise ValueError("task must pass independent QC before approval")
            if run_id is not None and (row["last_run"] != run_id or
                                       (attempt is not None and row["attempt"] != attempt)):
                db.execute("ROLLBACK")
                raise ValueError("stale_worker_lease")
            db.execute("UPDATE tasks SET status='approved',updated_at=? WHERE id=?",(now(),tid))
            if row["project_id"]:
                db.execute("DELETE FROM review_queue WHERE parent_id=?", (tid,))
                db.execute(
                    "INSERT INTO merge_queue(parent_id,project_id,candidate_sha,created_at) VALUES(?,?,?,?) "
                    "ON CONFLICT(parent_id) DO UPDATE SET candidate_sha=excluded.candidate_sha",
                    (tid, row["project_id"], row["candidate_sha"], now()),
                )
            db.execute("COMMIT")

    def overview(self) -> dict:
        with self.db() as db:
            counts={r[0]:r[1] for r in db.execute("SELECT status,count(*) FROM tasks GROUP BY status")}
            pending=db.execute("SELECT count(*) FROM events WHERE synced=0").fetchone()[0]
        answer={"version":VERSION,"state_version":self.get("version"),"approved_architecture":bool(self.get("approved_architecture_sha")),"workers_max":MAX_WORKERS,"integration_sha":self.get("integration_sha"),"tasks":counts,"monitor_pending":pending,
                "stop":(self.home/"STOP").exists(),"pause":(self.home/"PAUSE").exists(),"quota_pause":(self.home/"PAUSED_QUOTA").exists()}
        if self.database.exists():
            try:
                answer["full_plan"] = self.full_plan_status()
            except (sqlite3.OperationalError, ValueError):
                answer["full_plan"] = {"imported": False, "schema_ready": False}
        return answer
