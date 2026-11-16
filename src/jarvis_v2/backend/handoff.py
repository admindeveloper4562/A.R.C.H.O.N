"""Atomic, provider-neutral context handoffs in the existing task database."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from typing import Any


MAX_HANDOFF_BYTES = 16 * 1024
MAX_PERMISSION_SCOPES = 64
MAX_TOOL_EFFECTS = 32
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class HandoffError(ValueError):
    """Raised when a context handoff cannot be admitted safely."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise HandoffError(f"invalid {label}")
    return value


def _json(value: object, label: str) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
        )
    except (TypeError, ValueError) as exc:
        raise HandoffError(f"{label} must be bounded JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_HANDOFF_BYTES:
        raise HandoffError(f"{label} exceeds bounded size")
    return encoded


def _scopes(values: Iterable[str]) -> list[str]:
    if isinstance(values, (str, bytes, Mapping)):
        raise HandoffError("permission scopes must be a collection")
    try:
        normalized = list(values)
    except TypeError as exc:
        raise HandoffError("permission scopes must be a collection") from exc
    if not 1 <= len(normalized) <= MAX_PERMISSION_SCOPES:
        raise HandoffError("permission scopes are outside the bounded range")
    if any(not isinstance(value, str) for value in normalized):
        raise HandoffError("permission scopes must contain strings")
    if len(set(normalized)) != len(normalized):
        raise HandoffError("permission scopes must be unique")
    return sorted(_identifier(value, "permission scope") for value in normalized)


def _effects(values: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    if isinstance(values, (str, bytes, Mapping)):
        raise HandoffError("tool effects must be a collection")
    try:
        normalized = list(values)
    except TypeError as exc:
        raise HandoffError("tool effects must be a collection") from exc
    if len(normalized) > MAX_TOOL_EFFECTS:
        raise HandoffError("too many tool effects")
    if any(not isinstance(value, Mapping) for value in normalized):
        raise HandoffError("tool effects must be objects")
    return [dict(value) for value in normalized]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class HandoffStore:
    """Persist one idempotent handoff record using the caller's SQLite database."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS provider_handoffs (
                handoff_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                source_provider TEXT NOT NULL,
                target_provider TEXT NOT NULL,
                permission_scopes_json TEXT NOT NULL,
                tool_effects_json TEXT NOT NULL,
                context_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_provider_handoffs_task
                ON provider_handoffs(task_id, created_at);
            """
        )
        self.db.commit()

    def __enter__(self) -> "HandoffStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def handoff(
        self,
        task_id: str,
        handoff_id: str,
        *,
        source_provider: str,
        target_provider: str,
        permission_scopes: Iterable[str],
        tool_effects: Iterable[Mapping[str, object]] = (),
        context: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        """Atomically persist task identity, permissions, context and receipts."""
        task_id = _identifier(task_id, "task id")
        handoff_id = _identifier(handoff_id, "handoff id")
        source_provider = _identifier(source_provider, "source provider")
        target_provider = _identifier(target_provider, "target provider")
        if source_provider == target_provider:
            raise HandoffError("handoff providers must differ")
        scopes_json = _json(_scopes(permission_scopes), "permission scopes")
        effects_json = _json(_effects(tool_effects), "tool effects")
        if context is None:
            context = {}
        if not isinstance(context, Mapping):
            raise HandoffError("handoff context must be an object")
        context_json = _json(dict(context), "handoff context")
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT * FROM provider_handoffs WHERE handoff_id=?", (handoff_id,)
            ).fetchone()
            expected = {
                "task_id": task_id,
                "source_provider": source_provider,
                "target_provider": target_provider,
                "permission_scopes_json": scopes_json,
                "tool_effects_json": effects_json,
                "context_json": context_json,
            }
            if existing is not None:
                if any(existing[key] != value for key, value in expected.items()):
                    raise HandoffError("handoff idempotency conflict")
                result = self._snapshot(existing)
                self.db.commit()
                return result
            self.db.execute(
                """INSERT INTO provider_handoffs
                   (handoff_id, task_id, source_provider, target_provider,
                    permission_scopes_json, tool_effects_json, context_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    handoff_id, task_id, source_provider, target_provider,
                    scopes_json, effects_json, context_json, _now(),
                ),
            )
            result = self._snapshot(
                self.db.execute(
                    "SELECT * FROM provider_handoffs WHERE handoff_id=?", (handoff_id,)
                ).fetchone()
            )
            self.db.commit()
            return result
        except (sqlite3.Error, HandoffError) as exc:
            self.db.rollback()
            if isinstance(exc, HandoffError):
                raise
            raise HandoffError("handoff persistence failed") from exc

    def get(self, handoff_id: str) -> dict[str, Any]:
        handoff_id = _identifier(handoff_id, "handoff id")
        row = self.db.execute(
            "SELECT * FROM provider_handoffs WHERE handoff_id=?", (handoff_id,)
        ).fetchone()
        if row is None:
            raise HandoffError("unknown handoff")
        return self._snapshot(row)

    def list_for_task(self, task_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
        task_id = _identifier(task_id, "task id")
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise HandoffError("invalid handoff limit")
        rows = self.db.execute(
            "SELECT * FROM provider_handoffs WHERE task_id=? ORDER BY created_at LIMIT ?",
            (task_id, limit),
        )
        return [self._snapshot(row) for row in rows]

    @staticmethod
    def _snapshot(row: sqlite3.Row) -> dict[str, Any]:
        try:
            scopes = json.loads(row["permission_scopes_json"])
            effects = json.loads(row["tool_effects_json"])
            context = json.loads(row["context_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise HandoffError("stored handoff is invalid") from exc
        if not isinstance(scopes, list) or not isinstance(effects, list) or not isinstance(context, dict):
            raise HandoffError("stored handoff shape is invalid")
        return {
            "handoff_id": row["handoff_id"],
            "task_id": row["task_id"],
            "source_provider": row["source_provider"],
            "target_provider": row["target_provider"],
            "permission_scopes": scopes,
            "tool_effects": effects,
            "context": context,
            "created_at": row["created_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()


ContextHandoffStore = HandoffStore
AtomicHandoffStore = HandoffStore


__all__ = [
    "AtomicHandoffStore",
    "ContextHandoffStore",
    "HandoffError",
    "HandoffStore",
    "MAX_HANDOFF_BYTES",
    "MAX_PERMISSION_SCOPES",
    "MAX_TOOL_EFFECTS",
]
