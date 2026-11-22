"""Durable automation schedules backed by the existing timezone-safe store."""
from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
import sqlite3
from typing import Callable

from jarvis_v2.backend.scheduler import Reminder, ReminderError, ReminderScheduler


UTC = "UTC"
ASIA_BANGKOK = "Asia/Bangkok"


class AutomationScheduleStore:
    """Cloud-independent schedule facade; queued work remains durable offline."""

    def __init__(
        self,
        database: str | Path | sqlite3.Connection,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = ReminderScheduler(database, clock=clock)

    def schedule_once(
        self,
        schedule_id: str,
        message: str,
        due_at: datetime | str,
        *,
        timezone_name: str = UTC,
    ) -> Reminder:
        return self._store.create_reminder(schedule_id, message, due_at, timezone_name=timezone_name)

    def schedule_daily(
        self,
        schedule_id: str,
        message: str,
        local_time: time,
        *,
        timezone_name: str = ASIA_BANGKOK,
        start_date: date | None = None,
    ) -> Reminder:
        return self._store.create_daily_reminder(
            schedule_id,
            message,
            local_time,
            timezone_name=timezone_name,
            start_date=start_date,
        )

    def get(self, schedule_id: str) -> Reminder:
        return self._store.get(schedule_id)

    def list_reminders(self, *, status: str | None = "active", limit: int = 100) -> list[Reminder]:
        return self._store.list_reminders(status=status, limit=limit)

    def due(self, now: datetime | None = None, *, limit: int = 100) -> list[Reminder]:
        return self._store.due_reminders(now, limit=limit)

    def acknowledge(self, schedule_id: str, expected_due_utc: datetime) -> Reminder:
        return self._store.acknowledge(schedule_id, expected_due_utc=expected_due_utc)

    def cancel(self, schedule_id: str) -> Reminder:
        return self._store.cancel(schedule_id)

    def close(self) -> None:
        self._store.close()

    def __enter__(self) -> "AutomationScheduleStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


AutomationScheduler = AutomationScheduleStore
ScheduleStore = AutomationScheduleStore

__all__ = [
    "ASIA_BANGKOK",
    "AutomationScheduleStore",
    "AutomationScheduler",
    "Reminder",
    "ReminderError",
    "ScheduleStore",
    "UTC",
]
