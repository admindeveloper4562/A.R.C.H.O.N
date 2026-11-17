import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import QuestStore, TWS_SCHEMA_VERSION, TWSStoreError


class TWSRewardTests(unittest.TestCase):
    def _verified_quest(self, store: QuestStore, suffix: str = "1") -> tuple[str, str]:
        store.add_wing("wing-" + suffix, "Dawn")
        store.create_quest("quest-" + suffix, "wing-" + suffix, "Practice")
        for state in ("offered", "accepted", "in_progress"):
            store.transition_quest("quest-" + suffix, state)
        store.append_proof("proof-" + suffix, "quest-" + suffix, {"result": "done"})
        store.transition_quest("quest-" + suffix, "submitted")
        return "quest-" + suffix, "proof-" + suffix

    def test_review_gate_and_reward_retry_are_idempotent(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            self.assertEqual(store.schema_version, TWS_SCHEMA_VERSION)
            quest_id, proof_id = self._verified_quest(store)
            with self.assertRaises(TWSStoreError):
                store.transition_quest(quest_id, "verified")
            store.review_proof(proof_id, "accepted", "reviewer-1")
            store.transition_quest(quest_id, "verified")
            first = store.award_xp("profile-1", "reward-1", quest_id, proof_id, 10, "sync-1")
            retry = store.award_xp("profile-1", "reward-2", quest_id, proof_id, 10, "sync-1")
            self.assertEqual(retry, first)
            store.transition_quest(quest_id, "rewarded")
            late_retry = store.award_xp("profile-1", "reward-3", quest_id, proof_id, 10, "sync-1")
            self.assertEqual(late_retry, first)
            self.assertEqual(store.xp_total("profile-1"), 10)

    def test_rejected_proof_and_invalid_scope_cannot_be_rewarded(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            quest_id, proof_id = self._verified_quest(store)
            store.review_proof(proof_id, "rejected", "reviewer-1")
            with self.assertRaises(TWSStoreError):
                store.transition_quest(quest_id, "verified")
            with self.assertRaises(TWSStoreError):
                store.award_xp("profile-1", "reward-1", quest_id, proof_id, 10, "sync-1")
            with self.assertRaises(TWSStoreError):
                store.append_proof("bad-proof", quest_id, {"result": "other"}, privacy_scope="unknown")

    def test_realm_prerequisites_and_xp_thresholds_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            store.define_realm("realm-1", "Awakening")
            store.define_realm("realm-2", "Ascension", min_xp=10, prerequisites=("realm-1",))
            with self.assertRaises(TWSStoreError):
                store.unlock_realm("profile-1", "realm-2")
            store.unlock_realm("profile-1", "realm-1")
            quest_id, proof_id = self._verified_quest(store, "2")
            store.review_proof(proof_id, "accepted", "reviewer-1")
            store.transition_quest(quest_id, "verified")
            store.award_xp("profile-1", "reward-1", quest_id, proof_id, 10, "sync-1")
            store.unlock_realm("profile-1", "realm-2")


if __name__ == "__main__":
    unittest.main()
