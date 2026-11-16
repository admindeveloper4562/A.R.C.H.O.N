import hashlib
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.guardian.cutover import CutoverCoordinator, CutoverError
from jarvis_v2.guardian.fencing import WriterFence


class GuardianCutoverTests(unittest.TestCase):
    def setUp(self):
        self.fence = WriterFence(clock=lambda: 100.0)
        self.primary = self.fence.acquire("primary")
        self.digest = hashlib.sha256(b"standby").hexdigest()
        self.coordinator = CutoverCoordinator(
            self.fence,
            component_schema="archon.guardian.component/1",
            state_schema="sqlite/5",
            expected_artifact_sha256=self.digest,
        )

    def _readiness(self, **changes):
        readiness = {
            "component_schema": "archon.guardian.component/1",
            "state_schema": "sqlite/5",
            "artifact_sha256": self.digest,
            "sync_verified": True,
            "rollback_ready": True,
            "health": "healthy",
            "route_gate": {"mode": "inactive", "single_writer_fenced": True},
        }
        readiness.update(changes)
        return readiness

    def test_ready_cutover_fences_old_writer_and_keeps_one_authority(self):
        result = self.coordinator.cutover(
            self.primary,
            "standby",
            self._readiness(),
            capacity_available=True,
        )
        self.assertTrue(result["old_writer_fenced"])
        self.assertFalse(result["route_switched"])
        with self.assertRaisesRegex(ValueError, "stale"):
            self.fence.assert_current(self.primary)
        self.assertEqual(self.fence.snapshot()["owner_id"], "standby")

    def test_unverified_sync_degrades_without_handoff(self):
        decision = self.coordinator.prepare(
            self._readiness(sync_verified=False), capacity_available=True
        )
        self.assertEqual(decision.state, "degraded")
        self.assertFalse(decision.allowed)
        with self.assertRaisesRegex(CutoverError, "sync_not_verified"):
            self.coordinator.cutover(
                self.primary,
                "standby",
                self._readiness(sync_verified=False),
                capacity_available=True,
            )
        self.fence.assert_current(self.primary)

    def test_capacity_and_schema_mismatch_do_not_fabricate_readiness(self):
        decision = self.coordinator.prepare(
            self._readiness(state_schema="sqlite/4"), capacity_available=False
        )
        self.assertFalse(decision.allowed)
        self.assertIn("state_schema_mismatch", decision.reasons)
        self.assertIn("capacity_unavailable", decision.reasons)
        self.fence.assert_current(self.primary)

    def test_failback_requires_failed_health_and_fences_bad_standby(self):
        standby = self.fence.handoff(self.primary, "standby")
        with self.assertRaisesRegex(CutoverError, "failed or unhealthy"):
            self.coordinator.failback(
                standby,
                "primary",
                self._readiness(),
                capacity_available=True,
            )
        result = self.coordinator.failback(
            standby,
            "primary",
            self._readiness(health="failed"),
            capacity_available=True,
        )
        self.assertTrue(result["failed_writer_fenced"])
        self.assertEqual(self.fence.snapshot()["owner_id"], "primary")

    def test_control_marker_blocks_cutover(self):
        with tempfile.TemporaryDirectory() as directory:
            controls = Path(directory)
            (controls / "PAUSE").touch()
            coordinator = CutoverCoordinator(
                self.fence,
                component_schema="archon.guardian.component/1",
                state_schema="sqlite/5",
                expected_artifact_sha256=self.digest,
                control_dir=controls,
            )
            with self.assertRaisesRegex(CutoverError, "PAUSE"):
                coordinator.cutover(
                    self.primary,
                    "standby",
                    self._readiness(),
                    capacity_available=True,
                )


if __name__ == "__main__":
    unittest.main()
