"""A separate, replayable event session with causal metadata."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


MAX_EVENT_DETAIL = 16 * 1024
MAX_EVENT_BATCH = 100
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class EventSessionError(ValueError):
    """Raised when an event session input is invalid or conflicts."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise EventSessionError(f"invalid {label}")
    return value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class EventSessionInterpreter:
    """Persist and replay events independently of parent-task sessions."""

    def __init__(self, database: Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(Path(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self._ensure_schema()
        self.session = self.open_session(name="core-events")
        self.session_id = self.session["session_id"]

    def _ensure_schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS event_sessions (
                session_id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                correlation_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        columns = {row["name"] for row in self.db.execute("PRAGMA table_info(events)")}
        additions = {
            "event_id": "TEXT NOT NULL DEFAULT ''",
            "session_id": "TEXT NOT NULL DEFAULT ''",
            "correlation_id": "TEXT NOT NULL DEFAULT ''",
            "causation_id": "TEXT NOT NULL DEFAULT ''",
            "created_at": "TEXT NOT NULL DEFAULT ''",
        }
        for name, declaration in additions.items():
            if name not in columns:
                self.db.execute(f"ALTER TABLE events ADD COLUMN {name} {declaration}")
        legacy_session = "legacy-event-session"
        self.db.execute(
            """INSERT OR IGNORE INTO event_sessions
               (session_id, name, correlation_id, created_at, updated_at)
               VALUES (?, 'legacy-events', 'legacy-events', ?, ?)""",
            (legacy_session, _now(), _now()),
        )
        for row in self.db.execute(
            "SELECT seq, task_id FROM events WHERE event_id='' OR session_id='' OR correlation_id=''"
        ).fetchall():
            self.db.execute(
                """UPDATE events SET event_id=COALESCE(NULLIF(event_id, ''), ?),
                   session_id=COALESCE(NULLIF(session_id, ''), ?),
                   correlation_id=COALESCE(NULLIF(correlation_id, ''), ?),
                   created_at=COALESCE(NULLIF(created_at, ''), ?)
                   WHERE seq=?""",
                (
                    f"legacy-event-{row['seq']}",
                    legacy_session,
                    f"task:{row['task_id']}",
                    _now(),
                    row["seq"],
                ),
            )
        self.db.commit()

    def open_session(
        self,
        *,
        name: str,
        session_id: str | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        name = _identifier(name, "event session name")
        if session_id is not None:
            session_id = _identifier(session_id, "event session id")
        if correlation_id is not None:
            correlation_id = _identifier(correlation_id, "correlation_id")
        with self.db:
            row = self.db.execute("SELECT * FROM event_sessions WHERE name=?", (name,)).fetchone()
            if row is not None:
                if session_id is not None and row["session_id"] != session_id:
                    raise EventSessionError("event session name conflict")
                if correlation_id is not None and row["correlation_id"] != correlation_id:
                    raise EventSessionError("event session correlation conflict")
                return dict(row)
            session_id = session_id or uuid4().hex
            correlation_id = correlation_id or uuid4().hex
            now = _now()
            self.db.execute(
                """INSERT INTO event_sessions
                   (session_id, name, correlation_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (session_id, name, correlation_id, now, now),
            )
            return dict(
                self.db.execute(
                    "SELECT * FROM event_sessions WHERE session_id=?", (session_id,)
                ).fetchone()
            )

    def emit(
        self,
        task_id: str,
        kind: str,
        detail: str,
        *,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        event_id: str | None = None,
    ) -> dict:
        """Append one event and return metadata without private detail."""
        task_id = _identifier(task_id, "task_id")
        kind = _identifier(kind, "event kind")
        if not isinstance(detail, str) or not detail or len(detail.encode("utf-8")) > MAX_EVENT_DETAIL:
            raise EventSessionError("invalid event detail")
        correlation_id = correlation_id or f"task:{task_id}"
        correlation_id = _identifier(correlation_id, "correlation_id")
        if causation_id is not None:
            causation_id = _identifier(causation_id, "causation_id")
        if event_id is not None:
            event_id = _identifier(event_id, "event_id")
        with self.db:
            if event_id is not None:
                existing = self.db.execute(
                    "SELECT * FROM events WHERE event_id=?", (event_id,)
                ).fetchone()
                if existing is not None:
                    if any(existing[key] != value for key, value in {
                        "task_id": task_id,
                        "kind": kind,
                        "session_id": self.session_id,
                        "correlation_id": correlation_id,
                    }.items()):
                        raise EventSessionError("event id payload conflict")
                    if existing["detail"] != detail:
                        raise EventSessionError("event id payload conflict")
                    return self._metadata(existing)
            if causation_id is None:
                previous = self.db.execute(
                    """SELECT event_id FROM events
                       WHERE session_id=? AND correlation_id=?
                       ORDER BY seq DESC LIMIT 1""",
                    (self.session_id, correlation_id),
                ).fetchone()
                causation_id = previous["event_id"] if previous else None
            event_id = event_id or uuid4().hex
            self.db.execute(
                """INSERT INTO events
                   (task_id, kind, detail, event_id, session_id, correlation_id,
                    causation_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_id, kind, detail, event_id, self.session_id, correlation_id, causation_id or "", _now()),
            )
            return self._metadata(
                self.db.execute("SELECT * FROM events WHERE event_id=?", (event_id,)).fetchone()
            )

    def causal_chain(self, correlation_id: str, *, limit: int = MAX_EVENT_BATCH) -> list[dict]:
        correlation_id = _identifier(correlation_id, "correlation_id")
        limit = self._limit(limit)
        rows = self.db.execute(
            """SELECT * FROM events WHERE correlation_id=?
               ORDER BY seq LIMIT ?""",
            (correlation_id, limit),
        )
        return [self._metadata(row) for row in rows]

    def replay(self, *, limit: int = MAX_EVENT_BATCH) -> list[dict]:
        """Return unacknowledged event metadata for this event session."""
        limit = self._limit(limit)
        consumer = f"event-session:{self.session_id}"
        rows = self.db.execute(
            """SELECT e.* FROM events e
               WHERE e.session_id=? AND NOT EXISTS (
                   SELECT 1 FROM event_receipts r
                   WHERE r.consumer=? AND r.seq=e.seq
               ) ORDER BY e.seq LIMIT ?""",
            (self.session_id, consumer, limit),
        )
        return [self._metadata(row) for row in rows]

    def interpret(self, *, limit: int = MAX_EVENT_BATCH) -> list[dict]:
        """Read the durable event stream without acknowledging effects."""
        return self.replay(limit=limit)

    def ack(self, seq: int) -> None:
        if type(seq) is not int or seq < 1:
            raise EventSessionError("event sequence must be a positive integer")
        consumer = f"event-session:{self.session_id}"
        with self.db:
            if self.db.execute("SELECT 1 FROM events WHERE seq=? AND session_id=?", (seq, self.session_id)).fetchone() is None:
                raise EventSessionError("unknown event")
            self.db.execute(
                "INSERT OR IGNORE INTO event_receipts(consumer,seq) VALUES (?,?)",
                (consumer, seq),
            )

    @staticmethod
    def _limit(limit: int) -> int:
        if type(limit) is not int or limit < 1:
            raise EventSessionError("limit must be a positive integer")
        return min(limit, MAX_EVENT_BATCH)

    @staticmethod
    def _metadata(row: sqlite3.Row) -> dict:
        return {
            "seq": row["seq"],
            "event_id": row["event_id"],
            "session_id": row["session_id"],
            "task_id": row["task_id"],
            "kind": row["kind"],
            "correlation_id": row["correlation_id"],
            "causation_id": row["causation_id"] or None,
            "created_at": row["created_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()
