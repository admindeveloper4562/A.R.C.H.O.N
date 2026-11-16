import hashlib
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.guardian.controller import TrustedControllerManager
from jarvis_v2.guardian.recovery import GuardianRecoveryController, RecoveryError
from jarvis_v2.guardian.restart import RestartBudget


class GuardianRecoveryTests(unittest.TestCase):
    def _controller(self, root: Path, runner, controls: Path):
        executable = root / "guardian-controller"
        executable.write_bytes(b"trusted controller")
        executable.chmod(0o700)
        return TrustedControllerManager(
            executable,
            hashlib.sha256(executable.read_bytes()).hexdigest(),
            trusted_root=root,
            control_dir=controls,
            runner=runner,
        )

    def test_one_verified_boot_attempt_starts_controller(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            manager = self._controller(root, lambda command, cwd: calls.append((command, cwd)) or 41, controls)
            budget = RestartBudget("guardian", max_attempts=2, cooldown_seconds=1, clock=lambda: 0)
            result = GuardianRecoveryController(manager, budget, control_dir=controls).boot(
                reason="initial boot", evidence_ref="boot-1"
            )
            self.assertEqual(result["state"], "running")
            self.assertTrue(result["started"])
            self.assertEqual(len(calls), 1)

    def test_crash_loop_enters_safe_mode_at_bounded_attempt_limit(self):
        now = [0.0]
        calls = []

        def crash(command, cwd):
            calls.append(1)
            raise OSError("injected crash")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            manager = self._controller(root, crash, controls)
            budget = RestartBudget("guardian", max_attempts=2, cooldown_seconds=1, clock=lambda: now[0])
            recovery = GuardianRecoveryController(manager, budget, control_dir=controls)
            first = recovery.boot(reason="crash", evidence_ref="run-1")
            now[0] = 2
            second = recovery.boot(reason="crash", evidence_ref="run-2")
            now[0] = 4
            third = recovery.boot(reason="crash", evidence_ref="run-3")
            self.assertEqual(first["state"], "degraded")
            self.assertEqual(second["state"], "safe_mode")
            self.assertEqual(third["state"], "safe_mode")
            self.assertEqual(len(calls), 2)

    def test_stop_quota_and_approval_are_preserved(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            (controls / "STOP").touch()
            (controls / "PAUSED_QUOTA").touch()
            manager = self._controller(root, lambda *args: calls.append(args), controls)
            recovery = GuardianRecoveryController(
                manager,
                RestartBudget("guardian"),
                control_dir=controls,
            )
            result = recovery.boot(reason="blocked", approval_required=True)
            self.assertEqual(result["state"], "safe_mode")
            self.assertEqual(result["control_markers"], ["STOP", "PAUSED_QUOTA"])
            self.assertTrue(result["approval_required"])
            self.assertEqual(calls, [])
            self.assertTrue((controls / "STOP").exists())
            self.assertTrue((controls / "PAUSED_QUOTA").exists())

    def test_invalid_request_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            manager = self._controller(root, lambda *args: 1, controls)
            recovery = GuardianRecoveryController(manager, RestartBudget("guardian"))
            with self.assertRaises(RecoveryError):
                recovery.boot(reason="", approval_required=False)


if __name__ == "__main__":
    unittest.main()
