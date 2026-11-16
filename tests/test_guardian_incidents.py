import unittest

from jarvis_v2.guardian import (
    FailureClassifier,
    IncidentTracker,
    IncidentTrackerError,
    ProbeResult,
)


class GuardianIncidentTests(unittest.TestCase):
    def setUp(self):
        self.classifier = FailureClassifier()
        self.failure = self.classifier.classify(
            "atlas-sda",
            component=ProbeResult(False, "failed", 20),
            dependencies={"atlas-core": True},
            host=True,
            evidence_refs=("probe-1",),
        )

    def test_repeated_failure_is_one_incident(self):
        tracker = IncidentTracker(max_alerts_per_incident=2)
        first = tracker.record(self.failure)
        second = tracker.record(self.failure)

        self.assertTrue(first.new_incident)
        self.assertTrue(first.alert_emitted)
        self.assertFalse(second.new_incident)
        self.assertTrue(second.alert_emitted)
        self.assertEqual(second.record.fingerprint, first.record.fingerprint)
        self.assertEqual(second.record.occurrences, 2)
        self.assertEqual(len(tracker.records), 1)

    def test_alerts_are_rate_limited_without_losing_occurrences(self):
        tracker = IncidentTracker(max_alerts_per_incident=2)
        notices = [tracker.record(self.failure) for _ in range(5)]

        self.assertEqual(sum(notice.alert_emitted for notice in notices), 2)
        self.assertEqual(notices[-1].record.occurrences, 5)
        self.assertEqual(notices[-1].record.alerts_emitted, 2)

    def test_acknowledgment_suppresses_future_alerts_and_keeps_history(self):
        tracker = IncidentTracker(max_alerts_per_incident=3)
        first = tracker.record(self.failure)
        acknowledged = tracker.acknowledge(first.record.fingerprint)
        later = tracker.record(self.failure)

        self.assertTrue(acknowledged.acknowledged)
        self.assertFalse(later.alert_emitted)
        self.assertEqual(later.record.occurrences, 2)
        self.assertTrue(later.record.acknowledged)

    def test_distinct_root_causes_are_distinct_incidents(self):
        tracker = IncidentTracker()
        other = self.classifier.classify(
            "atlas-sda",
            component=ProbeResult(False, "failed", 20),
            dependencies={"atlas-backend": False},
            host=True,
            evidence_refs=("probe-2",),
        )

        tracker.record(self.failure)
        tracker.record(other)
        self.assertEqual(len(tracker.records), 2)

    def test_unverified_or_invalid_operations_are_rejected(self):
        tracker = IncidentTracker()
        unknown = self.classifier.classify(
            "atlas-sda",
            component=ProbeResult(False, "failed", 20),
            host=None,
        )
        with self.assertRaises(IncidentTrackerError):
            tracker.record(unknown)
        with self.assertRaises(IncidentTrackerError):
            tracker.acknowledge("bad")
        with self.assertRaises(IncidentTrackerError):
            IncidentTracker(max_alerts_per_incident=0)


if __name__ == "__main__":
    unittest.main()
