"""Bounded durable logical sessions for Core parent tasks."""
from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Mapping
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4


SESSION_STATUSES = frozenset({"active", "paused", "completed", "failed"})
RECORD_KINDS = frozenset({"decision", "handoff", "receipt", "checkpoint"})
MAX_CONTEXT_BYTES = 32 * 1024
MAX_RECORD_BYTES = 16 * 1024
MAX_SESSION_RECORDS = 1_000
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class SessionError(ValueError):
    """Raised when a session input would violate the durable contract."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SessionError(f"invalid {label}")
    return value


def _json(value: Mapping[str, object], *, limit: int, label: str) -> str:
    if not isinstance(value, Mapping):
        raise SessionError(f"{label} must be an object")
    try:
        encoded = json.dumps(
            dict(value),
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise SessionError(f"{label} must be JSON serializable") from exc
    if len(encoded.encode("utf-8")) > limit:
        raise SessionError(f"{label} exceeds bounded size")
    return encoded


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class TaskSessionStore:
    """Persist one reconstructable logical session for each parent task.

    The store accepts an existing SQLite connection so Core sessions share the
    queue's authoritative database. Callers should store references and
    redacted metadata, not raw prompts, secrets or unbounded model output.
    """

    def __init__(self, database: Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        if self._owns_connection:
            self.db = sqlite3.connect(Path(database))
        else:
            self.db = database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS task_sessions (
                session_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL UNIQUE,
                correlation_id TEXT NOT NULL,
                status TEXT NOT NULL,
                context TEXT NOT NULL,
                checkpoint TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS task_session_records (
                record_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                kind TEXT NOT NULL,
                idempotency_key TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES task_sessions(session_id) ON DELETE CASCADE,
                UNIQUE(session_id, sequence),
                UNIQUE(session_id, kind, idempotency_key)
            );
            CREATE INDEX IF NOT EXISTS idx_task_session_records_session
                ON task_session_records(session_id, sequence);
            """
        )
        self.db.commit()

    def open_session(
        self,
        task_id: str,
        *,
        session_id: str | None = None,
        correlation_id: str | None = None,
        context: Mapping[str, object] | None = None,
    ) -> dict:
        """Create or reopen the one durable session belonging to ``task_id``."""
        task_id = _identifier(task_id, "task_id")
        if session_id is not None:
            session_id = _identifier(session_id, "session_id")
        if correlation_id is not None:
            correlation_id = _identifier(correlation_id, "correlation_id")
        context_json = _json(
            {} if context is None else context,
            limit=MAX_CONTEXT_BYTES,
            label="context",
        )
        now = _now()

        with self.db:
            row = self.db.execute(
                "SELECT * FROM task_sessions WHERE task_id=?", (task_id,)
            ).fetchone()
            if row is not None:
                if session_id is not None and row["session_id"] != session_id:
                    raise SessionError("task already has a different session")
                if correlation_id is not None and row["correlation_id"] != correlation_id:
                    raise SessionError("task already has a different correlation")
                if context is not None and row["context"] != context_json:
                    raise SessionError("task session context conflict")
                return self._snapshot(row)

            session_id = session_id or uuid4().hex
            correlation_id = correlation_id or uuid4().hex
            self.db.execute(
                """INSERT INTO task_sessions
                   (session_id, task_id, correlation_id, status, context, checkpoint,
                    created_at, updated_at)
                   VALUES (?, ?, ?, 'active', ?, '{}', ?, ?)""",
                (session_id, task_id, correlation_id, context_json, now, now),
            )
            return self._snapshot(
                self.db.execute(
                    "SELECT * FROM task_sessions WHERE session_id=?", (session_id,)
                ).fetchone()
            )

    def restore_session(
        self, task_id: str | None = None, *, session_id: str | None = None
    ) -> dict:
        """Reconstruct a session and all bounded records after a restart."""
        if (task_id is None) == (session_id is None):
            raise SessionError("provide exactly one task_id or session_id")
        if task_id is not None:
            task_id = _identifier(task_id, "task_id")
            row = self.db.execute(
                "SELECT * FROM task_sessions WHERE task_id=?", (task_id,)
            ).fetchone()
        else:
            session_id = _identifier(session_id, "session_id")
            row = self.db.execute(
                "SELECT * FROM task_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
        if row is None:
            raise SessionError("unknown task session")
        return self._snapshot(row)

    def append(
        self,
        session_id: str,
        kind: str,
        payload: Mapping[str, object],
        *,
        idempotency_key: str,
    ) -> dict:
        """Append one bounded record, returning the existing record on replay."""
        session_id = _identifier(session_id, "session_id")
        if not isinstance(kind, str) or kind not in RECORD_KINDS:
            raise SessionError("invalid session record kind")
        idempotency_key = _identifier(idempotency_key, "idempotency_key")
        payload_json = _json(payload, limit=MAX_RECORD_BYTES, label="payload")
        with self.db:
            if self.db.execute(
                "SELECT 1 FROM task_sessions WHERE session_id=?", (session_id,)
            ).fetchone() is None:
                raise SessionError("unknown task session")
            existing = self.db.execute(
                """SELECT * FROM task_session_records
                   WHERE session_id=? AND kind=? AND idempotency_key=?""",
                (session_id, kind, idempotency_key),
            ).fetchone()
            if existing is not None:
                if existing["payload"] != payload_json:
                    raise SessionError("idempotency key payload conflict")
                return self._record(existing)
            count = self.db.execute(
                "SELECT COUNT(*) FROM task_session_records WHERE session_id=?",
                (session_id,),
            ).fetchone()[0]
            if count >= MAX_SESSION_RECORDS:
                raise SessionError("session record limit exceeded")
            sequence = self.db.execute(
                """SELECT COALESCE(MAX(sequence), 0) + 1
                   FROM task_session_records WHERE session_id=?""",
                (session_id,),
            ).fetchone()[0]
            record_id = uuid4().hex
            created_at = _now()
            self.db.execute(
                """INSERT INTO task_session_records
                   (record_id, session_id, sequence, kind, idempotency_key,
                    payload, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (record_id, session_id, sequence, kind, idempotency_key, payload_json, created_at),
            )
            return self._record(
                self.db.execute(
                    "SELECT * FROM task_session_records WHERE record_id=?", (record_id,)
                ).fetchone()
            )

    def record_decision(self, session_id: str, decision_id: str, decision: Mapping[str, object]) -> dict:
        return self.append(session_id, "decision", decision, idempotency_key=decision_id)

    def record_handoff(self, session_id: str, handoff_id: str, handoff: Mapping[str, object]) -> dict:
        return self.append(session_id, "handoff", handoff, idempotency_key=handoff_id)

    def record_receipt(self, session_id: str, effect_id: str, receipt: Mapping[str, object]) -> dict:
        return self.append(session_id, "receipt", receipt, idempotency_key=effect_id)

    def checkpoint_session(
        self,
        session_id: str,
        *,
        checkpoint: Mapping[str, object],
        context: Mapping[str, object] | None = None,
        status: str = "active",
        checkpoint_id: str | None = None,
    ) -> dict:
        """Atomically persist current state and an append-only checkpoint record."""
        session_id = _identifier(session_id, "session_id")
        if status not in SESSION_STATUSES or not isinstance(status, str):
            raise SessionError("invalid session status")
        checkpoint_json = _json(checkpoint, limit=MAX_RECORD_BYTES, label="checkpoint")
        with self.db:
            row = self.db.execute(
                "SELECT * FROM task_sessions WHERE session_id=?", (session_id,)
            ).fetchone()
            if row is None:
                raise SessionError("unknown task session")
            context_json = row["context"] if context is None else _json(
                context, limit=MAX_CONTEXT_BYTES, label="context"
            )
            checkpoint_id = checkpoint_id or "checkpoint-" + sha256(
                f"{status}:{context_json}:{checkpoint_json}".encode("utf-8")
            ).hexdigest()[:32]
            payload = {"context": json.loads(context_json), "checkpoint": json.loads(checkpoint_json), "status": status}
            payload_json = _json(payload, limit=MAX_RECORD_BYTES, label="checkpoint record")
            existing = self.db.execute(
                """SELECT * FROM task_session_records
                   WHERE session_id=? AND kind='checkpoint' AND idempotency_key=?""",
                (session_id, checkpoint_id),
            ).fetchone()
            if existing is None:
                count = self.db.execute(
                    "SELECT COUNT(*) FROM task_session_records WHERE session_id=?", (session_id,)
                ).fetchone()[0]
                if count >= MAX_SESSION_RECORDS:
                    raise SessionError("session record limit exceeded")
                sequence = self.db.execute(
                    """SELECT COALESCE(MAX(sequence), 0) + 1
                       FROM task_session_records WHERE session_id=?""",
                    (session_id,),
                ).fetchone()[0]
                self.db.execute(
                    """INSERT INTO task_session_records
                       (record_id, session_id, sequence, kind, idempotency_key,
                        payload, created_at)
                       VALUES (?, ?, ?, 'checkpoint', ?, ?, ?)""",
                    (uuid4().hex, session_id, sequence, checkpoint_id, payload_json, _now()),
                )
            elif existing["payload"] != payload_json:
                raise SessionError("checkpoint idempotency conflict")
            else:
                return self._snapshot(row)
            self.db.execute(
                """UPDATE task_sessions
                   SET status=?, context=?, checkpoint=?, updated_at=?
                   WHERE session_id=?""",
                (status, context_json, checkpoint_json, _now(), session_id),
            )
            return self._snapshot(
                self.db.execute(
                    "SELECT * FROM task_sessions WHERE session_id=?", (session_id,)
                ).fetchone()
            )

    def _snapshot(self, row: sqlite3.Row) -> dict:
        records = [
            self._record(record)
            for record in self.db.execute(
                """SELECT * FROM task_session_records
                   WHERE session_id=? ORDER BY sequence""",
                (row["session_id"],),
            )
        ]
        return {
            "session_id": row["session_id"],
            "task_id": row["task_id"],
            "correlation_id": row["correlation_id"],
            "status": row["status"],
            "context": json.loads(row["context"]),
            "checkpoint": json.loads(row["checkpoint"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "records": records,
            "decisions": [record for record in records if record["kind"] == "decision"],
            "handoffs": [record for record in records if record["kind"] == "handoff"],
            "receipts": [record for record in records if record["kind"] == "receipt"],
        }

    @staticmethod
    def _record(row: sqlite3.Row) -> dict:
        return {
            "record_id": row["record_id"],
            "session_id": row["session_id"],
            "sequence": row["sequence"],
            "kind": row["kind"],
            "idempotency_key": row["idempotency_key"],
            "payload": json.loads(row["payload"]),
            "created_at": row["created_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()
