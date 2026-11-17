import unittest

from jarvis_v2.wic import WICError, WorldCard, WorldTimeline


STAMP = "2026-11-17T00:00:00Z"


def card(card_id, event_at, *, status="active", correction=None):
    return WorldCard(
        card_id,
        f"Story {card_id}",
        (f"https://news.example/{card_id}",),
        STAMP,
        "2026-11-16T00:00:00Z",
        event_at,
        status,
        correction,
    )


class WICWorldTests(unittest.TestCase):
    def test_card_preserves_source_and_independent_dates(self):
        value = card("story-1", "2026-11-15T00:00:00Z")

        restored = WorldCard.from_dict(value.as_dict())

        self.assertEqual(restored.source_urls, ("https://news.example/story-1",))
        self.assertEqual(restored.fetched_at, STAMP)
        self.assertEqual(restored.published_at, "2026-11-16T00:00:00Z")
        self.assertEqual(restored.event_at, "2026-11-15T00:00:00Z")

    def test_correction_is_visible_and_retraction_is_not_silent(self):
        corrected = card("story-1", None, status="corrected", correction="publisher correction")
        retracted = card("story-2", None, status="retracted", correction="claim withdrawn")

        self.assertEqual(corrected.as_dict()["correction"], "publisher correction")
        self.assertEqual(retracted.as_dict()["status"], "retracted")
        with self.assertRaises(WICError):
            card("story-3", None, status="corrected")

    def test_timeline_is_bounded_and_newest_first(self):
        timeline = WorldTimeline.from_cards([
            card("older", "2026-11-15T00:00:00Z"),
            card("newer", "2026-11-17T00:00:00Z"),
        ])

        self.assertEqual([item.card_id for item in timeline.cards], ["newer", "older"])
        self.assertEqual(timeline.as_dict()["cards"][0]["event_at"], "2026-11-17T00:00:00Z")

    def test_empty_timeline_is_explicit_and_duplicates_fail_closed(self):
        self.assertEqual(WorldTimeline(()).as_dict(), {"cards": []})
        duplicate = card("story-1", STAMP)
        with self.assertRaises(WICError):
            WorldTimeline((duplicate, duplicate))


if __name__ == "__main__":
    unittest.main()
