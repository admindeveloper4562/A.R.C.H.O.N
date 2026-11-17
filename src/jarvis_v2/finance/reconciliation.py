"""Idempotent transfer, savings and balance-adjustment semantics."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sqlite3

from .ingestion import (
    _identifier,
    _satang,
    _text,
    _timestamp,
)


_MAX_BATCH_OPERATIONS = 1_000
_MISSING = object()


class FinanceReconciliationError(ValueError):
    """Raised when a finance operation cannot be applied safely."""


def _pick(data: Mapping[str, object], label: str, *keys: str, default: object = _MISSING) -> object:
    for key in keys:
        if key in data:
            return data[key]
    if default is not _MISSING:
        return default
    raise FinanceReconciliationError(f"missing {label}")


@dataclass(frozen=True)
class FinanceOperation:
    """One logical source operation; its effect is calculated exactly once."""

    operation_id: str
    kind: str
    account_id: str
    amount_satang: int
    occurred_at: str
    updated_at: str
    counterparty_account_id: str | None = None
    description: str = ""

    def __post_init__(self) -> None:
        _identifier(self.operation_id, "operation id")
        if self.kind not in {"transfer", "savings", "adjustment"}:
            raise FinanceReconciliationError("operation kind is not supported")
        _identifier(self.account_id, "operation account id")
        if self.counterparty_account_id is not None:
            _identifier(self.counterparty_account_id, "counterparty account id")
        if self.kind in {"transfer", "savings"}:
            if self.counterparty_account_id is None or self.counterparty_account_id == self.account_id:
                raise FinanceReconciliationError("transfer requires two distinct accounts")
            _satang(self.amount_satang, "operation amount", nonnegative=True)
            if self.amount_satang == 0:
                raise FinanceReconciliationError("transfer amount must be positive")
        else:
            if self.counterparty_account_id is not None:
                raise FinanceReconciliationError("adjustment cannot have a counterparty")
            _satang(self.amount_satang, "adjustment amount")
            if self.amount_satang == 0:
                raise FinanceReconciliationError("adjustment amount must be non-zero")
        _timestamp(self.occurred_at, "operation occurred timestamp")
        _timestamp(self.updated_at, "operation updated timestamp")
        if self.description:
            _text(self.description, "operation description")

    def as_dict(self) -> dict[str, object]:
        return {
            "operation_id": self.operation_id,
            "kind": self.kind,
            "account_id": self.account_id,
            "amount_satang": self.amount_satang,
            "occurred_at": self.occurred_at,
            "updated_at": self.updated_at,
            "counterparty_account_id": self.counterparty_account_id,
            "description": self.description,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "FinanceOperation":
        if not isinstance(data, Mapping):
            raise FinanceReconciliationError("operation record is invalid")
        counterparty = data.get("counterparty_account_id")
        return cls(
            _identifier(_pick(data, "operation id", "operation_id", "id"), "operation id"),
            _text(_pick(data, "operation kind", "kind"), "operation kind"),
            _identifier(_pick(data, "operation account id", "account_id"), "operation account id"),
            _satang(_pick(data, "operation amount", "amount_satang"), "operation amount"),
            _timestamp(_pick(data, "operation occurred timestamp", "occurred_at"), "operation occurred timestamp"),
            _timestamp(_pick(data, "operation updated timestamp", "updated_at"), "operation updated timestamp"),
            None if counterparty is None else _identifier(counterparty, "counterparty account id"),
            _text(data.get("description", ""), "operation description") if data.get("description", "") else "",
        )

    def effects(self) -> dict[str, int]:
        """Return the one accounting effect represented by this operation."""
        if self.kind in {"transfer", "savings"}:
            assert self.counterparty_account_id is not None
            return {
                self.account_id: -self.amount_satang,
                self.counterparty_account_id: self.amount_satang,
            }
        return {self.account_id: self.amount_satang}


@dataclass(frozen=True)
class FinanceReconciliationResult:
    source_id: str
    scope_id: str
    inserted: int
    updated: int
    unchanged: int
    account_deltas: tuple[tuple[str, int], ...]

    @property
    def total(self) -> int:
        return self.inserted + self.updated + self.unchanged

    @property
    def net_effect_satang(self) -> int:
        return sum(amount for _, amount in self.account_deltas)

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "scope_id": self.scope_id,
            "inserted": self.inserted,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "total": self.total,
            "account_deltas": dict(self.account_deltas),
            "net_effect_satang": self.net_effect_satang,
        }


class FinanceReconciliationStore:
    """Persist logical operations and calculate their effects once per ID."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS finance_reconciliation_operations (
                source_id TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                account_id TEXT NOT NULL,
                amount_satang INTEGER NOT NULL,
                occurred_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                counterparty_account_id TEXT,
                description TEXT NOT NULL,
                record_json TEXT NOT NULL,
                PRIMARY KEY(source_id, scope_id, operation_id)
            )"""
        )
        self.db.commit()

    def __enter__(self) -> "FinanceReconciliationStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()

    def sync(
        self,
        source_id: str,
        scope_id: str,
        operations: Iterable[FinanceOperation | Mapping[str, object]] = (),
    ) -> FinanceReconciliationResult:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        values = self._coerce(operations)
        if len(values) > _MAX_BATCH_OPERATIONS:
            raise FinanceReconciliationError("operation batch exceeds the bounded limit")
        unique: dict[str, FinanceOperation] = {}
        for operation in values:
            prior = unique.get(operation.operation_id)
            if prior is not None and prior != operation:
                raise FinanceReconciliationError("conflicting duplicate operation")
            unique[operation.operation_id] = operation

        inserted = updated = unchanged = 0
        try:
            self.db.execute("BEGIN IMMEDIATE")
            for operation in unique.values():
                payload = json.dumps(operation.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                existing = self.db.execute(
                    "SELECT record_json, updated_at FROM finance_reconciliation_operations "
                    "WHERE source_id=? AND scope_id=? AND operation_id=?",
                    (source_id, scope_id, operation.operation_id),
                ).fetchone()
                if existing is None:
                    self._insert(source_id, scope_id, operation, payload)
                    inserted += 1
                elif existing["record_json"] == payload:
                    unchanged += 1
                elif self._instant(operation.updated_at) > self._instant(existing["updated_at"]):
                    self._update(source_id, scope_id, operation, payload)
                    updated += 1
                else:
                    raise FinanceReconciliationError("operation conflicts with stored source revision")
            self.db.commit()
        except (sqlite3.Error, FinanceReconciliationError) as exc:
            self.db.rollback()
            if isinstance(exc, FinanceReconciliationError):
                raise
            raise FinanceReconciliationError("reconciliation persistence failed") from exc
        deltas = self.account_deltas(source_id, scope_id)
        return FinanceReconciliationResult(source_id, scope_id, inserted, updated, unchanged, tuple(deltas.items()))

    ingest = sync

    def operations(self, source_id: str, scope_id: str) -> tuple[FinanceOperation, ...]:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        rows = self.db.execute(
            "SELECT record_json FROM finance_reconciliation_operations "
            "WHERE source_id=? AND scope_id=? ORDER BY operation_id",
            (source_id, scope_id),
        ).fetchall()
        result = []
        for row in rows:
            try:
                result.append(FinanceOperation.from_mapping(json.loads(row["record_json"])))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise FinanceReconciliationError("stored operation is invalid") from exc
        return tuple(result)

    def account_deltas(self, source_id: str, scope_id: str) -> dict[str, int]:
        deltas: dict[str, int] = {}
        for operation in self.operations(source_id, scope_id):
            for account_id, amount in operation.effects().items():
                deltas[account_id] = deltas.get(account_id, 0) + amount
        return dict(sorted(deltas.items()))

    def reconcile(
        self, source_id: str, scope_id: str, opening_balances: Mapping[str, int],
    ) -> dict[str, int]:
        if not isinstance(opening_balances, Mapping):
            raise FinanceReconciliationError("opening balances must be a mapping")
        result = {}
        for account_id, balance in opening_balances.items():
            _identifier(account_id, "opening account id")
            _satang(balance, "opening balance")
            result[account_id] = balance
        for account_id, delta in self.account_deltas(source_id, scope_id).items():
            result[account_id] = result.get(account_id, 0) + delta
        return dict(sorted(result.items()))

    @staticmethod
    def _coerce(values: Iterable[FinanceOperation | Mapping[str, object]]) -> tuple[FinanceOperation, ...]:
        if isinstance(values, (str, bytes, Mapping)):
            raise FinanceReconciliationError("operations must be a collection")
        try:
            items = tuple(values)
        except TypeError as exc:
            raise FinanceReconciliationError("operations must be a collection") from exc
        result = []
        for item in items:
            if isinstance(item, FinanceOperation):
                result.append(item)
            elif isinstance(item, Mapping):
                result.append(FinanceOperation.from_mapping(item))
            else:
                raise FinanceReconciliationError("operation record is invalid")
        return tuple(result)

    def _insert(self, source_id: str, scope_id: str, operation: FinanceOperation, payload: str) -> None:
        self.db.execute(
            """INSERT INTO finance_reconciliation_operations
               (source_id,scope_id,operation_id,kind,account_id,amount_satang,
                occurred_at,updated_at,counterparty_account_id,description,record_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                source_id, scope_id, operation.operation_id, operation.kind, operation.account_id,
                operation.amount_satang, operation.occurred_at, operation.updated_at,
                operation.counterparty_account_id, operation.description, payload,
            ),
        )

    def _update(self, source_id: str, scope_id: str, operation: FinanceOperation, payload: str) -> None:
        self.db.execute(
            """UPDATE finance_reconciliation_operations SET kind=?,account_id=?,amount_satang=?,
               occurred_at=?,updated_at=?,counterparty_account_id=?,description=?,record_json=?
               WHERE source_id=? AND scope_id=? AND operation_id=?""",
            (
                operation.kind, operation.account_id, operation.amount_satang, operation.occurred_at,
                operation.updated_at, operation.counterparty_account_id, operation.description, payload,
                source_id, scope_id, operation.operation_id,
            ),
        )

    @staticmethod
    def _instant(value: str) -> float:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


TransferOperation = FinanceOperation
ReconciliationStore = FinanceReconciliationStore

__all__ = [
    "FinanceOperation",
    "FinanceReconciliationError",
    "FinanceReconciliationResult",
    "FinanceReconciliationStore",
    "ReconciliationStore",
    "TransferOperation",
]
