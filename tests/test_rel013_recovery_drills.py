import hashlib
import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.automation.recovery_drill import RecoveryDrill
from jarvis_v2.backend import BackupError, BackupManager, EventBus
from jarvis_v2.guardian.controller import TrustedControllerManager
from jarvis_v2.guardian.recovery import GuardianRecoveryController
from jarvis_v2.guardian.restart import RestartBudget
from jarvis_v2.guardian.rollback import restore_last_known_good, select_last_known_good
from tools.import_legacy import prepare_manifest


class Rel013RecoveryDrillTests(unittest.TestCase):
    def _git(self, repository: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repository), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _legacy_source(self, root: Path) -> tuple[Path, str]:
        repository = root / "legacy-source"
        repository.mkdir()
        self._git(repository, "init", "-q", "-b", "develop")
        self._git(repository, "config", "user.name", "REL-013 test")
        self._git(repository, "config", "user.email", "rel013@local.invalid")
        (repository / "source.py").write_text("answer = 42\n", encoding="utf-8")
        self._git(repository, "add", "--", "source.py")
        self._git(repository, "commit", "-qm", "pinned source")
        source_sha = self._git(repository, "rev-parse", "HEAD")
        self._git(repository, "remote", "add", "origin", "https://github.com/admindeveloper4562/personal-jarvis.git")
        self._git(repository, "update-ref", "refs/remotes/origin/develop", source_sha)
        return repository, source_sha

    def _destination(self, root: Path) -> tuple[Path, str]:
        destination = root / "destination"
        destination.mkdir()
        self._git(destination, "init", "-q", "-b", "develop")
        self._git(destination, "config", "user.name", "REL-013 destination")
        self._git(destination, "config", "user.email", "rel013-destination@local.invalid")
        (destination / "README.md").write_text("last-known-good\n", encoding="utf-8")
        self._git(destination, "add", "--", "README.md")
        self._git(destination, "commit", "-qm", "destination base")
        return destination, self._git(destination, "rev-parse", "HEAD")

    def _release_manifest(self, root: Path) -> Path:
        candidate = root / "candidate.bin"
        previous = root / "last-known-good.bin"
        target = root / "active.bin"
        state = root / "state.json"
        candidate.write_bytes(b"failed candidate")
        previous.write_bytes(b"known-good artifact")
        target.write_bytes(candidate.read_bytes())
        state.write_text('{"checkpoint":"known-good"}\n', encoding="utf-8")
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        manifest = root / "release.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema": "jarvis-v2.release-candidate/1",
                    "module": "guardian",
                    "artifact": candidate.name,
                    "sha256": digest(candidate),
                    "previous_healthy_artifact": previous.name,
                    "previous_healthy_artifact_sha256": digest(previous),
                    "rollback_target": target.name,
                    "state_checkpoint": state.name,
                    "candidate_sha": "a" * 40,
                    "base_sha": "b" * 40,
                    "external_watchdog_identity": "rel013-watchdog",
                    "gates": {
                        "independent_qc": True,
                        "tests": True,
                        "security": True,
                        "rollback_ready": True,
                        "owner_approved": True,
                        "watchdog_ready": True,
                    },
                    "evidence_refs": {
                        "independent_qc": "qc-rel013",
                        "tests": "tests-rel013",
                        "security": "security-rel013",
                        "rollback": "rollback-rel013",
                    },
                    "route_gate": {"mode": "inactive", "single_writer_fenced": True},
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def test_pinned_migration_dry_run_apply_and_verified_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, source_sha = self._legacy_source(root)
            destination, destination_base = self._destination(root)
            manifest = {
                "schema": "jarvis-v2.legacy-import/1",
                "expected_source_commit": source_sha,
                "entries": [{
                    "area": "core",
                    "ref": "develop",
                    "source": "source.py",
                    "target": "migration/imported/core/source.py",
                }],
            }
            dry_run = prepare_manifest(source, destination, manifest)
            self.assertTrue(dry_run["dry_run"])
            self.assertFalse((destination / "migration").exists())
            self.assertEqual(self._git(source, "status", "--porcelain"), "")
            applied = prepare_manifest(source, destination, manifest, apply=True)
            self.assertEqual(applied["entries"][0]["source_commit"], source_sha)
            provenance = json.loads(
                (destination / "migration/provenance/import-log.json").read_text(encoding="utf-8")
            )
            self.assertEqual(provenance["entries"][0]["source_commit"], source_sha)
            self.assertEqual(provenance["entries"][0]["sha256"], dry_run["entries"][0]["sha256"])
            self.assertEqual(self._git(destination, "rev-parse", "HEAD"), destination_base)
            self.assertEqual(self._git(source, "status", "--porcelain"), "")

            release_manifest = self._release_manifest(root)
            state_before = (root / "state.json").read_bytes()
            plan = select_last_known_good(release_manifest, canary_status="failed")
            result = restore_last_known_good(plan)
            self.assertTrue(result["restored"])
            self.assertTrue(result["candidate_preserved"])
            self.assertTrue(result["state_preserved"])
            self.assertEqual((root / "active.bin").read_bytes(), b"known-good artifact")
            self.assertEqual((root / "state.json").read_bytes(), state_before)

    def test_recovery_backup_replay_and_corruption_are_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = root / "events.sqlite"
            backup = root / "events.backup.sqlite"
            restored = root / "events.restored.sqlite"
            with EventBus(database) as bus:
                event = bus.publish(
                    "automation.job", "automation", "rel013-job", 1,
                    {"state": "retained"}, correlation_id="rel013-correlation",
                    idempotency_key="rel013-job",
                )
            drill = RecoveryDrill(database)
            receipt = drill.backup(backup)
            restored_receipt = drill.restore(backup, restored)
            self.assertEqual(receipt.integrity, "ok")
            self.assertEqual(restored_receipt.integrity, "ok")
            self.assertEqual(drill.inspect()["integrity"], "ok")
            calls: list[str] = []
            replayed = RecoveryDrill(restored).replay_pending(
                "rel013-worker",
                lambda received: calls.append(received.event_id) or {"accepted": True},
            )
            self.assertEqual([item.event_id for item in replayed], [event.event_id])
            self.assertEqual(calls, [event.event_id])
            self.assertEqual(
                RecoveryDrill(restored).replay_pending(
                    "rel013-worker",
                    lambda received: calls.append(received.event_id) or {"accepted": True},
                ),
                [],
            )
            self.assertEqual(calls, [event.event_id])

            corrupted = root / "events.corrupted.sqlite"
            corrupted.write_bytes(backup.read_bytes()[:-1] + b"X")
            with self.assertRaises(BackupError):
                BackupManager().restore(
                    corrupted, root / "corrupted-restored.sqlite",
                    expected_sha256=receipt.backup_sha256,
                )
            self.assertFalse((root / "corrupted-restored.sqlite").exists())

    def test_provider_outage_crash_and_stop_controls_fence_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controller = root / "controller.sh"
            controller.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            controller.chmod(0o700)
            digest = hashlib.sha256(controller.read_bytes()).hexdigest()
            calls: list[tuple[str, ...]] = []

            def failed_runner(command, _cwd):
                calls.append(command)
                raise OSError("simulated provider outage")

            controls = root / "controls"
            controls.mkdir()
            budget = RestartBudget(
                "rel013-controller", max_attempts=2, cooldown_seconds=1, clock=lambda: 0.0
            )
            manager = TrustedControllerManager(
                controller, digest, trusted_root=root, control_dir=controls, runner=failed_runner
            )
            recovery = GuardianRecoveryController(manager, budget, control_dir=controls)
            (controls / "STOP").touch()
            stopped = recovery.boot(reason="system crash", evidence_ref="rel013-crash")
            self.assertEqual(stopped["state"], "safe_mode")
            self.assertFalse(stopped["started"])
            self.assertEqual(stopped["control_markers"], ["STOP"])
            self.assertEqual(calls, [])
            (controls / "STOP").unlink()

            failed = recovery.boot(reason="provider outage", evidence_ref="rel013-outage")
            self.assertEqual(failed["reason"], "controller_start_failed")
            self.assertFalse(failed["started"])
            self.assertEqual(len(calls), 1)
            self.assertEqual(budget.history[-1].outcome, "failed")

            pending_budget = RestartBudget(
                "rel013-duplicate", max_attempts=2, cooldown_seconds=1, clock=lambda: 0.0
            )
            self.assertTrue(pending_budget.request(reason="crash", evidence_ref="rel013-a").allowed)
            duplicate = pending_budget.request(reason="duplicate", evidence_ref="rel013-b")
            self.assertFalse(duplicate.allowed)
            self.assertEqual(duplicate.reason, "restart_attempt_unreconciled")

    def test_unsafe_migration_and_rollback_inputs_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, source_sha = self._legacy_source(root)
            destination, _ = self._destination(root)
            unsafe = {
                "schema": "jarvis-v2.legacy-import/1",
                "expected_source_commit": source_sha,
                "entries": [{
                    "area": "core", "ref": "develop", "source": "source.py",
                    "target": "../outside.py",
                }],
            }
            with self.assertRaises(ValueError):
                prepare_manifest(source, destination, unsafe, apply=True)
            self.assertFalse((destination / "migration").exists())

            manifest = self._release_manifest(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["rollback_target"] = "../outside.bin"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(Exception, "unsafe"):
                select_last_known_good(manifest, canary_status="failed")


if __name__ == "__main__":
    unittest.main()
