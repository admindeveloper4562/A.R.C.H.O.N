import hashlib
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.guardian.standby import StandbyError, StandbyLauncher


class GuardianStandbyTests(unittest.TestCase):
    def _launcher(self, root: Path, runner):
        executable = root / "standby-controller"
        executable.write_bytes(b"trusted standby")
        executable.chmod(0o700)
        return StandbyLauncher(
            executable,
            hashlib.sha256(executable.read_bytes()).hexdigest(),
            trusted_root=root,
            component_schema="archon.guardian.component/1",
            state_schema="sqlite/5",
            runner=runner,
        )

    def test_matching_schema_and_explicit_capacity_start_is_isolated(self):
        calls = []

        def runner(command, cwd):
            calls.append((command, cwd))
            return 42

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            launcher = self._launcher(root, runner)
            result = launcher.start(
                component_schema="archon.guardian.component/1",
                state_schema="sqlite/5",
                capacity_available=True,
            )
            self.assertEqual(result["status"], "started")
            self.assertTrue(result["isolated"])
            self.assertFalse(result["automatic_capacity"])
            self.assertEqual(calls[0][1], root)

    def test_capacity_is_not_assumed_or_probed(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            launcher = self._launcher(root, lambda *args: calls.append(args))
            decision = launcher.inspect(
                component_schema="archon.guardian.component/1",
                state_schema="sqlite/5",
                capacity_available=False,
            )
            self.assertFalse(decision["eligible"])
            self.assertIn("capacity_unavailable", decision["reasons"])
            self.assertEqual(calls, [])

    def test_schema_and_state_mismatch_do_not_start(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            launcher = self._launcher(Path(directory), lambda *args: calls.append(args))
            with self.assertRaisesRegex(StandbyError, "component_schema_mismatch"):
                launcher.start(
                    component_schema="wrong/1",
                    state_schema="sqlite/4",
                    capacity_available=True,
                )
            self.assertEqual(calls, [])

    def test_active_control_marker_blocks_start(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            control = root / "controls"
            control.mkdir()
            (control / "PAUSE").touch()
            executable = root / "standby-controller"
            executable.write_bytes(b"trusted standby")
            executable.chmod(0o700)
            launcher = StandbyLauncher(
                executable,
                hashlib.sha256(executable.read_bytes()).hexdigest(),
                trusted_root=root,
                control_dir=control,
                component_schema="archon.guardian.component/1",
                state_schema="sqlite/5",
                runner=lambda *args: calls.append(args),
            )
            with self.assertRaisesRegex(StandbyError, "control_marker_active"):
                launcher.start(
                    component_schema="archon.guardian.component/1",
                    state_schema="sqlite/5",
                    capacity_available=True,
                )
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
