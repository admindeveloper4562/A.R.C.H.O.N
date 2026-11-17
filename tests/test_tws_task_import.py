import hashlib
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.tws import QuestStore, TWS_SCHEMA_VERSION, TWSStoreError


class TWSTaskImportTests(unittest.TestCase):
    def _task(self, task_id="CORE-IMPORT-1", source_module="core"):
        source_sha = hashlib.sha256(task_id.encode()).hexdigest()
        return {
            "task_id": task_id,
            "source_module": source_module,
            "source_sha256": source_sha,
            "wing_id": "wing-1",
            "title": "Review one bounded task",
            "kind": "skill",
            "cadence": "once",
        }

    def test_import_is_consent_bound_idempotent_and_draft_only(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            self.assertEqual(store.schema_version, TWS_SCHEMA_VERSION)
            store.add_wing("wing-1", "Dawn")
            task = self._task()
            first = store.import_tasks_as_quests(
                [task], consent_id="consent-1", consent_scope="internal_metadata"
            )
            retry = store.propose_task_quests(
                [task], consent_id="consent-1", consent_scope="internal_metadata"
            )
            self.assertEqual(retry, first)
            self.assertEqual(first[0]["quest"]["state"], "draft")
            self.assertEqual(first[0]["proposal"]["reward_gate"], "explicit_review")
            self.assertEqual(store.task_quest_proposals(), [first[0]["proposal"]])
            self.assertEqual(store.xp_total("profile-1"), 0)

    def test_import_rejects_missing_consent_or_same_task_mutation(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            store.add_wing("wing-1", "Dawn")
            task = self._task()
            with self.assertRaises(TWSStoreError):
                store.import_tasks_as_quests([task], consent_id="", consent_scope="internal_metadata")
            store.import_tasks_as_quests([task], consent_id="consent-1", consent_scope="internal_metadata")
            changed = dict(task, source_sha256="f" * 64)
            with self.assertRaises(TWSStoreError):
                store.import_tasks_as_quests(
                    [changed], consent_id="consent-1", consent_scope="internal_metadata"
                )

    def test_import_accepts_only_known_cross_module_sources(self):
        with tempfile.TemporaryDirectory() as directory, QuestStore(Path(directory) / "tws.sqlite") as store:
            store.add_wing("wing-1", "Dawn")
            with self.assertRaises(TWSStoreError):
                store.import_tasks_as_quests(
                    [self._task(source_module="tws")],
                    consent_id="consent-1", consent_scope="internal_metadata",
                )
            with self.assertRaises(TWSStoreError):
                store.import_tasks_as_quests(
                    [self._task(source_module="unknown")],
                    consent_id="consent-1", consent_scope="internal_metadata",
                )


if __name__ == "__main__":
    unittest.main()
