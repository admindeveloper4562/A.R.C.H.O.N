from datetime import datetime, timezone
import tempfile
import unittest

from jarvis_v2.wic import CategoryStore, WICError


STAMP = datetime(2026, 11, 17, 1, 2, 3, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
CLUSTER = "a" * 32


class WICCategoryTests(unittest.TestCase):
    def test_assignments_are_searchable(self):
        with tempfile.TemporaryDirectory() as directory:
            with CategoryStore(directory + "/wic.sqlite") as store:
                assignment = store.assign(CLUSTER, ("politics", "thailand"), STAMP)
                self.assertEqual(assignment.categories, ("politics", "thailand"))
                self.assertEqual(store.search("politics"), (assignment,))
                self.assertEqual(store.search("science"), ())

    def test_correction_replaces_current_search_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as directory:
            with CategoryStore(directory + "/wic.sqlite") as store:
                original = store.assign(CLUSTER, ("politics",), STAMP)
                corrected = store.correct(CLUSTER, ("technology", "thailand"), "reclassified", STAMP)
                self.assertEqual(store.get(CLUSTER), corrected)
                self.assertEqual(store.search("politics"), ())
                self.assertEqual(store.search("technology"), (corrected,))
                self.assertEqual(store.history(CLUSTER), (original, corrected))

    def test_invalid_category_and_duplicate_assignment_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with CategoryStore(directory + "/wic.sqlite") as store:
                with self.assertRaisesRegex(WICError, "invalid WIC category"):
                    store.assign(CLUSTER, ("politics", "horoscope"), STAMP)
                store.assign(CLUSTER, ("politics",), STAMP)
                with self.assertRaisesRegex(WICError, "already exists"):
                    store.assign(CLUSTER, ("science",), STAMP)

    def test_history_survives_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + "/wic.sqlite"
            with CategoryStore(path) as store:
                store.assign(CLUSTER, ("geography",), STAMP)
                store.correct(CLUSTER, ("economics",), "new evidence", STAMP)
            with CategoryStore(path) as store:
                self.assertEqual(store.get(CLUSTER).categories, ("economics",))
                self.assertEqual(len(store.history(CLUSTER)), 2)


if __name__ == "__main__":
    unittest.main()
