"""Durable timezone-aware reminders with deterministic DST handling."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import re
import sqlite3
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


UTC = timezone.utc
MAX_MESSAGE_BYTES = 4 * 1024
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class ReminderError(ValueError):
    """Raised when a reminder cannot be safely scheduled or persisted."""


@dataclass(frozen=True)
class Reminder:
    reminder_id: str
    message: str
    timezone: str
    recurrence: str
    scheduled_local: str
    next_due_utc: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    def as_dict(self) -> dict[str, Any]:
        return {
            "reminder_id": self.reminder_id,
            "message": self.message,
            "timezone": self.timezone,
            "recurrence": self.recurrence,
            "scheduled_local": self.scheduled_local,
            "next_due_utc": _format_utc(self.next_due_utc),
            "status": self.status,
            "created_at": _format_utc(self.created_at),
            "updated_at": _format_utc(self.updated_at),
        }


def _format_utc(value: datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ReminderError("stored timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise ReminderError("stored timestamp is not timezone-aware")
    return parsed.astimezone(UTC)


def _now(clock: Callable[[], datetime] | None) -> datetime:
    value = clock() if clock is not None else datetime.now(UTC)
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ReminderError("clock must return an aware datetime")
    return value.astimezone(UTC)


def _zone(name: str) -> ZoneInfo:
    if not isinstance(name, str) or not name or len(name) > 128 or "\x00" in name:
        raise ReminderError("invalid timezone")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ReminderError("unknown timezone") from exc


def _identifier(value: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ReminderError("invalid reminder id")
    return value


def _message(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.encode("utf-8")) > MAX_MESSAGE_BYTES:
        raise ReminderError("reminder message is outside the bounded range")
    if any(ord(char) < 32 and char not in "\t\n" for char in value):
        raise ReminderError("reminder message contains a control character")
    return value


def _resolve_local(local: datetime, zone: ZoneInfo) -> datetime:
    """Resolve wall time; choose the first fold and shift gaps forward."""
    if local.tzinfo is not None:
        raise ReminderError("local datetime must be naive")
    candidates: list[tuple[datetime, datetime]] = []
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        round_trip = aware.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
        if round_trip == local:
            candidates.append((round_trip, aware))
    if candidates:
        return candidates[0][1].astimezone(UTC)

    # A spring-forward gap has no exact instant. Move to the first valid wall
    # time after the gap instead of silently firing before the requested time.
    possible: list[tuple[datetime, datetime]] = []
    for fold in (0, 1):
        aware = local.replace(tzinfo=zone, fold=fold)
        round_trip = aware.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
        if round_trip > local:
            possible.append((round_trip, aware))
    if not possible:
        raise ReminderError("cannot resolve local timezone transition")
    return min(possible, key=lambda item: item[0])[1].astimezone(UTC)


def _local_datetime(value: datetime | str, zone: ZoneInfo) -> tuple[datetime, datetime]:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ReminderError("invalid reminder datetime") from exc
    if not isinstance(value, datetime):
        raise ReminderError("reminder datetime is required")
    if value.tzinfo is not None:
        local = value.astimezone(zone).replace(tzinfo=None)
    else:
        local = value
    return local, _resolve_local(local, zone)


def _local_time(value: time) -> time:
    if not isinstance(value, time) or value.tzinfo is not None:
        raise ReminderError("daily reminder time must be a naive time")
    return value.replace(microsecond=0)


class ReminderScheduler:
    """Persist one-shot and daily reminders using UTC instants."""

    def __init__(
        self,
        database: str | Path | sqlite3.Connection,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self._clock = clock
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS backend_reminders (
                reminder_id TEXT PRIMARY KEY,
                message TEXT NOT NULL,
                timezone TEXT NOT NULL,
                recurrence TEXT NOT NULL CHECK(recurrence IN ('once','daily')),
                scheduled_local TEXT NOT NULL,
                next_due_utc TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('active','completed','cancelled')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_backend_reminders_due
                ON backend_reminders(status, next_due_utc);
            """
        )
        self.db.commit()

    def __enter__(self) -> "ReminderScheduler":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def create_reminder(
        self,
        reminder_id: str,
        message: str,
        due_at: datetime | str,
        *,
        timezone_name: str = "UTC",
    ) -> Reminder:
        reminder_id = _identifier(reminder_id)
        message = _message(message)
        zone = _zone(timezone_name)
        local, due_utc = _local_datetime(due_at, zone)
        return self._insert(
            reminder_id, message, zone.key, "once", local.isoformat(timespec="seconds"), due_utc
        )

    def create_daily_reminder(
        self,
        reminder_id: str,
        message: str,
        local_time: time,
        *,
        timezone_name: str,
        start_date: date | None = None,
    ) -> Reminder:
        reminder_id = _identifier(reminder_id)
        message = _message(message)
        zone = _zone(timezone_name)
        local_time = _local_time(local_time)
        if start_date is None:
            start_date = _now(self._clock).astimezone(zone).date()
        if not isinstance(start_date, date) or isinstance(start_date, datetime):
            raise ReminderError("start date is invalid")
        local = datetime.combine(start_date, local_time)
        due_utc = _resolve_local(local, zone)
        return self._insert(
            reminder_id, message, zone.key, "daily", local_time.isoformat(), due_utc
        )

    schedule = create_reminder

    def get(self, reminder_id: str) -> Reminder:
        row = self.db.execute(
            "SELECT * FROM backend_reminders WHERE reminder_id=?", (_identifier(reminder_id),)
        ).fetchone()
        if row is None:
            raise ReminderError("unknown reminder")
        return self._snapshot(row)

    def due_reminders(self, now: datetime | None = None, *, limit: int = 100) -> list[Reminder]:
        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ReminderError("invalid reminder limit")
        current = _now(self._clock) if now is None else _now(lambda: now)
        rows = self.db.execute(
            "SELECT * FROM backend_reminders WHERE status='active' AND next_due_utc<=? "
            "ORDER BY next_due_utc,reminder_id LIMIT ?",
            (_format_utc(current), limit),
        )
        return [self._snapshot(row) for row in rows]

    due = due_reminders

    def acknowledge(self, reminder_id: str) -> Reminder:
        reminder_id = _identifier(reminder_id)
        now = _format_utc(_now(self._clock))
        try:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute(
                "SELECT * FROM backend_reminders WHERE reminder_id=?", (reminder_id,)
            ).fetchone()
            if row is None:
                raise ReminderError("unknown reminder")
            if row["status"] == "cancelled":
                raise ReminderError("cancelled reminder cannot be acknowledged")
            if row["status"] == "completed":
                self.db.commit()
                return self._snapshot(row)
            if row["recurrence"] == "once":
                self.db.execute(
                    "UPDATE backend_reminders SET status='completed',updated_at=? WHERE reminder_id=?",
                    (now, reminder_id),
                )
            else:
                zone = _zone(row["timezone"])
                scheduled = time.fromisoformat(row["scheduled_local"])
                current_due = _parse_utc(row["next_due_utc"]).astimezone(zone)
                next_local = datetime.combine(current_due.date() + timedelta(days=1), scheduled)
                next_due = _resolve_local(next_local, zone)
                self.db.execute(
                    "UPDATE backend_reminders SET next_due_utc=?,updated_at=? WHERE reminder_id=?",
                    (_format_utc(next_due), now, reminder_id),
                )
            self.db.commit()
            return self.get(reminder_id)
        except (sqlite3.Error, ReminderError) as exc:
            self.db.rollback()
            if isinstance(exc, ReminderError):
                raise
            raise ReminderError("reminder acknowledgement failed") from exc

    complete = acknowledge

    def cancel(self, reminder_id: str) -> Reminder:
        reminder_id = _identifier(reminder_id)
        now = _format_utc(_now(self._clock))
        with self.db:
            changed = self.db.execute(
                "UPDATE backend_reminders SET status='cancelled',updated_at=? "
                "WHERE reminder_id=? AND status='active'",
                (now, reminder_id),
            ).rowcount
        if not changed:
            reminder = self.get(reminder_id)
            if reminder.status != "cancelled":
                raise ReminderError("reminder cannot be cancelled")
        return self.get(reminder_id)

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()

    def _insert(
        self,
        reminder_id: str,
        message: str,
        timezone_name: str,
        recurrence: str,
        scheduled_local: str,
        next_due_utc: datetime,
    ) -> Reminder:
        created = _format_utc(_now(self._clock))
        expected = {
            "message": message,
            "timezone": timezone_name,
            "recurrence": recurrence,
            "scheduled_local": scheduled_local,
            "next_due_utc": _format_utc(next_due_utc),
        }
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT * FROM backend_reminders WHERE reminder_id=?", (reminder_id,)
            ).fetchone()
            if existing is not None:
                if any(existing[key] != value for key, value in expected.items()):
                    raise ReminderError("reminder idempotency conflict")
                self.db.commit()
                return self._snapshot(existing)
            self.db.execute(
                "INSERT INTO backend_reminders "
                "(reminder_id,message,timezone,recurrence,scheduled_local,next_due_utc,status,created_at,updated_at) "
                "VALUES (?,?,?,?,?,?, 'active', ?, ?)",
                (reminder_id, message, timezone_name, recurrence, scheduled_local,
                 expected["next_due_utc"], created, created),
            )
            row = self.db.execute(
                "SELECT * FROM backend_reminders WHERE reminder_id=?", (reminder_id,)
            ).fetchone()
            self.db.commit()
            return self._snapshot(row)
        except (sqlite3.Error, ReminderError) as exc:
            self.db.rollback()
            if isinstance(exc, ReminderError):
                raise
            raise ReminderError("reminder persistence failed") from exc

    @staticmethod
    def _snapshot(row: sqlite3.Row) -> Reminder:
        return Reminder(
            reminder_id=row["reminder_id"],
            message=row["message"],
            timezone=row["timezone"],
            recurrence=row["recurrence"],
            scheduled_local=row["scheduled_local"],
            next_due_utc=_parse_utc(row["next_due_utc"]),
            status=row["status"],
            created_at=_parse_utc(row["created_at"]),
            updated_at=_parse_utc(row["updated_at"]),
        )


ReminderStore = ReminderScheduler
DurableReminderStore = ReminderScheduler


__all__ = [
    "DurableReminderStore",
    "MAX_MESSAGE_BYTES",
    "Reminder",
    "ReminderError",
    "ReminderScheduler",
    "ReminderStore",
    "UTC",
]
