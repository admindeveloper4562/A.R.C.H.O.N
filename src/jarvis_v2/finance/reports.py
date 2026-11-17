"""Scoped, deterministic finance summaries over imported transaction snapshots."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime

from .ingestion import FinanceIngestionError, FinanceStore, _date, _identifier


class FinanceReportError(FinanceIngestionError):
    """Raised when a finance report request is outside its bounded contract."""


@dataclass(frozen=True)
class FinanceReport:
    """A source-timestamped summary with deterministic sorted breakdowns."""

    source_id: str
    scope_id: str
    start_date: str | None
    end_date: str | None
    source_timestamp: str | None
    income_satang: int
    expense_satang: int
    net_satang: int
    category_expense_satang: tuple[tuple[str, int], ...]
    merchant_expense_satang: tuple[tuple[str, int], ...]
    monthly_net_satang: tuple[tuple[str, int], ...]

    @property
    def total_income_satang(self) -> int:
        return self.income_satang

    @property
    def total_expense_satang(self) -> int:
        return self.expense_satang

    @property
    def category_totals(self) -> tuple[tuple[str, int], ...]:
        return self.category_expense_satang

    @property
    def merchant_totals(self) -> tuple[tuple[str, int], ...]:
        return self.merchant_expense_satang

    @property
    def trend(self) -> tuple[tuple[str, int], ...]:
        return self.monthly_net_satang

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "person_id": self.scope_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "source_timestamp": self.source_timestamp,
            "income_satang": self.income_satang,
            "expense_satang": self.expense_satang,
            "net_satang": self.net_satang,
            "category_expense_satang": dict(self.category_expense_satang),
            "merchant_expense_satang": dict(self.merchant_expense_satang),
            "monthly_net_satang": dict(self.monthly_net_satang),
        }


class FinanceReportService:
    """Calculate reports only from one source and person scope."""

    def __init__(self, store: FinanceStore):
        if not isinstance(store, FinanceStore):
            raise FinanceReportError("report requires a FinanceStore")
        self.store = store

    def report(
        self,
        source_id: str,
        scope_id: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> FinanceReport:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        start_date = self._valid_date(start_date, "start date")
        end_date = self._valid_date(end_date, "end date")
        if start_date and end_date and date.fromisoformat(end_date) < date.fromisoformat(start_date):
            raise FinanceReportError("report period is reversed")

        transactions = self.store.transactions(source_id, scope_id)
        selected = []
        for transaction in transactions:
            day = transaction.occurred_at[:10]
            if start_date and day < start_date:
                continue
            if end_date and day > end_date:
                continue
            selected.append(transaction)

        income = 0
        expense = 0
        categories: dict[str, int] = {}
        merchants: dict[str, int] = {}
        monthly: dict[str, int] = {}
        for transaction in selected:
            amount = transaction.amount_satang
            if amount >= 0:
                income += amount
            else:
                spent = -amount
                expense += spent
                categories[transaction.category_id or "uncategorized"] = (
                    categories.get(transaction.category_id or "uncategorized", 0) + spent
                )
                merchant = transaction.description or "unattributed"
                merchants[merchant] = merchants.get(merchant, 0) + spent
            month = transaction.occurred_at[:7]
            monthly[month] = monthly.get(month, 0) + amount

        source_timestamp = None
        if selected:
            source_timestamp = max((item.updated_at for item in selected), key=self._instant)
        return FinanceReport(
            source_id, scope_id, start_date, end_date, source_timestamp,
            income, expense, income - expense,
            tuple(sorted(categories.items())), tuple(sorted(merchants.items())),
            tuple(sorted(monthly.items())),
        )

    summary = report
    snapshot = report

    @staticmethod
    def _valid_date(value: str | None, label: str) -> str | None:
        if value is None:
            return None
        try:
            return _date(value, label)
        except FinanceIngestionError as exc:
            raise FinanceReportError(str(exc)) from exc

    @staticmethod
    def _instant(value: str) -> float:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


__all__ = ["FinanceReport", "FinanceReportError", "FinanceReportService"]
