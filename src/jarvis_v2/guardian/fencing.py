"""Bounded single-writer lease fencing for Guardian cutovers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
import threading
import time
from typing import Any, Callable
from uuid import uuid4


MAX_LEASE_SECONDS = 3_600
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class WriterFenceError(ValueError):
    """Raised when a writer lease is missing, stale or already held."""


@dataclass(frozen=True)
class WriterLease:
    """Opaque authority token for one writer generation."""

    owner_id: str
    lease_id: str
    generation: int
    expires_at: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class WriterFence:
    """Keep exactly one non-expired writer authority at a time.

    Operations are short and lock-protected; callers do not hold this lock
    while doing I/O, inference or tests. A handoff increments the generation,
    making every prior lease unusable even if its process is still alive.
    """

    def __init__(self, *, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._generation = 0
        self._lease: WriterLease | None = None

    def acquire(self, owner_id: str, *, ttl_seconds: int = 60) -> WriterLease:
        owner_id = _identifier(owner_id, "owner id")
        ttl = _ttl(ttl_seconds)
        with self._lock:
            now = self._now()
            self._expire(now)
            if self._lease is not None:
                raise WriterFenceError("write authority is already leased")
            self._generation += 1
            self._lease = WriterLease(
                owner_id, uuid4().hex, self._generation, now + ttl
            )
            return self._lease

    def renew(self, lease: WriterLease, *, ttl_seconds: int = 60) -> WriterLease:
        ttl = _ttl(ttl_seconds)
        with self._lock:
            current = self._require(lease)
            renewed = WriterLease(
                current.owner_id, current.lease_id, current.generation,
                self._now() + ttl,
            )
            self._lease = renewed
            return renewed

    def handoff(
        self,
        current: WriterLease,
        next_owner_id: str,
        *,
        ttl_seconds: int = 60,
    ) -> WriterLease:
        next_owner_id = _identifier(next_owner_id, "next owner id")
        ttl = _ttl(ttl_seconds)
        with self._lock:
            self._require(current)
            now = self._now()
            self._generation += 1
            self._lease = WriterLease(
                next_owner_id, uuid4().hex, self._generation, now + ttl
            )
            return self._lease

    def release(self, lease: WriterLease) -> None:
        with self._lock:
            self._require(lease)
            self._lease = None

    def assert_current(self, lease: WriterLease) -> None:
        """Fail closed unless ``lease`` is the current live authority."""
        with self._lock:
            self._require(lease)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            self._expire(self._now())
            return {
                "generation": self._generation,
                "owner_id": None if self._lease is None else self._lease.owner_id,
                "lease_id": None if self._lease is None else self._lease.lease_id,
                "expires_at": None if self._lease is None else self._lease.expires_at,
                "single_writer": True,
            }

    def _require(self, lease: WriterLease) -> WriterLease:
        if not isinstance(lease, WriterLease) or self._lease != lease:
            raise WriterFenceError("stale or foreign writer lease")
        if lease.expires_at <= self._now():
            self._lease = None
            raise WriterFenceError("writer lease has expired")
        return lease

    def _expire(self, now: float) -> None:
        if self._lease is not None and self._lease.expires_at <= now:
            self._lease = None

    def _now(self) -> float:
        value = self._clock()
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise WriterFenceError("clock value is invalid")
        return float(value)


def _identifier(value: str, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise WriterFenceError(f"invalid {label}")
    return value


def _ttl(value: int) -> int:
    if type(value) is not int or not 1 <= value <= MAX_LEASE_SECONDS:
        raise WriterFenceError("lease TTL is outside the bounded policy")
    return value


__all__ = ["MAX_LEASE_SECONDS", "WriterFenceError", "WriterLease", "WriterFence"]
