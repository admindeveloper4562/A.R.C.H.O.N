from datetime import datetime, timezone
import unittest
from zoneinfo import ZoneInfo

from jarvis_v2.runtime import (
    CALENDAR_READ_SCOPE,
    CALENDAR_WRITE_SCOPE,
    CalendarAuthorizationError,
    CalendarError,
    CalendarEvent,
    CalendarService,
)


UTC = timezone.utc


class FakeCalendar:
    def __init__(self):
        self.calls = []
        self.events = {}

    def read_events(self, start_utc, end_utc, *, limit):
        self.calls.append(("read", start_utc, end_utc, limit))
        return tuple(self.events.values())[:limit]

    def create_event(self, event):
        self.calls.append(("create", event))
        self.events[event.event_id] = event
        return event

    def update_event(self, event_id, event):
        self.calls.append(("update", event_id, event))
        self.events[event_id] = event
        return event


class RuntimeCalendarTests(unittest.TestCase):
    def test_read_and_writes_use_separate_scopes_and_confirmation(self):
        adapter = FakeCalendar()
        granted = {CALENDAR_READ_SCOPE, CALENDAR_WRITE_SCOPE}
        service = CalendarService(adapter, lambda scope: scope in granted)
        start = datetime(2026, 11, 17, 9, tzinfo=UTC)
        end = datetime(2026, 11, 17, 10, tzinfo=UTC)

        with self.assertRaises(CalendarAuthorizationError):
            service.create_event("e1", "standup", start, end)
        self.assertEqual(adapter.calls, [])
        event = service.create_event("e1", "standup", start, end, confirmed=True)
        self.assertEqual(service.read_events(start, end), (event,))
        updated = service.update_event("e1", "planning", start, end, confirmed=True)
        self.assertEqual(updated.title, "planning")
        self.assertEqual([call[0] for call in adapter.calls], ["create", "read", "update"])

    def test_timezone_is_aware_and_normalized_to_utc(self):
        adapter = FakeCalendar()
        service = CalendarService(adapter, lambda scope: True)
        start = datetime(2026, 11, 17, 9, tzinfo=ZoneInfo("America/New_York"))
        end = datetime(2026, 11, 17, 10, tzinfo=ZoneInfo("America/New_York"))
        event = service.create_event(
            "e1", "meeting", start, end, timezone_name="America/New_York", confirmed=True
        )
        self.assertEqual(event.start_utc, datetime(2026, 11, 17, 14, tzinfo=UTC))
        self.assertEqual(event.timezone, "America/New_York")

        with self.assertRaises(CalendarError):
            service.create_event("e2", "naive", start.replace(tzinfo=None), end, confirmed=True)
        with self.assertRaises(CalendarError):
            service.create_event("e3", "backwards", end, start, confirmed=True)
        with self.assertRaises(CalendarError):
            service.create_event("e4", "bad zone", start, end, timezone_name="Not/AZone", confirmed=True)

    def test_read_rejects_bad_ranges_and_adapter_results(self):
        service = CalendarService(FakeCalendar(), lambda scope: True)
        point = datetime(2026, 11, 17, 9, tzinfo=UTC)
        with self.assertRaises(CalendarError):
            service.read_events(point, point)
        with self.assertRaises(CalendarError):
            service.read_events(point.replace(tzinfo=None), point)

        class BadAdapter(FakeCalendar):
            def read_events(self, start_utc, end_utc, *, limit):
                return (object(),)

        with self.assertRaises(CalendarError):
            CalendarService(BadAdapter(), lambda scope: True).read_events(
                point, datetime(2026, 11, 17, 10, tzinfo=UTC)
            )

        class InfiniteAdapter(FakeCalendar):
            def read_events(self, start_utc, end_utc, *, limit):
                event = CalendarEvent("e1", "bounded", start_utc, end_utc, "UTC")
                while True:
                    yield event

        with self.assertRaises(CalendarError):
            CalendarService(InfiniteAdapter(), lambda scope: True).read_events(
                point, datetime(2026, 11, 17, 10, tzinfo=UTC), limit=2
            )

    def test_read_and_write_scopes_are_independently_required(self):
        point = datetime(2026, 11, 17, 9, tzinfo=UTC)
        end = datetime(2026, 11, 17, 10, tzinfo=UTC)
        read_only = CalendarService(FakeCalendar(), lambda scope: scope == CALENDAR_READ_SCOPE)
        write_only = CalendarService(FakeCalendar(), lambda scope: scope == CALENDAR_WRITE_SCOPE)
        with self.assertRaises(CalendarAuthorizationError):
            read_only.create_event("e1", "write", point, end, confirmed=True)
        with self.assertRaises(CalendarAuthorizationError):
            write_only.read_events(point, end)


if __name__ == "__main__":
    unittest.main()
