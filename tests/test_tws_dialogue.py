import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import AureliaDialogue, QuestStore, TWSStoreError


class TWSDialogueTests(unittest.TestCase):
    def _rewarded(self, store: QuestStore) -> None:
        store.add_wing("wing-1", "Dawn")
        store.create_quest("quest-1", "wing-1", "Practice")
        for state in ("offered", "accepted", "in_progress"):
            store.transition_quest("quest-1", state)
        store.append_proof("proof-1", "quest-1", {"objective": "practice", "result": "done"})
        store.transition_quest("quest-1", "submitted")
        store.review_proof("proof-1", "accepted", "reviewer-1")
        store.transition_quest("quest-1", "verified")
        store.award_xp("profile-1", "reward-1", "quest-1", "proof-1", 7, "sync-1")

    def test_dialogue_state_and_turns_are_idempotent_without_reward_side_effects(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            self._rewarded(store)
            dialogue = AureliaDialogue(store)
            before_xp = store.xp_total("profile-1")
            first = dialogue.record_turn(
                "profile-1",
                "turn-1",
                "You completed the practice quest.",
                mood="encouraging",
                narrative_node="sanctuary",
            )
            self.assertNotIn("line", first)
            self.assertEqual(dialogue.state("profile-1")["personality"], "aurelia")
            self.assertEqual(dialogue.record_turn(
                "profile-1",
                "turn-1",
                "You completed the practice quest.",
                mood="encouraging",
                narrative_node="sanctuary",
            ), first)
            self.assertEqual(dialogue.turns("profile-1"), [first])
            self.assertEqual(store.xp_total("profile-1"), before_xp)
            self.assertFalse(hasattr(dialogue, "award_xp"))
            with self.assertRaisesRegex(TWSStoreError, "identity conflict"):
                dialogue.record_turn("profile-1", "turn-1", "Different line")

    def test_dialogue_inputs_are_bounded_and_mood_is_allowlisted(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            dialogue = AureliaDialogue(store)
            with self.assertRaisesRegex(TWSStoreError, "dialogue mood"):
                dialogue.record_turn("profile-1", "turn-1", "Hello", mood="persuading")
            with self.assertRaisesRegex(TWSStoreError, "dialogue line"):
                dialogue.record_turn("profile-1", "turn-1", "")


if __name__ == "__main__":
    unittest.main()
