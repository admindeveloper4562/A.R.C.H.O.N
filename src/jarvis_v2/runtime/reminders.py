"""Runtime reminder scheduling with persisted notification preferences."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
import sqlite3
from collections.abc import Callable
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from jarvis_v2.backend import Reminder, ReminderError, ReminderScheduler


UTC = timezone.utc
_PREFERENCE_ID = 1


class ReminderServiceError(ValueError):
    """Raised when reminder or notification policy input is invalid."""


def _now(clock: Callable[[], datetime], value: datetime | None = None) -> datetime:
    current = clock() if value is None else value
    if not isinstance(current, datetime) or current.tzinfo is None:
        raise ReminderServiceError("clock value must be timezone-aware")
    return current.astimezone(UTC)


def _zone(name: str) -> ZoneInfo:
    if not isinstance(name, str) or not name or len(name) > 128 or "\x00" in name:
        raise ReminderServiceError("invalid notification timezone")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ReminderServiceError("unknown notification timezone") from exc


@dataclass(frozen=True)
class NotificationPreferences:
    """Persisted notification policy; equal quiet bounds are not ambiguous."""

    enabled: bool = True
    timezone: str = "UTC"
    quiet_start: time | None = None
    quiet_end: time | None = None

    def __post_init__(self) -> None:
        if type(self.enabled) is not bool:
            raise ReminderServiceError("notification enabled flag must be boolean")
        zone = _zone(self.timezone)
        start = self._time(self.quiet_start)
        end = self._time(self.quiet_end)
        if (start is None) != (end is None):
            raise ReminderServiceError("quiet hours require both bounds")
        if start is not None and start == end:
            raise ReminderServiceError("quiet hour bounds must differ")
        object.__setattr__(self, "timezone", zone.key)
        object.__setattr__(self, "quiet_start", start)
        object.__setattr__(self, "quiet_end", end)

    @staticmethod
    def _time(value: time | None) -> time | None:
        if value is None:
            return None
        if not isinstance(value, time) or value.tzinfo is not None:
            raise ReminderServiceError("quiet hour bounds must be naive times")
        return value.replace(microsecond=0)

    def is_quiet(self, current: datetime) -> bool:
        if self.quiet_start is None or self.quiet_end is None:
            return False
        local_time = current.astimezone(_zone(self.timezone)).time().replace(microsecond=0)
        if self.quiet_start < self.quiet_end:
            return self.quiet_start <= local_time < self.quiet_end
        return local_time >= self.quiet_start or local_time < self.quiet_end

    def as_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "timezone": self.timezone,
            "quiet_start": self.quiet_start.isoformat() if self.quiet_start else None,
            "quiet_end": self.quiet_end.isoformat() if self.quiet_end else None,
        }


@dataclass(frozen=True)
class ReminderNotification:
    reminder: Reminder
    status: str

    def __post_init__(self) -> None:
        if self.status not in {"ready", "paused_quiet_hours", "disabled"}:
            raise ReminderServiceError("invalid notification status")

    def as_dict(self) -> dict[str, object]:
        value = self.reminder.as_dict()
        value["notification_status"] = self.status
        return value


class ReminderService:
    """Reuse durable reminders and gate delivery by persisted local policy."""

    def __init__(
        self,
        database: str | Path | sqlite3.Connection,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(database, sqlite3.Connection):
            self._owns_connection = True
            self.db = sqlite3.connect(str(database))
        else:
            self._owns_connection = False
            self.db = database
        self.db.row_factory = sqlite3.Row
        if clock is not None and not callable(clock):
            raise ReminderServiceError("clock must be callable")
        self._clock: Callable[[], datetime] = clock or (lambda: datetime.now(UTC))
        self.scheduler = ReminderScheduler(self.db, clock=self._clock)
        now = self._format(_now(self._clock))
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS runtime_notification_preferences (
                preference_id INTEGER PRIMARY KEY CHECK(preference_id=1),
                enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),
                timezone TEXT NOT NULL,
                quiet_start TEXT,
                quiet_end TEXT,
                updated_at TEXT NOT NULL
            )"""
        )
        self.db.execute(
            """INSERT OR IGNORE INTO runtime_notification_preferences
               (preference_id, enabled, timezone, quiet_start, quiet_end, updated_at)
               VALUES (?, 1, 'UTC', NULL, NULL, ?)""",
            (_PREFERENCE_ID, now),
        )
        self.db.commit()

    def __enter__(self) -> "ReminderService":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def preferences(self) -> NotificationPreferences:
        row = self.db.execute(
            "SELECT enabled, timezone, quiet_start, quiet_end "
            "FROM runtime_notification_preferences WHERE preference_id=?",
            (_PREFERENCE_ID,),
        ).fetchone()
        if row is None:
            raise ReminderServiceError("notification preferences are missing")
        try:
            if row["enabled"] not in (0, 1):
                raise ReminderServiceError("stored notification enabled flag is invalid")
            start = time.fromisoformat(row["quiet_start"]) if row["quiet_start"] else None
            end = time.fromisoformat(row["quiet_end"]) if row["quiet_end"] else None
            return NotificationPreferences(row["enabled"] == 1, row["timezone"], start, end)
        except (TypeError, ValueError, ReminderServiceError) as exc:
            if isinstance(exc, ReminderServiceError):
                raise
            raise ReminderServiceError("stored notification preferences are invalid") from exc

    def set_preferences(
        self,
        *,
        enabled: bool = True,
        timezone_name: str = "UTC",
        quiet_start: time | None = None,
        quiet_end: time | None = None,
    ) -> NotificationPreferences:
        value = NotificationPreferences(enabled, timezone_name, quiet_start, quiet_end)
        with self.db:
            self.db.execute(
                "UPDATE runtime_notification_preferences SET enabled=?, timezone=?, "
                "quiet_start=?, quiet_end=?, updated_at=? WHERE preference_id=?",
                (
                    int(value.enabled),
                    value.timezone,
                    value.quiet_start.isoformat() if value.quiet_start else None,
                    value.quiet_end.isoformat() if value.quiet_end else None,
                    self._format(_now(self._clock)),
                    _PREFERENCE_ID,
                ),
            )
        return self.preferences()

    def schedule(
        self,
        reminder_id: str,
        message: str,
        due_at: datetime | str,
        *,
        timezone_name: str = "UTC",
    ) -> Reminder:
        return self._backend(
            self.scheduler.create_reminder,
            reminder_id,
            message,
            due_at,
            timezone_name=timezone_name,
        )

    create_reminder = schedule

    def schedule_daily(
        self,
        reminder_id: str,
        message: str,
        local_time: time,
        *,
        timezone_name: str,
        start_date: date | None = None,
    ) -> Reminder:
        return self._backend(
            self.scheduler.create_daily_reminder,
            reminder_id,
            message,
            local_time,
            timezone_name=timezone_name,
            start_date=start_date,
        )

    create_daily_reminder = schedule_daily

    def due_notifications(
        self, now: datetime | None = None, *, limit: int = 100
    ) -> tuple[ReminderNotification, ...]:
        current = _now(self._clock, now)
        try:
            reminders = self.scheduler.due_reminders(current, limit=limit)
        except ReminderError as exc:
            raise ReminderServiceError(str(exc)) from exc
        preferences = self.preferences()
        status = "disabled" if not preferences.enabled else (
            "paused_quiet_hours" if preferences.is_quiet(current) else "ready"
        )
        return tuple(ReminderNotification(item, status) for item in reminders)

    pending_notifications = due_notifications

    def get(self, reminder_id: str) -> Reminder:
        return self._backend(self.scheduler.get, reminder_id)

    def acknowledge(self, reminder_id: str) -> Reminder:
        return self._backend(self.scheduler.acknowledge, reminder_id)

    complete = acknowledge

    def cancel(self, reminder_id: str) -> Reminder:
        return self._backend(self.scheduler.cancel, reminder_id)

    def close(self) -> None:
        self.scheduler.close()
        if self._owns_connection:
            self.db.close()

    @staticmethod
    def _backend(call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        try:
            return call(*args, **kwargs)
        except ReminderError as exc:
            raise ReminderServiceError(str(exc)) from exc

    @staticmethod
    def _format(value: datetime) -> str:
        return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


ReminderConnector = ReminderService


__all__ = [
    "NotificationPreferences",
    "ReminderConnector",
    "ReminderNotification",
    "ReminderService",
    "ReminderServiceError",
]
