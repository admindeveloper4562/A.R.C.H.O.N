"""Deterministic durable Core task queue: no AI model and no external effects."""
from __future__ import annotations
import json
import re
import sqlite3
from pathlib import Path
from uuid import uuid4

from .dependency import DependencyOrchestrator
from .control import CoreControls
from .dispatch import DispatchStore
from .event_session import EventSessionInterpreter
from .intent import OwnerIntentRouter
from .session import TaskSessionStore
from .timeline import TaskTimeline

PRIORITIES = ("P0", "P1", "P2", "P3", "P4", "P5")
STATES = ("pending", "leased", "blocked", "completed", "failed", "cancelled")
MAX_HISTORY_ENTRIES = 100
MAX_EVENT_BATCH = 100
_CONSUMER = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
_REASON = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")

class TaskQueue:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, priority INTEGER NOT NULL, module TEXT NOT NULL,
                payload TEXT NOT NULL, state TEXT NOT NULL,
                created_id INTEGER NOT NULL UNIQUE,
                lease TEXT, receipt TEXT, title TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
                kind TEXT NOT NULL, detail TEXT NOT NULL,
                event_id TEXT NOT NULL DEFAULT '', session_id TEXT NOT NULL DEFAULT '',
                correlation_id TEXT NOT NULL DEFAULT '', causation_id TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(task_id) REFERENCES tasks(id));
            CREATE TABLE IF NOT EXISTS event_receipts (
                consumer TEXT NOT NULL, seq INTEGER NOT NULL,
                acknowledged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (consumer, seq),
                FOREIGN KEY(seq) REFERENCES events(seq));
        """)
        # The task ledger owns schema migrations; the separate monitor never writes.
        # A non-secret title lets the monitor describe work without reading payload.
        if 'title' not in {r['name'] for r in self.db.execute('PRAGMA table_info(tasks)')}:
            self.db.execute("ALTER TABLE tasks ADD COLUMN title TEXT NOT NULL DEFAULT ''")
        self.db.commit()
        self.event_session = EventSessionInterpreter(self.db)
        self.controls = CoreControls(self.db)
        self.events = self.event_session
        self.sessions = TaskSessionStore(self.db)
        self.dispatches = DispatchStore(self.db)
        self.dependencies = DependencyOrchestrator(self.db)
        self.intents = OwnerIntentRouter(self.db, queue=self)
        self.timeline_view = TaskTimeline(self.db)

    def add(self, *, task_id: str, priority: str, module: str, payload: dict, title: str = '') -> None:
        if (priority not in PRIORITIES or not task_id or not module or not isinstance(payload, dict)
                or not isinstance(title, str) or len(title) > 180 or any(ord(c) < 32 for c in title)):
            raise ValueError("invalid task input")
        with self.db:
            seq = self.db.execute("SELECT COALESCE(MAX(created_id),0)+1 FROM tasks").fetchone()[0]
            self.db.execute("INSERT INTO tasks (id,priority,module,payload,state,created_id,lease,receipt,title) VALUES (?,?,?,?,?,?,?,?,?)", (task_id, PRIORITIES.index(priority), module, json.dumps(payload,sort_keys=True), "pending", seq, None, None, title))
            self._emit_event(task_id, "pending", "queued")

    def block(self, task_id: str, *, reason: str, lease: str | None = None) -> None:
        """Fence pending or leased work without allowing a stale owner to block it."""
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id required")
        if not isinstance(reason, str) or not _REASON.fullmatch(reason):
            raise ValueError("invalid block reason")
        if lease is not None and (not isinstance(lease, str) or not lease):
            raise ValueError("invalid lease")
        expected_state = "leased" if lease is not None else "pending"
        with self.db:
            if lease is None:
                result = self.db.execute(
                    "UPDATE tasks SET state='blocked',lease=NULL WHERE id=? AND state=?",
                    (task_id, expected_state),
                )
            else:
                result = self.db.execute(
                    "UPDATE tasks SET state='blocked',lease=NULL WHERE id=? AND state=? AND lease=?",
                    (task_id, expected_state, lease),
                )
            if result.rowcount != 1:
                raise ValueError("unknown or stale task")
            self._emit_event(task_id, "blocked", reason)

    def unblock(self, task_id: str) -> None:
        """Return one blocked task to the pending queue with an audit event."""
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id required")
        with self.db:
            result = self.db.execute(
                "UPDATE tasks SET state='pending' WHERE id=? AND state='blocked'",
                (task_id,),
            )
            if result.rowcount != 1:
                raise ValueError("task is not blocked")
            self._emit_event(task_id, "pending", "unblocked")

    def lease_next(self, *, guardian_waiting: bool = False, allowed_modules: set[str] | None = None) -> dict | None:
        """Dispatch the highest-priority pending task with completed dependencies."""
        if not self.controls.allows_dispatch():
            return None
        where = "state='pending'"
        args: list[str] = []
        if guardian_waiting:
            where += " AND priority <= 1"
        if allowed_modules is not None:
            if not allowed_modules: return None
            where += " AND module IN (" + ",".join("?" for _ in allowed_modules) + ")"
            args.extend(sorted(allowed_modules))
        with self.db:
            rows = self.db.execute(f"SELECT * FROM tasks WHERE {where} ORDER BY priority,created_id", args).fetchall()
            row = next(
                (candidate for candidate in rows if self.dependencies.ready(json.loads(candidate["payload"]))),
                None,
            )
            if row is None:return None
            lease = uuid4().hex
            updated = self.db.execute(
                "UPDATE tasks SET state='leased',lease=? WHERE id=? AND state='pending' "
                "AND (SELECT state FROM core_controls WHERE control_id=1)='running'",
                (lease, row["id"],),
            )
            if updated.rowcount != 1:
                return None
            self._emit_event(row["id"], "leased", lease)
            return {"id":row["id"],"priority":PRIORITIES[row["priority"]],"module":row["module"],"payload":json.loads(row["payload"]),"lease":lease}

    def eligible(self, *, guardian_waiting: bool = False, allowed_modules: set[str] | None = None) -> list[dict]:
        """Return a read-only, priority/FIFO ordered ready frontier."""
        where = "state='pending'"
        args: list[str] = []
        if guardian_waiting:
            where += " AND priority <= 1"
        if allowed_modules is not None:
            if not allowed_modules:
                return []
            where += " AND module IN (" + ",".join("?" for _ in allowed_modules) + ")"
            args.extend(sorted(allowed_modules))
        rows = self.db.execute(f"SELECT * FROM tasks WHERE {where} ORDER BY priority,created_id", args)
        return [
            {"id": row["id"], "priority": PRIORITIES[row["priority"]], "module": row["module"], "payload": json.loads(row["payload"])}
            for row in rows
            if self.dependencies.ready(json.loads(row["payload"]))
        ]

    def finish(self, task_id: str, lease: str, *, ok: bool, receipt: str) -> None:
        if not isinstance(receipt,str) or not receipt or not isinstance(lease,str): raise ValueError("receipt and lease required")
        with self.db:
            res=self.db.execute("UPDATE tasks SET state=?,receipt=?,lease=NULL WHERE id=? AND state='leased' AND lease=?", ("completed" if ok else "failed", receipt, task_id,lease))
            if res.rowcount!=1: raise ValueError("unknown or stale lease")
            self._emit_event(task_id, "completed" if ok else "failed", receipt)

    def status(self) -> list[dict]:
        return [dict(row) for row in self.db.execute("SELECT id,priority,module,state,receipt FROM tasks ORDER BY created_id")]

    def history(self, task_id: str, *, limit: int = MAX_HISTORY_ENTRIES) -> list[dict]:
        """Return bounded, chronological, non-sensitive event metadata for a task."""
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("task_id required")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("limit must be a positive integer")
        limit = min(limit, MAX_HISTORY_ENTRIES)
        rows = self.db.execute(
            "SELECT seq, task_id, kind FROM events WHERE task_id=? ORDER BY seq LIMIT ?",
            (task_id, limit),
        )
        return [dict(row) for row in rows]

    def replay_events(self, consumer: str, *, limit: int = MAX_EVENT_BATCH) -> list[dict]:
        """Return unacknowledged event metadata in durable sequence order."""
        if not isinstance(consumer, str) or not _CONSUMER.fullmatch(consumer):
            raise ValueError("invalid event consumer")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("limit must be a positive integer")
        limit = min(limit, MAX_EVENT_BATCH)
        rows = self.db.execute(
            "SELECT e.seq, e.task_id, e.kind FROM events e "
            "WHERE NOT EXISTS (SELECT 1 FROM event_receipts r "
            "WHERE r.consumer=? AND r.seq=e.seq) ORDER BY e.seq LIMIT ?",
            (consumer, limit),
        )
        return [dict(row) for row in rows]

    def ack_event(self, consumer: str, seq: int) -> None:
        """Durably acknowledge one event; repeated acknowledgements are safe."""
        if not isinstance(consumer, str) or not _CONSUMER.fullmatch(consumer):
            raise ValueError("invalid event consumer")
        if type(seq) is not int or seq < 1:
            raise ValueError("event sequence must be a positive integer")
        with self.db:
            if self.db.execute("SELECT 1 FROM events WHERE seq=?", (seq,)).fetchone() is None:
                raise ValueError("unknown event")
            self.db.execute(
                "INSERT OR IGNORE INTO event_receipts(consumer,seq) VALUES (?,?)",
                (consumer, seq),
            )

    def open_session(self, task_id: str, **kwargs) -> dict:
        return self.sessions.open_session(task_id, **kwargs)

    def _emit_event(self, task_id: str, kind: str, detail: str) -> dict:
        return self.event_session.emit(task_id, kind, detail)

    def restore_session(self, task_id: str | None = None, *, session_id: str | None = None) -> dict:
        return self.sessions.restore_session(task_id, session_id=session_id)

    def record_decision(self, session_id: str, decision_id: str, decision: dict) -> dict:
        return self.sessions.record_decision(session_id, decision_id, decision)

    def record_handoff(self, session_id: str, handoff_id: str, handoff: dict) -> dict:
        return self.sessions.record_handoff(session_id, handoff_id, handoff)

    def record_receipt(self, session_id: str, effect_id: str, receipt: dict) -> dict:
        return self.sessions.record_receipt(session_id, effect_id, receipt)

    def checkpoint_session(self, session_id: str, **kwargs) -> dict:
        return self.sessions.checkpoint_session(session_id, **kwargs)

    def dispatch(self, task_id: str, target_module: str, scope, acceptance, **kwargs) -> dict:
        return self.dispatches.create(task_id, target_module, scope, acceptance, **kwargs)

    def claim_dispatch(self, dispatch_id: str, executor_id: str, **kwargs) -> dict:
        return self.dispatches.claim(dispatch_id, executor_id, **kwargs)

    def acknowledge_dispatch(self, dispatch_id: str, executor_id: str, claim_id: str, **kwargs) -> dict:
        return self.dispatches.acknowledge(dispatch_id, executor_id, claim_id, **kwargs)

    def restore_dispatch(self, dispatch_id: str) -> dict:
        return self.dispatches.get(dispatch_id)

    def submit_intent(self, intent: dict, *, approval: dict | None = None) -> dict:
        return self.intents.submit(intent, approval=approval)

    def control_status(self) -> dict[str, str]:
        return self.controls.status()

    def stop(self, *, reason: str = "owner_stop") -> dict[str, str]:
        return self.controls.stop(reason=reason)

    def pause(self, *, reason: str = "owner_pause") -> dict[str, str]:
        return self.controls.pause(reason=reason)

    def resume(self) -> dict[str, str]:
        return self.controls.resume()

    def timeline(self, task_id: str, *, limit: int = MAX_EVENT_BATCH) -> dict:
        return self.timeline_view.timeline(task_id, limit=limit)

    def progress(self, task_id: str) -> dict:
        return self.timeline_view.progress(task_id)

    def close(self): self.db.close()
