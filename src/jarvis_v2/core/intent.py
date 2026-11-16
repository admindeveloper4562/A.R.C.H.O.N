"""Deterministic owner-intent admission for Core tasks and approvals."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


MAX_INTENT_BYTES = 24 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_SENSITIVE_MARKERS = (
    "delete", "deploy", "publish", "credential", "financial", "trade",
    "production", "protected", "send",
)


class IntentError(ValueError):
    """Raised when an owner intent cannot be safely admitted."""


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise IntentError(f"invalid {label}")
    return value


def _encode(value: object, label: str) -> str:
    try:
        encoded = json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise IntentError(f"{label} must be JSON serializable") from exc
    if not isinstance(value, (Mapping, list, str)) or not encoded or len(encoded.encode("utf-8")) > MAX_INTENT_BYTES:
        raise IntentError(f"{label} is invalid or exceeds bounded size")
    return encoded


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


class OwnerIntentRouter:
    """Turn structured owner intent into a queue task only after admission checks."""

    def __init__(self, database: Path | sqlite3.Connection, queue=None):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(Path(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.queue = queue
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS owner_intents (
                request_id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL DEFAULT '',
                intent TEXT NOT NULL,
                intent_sha TEXT NOT NULL,
                status TEXT NOT NULL,
                approval_required INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS owner_intent_approvals (
                approval_id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL UNIQUE,
                decision TEXT NOT NULL,
                intent_sha TEXT NOT NULL,
                scope TEXT NOT NULL,
                evidence TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(request_id) REFERENCES owner_intents(request_id)
            );
            """
        )
        self.db.commit()

    def submit(self, intent: Mapping[str, object], *, approval: Mapping[str, object] | None = None) -> dict:
        normalized = self._normalize(intent)
        request_id = normalized["request_id"]
        intent_json = _encode(normalized, "intent")
        intent_sha = hashlib.sha256(intent_json.encode("utf-8")).hexdigest()
        sensitive = self._requires_approval(normalized)
        task_id = normalized["task_id"]
        now = _now()
        with self.db:
            existing = self.db.execute(
                "SELECT * FROM owner_intents WHERE request_id=?", (request_id,)
            ).fetchone()
            if existing is not None:
                if existing["intent_sha"] != intent_sha or existing["task_id"] != task_id:
                    raise IntentError("owner intent conflict")
                if existing["status"] in {"queued", "rejected"}:
                    return self._snapshot(existing)
            else:
                self.db.execute(
                    """INSERT INTO owner_intents
                       (request_id, task_id, session_id, intent, intent_sha, status,
                        approval_required, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, 'received', ?, ?, ?)""",
                    (request_id, task_id, normalized["session_id"], intent_json, intent_sha,
                     int(sensitive), now, now),
                )

            decision = self._approval_decision(approval, intent_sha) if sensitive else self._safe_decision(approval, intent_sha)
            if decision == "PENDING":
                self.db.execute(
                    "UPDATE owner_intents SET status='approval_required',updated_at=? WHERE request_id=?",
                    (now, request_id),
                )
                return self._snapshot(self.db.execute("SELECT * FROM owner_intents WHERE request_id=?", (request_id,)).fetchone())
            if decision == "REJECT":
                self._store_approval(request_id, approval, intent_sha, now)
                self.db.execute(
                    "UPDATE owner_intents SET status='rejected',updated_at=? WHERE request_id=?",
                    (now, request_id),
                )
                return self._snapshot(self.db.execute("SELECT * FROM owner_intents WHERE request_id=?", (request_id,)).fetchone())

            if sensitive:
                self._store_approval(request_id, approval, intent_sha, now)
            self._enqueue(normalized)
            self.db.execute(
                "UPDATE owner_intents SET status='queued',updated_at=? WHERE request_id=?",
                (now, request_id),
            )
            return self._snapshot(self.db.execute("SELECT * FROM owner_intents WHERE request_id=?", (request_id,)).fetchone())

    def get(self, request_id: str) -> dict:
        request_id = _identifier(request_id, "request_id")
        row = self.db.execute("SELECT * FROM owner_intents WHERE request_id=?", (request_id,)).fetchone()
        if row is None:
            raise IntentError("unknown owner intent")
        return self._snapshot(row)

    def _normalize(self, intent: Mapping[str, object]) -> dict:
        if not isinstance(intent, Mapping):
            raise IntentError("intent must be an object")
        request_id = _identifier(intent.get("request_id"), "request_id")
        task_id = _identifier(intent.get("task_id", request_id), "task_id")
        module = _identifier(intent.get("module"), "module")
        action = intent.get("action")
        if not isinstance(action, str) or not action.strip():
            raise IntentError("action is required")
        risk = intent.get("risk", "safe")
        if risk not in {"safe", "ambiguous", "sensitive"}:
            raise IntentError("invalid intent risk")
        priority = intent.get("priority", "P3")
        if priority not in {"P0", "P1", "P2", "P3", "P4", "P5"}:
            raise IntentError("invalid intent priority")
        objective = intent.get("objective")
        if not isinstance(objective, str) or not objective.strip() or len(objective.encode("utf-8")) > 2_000:
            raise IntentError("bounded objective is required")
        acceptance = intent.get("acceptance")
        if not isinstance(acceptance, (str, list, tuple)) or not acceptance:
            raise IntentError("acceptance is required")
        payload = intent.get("payload", {})
        if not isinstance(payload, Mapping):
            raise IntentError("payload must be an object")
        session_id = intent.get("session_id", "")
        if session_id:
            session_id = _identifier(session_id, "session_id")
        return {
            "request_id": request_id,
            "task_id": task_id,
            "session_id": session_id,
            "module": module,
            "action": action.strip(),
            "risk": risk,
            "priority": priority,
            "objective": objective.strip(),
            "acceptance": list(acceptance) if isinstance(acceptance, tuple) else acceptance,
            "payload": dict(payload),
        }

    @staticmethod
    def _requires_approval(intent: Mapping[str, object]) -> bool:
        action = str(intent["action"]).lower()
        return intent["risk"] != "safe" or any(marker in action for marker in _SENSITIVE_MARKERS)

    @staticmethod
    def _safe_decision(approval: Mapping[str, object] | None, intent_sha: str) -> str:
        if approval is None:
            return "APPROVE"
        decision = approval.get("decision")
        if decision == "REJECT":
            return "REJECT"
        if decision == "APPROVE" and approval.get("intent_sha") == intent_sha:
            return "APPROVE"
        raise IntentError("invalid safe-intent approval")

    @staticmethod
    def _approval_decision(approval: Mapping[str, object] | None, intent_sha: str) -> str:
        if approval is None:
            return "PENDING"
        if not isinstance(approval, Mapping):
            raise IntentError("approval must be an object")
        decision = approval.get("decision")
        if decision not in {"APPROVE", "REJECT"}:
            raise IntentError("approval decision is required")
        if approval.get("intent_sha") != intent_sha:
            raise IntentError("approval is not bound to this intent")
        _identifier(approval.get("approval_id"), "approval_id")
        scope = approval.get("scope")
        if not isinstance(scope, (str, list, tuple)) or not scope:
            raise IntentError("approval scope is required")
        return decision

    def _enqueue(self, intent: Mapping[str, object]) -> None:
        if self.queue is None:
            raise IntentError("owner intent queue is unavailable")
        payload = {
            "objective": intent["objective"],
            "acceptance": intent["acceptance"],
            "action": intent["action"],
            "intent_payload": intent["payload"],
        }
        try:
            self.queue.add(
                task_id=intent["task_id"],
                priority=intent["priority"],
                module=intent["module"],
                payload=payload,
                title=intent["objective"][:180],
            )
        except sqlite3.IntegrityError as exc:
            raise IntentError("task id already exists") from exc

    def _store_approval(self, request_id: str, approval: Mapping[str, object], intent_sha: str, now: str) -> None:
        approval_id = _identifier(approval.get("approval_id"), "approval_id")
        scope = _encode(approval.get("scope"), "approval scope")
        evidence = _encode(approval, "approval evidence")
        self.db.execute(
            """INSERT OR REPLACE INTO owner_intent_approvals
               (approval_id, request_id, decision, intent_sha, scope, evidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (approval_id, request_id, approval["decision"], intent_sha, scope, evidence, now),
        )

    def _snapshot(self, row: sqlite3.Row) -> dict:
        approval = self.db.execute(
            "SELECT * FROM owner_intent_approvals WHERE request_id=?", (row["request_id"],)
        ).fetchone()
        return {
            "request_id": row["request_id"],
            "task_id": row["task_id"],
            "session_id": row["session_id"] or None,
            "intent": json.loads(row["intent"]),
            "intent_sha": row["intent_sha"],
            "status": row["status"],
            "approval_required": bool(row["approval_required"]),
            "approval": None if approval is None else {
                "approval_id": approval["approval_id"],
                "decision": approval["decision"],
                "intent_sha": approval["intent_sha"],
                "scope": json.loads(approval["scope"]),
            },
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()
