import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import QuestStore


class TWSSanctuaryTests(unittest.TestCase):
    def test_sanctuary_snapshot_reads_current_wing_and_quest_ledger(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            store.add_wing("wing-1", "Dawn")
            store.add_wing("wing-2", "Dusk", state="resting")
            store.create_quest("quest-1", "wing-1", "Practice")
            store.create_quest("quest-2", "wing-2", "Reflect", kind="story")
            first = store.sanctuary_snapshot("profile-1")
            self.assertEqual(first["source"], "tws_ledger")
            self.assertEqual([item["wing_id"] for item in first["wings"]], ["wing-1", "wing-2"])
            self.assertEqual([item["state"] for item in first["quests"]], ["draft", "draft"])
            self.assertEqual(first["progress"], {
                "profile_id": "profile-1",
                "xp": 0,
                "unlocked_realms": [],
            })
            store.transition_quest("quest-1", "offered")
            second = store.sanctuary_snapshot("profile-1")
            self.assertEqual(second["quests"][0]["state"], "offered")
            self.assertEqual(second["wings"], first["wings"])


if __name__ == "__main__":
    unittest.main()
