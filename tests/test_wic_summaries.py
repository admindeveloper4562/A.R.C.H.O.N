from datetime import datetime, timezone
import tempfile
import unittest

from jarvis_v2.wic import CitedSummaryComposer, SummarySegment, SummaryStore, WICError


STAMP = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class WICSummariesTests(unittest.TestCase):
    def segment(self, claim_id, certainty="verified", note=None):
        return SummarySegment(
            claim_id, "A dated situation statement", f"https://news.example/article/{claim_id}",
            certainty, STAMP, note,
        )

    def test_citations_and_uncertainty_survive_synthesis(self):
        summary = CitedSummaryComposer().compose(
            "summary-1",
            (self.segment("claim-1"), self.segment("claim-2", "uncertain", "outlets disagree")),
            STAMP,
        )
        self.assertEqual(summary.status, "uncertain")
        self.assertIn("uncertain: outlets disagree", summary.text)
        self.assertEqual(
            summary.citations,
            ("https://news.example/article/claim-1", "https://news.example/article/claim-2"),
        )

    def test_live_freshness_is_rejected(self):
        with self.assertRaisesRegex(WICError, "live freshness"):
            CitedSummaryComposer().compose("summary-1", (self.segment("claim-1"),), STAMP, freshness="live")

    def test_unsupported_certainty_cannot_be_composed(self):
        with self.assertRaisesRegex(WICError, "summary certainty"):
            SummarySegment(
                "claim-1", "unsupported", "https://news.example/article/1", "retracted", STAMP
            )

    def test_summary_store_is_idempotent_and_survives_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            summary = CitedSummaryComposer().compose("summary-1", (self.segment("claim-1"),), STAMP)
            with SummaryStore(path) as store:
                self.assertTrue(store.save(summary))
                self.assertFalse(store.save(summary))
            with SummaryStore(path) as store:
                self.assertEqual(store.get("summary-1"), summary)


if __name__ == "__main__":
    unittest.main()
