from datetime import date, datetime, time, timezone
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from jarvis_v2.automation.scheduler import ASIA_BANGKOK, AutomationScheduleStore


UTC = timezone.utc


class AutomationScheduleTests(unittest.TestCase):
    def test_schedule_survives_offline_reopen_and_uses_utc(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "automation.sqlite"
            with AutomationScheduleStore(path) as store:
                first = store.schedule_daily(
                    "daily",
                    "morning",
                    time(9),
                    start_date=date(2026, 11, 17),
                )
                self.assertEqual(first.timezone, ASIA_BANGKOK)
                self.assertEqual(first.next_due_utc.astimezone(ZoneInfo(ASIA_BANGKOK)).hour, 9)
            with AutomationScheduleStore(path) as reopened:
                self.assertEqual([item.reminder_id for item in reopened.due(first.next_due_utc)], ["daily"])

    def test_dst_transition_and_replay_use_backend_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            with AutomationScheduleStore(Path(directory) / "automation.sqlite") as store:
                first = store.schedule_daily(
                    "dst",
                    "fall-back",
                    time(1, 30),
                    timezone_name="America/New_York",
                    start_date=date(2026, 11, 1),
                )
                self.assertEqual(first.next_due_utc.hour, 5)
                next_due = store.acknowledge("dst", expected_due_utc=first.next_due_utc)
                self.assertEqual(next_due.next_due_utc.hour, 6)

    def test_once_schedule_is_idempotent_and_conflicts_fail(self):
        due = datetime(2026, 11, 17, 2, tzinfo=UTC)
        with tempfile.TemporaryDirectory() as directory:
            with AutomationScheduleStore(Path(directory) / "automation.sqlite") as store:
                first = store.schedule_once("one", "run", due)
                self.assertEqual(store.schedule_once("one", "run", due), first)
                with self.assertRaises(ValueError):
                    store.schedule_once("one", "different", due)


if __name__ == "__main__":
    unittest.main()
