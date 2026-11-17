import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import QuestStore, TWS_SCHEMA_VERSION, TWSStoreError


class TWSLifecycleTests(unittest.TestCase):
    def test_catalog_metadata_and_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            self.assertEqual(store.schema_version, TWS_SCHEMA_VERSION)
            store.add_wing("wing-1", "Dawn")
            quest = store.create_quest(
                "quest-1", "wing-1", "Daily practice", kind="daily", cadence="daily"
            )
            self.assertEqual(quest["kind"], "daily")
            self.assertEqual(quest["cadence"], "daily")
            for state in ("offered", "accepted", "in_progress"):
                quest = store.transition_quest("quest-1", state)
            store.append_proof("proof-1", "quest-1", {"result": "done"})
            quest = store.transition_quest("quest-1", "submitted")
            store.review_proof("proof-1", "accepted", "reviewer-1")
            for state in ("verified", "rewarded"):
                quest = store.transition_quest("quest-1", state)
            self.assertEqual(quest["state"], "rewarded")
            self.assertEqual(store.catalog(kind="daily", state="rewarded")[0]["quest_id"], "quest-1")

    def test_invalid_transition_and_missing_proof_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            store.add_wing("wing-1", "Dawn")
            store.create_quest("quest-1", "wing-1", "Skill practice")
            with self.assertRaises(TWSStoreError):
                store.transition_quest("quest-1", "verified")
            with self.assertRaises(TWSStoreError):
                store.transition_quest("quest-1", "archived")
            with self.assertRaises(TWSStoreError):
                store.create_quest("quest-2", "wing-1", "Bad", kind="unknown")


if __name__ == "__main__":
    unittest.main()
