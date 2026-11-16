"""Durable exactly-once intent tracking for externally executed tool effects."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from typing import Any


MAX_EFFECT_BYTES = 16 * 1024
EFFECT_STATES = frozenset({"prepared", "needs_reconciliation", "completed", "failed"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class EffectJournalError(ValueError):
    """Raised when an effect cannot be safely recorded or reconciled."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise EffectJournalError(f"invalid {label}")
    return value


def _text(value: str, label: str, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > limit:
        raise EffectJournalError(f"invalid {label}")
    if any(ord(char) < 32 for char in value):
        raise EffectJournalError(f"invalid {label}")
    return value


def _json(value: object, label: str) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
        )
    except (TypeError, ValueError) as exc:
        raise EffectJournalError(f"{label} must be bounded JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_EFFECT_BYTES:
        raise EffectJournalError(f"{label} exceeds bounded size")
    return encoded


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class EffectJournal:
    """Persist one execution identity and fence replay after a crash.

    This class records intent and evidence only. The caller performs the
    external action after ``prepare`` and must call ``complete`` or ``fail``.
    """

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS tool_effect_journal (
                effect_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                target TEXT NOT NULL,
                request_json TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL CHECK(attempts >= 1),
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_tool_effect_journal_task
                ON tool_effect_journal(task_id, created_at);
            CREATE INDEX IF NOT EXISTS idx_tool_effect_journal_pending
                ON tool_effect_journal(status, updated_at);
            """
        )
        self.db.commit()

    def __enter__(self) -> "EffectJournal":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def prepare(
        self,
        effect_id: str,
        task_id: str,
        *,
        operation: str,
        target: str,
        request: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        """Create one effect intent; only a new intent permits execution."""
        effect_id = _identifier(effect_id, "effect id")
        task_id = _identifier(task_id, "task id")
        operation = _identifier(operation, "operation")
        target = _text(target, "target")
        if request is None:
            request = {}
        if not isinstance(request, Mapping):
            raise EffectJournalError("effect request must be an object")
        request_json = _json(dict(request), "effect request")
        now = _now()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT * FROM tool_effect_journal WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if existing is not None:
                self._check_identity(existing, task_id, operation, target, request_json)
                if existing["status"] == "prepared":
                    self.db.execute(
                        "UPDATE tool_effect_journal SET status='needs_reconciliation', updated_at=? WHERE effect_id=?",
                        (now, effect_id),
                    )
                    existing = self.db.execute(
                        "SELECT * FROM tool_effect_journal WHERE effect_id=?", (effect_id,)
                    ).fetchone()
                result = self._snapshot(existing, execution_permitted=False)
                self.db.commit()
                return result
            self.db.execute(
                """INSERT INTO tool_effect_journal
                   (effect_id, task_id, operation, target, request_json, status,
                    attempts, result_json, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, 'prepared', 1, '{}', ?, ?)""",
                (effect_id, task_id, operation, target, request_json, now, now),
            )
            result = self._snapshot(
                self.db.execute(
                    "SELECT * FROM tool_effect_journal WHERE effect_id=?", (effect_id,)
                ).fetchone(),
                execution_permitted=True,
            )
            self.db.commit()
            return result
        except (sqlite3.Error, EffectJournalError) as exc:
            self.db.rollback()
            if isinstance(exc, EffectJournalError):
                raise
            raise EffectJournalError("effect preparation failed") from exc

    def complete(self, effect_id: str, result: Mapping[str, object] | None = None) -> dict[str, Any]:
        return self._finish(effect_id, "completed", result)

    def fail(self, effect_id: str, result: Mapping[str, object] | None = None) -> dict[str, Any]:
        return self._finish(effect_id, "failed", result)

    def reconcile_pending(self) -> list[dict[str, Any]]:
        """Fence every unfinished intent so restart cannot replay it blindly."""
        now = _now()
        try:
            with self.db:
                self.db.execute(
                    "UPDATE tool_effect_journal SET status='needs_reconciliation', updated_at=? WHERE status='prepared'",
                    (now,),
                )
                rows = self.db.execute(
                    "SELECT * FROM tool_effect_journal WHERE status='needs_reconciliation' ORDER BY created_at"
                )
                return [self._snapshot(row, execution_permitted=False) for row in rows]
        except sqlite3.Error as exc:
            raise EffectJournalError("effect reconciliation failed") from exc

    def get(self, effect_id: str) -> dict[str, Any]:
        effect_id = _identifier(effect_id, "effect id")
        row = self.db.execute(
            "SELECT * FROM tool_effect_journal WHERE effect_id=?", (effect_id,)
        ).fetchone()
        if row is None:
            raise EffectJournalError("unknown effect")
        return self._snapshot(row, execution_permitted=False)

    def pending(self, *, limit: int = 100) -> list[dict[str, Any]]:
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise EffectJournalError("invalid pending limit")
        rows = self.db.execute(
            "SELECT * FROM tool_effect_journal WHERE status IN ('prepared','needs_reconciliation') "
            "ORDER BY created_at LIMIT ?", (limit,)
        )
        return [self._snapshot(row, execution_permitted=False) for row in rows]

    def _finish(
        self, effect_id: str, status: str, result: Mapping[str, object] | None
    ) -> dict[str, Any]:
        effect_id = _identifier(effect_id, "effect id")
        if result is None:
            result = {}
        if not isinstance(result, Mapping):
            raise EffectJournalError("effect result must be an object")
        result_json = _json(dict(result), "effect result")
        try:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute(
                "SELECT * FROM tool_effect_journal WHERE effect_id=?", (effect_id,)
            ).fetchone()
            if row is None:
                raise EffectJournalError("unknown effect")
            if row["status"] == status:
                if row["result_json"] != result_json:
                    raise EffectJournalError("effect result conflict")
                result_row = self._snapshot(row, execution_permitted=False)
                self.db.commit()
                return result_row
            if row["status"] not in {"prepared", "needs_reconciliation"}:
                raise EffectJournalError("effect is already finalized")
            now = _now()
            self.db.execute(
                "UPDATE tool_effect_journal SET status=?, result_json=?, updated_at=? WHERE effect_id=?",
                (status, result_json, now, effect_id),
            )
            result_row = self._snapshot(
                self.db.execute(
                    "SELECT * FROM tool_effect_journal WHERE effect_id=?", (effect_id,)
                ).fetchone(),
                execution_permitted=False,
            )
            self.db.commit()
            return result_row
        except (sqlite3.Error, EffectJournalError) as exc:
            self.db.rollback()
            if isinstance(exc, EffectJournalError):
                raise
            raise EffectJournalError("effect finalization failed") from exc

    @staticmethod
    def _check_identity(
        row: sqlite3.Row,
        task_id: str,
        operation: str,
        target: str,
        request_json: str,
    ) -> None:
        if any(row[key] != value for key, value in {
            "task_id": task_id,
            "operation": operation,
            "target": target,
            "request_json": request_json,
        }.items()):
            raise EffectJournalError("effect identity conflict")

    @staticmethod
    def _snapshot(row: sqlite3.Row, *, execution_permitted: bool) -> dict[str, Any]:
        try:
            request = json.loads(row["request_json"])
            result = json.loads(row["result_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise EffectJournalError("stored effect is invalid") from exc
        if not isinstance(request, dict) or not isinstance(result, dict):
            raise EffectJournalError("stored effect shape is invalid")
        return {
            "effect_id": row["effect_id"],
            "task_id": row["task_id"],
            "operation": row["operation"],
            "target": row["target"],
            "request": request,
            "status": row["status"],
            "attempts": row["attempts"],
            "result": result,
            "execution_permitted": execution_permitted,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


ToolEffectJournal = EffectJournal
ToolEffectJournalError = EffectJournalError


__all__ = [
    "EFFECT_STATES",
    "EffectJournal",
    "EffectJournalError",
    "MAX_EFFECT_BYTES",
    "ToolEffectJournal",
    "ToolEffectJournalError",
]
