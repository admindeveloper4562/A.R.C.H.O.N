import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from jarvis_v2.automation.queue_api import CoordinatorQueue
from jarvis_v2.cli import main


class LinuxReleaseCliTests(unittest.TestCase):
    def _run_cli(self, arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(arguments)
        return code, json.loads(output.getvalue()) if output.getvalue().strip() else None

    def test_fresh_init_admits_and_cancels_local_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            code, result = self._run_cli(["init", "--state", str(state)])
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "initialized")
            for name in ("runtime.sqlite3", "atlas.sqlite3"):
                self.assertEqual((state / name).stat().st_mode & 0o077, 0)

            document = root / "task.json"
            document.write_text(json.dumps({
                "task_id": "release-smoke",
                "priority": "P3",
                "module": "core",
                "payload": {"operation": "native_capabilities"},
            }))
            code, admitted = self._run_cli([
                "submit", "--state", str(state), "--task-file", str(document),
            ])
            self.assertEqual(code, 0)
            self.assertEqual(admitted["status"], "accepted")
            code, cancelled = self._run_cli([
                "cancel", "--state", str(state), "--task-id", "release-smoke",
            ])
            self.assertEqual(code, 0)
            self.assertEqual(cancelled["state"], "cancelled")
            with CoordinatorQueue.open(state / "atlas.sqlite3") as queue:
                self.assertEqual(queue.status()[0]["state"], "cancelled")

    @unittest.skipUnless(sys.platform == "linux", "Linux process signal behavior")
    def test_watch_controller_exits_on_sigterm(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state"
            self._run_cli(["init", "--state", str(state)])
            source = Path(__file__).resolve().parents[1] / "src"
            environment = dict(os.environ, PYTHONPATH=str(source))
            process = subprocess.Popen(
                [
                    sys.executable, "-m", "jarvis_v2.native_controller", "--watch",
                    "--state", str(state), "--repository", str(source.parent),
                    "--poll-seconds", "30",
                ],
                cwd=source.parent,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            time.sleep(0.25)
            self.assertIsNone(process.poll(), "controller exited before SIGTERM")
            process.send_signal(signal.SIGTERM)
            _, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)


if __name__ == "__main__":
    unittest.main()
