import base64
import hashlib
import json
import os
import time
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from jarvis_v2.automation.queue_api import QueueEnvelope
from jarvis_v2.automation.queue_api import CoordinatorQueue
from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.backend.effects import EffectJournal
from jarvis_v2.backend.ollama_gateway import LocalOllamaGateway
from jarvis_v2.backend.ollama_profile import OllamaInferenceProfile
from jarvis_v2.backend.protocol_adapters import ProtocolResponse, ProtocolToolCall
from jarvis_v2 import native_executor
from jarvis_v2.native_executor import (
    NativeControlPlaneExecutor,
    NativeExecutorError,
)
from tests.queue_admission import enqueue_approved


class NativeExecutorTests(unittest.TestCase):
    def _executor(self):
        root = Path(tempfile.mkdtemp())
        state = root / "state"
        state.mkdir()
        state.chmod(0o700)
        return root, NativeControlPlaneExecutor(repository=root, state_dir=state)


    def _workspace_executor(self):
        root = Path(tempfile.mkdtemp())
        state = root / "state"
        workspace = root / "workspace"
        state.mkdir(mode=0o700)
        workspace.mkdir(mode=0o700)
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        executor = NativeControlPlaneExecutor(
            repository=root,
            state_dir=state,
            workspace_root=workspace,
            owner_keys={"test-owner": public_key},
        )
        return root, state, workspace, private_key, executor

    def _write_task(self, private_key, task_id, target, content, **changes):
        claims = {
            "schema": 1,
            "approval_id": f"approval-{task_id}",
            "key_id": "test-owner",
            "task_id": task_id,
            "operation": "workspace_write",
            "target": target,
            "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
            "expires_at": int(time.time()) + 600,
            "decision": "APPROVE",
        }
        claims.update(changes)
        message = json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()
        approval = dict(claims, signature=base64.b64encode(private_key.sign(message)).decode())
        return QueueEnvelope(task_id, "P3", "core", {
            "operation": "workspace_write", "target": target,
            "content": content, "approval": approval,
        })

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

    def test_capability_matrix_rejects_side_effect_classes(self):
        root, executor = self._executor()
        result = executor(
            QueueEnvelope("capabilities", "P3", "core", {"operation": "native_capabilities"})
        )
        self.assertIn("queue_status", result["read_only_operations"])
        self.assertIn("requires a private workspace", result["rejected_operations"]["filesystem_write"])
        self.assertNotIn("workspace_write", result["enabled_operations"])
        self.assertEqual(result["domain_effect_handlers"], "not_configured")

    def test_model_inference_requires_explicit_local_gateway_and_trusted_keys(self):
        root, executor = self._executor()
        task = QueueEnvelope("model-disabled", "P2", "core", {
            "operation": "model_inference", "prompt": "hello",
        })
        result = executor(QueueEnvelope(
            "capabilities-model-disabled", "P3", "core",
            {"operation": "native_capabilities"},
        ))
        self.assertNotIn("model_inference", result["enabled_operations"])
        self.assertIn("local Ollama", result["rejected_operations"]["model_inference"])
        with self.assertRaisesRegex(NativeExecutorError, "model_inference_not_configured"):
            executor(task)

        gateway = LocalOllamaGateway(OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048))
        keyed_executor = NativeControlPlaneExecutor(
            repository=root,
            state_dir=executor.state_dir,
            model_gateway=gateway,
        )
        with self.assertRaisesRegex(NativeExecutorError, "trusted_owner_keys"):
            keyed_executor(task)
        self.assertNotIn("model_inference", keyed_executor.capabilities())

    @patch.object(LocalOllamaGateway, "complete")
    def test_model_inference_persists_private_turns_and_replays_idempotently(self, complete):
        root = Path(tempfile.mkdtemp())
        state = root / "state"
        state.mkdir(mode=0o700)
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw,
        )
        gateway = LocalOllamaGateway(OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048))
        complete.return_value = ProtocolResponse(
            "ollama-local", "test-response", "qwen3:4b", "local answer", "stop",
            tool_calls=(ProtocolToolCall("untrusted-call", "shell", {"command": "id"}),),
        )
        executor = NativeControlPlaneExecutor(
            repository=root,
            state_dir=state,
            owner_keys={"test-owner": public_key},
            model_gateway=gateway,
        )
        task = QueueEnvelope("model-idempotent", "P2", "core", {
            "operation": "model_inference", "prompt": "hello local model",
        })
        first = executor(task)
        replay = executor(task)
        self.assertEqual(first, replay)
        complete.assert_called_once_with("hello local model", model="qwen3:4b")
        self.assertIn("model_inference", executor.capabilities())
        self.assertNotIn("model_inference", executor.rejected_capabilities())

        database = state / "conversations.sqlite3"
        self.assertEqual(database.stat().st_mode & 0o777, 0o600)
        with ConversationStore(database) as conversations:
            turns = conversations.list_turns(first["conversation_id"])
        self.assertEqual([turn["role"] for turn in turns], ["user", "assistant"])
        self.assertEqual(turns[-1]["content"], "local answer")
        self.assertEqual(turns[-1]["provider"], "ollama-local")
        self.assertEqual(turns[-1]["tool_effects"], [])
        self.assertEqual(first["content_sha256"], hashlib.sha256(b"local answer").hexdigest())

    @patch.object(LocalOllamaGateway, "complete")
    def test_model_inference_rejects_wrong_module_payload_and_prompt(self, complete):
        root, base_executor = self._executor()
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw,
        )
        gateway = LocalOllamaGateway(OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048))
        executor = NativeControlPlaneExecutor(
            repository=root,
            state_dir=base_executor.state_dir,
            owner_keys={"test-owner": public_key},
            model_gateway=gateway,
        )
        with self.assertRaisesRegex(NativeExecutorError, "model_inference_requires_core"):
            executor(QueueEnvelope("wrong-module", "P2", "research", {
                "operation": "model_inference", "prompt": "hello",
            }))
        with self.assertRaisesRegex(NativeExecutorError, "model_inference_payload_invalid"):
            executor(QueueEnvelope("unapproved-destination", "P2", "core", {
                "operation": "model_inference",
                "prompt": "hello",
                "base_url": "https://example.invalid",
            }))
        for prompt, error in (("\x00", "model_prompt_invalid"), ("x" * (16 * 1024 + 1), "model_prompt_too_large")):
            with self.assertRaisesRegex(NativeExecutorError, error):
                executor(QueueEnvelope("invalid-prompt", "P2", "core", {
                    "operation": "model_inference", "prompt": prompt,
                }))
        complete.assert_not_called()


    def test_signed_workspace_write_is_bounded_and_idempotent(self):
        root, state, workspace, private_key, executor = self._workspace_executor()
        task = self._write_task(private_key, "write-once", "result.txt", "approved result")
        first = executor(task)
        second = executor(task)
        self.assertEqual(first, second)
        self.assertEqual((workspace / "result.txt").read_text(), "approved result")
        self.assertEqual((workspace / "result.txt").stat().st_mode & 0o777, 0o600)
        self.assertEqual((state / "effects.sqlite3").stat().st_mode & 0o077, 0)

    def test_workspace_write_rejects_unsigned_or_changed_content(self):
        root, state, workspace, private_key, executor = self._workspace_executor()
        unsigned = QueueEnvelope("unsigned", "P3", "core", {
            "operation": "workspace_write", "target": "denied.txt", "content": "no approval",
        })
        with self.assertRaisesRegex(NativeExecutorError, "owner_approval_invalid"):
            executor(unsigned)
        task = self._write_task(private_key, "changed", "denied.txt", "signed text")
        task.payload["content"] = "changed after approval"
        with self.assertRaisesRegex(NativeExecutorError, "owner_approval_scope_invalid"):
            executor(task)
        self.assertFalse((workspace / "denied.txt").exists())

    def test_workspace_write_refuses_path_traversal_and_overwrite(self):
        root, state, workspace, private_key, executor = self._workspace_executor()
        traversal = self._write_task(private_key, "traversal", "../outside.txt", "bad")
        with self.assertRaisesRegex(NativeExecutorError, "workspace_target_invalid"):
            executor(traversal)
        (workspace / "existing.txt").write_text("original")
        overwrite = self._write_task(private_key, "overwrite", "existing.txt", "replacement")
        with self.assertRaisesRegex(NativeExecutorError, "workspace_target_conflict"):
            executor(overwrite)
        self.assertEqual((workspace / "existing.txt").read_text(), "original")

    def test_workspace_write_reconciles_journal_after_interrupted_effect(self):
        root, state, workspace, private_key, executor = self._workspace_executor()
        task = self._write_task(private_key, "interrupted", "recovered.txt", "durable result")
        approval = task.payload["approval"]
        content = task.payload["content"]
        digest = hashlib.sha256(content.encode()).hexdigest()
        effect_path = state / "effects.sqlite3"
        with EffectJournal(effect_path) as journal:
            journal.prepare(
                hashlib.sha256(task.task_id.encode()).hexdigest(),
                task.task_id,
                operation="workspace_write",
                target="recovered.txt",
                request={
                    "approval_id": approval["approval_id"],
                    "content_sha256": digest,
                    "size_bytes": len(content.encode()),
                },
            )
        effect_path.chmod(0o600)
        (workspace / "recovered.txt").write_text(content)
        (workspace / "recovered.txt").chmod(0o600)
        result = executor(task)
        self.assertEqual(result["sha256"], digest)
        with sqlite3.connect(effect_path) as db:
            self.assertEqual(db.execute(
                "select status from tool_effect_journal where task_id=?", (task.task_id,)
            ).fetchone()[0], "completed")

    def test_queue_status_is_read_only_and_reports_durable_controls(self):
        root, executor = self._executor()
        with CoordinatorQueue.open(executor.state_dir / "atlas.sqlite3") as queue:
            enqueue_approved(queue, task_id="queued", priority="P3", module="core", payload={})
        result = executor(
            QueueEnvelope("queue", "P3", "core", {"operation": "queue_status"})
        )
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["task_counts"], {"pending": 1})
        self.assertEqual(result["control"]["state"], "running")

    def test_database_inspect_allows_only_named_native_databases(self):
        root, executor = self._executor()
        database = executor.state_dir / "runtime.sqlite3"
        with sqlite3.connect(database) as db:
            db.execute("create table sample(value text)")
        result = executor(
            QueueEnvelope(
                "database", "P3", "backend",
                {"operation": "database_inspect", "database": "runtime"},
            )
        )
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["integrity"], "ok")
        conversations = executor.state_dir / "conversations.sqlite3"
        with ConversationStore(conversations):
            pass
        conversations.chmod(0o600)
        result = executor(
            QueueEnvelope(
                "database-conversations", "P3", "backend",
                {"operation": "database_inspect", "database": "conversations"},
            )
        )
        self.assertEqual(result["integrity"], "ok")
        with self.assertRaisesRegex(NativeExecutorError, "database_name_not_allowed"):
            executor(
                QueueEnvelope(
                    "database-bad", "P3", "backend",
                    {"operation": "database_inspect", "database": "../runtime.sqlite3"},
                )
            )

    def test_sda_and_guardian_probes_remain_blocked_without_cutover_evidence(self):
        root, executor = self._executor()
        handoff = executor(
            QueueEnvelope("handoff", "P3", "sda", {"operation": "sda_handoff_status"})
        )
        guardian = executor(
            QueueEnvelope("guardian", "P3", "guardian", {"operation": "guardian_readiness"})
        )
        self.assertEqual(handoff["status"], "blocked")
        self.assertTrue(handoff["shadow_mode"])
        self.assertEqual(guardian["status"], "blocked")
        self.assertFalse(guardian["trusted_watchdog"])

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
            enqueue_approved(queue,
                task_id="module-health",
                priority="P3",
                module="guardian",
                payload={"operation": "module_health"},
            )
        test_config = root / "test-config"
        test_config.mkdir()
        (test_config / "sitecustomize.py").write_text(
            "from pathlib import Path\n"
            "from jarvis_v2 import native_executor\n"
            f"native_executor.OWNER_KEYS_PATH = Path({str(native_executor.OWNER_KEYS_PATH)!r})\n",
            encoding="utf-8",
        )
        environment = dict(
            os.environ,
            PYTHONPATH=f"{test_config}:{Path.cwd() / 'src'}",
        )
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
