from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jarvis_v2.native_controller import NativeController


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "operations" / "ARCHON_LINUX_RELEASE.md"


def _backup_python(document: str) -> str:
    command = "docker compose exec -T archon python - > \"$backup\" <<'PY'"
    start = document.index(command) + len(command)
    end = document.index("\nPY\n~~~", start)
    return document[start + 1:end]


def _restore_python(document: str) -> str:
    command = "--entrypoint python archon -c '"
    start = document.index(command) + len(command)
    end = document.index("\n'\ndocker compose -p \"$project\" up -d", start)
    return document[start:end]


class LinuxReleaseRunbookTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "linux", "Linux container paths and controller lock semantics")
    def test_backup_restore_snippets_preserve_controls_and_restore_safe_mode(self) -> None:
        document = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("Before any marker removal, reconcile its origin and owner intent", document)
        self.assertIn("record the authorized reconciliation and audit receipt", document)
        self.assertIn("The controller must enter safe_mode while any marker remains present", document)
        backup_script = _backup_python(document)
        restore_script = _restore_python(document)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_state = root / "source-state"
            source_workspace = root / "source-workspace"
            source_controls = source_state / "controls"
            source_controls.mkdir(parents=True, mode=0o700)
            source_workspace.mkdir(mode=0o700)
            markers = {
                "STOP": "owner requested stop\n",
                "PAUSE": "maintenance pause\n",
                "PAUSED_QUOTA": "quota exhausted\n",
            }
            for name, content in markers.items():
                marker = source_controls / name
                marker.write_text(content, encoding="utf-8")
                marker.chmod(0o600)

            backup_path = root / "state-backup.tar.gz"
            environment = os.environ.copy()
            environment["ARCHON_STATE"] = str(source_state)
            environment["ARCHON_WORKSPACE"] = str(source_workspace)
            backup = subprocess.run(
                [sys.executable, "-c", backup_script],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                check=False,
            )
            self.assertEqual(backup.returncode, 0, backup.stderr.decode(errors="replace"))
            backup_path.write_bytes(backup.stdout)

            restored_state = root / "restored-state"
            restored_workspace = root / "restored-workspace"
            environment["ARCHON_STATE"] = str(restored_state)
            environment["ARCHON_WORKSPACE"] = str(restored_workspace)
            environment["ARCHON_RESTORE_ARCHIVE"] = str(backup_path)
            restored = subprocess.run(
                [sys.executable, "-c", restore_script],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                check=False,
            )
            self.assertEqual(restored.returncode, 0, restored.stderr.decode(errors="replace"))

            controls = restored_state / "controls"
            self.assertEqual(controls.stat().st_mode & 0o777, 0o700)
            for name, content in markers.items():
                marker = controls / name
                self.assertTrue(marker.is_file(), name)
                self.assertEqual(marker.read_text(encoding="utf-8"), content)
                self.assertEqual(marker.stat().st_mode & 0o777, 0o600)

            with NativeController(restored_state) as controller:
                result = controller.run_once()
                self.assertEqual(result["state"], "safe_mode")
                self.assertEqual(result["reason"], "control_marker_active")
                self.assertEqual(result["controls"], ["STOP", "PAUSE", "PAUSED_QUOTA"])
                self.assertEqual(controller.active_controls(), ("STOP", "PAUSE", "PAUSED_QUOTA"))

    @unittest.skipUnless(sys.platform == "linux", "Linux container paths and controller lock semantics")
    def test_backup_rejects_symlink_control_marker(self) -> None:
        backup_script = _backup_python(RUNBOOK.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            controls = state / "controls"
            workspace = root / "workspace"
            controls.mkdir(parents=True, mode=0o700)
            workspace.mkdir(mode=0o700)
            external_marker = root / "outside-marker"
            external_marker.write_text("do not follow\n", encoding="utf-8")
            (controls / "STOP").symlink_to(external_marker)
            environment = os.environ.copy()
            environment["ARCHON_STATE"] = str(state)
            environment["ARCHON_WORKSPACE"] = str(workspace)
            backup = subprocess.run(
                [sys.executable, "-c", backup_script],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(backup.returncode, 0)
        self.assertIn(b"control marker is a symlink: STOP", backup.stderr)


if __name__ == "__main__":
    unittest.main()
