import asyncio
from pathlib import Path
import tempfile
import unittest

from jarvis_v2.backend.conversation import ConversationStore
from jarvis_v2.runtime import SpeechService


class _Adapter:
    def __init__(self):
        self.stopped = False

    def __call__(self, _text, _voice):
        async def audio():
            yield b"first"
            yield b"second"
        return audio()

    def stop(self):
        self.stopped = True


class RuntimeSpeechTests(unittest.TestCase):
    def test_streams_bounded_audio_and_completes(self):
        adapter = _Adapter()
        events = asyncio.run(self._events(SpeechService(adapter).stream("hello")))
        self.assertEqual([event["type"] for event in events], ["audio", "audio", "done"])
        self.assertEqual([event["content"] for event in events[:2]], [b"first", b"second"])
        self.assertEqual(events[-1]["voice"], "en_GB")
        self.assertFalse(adapter.stopped)

    def test_interruption_stops_adapter_without_persisting_speech(self):
        async def run(store):
            adapter = _Adapter()
            cancelled = asyncio.Event()
            events = []
            async for event in SpeechService(adapter).stream("hello", cancel_event=cancelled):
                events.append(event)
                if event["type"] == "audio":
                    cancelled.set()
            return adapter, events, store.list_turns("conversation-1")

        with tempfile.TemporaryDirectory() as directory:
            with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                store.create_conversation("conversation-1")
                adapter, events, turns = asyncio.run(run(store))
        self.assertEqual([event["type"] for event in events], ["audio", "error"])
        self.assertEqual(events[-1]["error"]["code"], "cancelled")
        self.assertTrue(adapter.stopped)
        self.assertEqual(turns, [])

    def test_adapter_failure_does_not_report_success(self):
        def broken(_text, _voice):
            raise OSError("offline")

        events = asyncio.run(self._events(SpeechService(broken).stream("hello")))
        self.assertEqual(events[-1]["type"], "error")
        self.assertEqual(events[-1]["error"]["code"], "provider_unavailable")
        self.assertNotIn("done", [event["type"] for event in events])

    def test_invalid_audio_is_rejected(self):
        def broken(_text, _voice):
            return ["not audio"]

        events = asyncio.run(self._events(SpeechService(broken).stream("hello")))
        self.assertEqual(events[-1]["error"]["code"], "provider_invalid")

    @staticmethod
    async def _events(stream):
        return [event async for event in stream]


if __name__ == "__main__":
    unittest.main()
