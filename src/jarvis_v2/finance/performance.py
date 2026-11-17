"""Deterministic paper performance replay without future-data access."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from .ingestion import FinanceIngestionError, _identifier, _satang, _timestamp


class PaperPerformanceError(FinanceIngestionError):
    """Raised when paper performance evidence cannot be replayed safely."""


def _quantity(value: object, label: str) -> int:
    if type(value) is not int or value <= 0 or value > 10**12:
        raise PaperPerformanceError(f"invalid {label}")
    return value


@dataclass(frozen=True)
class PaperTrade:
    executed_at: str
    symbol: str
    side: str
    quantity: int
    price_satang: int
    fee_satang: int = 0

    def __post_init__(self) -> None:
        _timestamp(self.executed_at, "trade timestamp")
        _identifier(self.symbol, "trade symbol")
        if self.side not in {"buy", "sell"}:
            raise PaperPerformanceError("trade side is invalid")
        _quantity(self.quantity, "trade quantity")
        _satang(self.price_satang, "trade price", nonnegative=True)
        if self.price_satang == 0:
            raise PaperPerformanceError("trade price must be positive")
        _satang(self.fee_satang, "trade fee", nonnegative=True)

    @property
    def notional_satang(self) -> int:
        return self.quantity * self.price_satang


@dataclass(frozen=True)
class PaperMarketMark:
    observed_at: str
    symbol: str
    price_satang: int

    def __post_init__(self) -> None:
        _timestamp(self.observed_at, "market mark timestamp")
        _identifier(self.symbol, "market mark symbol")
        _satang(self.price_satang, "market mark price", nonnegative=True)
        if self.price_satang == 0:
            raise PaperPerformanceError("market mark price must be positive")


@dataclass(frozen=True)
class PaperSplit:
    symbol: str
    effective_at: str
    ratio_numerator: int
    ratio_denominator: int

    def __post_init__(self) -> None:
        _identifier(self.symbol, "split symbol")
        _timestamp(self.effective_at, "split timestamp")
        _quantity(self.ratio_numerator, "split numerator")
        _quantity(self.ratio_denominator, "split denominator")


@dataclass(frozen=True)
class PaperPerformance:
    initial_cash_satang: int
    final_equity_satang: int
    pnl_satang: int
    max_drawdown_satang: int
    equity_curve: tuple[tuple[str, int], ...]
    source_timestamp: str

    def __post_init__(self) -> None:
        _satang(self.initial_cash_satang, "initial cash", nonnegative=True)
        _satang(self.final_equity_satang, "final equity", nonnegative=True)
        _satang(self.max_drawdown_satang, "maximum drawdown", nonnegative=True)
        if not self.equity_curve:
            raise PaperPerformanceError("performance requires an equity curve")
        if any(type(value) is not int for _, value in self.equity_curve):
            raise PaperPerformanceError("equity values must be integer satang")
        _timestamp(self.source_timestamp, "performance source timestamp")

    def as_dict(self) -> dict[str, object]:
        return {
            "initial_cash_satang": self.initial_cash_satang,
            "final_equity_satang": self.final_equity_satang,
            "pnl_satang": self.pnl_satang,
            "max_drawdown_satang": self.max_drawdown_satang,
            "equity_curve": [{"observed_at": stamp, "equity_satang": value} for stamp, value in self.equity_curve],
            "source_timestamp": self.source_timestamp,
        }


class PaperPerformanceService:
    """Replay a paper ledger using only observations available at each mark."""

    @staticmethod
    def evaluate(
        initial_cash_satang: int,
        trades: Iterable[PaperTrade],
        marks: Iterable[PaperMarketMark],
        corporate_actions: Iterable[PaperSplit] = (),
    ) -> PaperPerformance:
        _satang(initial_cash_satang, "initial cash", nonnegative=True)
        trades = PaperPerformanceService._records(trades, PaperTrade, "trades")
        marks = PaperPerformanceService._records(marks, PaperMarketMark, "market marks")
        actions = PaperPerformanceService._records(corporate_actions, PaperSplit, "corporate actions")
        if not marks:
            raise PaperPerformanceError("performance requires market marks")
        PaperPerformanceService._ordered([item.executed_at for item in trades], "trades")
        PaperPerformanceService._ordered([item.observed_at for item in marks], "market marks")
        PaperPerformanceService._ordered([item.effective_at for item in actions], "corporate actions")

        cash = initial_cash_satang
        positions: dict[str, int] = {}
        latest_marks: dict[str, int] = {}
        trade_index = action_index = 0
        equity_curve: list[tuple[str, int]] = []
        for mark in marks:
            while action_index < len(actions) and PaperPerformanceService._instant(actions[action_index].effective_at) <= PaperPerformanceService._instant(mark.observed_at):
                action = actions[action_index]
                if action.symbol in positions:
                    quantity = positions[action.symbol]
                    if quantity * action.ratio_numerator % action.ratio_denominator:
                        raise PaperPerformanceError("split would create fractional paper units")
                    positions[action.symbol] = quantity * action.ratio_numerator // action.ratio_denominator
                action_index += 1
            while trade_index < len(trades) and PaperPerformanceService._instant(trades[trade_index].executed_at) <= PaperPerformanceService._instant(mark.observed_at):
                trade = trades[trade_index]
                notional = trade.notional_satang
                if trade.side == "buy":
                    cash -= notional + trade.fee_satang
                    positions[trade.symbol] = positions.get(trade.symbol, 0) + trade.quantity
                else:
                    if positions.get(trade.symbol, 0) < trade.quantity:
                        raise PaperPerformanceError("trade sells more than the replayed position")
                    cash += notional - trade.fee_satang
                    positions[trade.symbol] -= trade.quantity
                    if positions[trade.symbol] == 0:
                        del positions[trade.symbol]
                if cash < 0:
                    raise PaperPerformanceError("replayed cash became negative")
                trade_index += 1
            latest_marks[mark.symbol] = mark.price_satang
            if any(symbol not in latest_marks for symbol in positions):
                raise PaperPerformanceError("open position lacks an observation at this mark")
            equity = cash + sum(quantity * latest_marks[symbol] for symbol, quantity in positions.items())
            equity_curve.append((mark.observed_at, equity))

        if trade_index != len(trades):
            raise PaperPerformanceError("trade occurs after the final market observation")
        peak = equity_curve[0][1]
        drawdown = 0
        for _, equity in equity_curve:
            peak = max(peak, equity)
            drawdown = max(drawdown, peak - equity)
        final_equity = equity_curve[-1][1]
        return PaperPerformance(
            initial_cash_satang, final_equity, final_equity - initial_cash_satang,
            drawdown, tuple(equity_curve), equity_curve[-1][0],
        )

    @staticmethod
    def _records(values: Iterable[object], cls: type[object], label: str) -> tuple[object, ...]:
        if isinstance(values, (str, bytes)):
            raise PaperPerformanceError(f"{label} must be a collection")
        try:
            result = tuple(values)
        except TypeError as exc:
            raise PaperPerformanceError(f"{label} must be a collection") from exc
        if any(not isinstance(value, cls) for value in result):
            raise PaperPerformanceError(f"{label} contain an invalid record")
        return result

    @staticmethod
    def _ordered(values: list[str], label: str) -> None:
        if any(PaperPerformanceService._instant(previous) > PaperPerformanceService._instant(current) for previous, current in zip(values, values[1:])):
            raise PaperPerformanceError(f"{label} are not chronological")

    @staticmethod
    def _instant(value: str) -> float:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


__all__ = [
    "PaperMarketMark",
    "PaperPerformance",
    "PaperPerformanceError",
    "PaperPerformanceService",
    "PaperSplit",
    "PaperTrade",
]
