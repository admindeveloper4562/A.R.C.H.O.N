from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SAMPLE_EVENTS = (
    {"id": "sample-1", "title": "JARVIS design review", "start": "2026-11-10T09:00:00+00:00", "end": "2026-11-10T10:00:00+00:00"},
    {"id": "sample-2", "title": "Overlapping sample appointment", "start": "2026-11-10T09:30:00+00:00", "end": "2026-11-10T10:30:00+00:00"},
)


def proposal_event_ids(timezone_name: str) -> set[str]:
    """Return event IDs visible in the explicitly connected sample view."""
    return {event["id"] for event in sample_calendar(timezone_name)["events"]}


def sample_calendar(timezone_name: str = "UTC") -> dict:
    """Return deterministic, clearly-labelled fixture data; never accesses credentials."""
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        raise ValueError("unknown timezone") from None
    events = []
    for item in SAMPLE_EVENTS:
        start = datetime.fromisoformat(item["start"]).astimezone(zone)
        end = datetime.fromisoformat(item["end"]).astimezone(zone)
        events.append({**item, "start_local": start.isoformat(), "end_local": end.isoformat()})
    events[1]["conflict_with"] = [events[0]["id"]]
    return {
        "state": "connected",
        "provider": "sample",
        "timezone": timezone_name,
        "events": events,
        "message": "Sample calendar connector is active; events are fixture data, not an external account.",
        "writes": "disabled",
        "proposals": "disabled",
    }
