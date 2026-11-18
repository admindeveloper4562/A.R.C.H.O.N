"""Durable, fail-closed local task state transitions.

This module stores orchestration state only. It does not execute shell commands
or authorize filesystem/account side effects; those remain separate capabilities.
"""
from __future__ import annotations

import json
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from .storage import connect, ensure_schema

STATES = {"queued", "running", "waiting", "blocked", "done", "failed", "cancelled"}
TERMINAL = {"done", "failed", "cancelled"}


@dataclass(frozen=True)
class Task:
    task_id: str
    idempotency_key: str
    kind: str
    payload: dict
    state: str
    result: dict | None
    error: str | None


class TaskStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        ensure_schema(path)

    @staticmethod
    def _row(row) -> Task:
        return Task(row[0], row[1], row[2], json.loads(row[3]), row[4],
                    json.loads(row[5]) if row[5] else None, row[6])

    def create(self, kind: str, payload: dict, idempotency_key: str) -> Task:
        if not kind.strip() or not idempotency_key.strip() or not isinstance(payload, dict):
            raise ValueError("kind, payload and idempotency_key are required")
        now = time.time()
        task_id = secrets.token_urlsafe(18)
        with connect(self.path) as db:
            existing = db.execute("SELECT * FROM tasks WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
            if existing:
                return self._row(existing)
            db.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, 'queued', NULL, NULL, ?, ?)",
                       (task_id, idempotency_key, kind, json.dumps(payload, separators=(",", ":")), now, now))
            self._event(db, task_id, "queued", "task created")
        return self.get(task_id)

    @staticmethod
    def _event(db, task_id: str, state: str, detail: str) -> None:
        db.execute("INSERT INTO task_events(task_id, state, detail, created) VALUES (?, ?, ?, ?)",
                   (task_id, state, detail, time.time()))

    def get(self, task_id: str) -> Task:
        with connect(self.path) as db:
            row = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        if not row:
            raise KeyError(task_id)
        return self._row(row)

    def transition(self, task_id: str, state: str, *, result: dict | None = None, error: str | None = None) -> Task:
        if state not in STATES:
            raise ValueError("invalid task state")
        current = self.get(task_id)
        if current.state in TERMINAL:
            raise ValueError("terminal task cannot transition")
        if state == "queued" and current.state != "queued":
            raise ValueError("task cannot return to queued")
        with connect(self.path) as db:
            db.execute("UPDATE tasks SET state=?, result=?, error=?, updated=? WHERE task_id=?",
                       (state, json.dumps(result) if result is not None else None, error, time.time(), task_id))
            self._event(db, task_id, state, error or "state changed")
        return self.get(task_id)

    def list(self, limit: int = 50, query: str = "") -> list[Task]:
        limit = max(1, min(int(limit), 100))
        query = query.strip()[:200]
        with connect(self.path) as db:
            if query:
                like = f"%{query}%"
                rows = db.execute(
                    "SELECT t.* FROM tasks t LEFT JOIN task_events e ON e.task_id=t.task_id "
                    "WHERE t.kind LIKE ? OR t.state LIKE ? OR COALESCE(t.error, '') LIKE ? "
                    "OR COALESCE(e.detail, '') LIKE ? GROUP BY t.task_id ORDER BY t.updated DESC LIMIT ?",
                    (like, like, like, like, limit),
                ).fetchall()
            else:
                rows = db.execute("SELECT * FROM tasks ORDER BY updated DESC LIMIT ?", (limit,)).fetchall()
        return [self._row(row) for row in rows]

    def events_since(self, event_id: int = 0, limit: int = 100) -> list[dict]:
        with connect(self.path) as db:
            rows = db.execute(
                "SELECT event_id, task_id, state, detail, created FROM task_events "
                "WHERE event_id > ? ORDER BY event_id LIMIT ?", (max(0, int(event_id)), max(1, min(int(limit), 200)))
            ).fetchall()
        return [{"id": row[0], "task_id": row[1], "state": row[2], "detail": row[3], "created": row[4]} for row in rows]

    def events_for(self, task_id: str, limit: int = 50) -> list[dict]:
        """Return a bounded, read-only event history for one task."""
        with connect(self.path) as db:
            rows = db.execute(
                "SELECT event_id, task_id, state, detail, created FROM task_events "
                "WHERE task_id = ? ORDER BY event_id LIMIT ?",
                (task_id, max(1, min(int(limit), 100))),
            ).fetchall()
        return [{"id": row[0], "task_id": row[1], "state": row[2],
                 "detail": row[3], "created": row[4]} for row in rows]

    def cancel(self, task_id: str) -> Task:
        return self.transition(task_id, "cancelled", error="cancelled by owner")

    def recover_running(self) -> int:
        """After restart, never replay work: return abandoned jobs to waiting."""
        with connect(self.path) as db:
            abandoned = db.execute("SELECT task_id FROM tasks WHERE state='running'").fetchall()
            cur = db.execute("UPDATE tasks SET state='waiting', error=?, updated=? WHERE state='running'",
                             ("worker interrupted; review before retry", time.time()))
            for task_id, in abandoned:
                self._event(db, task_id, "waiting", "worker interrupted; review before retry")
            return cur.rowcount
