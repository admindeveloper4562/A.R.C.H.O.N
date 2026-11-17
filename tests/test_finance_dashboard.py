from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceBalance,
    FinanceDashboardError,
    FinanceStore,
    FinanceTransaction,
)


STAMP = datetime(2026, 11, 17, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinanceDashboardTests(unittest.TestCase):
    def test_estimated_balances_are_scoped_labeled_and_timestamped(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync(
                "mira", "person-1",
                accounts=[FinanceAccount("wallet", "Wallet", "THB", STAMP)],
                transactions=[FinanceTransaction("in", "wallet", 1_000, STAMP, LATER)],
            )
            dashboard = store.dashboard("mira", "person-1")
            self.assertEqual(dashboard.person_id, "person-1")
            self.assertEqual(dashboard.accounts[0].balance_satang, 1_000)
            self.assertEqual(dashboard.accounts[0].status, "estimated")
            self.assertEqual(dashboard.accounts[0].source_timestamp, LATER)
            self.assertEqual(dashboard.as_dict()["accounts"][0]["status"], "estimated")

    def test_reconciled_balance_overrides_estimate_without_leaking_scope(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            account = FinanceAccount("bank", "Bank", "THB", STAMP)
            store.sync("mira", "person-1", accounts=[account], transactions=[FinanceTransaction("tx", "bank", 10, STAMP, STAMP)])
            store.sync("mira", "person-2", accounts=[account], transactions=[FinanceTransaction("tx", "bank", 99, STAMP, STAMP)])
            result = store.dashboard(
                "mira", "person-1",
                reconciled_balances=[FinanceBalance("bank", "Bank", "THB", 7, "reconciled", LATER)],
            )
            self.assertEqual(result.accounts[0].balance_satang, 7)
            self.assertEqual(result.accounts[0].status, "reconciled")
            self.assertEqual(store.dashboard("mira", "person-2").accounts[0].balance_satang, 99)

    def test_authoritative_balance_must_match_a_known_account_and_status(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "person-1", accounts=[FinanceAccount("bank", "Bank", "THB", STAMP)])
            with self.assertRaisesRegex(FinanceDashboardError, "unknown account"):
                store.dashboard(
                    "mira", "person-1",
                    reconciled_balances=[FinanceBalance("other", "Other", "THB", 1, "reconciled", STAMP)],
                )
            with self.assertRaisesRegex(FinanceDashboardError, "must be reconciled"):
                store.dashboard(
                    "mira", "person-1",
                    reconciled_balances=[FinanceBalance("bank", "Bank", "THB", 1, "estimated", STAMP)],
                )


if __name__ == "__main__":
    unittest.main()
