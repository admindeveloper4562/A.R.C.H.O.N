"""Explainable, source-linked finance alerts with immutable suppression."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
import hashlib

from .ingestion import FinanceIngestionError, FinanceStore, FinanceTransaction, _identifier, _satang, _text, _timestamp


class FinanceAlertError(FinanceIngestionError):
    """Raised when an alert cannot be represented safely."""


@dataclass(frozen=True)
class FinanceAlert:
    """One bounded alert that points back to its source transactions."""

    alert_id: str
    source_id: str
    scope_id: str
    kind: str
    transaction_ids: tuple[str, ...]
    amount_satang: int
    explanation: str
    source_timestamps: tuple[str, ...]
    suppressed: bool = False

    def __post_init__(self) -> None:
        _identifier(self.alert_id, "alert id")
        _identifier(self.source_id, "source id")
        _identifier(self.scope_id, "scope id")
        if self.kind not in {"recurring", "unusual"}:
            raise FinanceAlertError("alert kind is not supported")
        if not self.transaction_ids or len(self.transaction_ids) != len(set(self.transaction_ids)):
            raise FinanceAlertError("alert source transactions are invalid")
        for transaction_id in self.transaction_ids:
            _identifier(transaction_id, "alert transaction id")
        _satang(self.amount_satang, "alert amount", nonnegative=True)
        if self.amount_satang == 0:
            raise FinanceAlertError("alert amount must be positive")
        _text(self.explanation, "alert explanation")
        if len(self.source_timestamps) != len(self.transaction_ids):
            raise FinanceAlertError("alert source timestamps do not match transactions")
        for timestamp in self.source_timestamps:
            _timestamp(timestamp, "alert source timestamp")
        if type(self.suppressed) is not bool:
            raise FinanceAlertError("alert suppression state is invalid")

    def suppress(self) -> "FinanceAlert":
        return replace(self, suppressed=True)

    def as_dict(self) -> dict[str, object]:
        return {
            "alert_id": self.alert_id,
            "source_id": self.source_id,
            "person_id": self.scope_id,
            "kind": self.kind,
            "transaction_ids": list(self.transaction_ids),
            "amount_satang": self.amount_satang,
            "explanation": self.explanation,
            "source_timestamps": list(self.source_timestamps),
            "suppressed": self.suppressed,
        }


class FinanceAlertService:
    """Detect repeat/unusual expenses without mutating the source ledger."""

    def __init__(self, store: FinanceStore):
        if not isinstance(store, FinanceStore):
            raise FinanceAlertError("alerts require a FinanceStore")
        self.store = store

    def detect(self, source_id: str, scope_id: str, *, unusual_multiplier: int = 2) -> tuple[FinanceAlert, ...]:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        if type(unusual_multiplier) is not int or unusual_multiplier < 2:
            raise FinanceAlertError("unusual multiplier must be an integer of at least two")
        transactions = tuple(
            transaction for transaction in self.store.transactions(source_id, scope_id)
            if transaction.amount_satang < 0
        )
        alerts = list(self._recurring(source_id, scope_id, transactions))
        if transactions:
            typical = sum(-item.amount_satang for item in transactions) // len(transactions)
            threshold = typical * unusual_multiplier
            for transaction in transactions:
                amount = -transaction.amount_satang
                if amount >= threshold and threshold > 0:
                    alerts.append(self._unusual(source_id, scope_id, transaction, typical, threshold))
        return tuple(sorted(alerts, key=lambda alert: alert.alert_id))

    @staticmethod
    def suppress(alerts: tuple[FinanceAlert, ...], alert_id: str) -> tuple[FinanceAlert, ...]:
        _identifier(alert_id, "alert id")
        if not isinstance(alerts, tuple) or any(not isinstance(alert, FinanceAlert) for alert in alerts):
            raise FinanceAlertError("alerts must be a tuple of FinanceAlert records")
        if not any(alert.alert_id == alert_id for alert in alerts):
            raise FinanceAlertError("alert was not found")
        return tuple(alert.suppress() if alert.alert_id == alert_id else alert for alert in alerts)

    @staticmethod
    def _recurring(source_id: str, scope_id: str, transactions: tuple[FinanceTransaction, ...]) -> tuple[FinanceAlert, ...]:
        groups: dict[tuple[str, int, str | None], list[FinanceTransaction]] = defaultdict(list)
        for transaction in transactions:
            groups[(transaction.description or "unattributed", -transaction.amount_satang, transaction.category_id)].append(transaction)
        result = []
        for (merchant, amount, _category), values in groups.items():
            if len(values) < 2:
                continue
            values = sorted(values, key=lambda item: item.transaction_id)
            ids = tuple(item.transaction_id for item in values)
            result.append(FinanceAlert(
                FinanceAlertService._id("recurring", source_id, scope_id, ids), source_id, scope_id,
                "recurring", ids, amount,
                f"Recurring expense: {merchant} charged {amount} satang in {len(values)} source transactions.",
                tuple(item.updated_at for item in values),
            ))
        return tuple(result)

    @staticmethod
    def _unusual(source_id: str, scope_id: str, transaction: FinanceTransaction, typical: int, threshold: int) -> FinanceAlert:
        return FinanceAlert(
            FinanceAlertService._id("unusual", source_id, scope_id, (transaction.transaction_id,)),
            source_id, scope_id, "unusual", (transaction.transaction_id,), -transaction.amount_satang,
            f"Unusual expense: {transaction.description or 'unattributed'} is {(-transaction.amount_satang)} satang; threshold is {threshold} satang from a {typical} satang average.",
            (transaction.updated_at,),
        )

    @staticmethod
    def _id(kind: str, source_id: str, scope_id: str, transaction_ids: tuple[str, ...]) -> str:
        digest = hashlib.sha256("|".join((kind, source_id, scope_id, *transaction_ids)).encode()).hexdigest()[:20]
        return f"{kind}-{digest}"


__all__ = ["FinanceAlert", "FinanceAlertError", "FinanceAlertService"]
