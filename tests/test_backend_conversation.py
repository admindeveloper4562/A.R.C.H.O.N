import tempfile
import os
import subprocess
import sys
import unittest
from pathlib import Path

from jarvis_v2.backend.conversation import ConversationStore, ConversationStoreError


class BackendConversationTests(unittest.TestCase):
    def test_backend_exports_are_safe_when_core_is_imported_first(self):
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
        result = subprocess.run(
            [sys.executable, "-c", "import jarvis_v2.core; from jarvis_v2.backend import ConversationStore"],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_turns_are_durable_ordered_and_provider_neutral(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "conversation.sqlite"
            with ConversationStore(path) as store:
                conversation = store.create_conversation(
                    "conversation-1", metadata={"scope": "local"}
                )
                first = store.append_turn(
                    conversation["conversation_id"],
                    role="user",
                    provider="codex",
                    model="gpt-5.6-luna",
                    content="hello",
                    idempotency_key="turn-1",
                )
                second = store.append_turn(
                    conversation["conversation_id"],
                    role="assistant",
                    provider="ollama",
                    model="qwen3:8b",
                    content="hi",
                    tool_effects=[{"effect_id": "read-1", "status": "accepted"}],
                    idempotency_key="turn-2",
                )
                self.assertEqual([first["sequence"], second["sequence"]], [1, 2])
                self.assertEqual(second["tool_effects"][0]["effect_id"], "read-1")
            with ConversationStore(path) as reopened:
                restored = reopened.get_conversation("conversation-1")
                self.assertEqual(restored["metadata"], {"scope": "local"})
                self.assertEqual([turn["provider"] for turn in restored["turns"]], ["codex", "ollama"])

    def test_turn_replay_is_idempotent_and_conflicts_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                store.create_conversation("conversation-1")
                first = store.append_turn(
                    "conversation-1", role="user", provider="codex", content="same",
                    idempotency_key="turn-1", turn_id="turn-record-1",
                )
                replay = store.append_turn(
                    "conversation-1", role="user", provider="codex", content="same",
                    idempotency_key="turn-1", turn_id="turn-record-1",
                )
                self.assertEqual(first, replay)
                with self.assertRaises(ConversationStoreError):
                    store.append_turn(
                        "conversation-1", role="user", provider="codex", content="changed",
                        idempotency_key="turn-1", turn_id="turn-record-1",
                    )
                implicit = store.append_turn(
                    "conversation-1", role="assistant", provider="codex", content="reply",
                    idempotency_key="turn-2",
                )
                self.assertEqual(
                    implicit,
                    store.append_turn(
                        "conversation-1", role="assistant", provider="codex", content="reply",
                        idempotency_key="turn-2",
                    ),
                )

    def test_invalid_and_unbounded_values_are_rejected_without_partial_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                store.create_conversation("conversation-1")
                with self.assertRaises(ConversationStoreError):
                    store.append_turn("conversation-1", role="user", provider="codex", content="x", tool_effects=["raw"])
                with self.assertRaises(ConversationStoreError):
                    store.append_turn("conversation-1", role="user", provider="codex", content="x", tool_effects=[{"x": "y"}] * 33)
                with self.assertRaises(ConversationStoreError):
                    store.append_turn("conversation-1", role="unknown", provider="codex", content="x")
                self.assertEqual(store.list_turns("conversation-1"), [])

    def test_explicit_conversation_creation_is_idempotent_but_metadata_is_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            with ConversationStore(Path(directory) / "conversation.sqlite") as store:
                self.assertEqual(store.create_conversation("conversation-1"), store.create_conversation("conversation-1"))
                with self.assertRaises(ConversationStoreError):
                    store.open_conversation("conversation-1", metadata={"changed": True})


if __name__ == "__main__":
    unittest.main()
