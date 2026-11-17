from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceAlertError,
    FinanceCategory,
    FinanceStore,
    FinanceTransaction,
)


STAMP = datetime(2026, 11, 1, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 2, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinanceAlertTests(unittest.TestCase):
    def test_recurring_alert_is_explainable_source_linked_and_suppressible(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync(
                "mira", "person-1",
                accounts=[FinanceAccount("bank", "Bank", "THB", LATER)],
                categories=[FinanceCategory("food", "Food", STAMP)],
                transactions=[
                    FinanceTransaction("cafe-1", "bank", -100, STAMP, STAMP, "food", "Cafe"),
                    FinanceTransaction("cafe-2", "bank", -100, LATER, LATER, "food", "Cafe"),
                ],
            )
            alerts = store.alerts("mira", "person-1")
            recurring = next(alert for alert in alerts if alert.kind == "recurring")
            self.assertEqual(recurring.transaction_ids, ("cafe-1", "cafe-2"))
            self.assertIn("Cafe", recurring.explanation)
            self.assertEqual(recurring.source_timestamps, (STAMP, LATER))
            self.assertTrue(recurring.suppress().suppressed)
            self.assertTrue(store.alerts("mira", "person-1")[0].suppressed is False)

    def test_unusual_alert_uses_a_bounded_explainable_threshold(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync(
                "mira", "person-1",
                accounts=[FinanceAccount("bank", "Bank", "THB", LATER)],
                transactions=[
                    FinanceTransaction("small-1", "bank", -100, STAMP, STAMP, description="Meal"),
                    FinanceTransaction("small-2", "bank", -100, LATER, LATER, description="Meal"),
                    FinanceTransaction("large", "bank", -500, LATER, LATER, description="Repair"),
                ],
            )
            alerts = store.alerts("mira", "person-1")
            unusual = next(alert for alert in alerts if alert.kind == "unusual")
            self.assertEqual(unusual.transaction_ids, ("large",))
            self.assertIn("threshold", unusual.explanation)

    def test_scope_isolation_and_invalid_multiplier_are_enforced(self):
        with tempfile.TemporaryDirectory() as directory, FinanceStore(Path(directory) / "finance.sqlite") as store:
            store.sync("mira", "person-1", accounts=[FinanceAccount("bank", "Bank", "THB", STAMP)])
            store.sync("mira", "person-2", accounts=[FinanceAccount("bank", "Bank", "THB", STAMP)], transactions=[FinanceTransaction("other", "bank", -100, STAMP, STAMP)])
            self.assertEqual(store.alerts("mira", "person-1"), ())
            with self.assertRaisesRegex(FinanceAlertError, "at least two"):
                store.alerts("mira", "person-2", unusual_multiplier=1)


if __name__ == "__main__":
    unittest.main()
