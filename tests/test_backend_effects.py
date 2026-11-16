import tempfile
import unittest
from pathlib import Path

from jarvis_v2.backend import EffectJournal, EffectJournalError


class BackendEffectJournalTests(unittest.TestCase):
    def test_completed_effect_is_not_executed_again_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "effects.sqlite"
            with EffectJournal(path) as journal:
                prepared = journal.prepare(
                    "effect-1", "BACK-012", operation="email.send", target="mailbox-1",
                    request={"message_ref": "notice-1"},
                )
                self.assertTrue(prepared["execution_permitted"])
                journal.complete("effect-1", {"receipt_ref": "mail-1"})
            with EffectJournal(path) as reopened:
                replay = reopened.prepare(
                    "effect-1", "BACK-012", operation="email.send", target="mailbox-1",
                    request={"message_ref": "notice-1"},
                )
                self.assertEqual((replay["status"], replay["execution_permitted"]), ("completed", False))
                self.assertEqual(replay["result"], {"receipt_ref": "mail-1"})

    def test_unfinished_effect_requires_reconciliation_before_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "effects.sqlite"
            with EffectJournal(path) as journal:
                first = journal.prepare(
                    "effect-1", "BACK-012", operation="git.write", target="worktree-1",
                    request={"change_ref": "change-1"},
                )
                self.assertTrue(first["execution_permitted"])
            with EffectJournal(path) as reopened:
                pending = reopened.reconcile_pending()
                self.assertEqual(pending[0]["status"], "needs_reconciliation")
                replay = reopened.prepare(
                    "effect-1", "BACK-012", operation="git.write", target="worktree-1",
                    request={"change_ref": "change-1"},
                )
                self.assertFalse(replay["execution_permitted"])
                self.assertEqual(reopened.complete("effect-1", {"observed": True})["status"], "completed")
                self.assertEqual(reopened.pending(), [])

    def test_effect_identity_and_result_replays_are_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            with EffectJournal(Path(directory) / "effects.sqlite") as journal:
                values = {
                    "operation": "file.write",
                    "target": "worktree-1",
                    "request": {"change_ref": "change-1"},
                }
                journal.prepare("effect-1", "BACK-012", **values)
                with self.assertRaises(EffectJournalError):
                    journal.prepare("effect-1", "BACK-013", **values)
                journal.complete("effect-1", {"receipt_ref": "file-1"})
                self.assertEqual(
                    journal.complete("effect-1", {"receipt_ref": "file-1"})["status"],
                    "completed",
                )
                with self.assertRaises(EffectJournalError):
                    journal.complete("effect-1", {"receipt_ref": "file-2"})

    def test_invalid_effects_do_not_create_records(self):
        with tempfile.TemporaryDirectory() as directory:
            with EffectJournal(Path(directory) / "effects.sqlite") as journal:
                with self.assertRaises(EffectJournalError):
                    journal.prepare(
                        "effect-1", "BACK-012", operation="file.write", target="worktree-1",
                        request={"bad": float("nan")},
                    )
                with self.assertRaises(EffectJournalError):
                    journal.prepare(
                        "effect-2", "BACK-012", operation="file.write", target="worktree-1",
                        request=["not-an-object"],
                    )
                self.assertEqual(journal.pending(), [])


if __name__ == "__main__":
    unittest.main()
