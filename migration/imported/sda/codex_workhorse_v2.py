#!/usr/bin/env python3
"""JARVIS workhorse v2: durable queues and resumable, role-scoped Codex sessions.

Run this *outside* the interactive supervisor Codex chat. Only this master
mutates shared develop; five worker processes maximum, plus one QC and merger.
"""
from __future__ import annotations

import argparse
import secrets
import fcntl
import json
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = Path.home() / ".local" / "state" / "jarvis" / "workhorse-v2"
TASKS = ROOT / "TASKS.md"
PARENTS = re.compile(r"^- \[([ x])\] (JRV-\d{3}) \[P(\d)\]", re.MULTILINE)
STATES = ("pending", "waiting", "running", "qc", "repairing", "merge", "merging",
          "rebuild", "done", "blocked")
RESTRICTED = re.compile(
    r"(^|/)(\.env($|\.)|\.ssh/|\.gnupg/|keyrings/|cookies?($|\.)|"
    r"sessions?($|\.)|id_rsa$|id_ed25519$)|\.(pem|p12|pfx|sqlite|sqlite3|db|key)$", re.I
)
VALID_REMOTES = {
    "git@github.com:admindeveloper4562/personal-jarvis.git",
    "https://github.com/admindeveloper4562/personal-jarvis.git",
    "https://github.com/admindeveloper4562/personal-jarvis",
}
MODELS = {
    "supervisor": ("gpt-5.6-luna", "medium"),  # interactive, not spawned
    "worker": ("gpt-5.1-luna", "low"),
    "repairer": ("gpt-5.6-luna", "low"),
    "merger": ("gpt-5.6-sol", "medium"),
}
MAX_ATTEMPTS = 20
QUOTA = re.compile(r"usage limit|quota exceeded|insufficient_quota|rate.?limit|billing limit", re.I)
ENV_BLOCKER = re.compile(r"unknown model|model not found|model is not supported|invalid model|authentication required|not logged in", re.I)
ALL_CHECKBOXES = re.compile(r"^\s*- \[([ x])\] ", re.MULTILINE)


def git(*args: str, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError("Git command failed: " + " ".join(args[:3]) + ": " + p.stderr[-350:])
    return p


def proc_identity(pid: int) -> tuple[int, str] | None:
    """Linux process start tick and state; prevents PID-reuse false positives."""
    try:
        tail = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return int(tail[19]), tail[0]  # /proc field 22 and field 3
    except (FileNotFoundError, PermissionError, IndexError, ValueError):
        return None


def alive(pid: int, start_tick: int) -> bool:
    identity = proc_identity(pid)
    return bool(identity and identity[0] == start_tick and identity[1] not in {"Z", "X"})


def codex_events(path: str) -> tuple[str | None, int, int, bool, bool, str]:
    """Read persisted JSONL; missing token values are unknown, never invented."""
    session = None
    tin = tout = 0
    complete = failed = False
    last_message = ""
    if not path or not Path(path).is_file():
        return session, tin, tout, complete, failed, last_message
    for raw in Path(path).read_text(errors="replace").splitlines():
        try:
            event = json.loads(raw)
        except (ValueError, TypeError):
            continue
        kind = str(event.get("type", ""))
        if kind in {"thread.started", "session.started"}:
            session = event.get("thread_id") or event.get("session_id") or session
        if kind in {"turn.completed", "task.completed"}:
            complete = True
            usage = event.get("usage") or {}
            tin += int(usage.get("input_tokens") or 0)
            tout += int(usage.get("output_tokens") or 0)
        if kind in {"turn.failed", "error", "task.failed"}:
            failed = True
            last_message = str(event.get("message") or event.get("error") or "")[-300:]
        if kind in {"item.completed", "agent_message"}:
            item = event.get("item") or {}
            if isinstance(item, dict) and item.get("type") == "agent_message":
                message = str(item.get("text", ""))
                # Preserve a merger's focused request for additional tests
                # even when its final response includes a lengthy review.
                if "MERGER_NEEDS_QC:" in message:
                    marker = message.index("MERGER_NEEDS_QC:")
                    last_message = message[marker:marker + 1200]
                elif "MERGER_NEEDS_QC:" not in last_message:
                    last_message = message[-450:]
    return session, tin, tout, complete, failed, last_message



def require_one_line(value: str, max_len: int) -> str:
    if not value or len(value) > max_len or any(c in value for c in "\r\n\x00"):
        raise ValueError("supervisor task text must be a bounded single line")
    return value.strip()

def task_rows(text: str) -> list[tuple[str, int, bool]]:
    return [(m.group(2), int(m.group(3)), m.group(1) == "x") for m in PARENTS.finditer(text)]


def checkbox_progress(text: str) -> tuple[int, int]:
    marks = ALL_CHECKBOXES.findall(text)
    return sum(mark == "x" for mark in marks), len(marks)


def quota_in_log(path: str) -> bool:
    try:
        return bool(QUOTA.search(Path(path).read_text(errors="replace")[-12000:]))
    except OSError:
        return False


def parent_checked(path: Path, parent: str) -> bool:
    try:
        return any(pid == parent and done for pid, _, done in task_rows(path.read_text()))
    except OSError:
        return False


def deleted_sources_logged(worktree: Path, baseline: str = "develop") -> tuple[bool, str]:
    """Audit tracked deletions before QC or merge, never infer owner approval.

    This is a Git-content policy check only. Unrestricted Codex can modify user
    files outside this repo, which requires OS-level audit controls separately.
    """
    deleted: set[str] = set()
    for args in (
        ("diff", "--name-only", "--diff-filter=D", baseline + "...HEAD"),
        ("diff", "--cached", "--name-only", "--diff-filter=D"),
        ("diff", "--name-only", "--diff-filter=D"),
    ):
        result = git(*args, cwd=worktree, check=False)
        if result.returncode:
            return False, "cannot verify deleted paths against baseline"
        deleted.update(name for name in result.stdout.splitlines() if name)
    if not deleted:
        return True, "no tracked source deletions"
    path = worktree / "DELETE-LOGS.md"
    if not path.is_file():
        return False, "tracked deletion without DELETE-LOGS.md"
    record = path.read_text(errors="replace")
    for name in sorted(deleted):
        rows = []
        for line in record.splitlines():
            if not line.startswith("|"):
                continue
            cells = [part.strip() for part in line.strip("|").split("|")]
            if len(cells) >= 7 and cells[1] == name and cells[3] not in {"", "-", "—"}:
                rows.append(cells)
        if not rows:
            return False, f"missing one-file approval log for deleted path: {name}"
    return True, f"{len(deleted)} tracked deletions have individual log entries"


def tests_pass(worktree: Path) -> tuple[bool, str]:
    """Run actual tests, not only model self-reports; gate the merge."""
    # Use the same repository safety + compilation + unittest gate as CI.
    # It also validates tracked-file modes before a branch can merge.
    p = subprocess.run(
        [sys.executable, "scripts/ci_checks.py"],
        cwd=worktree, capture_output=True, text=True, timeout=240,
    )
    if p.returncode:
        return False, "CI safety/compile/tests failed: " + (p.stderr or p.stdout)[-500:]
    logged, detail = deleted_sources_logged(worktree)
    if not logged:
        return False, detail
    p = git("diff", "--check", cwd=worktree, check=False)
    if p.returncode:
        return False, "git diff --check failed: " + p.stdout[-300:]
    return True, "full unittest and diff gate passed"


class Master:
    def __init__(self, root: Path = ROOT, state: Path = STATE, workers: int = 5,
                 models: dict | None = None, push: bool = False,
                 retry_limit: int = MAX_ATTEMPTS):
        if not 1 <= workers <= 5:
            raise ValueError("workers must be between 1 and 5")
        self.root = root.resolve()
        self.state = state
        self.tasks = self.root / "TASKS.md"
        self.workers = workers
        self.models = models or {
            role: (
                os.environ.get(f"JARVIS_{role.upper()}_MODEL", model),
                os.environ.get(f"JARVIS_{role.upper()}_EFFORT", effort),
            )
            for role, (model, effort) in MODELS.items()
        }
        self.push = push
        self.retry_limit = retry_limit
        self.processes: dict[int, subprocess.Popen] = {}
        self.guard_handles = []
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.state, 0o700)
        self.db = sqlite3.connect(self.state / "queue.db", timeout=10, isolation_level=None)
        os.chmod(self.state / "queue.db", 0o600)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS jobs (
                parent TEXT PRIMARY KEY,
                priority INTEGER NOT NULL,
                state TEXT NOT NULL,
                generation INTEGER NOT NULL DEFAULT 1,
                branch TEXT NOT NULL DEFAULT '',
                worktree TEXT NOT NULL DEFAULT '',
                integration_branch TEXT NOT NULL DEFAULT '',
                integration_tree TEXT NOT NULL DEFAULT '',
                worker_session TEXT NOT NULL DEFAULT '',
                repair_session TEXT NOT NULL DEFAULT '',
                merger_session TEXT NOT NULL DEFAULT '',
                worker_pid INTEGER NOT NULL DEFAULT 0,
                worker_start_tick INTEGER NOT NULL DEFAULT 0,
                worker_started REAL NOT NULL DEFAULT 0,
                worker_log TEXT NOT NULL DEFAULT '',
                worker_attempts INTEGER NOT NULL DEFAULT 0,
                repair_attempts INTEGER NOT NULL DEFAULT 0,
                merge_attempts INTEGER NOT NULL DEFAULT 0,
                rebuilds INTEGER NOT NULL DEFAULT 0,
                failure TEXT NOT NULL DEFAULT '',
                feedback TEXT NOT NULL DEFAULT '',
                input_tokens INTEGER NOT NULL DEFAULT 0,
                output_tokens INTEGER NOT NULL DEFAULT 0,
                queued_at REAL NOT NULL DEFAULT 0,
                completed_at REAL NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS roles (
                name TEXT PRIMARY KEY, state TEXT NOT NULL DEFAULT 'idle',
                parent TEXT NOT NULL DEFAULT '', pid INTEGER NOT NULL DEFAULT 0,
                start_tick INTEGER NOT NULL DEFAULT 0, started REAL NOT NULL DEFAULT 0,
                logfile TEXT NOT NULL DEFAULT '',
                total_input INTEGER NOT NULL DEFAULT 0,
                total_output INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created REAL NOT NULL, parent TEXT NOT NULL,
                actor TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT NOT NULL
            );
        """)
        columns = {r["name"] for r in self.rows("PRAGMA table_info(jobs)")}
        if "worker_attempts" not in columns:
            self.db.execute("ALTER TABLE jobs ADD COLUMN worker_attempts INTEGER NOT NULL DEFAULT 0")
        for role in ("master", "repairer", "merger"):
            self.db.execute("INSERT OR IGNORE INTO roles(name,state) VALUES (?, 'idle')", (role,))

    def rows(self, sql: str, args: tuple = ()) -> list[dict]:
        return [dict(row) for row in self.db.execute(sql, args).fetchall()]

    def job(self, parent: str) -> dict:
        rows = self.rows("SELECT * FROM jobs WHERE parent=?", (parent,))
        if not rows:
            raise KeyError(parent)
        return rows[0]

    def update(self, parent: str, **fields) -> None:
        if not fields:
            return
        if any(not re.fullmatch(r"[a-z_]+", key) for key in fields):
            raise ValueError("invalid database field")
        sql = ", ".join(f"{field}=?" for field in fields)
        self.db.execute(f"UPDATE jobs SET {sql} WHERE parent=?", (*fields.values(), parent))

    def event(self, parent: str, actor: str, kind: str, detail: str) -> None:
        self.db.execute(
            "INSERT INTO events(created,parent,actor,kind,detail) VALUES (?,?,?,?,?)",
            (time.time(), parent, actor, kind, detail[-1200:]),
        )

    def ingest_submissions(self) -> None:
        """Safely accept supervisor requirements only between merge operations.

        Intake files are never deleted; every accepted requirement receives a
        deterministic parent ID, an on-develop commit, and an archived receipt.
        """
        inbox = self.state / "inbox"
        if not inbox.exists():
            return
        merger = self.rows("SELECT state FROM roles WHERE name='merger'")[0]["state"]
        if merger != "idle" or git("status", "--porcelain", cwd=self.root).stdout.strip():
            return
        for file in sorted(inbox.glob("*.json")):
            try:
                request = json.loads(file.read_text())
                source = str(request["submission_id"])
                if not re.fullmatch(r"[a-f0-9]{16,40}", source):
                    raise ValueError("invalid submission id")
                priority = int(request["priority"])
                accept = str(request["acceptance"])
                if not 0 <= priority <= 4 or not re.fullmatch(r"AC-\d{2}", accept):
                    raise ValueError("invalid priority or gate")
                title = require_one_line(str(request["title"]), 260)
                done = require_one_line(str(request["done_when"]), 300)
            except (ValueError, TypeError, KeyError):
                self.event("", "supervisor", "invalid_submission", file.name)
                continue
            before = self.tasks.read_text()
            if f"Submission: {source}" in before:
                self.archive_submission(file)
                continue
            nums = [int(pid.split("-")[1]) for pid, _, _ in task_rows(before)]
            parent = f"JRV-{max(nums, default=0)+1:03d}"
            if "## Supervisor-submitted parent tasks" not in before:
                before += "\n\n## Supervisor-submitted parent tasks\n"
            line = (
                f"- [ ] {parent} [P{priority}][{accept}] {title} "
                f"| Done when: {done} | Submission: {source}\n"
            )
            self.tasks.write_text(before.rstrip("\n") + "\n" + line)
            os.chmod(self.tasks, self.tasks.stat().st_mode & 0o777)
            git("add", "--", "TASKS.md", cwd=self.root)
            try:
                git("commit", "-m", f"tasks(supervisor): create {parent}", cwd=self.root)
            except RuntimeError:
                # No deletion/rollback: fail visibly for owner investigation.
                self.event(parent, "master", "task_commit_blocked",
                           "TASKS.md was updated but commit failed; pause merges")
                break
            self.archive_submission(file)
            self.event(parent, "supervisor", "accepted", title)

    def archive_submission(self, source: Path) -> None:
        folder = self.state / "submitted"
        folder.mkdir(parents=True, exist_ok=True)
        destination = folder / source.name
        if destination.exists():
            raise RuntimeError("submission receipt already exists")
        source.rename(destination)  # preserve receipt; never delete it

    def ingest(self) -> None:
        for parent, priority, done in task_rows(self.tasks.read_text()):
            existing = self.rows("SELECT state FROM jobs WHERE parent=?", (parent,))
            if not existing:
                self.db.execute(
                    "INSERT INTO jobs(parent,priority,state,queued_at) VALUES (?,?,?,?)",
                    (parent, priority, "done" if done else "pending", time.time()),
                )
                self.event(parent, "master", "discovered", "parent ingested from TASKS.md")
            elif done and existing[0]["state"] == "pending":
                self.update(parent, state="done")

    def validate(self) -> None:
        if git("rev-parse", "--show-toplevel", cwd=self.root).stdout.strip() != str(self.root):
            raise RuntimeError("unexpected repository root")
        if git("branch", "--show-current", cwd=self.root).stdout.strip() != "develop":
            raise RuntimeError("master requires checked-out develop")
        if git("remote", "get-url", "origin", cwd=self.root).stdout.strip() not in VALID_REMOTES:
            raise RuntimeError("unexpected remote; refusing automated merge or push")
        # Do not race with the original sequential autopilot or legacy master.
        for file in (
            Path.home() / ".local/state/jarvis/codex-autopilot/autopilot.lock",
            Path.home() / ".local/state/jarvis/codex-workhorse/master.lock",
        ):
            file.parent.mkdir(parents=True, exist_ok=True)
            handle = file.open("a")
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                handle.close()
                raise RuntimeError("conflicting older supervisor is active") from exc
            self.guard_handles.append(handle)

    def pick(self, states: tuple[str, ...]) -> dict | None:
        marks = ",".join("?" for _ in states)
        jobs = self.rows(
            f"SELECT * FROM jobs WHERE state IN ({marks}) "
            "ORDER BY CASE state WHEN 'waiting' THEN 0 WHEN 'rebuild' THEN 1 ELSE 2 END,"
            "priority, queued_at, parent LIMIT 1", states,
        )
        return jobs[0] if jobs else None

    def prepare_worker(self, row: dict) -> dict:
        parent = row["parent"]
        if row["branch"] and Path(row["worktree"]).is_dir():
            return row
        branch = f"workhorse-v2/{parent}-g{row['generation']}"
        path = self.state / "worktrees" / f"{parent}-g{row['generation']}"
        path.parent.mkdir(parents=True, exist_ok=True)
        # Never overwrite a stale directory or branch with unreviewed work.
        if path.exists() or git("show-ref", "--verify", "--quiet",
                               f"refs/heads/{branch}", cwd=self.root, check=False).returncode == 0:
            raise RuntimeError(f"worker path/branch collision: {parent}")
        git("worktree", "add", "-b", branch, str(path), "develop", cwd=self.root)
        self.update(parent, branch=branch, worktree=str(path))
        self.event(parent, "master", "worktree", f"created {branch} from current develop")
        return self.job(parent)

    def prompt(self, row: dict, role: str) -> str:
        parent = row["parent"]
        if role == "worker":
            return (
                f"JARVIS feature WORKER, assigned only {parent}. Read AGENTS.md, "
                "SECURITY.md, TASKS.md and docs/PROJECT_ACCEPTANCE.md. Build this parent "
                "feature in this isolated worktree; add concrete subtasks to TASKS.md as "
                "needed, implement code/tests and commit. Resume your exact existing "
                "session and apply this QC feedback before anything else: "
                f"{row['feedback'][-1800:] or 'new task'}. Mark the parent [x] ONLY "
                "when tests prove it finished. Never push or merge. Every real existing "
                "file deletion needs individual owner approval and DELETE-LOGS.md entry."
            )
        if role == "repairer":
            return (
                f"JARVIS single QC REPAIRER for {parent}. Inspect full diff relative "
                "to base develop, verify feature acceptance, add real unit and regression "
                "tests, fix bugs in this worker branch, run python3 -m unittest discover "
                "-s tests -q and git diff --check. Commit reviewed fixes. If broken, "
                "state exact error, cause and recommendation. Never merge, push, or delete "
                "existing files without individual approval. Previous feedback: "
                + row["feedback"][-1200:]
            )
        return (
            f"JARVIS single MERGER for {parent}. In this INTEGRATION worktree, inspect "
            "the current full codebase and diff from the worker branch. Resolve conflicts "
            "and refactor integration code if needed. Run full unit suite and check "
            "new features against base acceptance. Commit clean changes only after "
            "tests. If tests are missing, clearly state MERGER_NEEDS_QC: followed by "
            "specific missing tests; the master will send the job back to QC. Never "
            "delete existing user files; no remote push or root develop checkout edits."
            f" Previous issue: {row['feedback'][-1200:]}"
        )

    def spawn(self, row: dict, role: str, cwd: Path, session: str = "") -> tuple[int, int, str]:
        model, effort = self.models[role]
        prompt = self.prompt(row, role)
        command = ["codex", "--dangerously-bypass-approvals-and-sandbox", "exec", "--json"]
        if session:
            command += ["resume", session, prompt]
        else:
            command += ["--model", model, "-c", f"model_reasoning_effort={effort}", prompt]
        logs = self.state / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        suffix = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        path = logs / f"{row['parent']}-{role}-{suffix}.jsonl"
        with path.open("wb") as log:
            os.chmod(path, 0o600)
            process = subprocess.Popen(command, cwd=cwd, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
        self.processes[process.pid] = process
        tick = (proc_identity(process.pid) or (0, ""))[0]
        if not tick:
            raise RuntimeError("cannot verify worker process identity")
        self.event(row["parent"], "master", "launched",
                   f"{role} pid={process.pid}, model={model}, resumed={bool(session)}")
        return process.pid, tick, str(path)

    def start_worker(self, row: dict) -> None:
        row = self.prepare_worker(row)
        pid, tick, log = self.spawn(row, "worker", Path(row["worktree"]), row["worker_session"])
        self.update(row["parent"], state="running", worker_pid=pid,
                    worker_start_tick=tick, worker_started=time.time(), worker_log=log)

    def start_role(self, role: str, row: dict, cwd: Path) -> None:
        session = row["repair_session"] if role == "repairer" else row["merger_session"]
        pid, tick, log = self.spawn(row, role, cwd, session)
        self.db.execute(
            "UPDATE roles SET state='running',parent=?,pid=?,start_tick=?,started=?,logfile=? WHERE name=?",
            (row["parent"], pid, tick, time.time(), log, role),
        )
        self.update(row["parent"], state="repairing" if role == "repairer" else "merging")

    def exit_code(self, pid: int, logfile: str) -> int:
        process = self.processes.pop(pid, None)
        if process is not None:
            return process.wait(timeout=1)
        _, _, _, ok, failed, _ = codex_events(logfile)
        return 0 if ok and not failed else 1

    def saved_usage(self, parent: str, logfile: str, role: str) -> tuple[bool, bool, str]:
        session, tin, tout, completed, failed, message = codex_events(logfile)
        row = self.job(parent)
        update = {
            "input_tokens": row["input_tokens"] + tin,
            "output_tokens": row["output_tokens"] + tout,
        }
        field = {"worker": "worker_session", "repairer": "repair_session", "merger": "merger_session"}[role]
        if session:
            update[field] = session
        self.update(parent, **update)
        if role != "worker":
            self.db.execute(
                "UPDATE roles SET state='idle',parent='',pid=0,start_tick=0,"
                "total_input=total_input+?,total_output=total_output+? WHERE name=?",
                (tin, tout, role),
            )
        return completed, failed, message

    def finish_worker(self, row: dict) -> None:
        parent = row["parent"]
        rc = self.exit_code(row["worker_pid"], row["worker_log"])
        if quota_in_log(row["worker_log"]):
            self.pause_quota(parent, "worker")
            return
        completed, failed, msg = self.saved_usage(parent, row["worker_log"], "worker")
        if ENV_BLOCKER.search(msg):
            self.update(parent, state="blocked", failure="MODEL_OR_AUTH: " + msg[:350])
            self.event(parent, "master", "blocked_environment", msg[:350])
            return
        if not rc and not failed and parent_checked(Path(row["worktree"]) / "TASKS.md", parent):
            commits = git("rev-list", "--count", f"develop..{row['branch']}", cwd=self.root)
            if int(commits.stdout.strip() or 0) > 0:
                self.update(parent, state="qc", feedback="")
                self.event(parent, "master", "qc_enqueued", "worker claims complete; code review required")
                return
        note = msg or f"worker incomplete: exit={rc}, completed={completed}, parent unchecked or no commit"
        attempts = row["worker_attempts"] + 1
        self.update(parent, state="waiting", feedback=note, worker_attempts=attempts,
                    queued_at=time.time())
        self.event(parent, "master", "worker_retry", f"attempt {attempts}: {note}")
        if attempts >= self.retry_limit:
            self.rebuild(parent, "WORKER", note)

    def finish_repairer(self, role_row: dict) -> None:
        parent = role_row["parent"]
        row = self.job(parent)
        rc = self.exit_code(role_row["pid"], role_row["logfile"])
        if quota_in_log(role_row["logfile"]):
            self.pause_quota(parent, "repairer")
            return
        _, failed, note = self.saved_usage(parent, role_row["logfile"], "repairer")
        if ENV_BLOCKER.search(note):
            self.update(parent, state="blocked", failure="MODEL_OR_AUTH: " + note[:350])
            self.event(parent, "repairer", "blocked_environment", note[:350])
            return
        try:
            passed, reason = tests_pass(Path(row["worktree"]))
        except (OSError, subprocess.TimeoutExpired) as exc:
            passed, reason = False, type(exc).__name__
        clean = not git("status", "--porcelain", cwd=Path(row["worktree"])).stdout.strip()
        marked = parent_checked(Path(row["worktree"]) / "TASKS.md", parent)
        committed = int(git("rev-list", "--count", f"develop..{row['branch']}", cwd=self.root).stdout or "0") > 0
        if rc == 0 and not failed and passed and clean and marked and committed:
            self.update(parent, state="merge", feedback="", queued_at=time.time())
            self.event(parent, "repairer", "qc_pass", reason)
        else:
            attempts = row["repair_attempts"] + 1
            problems = []
            if rc:
                problems.append(f"repairer exited {rc}")
            if failed:
                problems.append("Codex reported failure")
            if not passed:
                problems.append(reason)
            if not clean:
                problems.append("worker tree has uncommitted changes; commit fixes")
            if not marked:
                problems.append("parent TASKS.md checkbox remains unchecked")
            if not committed:
                problems.append("branch contains no new feature commit")
            problem = ("; ".join(problems) + "; " + (note or ""))[:800]
            self.update(parent, repair_attempts=attempts, feedback=problem, queued_at=time.time())
            self.event(parent, "repairer", "qc_fail", f"attempt {attempts}: {problem}")
            if attempts >= self.retry_limit:
                self.rebuild(parent, "QC", problem)
            else:
                self.update(parent, state="waiting")

    def setup_merge(self, row: dict) -> Path:
        if row["integration_tree"] and Path(row["integration_tree"]).exists():
            return Path(row["integration_tree"])
        n = row["generation"]
        # A new integration tree is created when QC changes the worker branch.
        seq = row["merge_attempts"] + 1
        branch = f"integration-v2/{row['parent']}-g{n}-a{seq}"
        path = self.state / "integrations" / f"{row['parent']}-g{n}-a{seq}"
        path.parent.mkdir(parents=True, exist_ok=True)
        git("worktree", "add", "-b", branch, str(path), "develop", cwd=self.root)
        merge = git("merge", "--no-ff", "--no-commit", row["branch"], cwd=path, check=False)
        self.update(row["parent"], integration_tree=str(path), integration_branch=branch)
        self.event(row["parent"], "master", "integration",
                   f"prepared {branch}; clean_merge={merge.returncode == 0}")
        return path

    def finish_merger(self, role_row: dict) -> None:
        parent = role_row["parent"]
        row = self.job(parent)
        rc = self.exit_code(role_row["pid"], role_row["logfile"])
        if quota_in_log(role_row["logfile"]):
            self.pause_quota(parent, "merger")
            return
        _, failed, msg = self.saved_usage(parent, role_row["logfile"], "merger")
        if ENV_BLOCKER.search(msg):
            self.update(parent, state="blocked", failure="MODEL_OR_AUTH: " + msg[:350])
            self.event(parent, "merger", "blocked_environment", msg[:350])
            return
        integration = Path(row["integration_tree"])
        if "MERGER_NEEDS_QC:" in msg:
            count = row["merge_attempts"] + 1
            self.update(parent, state="qc", feedback=msg[-900:],
                        merge_attempts=count, merger_session="",
                        integration_tree="", integration_branch="", queued_at=time.time())
            self.event(parent, "merger", "qc_requested", msg[-400:])
            if count >= self.retry_limit:
                self.rebuild(parent, "MERGE", "Repeated QC requests from merger: " + msg[-800:])
            return
        try:
            passed, reason = tests_pass(integration)
            unresolved = git("diff", "--name-only", "--diff-filter=U",
                             cwd=integration).stdout.strip()
            if unresolved:
                passed, reason = False, "unresolved conflicts: " + unresolved[:350]
        except (OSError, subprocess.TimeoutExpired) as exc:
            passed, reason = False, type(exc).__name__
        if rc or failed or not passed:
            count = row["merge_attempts"] + 1
            reason = msg or reason or f"merger exit {rc}"
            self.update(parent, merge_attempts=count, feedback=reason[-800:],
                        state="merge", queued_at=time.time())
            self.event(parent, "merger", "merge_fail", f"attempt {count}: {reason[:400]}")
            if count >= self.retry_limit:
                self.rebuild(parent, "MERGE", reason)
            return
        try:
            self.accept_integration(self.job(parent))
        except (RuntimeError, OSError) as exc:
            reason = str(exc)[:800]
            if "develop moved since integration" in reason or "develop working tree is dirty" in reason:
                self.update(parent, state="blocked", failure=reason)
                self.event(parent, "master", "external_merge_blocker", reason)
                return
            count = row["merge_attempts"] + 1
            self.update(parent, merge_attempts=count, feedback=reason,
                        state="merge", queued_at=time.time())
            self.event(parent, "merger", "merge_gate_failed", f"attempt {count}: {reason}")
            if count >= self.retry_limit:
                self.rebuild(parent, "MERGE", reason)

    def accept_integration(self, row: dict) -> None:
        parent = row["parent"]
        path = Path(row["integration_tree"])
        has_merge = git("rev-parse", "-q", "--verify", "MERGE_HEAD", cwd=path, check=False).returncode == 0
        if has_merge:
            # Commit only already staged, independently tested merge content.
            git("commit", "-m", f"master: merge verified {parent}", cwd=path)
        else:
            if git("merge-base", "--is-ancestor", row["branch"], "HEAD",
                   cwd=path, check=False).returncode:
                raise RuntimeError("integration no longer contains the worker branch")
        if git("status", "--porcelain", cwd=path).stdout.strip():
            raise RuntimeError("integration worktree dirty; manual review required")
        logged, detail = deleted_sources_logged(path)
        if not logged:
            raise RuntimeError(detail)
        if git("status", "--porcelain", cwd=self.root).stdout.strip():
            raise RuntimeError("develop working tree is dirty; refusing merge")
        current = git("rev-parse", "HEAD", cwd=self.root).stdout.strip()
        base = git("merge-base", row["integration_branch"], "develop",
                   cwd=self.root).stdout.strip()
        if current != base:
            raise RuntimeError("develop moved since integration preparation; must rebase")
        git("merge", "--ff-only", row["integration_branch"], cwd=self.root)
        if not parent_checked(self.tasks, parent):
            raise RuntimeError("integration did not finish the parent checkbox")
        self.update(parent, state="done", completed_at=time.time(), feedback="")
        self.event(parent, "master", "merged", git("rev-parse", "--short", "HEAD").stdout.strip())
        self.retire_branch(self.job(parent), "merged")
        if self.push:
            self.checkpoint_push()

    def retire_branch(self, row: dict, reason: str) -> None:
        """Retire a generated Git ref without deleting any physical worktree files."""
        branch, path_text = row["branch"], row["worktree"]
        if not branch or not path_text:
            return
        path = Path(path_text)
        head = git("rev-parse", branch, cwd=self.root, check=False).stdout.strip()
        if not path.is_dir() or git("status", "--porcelain", cwd=path).stdout.strip():
            self.event(row["parent"], "master", "archive",
                       f"kept branch {branch}: dirty or missing worktree; SHA={head}")
            return
        git("switch", "--detach", cwd=path)
        git("branch", "-D", branch, cwd=self.root)
        self.event(row["parent"], "master", "branch_ref_retired",
                   f"{branch} SHA={head} ({reason}); detached files preserved locally")

    def rebuild(self, parent: str, stage: str, error: str) -> None:
        """After the twentieth QC/merge failure, preserve evidence and start fresh."""
        row = self.job(parent)
        report_dir = self.state / "breakdowns"
        report_dir.mkdir(exist_ok=True)
        events = self.rows(
            "SELECT created,actor,kind,detail FROM events WHERE parent=? "
            "AND kind IN ('worker_retry','qc_fail','merge_fail','merge_gate_failed',"
            "'merge_setup_failure','qc_requested') ORDER BY id DESC LIMIT 25",
            (parent,),
        )
        events.reverse()
        history = "\n".join(
            f"- {datetime.fromtimestamp(e['created'], timezone.utc).isoformat()} "
            f"[{e['actor']} / {e['kind']}] {e['detail'][:600]}"
            for e in events
        ) or "- No prior attempt events were recorded."
        differences = git(
            "diff", "--name-only", f"develop...{row['branch']}",
            cwd=self.root, check=False,
        ).stdout.strip() if row["branch"] else ""
        failure = error.lower()
        if "conflict" in failure or stage == "MERGE":
            recommendation = (
                "Extract shared server changes into a small isolated module, "
                "rebase the parent against fresh develop, then verify merged "
                "behavior with targeted integration tests before committing."
            )
        elif "test" in failure or stage == "QC":
            recommendation = (
                "Reproduce the first failing test against fresh develop, "
                "fix the smallest feature slice, and add regression coverage "
                "before repeating the full test suite."
            )
        else:
            recommendation = (
                "Inspect the previous session log for the first root failure, "
                "check Codex session/model compatibility and external dependencies, "
                "and split the feature into independently tested subtasks."
            )
        note = (
            f"# {parent} — {stage} rebuild breakdown\n\n"
            f"UTC: {datetime.now(timezone.utc).isoformat()}\n\n"
            f"- Retired worker branch: {row['branch']}\n"
            f"- Worker generation: {row['generation']}\n"
            f"- Worker retries: {row['worker_attempts']}\n"
            f"- QC failed attempts: {row['repair_attempts']}\n"
            f"- Merge failed attempts: {row['merge_attempts']}\n"
            f"- Worker Codex session: {row['worker_session'] or 'unavailable'}\n"
            f"- Last failure: {error[:1200]}\n"
            f"- Changed tracked files:\n{differences[:1800] or '(none)'}\n\n"
            "## Attempt-by-attempt failure history\n\n"
            f"{history}\n\n"
            "## Supervisor recommendation\n\n"
            f"{recommendation}\n\n"
            "The failed worker branch ref may be retired, but its detached "
            "worktree and Git commit SHA must remain locally recoverable. "
            "A new generation will begin from the current develop branch; "
            "do not delete develop or copy the failed session into that worker.\n"
        )
        report = report_dir / f"{parent}-g{row['generation']}-{stage.lower()}.md"
        report.write_text(note)
        os.chmod(report, 0o600)
        self.event(parent, "master", "rebuild_report", str(report))
        self.retire_branch(row, "failed after 20 attempts")
        self.update(
            parent, state="rebuild", generation=row["generation"] + 1,
            branch="", worktree="", integration_branch="", integration_tree="",
            worker_session="", repair_session="", merger_session="",
            worker_attempts=0, repair_attempts=0, merge_attempts=0,
            rebuilds=row["rebuilds"] + 1,
            feedback=f"fresh rebuild after {stage} 20 attempts; report: {report.name}",
            queued_at=time.time(),
        )

    def checkpoint_push(self) -> str:
        if git("status", "--porcelain", cwd=self.root).stdout.strip():
            return "SKIP: develop dirty"
        if not shutil.which("gitleaks"):
            return "SKIP: gitleaks absent"
        if git("fetch", "origin", "develop", cwd=self.root, check=False).returncode:
            return "SKIP: cannot fetch"
        if git("merge-base", "--is-ancestor", "origin/develop", "HEAD",
               cwd=self.root, check=False).returncode:
            return "SKIP: remote diverged"
        diff = git("diff", "--name-only", "origin/develop..HEAD",
                   cwd=self.root).stdout.splitlines()
        if any(RESTRICTED.search(name) for name in diff):
            return "BLOCK: private file in unpublished diff"
        if git("diff", "--name-status", "origin/develop..HEAD",
               cwd=self.root).stdout.find("D\t") != -1:
            # A deleted repo file needs a matching, reviewed DELETE-LOGS row.
            if not (self.root / "DELETE-LOGS.md").exists():
                return "BLOCK: unlogged repository deletion"
        scan = subprocess.run(
            ["gitleaks", "git", "--redact", "--log-opts=origin/develop..HEAD", "."],
            cwd=self.root, capture_output=True, text=True,
        )
        if scan.returncode:
            return "BLOCK: Gitleaks scan failed"
        ok, reason = tests_pass(self.root)
        if not ok:
            return "BLOCK: " + reason[:120]
        if git("push", "origin", "HEAD:refs/heads/develop",
               cwd=self.root, check=False).returncode:
            return "SKIP: remote push rejected"
        return "PUSHED " + git("rev-parse", "--short", "HEAD").stdout.strip()

    def reap(self) -> None:
        for row in self.rows("SELECT * FROM jobs WHERE state='running'"):
            if row["worker_pid"] and not alive(row["worker_pid"], row["worker_start_tick"]):
                self.finish_worker(row)
        for role in ("repairer", "merger"):
            r = self.rows("SELECT * FROM roles WHERE name=?", (role,))[0]
            if r["state"] == "running" and r["pid"] and not alive(r["pid"], r["start_tick"]):
                if role == "repairer":
                    self.finish_repairer(r)
                else:
                    self.finish_merger(r)

    def dispatch(self) -> None:
        # Repairer is a single long-running role, NOT one per worker.
        repairer = self.rows("SELECT * FROM roles WHERE name='repairer'")[0]
        if repairer["state"] == "idle":
            row = self.pick(("qc",))
            if row:
                self.start_role("repairer", row, Path(row["worktree"]))
        merger = self.rows("SELECT * FROM roles WHERE name='merger'")[0]
        if merger["state"] == "idle":
            row = self.pick(("merge",))
            if row:
                try:
                    integration = self.setup_merge(row)
                    self.start_role("merger", self.job(row["parent"]), integration)
                except (OSError, RuntimeError) as exc:
                    count = row["merge_attempts"] + 1
                    self.update(row["parent"], merge_attempts=count, feedback=str(exc)[-500:])
                    self.event(row["parent"], "master", "merge_setup_failure", str(exc)[-450:])
                    if count >= self.retry_limit:
                        self.rebuild(row["parent"], "MERGE", str(exc))
        busy = self.rows("SELECT COUNT(*) AS n FROM jobs WHERE state='running'")[0]["n"]
        for _ in range(max(0, self.workers - busy)):
            row = self.pick(("waiting", "rebuild", "pending"))
            if not row:
                break
            try:
                self.start_worker(row)
            except (RuntimeError, OSError) as exc:
                self.update(row["parent"], state="blocked", failure=str(exc)[-500:])
                self.event(row["parent"], "master", "blocked_launch", str(exc)[-450:])

    def pause_quota(self, parent: str, role: str) -> None:
        """Preserve Codex session/tokens and park the job until an owner resumes.

        An exhausted turn is not treated as a worker or QC failure. The stored
        role determines which queue should receive the job after quota reset.
        """
        if role not in {"worker", "repairer", "merger"}:
            raise ValueError("unknown quota-paused role")
        if role == "worker":
            logfile = self.job(parent)["worker_log"]
        else:
            role_row = self.rows("SELECT * FROM roles WHERE name=?", (role,))[0]
            if role_row["parent"] != parent:
                raise RuntimeError("quota role no longer matches the active job")
            logfile = role_row["logfile"]
        self.saved_usage(parent, logfile, role)
        self.event(parent, role, "quota_exhausted", "Codex usage limit; owner-controlled resume required")
        self.update(parent, state="blocked", failure="QUOTA_EXHAUSTED")
        self.db.execute(
            "UPDATE roles SET state='idle',parent='',pid=0,start_tick=0 WHERE name=?",
            (role,),
        )
        marker = self.state / "PAUSED_QUOTA"
        with marker.open("w") as control:
            os.chmod(marker, 0o600)
            control.write(f"{role} {parent}\n")
            control.flush()
            os.fsync(control.fileno())

    def archive_marker(self, path: Path) -> None:
        """Keep control marker history instead of deleting existing files."""
        if not path.exists():
            return
        folder = self.state / "control-marker-history"
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        destination = folder / (
            f"{int(time.time() * 1_000_000)}-{os.getpid()}-{path.name}"
        )
        if destination.exists():
            raise RuntimeError("control marker archive collision")
        path.rename(destination)

    def resume_quota(self) -> str:
        """Owner-requested, crash-recoverable quota resumption.

        A previously blocked worker returns to waiting with its saved session;
        QC and merger return to their own serialized queues. No process starts
        merely by calling resume: the owner must launch the master afterward.
        """
        marker = self.state / "PAUSED_QUOTA"
        if not marker.is_file():
            return "No quota marker; task states unchanged"
        fields = marker.read_text().strip().split()
        if len(fields) != 2:
            raise RuntimeError("invalid quota marker; refusing to change queued tasks")
        role, parent = fields
        if role not in {"worker", "repairer", "merger"} or not re.fullmatch(r"JRV-\d{3}", parent):
            raise RuntimeError("invalid quota marker identity")
        row = self.job(parent)
        destination = {"worker": "waiting", "repairer": "qc", "merger": "merge"}[role]
        if row["state"] == "blocked" and row["failure"] == "QUOTA_EXHAUSTED":
            self.update(
                parent, state=destination, failure="", queued_at=time.time(),
                feedback=(row["feedback"] or f"Resume {role} after owner-confirmed quota reset"),
            )
            self.event(parent, "supervisor", "quota_resumed", f"{role} -> {destination}")
        elif row["state"] != destination or row["failure"] == "QUOTA_EXHAUSTED":
            raise RuntimeError("quota job state changed; refusing ambiguous resume")
        # Archiving is not file deletion, and an interrupted archive can be
        # retried without putting the job into the wrong queue.
        self.archive_marker(marker)
        return f"Resumed {parent} into {destination}; previous Codex session retained"

    def stop_children(self) -> None:
        for row in self.rows("SELECT worker_pid AS pid,worker_start_tick AS tick FROM jobs WHERE state='running'"):
            if alive(row["pid"], row["tick"]):
                try:
                    os.killpg(row["pid"], signal.SIGTERM)
                except ProcessLookupError:
                    pass
        for row in self.rows("SELECT pid,start_tick AS tick FROM roles WHERE state='running'"):
            if alive(row["pid"], row["tick"]):
                try:
                    os.killpg(row["pid"], signal.SIGTERM)
                except ProcessLookupError:
                    pass

    def tick(self) -> None:
        self.ingest_submissions()
        self.ingest()
        self.reap()
        self.dispatch()

    def run(self, poll: int = 3, once: bool = False) -> int:
        self.validate()
        stop = self.state / "STOP"
        lock = self.state / "master.lock"
        with lock.open("w") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("Another v2 master is already running")
                return 2
            try:
                self.db.execute(
                    "UPDATE roles SET state='running',started=? WHERE name='master'", (time.time(),)
                )
                while True:
                    if (self.state / "PAUSED_QUOTA").exists():
                        print("QUOTA_EXHAUSTED: paused without restarting Codex")
                        self.stop_children()
                        return 4
                    if stop.exists():
                        print("Owner STOP received; signalling active jobs")
                        self.stop_children()
                        return 130
                    self.tick()
                    rows = self.rows("SELECT state,COUNT(*) AS n FROM jobs GROUP BY state")
                    counts = {x["state"]: x["n"] for x in rows}
                    print("WORKHORSE v2", counts, flush=True)
                    if once:
                        return 0
                    if counts and all(k == "done" for k in counts):
                        completed, total = checkbox_progress(self.tasks.read_text())
                        if completed != total:
                            print(f"PAUSED_NEEDS_HUMAN: {total-completed} unchecked "
                                  "non-parent/acceptance tasks still require mapping")
                            return 6
                        return 0
                    if counts and not any(counts.get(s, 0) for s in
                                          ("pending", "waiting", "rebuild", "running",
                                           "qc", "repairing", "merge", "merging")):
                        print("PAUSED_NEEDS_HUMAN: all remaining tasks blocked")
                        return 6
                    time.sleep(max(1, poll))
            except KeyboardInterrupt:
                self.stop_children()
                return 130

    def close(self) -> None:
        for handle in self.guard_handles:
            handle.close()
        self.guard_handles.clear()
        self.db.close()


def dashboard(master: Master) -> str:
    roles = master.rows("SELECT * FROM roles ORDER BY name")
    jobs = master.rows("SELECT * FROM jobs ORDER BY priority,queued_at,parent")
    task_text = master.tasks.read_text()
    ledger = task_rows(task_text)
    checked, total = checkbox_progress(task_text)
    parent_checked_count = sum(done for _, _, done in ledger)
    lines = [
        "JARVIS WORKHORSE V2 | UTC " + datetime.now(timezone.utc).strftime("%H:%M:%S"),
        f"TASKS.md all items: {checked}/{total} done ({(100*checked/total if total else 0):.1f}%)",
        f"Parent tasks: {parent_checked_count}/{len(ledger)}",
        f"Token usage (recorded): {sum(j['input_tokens'] for j in jobs):,} input / "
        f"{sum(j['output_tokens'] for j in jobs):,} output",
        "ROLES: Supervisor=interactive Codex | Master=local Python coordinator",
    ]
    for r in roles:
        elapsed = f"{int(time.time()-r['started'])}s" if r["state"] == "running" else "-"
        lines.append(f"  {r['name']:<9} {r['state']:<9} {r['parent']:<8} elapsed={elapsed} "
                     f"tokens={r['total_input'] + r['total_output']:,}")
    for title, state in [("RUNNING (max 5)", "running"), ("WAITING (QC returns first)", "waiting"),
                         ("QC/CI QUEUE", "qc"), ("MERGE QUEUE", "merge"),
                         ("REBUILD PRIORITY", "rebuild"), ("PENDING", "pending")]:
        selection = [j for j in jobs if j["state"] == state]
        lines.append(f"{title}: {len(selection)}")
        for j in selection[:10]:
            sec = int(time.time()-j["worker_started"]) if state == "running" else 0
            lines.append(f"  {j['parent']:<8} P{j['priority']} g{j['generation']} "
                         f"qc={j['repair_attempts']}/{master.retry_limit} "
                         f"merge={j['merge_attempts']}/{master.retry_limit} "
                         f"runtime={sec}s tokens={j['input_tokens']+j['output_tokens']:,}")
    blocked = [j for j in jobs if j["state"] == "blocked"]
    lines.append(f"BLOCKED: {len(blocked)} | DONE: {sum(j['state']=='done' for j in jobs)}")
    for j in blocked[:6]:
        lines.append(f"  {j['parent']}: {j['failure'][:120]}")
    lines.append("Ctrl+C stops the dashboard only; use 'stop' command for master.")
    return "\n".join(lines)


def cli() -> int:
    parser = argparse.ArgumentParser(description="JARVIS multi-role Codex workhorse v2")
    sub = parser.add_subparsers(dest="command")
    start = sub.add_parser("run")
    start.add_argument("--workers", type=int, default=5)
    start.add_argument("--poll", type=int, default=3)
    start.add_argument("--push", action="store_true")
    start.add_argument("--once", action="store_true")
    start.add_argument("--repair-attempts", type=int, default=20)
    status = sub.add_parser("status")
    status.add_argument("--watch", type=float, default=0)
    sub.add_parser("stop")
    sub.add_parser("resume")
    submit = sub.add_parser("submit", help="submit parent requirement without editing develop")
    submit.add_argument("--title", required=True)
    submit.add_argument("--priority", type=int, default=1)
    submit.add_argument("--acceptance", required=True)
    submit.add_argument("--done-when", required=True)
    args = parser.parse_args()
    if args.command == "submit":
        title = require_one_line(args.title, 260)
        done = require_one_line(args.done_when, 300)
        if not 0 <= args.priority <= 4 or not re.fullmatch(r"AC-\d{2}", args.acceptance):
            parser.error("priority must be 0..4 and acceptance must be AC-NN")
        inbox = STATE / "inbox"
        inbox.mkdir(parents=True, exist_ok=True, mode=0o700)
        token = secrets.token_hex(12)
        payload = {"submission_id": token, "priority": args.priority,
                   "acceptance": args.acceptance, "title": title, "done_when": done}
        target = inbox / (token + ".json")
        with target.open("x") as handle:
            os.chmod(target, 0o600)
            json.dump(payload, handle, indent=2)
        print("SUPERVISOR REQUIREMENT QUEUED:", token, title)
        return 0
    if args.command == "stop":
        STATE.mkdir(parents=True, exist_ok=True)
        (STATE / "STOP").write_text("owner requested stop\n")
        print("STOP written; coordinator will signal child sessions")
        return 0
    if args.command == "resume":
        # Resume must not race a live master. Keep all control markers in an
        # archive rather than silently deleting them.
        STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (STATE / "master.lock").open("a") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                print("Master is running; stop it before requesting quota resume")
                return 2
            m = Master()
            try:
                print(m.resume_quota())
                m.archive_marker(STATE / "STOP")
            finally:
                m.close()
        print("Control markers archived; owner may restart master after quota reset")
        return 0
    if args.command not in {"run", "status"}:
        parser.print_help()
        return 2
    m = Master(workers=getattr(args, "workers", 5),
               push=getattr(args, "push", False),
               retry_limit=getattr(args, "repair_attempts", 20))
    try:
        if args.command == "run":
            if args.repair_attempts != 20:
                parser.error("the owner requires exactly 20 QC/merge attempts")
            return m.run(poll=args.poll, once=args.once)
        while True:
            print("\033[2J\033[H" + dashboard(m), flush=True)
            if args.watch <= 0:
                return 0
            time.sleep(max(0.5, args.watch))
    finally:
        m.close()


if __name__ == "__main__":
    raise SystemExit(cli())
