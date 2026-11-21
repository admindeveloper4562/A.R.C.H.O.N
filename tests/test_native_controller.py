import contextlib
from hashlib import sha256
import os
import io
import select
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from jarvis_v2 import native_executor
from jarvis_v2.automation.queue_api import QueueApiError
from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.backend.ollama_gateway import LocalOllamaGateway
from jarvis_v2.backend.ollama_profile import OllamaInferenceProfile
from jarvis_v2.backend.protocol_adapters import ProtocolResponse
from jarvis_v2.native_controller import NativeController, NativeControllerError, main
from jarvis_v2.native_executor import NativeControlPlaneExecutor
from tests.queue_admission import enqueue_approved


class NativeControllerTests(unittest.TestCase):
    def test_controller_cli_rejects_per_invocation_owner_key_override(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as rejected:
                main(["--owner-keys", "caller-controlled.json"])
        self.assertEqual(rejected.exception.code, 2)

    def test_local_model_cli_requires_trusted_owner_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("jarvis_v2.native_controller._load_configured_owner_keys", return_value={}):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as rejected:
                        main([
                            "--state", directory,
                            "--ollama-model", "qwen3:4b",
                            "--once",
                        ])
        self.assertEqual(rejected.exception.code, 2)

    def test_local_model_executor_requires_lease_timeout_margin(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            for timeout, minimum_lease in ((45, 60), (120, 135)):
                executor = NativeControlPlaneExecutor(
                    repository=Path(__file__).parents[1],
                    state_dir=state,
                    owner_keys=native_executor._load_configured_owner_keys(),
                    model_gateway=LocalOllamaGateway(
                        OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048),
                        timeout_seconds=timeout,
                    ),
                )
                with self.assertRaisesRegex(
                    NativeControllerError, f"lease of at least {minimum_lease} seconds",
                ):
                    NativeController(state, executor=executor, lease_seconds=minimum_lease - 1)
                with NativeController(state, executor=executor, lease_seconds=minimum_lease) as controller:
                    self.assertEqual(controller.lease_seconds, minimum_lease)

    @patch.object(LocalOllamaGateway, "complete")
    def test_signed_native_model_task_persists_and_returns_a_safe_reference(self, complete):
        task_id = "native-model-queue"
        payload = {"operation": "model_inference", "prompt": "Reply exactly ARCHON_NATIVE_MODEL_OK."}
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            gateway = LocalOllamaGateway(OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048))
            complete.return_value = ProtocolResponse(
                "ollama-local", "test-response", "qwen3:4b", "ARCHON_NATIVE_MODEL_OK", "stop",
            )
            executor = NativeControlPlaneExecutor(
                repository=Path(__file__).parents[1],
                state_dir=state,
                owner_keys=native_executor._load_configured_owner_keys(),
                model_gateway=gateway,
            )
            with NativeController(state, executor=executor) as controller:
                with self.assertRaises(QueueApiError):
                    enqueue_approved(
                        controller.queue,
                        task_id="native-model-forged",
                        priority="P2",
                        module="core",
                        payload=payload,
                        trusted_signer=False,
                    )
                self.assertEqual(controller.queue.status(), [])
                admitted = enqueue_approved(
                    controller.queue,
                    task_id=task_id,
                    priority="P2",
                    module="core",
                    payload=payload,
                )
                result = controller.run_once()
                self.assertEqual(result["state"], "completed")
                self.assertEqual(result["result_ref"], "native-" + sha256(task_id.encode()).hexdigest())
                self.assertNotIn("ARCHON_NATIVE_MODEL_OK", str(result))
                self.assertEqual(controller.queue.status()[0]["state"], "completed")

            with ConversationStore(state / "conversations.sqlite3") as conversations:
                turns = conversations.list_turns(result["result_ref"])
            self.assertEqual([turn["role"] for turn in turns], ["user", "assistant"])
            self.assertEqual(turns[-1]["content"], "ARCHON_NATIVE_MODEL_OK")
            self.assertEqual(executor(admitted), executor(admitted))
            complete.assert_called_once_with(payload["prompt"], model="qwen3:4b")

    @unittest.skipUnless(
        os.environ.get("ARCHON_RUN_NATIVE_OLLAMA_E2E") == "1",
        "opt-in signed native queue and local Ollama integration",
    )
    def test_real_signed_native_model_task_round_trip(self):
        task_id = "native-model-live-e2e"
        payload = {
            "operation": "model_inference",
            "prompt": "Reply exactly ARCHON_NATIVE_QUEUE_OLLAMA_OK and nothing else.",
        }
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            gateway = LocalOllamaGateway(
                OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048),
                timeout_seconds=45,
            )
            with patch.object(gateway, "complete", wraps=gateway.complete) as complete:
                executor = NativeControlPlaneExecutor(
                    repository=Path(__file__).parents[1],
                    state_dir=state,
                    owner_keys=native_executor._load_configured_owner_keys(),
                    model_gateway=gateway,
                )
                with NativeController(state, executor=executor) as controller:
                    admitted = enqueue_approved(
                        controller.queue,
                        task_id=task_id,
                        priority="P2",
                        module="core",
                        payload=payload,
                    )
                    result = controller.run_once()
                    self.assertEqual(result["state"], "completed")
                    self.assertEqual(result["result_ref"], "native-" + sha256(task_id.encode()).hexdigest())
                with ConversationStore(state / "conversations.sqlite3") as conversations:
                    turns = conversations.list_turns(result["result_ref"])
                self.assertEqual(turns[-1]["content"], "ARCHON_NATIVE_QUEUE_OLLAMA_OK")
                self.assertEqual(turns[-1]["provider"], "ollama-local")
                self.assertEqual(len(turns), 2)
                replay = executor(admitted)
                self.assertEqual(replay["assistant_turn_id"], turns[-1]["turn_id"])
                complete.assert_called_once_with(payload["prompt"], model="qwen3:4b")

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

    @unittest.skipUnless(sys.platform == "linux", "Linux signal and descriptor semantics")
    def test_watch_sigterm_during_controller_startup_is_orderly(self):
        with tempfile.TemporaryDirectory() as directory:
            state_dir = Path(directory) / "state"
            state_dir.mkdir(mode=0o700)
            repository = Path(__file__).parents[1]
            ready_read, ready_write = os.pipe()
            release_read, release_write = os.pipe()
            signal_read, signal_write = os.pipe()
            process = None
            script = (
                "import os, signal, sys\n"
                "import jarvis_v2.native_controller as native\n"
                "ready_fd, release_fd, signal_fd = map(int, sys.argv[1:4])\n"
                "state_dir, repository = sys.argv[4:6]\n"
                "original_signal = signal.signal\n"
                "def observe_signal(signum, handler):\n"
                "    if signum == signal.SIGTERM and callable(handler):\n"
                "        original_handler = handler\n"
                "        def acknowledge(received, frame):\n"
                "            result = original_handler(received, frame)\n"
                "            os.write(signal_fd, b'S')\n"
                "            return result\n"
                "        handler = acknowledge\n"
                "    return original_signal(signum, handler)\n"
                "signal.signal = observe_signal\n"
                "original_init = native.NativeController.__init__\n"
                "def gated_init(self, *args, **kwargs):\n"
                "    os.write(ready_fd, b'I')\n"
                "    os.read(release_fd, 1)\n"
                "    return original_init(self, *args, **kwargs)\n"
                "native.NativeController.__init__ = gated_init\n"
                "raise SystemExit(native.main(['--watch', '--state', state_dir, '--repository', repository]))\n"
            )
            environment = os.environ.copy()
            source_root = str(repository / "src")
            inherited_pythonpath = environment.get("PYTHONPATH")
            environment["PYTHONPATH"] = os.pathsep.join(
                [source_root] + ([inherited_pythonpath] if inherited_pythonpath else [])
            )
            try:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        script,
                        str(ready_write),
                        str(release_read),
                        str(signal_write),
                        str(state_dir),
                        str(repository),
                    ],
                    env=environment,
                    pass_fds=(ready_write, release_read, signal_write),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                os.close(ready_write)
                ready_write = -1
                os.close(release_read)
                release_read = -1
                os.close(signal_write)
                signal_write = -1

                self.assertTrue(select.select([ready_read], [], [], 5)[0], "controller startup did not reach gate")
                if os.read(ready_read, 1) != b"I":
                    stdout, stderr = process.communicate(timeout=10)
                    self.fail(
                        f"controller exited before startup gate: {process.returncode}; {stdout!r}; {stderr!r}"
                    )
                process.send_signal(signal.SIGTERM)
                self.assertTrue(select.select([signal_read], [], [], 5)[0], "SIGTERM handler did not acknowledge")
                self.assertEqual(os.read(signal_read, 1), b"S")
                os.write(release_write, b"C")
                stdout, stderr = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 0, (stdout, stderr))

                with NativeController(state_dir):
                    pass
            finally:
                for fd in (ready_read, ready_write, release_read, release_write, signal_read, signal_write):
                    if fd >= 0:
                        try:
                            os.close(fd)
                        except OSError:
                            pass
                if process is not None and process.poll() is None:
                    process.kill()
                    process.communicate(timeout=10)

    def test_controls_stop_admission_before_a_task_is_claimed(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)
            with NativeController(state) as controller:
                enqueue_approved(controller.queue,
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
                enqueue_approved(controller.queue,
                    task_id="native-ok", priority="P1", module="core", payload={}
                )
                enqueue_approved(controller.queue,
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
                enqueue_approved(controller.queue,
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
