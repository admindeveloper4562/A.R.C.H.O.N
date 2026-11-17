from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceGoal,
    FinancePlanningError,
    FinancePlanningService,
    FinanceStore,
    FinanceTransaction,
)


STAMP = datetime(2026, 11, 1, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 12, 1, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinancePlanningTests(unittest.TestCase):
    def test_forecast_is_uncertain_and_uses_historical_net(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync(
                "mira", "person-1",
                accounts=[FinanceAccount("bank", "Bank", "THB", LATER)],
                transactions=[
                    FinanceTransaction("income", "bank", 10_000, STAMP, STAMP),
                    FinanceTransaction("expense", "bank", -2_000, LATER, LATER),
                ],
            )
            forecast = store.forecast("mira", "person-1")
            self.assertEqual(forecast.average_monthly_net_satang, 4_000)
            self.assertEqual((forecast.certainty, forecast.observed_months), ("uncertain", 2))
            self.assertEqual(forecast.source_timestamp, LATER)

    def test_goal_progress_does_not_double_debit_transaction_totals(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync(
                "mira", "person-1",
                accounts=[FinanceAccount("bank", "Bank", "THB", STAMP)],
                transactions=[FinanceTransaction("expense", "bank", -1_000, STAMP, STAMP)],
            )
            goals = FinancePlanningService.goal_progress([
                FinanceGoal("home", "Home", 10_000, 2_000, STAMP),
            ])
            self.assertEqual(goals[0].remaining_satang, 8_000)
            self.assertEqual(store.report("mira", "person-1").expense_satang, 1_000)

    def test_invalid_goal_and_duplicate_goal_fail_closed(self):
        with self.assertRaisesRegex(FinancePlanningError, "positive"):
            FinanceGoal("home", "Home", 0, 0, STAMP)
        goal = FinanceGoal("home", "Home", 10, 0, STAMP)
        with self.assertRaisesRegex(FinancePlanningError, "duplicate"):
            FinancePlanningService.goal_progress([goal, goal])


if __name__ == "__main__":
    unittest.main()
