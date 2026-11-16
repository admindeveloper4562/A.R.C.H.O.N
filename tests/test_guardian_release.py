import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.guardian.release import inspect_canary


class GuardianReleaseTests(unittest.TestCase):
    def _manifest(self, root: Path) -> Path:
        artifact = root / "candidate.bin"
        artifact.write_bytes(b"accepted guardian candidate")
        manifest = root / "candidate.json"
        data = {
            "schema": "jarvis-v2.release-candidate/1",
            "module": "guardian",
            "artifact": artifact.name,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
            "previous_healthy_artifact_sha256": "b" * 64,
            "candidate_sha": "a" * 40,
            "base_sha": "c" * 40,
            "external_watchdog_identity": "watchdog-1",
            "gates": {
                "independent_qc": True,
                "tests": True,
                "security": True,
                "rollback_ready": True,
                "owner_approved": True,
                "watchdog_ready": True,
            },
            "evidence_refs": {
                "independent_qc": "qc-1",
                "tests": "tests-1",
                "security": "security-1",
                "rollback": "rollback-1",
            },
            "route_gate": {"mode": "inactive", "single_writer_fenced": True},
        }
        manifest.write_text(json.dumps(data), encoding="utf-8")
        return manifest

    def test_only_evidence_bound_candidate_with_closed_route_is_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            result = inspect_canary(self._manifest(Path(directory)))
            self.assertTrue(result["eligible_for_canary"])
            self.assertFalse(result["route_switched"])

    def test_missing_qc_evidence_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            data = json.loads(manifest.read_text())
            del data["evidence_refs"]["independent_qc"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = inspect_canary(manifest)
            self.assertFalse(result["eligible_for_canary"])
            self.assertIn("invalid independent_qc evidence reference", result["canary_reasons"])

    def test_open_or_extended_route_gate_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self._manifest(Path(directory))
            data = json.loads(manifest.read_text())
            data["route_gate"] = {"mode": "active", "single_writer_fenced": True}
            manifest.write_text(json.dumps(data), encoding="utf-8")
            result = inspect_canary(manifest)
            self.assertFalse(result["eligible_for_canary"])
            self.assertIn("route gate is not closed", result["canary_reasons"])

    def test_artifact_change_invalidates_canary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._manifest(root)
            (root / "candidate.bin").write_bytes(b"changed")
            result = inspect_canary(manifest)
            self.assertFalse(result["eligible_for_canary"])
            self.assertIn("artifact checksum mismatch", result["canary_reasons"])


if __name__ == "__main__":
    unittest.main()
