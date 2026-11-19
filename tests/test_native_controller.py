import tempfile
import unittest
from pathlib import Path

from jarvis_v2.native_controller import NativeController, NativeControllerError


class NativeControllerTests(unittest.TestCase):
    def test_empty_native_cycle_is_a_safe_idle_without_an_executor(self):
        with tempfile.TemporaryDirectory() as directory:
            with NativeController(Path(directory)) as controller:
                result = controller.run_once()
                self.assertEqual(result["state"], "idle")
                self.assertEqual(result["reason"], "executor_unconfigured")

    def test_process_lock_fences_a_second_native_controller_and_releases_on_close(self):
        with tempfile.TemporaryDirectory() as directory:
            first = NativeController(Path(directory))
            try:
                with self.assertRaises(NativeControllerError):
                    NativeController(Path(directory))
            finally:
                first.close()
            with NativeController(Path(directory)):
                pass

    def test_controls_stop_admission_before_a_task_is_claimed(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            with NativeController(state) as controller:
                controller.queue.enqueue(
                    task_id="native-1", priority="P1", module="core", payload={}
                )
                (controller.control_dir / "PAUSE").touch()
                result = controller.run_once()
                self.assertEqual(result["state"], "safe_mode")
                self.assertEqual(controller.queue.status()[0]["state"], "pending")

    def test_executor_completion_and_failure_are_digest_only_and_durable(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            with NativeController(state) as controller:
                controller.queue.enqueue(
                    task_id="native-ok", priority="P1", module="core", payload={}
                )
                controller.queue.enqueue(
                    task_id="native-fail", priority="P1", module="core", payload={}
                )
            def execute(item):
                if item.task_id == "native-fail":
                    raise RuntimeError("private executor detail")
                return {"ok": True}
            with NativeController(state, executor=execute) as controller:
                first = controller.run_once()
                second = controller.run_once()
                self.assertEqual(first["state"], "completed")
                self.assertEqual(second["state"], "failed")
                states = {row["id"]: row["state"] for row in controller.queue.status()}
                self.assertEqual(states, {"native-ok": "completed", "native-fail": "failed"})

    def test_executor_exception_is_recorded_as_failed_without_raw_error(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            with NativeController(state) as controller:
                controller.queue.enqueue(
                    task_id="native-error", priority="P1", module="core", payload={}
                )
            def fail(_item):
                raise RuntimeError("private executor detail")
            with NativeController(state, executor=fail) as controller:
                result = controller.run_once()
                self.assertEqual(result["state"], "failed")
                self.assertNotIn("private", str(result))
                self.assertEqual(controller.queue.status()[0]["state"], "failed")

    def test_native_user_unit_points_only_to_the_native_controller(self):
        unit = (Path(__file__).parents[1] / "infra/systemd/archon.service").read_text(
            encoding="utf-8"
        )
        self.assertIn("jarvis_v2.native_controller", unit)
        self.assertIn("ReadWritePaths=%h/.local/state/archon", unit)
        self.assertNotIn("archon-astra", unit)


if __name__ == "__main__":
    unittest.main()
