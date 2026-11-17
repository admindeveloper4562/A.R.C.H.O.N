from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceBudget,
    FinanceCategory,
    FinanceIngestionError,
    FinanceStore,
    FinanceTransaction,
)


STAMP = datetime(2026, 11, 17, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def snapshot():
    return {
        "accounts": [FinanceAccount("acct-1", "Checking", "THB", STAMP)],
        "categories": [FinanceCategory("cat-1", "Food", STAMP)],
        "budgets": [FinanceBudget("budget-1", "cat-1", 12500, "2026-11-01", "2026-11-30", STAMP)],
        "transactions": [
            FinanceTransaction("txn-1", "acct-1", -1234, STAMP, STAMP, "cat-1", "Lunch", "THB")
        ],
    }


class FinanceIngestionTests(unittest.TestCase):
    def test_sync_preserves_original_ids_timestamps_and_integer_satang(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            result = store.sync("mira", "owner-1", **snapshot())
            self.assertEqual((result.inserted, result.updated, result.unchanged), (4, 0, 0))
            self.assertEqual(store.transactions("mira", "owner-1")[0].amount_satang, -1234)
            self.assertEqual(store.transactions("mira", "owner-1")[0].occurred_at, STAMP)
            self.assertEqual(store.accounts("mira", "owner-1")[0].account_id, "acct-1")
            self.assertEqual(store.budgets("mira", "owner-1")[0].amount_satang, 12500)

    def test_replaying_identical_snapshot_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", **snapshot())
            result = store.sync("mira", "owner-1", **snapshot())
            self.assertEqual((result.inserted, result.updated, result.unchanged), (0, 0, 4))
            self.assertEqual(len(store.transactions("mira", "owner-1")), 1)

    def test_newer_source_revision_updates_one_row_without_duplication(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", **snapshot())
            revised = FinanceTransaction("txn-1", "acct-1", -1300, STAMP, LATER, "cat-1", "Lunch", "THB")
            result = store.sync("mira", "owner-1", transactions=[revised])
            self.assertEqual((result.inserted, result.updated, result.unchanged), (0, 1, 0))
            self.assertEqual(store.transactions("mira", "owner-1")[0].amount_satang, -1300)

    def test_scope_isolation_is_required_for_reads(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", accounts=[FinanceAccount("acct-1", "One", "THB", STAMP)])
            self.assertEqual(store.accounts("mira", "owner-2"), ())

    def test_source_mappings_are_normalized_without_losing_original_ids(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            result = store.sync(
                "mira", "owner-1",
                accounts=[{"id": "acct-9", "name": "Wallet", "currency_code": "THB", "updated_at": STAMP}],
                transactions=[{
                    "id": "txn-9", "account_id": "acct-9", "amount_satang": 99,
                    "occurred_at": STAMP, "updated_at": STAMP,
                }],
            )
            self.assertEqual(result.total, 2)
            self.assertEqual(store.accounts("mira", "owner-1")[0].account_id, "acct-9")
            self.assertEqual(store.transactions("mira", "owner-1")[0].transaction_id, "txn-9")

    def test_invalid_precision_and_timestamps_fail_closed(self):
        with self.assertRaisesRegex(FinanceIngestionError, "integer satang"):
            FinanceTransaction("txn-1", "acct-1", 12.5, STAMP, STAMP)
        with self.assertRaisesRegex(FinanceIngestionError, "timezone"):
            FinanceAccount("acct-1", "Checking", "THB", "2026-11-17T02:00:00")

    def test_conflicting_revision_rolls_back_the_whole_snapshot(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", accounts=[FinanceAccount("acct-1", "Checking", "THB", STAMP)])
            with self.assertRaisesRegex(FinanceIngestionError, "conflicts"):
                store.sync(
                    "mira", "owner-1",
                    accounts=[FinanceAccount("acct-1", "Changed", "THB", STAMP)],
                    categories=[FinanceCategory("cat-1", "Food", LATER)],
                )
            self.assertEqual(store.accounts("mira", "owner-1")[0].name, "Checking")
            self.assertEqual(store.categories("mira", "owner-1"), ())


if __name__ == "__main__":
    unittest.main()
