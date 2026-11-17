from datetime import datetime, timezone
import unittest

from jarvis_v2.finance import (
    PaperMarketMark,
    PaperPerformanceError,
    PaperPerformanceService,
    PaperSplit,
    PaperTrade,
)


OPEN = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
LATER = datetime(2026, 11, 3, 10, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class FinancePerformanceTests(unittest.TestCase):
    def test_pnl_and_drawdown_replay_is_reproducible(self):
        result = PaperPerformanceService.evaluate(
            1_000,
            [PaperTrade(OPEN, "ARCH", "buy", 2, 100)],
            [PaperMarketMark(OPEN, "ARCH", 100), PaperMarketMark(LATER, "ARCH", 90), PaperMarketMark("2026-11-04T10:00:00Z", "ARCH", 110)],
        )
        self.assertEqual((result.pnl_satang, result.max_drawdown_satang), (20, 20))
        self.assertEqual(result.equity_curve[1], (LATER, 980))
        self.assertEqual(result, PaperPerformanceService.evaluate(1_000, [PaperTrade(OPEN, "ARCH", "buy", 2, 100)], [PaperMarketMark(OPEN, "ARCH", 100), PaperMarketMark(LATER, "ARCH", 90), PaperMarketMark("2026-11-04T10:00:00Z", "ARCH", 110)]))

    def test_future_trade_is_not_used_at_an_earlier_mark(self):
        result = PaperPerformanceService.evaluate(
            1_000,
            [PaperTrade(LATER, "ARCH", "buy", 2, 100)],
            [PaperMarketMark(OPEN, "ARCH", 120), PaperMarketMark(LATER, "ARCH", 110), PaperMarketMark("2026-11-04T10:00:00Z", "ARCH", 100)],
        )
        self.assertEqual(result.equity_curve[0], (OPEN, 1_000))
        self.assertEqual(result.equity_curve[1][1], 1_020)

    def test_split_and_invalid_future_or_missing_evidence_fail_closed(self):
        result = PaperPerformanceService.evaluate(
            1_000,
            [PaperTrade(OPEN, "ARCH", "buy", 2, 100)],
            [PaperMarketMark(OPEN, "ARCH", 100), PaperMarketMark(LATER, "ARCH", 50)],
            [PaperSplit("ARCH", LATER, 2, 1)],
        )
        self.assertEqual(result.final_equity_satang, 1_000)
        with self.assertRaisesRegex(PaperPerformanceError, "chronological"):
            PaperPerformanceService.evaluate(1_000, [], [PaperMarketMark(LATER, "ARCH", 100), PaperMarketMark(OPEN, "ARCH", 100)])
        with self.assertRaisesRegex(PaperPerformanceError, "after"):
            PaperPerformanceService.evaluate(1_000, [PaperTrade(LATER, "ARCH", "buy", 1, 100)], [PaperMarketMark(OPEN, "ARCH", 100)])


if __name__ == "__main__":
    unittest.main()
