from datetime import date, datetime, time, timezone
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from jarvis_v2.backend import ReminderError, ReminderScheduler


UTC = timezone.utc


class BackendSchedulerTests(unittest.TestCase):
    def test_one_shot_survives_reopen_and_uses_utc(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reminders.sqlite"
            due = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)
            with ReminderScheduler(path) as store:
                reminder = store.create_reminder("r1", "check in", due)
                self.assertEqual(reminder.next_due_utc, due)
            with ReminderScheduler(path) as reopened:
                self.assertEqual([item.reminder_id for item in reopened.due_reminders(due)], ["r1"])
                completed = reopened.acknowledge("r1")
                self.assertEqual(completed.status, "completed")
                self.assertEqual(reopened.due_reminders(due), [])

    def test_daily_wall_time_survives_fall_dst_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            with ReminderScheduler(Path(directory) / "reminders.sqlite") as store:
                first = store.create_daily_reminder(
                    "r1", "morning", time(1, 30),
                    timezone_name="America/New_York", start_date=date(2026, 11, 1),
                )
                self.assertEqual(first.next_due_utc.hour, 5)
                next_day = store.acknowledge("r1")
                self.assertEqual(next_day.next_due_utc.hour, 6)
                self.assertEqual(
                    next_day.next_due_utc.astimezone(ZoneInfo("America/New_York")).date(),
                    date(2026, 11, 2),
                )

    def test_spring_gap_moves_forward_and_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            with ReminderScheduler(Path(directory) / "reminders.sqlite") as store:
                first = store.create_daily_reminder(
                    "r1", "spring", time(2, 30),
                    timezone_name="America/New_York", start_date=date(2026, 3, 8),
                )
                local = first.next_due_utc.astimezone(ZoneInfo("America/New_York"))
                self.assertEqual((local.hour, local.minute), (3, 30))
                self.assertEqual(store.create_daily_reminder(
                    "r1", "spring", time(2, 30),
                    timezone_name="America/New_York", start_date=date(2026, 3, 8),
                ), first)
                with self.assertRaises(ReminderError):
                    store.create_daily_reminder(
                        "r1", "different", time(2, 30),
                        timezone_name="America/New_York", start_date=date(2026, 3, 8),
                    )

    def test_invalid_timezone_and_message_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with ReminderScheduler(Path(directory) / "reminders.sqlite") as store:
                with self.assertRaises(ReminderError):
                    store.create_daily_reminder("r1", "x", time(9), timezone_name="Not/AZone")
                with self.assertRaises(ReminderError):
                    store.create_reminder("r1", "x\x00y", datetime.now(UTC))


if __name__ == "__main__":
    unittest.main()
