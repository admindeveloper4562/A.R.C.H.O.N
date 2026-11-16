"""Scoped module dispatch envelopes and one-writer acknowledgements."""
from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


MAX_DISPATCH_BYTES = 16 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_MODULE = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
ACK_STATUSES = frozenset({"completed", "failed", "rejected"})


class DispatchError(ValueError):
    """Raised when an assignment or its ownership fence is invalid."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise DispatchError(f"invalid {label}")
    return value


def _module(value: str) -> str:
    if not isinstance(value, str) or not _MODULE.fullmatch(value):
        raise DispatchError("invalid target module")
    return value


def _encode(value: object, label: str) -> str:
    if isinstance(value, str):
        value = [value]
    elif isinstance(value, tuple):
        value = list(value)
    if not isinstance(value, (Mapping, list)):
        raise DispatchError(f"{label} must be a string, list or object")
    if isinstance(value, list) and (not value or not all(isinstance(item, str) for item in value)):
        raise DispatchError(f"{label} must contain strings")
    if label in {"scope", "acceptance"} and not value:
        raise DispatchError(f"{label} must not be empty")
    try:
        encoded = json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise DispatchError(f"{label} must be JSON serializable") from exc
    if not encoded or len(encoded.encode("utf-8")) > MAX_DISPATCH_BYTES:
        raise DispatchError(f"{label} exceeds bounded size")
    return encoded


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class DispatchStore:
    """Persist an assignment and fence its execution to one consumer."""

    def __init__(self, database: Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(Path(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS dispatches (
                dispatch_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                target_module TEXT NOT NULL,
                scope TEXT NOT NULL,
                acceptance TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                input_refs TEXT NOT NULL,
                status TEXT NOT NULL,
                executor_id TEXT NOT NULL DEFAULT '',
                claim_id TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dispatch_acknowledgments (
                ack_id TEXT PRIMARY KEY,
                dispatch_id TEXT NOT NULL UNIQUE,
                executor_id TEXT NOT NULL,
                claim_id TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(dispatch_id) REFERENCES dispatches(dispatch_id)
            );
            """
        )
        self.db.commit()

    def create(
        self,
        task_id: str,
        target_module: str,
        scope: str | Sequence[str] | Mapping[str, object],
        acceptance: str | Sequence[str] | Mapping[str, object],
        *,
        correlation_id: str,
        input_refs: Mapping[str, object] | None = None,
        dispatch_id: str | None = None,
    ) -> dict:
        task_id = _identifier(task_id, "task_id")
        target_module = _module(target_module)
        correlation_id = _identifier(correlation_id, "correlation_id")
        scope_json = _encode(scope, "scope")
        acceptance_json = _encode(acceptance, "acceptance")
        input_json = _encode(input_refs or {}, "input_refs")
        dispatch_id = _identifier(dispatch_id or uuid4().hex, "dispatch_id")
        with self.db:
            existing = self.db.execute(
                "SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)
            ).fetchone()
            if existing is not None:
                expected = {
                    "task_id": task_id,
                    "target_module": target_module,
                    "scope": scope_json,
                    "acceptance": acceptance_json,
                    "correlation_id": correlation_id,
                    "input_refs": input_json,
                }
                if any(existing[key] != value for key, value in expected.items()):
                    raise DispatchError("dispatch id payload conflict")
                return self._snapshot(existing)
            now = _now()
            self.db.execute(
                """INSERT INTO dispatches
                   (dispatch_id, task_id, target_module, scope, acceptance,
                    correlation_id, input_refs, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)""",
                (dispatch_id, task_id, target_module, scope_json, acceptance_json,
                 correlation_id, input_json, now, now),
            )
            return self._snapshot(
                self.db.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
            )

    def claim(self, dispatch_id: str, executor_id: str, *, claim_id: str | None = None) -> dict:
        dispatch_id = _identifier(dispatch_id, "dispatch_id")
        executor_id = _identifier(executor_id, "executor_id")
        claim_id = _identifier(claim_id or uuid4().hex, "claim_id")
        with self.db:
            row = self.db.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
            if row is None:
                raise DispatchError("unknown dispatch")
            if row["status"] == "claimed":
                if row["executor_id"] != executor_id or row["claim_id"] != claim_id:
                    raise DispatchError("dispatch already claimed")
                return self._snapshot(row)
            if row["status"] != "queued":
                raise DispatchError("dispatch is not claimable")
            updated = self.db.execute(
                """UPDATE dispatches SET status='claimed', executor_id=?, claim_id=?, updated_at=?
                   WHERE dispatch_id=? AND status='queued'""",
                (executor_id, claim_id, _now(), dispatch_id),
            )
            if updated.rowcount != 1:
                raise DispatchError("dispatch claim lost")
            return self._snapshot(
                self.db.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
            )

    def acknowledge(
        self,
        dispatch_id: str,
        executor_id: str,
        claim_id: str,
        *,
        status: str,
        result: Mapping[str, object],
    ) -> dict:
        dispatch_id = _identifier(dispatch_id, "dispatch_id")
        executor_id = _identifier(executor_id, "executor_id")
        claim_id = _identifier(claim_id, "claim_id")
        if status not in ACK_STATUSES or not isinstance(status, str):
            raise DispatchError("invalid acknowledgement status")
        result_json = _encode(result, "result")
        with self.db:
            row = self.db.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
            if row is None:
                raise DispatchError("unknown dispatch")
            existing = self.db.execute(
                "SELECT * FROM dispatch_acknowledgments WHERE dispatch_id=?", (dispatch_id,)
            ).fetchone()
            if existing is not None:
                if any(existing[key] != value for key, value in {
                    "executor_id": executor_id,
                    "claim_id": claim_id,
                    "status": status,
                    "result": result_json,
                }.items()):
                    raise DispatchError("acknowledgement conflict")
                return self._snapshot(row)
            if row["status"] != "claimed" or row["executor_id"] != executor_id or row["claim_id"] != claim_id:
                raise DispatchError("invalid dispatch claim")
            ack_id = uuid4().hex
            now = _now()
            self.db.execute(
                """INSERT INTO dispatch_acknowledgments
                   (ack_id, dispatch_id, executor_id, claim_id, status, result, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (ack_id, dispatch_id, executor_id, claim_id, status, result_json, now),
            )
            self.db.execute(
                "UPDATE dispatches SET status=?, updated_at=? WHERE dispatch_id=?",
                (status, now, dispatch_id),
            )
            return self._snapshot(
                self.db.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
            )

    def get(self, dispatch_id: str) -> dict:
        dispatch_id = _identifier(dispatch_id, "dispatch_id")
        row = self.db.execute("SELECT * FROM dispatches WHERE dispatch_id=?", (dispatch_id,)).fetchone()
        if row is None:
            raise DispatchError("unknown dispatch")
        return self._snapshot(row)

    def _snapshot(self, row: sqlite3.Row) -> dict:
        result = {
            "dispatch_id": row["dispatch_id"],
            "task_id": row["task_id"],
            "target_module": row["target_module"],
            "scope": json.loads(row["scope"]),
            "acceptance": json.loads(row["acceptance"]),
            "correlation_id": row["correlation_id"],
            "input_refs": json.loads(row["input_refs"]),
            "status": row["status"],
            "executor_id": row["executor_id"] or None,
            "claim_id": row["claim_id"] or None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        ack = self.db.execute(
            "SELECT * FROM dispatch_acknowledgments WHERE dispatch_id=?", (row["dispatch_id"],)
        ).fetchone()
        result["ack"] = None if ack is None else {
            "ack_id": ack["ack_id"],
            "executor_id": ack["executor_id"],
            "claim_id": ack["claim_id"],
            "status": ack["status"],
            "result": json.loads(ack["result"]),
            "created_at": ack["created_at"],
        }
        return result

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()
