import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend.storage import StorageManager
from jarvis_v2.tws import QuestStore, TWS_MIGRATIONS, TWS_SCHEMA_VERSION, TWSStoreError


class TWSStorageTests(unittest.TestCase):
    def test_versioned_upgrade_preserves_wings_and_proofs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tws.sqlite"
            with StorageManager(path, migrations=TWS_MIGRATIONS[:2]) as storage:
                storage.migrate()
                storage.module("tws").insert(
                    "tws_wings",
                    {"wing_id": "wing-1", "name": "Dawn", "state": "active",
                     "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"},
                )
                storage.module("tws").insert(
                    "tws_quests",
                    {"quest_id": "quest-1", "wing_id": "wing-1", "title": "First quest",
                     "state": "draft", "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"},
                )
                storage.module("tws").insert(
                    "tws_proofs",
                    {"proof_id": "proof-1", "quest_id": "quest-1", "evidence_json": '{"ok":true}',
                     "evidence_sha256": "4062edaf750fb8074e7e83e0c9028c94e32468a8b6f1614774328ef045150f93",
                     "review_state": "submitted", "submitted_at": "2026-01-01T00:00:00Z", "reviewed_at": None},
                )
            with QuestStore(path) as store:
                self.assertEqual(store.schema_version, TWS_SCHEMA_VERSION)
                self.assertEqual(store.wing("wing-1")["name"], "Dawn")
                self.assertEqual(store.quest("quest-1")["title"], "First quest")
                self.assertEqual(store.proofs("quest-1")[0]["proof_id"], "proof-1")

    def test_retries_are_idempotent_and_duplicate_proofs_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            first_wing = store.add_wing("wing-1", "Dawn")
            self.assertEqual(store.add_wing("wing-1", "Dawn"), first_wing)
            quest = store.create_quest("quest-1", "wing-1", "First quest")
            self.assertEqual(store.create_quest("quest-1", "wing-1", "First quest"), quest)
            proof = store.append_proof("proof-1", "quest-1", {"source": "local", "value": 1})
            self.assertEqual(store.append_proof("proof-1", "quest-1", {"value": 1, "source": "local"}), proof)
            with self.assertRaises(TWSStoreError):
                store.append_proof("proof-2", "quest-1", {"source": "local", "value": 1})
            with self.assertRaises(TWSStoreError):
                store.add_wing("wing-1", "Changed")

    def test_rejects_unknown_references_and_invalid_evidence(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            with self.assertRaises(TWSStoreError):
                store.create_quest("quest-1", "missing-wing", "First quest")
            store.add_wing("wing-1", "Dawn")
            store.create_quest("quest-1", "wing-1", "First quest")
            with self.assertRaises(TWSStoreError):
                store.append_proof("proof-1", "missing-quest", {})
            with self.assertRaises(TWSStoreError):
                store.append_proof("proof-1", "quest-1", {"bad": float("nan")})


if __name__ == "__main__":
    unittest.main()
