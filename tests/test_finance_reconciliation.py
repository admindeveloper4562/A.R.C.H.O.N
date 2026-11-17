from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceOperation,
    FinanceReconciliationError,
    FinanceReconciliationStore,
)


STAMP = datetime(2026, 11, 17, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinanceReconciliationTests(unittest.TestCase):
    def test_transfer_is_applied_once_and_has_zero_net_effect(self):
        operation = FinanceOperation("transfer-1", "transfer", "checking", 1000, STAMP, STAMP, "savings")
        with tempfile.TemporaryDirectory() as directory, FinanceReconciliationStore(Path(directory) / "finance.sqlite") as store:
            first = store.sync("mira", "owner-1", [operation])
            replay = store.sync("mira", "owner-1", [operation])
            self.assertEqual((first.inserted, first.net_effect_satang), (1, 0))
            self.assertEqual((replay.inserted, replay.unchanged), (0, 1))
            self.assertEqual(store.account_deltas("mira", "owner-1"), {"checking": -1000, "savings": 1000})

    def test_savings_has_transfer_semantics_and_adjustment_is_applied_once(self):
        operations = [
            FinanceOperation("save-1", "savings", "checking", 2500, STAMP, STAMP, "savings"),
            FinanceOperation("adjust-1", "adjustment", "checking", -100, STAMP, STAMP),
        ]
        with tempfile.TemporaryDirectory() as directory, FinanceReconciliationStore(Path(directory) / "finance.sqlite") as store:
            result = store.sync("mira", "owner-1", operations)
            self.assertEqual(result.net_effect_satang, -100)
            self.assertEqual(store.reconcile("mira", "owner-1", {"checking": 10_000}), {"checking": 7_400, "savings": 2_500})

    def test_newer_revision_replaces_effect_without_creating_a_second_operation(self):
        with tempfile.TemporaryDirectory() as directory, FinanceReconciliationStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", [FinanceOperation("transfer-1", "transfer", "a", 100, STAMP, STAMP, "b")])
            result = store.sync("mira", "owner-1", [FinanceOperation("transfer-1", "transfer", "a", 150, STAMP, LATER, "b")])
            self.assertEqual((result.updated, len(store.operations("mira", "owner-1"))), (1, 1))
            self.assertEqual(store.account_deltas("mira", "owner-1"), {"a": -150, "b": 150})

    def test_scope_isolation_and_mapping_input_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory, FinanceReconciliationStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", [{
                "id": "adjust-1", "kind": "adjustment", "account_id": "a",
                "amount_satang": 7, "occurred_at": STAMP, "updated_at": STAMP,
            }])
            self.assertEqual(store.operations("mira", "owner-2"), ())

    def test_invalid_transfer_and_stale_conflict_fail_closed(self):
        with self.assertRaisesRegex(FinanceReconciliationError, "two distinct"):
            FinanceOperation("transfer-1", "transfer", "a", 100, STAMP, STAMP, "a")
        with tempfile.TemporaryDirectory() as directory, FinanceReconciliationStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "owner-1", [FinanceOperation("adjust-1", "adjustment", "a", 100, STAMP, LATER)])
            with self.assertRaisesRegex(FinanceReconciliationError, "conflicts"):
                store.sync("mira", "owner-1", [FinanceOperation("adjust-1", "adjustment", "a", 200, STAMP, STAMP)])
            self.assertEqual(store.account_deltas("mira", "owner-1"), {"a": 100})


if __name__ == "__main__":
    unittest.main()
