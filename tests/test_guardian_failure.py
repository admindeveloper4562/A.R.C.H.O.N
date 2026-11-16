import unittest

from jarvis_v2.guardian import (
    FailureClassificationError,
    FailureClassifier,
    ProbeResult,
)


class GuardianFailureTests(unittest.TestCase):
    def setUp(self):
        self.classifier = FailureClassifier()
        self.ok = ProbeResult(True, "healthy", 2)
        self.failed = ProbeResult(False, "failed", 20)

    def test_component_failure_requires_healthy_upstream_observations(self):
        assessment = self.classifier.classify(
            "atlas-sda",
            component=self.failed,
            dependencies={"atlas-core": self.ok},
            host=self.ok,
            evidence_refs=("probe-1",),
        )

        self.assertEqual(assessment.category, "component_failure")
        self.assertEqual(assessment.severity, "high")
        self.assertEqual(assessment.root_cause, "atlas-sda")
        self.assertTrue(assessment.evidence_complete)

    def test_dependency_failure_correlates_to_the_first_upstream_root(self):
        assessment = self.classifier.classify(
            "atlas-sda",
            component=self.failed,
            dependencies={"atlas-core": self.failed, "atlas-backend": self.ok},
            host=self.ok,
            evidence_refs=("probe-2",),
        )

        self.assertEqual(assessment.category, "dependency_outage")
        self.assertEqual(assessment.root_cause, "atlas-core")
        self.assertEqual(assessment.severity, "high")

    def test_host_failure_takes_precedence_over_component_and_dependency(self):
        assessment = self.classifier.classify(
            "atlas-sda",
            component=self.failed,
            dependencies={"atlas-core": self.failed},
            host=self.failed,
            evidence_refs=("host-probe", "component-probe"),
        )

        self.assertEqual(assessment.category, "host_outage")
        self.assertEqual(assessment.root_cause, "host")
        self.assertEqual(assessment.severity, "critical")

    def test_unknown_upstream_state_is_not_called_a_component_failure(self):
        assessment = self.classifier.classify(
            "atlas-sda",
            component=self.failed,
            dependencies={"atlas-core": ProbeResult(False, "unknown", 0)},
            host=None,
        )

        self.assertEqual(assessment.category, "unknown")
        self.assertEqual(assessment.severity, "warning")
        self.assertFalse(assessment.evidence_complete)

    def test_healthy_observations_are_not_failures(self):
        assessment = self.classifier.classify(
            "atlas-sda",
            component=self.ok,
            dependencies={"atlas-core": True},
            host=True,
            evidence_refs=("health-probe",),
        )

        self.assertEqual(assessment.category, "healthy")
        self.assertEqual(assessment.severity, "none")
        self.assertEqual(assessment.root_cause, "none")

    def test_malformed_observations_and_evidence_are_rejected(self):
        with self.assertRaises(FailureClassificationError):
            self.classifier.classify("atlas-sda", component=True)
        with self.assertRaises(FailureClassificationError):
            self.classifier.classify("atlas-sda", component=self.ok, evidence_refs="raw")
        with self.assertRaises(FailureClassificationError):
            self.classifier.classify("atlas-sda", component=self.ok, dependencies={"bad name": True})


if __name__ == "__main__":
    unittest.main()
