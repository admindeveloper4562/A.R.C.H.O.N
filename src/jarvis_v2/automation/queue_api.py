"""Versioned local adapter for the ARCHON coordinator queue.

The coordinator queue is a protocol boundary, not a second task ledger.  The
ATLAS ``TaskQueue`` remains authoritative; this module gives callers a stable
versioned envelope and reopens its existing SQLite format without rewriting it.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Callable, Mapping

from jarvis_v2.core.queue import PRIORITIES, TaskQueue


SCHEMA = "archon-coordinator-queue/1"
LEGACY_SCHEMA = "atlas-task-queue/1"
MAX_PAYLOAD_BYTES = 32_768
DEFAULT_LEASE_SECONDS = 60
MAX_LEASE_SECONDS = 3_600
MAX_LEASE_ATTEMPTS = 3
_TASK_COLUMNS = {"id", "priority", "module", "payload", "state", "created_id", "lease", "receipt"}
_EVENT_COLUMNS = {"seq", "task_id", "kind", "detail"}


class QueueSchemaError(ValueError):
    """Raised when a queue envelope or existing queue is incompatible."""


class QueueApiError(ValueError):
    """Raised for invalid queue operations without changing queue state."""


def _text(value: Any, name: str, limit: int) -> str:
    if not isinstance(value, str) or not value or len(value) > limit or any(ord(c) < 32 for c in value):
        raise QueueSchemaError(f"invalid {name}")
    return value


def _payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise QueueSchemaError("payload must be an object")
    result = dict(value)
    try:
        encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise QueueSchemaError("payload must be JSON-compatible") from exc
    if len(encoded.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise QueueSchemaError("payload too large")
    return result


@dataclass(frozen=True)
class QueueEnvelope:
    """A versioned task message used by local coordinator callers."""

    task_id: str
    priority: str
    module: str
    payload: dict[str, Any]
    lease: str | None = None

    def __post_init__(self) -> None:
        _text(self.task_id, "task_id", 120)
        if self.priority not in PRIORITIES:
            raise QueueSchemaError("invalid priority")
        _text(self.module, "module", 80)
        _payload(self.payload)
        if self.lease is not None:
            _text(self.lease, "lease", 128)

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "schema": SCHEMA,
            "task_id": self.task_id,
            "priority": self.priority,
            "module": self.module,
            "payload": self.payload,
        }
        if self.lease is not None:
            value["lease"] = self.lease
        return value

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_dict(cls, value: Any) -> "QueueEnvelope":
        if not isinstance(value, Mapping) or value.get("schema") != SCHEMA:
            raise QueueSchemaError("unsupported queue schema")
        allowed = {"schema", "task_id", "priority", "module", "payload", "lease"}
        if set(value) - allowed or set(value) - {"schema", "task_id", "priority", "module", "payload"} and "lease" not in value:
            raise QueueSchemaError("invalid queue envelope fields")
        return cls(
            task_id=value.get("task_id"),
            priority=value.get("priority"),
            module=value.get("module"),
            payload=value.get("payload"),
            lease=value.get("lease"),
        )

    @classmethod
    def loads(cls, value: str) -> "QueueEnvelope":
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError) as exc:
            raise QueueSchemaError("invalid queue JSON") from exc
        return cls.from_dict(parsed)


def detect_schema(path: Path) -> str:
    """Identify the supported legacy queue layout without modifying it."""

    path = Path(path)
    if not path.exists():
        return "new"
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
            tables = {row[0] for row in db.execute("select name from sqlite_master where type='table'")}
            if not {"tasks", "events"}.issubset(tables):
                raise QueueSchemaError("unsupported queue database")
            task_columns = {row[1] for row in db.execute("pragma table_info(tasks)")}
            event_columns = {row[1] for row in db.execute("pragma table_info(events)")}
    except sqlite3.Error as exc:
        raise QueueSchemaError("unreadable queue database") from exc
    if not _TASK_COLUMNS.issubset(task_columns) or not _EVENT_COLUMNS.issubset(event_columns):
        raise QueueSchemaError("unsupported queue database")
    return LEGACY_SCHEMA


class CoordinatorQueue:
    """Small versioned facade over the existing durable ATLAS queue."""

    def __init__(
        self,
        queue: TaskQueue,
        *,
        source_schema: str = "new",
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._queue = queue
        self.source_schema = source_schema
        self._clock = clock or time.time
        with self._queue.db:
            columns = {row[1] for row in self._queue.db.execute("pragma table_info(tasks)")}
            if "lease_expires_at" not in columns:
                self._queue.db.execute(
                    "alter table tasks add column lease_expires_at real not null default 0"
                )

    @classmethod
    def open(cls, path: Path, *, clock: Callable[[], float] | None = None) -> "CoordinatorQueue":
        path = Path(path)
        source_schema = detect_schema(path)
        return cls(TaskQueue(path), source_schema=source_schema, clock=clock)

    def enqueue(self, *, task_id: str, priority: str, module: str, payload: Mapping[str, Any]) -> QueueEnvelope:
        envelope = QueueEnvelope(task_id, priority, module, dict(payload))
        if any(row["id"] == task_id for row in self._queue.status()):
            raise QueueApiError("task already exists")
        try:
            self._queue.add(task_id=task_id, priority=priority, module=module, payload=envelope.payload)
        except sqlite3.IntegrityError as exc:
            raise QueueApiError("task already exists") from exc
        return envelope

    @staticmethod
    def _lease_seconds(value: int) -> int:
        if type(value) is not int or not 1 <= value <= MAX_LEASE_SECONDS:
            raise QueueApiError("lease duration is outside the bounded policy")
        return value

    def _requeue_expired(self) -> int:
        now = self._clock()
        attempts = "(SELECT count(*) FROM events e WHERE e.task_id=tasks.id AND e.kind='leased')"
        rows = self._queue.db.execute(
            f"SELECT id,state,{attempts} AS attempts FROM tasks "
            "WHERE (state='leased' AND lease_expires_at > 0 AND lease_expires_at <= ?) "
            f"OR (state='pending' AND {attempts} >= ?)",
            (now, MAX_LEASE_ATTEMPTS),
        ).fetchall()
        changed = 0
        with self._queue.db:
            for row in rows:
                if row["attempts"] >= MAX_LEASE_ATTEMPTS:
                    receipt = sha256(f"{row['id']}:lease_attempt_limit".encode()).hexdigest()
                    updated = self._queue.db.execute(
                        "UPDATE tasks SET state='failed',lease=NULL,lease_expires_at=0,receipt=? "
                        "WHERE id=? AND state=? AND (state='pending' OR lease_expires_at <= ?)",
                        (receipt, row["id"], row["state"], now),
                    )
                    if updated.rowcount:
                        self._queue._emit_event(row["id"], "failed", "lease_attempt_limit")
                        changed += 1
                else:
                    updated = self._queue.db.execute(
                        "UPDATE tasks SET state='pending',lease=NULL,lease_expires_at=0 "
                        "WHERE id=? AND state='leased' AND lease_expires_at > 0 AND lease_expires_at <= ?",
                        (row["id"], now),
                    )
                    if updated.rowcount:
                        self._queue._emit_event(row["id"], "pending", "lease_expired")
                        changed += 1
        return changed

    def lease_next(
        self,
        *,
        guardian_waiting: bool = False,
        allowed_modules: set[str] | None = None,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
    ) -> QueueEnvelope | None:
        lease_seconds = self._lease_seconds(lease_seconds)
        self._requeue_expired()
        leased = self._queue.lease_next(guardian_waiting=guardian_waiting, allowed_modules=allowed_modules)
        if leased is None:
            return None
        with self._queue.db:
            self._queue.db.execute(
                "update tasks set lease_expires_at=? where id=? and state='leased' and lease=?",
                (self._clock() + lease_seconds, leased["id"], leased["lease"]),
            )
        return QueueEnvelope(leased["id"], leased["priority"], leased["module"], leased["payload"], leased["lease"])

    def eligible(self, *, guardian_waiting: bool = False, allowed_modules: set[str] | None = None) -> list[QueueEnvelope]:
        """Return ready work without claiming it."""
        self._requeue_expired()
        return [
            QueueEnvelope(row["id"], row["priority"], row["module"], row["payload"])
            for row in self._queue.eligible(guardian_waiting=guardian_waiting, allowed_modules=allowed_modules)
        ]

    def release(self, item: QueueEnvelope, *, reason: str = "dispatch_deferred") -> None:
        """Return a leased item to pending after a bounded handoff failure."""
        if not item.lease:
            raise QueueApiError("leased item required")
        if not isinstance(reason, str) or not reason or len(reason) > 80 or any(
            not (char.isalnum() or char in "_.:-") for char in reason
        ):
            raise QueueApiError("invalid release reason")
        with self._queue.db:
            updated = self._queue.db.execute(
                "update tasks set state='pending',lease=null,lease_expires_at=0 "
                "where id=? and state='leased' and lease=?",
                (item.task_id, item.lease),
            )
            if updated.rowcount != 1:
                raise QueueApiError("unknown or stale lease")
            self._queue._emit_event(item.task_id, "pending", reason)


    def cancel(self, task_id: str) -> dict[str, str]:
        if not isinstance(task_id, str) or not task_id or len(task_id) > 120:
            raise QueueApiError("invalid task id")
        receipt = sha256(f"{task_id}:cancelled".encode()).hexdigest()
        with self._queue.db:
            row = self._queue.db.execute(
                "SELECT state,receipt FROM tasks WHERE id=?", (task_id,)
            ).fetchone()
            if row is None:
                raise QueueApiError("unknown task")
            if row["state"] == "cancelled":
                return {"task_id": task_id, "state": "cancelled", "receipt": row["receipt"]}
            if row["state"] != "pending":
                raise QueueApiError("only pending tasks can be cancelled")
            updated = self._queue.db.execute(
                "UPDATE tasks SET state='cancelled',receipt=? WHERE id=? AND state='pending'",
                (receipt, task_id),
            )
            if updated.rowcount != 1:
                raise QueueApiError("task changed before cancellation")
            self._queue._emit_event(task_id, "cancelled", receipt)
        return {"task_id": task_id, "state": "cancelled", "receipt": receipt}

    def renew(self, item: QueueEnvelope, *, lease_seconds: int = DEFAULT_LEASE_SECONDS) -> QueueEnvelope:
        if not item.lease:
            raise QueueApiError("leased item required")
        lease_seconds = self._lease_seconds(lease_seconds)
        row = self._queue.db.execute(
            "select state,lease,lease_expires_at from tasks where id=?", (item.task_id,)
        ).fetchone()
        if row is None or row["state"] != "leased" or row["lease"] != item.lease:
            raise QueueApiError("unknown or stale lease")
        if row["lease_expires_at"] <= self._clock():
            self._requeue_expired()
            raise QueueApiError("lease has expired")
        with self._queue.db:
            self._queue.db.execute(
                "update tasks set lease_expires_at=? where id=? and state='leased' and lease=?",
                (self._clock() + lease_seconds, item.task_id, item.lease),
            )
        return item

    def complete(self, item: QueueEnvelope, *, ok: bool, receipt: str) -> dict[str, Any]:
        if not item.lease:
            raise QueueApiError("leased item required")
        row = self._queue.db.execute(
            "select state,lease,receipt,lease_expires_at from tasks where id=?", (item.task_id,)
        ).fetchone()
        if row is None:
            raise QueueApiError("unknown task")
        if row["state"] in {"completed", "failed", "cancelled"}:
            if row["receipt"] == receipt and row["state"] == ("completed" if ok else "failed"):
                return {"task_id": item.task_id, "state": row["state"], "receipt": receipt}
            raise QueueApiError("task is already finalized")
        if row["lease"] != item.lease or row["state"] != "leased":
            raise QueueApiError("unknown or stale lease")
        if row["lease_expires_at"] <= self._clock():
            self._requeue_expired()
            raise QueueApiError("lease has expired")
        self._queue.finish(item.task_id, item.lease, ok=ok, receipt=receipt)
        with self._queue.db:
            self._queue.db.execute("update tasks set lease_expires_at=0 where id=?", (item.task_id,))
        return {"task_id": item.task_id, "state": "completed" if ok else "failed", "receipt": receipt}

    def status(self) -> list[dict[str, Any]]:
        return self._queue.status()

    def control_status(self) -> dict[str, str]:
        """Expose durable owner controls without leaking the queue implementation."""
        return self._queue.control_status()

    def history(self, task_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        return self._queue.history(task_id, limit=limit)

    def close(self) -> None:
        self._queue.close()

    def __enter__(self) -> "CoordinatorQueue":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
