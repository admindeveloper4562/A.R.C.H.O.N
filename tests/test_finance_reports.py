from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceCategory,
    FinanceReportError,
    FinanceStore,
    FinanceTransaction,
)


STAMP = datetime(2026, 11, 1, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 5, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinanceReportTests(unittest.TestCase):
    def test_summary_totals_breakdowns_and_trend_match_fixture_ledger(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync(
                "mira", "person-1",
                accounts=[FinanceAccount("bank", "Bank", "THB", LATER)],
                categories=[FinanceCategory("food", "Food", STAMP)],
                transactions=[
                    FinanceTransaction("income", "bank", 10_000, STAMP, STAMP),
                    FinanceTransaction("food-1", "bank", -1_200, STAMP, STAMP, "food", "Cafe"),
                    FinanceTransaction("food-2", "bank", -800, LATER, LATER, "food", "Cafe"),
                ],
            )
            report = store.report("mira", "person-1")
            self.assertEqual((report.income_satang, report.expense_satang, report.net_satang), (10_000, 2_000, 8_000))
            self.assertEqual(report.category_totals, (("food", 2_000),))
            self.assertEqual(report.merchant_totals, (("Cafe", 2_000),))
            self.assertEqual(report.trend, (("2026-11", 8_000),))
            self.assertEqual(report.source_timestamp, LATER)

    def test_period_filter_and_person_scope_are_applied_before_aggregation(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            account = FinanceAccount("bank", "Bank", "THB", STAMP)
            store.sync("mira", "person-1", accounts=[account], transactions=[FinanceTransaction("old", "bank", 100, STAMP, STAMP)])
            store.sync("mira", "person-2", accounts=[account], transactions=[FinanceTransaction("other", "bank", 999, STAMP, STAMP)])
            report = store.report("mira", "person-1", start_date="2026-11-02", end_date="2026-11-30")
            self.assertEqual((report.income_satang, report.expense_satang, report.source_timestamp), (0, 0, None))
            self.assertEqual(store.report("mira", "person-2").income_satang, 999)

    def test_reversed_period_and_bad_date_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            with self.assertRaisesRegex(FinanceReportError, "reversed"):
                store.report("mira", "person-1", start_date="2026-12-01", end_date="2026-11-01")
            with self.assertRaisesRegex(FinanceReportError, "invalid"):
                store.report("mira", "person-1", start_date="not-a-date")


if __name__ == "__main__":
    unittest.main()
