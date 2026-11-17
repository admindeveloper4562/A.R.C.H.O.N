"""Read-only Runtime dashboard snapshots backed by explicit data readers."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import islice
import re


UTC = timezone.utc
MAX_RECORDS = 100
_CODE = re.compile(r"^[a-z][a-z0-9_.:-]{0,63}$")


class DashboardError(ValueError):
    """Raised when a dashboard source or record violates the bounded contract."""


def _code(value: str, label: str) -> str:
    if not isinstance(value, str) or not _CODE.fullmatch(value):
        raise DashboardError(f"invalid {label}")
    return value


def _text(value: str, label: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > maximum:
        raise DashboardError(f"invalid {label}")
    if any(ord(char) < 32 for char in value):
        raise DashboardError(f"invalid {label}")
    return value


def _timestamp(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise DashboardError("observed_at must be timezone-aware")
    return value.astimezone(UTC)


def _now(clock: Callable[[], datetime]) -> datetime:
    return _timestamp(clock())


@dataclass(frozen=True)
class DashboardRecord:
    """One source-bound item; absence and failure are represented explicitly."""

    name: str
    status: str
    source: str
    observed_at: datetime
    failure: str | None = None

    def __post_init__(self) -> None:
        _text(self.name, "record name")
        _code(self.status, "record status")
        _text(self.source, "record source")
        observed_at = _timestamp(self.observed_at)
        if self.failure is not None:
            _code(self.failure, "failure code")
        object.__setattr__(self, "observed_at", observed_at)

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "source": self.source,
            "observed_at": self.observed_at.isoformat().replace("+00:00", "Z"),
            "failure": self.failure,
        }


@dataclass(frozen=True)
class DashboardSnapshot:
    captured_at: datetime
    system: tuple[DashboardRecord, ...]
    projects: tuple[DashboardRecord, ...]
    activity: tuple[DashboardRecord, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "captured_at", _timestamp(self.captured_at))
        for label in ("system", "projects", "activity"):
            values = getattr(self, label)
            if not isinstance(values, tuple) or len(values) > MAX_RECORDS:
                raise DashboardError(f"{label} records are outside the bounded range")
            if any(not isinstance(item, DashboardRecord) for item in values):
                raise DashboardError(f"{label} contains an invalid record")

    def as_dict(self) -> dict[str, object]:
        return {
            "captured_at": self.captured_at.isoformat().replace("+00:00", "Z"),
            "system": [item.as_dict() for item in self.system],
            "projects": [item.as_dict() for item in self.projects],
            "activity": [item.as_dict() for item in self.activity],
        }


DashboardReader = Callable[[], Iterable[DashboardRecord]]


class DashboardService:
    """Collect real reader results without inventing health or CI state."""

    def __init__(
        self,
        *,
        system: DashboardReader | None = None,
        projects: DashboardReader | None = None,
        activity: DashboardReader | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if clock is not None and not callable(clock):
            raise DashboardError("clock must be callable")
        for reader in (system, projects, activity):
            if reader is not None and not callable(reader):
                raise DashboardError("dashboard readers must be callable")
        self._clock = clock or (lambda: datetime.now(UTC))
        self._readers = {"system": system, "projects": projects, "activity": activity}

    def snapshot(self) -> DashboardSnapshot:
        captured_at = _now(self._clock)
        return DashboardSnapshot(
            captured_at,
            self._read("system"),
            self._read("projects"),
            self._read("activity"),
        )

    current = snapshot

    def _read(self, category: str) -> tuple[DashboardRecord, ...]:
        reader = self._readers[category]
        observed_at = _now(self._clock)
        if reader is None:
            return (self._unavailable(category, observed_at, "source_not_configured"),)
        try:
            values = reader()
            if isinstance(values, (str, bytes, Mapping)):
                raise DashboardError("reader must return dashboard records")
            records = tuple(islice(iter(values), MAX_RECORDS + 1))
            if len(records) > MAX_RECORDS or any(not isinstance(item, DashboardRecord) for item in records):
                raise DashboardError("reader returned invalid dashboard records")
            return records
        except DashboardError:
            return (self._unavailable(category, observed_at, "source_invalid"),)
        except Exception:
            return (self._unavailable(category, observed_at, "source_unavailable"),)

    @staticmethod
    def _unavailable(category: str, observed_at: datetime, failure: str) -> DashboardRecord:
        return DashboardRecord(
            name=category,
            status="unavailable",
            source="runtime",
            observed_at=observed_at,
            failure=failure,
        )


RuntimeDashboard = DashboardService


__all__ = [
    "DashboardError",
    "DashboardReader",
    "DashboardRecord",
    "DashboardService",
    "DashboardSnapshot",
    "RuntimeDashboard",
]
