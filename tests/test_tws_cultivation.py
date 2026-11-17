import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import QuestStore, TWSStoreError


class TWSCultivationTests(unittest.TestCase):
    def _submitted(self, store: QuestStore, suffix: str = "1") -> tuple[str, str]:
        wing_id = "wing-" + suffix
        quest_id = "quest-" + suffix
        proof_id = "proof-" + suffix
        store.add_wing(wing_id, "Dawn")
        store.create_quest(quest_id, wing_id, "Practice")
        for state in ("offered", "accepted", "in_progress"):
            store.transition_quest(quest_id, state)
        store.append_proof(proof_id, quest_id, {"objective": "practice", "result": "done"})
        store.transition_quest(quest_id, "submitted")
        return quest_id, proof_id

    def _verified_with_reward(
        self, store: QuestStore, suffix: str, xp: int = 5
    ) -> tuple[str, str]:
        quest_id, proof_id = self._submitted(store, suffix)
        store.review_proof(proof_id, "accepted", "reviewer-1")
        store.transition_quest(quest_id, "verified")
        store.award_xp("profile-1", "reward-" + suffix, quest_id, proof_id, xp, "sync-" + suffix)
        return quest_id, proof_id

    def test_progression_requires_independent_proof_acceptance(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            quest_id, proof_id = self._submitted(store)
            with self.assertRaisesRegex(TWSStoreError, "independently accepted"):
                store.record_achievement("profile-1", "achievement-1", "focus", "practice", quest_id, proof_id, "sync-1")
            store.review_proof(proof_id, "accepted", "reviewer-1")
            store.transition_quest(quest_id, "verified")
            achievement = store.record_achievement(
                "profile-1", "achievement-1", "focus", "practice", quest_id, proof_id, "sync-1"
            )
            self.assertEqual(achievement["evidence_sha256"], store.proofs(quest_id)[0]["evidence_sha256"])

    def test_achievement_and_adaptation_are_idempotent_and_fair(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            quest_id, proof_id = self._verified_with_reward(store, "1")
            first = store.record_achievement(
                "profile-1", "achievement-1", "focus", "practice", quest_id, proof_id, "sync-1"
            )
            self.assertEqual(
                store.record_achievement(
                    "profile-1", "achievement-1", "focus", "practice", quest_id, proof_id, "sync-1"
                ),
                first,
            )
            with self.assertRaisesRegex(TWSStoreError, "identity conflict"):
                store.record_achievement(
                    "profile-1", "achievement-2", "focus", "different", quest_id, proof_id, "sync-2"
                )
            self.assertEqual(
                store.cultivation_progress("profile-1", "focus"),
                {
                    "profile_id": "profile-1",
                    "skill_id": "focus",
                    "verified_achievements": 1,
                    "pattern_counts": {"practice": 1},
                    "xp": 5,
                },
            )
            adaptation = store.adapt_skill("profile-1", "adaptation-1", "focus")
            self.assertEqual(adaptation["pattern"], "practice")
            self.assertEqual(
                store.adapt_skill("profile-1", "adaptation-1", "focus"), adaptation
            )
            with self.assertRaisesRegex(TWSStoreError, "no verified achievement"):
                store.adapt_skill("profile-1", "adaptation-2", "focus", pattern="persuasion")


if __name__ == "__main__":
    unittest.main()
