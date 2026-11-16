import unittest

from jarvis_v2.guardian import (
    GuardianHealthError,
    GuardianHealthEvaluator,
    ProbeResult,
)


class GuardianHealthTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = GuardianHealthEvaluator()
        self.failed = ProbeResult(False, "timeout", 20)
        self.healthy = ProbeResult(True, "ok", 2)

    def test_failed_probe_waits_when_dependency_was_not_checked(self):
        evidence = self.evaluator.assess(
            "atlas-sda",
            liveness=self.failed,
            readiness=self.failed,
            required_dependencies=("atlas-core",),
            dependencies={},
        )
        self.assertEqual(evidence.state, "dependency_unknown")
        self.assertEqual(evidence.reason, "dependency_not_checked")
        self.assertFalse(evidence.dependencies_checked)
        self.assertFalse(evidence.restart_allowed)

    def test_failed_dependency_blocks_restart_after_failed_probe(self):
        evidence = self.evaluator.assess(
            "atlas-sda",
            liveness=self.failed,
            readiness=self.failed,
            required_dependencies=("atlas-core",),
            dependencies={"atlas-core": False},
        )
        self.assertEqual(evidence.state, "dependency_wait")
        self.assertEqual(evidence.reason, "dependency_failed")
        self.assertFalse(evidence.restart_allowed)

    def test_failed_probe_is_restartable_only_after_healthy_dependencies(self):
        evidence = self.evaluator.assess(
            "atlas-sda",
            liveness=self.failed,
            readiness=self.healthy,
            required_dependencies=("atlas-core",),
            dependencies={"atlas-core": True},
        )
        self.assertEqual(evidence.state, "restartable")
        self.assertEqual(evidence.reason, "probe_failed_after_dependency_check")
        self.assertTrue(evidence.dependencies_checked)
        self.assertTrue(evidence.restart_allowed)

    def test_healthy_component_does_not_request_restart(self):
        evidence = self.evaluator.assess(
            "atlas-sda",
            liveness=self.healthy,
            readiness=self.healthy,
            required_dependencies=("atlas-core",),
            dependencies={"atlas-core": self.healthy},
        )
        self.assertEqual(evidence.state, "healthy")
        self.assertFalse(evidence.restart_allowed)
        self.assertEqual(evidence.as_dict()["dependencies"]["atlas-core"]["ok"], True)

    def test_restart_policy_and_budget_are_bounded(self):
        disabled = self.evaluator.assess(
            "atlas-sda",
            liveness=self.failed,
            readiness=self.failed,
            restart_enabled=False,
        )
        exhausted = self.evaluator.assess(
            "atlas-sda",
            liveness=self.failed,
            readiness=self.failed,
            restart_attempts=3,
            max_restart_attempts=3,
        )
        self.assertEqual(disabled.reason, "restart_disabled")
        self.assertEqual(exhausted.reason, "restart_budget_exhausted")
        self.assertFalse(disabled.restart_allowed)
        self.assertFalse(exhausted.restart_allowed)

    def test_malformed_observations_and_dependency_sets_are_rejected(self):
        with self.assertRaises(GuardianHealthError):
            ProbeResult(False, "bad\nreason")
        with self.assertRaises(GuardianHealthError):
            self.evaluator.assess(
                "atlas-sda",
                liveness=self.healthy,
                readiness=self.healthy,
                required_dependencies=("atlas-core", "atlas-core"),
            )
        with self.assertRaises(GuardianHealthError):
            self.evaluator.assess(
                "atlas-sda",
                liveness=self.healthy,
                readiness=self.healthy,
                restart_attempts=6,
            )


if __name__ == "__main__":
    unittest.main()
