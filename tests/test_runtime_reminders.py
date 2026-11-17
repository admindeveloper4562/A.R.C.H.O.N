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
                self.assertEqual(reopened.acknowledge("r1").status, "completed")

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
