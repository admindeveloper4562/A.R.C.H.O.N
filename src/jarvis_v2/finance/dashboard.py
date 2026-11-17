"""Scoped finance balance projections with explicit certainty labels."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime

from .ingestion import (
    FinanceAccount,
    FinanceIngestionError,
    FinanceStore,
    _currency,
    _identifier,
    _satang,
    _text,
    _timestamp,
)


_MAX_DASHBOARD_ACCOUNTS = 1_000


class FinanceDashboardError(FinanceIngestionError):
    """Raised when a dashboard projection cannot be built safely."""


@dataclass(frozen=True)
class FinanceBalance:
    """One account balance with its certainty and source observation time."""

    account_id: str
    name: str
    currency: str
    balance_satang: int
    status: str
    source_timestamp: str

    def __post_init__(self) -> None:
        _identifier(self.account_id, "balance account id")
        _text(self.name, "balance account name")
        _currency(self.currency)
        _satang(self.balance_satang, "balance amount")
        if self.status not in {"reconciled", "estimated"}:
            raise FinanceDashboardError("balance status must be reconciled or estimated")
        _timestamp(self.source_timestamp, "balance source timestamp")

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "FinanceBalance":
        if not isinstance(data, Mapping):
            raise FinanceDashboardError("balance record is invalid")
        try:
            return cls(
                _identifier(data["account_id"], "balance account id"),
                _text(data.get("name", "Account"), "balance account name"),
                _currency(data.get("currency", "THB")),
                _satang(data["balance_satang"], "balance amount"),
                _text(data.get("status", "reconciled"), "balance status"),
                _timestamp(data["source_timestamp"], "balance source timestamp"),
            )
        except KeyError as exc:
            raise FinanceDashboardError(f"missing balance {exc.args[0]}") from exc

    def as_dict(self) -> dict[str, object]:
        return {
            "account_id": self.account_id,
            "name": self.name,
            "currency": self.currency,
            "balance_satang": self.balance_satang,
            "status": self.status,
            "source_timestamp": self.source_timestamp,
        }


@dataclass(frozen=True)
class FinanceDashboard:
    """A bounded, person-scoped finance dashboard snapshot."""

    source_id: str
    scope_id: str
    accounts: tuple[FinanceBalance, ...]

    def __post_init__(self) -> None:
        _identifier(self.source_id, "source id")
        _identifier(self.scope_id, "scope id")
        if not isinstance(self.accounts, tuple) or len(self.accounts) > _MAX_DASHBOARD_ACCOUNTS:
            raise FinanceDashboardError("dashboard account count is outside the bounded range")
        if any(not isinstance(account, FinanceBalance) for account in self.accounts):
            raise FinanceDashboardError("dashboard contains an invalid balance")
        ids = [account.account_id for account in self.accounts]
        if len(ids) != len(set(ids)):
            raise FinanceDashboardError("dashboard contains duplicate accounts")

    @property
    def person_id(self) -> str:
        return self.scope_id

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "person_id": self.scope_id,
            "accounts": [account.as_dict() for account in self.accounts],
        }


class FinanceDashboardService:
    """Build a read-only projection from one scoped FinanceStore snapshot."""

    def __init__(self, store: FinanceStore):
        if not isinstance(store, FinanceStore):
            raise FinanceDashboardError("dashboard requires a FinanceStore")
        self.store = store

    def snapshot(
        self,
        source_id: str,
        scope_id: str,
        *,
        reconciled_balances: Iterable[FinanceBalance | Mapping[str, object]] = (),
    ) -> FinanceDashboard:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        accounts = self.store.accounts(source_id, scope_id)
        known = {account.account_id: account for account in accounts}
        authoritative = self._coerce_reconciled(reconciled_balances)
        unknown = set(authoritative) - set(known)
        if unknown:
            raise FinanceDashboardError("reconciled balance references an unknown account")
        transactions = self.store.transactions(source_id, scope_id)
        amounts: dict[str, int] = {}
        timestamps: dict[str, list[str]] = {}
        for transaction in transactions:
            if transaction.account_id not in known:
                continue
            amounts[transaction.account_id] = amounts.get(transaction.account_id, 0) + transaction.amount_satang
            timestamps.setdefault(transaction.account_id, []).append(transaction.updated_at)

        balances = []
        for account in accounts:
            supplied = authoritative.get(account.account_id)
            if supplied is not None:
                balances.append(FinanceBalance(
                    account.account_id, account.name, account.currency,
                    supplied.balance_satang, "reconciled", supplied.source_timestamp,
                ))
                continue
            observed = [account.updated_at, *timestamps.get(account.account_id, ())]
            source_timestamp = max(observed, key=self._instant)
            balances.append(FinanceBalance(
                account.account_id, account.name, account.currency,
                amounts.get(account.account_id, 0), "estimated", source_timestamp,
            ))
        return FinanceDashboard(source_id, scope_id, tuple(balances))

    current = snapshot

    @staticmethod
    def _coerce_reconciled(
        values: Iterable[FinanceBalance | Mapping[str, object]],
    ) -> dict[str, FinanceBalance]:
        if isinstance(values, (str, bytes, Mapping)):
            raise FinanceDashboardError("reconciled balances must be a collection")
        try:
            items = tuple(values)
        except TypeError as exc:
            raise FinanceDashboardError("reconciled balances must be a collection") from exc
        result: dict[str, FinanceBalance] = {}
        for item in items:
            balance = item if isinstance(item, FinanceBalance) else FinanceBalance.from_mapping(item)
            if balance.status != "reconciled":
                raise FinanceDashboardError("authoritative balance must be reconciled")
            if balance.account_id in result and result[balance.account_id] != balance:
                raise FinanceDashboardError("conflicting reconciled balance")
            result[balance.account_id] = balance
        return result

    @staticmethod
    def _instant(value: str) -> float:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


__all__ = [
    "FinanceBalance",
    "FinanceDashboard",
    "FinanceDashboardError",
    "FinanceDashboardService",
]
