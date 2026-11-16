import unittest

from jarvis_v2.guardian import IntegrityScanError, IntegrityScanner


class GuardianIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.digest = "a" * 64
        self.scanner = IntegrityScanner(
            5,
            expected_schemas={"sda": 5, "events": 2},
            required_queues=("project_queue", "pending_queue", "rebuild_queue"),
            expected_hashes={"source": self.digest},
        )

    def test_healthy_snapshot_is_read_only_and_serializable(self):
        schemas = {"sda": 5, "events": 2}
        queues = {"project_queue": 1, "pending_queue": 0, "rebuild_queue": 0}
        hashes = {"source": self.digest}
        report = self.scanner.scan(version=5, schemas=schemas, queues=queues, hashes=hashes)

        self.assertTrue(report.ok)
        self.assertEqual(report.status, "healthy")
        self.assertTrue(report.read_only)
        self.assertEqual(report.as_dict()["queues"]["project_queue"], 1)
        self.assertEqual(schemas, {"sda": 5, "events": 2})
        self.assertEqual(queues["pending_queue"], 0)

    def test_mismatches_are_reported_without_raw_values(self):
        report = self.scanner.scan(
            version=4,
            schemas={"sda": 4, "events": 2, "extra": 1},
            queues={"project_queue": 0, "pending_queue": 0, "other": 1},
            hashes={"source": "b" * 64},
        )

        self.assertFalse(report.ok)
        self.assertEqual(
            report.findings,
            (
                "version_mismatch",
                "schema_unexpected:extra",
                "schema_mismatch:sda",
                "queue_missing:rebuild_queue",
                "queue_unexpected:other",
                "hash_mismatch:source",
            ),
        )
        self.assertNotIn("aaaa", " ".join(report.findings))

    def test_malformed_snapshots_are_rejected_before_comparison(self):
        with self.assertRaises(IntegrityScanError):
            self.scanner.scan(version=True, schemas={}, queues={}, hashes={})
        with self.assertRaises(IntegrityScanError):
            self.scanner.scan(version=5, schemas={}, queues={"pending_queue": -1}, hashes={})
        with self.assertRaises(IntegrityScanError):
            self.scanner.scan(version=5, schemas={}, queues={}, hashes={"source": "not-a-digest"})


if __name__ == "__main__":
    unittest.main()
