from datetime import datetime, time, timezone
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.runtime import (
    NotificationPreferences,
    ReminderService,
    ReminderServiceError,
)


UTC = timezone.utc


class RuntimeReminderTests(unittest.TestCase):
    def test_schedule_and_preferences_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.sqlite"
            due = datetime(2026, 11, 17, 23, 30, tzinfo=UTC)
            with ReminderService(path) as service:
                service.set_preferences(
                    timezone_name="UTC", quiet_start=time(22), quiet_end=time(7)
                )
                first = service.schedule("r1", "check in", due)
                self.assertEqual(service.due_notifications(due)[0].status, "paused_quiet_hours")
            with ReminderService(path) as reopened:
                self.assertEqual(reopened.preferences().quiet_start, time(22))
                notification = reopened.due_notifications(datetime(2026, 11, 18, 8, tzinfo=UTC))[0]
                self.assertEqual(notification.status, "ready")
                self.assertEqual(reopened.get("r1"), first)
                completed = reopened.acknowledge("r1")
                self.assertEqual(completed.status, "completed")
                self.assertEqual(reopened.complete("r1"), completed)

    def test_daily_acknowledgement_binds_occurrence_through_runtime_after_restart(self):
        clock = [datetime(2026, 11, 21, 12, tzinfo=UTC)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.sqlite"
            with ReminderService(path, clock=lambda: clock[0]) as service:
                service.schedule_daily(
                    "daily", "morning", time(12), timezone_name="UTC"
                )
                first = service.due_notifications(clock[0])[0].reminder
                with self.assertRaises(ReminderServiceError):
                    service.acknowledge("daily")
                with self.assertRaises(ReminderServiceError):
                    service.acknowledge("daily")
                with self.assertRaises(ReminderServiceError):
                    service.complete("daily")
                self.assertEqual(service.get("daily"), first)
                after_first = service.acknowledge(
                    "daily", expected_due_utc=first.next_due_utc
                )
                clock[0] = after_first.next_due_utc
                second = service.due_notifications(clock[0])[0].reminder
                after_second = service.acknowledge(
                    "daily", expected_due_utc=second.next_due_utc
                )

            with ReminderService(path, clock=lambda: clock[0]) as reopened:
                replay = reopened.acknowledge(
                    "daily", expected_due_utc=first.next_due_utc
                )
                replay_again = reopened.acknowledge(
                    "daily", expected_due_utc=first.next_due_utc
                )
                complete_replay = reopened.complete(
                    "daily", expected_due_utc=second.next_due_utc
                )
                self.assertEqual(replay, after_second)
                self.assertEqual(replay_again, after_second)
                self.assertEqual(complete_replay, after_second)
                self.assertEqual(reopened.due_notifications(clock[0]), ())

    def test_daily_schedule_and_disabled_notifications_are_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            with ReminderService(Path(directory) / "runtime.sqlite") as service:
                service.set_preferences(enabled=False)
                due = datetime(2026, 11, 17, 10, tzinfo=UTC)
                service.schedule_daily(
                    "daily", "morning", time(9), timezone_name="UTC", start_date=due.date()
                )
                self.assertEqual(service.due_notifications(due)[0].status, "disabled")

    def test_invalid_quiet_hours_are_rejected(self):
        with self.assertRaises(ReminderServiceError):
            NotificationPreferences(timezone="Not/AZone")
        with self.assertRaises(ReminderServiceError):
            NotificationPreferences(quiet_start=time(22))
        with self.assertRaises(ReminderServiceError):
            NotificationPreferences(quiet_start=time(7), quiet_end=time(7))


if __name__ == "__main__":
    unittest.main()
