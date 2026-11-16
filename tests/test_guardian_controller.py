import hashlib
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.guardian import GuardianControllerError, TrustedControllerManager


class GuardianControllerTests(unittest.TestCase):
    def _manager(self, root: Path, *, runner=None, control_dir=None):
        artifact = root / "trusted" / "controller"
        artifact.parent.mkdir()
        artifact.write_bytes(b"trusted controller\n")
        artifact.chmod(0o700)
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        return TrustedControllerManager(
            artifact,
            digest,
            trusted_root=artifact.parent,
            control_dir=control_dir,
            runner=runner,
        )

    def test_verified_artifact_is_the_only_launchable_controller(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []
            root = Path(directory)
            manager = self._manager(
                root,
                runner=lambda command, cwd: calls.append((command, cwd)) or 4312,
            )
            self.assertTrue(manager.verify()["trusted"])
            result = manager.restart()
            self.assertEqual(result["status"], "started")
            self.assertEqual(result["pid"], 4312)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][0], (str(root / "trusted" / "controller"),))

    def test_digest_change_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manager = self._manager(root)
            artifact = root / "trusted" / "controller"
            artifact.write_bytes(b"changed\n")
            self.assertEqual(manager.verify()["reason"], "controller_digest_mismatch")
            with self.assertRaises(GuardianControllerError):
                manager.restart()
            artifact.unlink()
            artifact.symlink_to(root / "other")
            (root / "other").write_bytes(b"trusted controller\n")
            self.assertEqual(manager.verify()["reason"], "controller_symlink")

    def test_control_markers_are_honored_before_artifact_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            manager = self._manager(root, control_dir=controls)
            (controls / "PAUSE").touch()
            self.assertEqual(manager.verify()["reason"], "control_marker_active")
            with self.assertRaises(GuardianControllerError):
                manager.restart()

    def test_command_must_be_direct_and_artifact_must_be_private_to_group(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "trusted" / "controller"
            artifact.parent.mkdir()
            artifact.write_bytes(b"trusted controller\n")
            artifact.chmod(0o776)
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            with self.assertRaises(GuardianControllerError):
                TrustedControllerManager(
                    artifact,
                    digest,
                    trusted_root=artifact.parent,
                    command=("/bin/sh", "-c", str(artifact)),
                )
            self.assertEqual(
                TrustedControllerManager(
                    artifact,
                    digest,
                    trusted_root=artifact.parent,
                ).verify()["reason"],
                "controller_writable_by_other_identity",
            )


if __name__ == "__main__":
    unittest.main()
