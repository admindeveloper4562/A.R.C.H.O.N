from datetime import datetime, timezone
import unittest

from jarvis_v2.runtime import (
    ACCEPTANCE_GATES,
    HostAcceptanceRecord,
    HostQualificationError,
    build_host_qualification_report,
)


class RuntimeQualificationTests(unittest.TestCase):
    def checks(self, status="passed"):
        return tuple(
            HostAcceptanceRecord(
                gate,
                status,
                f"local:run-018/{gate}",
                commands=(f"probe {gate}",),
                exit_code=0 if status == "passed" else None,
            )
            for gate in ACCEPTANCE_GATES
        )

    def test_report_requires_all_gates_and_preserves_unresolved_host_evidence(self):
        report = build_host_qualification_report(
            "ubuntu-local",
            "Ubuntu 24.04",
            "a" * 40,
            self.checks("blocked"),
            captured_at=datetime(2026, 11, 17, tzinfo=timezone.utc),
        )
        self.assertFalse(report.all_passed)
        self.assertEqual(report.unresolved_gates, ACCEPTANCE_GATES)
        self.assertEqual(report.as_dict()["checks"][0]["status"], "blocked")

    def test_missing_or_duplicate_gate_is_rejected(self):
        checks = self.checks()
        with self.assertRaisesRegex(HostQualificationError, "exactly twelve"):
            build_host_qualification_report("ubuntu-local", "Ubuntu 24.04", "a" * 40, checks[:-1])
        with self.assertRaisesRegex(HostQualificationError, "exactly once"):
            build_host_qualification_report(
                "ubuntu-local", "Ubuntu 24.04", "a" * 40,
                (*checks[:-1], checks[0]),
            )

    def test_passed_record_cannot_hide_failed_command(self):
        with self.assertRaisesRegex(HostQualificationError, "failing exit code"):
            HostAcceptanceRecord(
                "AC-04", "passed", "local:firefox", commands=("firefox --version",), exit_code=1
            )

    def test_raw_multiline_output_is_not_accepted_as_evidence(self):
        with self.assertRaisesRegex(HostQualificationError, "evidence reference"):
            HostAcceptanceRecord("AC-05", "blocked", "raw microphone output\n")


if __name__ == "__main__":
    unittest.main()
