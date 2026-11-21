import contextlib
import base64
import hashlib
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
from unittest.mock import patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from jarvis_v2.automation.queue_api import CoordinatorQueue
from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2 import native_executor
from jarvis_v2.cli import main


class LinuxReleaseCliTests(unittest.TestCase):
    def _run_cli(self, arguments, *, owner_keys_path=None, env=None):
        output = io.StringIO()
        trust_store = (
            patch.object(native_executor, "OWNER_KEYS_PATH", owner_keys_path)
            if owner_keys_path is not None else contextlib.nullcontext()
        )
        with trust_store, patch.dict(os.environ, env or {}), contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            code = main(arguments)
        return code, json.loads(output.getvalue()) if output.getvalue().strip() else None

    @staticmethod
    def _cancel_approval(private_key, task_id):
        claims = {
            "schema": 1,
            "approval_id": f"cancel-{task_id}",
            "key_id": "test-owner",
            "task_id": task_id,
            "operation": "task_cancel",
            "target": task_id,
            "content_sha256": hashlib.sha256(task_id.encode()).hexdigest(),
            "expires_at": int(time.time()) + 600,
            "decision": "APPROVE",
        }
        signed = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        return dict(claims, signature=base64.b64encode(private_key.sign(signed)).decode())

    @staticmethod
    def _admission_approval(private_key, task):
        task_id = task["task_id"]
        task_bytes = json.dumps(
            task, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode()
        claims = {
            "schema": 1,
            "approval_id": f"submit-{hashlib.sha256(task_id.encode()).hexdigest()[:24]}",
            "key_id": "test-owner",
            "task_id": task_id,
            "operation": "task_submit",
            "target": task_id,
            "content_sha256": hashlib.sha256(task_bytes).hexdigest(),
            "expires_at": int(time.time()) + 600,
            "decision": "APPROVE",
        }
        signed = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        return dict(claims, signature=base64.b64encode(private_key.sign(signed)).decode())

    def test_native_result_command_reads_persisted_answer_without_writing(self):
        task_id = "result-read"
        conversation_id = "native-" + hashlib.sha256(task_id.encode()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state"
            state.mkdir(mode=0o700)
            database = state / "conversations.sqlite3"
            with ConversationStore(database) as conversations:
                conversations.create_conversation(
                    conversation_id,
                    metadata={"task_id": task_id},
                )
                conversations.append_turn(
                    conversation_id,
                    role="assistant",
                    provider="ollama-local",
                    model="qwen3-4b",
                    content="private local answer",
                    idempotency_key=f"{conversation_id}:a",
                )
            database.chmod(0o600)
            before = hashlib.sha256(database.read_bytes()).hexdigest()
            code, result = self._run_cli([
                "result", "--state", str(state), "--task-id", task_id,
            ])
            after = hashlib.sha256(database.read_bytes()).hexdigest()

        self.assertEqual(code, 0)
        self.assertEqual(result["task_id"], task_id)
        self.assertEqual(result["conversation_id"], conversation_id)
        self.assertEqual(result["content"], "private local answer")
        self.assertEqual(before, after)

    def test_fresh_init_requires_signed_admission_and_cancels_local_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / "state"
            code, result = self._run_cli(["init", "--state", str(state)])
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "initialized")
            for name in ("runtime.sqlite3", "atlas.sqlite3"):
                self.assertEqual((state / name).stat().st_mode & 0o077, 0)

            task = {
                "task_id": "release-smoke",
                "priority": "P3",
                "module": "core",
                "payload": {"operation": "native_capabilities"},
            }
            document = root / "task.json"
            document.write_text(json.dumps(task))
            trusted = Ed25519PrivateKey.generate()
            untrusted = Ed25519PrivateKey.generate()
            keys = root / "owner-keys.json"
            keys.write_text(json.dumps({
                "schema": 1,
                "keys": {"test-owner": base64.b64encode(trusted.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw,
                )).decode()},
            }))
            keys.chmod(0o600)
            attacker_keys = root / "attacker-keys.json"
            attacker_keys.write_text(json.dumps({
                "schema": 1,
                "keys": {"test-owner": base64.b64encode(untrusted.public_key().public_bytes(
                    serialization.Encoding.Raw, serialization.PublicFormat.Raw,
                )).decode()},
            }))
            attacker_keys.chmod(0o600)
            admission_file = root / "admission-approval.json"
            submit_args = [
                "submit", "--state", str(state), "--task-file", str(document),
                "--approval-file", str(admission_file),
            ]
            attacker_env = {"ARCHON_OWNER_KEYS": str(attacker_keys)}
            admission_file.write_text(json.dumps(self._admission_approval(untrusted, task)))
            code, denied = self._run_cli(submit_args, owner_keys_path=keys, env=attacker_env)
            self.assertEqual(code, 2)
            self.assertIsNone(denied)
            with CoordinatorQueue.open(state / "atlas.sqlite3") as queue:
                self.assertEqual(queue.status(), [])

            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as rejected_override:
                    main([*submit_args, "--owner-keys", str(keys)])
            self.assertEqual(rejected_override.exception.code, 2)

            admission_file.write_text(json.dumps(self._admission_approval(trusted, task)))
            document.write_text(json.dumps({**task, "payload": {"operation": "queue_status"}}))
            code, denied = self._run_cli(submit_args, owner_keys_path=keys, env=attacker_env)
            self.assertEqual(code, 2)
            self.assertIsNone(denied)
            with CoordinatorQueue.open(state / "atlas.sqlite3") as queue:
                self.assertEqual(queue.status(), [])

            document.write_text(json.dumps(task))
            code, admitted = self._run_cli(submit_args, owner_keys_path=keys, env=attacker_env)
            self.assertEqual(code, 0)
            self.assertEqual(admitted["status"], "accepted")
            self.assertEqual(admitted["approval_id"], json.loads(admission_file.read_text())["approval_id"])
            self.assertEqual(len(admitted["receipt"]), 64)
            with CoordinatorQueue.open(state / "atlas.sqlite3") as queue:
                self.assertEqual(queue.status()[0]["state"], "pending")
                detail = queue._queue.db.execute(
                    "SELECT detail FROM events WHERE task_id=? AND kind='pending'",
                    ("release-smoke",),
                ).fetchone()[0]
                persisted = json.loads(detail)
                self.assertEqual(persisted["approval"], json.loads(admission_file.read_text()))
                self.assertEqual(persisted["receipt"], admitted["receipt"])

            approval_file = root / "cancel-approval.json"
            approval_file.write_text(json.dumps(self._cancel_approval(untrusted, "release-smoke")))
            code, denied = self._run_cli([
                "cancel", "--state", str(state), "--task-id", "release-smoke",
                "--approval-file", str(approval_file),
            ], owner_keys_path=keys, env=attacker_env)
            self.assertEqual(code, 2)
            self.assertIsNone(denied)
            with CoordinatorQueue.open(state / "atlas.sqlite3") as queue:
                self.assertEqual(queue.status()[0]["state"], "pending")
            approval_file.write_text(json.dumps(self._cancel_approval(trusted, "release-smoke")))
            code, cancelled = self._run_cli([
                "cancel", "--state", str(state), "--task-id", "release-smoke",
                "--approval-file", str(approval_file),
            ], owner_keys_path=keys, env=attacker_env)
            self.assertEqual(code, 0)
            self.assertEqual(cancelled["state"], "cancelled")
            with CoordinatorQueue.open(state / "atlas.sqlite3") as queue:
                self.assertEqual(queue.status()[0]["state"], "cancelled")
                detail = queue._queue.db.execute(
                    "SELECT detail FROM events WHERE task_id=? AND kind='cancelled'",
                    ("release-smoke",),
                ).fetchone()[0]
                self.assertEqual(json.loads(detail)["approval"], json.loads(approval_file.read_text()))

    @unittest.skipUnless(sys.platform == "linux", "Linux process signal behavior")
    def test_watch_controller_exits_on_sigterm(self):
        import fcntl

        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state"
            self._run_cli(["init", "--state", str(state)])
            source = Path(__file__).resolve().parents[1] / "src"
            environment = dict(os.environ, PYTHONPATH=str(source))
            controller_lock = state / "run" / "controller.lock"

            def controller_lock_is_held():
                if not controller_lock.is_file():
                    return False
                with controller_lock.open("r+b") as lock_file:
                    try:
                        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        return True
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
                    return False

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
            try:
                startup_deadline = time.monotonic() + 5
                while not controller_lock_is_held():
                    return_code = process.poll()
                    if return_code is not None:
                        _, stderr = process.communicate(timeout=5)
                        self.fail(f"controller exited with status {return_code} before startup readiness: {stderr}")
                    if time.monotonic() >= startup_deadline:
                        process.terminate()
                        _, stderr = process.communicate(timeout=5)
                        self.fail(f"controller did not create its startup lock within 5 seconds: {stderr}")
                    time.sleep(0.01)

                return_code = process.poll()
                if return_code is not None:
                    _, stderr = process.communicate(timeout=5)
                    self.fail(f"controller exited with status {return_code} after creating its startup lock: {stderr}")
                process.send_signal(signal.SIGTERM)
                _, stderr = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0, stderr)
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.communicate(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.communicate(timeout=5)


if __name__ == "__main__":
    unittest.main()
