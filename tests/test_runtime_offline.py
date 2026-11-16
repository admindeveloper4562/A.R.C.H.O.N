import asyncio
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.runtime import ChatService, OfflineChatService


class RuntimeOfflineTests(unittest.TestCase):
    def _service(self, directory, *, adapter=None, allow_fallback=False):
        store = ConversationStore(Path(directory) / "conversation.sqlite")
        store.create_conversation("conversation-1")
        chat = ChatService(store)
        offline = OfflineChatService(
            chat,
            {"qwen3-8b"},
            adapter=adapter,
            fallback_model="qwen3-8b",
            allow_fallback=allow_fallback,
        )
        return store, offline

    def test_unavailable_model_pauses_without_calling_adapter(self):
        calls = []

        def adapter(message, model):
            calls.append((message, model))
            return None

        async def run(service):
            return [event async for event in service.stream(
                "conversation-1", "hello", "missing-model",
            )]

        with tempfile.TemporaryDirectory() as directory:
            store, service = self._service(directory, adapter=adapter)
            try:
                events = asyncio.run(run(service))
                self.assertEqual(events[0]["status"], "paused")
                self.assertEqual(events[0]["reason"], "unsupported_model_alias")
                self.assertEqual(calls, [])
                self.assertEqual(store.list_turns("conversation-1"), [])
            finally:
                store.close()

    def test_explicit_fallback_uses_authorized_adapter(self):
        async def adapter(_message, model):
            yield {"content": model}

        async def run(service):
            return [event async for event in service.stream(
                "conversation-1", "hello", "gpt-5.6-luna",
            )]

        with tempfile.TemporaryDirectory() as directory:
            store, service = self._service(directory, adapter=adapter, allow_fallback=True)
            try:
                events = asyncio.run(run(service))
                self.assertEqual(events[0]["type"], "fallback")
                self.assertEqual(events[0]["selected_model"], "qwen3-8b")
                self.assertEqual(events[-1]["type"], "done")
                self.assertEqual(store.list_turns("conversation-1")[1]["model"], "qwen3-8b")
            finally:
                store.close()

    def test_fallback_requires_explicit_opt_in(self):
        called = False

        async def adapter(_message, _model):
            nonlocal called
            called = True
            yield {"content": "not used"}

        async def run(service):
            return [event async for event in service.stream(
                "conversation-1", "hello", "gpt-5.6-luna",
            )]

        with tempfile.TemporaryDirectory() as directory:
            store, service = self._service(directory, adapter=adapter)
            try:
                events = asyncio.run(run(service))
                self.assertEqual(events[0]["reason"], "unsupported_model_alias")
                self.assertFalse(called)
            finally:
                store.close()

    def test_registered_model_without_adapter_stays_paused(self):
        async def run(service):
            return [event async for event in service.stream(
                "conversation-1", "hello", "qwen3-8b",
            )]

        with tempfile.TemporaryDirectory() as directory:
            store, service = self._service(directory)
            try:
                events = asyncio.run(run(service))
                self.assertEqual(events[0]["reason"], "adapter_unavailable")
                self.assertEqual(store.list_turns("conversation-1"), [])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()
