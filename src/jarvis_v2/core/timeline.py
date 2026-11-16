"""Read-only task timelines joined from Core's durable records."""
from __future__ import annotations

import hashlib
import re
import sqlite3
from collections import Counter
from pathlib import Path


MAX_TIMELINE_ENTRIES = 100
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class TimelineError(ValueError):
    """Raised when a timeline query is invalid or cannot be satisfied."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise TimelineError(f"invalid {label}")
    return value


def _limit(value: int) -> int:
    if type(value) is not int or value < 1:
        raise TimelineError("limit must be a positive integer")
    return min(value, MAX_TIMELINE_ENTRIES)


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class TaskTimeline:
    """Join task, event, session and dispatch metadata without writing."""

    def __init__(self, database: Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        if self._owns_connection:
            path = Path(database).resolve()
            self.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        else:
            self.db = database
        self.db.row_factory = sqlite3.Row

    def timeline(self, task_id: str, *, limit: int = MAX_TIMELINE_ENTRIES) -> dict:
        task_id = _identifier(task_id, "task_id")
        limit = _limit(limit)
        task = self.db.execute(
            "SELECT id, priority, module, state, title, receipt FROM tasks WHERE id=?",
            (task_id,),
        ).fetchone()
        if task is None:
            raise TimelineError("unknown task")

        events = [self._event(row) for row in self.db.execute(
            """SELECT seq, event_id, session_id, task_id, kind,
                      correlation_id, causation_id, created_at
                 FROM events WHERE task_id=? ORDER BY seq LIMIT ?""",
            (task_id, limit),
        )]
        sessions = []
        for row in self.db.execute(
            """SELECT session_id, correlation_id, status, created_at, updated_at
                 FROM task_sessions WHERE task_id=? ORDER BY created_at LIMIT ?""",
            (task_id, limit),
        ):
            records = [self._record(record) for record in self.db.execute(
                """SELECT record_id, session_id, sequence, kind,
                          idempotency_key, payload, created_at
                     FROM task_session_records WHERE session_id=?
                     ORDER BY sequence LIMIT ?""",
                (row["session_id"], limit),
            )]
            sessions.append({
                "session_id": row["session_id"],
                "correlation_id": row["correlation_id"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "records": records,
            })

        dispatches = [self._dispatch(row) for row in self.db.execute(
            """SELECT d.dispatch_id, d.task_id, d.target_module, d.correlation_id,
                      d.status, d.created_at, d.updated_at,
                      a.ack_id, a.status AS ack_status, a.result AS ack_result,
                      a.created_at AS ack_created_at
                 FROM dispatches d
                 LEFT JOIN dispatch_acknowledgments a ON a.dispatch_id=d.dispatch_id
                 WHERE d.task_id=? ORDER BY d.created_at LIMIT ?""",
            (task_id, limit),
        )]
        outcome = {
            "state": task["state"],
            "receipt_present": task["receipt"] is not None,
            "receipt_sha256": _sha256(task["receipt"]) if task["receipt"] else None,
            "event_outcomes": [
                event["kind"] for event in events if event["kind"] in {"completed", "failed"}
            ],
            "dispatch_acknowledgements": [
                item["ack_status"] for item in dispatches if item["ack_status"]
            ],
            "session_receipts": sum(
                record["kind"] == "receipt"
                for session in sessions for record in session["records"]
            ),
        }
        return {
            "task": {
                "id": task["id"],
                "priority": task["priority"],
                "module": task["module"],
                "state": task["state"],
                "title": task["title"],
            },
            "source_ids": {
                "task_id": task_id,
                "event_ids": [event["event_id"] for event in events],
                "session_ids": [session["session_id"] for session in sessions],
                "record_ids": [
                    record["record_id"]
                    for session in sessions for record in session["records"]
                ],
                "dispatch_ids": [item["dispatch_id"] for item in dispatches],
            },
            "events": events,
            "sessions": sessions,
            "dispatches": dispatches,
            "outcome": outcome,
        }

    def progress(self, task_id: str) -> dict:
        """Return bounded state and evidence counts for one task."""
        view = self.timeline(task_id, limit=MAX_TIMELINE_ENTRIES)
        events = view["events"]
        return {
            "task_id": task_id,
            "state": view["task"]["state"],
            "events": len(events),
            "event_kinds": dict(Counter(event["kind"] for event in events)),
            "sessions": len(view["sessions"]),
            "session_records": sum(
                len(session["records"]) for session in view["sessions"]
            ),
            "dispatches": len(view["dispatches"]),
            "acknowledged_dispatches": sum(
                item["ack_status"] is not None for item in view["dispatches"]
            ),
            "outcome": view["outcome"],
        }

    @staticmethod
    def _event(row: sqlite3.Row) -> dict:
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

    @staticmethod
    def _record(row: sqlite3.Row) -> dict:
        return {
            "record_id": row["record_id"],
            "session_id": row["session_id"],
            "sequence": row["sequence"],
            "kind": row["kind"],
            "idempotency_key": row["idempotency_key"],
            "created_at": row["created_at"],
            "payload_sha256": _sha256(row["payload"]),
        }

    @staticmethod
    def _dispatch(row: sqlite3.Row) -> dict:
        return {
            "dispatch_id": row["dispatch_id"],
            "task_id": row["task_id"],
            "target_module": row["target_module"],
            "correlation_id": row["correlation_id"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "ack_id": row["ack_id"],
            "ack_status": row["ack_status"],
            "ack_result_sha256": _sha256(row["ack_result"]) if row["ack_result"] else None,
            "ack_created_at": row["ack_created_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


__all__ = ["MAX_TIMELINE_ENTRIES", "TaskTimeline", "TimelineError"]
