from datetime import datetime, timezone
import hashlib
import tempfile
import unittest

from jarvis_v2.wic import (
    ClaimLedger,
    SourceObservation,
    StoryClusterStore,
    StoryClusterer,
    WICError,
)


STAMP = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def observation(observation_id, source_id, article_number):
    return SourceObservation(
        observation_id, source_id, f"https://{source_id}.example/feed",
        f"https://{source_id}.example/article/{article_number}", STAMP,
    )


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class WICVerificationTests(unittest.TestCase):
    def cluster(self, path, include_second=True):
        first = observation("obs-1", "alpha", 1)
        values = (first, observation("obs-2", "beta", 2)) if include_second else (first,)
        with StoryClusterStore(path) as store:
            return StoryClusterer(store).cluster(values, incident_key="event-1")

    def test_uncertain_claim_cannot_be_verified(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            cluster = self.cluster(path, include_second=False)
            with ClaimLedger(path) as ledger:
                created = ledger.create("claim-1", cluster, digest("first"), STAMP, confidence=0.5)
                self.assertEqual(created.status, "uncertain")
                with self.assertRaisesRegex(WICError, "cannot be verified"):
                    ledger.verify("claim-1", STAMP)

    def test_corroboration_is_required_before_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            one = self.cluster(path, include_second=False)
            both = self.cluster(path, include_second=True)
            with ClaimLedger(path) as ledger:
                self.assertEqual(ledger.create("claim-1", one, digest("first"), STAMP, 0.8).status, "uncertain")
                supported = ledger.corroborate("claim-1", both, STAMP, 0.8)
                self.assertEqual(supported.status, "supported")
                verified = ledger.verify("claim-1", STAMP)
                self.assertEqual(verified.status, "verified")

    def test_retraction_is_visible_and_blocks_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            cluster = self.cluster(path)
            with ClaimLedger(path) as ledger:
                ledger.create("claim-1", cluster, digest("first"), STAMP, 0.9)
                ledger.verify("claim-1", STAMP)
                retracted = ledger.retract("claim-1", "publisher correction", STAMP)
                self.assertEqual(retracted.status, "retracted")
                self.assertEqual(ledger.get("claim-1").status, "retracted")
                self.assertEqual(ledger.history("claim-1")[-1].reason, "publisher correction")
                with self.assertRaisesRegex(WICError, "cannot be verified"):
                    ledger.verify("claim-1", STAMP)

    def test_correction_preserves_retraction_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            cluster = self.cluster(path)
            with ClaimLedger(path) as ledger:
                ledger.create("claim-1", cluster, digest("first"), STAMP, 0.9)
                ledger.retract("claim-1", "publisher correction", STAMP)
                corrected = ledger.correct("claim-1", cluster, digest("replacement"), "replacement revision", STAMP)
                self.assertEqual(corrected.status, "corrected")
                with self.assertRaisesRegex(WICError, "cannot be verified"):
                    ledger.verify("claim-1", STAMP)
                supported = ledger.corroborate("claim-1", cluster, STAMP, 0.9)
                self.assertEqual(supported.status, "supported")
                self.assertEqual(ledger.verify("claim-1", STAMP).status, "verified")
                self.assertEqual(
                    [item.status for item in ledger.history("claim-1")],
                    ["supported", "retracted", "corrected", "supported", "verified"],
                )

    def test_claim_history_survives_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            cluster = self.cluster(path)
            with ClaimLedger(path) as ledger:
                ledger.create("claim-1", cluster, digest("first"), STAMP, 0.8)
                ledger.retract("claim-1", "withdrawn", STAMP)
            with ClaimLedger(path) as ledger:
                self.assertEqual(ledger.get("claim-1").status, "retracted")
                self.assertEqual(len(ledger.history("claim-1")), 2)


if __name__ == "__main__":
    unittest.main()
