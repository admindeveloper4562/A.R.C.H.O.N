"""Advisory finance forecasts and non-debit savings goal progress."""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .ingestion import FinanceIngestionError, FinanceStore, _identifier, _satang, _text, _timestamp
from .reports import FinanceReportService


class FinancePlanningError(FinanceIngestionError):
    """Raised when a planning input cannot be safely represented."""


@dataclass(frozen=True)
class FinanceGoal:
    """Progress metadata; it is never written as a ledger transaction."""

    goal_id: str
    name: str
    target_satang: int
    contributed_satang: int
    updated_at: str

    def __post_init__(self) -> None:
        _identifier(self.goal_id, "goal id")
        _text(self.name, "goal name")
        _satang(self.target_satang, "goal target", nonnegative=True)
        if self.target_satang == 0:
            raise FinancePlanningError("goal target must be positive")
        _satang(self.contributed_satang, "goal contribution", nonnegative=True)
        _timestamp(self.updated_at, "goal updated timestamp")

    @property
    def remaining_satang(self) -> int:
        return max(self.target_satang - self.contributed_satang, 0)

    def as_dict(self) -> dict[str, object]:
        return {
            "goal_id": self.goal_id,
            "name": self.name,
            "target_satang": self.target_satang,
            "contributed_satang": self.contributed_satang,
            "remaining_satang": self.remaining_satang,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True)
class FinanceForecast:
    """A historical average explicitly marked as uncertain advice."""

    source_id: str
    scope_id: str
    average_monthly_net_satang: int
    certainty: str
    source_timestamp: str | None
    observed_months: int

    def __post_init__(self) -> None:
        _identifier(self.source_id, "source id")
        _identifier(self.scope_id, "scope id")
        _satang(self.average_monthly_net_satang, "forecast amount")
        if self.certainty != "uncertain":
            raise FinancePlanningError("forecasts must be labeled uncertain")
        if self.source_timestamp is not None:
            _timestamp(self.source_timestamp, "forecast source timestamp")
        if type(self.observed_months) is not int or self.observed_months < 0:
            raise FinancePlanningError("forecast month count is invalid")

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "person_id": self.scope_id,
            "average_monthly_net_satang": self.average_monthly_net_satang,
            "certainty": self.certainty,
            "source_timestamp": self.source_timestamp,
            "observed_months": self.observed_months,
        }


class FinancePlanningService:
    """Read-only forecasts and goal progress over a FinanceStore."""

    def __init__(self, store: FinanceStore):
        if not isinstance(store, FinanceStore):
            raise FinancePlanningError("planning requires a FinanceStore")
        self.store = store
        self.reports = FinanceReportService(store)

    def forecast(self, source_id: str, scope_id: str) -> FinanceForecast:
        report = self.reports.report(source_id, scope_id)
        months = len(report.monthly_net_satang)
        total = report.net_satang
        average = 0 if not months else (abs(total) // months) * (-1 if total < 0 else 1)
        return FinanceForecast(
            report.source_id, report.scope_id, average, "uncertain",
            report.source_timestamp, months,
        )

    @staticmethod
    def goal_progress(goals: Iterable[FinanceGoal]) -> tuple[FinanceGoal, ...]:
        if isinstance(goals, (str, bytes)):
            raise FinancePlanningError("goals must be a collection")
        try:
            values = tuple(goals)
        except TypeError as exc:
            raise FinancePlanningError("goals must be a collection") from exc
        if any(not isinstance(goal, FinanceGoal) for goal in values):
            raise FinancePlanningError("goals contain an invalid record")
        by_id = {goal.goal_id: goal for goal in values}
        if len(by_id) != len(values):
            raise FinancePlanningError("goals contain duplicate IDs")
        return tuple(by_id[key] for key in sorted(by_id))


__all__ = ["FinanceForecast", "FinanceGoal", "FinancePlanningError", "FinancePlanningService"]
