"""Durable Backend event outbox with per-consumer effect receipts."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any
from uuid import uuid4

from .storage import DEFAULT_MIGRATIONS, Migration, StorageManager


MAX_EVENT_BYTES = 16 * 1024
EVENT_SCHEMA = "archon.event/1"
PRIVACY_SCOPES = frozenset({"public_metadata", "internal_metadata", "scoped_private"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class EventBusError(ValueError):
    """Raised for invalid, conflicting or unavailable event operations."""


class DeliveryInProgress(EventBusError):
    """Raised when another consumer instance owns the effect fence."""


class DeliveryError(EventBusError):
    """Raised when a consumer effect fails and remains retryable."""


@dataclass(frozen=True)
class EventEnvelope:
    schema: str
    event_id: str
    event_type: str
    producer: str
    aggregate_id: str
    sequence: int
    occurred_at: str
    correlation_id: str
    causation_id: str | None
    privacy_scope: str
    payload_hash: str
    payload: Mapping[str, Any]
    idempotency_key: str | None

    def canonical_payload(self) -> str:
        return json.dumps(self.payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass(frozen=True)
class DeliveryReceipt:
    consumer: str
    event_id: str
    status: str
    attempt: int
    effect_hash: str
    result: Mapping[str, Any]


EVENT_BUS_MIGRATIONS = DEFAULT_MIGRATIONS + (
    Migration(
        module="backend",
        version=2,
        name="event-outbox-and-receipts",
        tables=("backend_outbox", "backend_delivery_receipts"),
        up_sql=(
            "CREATE TABLE backend_outbox ("
            "event_id TEXT PRIMARY KEY, schema TEXT NOT NULL, event_type TEXT NOT NULL, "
            "producer TEXT NOT NULL, aggregate_id TEXT NOT NULL, sequence INTEGER NOT NULL, "
            "occurred_at TEXT NOT NULL, correlation_id TEXT NOT NULL, causation_id TEXT, "
            "privacy_scope TEXT NOT NULL, payload_json TEXT NOT NULL, payload_hash TEXT NOT NULL, "
            "idempotency_key TEXT, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, "
            "created_at TEXT NOT NULL, updated_at TEXT NOT NULL, "
            "UNIQUE(producer, idempotency_key)"
            ")",
            "CREATE TABLE backend_delivery_receipts ("
            "consumer TEXT NOT NULL, event_id TEXT NOT NULL, status TEXT NOT NULL, "
            "attempt INTEGER NOT NULL, effect_hash TEXT NOT NULL DEFAULT '', result_json TEXT NOT NULL DEFAULT '{}', "
            "error_code TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, "
            "PRIMARY KEY (consumer, event_id), FOREIGN KEY(event_id) REFERENCES backend_outbox(event_id)"
            ")",
        ),
        down_sql=("DROP TABLE backend_delivery_receipts", "DROP TABLE backend_outbox"),
    ),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise EventBusError(f"invalid {label}")
    return value


def _json(value: object, label: str) -> str:
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise EventBusError(f"{label} is not bounded JSON") from exc
    if len(encoded.encode("utf-8")) > MAX_EVENT_BYTES:
        raise EventBusError(f"{label} is too large")
    return encoded


class EventBus:
    """Publish events transactionally and fence each consumer effect once."""

    def __init__(self, path: str | Path) -> None:
        self.storage = StorageManager(path, migrations=EVENT_BUS_MIGRATIONS)
        self.storage.migrate()
        self.db = self.storage.db

    def close(self) -> None:
        self.storage.close()

    def __enter__(self) -> "EventBus":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def publish(
        self,
        event_type: str,
        producer: str,
        aggregate_id: str,
        sequence: int,
        payload: Mapping[str, Any],
        *,
        correlation_id: str,
        causation_id: str | None = None,
        privacy_scope: str = "internal_metadata",
        idempotency_key: str | None = None,
        event_id: str | None = None,
    ) -> EventEnvelope:
        event_type = _identifier(event_type, "event_type")
        producer = _identifier(producer, "producer")
        aggregate_id = _identifier(aggregate_id, "aggregate_id")
        correlation_id = _identifier(correlation_id, "correlation_id")
        if causation_id is not None:
            causation_id = _identifier(causation_id, "causation_id")
        if type(sequence) is not int or sequence < 1:
            raise EventBusError("sequence must be a positive integer")
        if privacy_scope not in PRIVACY_SCOPES:
            raise EventBusError("invalid privacy scope")
        if not isinstance(payload, Mapping):
            raise EventBusError("payload must be an object")
        payload_dict = dict(payload)
        payload_json = _json(payload_dict, "payload")
        payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        event_id = _identifier(event_id or uuid4().hex, "event_id")
        if idempotency_key is not None:
            idempotency_key = _identifier(idempotency_key, "idempotency_key")
        occurred_at = _now()
        candidate = EventEnvelope(
            schema=EVENT_SCHEMA,
            event_id=event_id,
            event_type=event_type,
            producer=producer,
            aggregate_id=aggregate_id,
            sequence=sequence,
            occurred_at=occurred_at,
            correlation_id=correlation_id,
            causation_id=causation_id,
            privacy_scope=privacy_scope,
            payload_hash=payload_hash,
            payload=payload_dict,
            idempotency_key=idempotency_key,
        )
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute("SELECT * FROM backend_outbox WHERE event_id=?", (event_id,)).fetchone()
            if existing is None and idempotency_key is not None:
                existing = self.db.execute(
                    "SELECT * FROM backend_outbox WHERE producer=? AND idempotency_key=?",
                    (producer, idempotency_key),
                ).fetchone()
            if existing is not None:
                stored = self._event(existing)
                if not self._same_event(stored, candidate):
                    raise EventBusError("event idempotency conflict")
                self.db.commit()
                return stored
            self.db.execute(
                """INSERT INTO backend_outbox
                   (event_id,schema,event_type,producer,aggregate_id,sequence,occurred_at,
                    correlation_id,causation_id,privacy_scope,payload_json,payload_hash,
                    idempotency_key,status,attempts,created_at,updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    event_id, EVENT_SCHEMA, event_type, producer, aggregate_id, sequence,
                    occurred_at, correlation_id, causation_id, privacy_scope, payload_json,
                    payload_hash, idempotency_key, "pending", 0, occurred_at, occurred_at,
                ),
            )
            self.db.commit()
            return candidate
        except (sqlite3.Error, EventBusError) as exc:
            self.db.rollback()
            if isinstance(exc, EventBusError):
                raise
            raise EventBusError("event publish failed") from exc

    def pending(self, consumer: str, *, limit: int = 100) -> list[EventEnvelope]:
        consumer = _identifier(consumer, "consumer")
        if type(limit) is not int or not 1 <= limit <= 100:
            raise EventBusError("invalid pending limit")
        rows = self.db.execute(
            """SELECT o.* FROM backend_outbox o
               LEFT JOIN backend_delivery_receipts r
                 ON r.event_id=o.event_id AND r.consumer=?
               WHERE r.event_id IS NULL OR r.status='failed'
               ORDER BY o.created_at,o.event_id LIMIT ?""",
            (consumer, limit),
        )
        return [self._event(row) for row in rows]

    def deliver(
        self,
        consumer: str,
        event_id: str,
        effect: Callable[[EventEnvelope], Mapping[str, Any]],
    ) -> DeliveryReceipt:
        """Run one fenced effect; duplicate successful deliveries are no-ops."""
        consumer = _identifier(consumer, "consumer")
        event_id = _identifier(event_id, "event_id")
        if not callable(effect):
            raise EventBusError("effect must be callable")
        try:
            self.db.execute("BEGIN IMMEDIATE")
            event_row = self.db.execute("SELECT * FROM backend_outbox WHERE event_id=?", (event_id,)).fetchone()
            if event_row is None:
                raise EventBusError("unknown event")
            row = self.db.execute(
                "SELECT * FROM backend_delivery_receipts WHERE consumer=? AND event_id=?",
                (consumer, event_id),
            ).fetchone()
            if row is not None and row["status"] == "completed":
                self.db.commit()
                return self._receipt(row)
            if row is not None and row["status"] == "processing":
                raise DeliveryInProgress("event effect is already fenced")
            attempt = (row["attempt"] if row is not None else 0) + 1
            now = _now()
            if row is None:
                self.db.execute(
                    """INSERT INTO backend_delivery_receipts
                       (consumer,event_id,status,attempt,created_at,updated_at)
                       VALUES (?,?,?,?,?,?)""",
                    (consumer, event_id, "processing", attempt, now, now),
                )
            else:
                self.db.execute(
                    "UPDATE backend_delivery_receipts SET status='processing',attempt=?,updated_at=? "
                    "WHERE consumer=? AND event_id=?",
                    (attempt, now, consumer, event_id),
                )
            self.db.execute(
                "UPDATE backend_outbox SET attempts=attempts+1,status='published',updated_at=? WHERE event_id=?",
                (now, event_id),
            )
            self.db.commit()
        except (sqlite3.Error, EventBusError) as exc:
            self.db.rollback()
            if isinstance(exc, EventBusError):
                raise
            raise EventBusError("event delivery reservation failed") from exc

        event = self._event(event_row)
        try:
            result = effect(event)
            if not isinstance(result, Mapping):
                raise TypeError("effect result must be an object")
            result_json = _json(dict(result), "effect result")
        except Exception as exc:
            try:
                self.db.execute("BEGIN IMMEDIATE")
                self.db.execute(
                    "UPDATE backend_delivery_receipts SET status='failed',error_code='effect_failed',updated_at=? "
                    "WHERE consumer=? AND event_id=? AND status='processing'",
                    (_now(), consumer, event_id),
                )
                self.db.commit()
            except sqlite3.Error:
                self.db.rollback()
            raise DeliveryError("event effect failed") from exc

        effect_hash = hashlib.sha256(result_json.encode("utf-8")).hexdigest()
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute(
                """UPDATE backend_delivery_receipts
                   SET status='completed',effect_hash=?,result_json=?,error_code='',updated_at=?
                   WHERE consumer=? AND event_id=? AND status='processing'""",
                (effect_hash, result_json, _now(), consumer, event_id),
            )
            self.db.commit()
        except sqlite3.Error as exc:
            self.db.rollback()
            raise DeliveryError("event receipt commit failed") from exc
        return DeliveryReceipt(consumer, event_id, "completed", attempt, effect_hash, dict(result))

    @staticmethod
    def _same_event(left: EventEnvelope, right: EventEnvelope) -> bool:
        return (
            left.schema == right.schema and left.event_type == right.event_type
            and left.producer == right.producer and left.aggregate_id == right.aggregate_id
            and left.sequence == right.sequence and left.correlation_id == right.correlation_id
            and left.causation_id == right.causation_id and left.privacy_scope == right.privacy_scope
            and left.payload_hash == right.payload_hash and left.idempotency_key == right.idempotency_key
        )

    @staticmethod
    def _event(row: sqlite3.Row) -> EventEnvelope:
        try:
            payload = json.loads(row["payload_json"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise EventBusError("stored event payload is invalid") from exc
        if not isinstance(payload, dict):
            raise EventBusError("stored event payload is not an object")
        return EventEnvelope(
            schema=row["schema"], event_id=row["event_id"], event_type=row["event_type"],
            producer=row["producer"], aggregate_id=row["aggregate_id"], sequence=row["sequence"],
            occurred_at=row["occurred_at"], correlation_id=row["correlation_id"],
            causation_id=row["causation_id"], privacy_scope=row["privacy_scope"],
            payload_hash=row["payload_hash"], payload=payload, idempotency_key=row["idempotency_key"],
        )

    @staticmethod
    def _receipt(row: sqlite3.Row) -> DeliveryReceipt:
        return DeliveryReceipt(
            consumer=row["consumer"], event_id=row["event_id"], status=row["status"],
            attempt=row["attempt"], effect_hash=row["effect_hash"], result=json.loads(row["result_json"]),
        )


__all__ = [
    "DeliveryError", "DeliveryInProgress", "DeliveryReceipt", "EVENT_BUS_MIGRATIONS",
    "EVENT_SCHEMA", "EventBus", "EventBusError", "EventEnvelope", "MAX_EVENT_BYTES",
    "PRIVACY_SCOPES",
]
