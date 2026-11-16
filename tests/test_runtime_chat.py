import asyncio
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.runtime.chat import ChatService


async def _deltas(*values):
    for value in values:
        yield {"content": value}


class RuntimeChatTests(unittest.TestCase):
    def test_completed_stream_persists_only_after_done(self):
        async def run(store):
            service = ChatService(store)
            events = [event async for event in service.stream(
                "conversation-1", "hello", lambda _message: _deltas("he", "llo"),
                provider_id="codex", model="gpt-5.6-luna", idempotency_key="chat-1",
            )]
            return events

        with tempfile.TemporaryDirectory() as directory:
            with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                events = asyncio.run(self._with_conversation(store, run))
                self.assertEqual([event["type"] for event in events], ["delta", "delta", "done"])
                turns = store.list_turns("conversation-1")
                self.assertEqual([turn["role"] for turn in turns], ["user", "assistant"])
                self.assertEqual([turn["content"] for turn in turns], ["hello", "hello"])

    async def _with_conversation(self, store, callback):
        store.create_conversation("conversation-1")
        return await callback(store)

    def test_cancellation_does_not_persist_a_successful_turn(self):
        async def run(store, cancel_event):
            service = ChatService(store)
            async def provider(_message):
                yield {"content": "partial"}
                cancel_event.set()
                yield {"content": "never-saved"}
            return [event async for event in service.stream(
                "conversation-1", "hello", provider, cancel_event=cancel_event,
            )]

        with tempfile.TemporaryDirectory() as directory:
            with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                store.create_conversation("conversation-1")
                cancel_event = asyncio.Event()
                events = asyncio.run(run(store, cancel_event))
                self.assertEqual(events[-1]["error"]["code"], "cancelled")
                self.assertEqual(store.list_turns("conversation-1"), [])

    def test_provider_failures_are_precise_and_not_persisted(self):
        async def run(store, failure):
            async def provider(_message):
                raise failure
                yield  # Keep this an async generator.
            return [event async for event in ChatService(store).stream(
                "conversation-1", "hello", provider,
            )]

        for failure, code in ((TimeoutError(), "provider_timeout"), (ConnectionError(), "provider_unavailable")):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                    store.create_conversation("conversation-1")
                    events = asyncio.run(run(store, failure))
                    self.assertEqual(events[0]["type"], "error")
                    self.assertEqual(events[0]["error"]["code"], code)
                    self.assertTrue(events[0]["error"]["message"])
                    self.assertEqual(store.list_turns("conversation-1"), [])

    def test_invalid_delta_and_empty_response_are_not_successes(self):
        async def run(provider):
            with tempfile.TemporaryDirectory() as directory:
                with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                    store.create_conversation("conversation-1")
                    return [event async for event in ChatService(store).stream(
                        "conversation-1", "hello", provider,
                    )], store.list_turns("conversation-1")

        async def invalid(_message):
            yield {"content": 1}

        async def empty(_message):
            if False:
                yield {"content": ""}

        invalid_events, invalid_turns = asyncio.run(run(invalid))
        empty_events, empty_turns = asyncio.run(run(empty))
        self.assertEqual(invalid_events[-1]["error"]["code"], "provider_invalid")
        self.assertEqual(empty_events[-1]["error"]["code"], "empty_response")
        self.assertEqual(invalid_turns, [])
        self.assertEqual(empty_turns, [])


if __name__ == "__main__":
    unittest.main()
