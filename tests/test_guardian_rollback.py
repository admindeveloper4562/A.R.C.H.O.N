import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.guardian.rollback import (
    RollbackError,
    restore_last_known_good,
    select_last_known_good,
)


class GuardianRollbackTests(unittest.TestCase):
    def _manifest(self, root: Path) -> Path:
        candidate = root / "candidate.bin"
        candidate.write_bytes(b"failed canary")
        previous = root / "last-known-good.bin"
        previous.write_bytes(b"healthy release")
        target = root / "active.bin"
        target.write_bytes(candidate.read_bytes())
        state = root / "state.json"
        state.write_text('{"committed": true}\n', encoding="utf-8")
        manifest = root / "candidate.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema": "jarvis-v2.release-candidate/1",
                    "module": "guardian",
                    "artifact": candidate.name,
                    "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
                    "previous_healthy_artifact": previous.name,
                    "previous_healthy_artifact_sha256": hashlib.sha256(
                        previous.read_bytes()
                    ).hexdigest(),
                    "rollback_target": target.name,
                    "state_checkpoint": state.name,
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
            ),
            encoding="utf-8",
        )
        return manifest

    def test_failed_canary_restores_last_known_good_and_preserves_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._manifest(root)
            state_before = (root / "state.json").read_bytes()
            plan = select_last_known_good(manifest, canary_status="failed")
            self.assertEqual((root / "active.bin").read_bytes(), b"failed canary")

            result = restore_last_known_good(plan)

            self.assertTrue(result["restored"])
            self.assertTrue(result["candidate_preserved"])
            self.assertTrue(result["state_preserved"])
            self.assertEqual((root / "active.bin").read_bytes(), b"healthy release")
            self.assertEqual((root / "state.json").read_bytes(), state_before)

    def test_healthy_canary_cannot_trigger_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RollbackError, "failed or unhealthy"):
                select_last_known_good(self._manifest(Path(directory)), canary_status="healthy")

    def test_tampered_last_known_good_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._manifest(root)
            (root / "last-known-good.bin").write_bytes(b"tampered")
            with self.assertRaisesRegex(RollbackError, "checksum mismatch"):
                select_last_known_good(manifest, canary_status="unhealthy")

    def test_unsafe_path_and_target_mismatch_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._manifest(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["rollback_target"] = "../outside.bin"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RollbackError, "unsafe"):
                select_last_known_good(manifest, canary_status="failed")

            manifest = self._manifest(root)
            (root / "active.bin").write_bytes(b"unknown active state")
            with self.assertRaisesRegex(RollbackError, "does not match"):
                select_last_known_good(manifest, canary_status="failed")


if __name__ == "__main__":
    unittest.main()
