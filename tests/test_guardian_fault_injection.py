import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.guardian.controller import TrustedControllerManager
from jarvis_v2.guardian.cutover import CutoverCoordinator
from jarvis_v2.guardian.fencing import WriterFence, WriterFenceError
from jarvis_v2.guardian.recovery import GuardianRecoveryController
from jarvis_v2.guardian.release import inspect_canary
from jarvis_v2.guardian.rollback import restore_last_known_good, select_last_known_good
from jarvis_v2.guardian.restart import RestartBudget


class GuardianFaultInjectionTests(unittest.TestCase):
    def _controller(self, root: Path, controls: Path, runner):
        executable = root / "guardian-controller"
        executable.write_bytes(b"fault-injection controller")
        executable.chmod(0o700)
        return TrustedControllerManager(
            executable,
            hashlib.sha256(executable.read_bytes()).hexdigest(),
            trusted_root=root,
            control_dir=controls,
            runner=runner,
        )

    def test_p0_controls_survive_recovery_denial(self):
        calls = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            for marker in ("STOP", "PAUSE", "PAUSED_QUOTA"):
                (controls / marker).touch()
            manager = self._controller(root, controls, lambda *args: calls.append(args))
            recovery = GuardianRecoveryController(
                manager, RestartBudget("guardian"), control_dir=controls
            )
            result = recovery.boot(reason="p0 control injection")
            self.assertEqual(result["state"], "safe_mode")
            self.assertEqual(result["control_markers"], ["STOP", "PAUSE", "PAUSED_QUOTA"])
            self.assertEqual(calls, [])
            self.assertTrue(all((controls / marker).exists() for marker in result["control_markers"]))

    def test_p1_crash_loop_is_bounded_and_history_is_retained(self):
        clock = [0.0]
        calls = []

        def crash(*args):
            calls.append(1)
            raise OSError("injected controller crash")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controls = root / "controls"
            controls.mkdir()
            manager = self._controller(root, controls, crash)
            budget = RestartBudget("guardian", max_attempts=2, cooldown_seconds=1, clock=lambda: clock[0])
            recovery = GuardianRecoveryController(manager, budget, control_dir=controls)
            first = recovery.boot(reason="p1 crash", evidence_ref="fault-1")
            clock[0] = 2
            second = recovery.boot(reason="p1 crash", evidence_ref="fault-2")
            clock[0] = 4
            third = recovery.boot(reason="p1 crash", evidence_ref="fault-3")
            self.assertEqual(first["state"], "degraded")
            self.assertEqual(second["state"], "safe_mode")
            self.assertEqual(third["state"], "safe_mode")
            self.assertEqual(len(calls), 2)
            self.assertEqual([item.outcome for item in budget.history], ["failed", "failed"])

    def test_p2_stale_writer_cannot_survive_cutover(self):
        fence = WriterFence(clock=lambda: 100.0)
        primary = fence.acquire("primary")
        digest = hashlib.sha256(b"standby").hexdigest()
        coordinator = CutoverCoordinator(
            fence,
            component_schema="archon.guardian.component/1",
            state_schema="sqlite/5",
            expected_artifact_sha256=digest,
        )
        result = coordinator.cutover(
            primary,
            "standby",
            {
                "component_schema": "archon.guardian.component/1",
                "state_schema": "sqlite/5",
                "artifact_sha256": digest,
                "sync_verified": True,
                "rollback_ready": True,
                "health": "healthy",
                "route_gate": {"mode": "inactive", "single_writer_fenced": True},
            },
            capacity_available=True,
        )
        self.assertTrue(result["old_writer_fenced"])
        with self.assertRaises(WriterFenceError):
            fence.assert_current(primary)
        self.assertEqual(fence.snapshot()["owner_id"], "standby")

    def test_p3_bad_canary_restores_artifact_without_state_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = root / "candidate.bin"
            candidate.write_bytes(b"bad canary")
            previous = root / "last-known-good.bin"
            previous.write_bytes(b"healthy artifact")
            active = root / "active.bin"
            active.write_bytes(candidate.read_bytes())
            state = root / "state.json"
            state.write_text('{"committed":true}\n', encoding="utf-8")
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
                        "rollback_target": active.name,
                        "state_checkpoint": state.name,
                        "candidate_sha": "a" * 40,
                        "base_sha": "b" * 40,
                        "external_watchdog_identity": "watchdog-1",
                        "gates": {key: True for key in (
                            "independent_qc", "tests", "security", "rollback_ready",
                            "owner_approved", "watchdog_ready",
                        )},
                        "evidence_refs": {key: f"{key}-1" for key in (
                            "independent_qc", "tests", "security", "rollback",
                        )},
                        "route_gate": {"mode": "inactive", "single_writer_fenced": True},
                    }
                ),
                encoding="utf-8",
            )
            self.assertTrue(inspect_canary(manifest)["eligible_for_canary"])
            plan = select_last_known_good(manifest, canary_status="failed")
            before = state.read_bytes()
            result = restore_last_known_good(plan)
            self.assertTrue(result["restored"])
            self.assertTrue(result["candidate_preserved"])
            self.assertEqual(active.read_bytes(), previous.read_bytes())
            self.assertEqual(state.read_bytes(), before)

    def test_unverified_cutover_degrades_without_changing_authority(self):
        fence = WriterFence(clock=lambda: 100.0)
        primary = fence.acquire("primary")
        coordinator = CutoverCoordinator(
            fence,
            component_schema="archon.guardian.component/1",
            state_schema="sqlite/5",
            expected_artifact_sha256="a" * 64,
        )
        decision = coordinator.prepare(
            {"health": "unknown", "sync_verified": False}, capacity_available=True
        )
        self.assertEqual(decision.state, "degraded")
        self.assertFalse(decision.allowed)
        fence.assert_current(primary)


if __name__ == "__main__":
    unittest.main()
