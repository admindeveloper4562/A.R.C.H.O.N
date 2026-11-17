from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceAdviceError,
    FinanceAdviceService,
    FinanceStore,
    FinanceTransaction,
)


STAMP = datetime(2026, 11, 1, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 2, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinanceAdviceTests(unittest.TestCase):
    def store(self):
        directory = tempfile.TemporaryDirectory()
        store = FinanceStore(Path(directory.name) / "finance.sqlite")
        store.sync(
            "mira", "person-1",
            accounts=[FinanceAccount("bank", "Bank", "THB", LATER)],
            transactions=[
                FinanceTransaction("cafe-1", "bank", -100, STAMP, STAMP, description="Cafe"),
                FinanceTransaction("cafe-2", "bank", -100, LATER, LATER, description="Cafe"),
            ],
        )
        return directory, store

    def test_without_consent_advice_is_bounded_and_requires_consent(self):
        directory, store = self.store()
        try:
            recommendation = store.recommendations("mira", "person-1")[0]
            self.assertEqual(recommendation.status, "consent_required")
            self.assertIn("no action is required", recommendation.message)
            self.assertNotIn("Cafe", recommendation.message)
            self.assertEqual(store.db.execute("select count(*) from finance_transactions").fetchone()[0], 2)
        finally:
            store.close()
            directory.cleanup()

    def test_explicit_consent_then_approval_makes_notification_ready(self):
        directory, store = self.store()
        try:
            recommendation = store.recommendations("mira", "person-1", consent_granted=True)[0]
            self.assertEqual(recommendation.status, "approval_required")
            approved = recommendation.approve(consent_granted=True)
            notification = FinanceAdviceService.notification(approved, consent_granted=True)
            self.assertTrue(notification.deliverable)
            self.assertEqual(notification.status, "ready")
        finally:
            store.close()
            directory.cleanup()

    def test_approval_without_consent_and_suppression_fail_closed(self):
        directory, store = self.store()
        try:
            recommendation = store.recommendations("mira", "person-1")[0]
            with self.assertRaisesRegex(FinanceAdviceError, "consent"):
                recommendation.approve(consent_granted=False)
            suppressed = recommendation.suppress()
            self.assertEqual(FinanceAdviceService.notification(suppressed, consent_granted=True).status, "suppressed")
        finally:
            store.close()
            directory.cleanup()


if __name__ == "__main__":
    unittest.main()
