from datetime import datetime, timezone
import tempfile
import unittest
from pathlib import Path

from jarvis_v2.finance import (
    FinanceAccount,
    FinanceStore,
    FinanceTransaction,
    PaperAccount,
    PaperLedger,
    PaperLedgerError,
    PaperOrder,
)


STAMP = datetime(2026, 11, 1, 2, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinancePaperTests(unittest.TestCase):
    def test_paper_cash_and_positions_are_separate_from_finance_store(self):
        with tempfile.TemporaryDirectory() as directory:
            real_path = Path(directory) / "finance.sqlite"
            paper_path = Path(directory) / "paper.sqlite"
            with FinanceStore(real_path) as real:
                real.sync("mira", "person-1", accounts=[FinanceAccount("real", "Real", "THB", STAMP)], transactions=[FinanceTransaction("tx", "real", 500, STAMP, STAMP)])
                with PaperLedger(paper_path) as paper:
                    paper.open_account(PaperAccount("demo", "person-1", "THB", 1_000, STAMP))
                    paper.place_order(PaperOrder("buy-1", "demo", "ARCH", "buy", 2, 100, "pending", STAMP))
                    filled = paper.fill_order("buy-1", filled_at=STAMP)
                    self.assertEqual(filled.status, "filled")
                    self.assertEqual(paper.account("demo").cash_satang, 800)
                    self.assertEqual(paper.positions("demo")[0].quantity, 2)
                self.assertEqual(real.accounts("mira", "person-1")[0].account_id, "real")
                self.assertEqual(real.transactions("mira", "person-1")[0].amount_satang, 500)

    def test_duplicate_order_is_idempotent_and_insufficient_cash_fails(self):
        with tempfile.TemporaryDirectory() as directory, PaperLedger(Path(directory) / "paper.sqlite") as paper:
            account = PaperAccount("demo", "person-1", "THB", 100, STAMP)
            paper.open_account(account)
            order = PaperOrder("buy-1", "demo", "ARCH", "buy", 1, 100, "pending", STAMP)
            self.assertEqual(paper.place_order(order), paper.place_order(order))
            paper.fill_order("buy-1", filled_at=STAMP)
            paper.place_order(PaperOrder("buy-2", "demo", "ARCH", "buy", 1, 100, "pending", STAMP))
            with self.assertRaisesRegex(PaperLedgerError, "insufficient"):
                paper.fill_order("buy-2", filled_at=STAMP)

    def test_sell_cannot_create_a_position_or_touch_real_accounts(self):
        with tempfile.TemporaryDirectory() as directory, PaperLedger(Path(directory) / "paper.sqlite") as paper:
            paper.open_account(PaperAccount("demo", "person-1", "THB", 100, STAMP))
            paper.place_order(PaperOrder("sell-1", "demo", "ARCH", "sell", 1, 100, "pending", STAMP))
            with self.assertRaisesRegex(PaperLedgerError, "insufficient"):
                paper.fill_order("sell-1", filled_at=STAMP)


if __name__ == "__main__":
    unittest.main()
