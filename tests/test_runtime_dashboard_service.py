from datetime import datetime, timezone
import unittest

from jarvis_v2.runtime import DashboardError, DashboardRecord, DashboardService


UTC = timezone.utc
OBSERVED = datetime(2026, 11, 17, 1, 2, 3, tzinfo=UTC)


class RuntimeDashboardServiceTests(unittest.TestCase):
    def test_snapshot_preserves_source_timestamps_and_failures(self):
        service = DashboardService(
            system=lambda: [DashboardRecord("linux", "ready", "host", OBSERVED)],
            projects=lambda: [DashboardRecord("archon", "running", "sqlite", OBSERVED)],
            activity=lambda: [DashboardRecord("ci", "failed", "local-ci", OBSERVED, "test_failed")],
            clock=lambda: OBSERVED,
        )
        snapshot = service.snapshot()
        self.assertEqual(snapshot.system[0].source, "host")
        self.assertEqual(snapshot.projects[0].observed_at, OBSERVED)
        self.assertEqual(snapshot.activity[0].failure, "test_failed")
        self.assertEqual(snapshot.as_dict()["activity"][0]["failure"], "test_failed")

    def test_missing_and_failing_sources_are_visible_not_healthy(self):
        service = DashboardService(
            system=lambda: (_ for _ in ()).throw(RuntimeError("source down")),
            clock=lambda: OBSERVED,
        )
        snapshot = service.snapshot()
        self.assertEqual(snapshot.system[0].status, "unavailable")
        self.assertEqual(snapshot.system[0].failure, "source_unavailable")
        self.assertEqual(snapshot.projects[0].failure, "source_not_configured")
        self.assertEqual(snapshot.activity[0].failure, "source_not_configured")

    def test_reader_output_is_bounded_and_records_are_validated(self):
        def too_many():
            for index in range(101):
                yield DashboardRecord(str(index), "ready", "test", OBSERVED)

        service = DashboardService(system=too_many, clock=lambda: OBSERVED)
        self.assertEqual(service.snapshot().system[0].failure, "source_invalid")
        with self.assertRaises(DashboardError):
            DashboardRecord("bad", "ready", "test", datetime(2026, 11, 17, 1, 2, 3))


if __name__ == "__main__":
    unittest.main()
