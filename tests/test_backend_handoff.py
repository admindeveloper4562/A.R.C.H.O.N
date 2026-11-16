import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import HandoffError, HandoffStore


class BackendHandoffTests(unittest.TestCase):
    def test_handoff_preserves_task_permissions_effects_and_context_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "handoff.sqlite"
            with HandoffStore(path) as store:
                first = store.handoff(
                    "BACK-011",
                    "handoff-1",
                    source_provider="codex",
                    target_provider="ollama",
                    permission_scopes=["backend:health", "backend:read"],
                    tool_effects=[{"effect_id": "read-1", "status": "accepted"}],
                    context={"checkpoint": "c1"},
                )
                self.assertEqual(first["task_id"], "BACK-011")
                self.assertEqual(first["permission_scopes"], ["backend:health", "backend:read"])
                self.assertEqual(first["tool_effects"][0]["effect_id"], "read-1")
            with HandoffStore(path) as reopened:
                restored = reopened.get("handoff-1")
                self.assertEqual(restored["target_provider"], "ollama")
                self.assertEqual(reopened.list_for_task("BACK-011"), [restored])

    def test_handoff_replay_is_idempotent_and_conflicts_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with HandoffStore(Path(directory) / "handoff.sqlite") as store:
                values = {
                    "source_provider": "codex",
                    "target_provider": "ollama",
                    "permission_scopes": ["backend:read"],
                    "tool_effects": [],
                }
                first = store.handoff("BACK-011", "handoff-1", **values)
                self.assertEqual(first, store.handoff("BACK-011", "handoff-1", **values))
                with self.assertRaises(HandoffError):
                    store.handoff("BACK-012", "handoff-1", **values)

    def test_handoff_rejects_invalid_or_unbounded_inputs_without_a_record(self):
        with tempfile.TemporaryDirectory() as directory:
            with HandoffStore(Path(directory) / "handoff.sqlite") as store:
                with self.assertRaises(HandoffError):
                    store.handoff(
                        "BACK-011", "handoff-1", source_provider="codex",
                        target_provider="codex", permission_scopes=["backend:read"],
                    )
                with self.assertRaises(HandoffError):
                    store.handoff(
                        "BACK-011", "handoff-2", source_provider="codex",
                        target_provider="ollama", permission_scopes=["backend:read"],
                        tool_effects=["not-an-effect"],
                    )
                self.assertEqual(store.list_for_task("BACK-011"), [])


if __name__ == "__main__":
    unittest.main()
