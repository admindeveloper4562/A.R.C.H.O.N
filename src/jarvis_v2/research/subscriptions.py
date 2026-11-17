"""Bounded followed-channel subscriptions with cadence and terms checks."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import sqlite3
import time
from typing import Any


MIN_CADENCE_SECONDS = 300
MAX_CADENCE_SECONDS = 30 * 24 * 60 * 60
MAX_REFRESH_BATCH = 100
ACCESS_SCOPE = "public_metadata"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class SubscriptionError(ValueError):
    """Raised when a subscription or refresh request is outside policy."""


def _text(value: object, label: str, maximum: int = 128) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise SubscriptionError(f"invalid {label}")
    return value


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SubscriptionError(f"invalid {label}")
    return value


def _cadence(value: object) -> int:
    if type(value) is not int or not MIN_CADENCE_SECONDS <= value <= MAX_CADENCE_SECONDS:
        raise SubscriptionError("cadence is outside the approved range")
    return value


def _clock_value(clock: Callable[[], int]) -> int:
    value = clock()
    if type(value) is not int or value < 0:
        raise SubscriptionError("clock must return a non-negative integer")
    return value


@dataclass(frozen=True)
class Subscription:
    subscription_id: str
    source_id: str
    channel: str
    topic: str
    access_scope: str
    cadence_seconds: int
    next_refresh_at: int
    enabled: bool = True
    last_refresh_at: int | None = None
    last_status: str | None = None
    last_error: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.subscription_id, "subscription id")
        _identifier(self.source_id, "source id")
        _text(self.channel, "channel")
        _text(self.topic, "topic")
        if self.access_scope != ACCESS_SCOPE:
            raise SubscriptionError("provider access scope is not allowed")
        _cadence(self.cadence_seconds)
        if type(self.next_refresh_at) is not int or self.next_refresh_at < 0:
            raise SubscriptionError("invalid next refresh time")
        if not isinstance(self.enabled, bool):
            raise SubscriptionError("invalid enabled state")
        if self.last_refresh_at is not None and (
            type(self.last_refresh_at) is not int or self.last_refresh_at < 0
        ):
            raise SubscriptionError("invalid last refresh time")
        if self.last_status is not None and self.last_status not in {"refreshed", "failed"}:
            raise SubscriptionError("invalid refresh status")
        if self.last_error is not None:
            _identifier(self.last_error, "refresh error")

    def as_dict(self) -> dict[str, object]:
        return {
            "subscription_id": self.subscription_id,
            "source_id": self.source_id,
            "channel": self.channel,
            "topic": self.topic,
            "access_scope": self.access_scope,
            "cadence_seconds": self.cadence_seconds,
            "next_refresh_at": self.next_refresh_at,
            "enabled": self.enabled,
            "last_refresh_at": self.last_refresh_at,
            "last_status": self.last_status,
            "last_error": self.last_error,
        }


@dataclass(frozen=True)
class RefreshResult:
    subscription_id: str
    status: str
    next_refresh_at: int
    failure: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.subscription_id, "subscription id")
        if self.status not in {"refreshed", "failed"}:
            raise SubscriptionError("invalid refresh result")
        if type(self.next_refresh_at) is not int or self.next_refresh_at < 0:
            raise SubscriptionError("invalid next refresh time")
        if self.failure is not None:
            _identifier(self.failure, "refresh failure")


class SubscriptionStore:
    """Persist subscriptions and only bounded refresh metadata."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        if isinstance(database, sqlite3.Connection):
            self._owns_connection = False
            self.db = database
        else:
            self._owns_connection = True
            self.db = sqlite3.connect(str(database))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS research_subscriptions (
                subscription_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                topic TEXT NOT NULL,
                access_scope TEXT NOT NULL,
                cadence_seconds INTEGER NOT NULL,
                next_refresh_at INTEGER NOT NULL,
                enabled INTEGER NOT NULL CHECK(enabled IN (0, 1)),
                last_refresh_at INTEGER,
                last_status TEXT,
                last_error TEXT,
                created_at INTEGER NOT NULL,
                UNIQUE(source_id, channel, topic)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "SubscriptionStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()

    def save(
        self,
        source_id: str,
        channel: str,
        topic: str,
        cadence_seconds: int,
        *,
        now: int,
        next_refresh_at: int | None = None,
    ) -> Subscription:
        source_id = _identifier(source_id, "source id")
        channel = _text(channel, "channel")
        topic = _text(topic, "topic")
        cadence_seconds = _cadence(cadence_seconds)
        if type(now) is not int or now < 0:
            raise SubscriptionError("invalid current time")
        next_refresh_at = now if next_refresh_at is None else next_refresh_at
        if type(next_refresh_at) is not int or next_refresh_at < now:
            raise SubscriptionError("invalid next refresh time")
        subscription_id = "sub-" + hashlib.sha256(
            f"{source_id}\0{channel}\0{topic}\0{ACCESS_SCOPE}".encode("utf-8")
        ).hexdigest()[:32]
        existing = self.db.execute(
            "SELECT * FROM research_subscriptions WHERE source_id=? AND channel=? AND topic=?",
            (source_id, channel, topic),
        ).fetchone()
        if existing is not None:
            current = self._row(existing)
            if current.cadence_seconds != cadence_seconds or current.access_scope != ACCESS_SCOPE:
                raise SubscriptionError("subscription terms conflict")
            return current
        try:
            with self.db:
                self.db.execute(
                    """INSERT INTO research_subscriptions
                       (subscription_id,source_id,channel,topic,access_scope,cadence_seconds,
                        next_refresh_at,enabled,last_refresh_at,last_status,last_error,created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (subscription_id, source_id, channel, topic, ACCESS_SCOPE, cadence_seconds,
                     next_refresh_at, 1, None, None, None, now),
                )
        except sqlite3.IntegrityError as exc:
            raise SubscriptionError("subscription identity conflict") from exc
        return self.get(subscription_id)

    def get(self, subscription_id: str) -> Subscription:
        subscription_id = _identifier(subscription_id, "subscription id")
        row = self.db.execute(
            "SELECT * FROM research_subscriptions WHERE subscription_id=?", (subscription_id,)
        ).fetchone()
        if row is None:
            raise SubscriptionError("subscription not found")
        return self._row(row)

    def due(self, now: int, *, limit: int = MAX_REFRESH_BATCH) -> list[Subscription]:
        if type(now) is not int or now < 0:
            raise SubscriptionError("invalid current time")
        if type(limit) is not int or not 1 <= limit <= MAX_REFRESH_BATCH:
            raise SubscriptionError("refresh limit is outside the bounded range")
        rows = self.db.execute(
            """SELECT * FROM research_subscriptions
               WHERE enabled=1 AND next_refresh_at<=?
               ORDER BY next_refresh_at,subscription_id LIMIT ?""",
            (now, limit),
        )
        return [self._row(row) for row in rows]

    def record_refresh(self, subscription_id: str, *, now: int, status: str, failure: str | None = None) -> Subscription:
        subscription = self.get(subscription_id)
        if type(now) is not int or now < subscription.next_refresh_at:
            raise SubscriptionError("refresh time is before the due time")
        if status not in {"refreshed", "failed"}:
            raise SubscriptionError("invalid refresh status")
        if failure is not None:
            _identifier(failure, "refresh failure")
        with self.db:
            self.db.execute(
                """UPDATE research_subscriptions
                   SET last_refresh_at=?, last_status=?, last_error=?, next_refresh_at=?
                   WHERE subscription_id=? AND enabled=1""",
                (now, status, failure, now + subscription.cadence_seconds, subscription_id),
            )
        return self.get(subscription_id)

    def disable(self, subscription_id: str) -> None:
        subscription_id = _identifier(subscription_id, "subscription id")
        with self.db:
            if self.db.execute(
                "UPDATE research_subscriptions SET enabled=0 WHERE subscription_id=?",
                (subscription_id,),
            ).rowcount != 1:
                raise SubscriptionError("subscription not found")

    @staticmethod
    def _row(row: sqlite3.Row) -> Subscription:
        return Subscription(
            row["subscription_id"], row["source_id"], row["channel"], row["topic"],
            row["access_scope"], row["cadence_seconds"], row["next_refresh_at"],
            bool(row["enabled"]), row["last_refresh_at"], row["last_status"], row["last_error"],
        )


RefreshTransport = Callable[[Subscription], Mapping[str, Any]]


class SubscriptionService:
    """Schedule only due public-metadata refreshes through an injected transport."""

    def __init__(self, store: SubscriptionStore, *, clock: Callable[[], int] | None = None) -> None:
        if not isinstance(store, SubscriptionStore):
            raise SubscriptionError("subscription store is required")
        if clock is not None and not callable(clock):
            raise SubscriptionError("clock must be callable")
        self.store = store
        self.clock = clock or (lambda: int(time.time()))

    def follow(
        self,
        source_id: str,
        channel: str,
        topic: str,
        cadence_seconds: int,
        *,
        next_refresh_at: int | None = None,
    ) -> Subscription:
        now = _clock_value(self.clock)
        return self.store.save(
            source_id, channel, topic, cadence_seconds,
            now=now, next_refresh_at=next_refresh_at,
        )

    def refresh_due(self, transport: RefreshTransport, *, limit: int = MAX_REFRESH_BATCH) -> tuple[RefreshResult, ...]:
        if not callable(transport):
            raise SubscriptionError("refresh transport must be callable")
        now = _clock_value(self.clock)
        results: list[RefreshResult] = []
        for subscription in self.store.due(now, limit=limit):
            failure: str | None = None
            status = "refreshed"
            try:
                if not isinstance(transport(subscription), Mapping):
                    raise TypeError("refresh result must be an object")
            except TimeoutError:
                status, failure = "failed", "provider_timeout"
            except (ConnectionError, OSError):
                status, failure = "failed", "provider_unavailable"
            except (SubscriptionError, TypeError, ValueError):
                status, failure = "failed", "provider_invalid"
            updated = self.store.record_refresh(
                subscription.subscription_id, now=now, status=status, failure=failure,
            )
            results.append(RefreshResult(
                updated.subscription_id, status, updated.next_refresh_at, failure,
            ))
        return tuple(results)


__all__ = [
    "ACCESS_SCOPE",
    "MAX_CADENCE_SECONDS",
    "MAX_REFRESH_BATCH",
    "MIN_CADENCE_SECONDS",
    "RefreshResult",
    "Subscription",
    "SubscriptionError",
    "SubscriptionService",
    "SubscriptionStore",
]
