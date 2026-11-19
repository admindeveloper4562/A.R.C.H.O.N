import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.automation.queue_api import QueueEnvelope
from jarvis_v2.automation.queue_api import CoordinatorQueue
from jarvis_v2.native_executor import (
    NativeControlPlaneExecutor,
    NativeExecutorError,
)


class NativeExecutorTests(unittest.TestCase):
    def _executor(self):
        root = Path(tempfile.mkdtemp())
        state = root / "state"
        state.mkdir()
        state.chmod(0o700)
        return root, NativeControlPlaneExecutor(repository=root, state_dir=state)

    def test_module_health_covers_all_ten_active_modules(self):
        root, executor = self._executor()
        try:
            modules = (
                "core", "sda", "backend", "runtime", "research",
                "tws", "wic", "finance", "guardian", "automation",
            )
            for module in modules:
                result = executor(
                    QueueEnvelope(
                        f"health-{module}", "P3", module,
                        {"operation": "module_health"},
                    )
                )
                self.assertEqual(result["status"], "ready")
                self.assertEqual(result["module"], module)
        finally:
            del executor

    def test_unknown_operation_fails_closed(self):
        root, executor = self._executor()
        with self.assertRaisesRegex(NativeExecutorError, "unsupported_native_operation"):
            executor(QueueEnvelope("unknown", "P3", "core", {"operation": "shell"}))

    def test_inventory_digest_returns_metadata_only(self):
        root, executor = self._executor()
        inventory = executor.state_dir / "host_inventory.json"
        inventory.write_text(
            json.dumps({"filesystem": {"coverage": {"scanned_entries": 4, "truncated": False}}}),
            encoding="utf-8",
        )
        result = executor(
            QueueEnvelope("inventory", "P3", "backend", {"operation": "inventory_digest"})
        )
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["scanned_entries"], 4)
        self.assertNotIn("filesystem", result)

    def test_native_cli_uses_built_in_executor_for_read_only_task(self):
        root, executor = self._executor()
        del executor
        with CoordinatorQueue.open(root / "state" / "atlas.sqlite3") as queue:
            queue.enqueue(
                task_id="module-health",
                priority="P3",
                module="guardian",
                payload={"operation": "module_health"},
            )
        environment = dict(os.environ, PYTHONPATH="src")
        result = subprocess.run(
            [
                "/usr/bin/python3",
                "-m",
                "jarvis_v2.native_controller",
                "--once",
                "--state",
                str(root / "state"),
                "--repository",
                str(Path.cwd()),
            ],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "completed")
        with CoordinatorQueue.open(root / "state" / "atlas.sqlite3") as queue:
            self.assertEqual(queue.status()[0]["state"], "completed")


if __name__ == "__main__":
    unittest.main()
