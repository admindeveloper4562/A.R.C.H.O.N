import tempfile
import unittest
from pathlib import Path

from jarvis_v2.wic import WICError, WatchlistStore


STAMP = "2026-11-17T00:00:00Z"


class WICWatchlistTests(unittest.TestCase):
    def test_owner_can_save_and_reopen_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "watchlists.sqlite"
            with WatchlistStore(path) as store:
                saved = store.save(
                    "owner-1", ["Thailand"], ["Southeast Asia"], ["politics", "science"],
                    STAMP, requester_id="owner-1",
                )
                self.assertEqual(saved.revision, 1)
                self.assertEqual(saved.topics, ("politics", "science"))
            with WatchlistStore(path) as store:
                restored = store.get("owner-1", requester_id="owner-1")
                self.assertEqual(restored, saved)
                self.assertEqual(store.history("owner-1", requester_id="owner-1"), (saved,))

    def test_preferences_are_owner_scoped(self):
        with tempfile.TemporaryDirectory() as directory:
            with WatchlistStore(Path(directory) / "watchlists.sqlite") as store:
                with self.assertRaises(WICError):
                    store.get("owner-1", requester_id="other-owner")
                with self.assertRaises(WICError):
                    store.save("owner-1", [], [], ["science"], STAMP, requester_id="other-owner")

    def test_unchanged_save_is_idempotent_and_changes_are_revisioned(self):
        with tempfile.TemporaryDirectory() as directory:
            with WatchlistStore(Path(directory) / "watchlists.sqlite") as store:
                first = store.save("owner-1", [], [], ["science"], STAMP, requester_id="owner-1")
                same = store.save(
                    "owner-1", [], [], ["science"], "2026-11-18T00:00:00Z", requester_id="owner-1"
                )
                changed = store.save(
                    "owner-1", ["Japan"], [], ["science"], "2026-11-18T00:00:00Z", requester_id="owner-1"
                )
                self.assertEqual(same, first)
                self.assertEqual(changed.revision, 2)
                self.assertEqual([item.revision for item in store.history("owner-1", requester_id="owner-1")], [1, 2])

    def test_invalid_duplicate_preferences_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with WatchlistStore(Path(directory) / "watchlists.sqlite") as store:
                with self.assertRaises(WICError):
                    store.save("owner-1", ["Thailand", "Thailand"], [], [], STAMP, requester_id="owner-1")


if __name__ == "__main__":
    unittest.main()
