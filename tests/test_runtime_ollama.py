from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from jarvis_v2.backend import OllamaInferenceProfile
from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.backend.ollama_gateway import LocalOllamaGateway
from jarvis_v2.backend.protocol_adapters import ProtocolResponse
from jarvis_v2.runtime import ChatService, OfflineChatService, OllamaOfflineAdapter


class RuntimeOllamaTests(unittest.TestCase):
    def _service(self, directory: str, adapter) -> tuple[ConversationStore, OfflineChatService]:
        store = ConversationStore(Path(directory) / "conversation.sqlite")
        store.create_conversation("local-chat")
        chat = ChatService(store)
        service = OfflineChatService(
            chat,
            {adapter.model_alias},
            adapter=adapter,
            provider_id="ollama-local",
        )
        return store, service

    def test_local_adapter_persists_only_a_completed_response(self) -> None:
        gateway = LocalOllamaGateway(OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048))
        response = ProtocolResponse("ollama-local", "ollama-test", "qwen3:4b", "saved locally", "stop", ())
        with patch.object(gateway, "complete", return_value=response) as complete:
            with tempfile.TemporaryDirectory() as directory:
                store, service = self._service(directory, OllamaOfflineAdapter(gateway))
                try:
                    async def run():
                        return [event async for event in service.stream("local-chat", "hello", "qwen3-4b")]

                    events = asyncio.run(run())
                    self.assertEqual(events[-1]["type"], "done")
                    self.assertEqual(store.list_turns("local-chat")[-1]["content"], "saved locally")
                finally:
                    store.close()
        complete.assert_called_once_with("hello", model="qwen3:4b")

    @unittest.skipUnless(os.environ.get("ARCHON_RUN_OLLAMA_INTEGRATION") == "1", "opt-in local Ollama integration")
    def test_real_local_ollama_runtime_round_trip(self) -> None:
        gateway = LocalOllamaGateway(OllamaInferenceProfile(model="qwen3:4b", num_ctx=2_048), timeout_seconds=120)
        with tempfile.TemporaryDirectory() as directory:
            store, service = self._service(directory, OllamaOfflineAdapter(gateway))
            start = time.monotonic()
            try:
                async def run():
                    return [event async for event in service.stream(
                        "local-chat",
                        "Reply exactly ARCHON_RUNTIME_LOCAL_INFERENCE_OK and nothing else.",
                        "qwen3-4b",
                        idempotency_key="local-inference-round-trip",
                    )]

                events = asyncio.run(run())
                turns = store.list_turns("local-chat")
                reply = turns[-1]["content"]
                elapsed = time.monotonic() - start
                self.assertEqual(events[-1]["type"], "done")
                self.assertIn("ARCHON_RUNTIME_LOCAL_INFERENCE_OK", reply)
                self.assertEqual(turns[-1]["provider"], "ollama-local")
                print("OLLAMA_RUNTIME_E2E=" + json.dumps({
                    "elapsed_seconds": round(elapsed, 3),
                    "model": "qwen3:4b",
                    "provider": "ollama-local",
                    "persisted_turns": len(turns),
                    "marker_ok": True,
                }, sort_keys=True))
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
