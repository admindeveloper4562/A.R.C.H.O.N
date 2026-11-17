"""Approval-scoped calendar operations with explicit timezone boundaries."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import islice
import re
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


UTC = timezone.utc
CALENDAR_READ_SCOPE = "calendar:read"
CALENDAR_WRITE_SCOPE = "calendar:write"
MAX_EVENTS = 100
MAX_TITLE_BYTES = 256
MAX_DESCRIPTION_BYTES = 4 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class CalendarError(ValueError):
    """Raised when calendar input or an adapter result is invalid."""


class CalendarAuthorizationError(CalendarError):
    """Raised when a calendar operation lacks its explicit approval scope."""


def _identifier(value: str, label: str = "event id") -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise CalendarError(f"invalid {label}")
    return value


def _zone(value: str) -> ZoneInfo:
    if not isinstance(value, str) or not value or len(value) > 128 or "\x00" in value:
        raise CalendarError("invalid timezone")
    try:
        return ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise CalendarError("unknown timezone") from exc


def _timestamp(value: datetime | str, label: str) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise CalendarError(f"invalid {label}") from exc
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise CalendarError(f"{label} must be timezone-aware")
    return value.astimezone(UTC)


def _text(value: str, label: str, maximum: int, *, required: bool = True) -> str:
    if not isinstance(value, str) or (required and not value.strip()):
        raise CalendarError(f"invalid {label}")
    if len(value.encode("utf-8")) > maximum:
        raise CalendarError(f"{label} is outside the bounded range")
    if any(ord(char) < 32 and char not in "\t\n" for char in value):
        raise CalendarError(f"{label} contains control data")
    return value


@dataclass(frozen=True)
class CalendarEvent:
    """A provider-neutral event whose instants are always represented in UTC."""

    event_id: str
    title: str
    start_utc: datetime
    end_utc: datetime
    timezone: str
    description: str = ""

    def __post_init__(self) -> None:
        event_id = _identifier(self.event_id)
        title = _text(self.title, "event title", MAX_TITLE_BYTES)
        description = _text(
            self.description, "event description", MAX_DESCRIPTION_BYTES, required=False
        )
        start = _timestamp(self.start_utc, "event start")
        end = _timestamp(self.end_utc, "event end")
        _zone(self.timezone)
        if end <= start:
            raise CalendarError("event end must be after event start")
        object.__setattr__(self, "event_id", event_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "start_utc", start)
        object.__setattr__(self, "end_utc", end)

    def as_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_utc": self.start_utc.isoformat().replace("+00:00", "Z"),
            "end_utc": self.end_utc.isoformat().replace("+00:00", "Z"),
            "timezone": self.timezone,
            "description": self.description,
        }


class CalendarAdapter(Protocol):
    """The narrow provider boundary; implementations perform the actual I/O."""

    def read_events(
        self, start_utc: datetime, end_utc: datetime, *, limit: int
    ) -> Sequence[CalendarEvent]: ...

    def create_event(self, event: CalendarEvent) -> CalendarEvent: ...

    def update_event(self, event_id: str, event: CalendarEvent) -> CalendarEvent: ...


class CalendarService:
    """Expose read and explicitly confirmed write operations behind scope checks."""

    def __init__(
        self, adapter: CalendarAdapter, authorize: Callable[[str], bool]
    ) -> None:
        if not callable(authorize):
            raise CalendarAuthorizationError("calendar approval checker is required")
        self.adapter = adapter
        self._authorize = authorize

    def read_events(
        self, start: datetime | str, end: datetime | str, *, limit: int = MAX_EVENTS
    ) -> tuple[CalendarEvent, ...]:
        self._require(CALENDAR_READ_SCOPE)
        start_utc, end_utc = self._range(start, end)
        if type(limit) is not int or not 1 <= limit <= MAX_EVENTS:
            raise CalendarError("event limit is outside the bounded range")
        try:
            result = self.adapter.read_events(start_utc, end_utc, limit=limit)
            if isinstance(result, (str, bytes, Mapping)):
                raise CalendarError("calendar adapter returned an invalid event collection")
            # Bound provider iterables before materializing them.
            events = tuple(islice(iter(result), limit + 1))
        except TypeError as exc:
            raise CalendarError("calendar adapter returned an invalid event collection") from exc
        except CalendarError:
            raise
        except Exception as exc:
            raise CalendarError("calendar read failed") from exc
        if len(events) > limit:
            raise CalendarError("calendar adapter returned too many events")
        return tuple(self._returned(event) for event in events)

    list_events = read_events

    def create_event(
        self,
        event_id: str,
        title: str,
        start: datetime | str,
        end: datetime | str,
        *,
        timezone_name: str = "UTC",
        description: str = "",
        confirmed: bool = False,
    ) -> CalendarEvent:
        self._require_write(confirmed)
        event = self._build(event_id, title, start, end, timezone_name, description)
        try:
            return self._returned(self.adapter.create_event(event))
        except CalendarError:
            raise
        except Exception as exc:
            raise CalendarError("calendar create failed") from exc

    def update_event(
        self,
        event_id: str,
        title: str,
        start: datetime | str,
        end: datetime | str,
        *,
        timezone_name: str = "UTC",
        description: str = "",
        confirmed: bool = False,
    ) -> CalendarEvent:
        self._require_write(confirmed)
        event_id = _identifier(event_id)
        event = self._build(event_id, title, start, end, timezone_name, description)
        try:
            return self._returned(self.adapter.update_event(event_id, event))
        except CalendarError:
            raise
        except Exception as exc:
            raise CalendarError("calendar update failed") from exc

    def _require(self, scope: str) -> None:
        try:
            allowed = self._authorize(scope)
        except Exception as exc:
            raise CalendarAuthorizationError("calendar approval check failed") from exc
        if allowed is not True:
            raise CalendarAuthorizationError("calendar approval scope denied")

    def _require_write(self, confirmed: bool) -> None:
        if type(confirmed) is not bool or not confirmed:
            raise CalendarAuthorizationError("explicit calendar write confirmation is required")
        self._require(CALENDAR_WRITE_SCOPE)

    @staticmethod
    def _range(start: datetime | str, end: datetime | str) -> tuple[datetime, datetime]:
        start_utc = _timestamp(start, "range start")
        end_utc = _timestamp(end, "range end")
        if end_utc <= start_utc:
            raise CalendarError("calendar range end must be after start")
        return start_utc, end_utc

    @staticmethod
    def _build(
        event_id: str,
        title: str,
        start: datetime | str,
        end: datetime | str,
        timezone_name: str,
        description: str,
    ) -> CalendarEvent:
        _zone(timezone_name)
        start_utc, end_utc = CalendarService._range(start, end)
        return CalendarEvent(event_id, title, start_utc, end_utc, timezone_name, description)

    @staticmethod
    def _returned(value: object) -> CalendarEvent:
        if not isinstance(value, CalendarEvent):
            raise CalendarError("calendar adapter returned an invalid event")
        return value


CalendarConnector = CalendarService


__all__ = [
    "CALENDAR_READ_SCOPE",
    "CALENDAR_WRITE_SCOPE",
    "CalendarAdapter",
    "CalendarAuthorizationError",
    "CalendarConnector",
    "CalendarError",
    "CalendarEvent",
    "CalendarService",
    "MAX_EVENTS",
]
