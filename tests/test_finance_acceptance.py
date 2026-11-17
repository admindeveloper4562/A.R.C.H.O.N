import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jarvis_v2.backend import ConnectorAuthorizationError
from jarvis_v2.finance import (
    FinanceAccount,
    FinanceBudget,
    FinanceCategory,
    FinanceStore,
    FinanceTransaction,
)
from jarvis_v2.finance.mira_connector import MiraConnectorTokenBroker


STAMP = datetime(2026, 11, 17, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 18, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinanceAcceptanceTests(unittest.TestCase):
    def test_revocation_stops_sync_and_fixture_budget_report_remain_stable(self):
        snapshot = {
            "accounts": [FinanceAccount("checking", "Checking", "THB", STAMP)],
            "categories": [FinanceCategory("food", "Food", STAMP)],
            "budgets": [FinanceBudget("food-budget", "food", 12_500, "2026-11-01", "2026-11-30", STAMP)],
            "transactions": [
                FinanceTransaction("income", "checking", 10_000, STAMP, STAMP),
                FinanceTransaction("lunch", "checking", -1_200, STAMP, STAMP, "food", "Lunch"),
                FinanceTransaction("dinner", "checking", -800, LATER, LATER, "food", "Dinner"),
            ],
        }
        broker = MiraConnectorTokenBroker()
        token = broker.issue("archon-finance", token_id="fin-016-sync")

        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            sync = lambda: store.sync("mira", "owner-1", **snapshot)
            result = broker.run_read_sync("archon-finance", token.token_id, sync)
            self.assertEqual((result.inserted, result.updated, result.unchanged), (6, 0, 0))
            self.assertEqual(store.budgets("mira", "owner-1")[0].amount_satang, 12_500)
            report = store.report("mira", "owner-1")
            self.assertEqual((report.income_satang, report.expense_satang, report.net_satang), (10_000, 2_000, 8_000))
            self.assertEqual(report.category_totals, (("food", 2_000),))
            self.assertEqual(report.merchant_totals, (("Dinner", 800), ("Lunch", 1_200)))

            broker.revoke(token.token_id)
            with self.assertRaisesRegex(ConnectorAuthorizationError, "sync capability denied"):
                broker.run_read_sync("archon-finance", token.token_id, sync)
            self.assertEqual(len(store.transactions("mira", "owner-1")), 3)


if __name__ == "__main__":
    unittest.main()
