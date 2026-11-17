"""Scoped, idempotent ingestion of read-only finance snapshots.

The store is ARCHON-owned staging state.  It never connects to Mira and never
writes to an external finance source.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, ClassVar, TypeVar


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")
_MAX_SATANG = 10**15
_MAX_BATCH_RECORDS = 1_000
_MAX_TEXT_BYTES = 512
_MISSING = object()


class FinanceIngestionError(ValueError):
    """Raised when a finance snapshot cannot be safely admitted."""


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise FinanceIngestionError(f"invalid {label}")
    return value


def _text(value: object, label: str, maximum: int = _MAX_TEXT_BYTES) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value.encode("utf-8")) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise FinanceIngestionError(f"invalid {label}")
    return value


def _currency(value: object) -> str:
    if not isinstance(value, str) or not _CURRENCY.fullmatch(value):
        raise FinanceIngestionError("invalid currency")
    return value


def _timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) > 64 or any(ord(char) < 32 for char in value):
        raise FinanceIngestionError(f"invalid {label}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FinanceIngestionError(f"invalid {label}") from exc
    if parsed.tzinfo is None:
        raise FinanceIngestionError(f"{label} must include timezone")
    return value


def _date(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise FinanceIngestionError(f"invalid {label}")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise FinanceIngestionError(f"invalid {label}") from exc
    return value


def _satang(value: object, label: str, *, nonnegative: bool = False) -> int:
    if type(value) is not int or abs(value) > _MAX_SATANG:
        raise FinanceIngestionError(f"invalid {label}; use integer satang")
    if nonnegative and value < 0:
        raise FinanceIngestionError(f"invalid {label}; must be non-negative")
    return value


def _pick(data: Mapping[str, object], label: str, *keys: str, default: object = _MISSING) -> object:
    for key in keys:
        if key in data:
            return data[key]
    if default is not _MISSING:
        return default
    raise FinanceIngestionError(f"missing {label}")


@dataclass(frozen=True)
class FinanceAccount:
    """One source account identified by its original source ID."""

    account_id: str
    name: str
    currency: str
    updated_at: str

    def __post_init__(self) -> None:
        _identifier(self.account_id, "account id")
        _text(self.name, "account name")
        _currency(self.currency)
        _timestamp(self.updated_at, "account updated timestamp")

    def as_dict(self) -> dict[str, object]:
        return {
            "account_id": self.account_id,
            "name": self.name,
            "currency": self.currency,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "FinanceAccount":
        if not isinstance(data, Mapping):
            raise FinanceIngestionError("account record is invalid")
        return cls(
            _identifier(_pick(data, "account id", "account_id", "id"), "account id"),
            _text(_pick(data, "account name", "name"), "account name"),
            _currency(_pick(data, "currency", "currency", "currency_code")),
            _timestamp(_pick(data, "account updated timestamp", "updated_at"), "account updated timestamp"),
        )


@dataclass(frozen=True)
class FinanceCategory:
    """One source category identified by its original source ID."""

    category_id: str
    name: str
    updated_at: str

    def __post_init__(self) -> None:
        _identifier(self.category_id, "category id")
        _text(self.name, "category name")
        _timestamp(self.updated_at, "category updated timestamp")

    def as_dict(self) -> dict[str, object]:
        return {
            "category_id": self.category_id,
            "name": self.name,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "FinanceCategory":
        if not isinstance(data, Mapping):
            raise FinanceIngestionError("category record is invalid")
        return cls(
            _identifier(_pick(data, "category id", "category_id", "id"), "category id"),
            _text(_pick(data, "category name", "name"), "category name"),
            _timestamp(_pick(data, "category updated timestamp", "updated_at"), "category updated timestamp"),
        )


@dataclass(frozen=True)
class FinanceBudget:
    """A source budget amount with an inclusive, date-only period."""

    budget_id: str
    category_id: str | None
    amount_satang: int
    period_start: str
    period_end: str
    updated_at: str
    currency: str = "THB"

    def __post_init__(self) -> None:
        _identifier(self.budget_id, "budget id")
        if self.category_id is not None:
            _identifier(self.category_id, "budget category id")
        _satang(self.amount_satang, "budget amount", nonnegative=True)
        start = _date(self.period_start, "budget period start")
        end = _date(self.period_end, "budget period end")
        if date.fromisoformat(end) < date.fromisoformat(start):
            raise FinanceIngestionError("budget period is reversed")
        _timestamp(self.updated_at, "budget updated timestamp")
        _currency(self.currency)

    def as_dict(self) -> dict[str, object]:
        return {
            "budget_id": self.budget_id,
            "category_id": self.category_id,
            "amount_satang": self.amount_satang,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "updated_at": self.updated_at,
            "currency": self.currency,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "FinanceBudget":
        if not isinstance(data, Mapping):
            raise FinanceIngestionError("budget record is invalid")
        return cls(
            _identifier(_pick(data, "budget id", "budget_id", "id"), "budget id"),
            None if (value := data.get("category_id")) is None else _identifier(value, "budget category id"),
            _satang(_pick(data, "budget amount", "amount_satang"), "budget amount", nonnegative=True),
            _date(_pick(data, "budget period start", "period_start"), "budget period start"),
            _date(_pick(data, "budget period end", "period_end"), "budget period end"),
            _timestamp(_pick(data, "budget updated timestamp", "updated_at"), "budget updated timestamp"),
            _currency(data.get("currency", "THB")),
        )


@dataclass(frozen=True)
class FinanceTransaction:
    """A source transaction; amount and timestamps remain exact and opaque."""

    transaction_id: str
    account_id: str
    amount_satang: int
    occurred_at: str
    updated_at: str
    category_id: str | None = None
    description: str = ""
    currency: str = "THB"

    def __post_init__(self) -> None:
        _identifier(self.transaction_id, "transaction id")
        _identifier(self.account_id, "transaction account id")
        _satang(self.amount_satang, "transaction amount")
        _timestamp(self.occurred_at, "transaction occurred timestamp")
        _timestamp(self.updated_at, "transaction updated timestamp")
        if self.category_id is not None:
            _identifier(self.category_id, "transaction category id")
        if self.description:
            _text(self.description, "transaction description")
        _currency(self.currency)

    def as_dict(self) -> dict[str, object]:
        return {
            "transaction_id": self.transaction_id,
            "account_id": self.account_id,
            "amount_satang": self.amount_satang,
            "occurred_at": self.occurred_at,
            "updated_at": self.updated_at,
            "category_id": self.category_id,
            "description": self.description,
            "currency": self.currency,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, object]) -> "FinanceTransaction":
        if not isinstance(data, Mapping):
            raise FinanceIngestionError("transaction record is invalid")
        return cls(
            _identifier(_pick(data, "transaction id", "transaction_id", "id"), "transaction id"),
            _identifier(_pick(data, "transaction account id", "account_id"), "transaction account id"),
            _satang(_pick(data, "transaction amount", "amount_satang"), "transaction amount"),
            _timestamp(_pick(data, "transaction occurred timestamp", "occurred_at"), "transaction occurred timestamp"),
            _timestamp(_pick(data, "transaction updated timestamp", "updated_at"), "transaction updated timestamp"),
            None if (value := data.get("category_id")) is None else _identifier(value, "transaction category id"),
            _text(data.get("description", ""), "transaction description") if data.get("description", "") else "",
            _currency(data.get("currency", "THB")),
        )


@dataclass(frozen=True)
class FinanceSyncResult:
    source_id: str
    scope_id: str
    inserted: int
    updated: int
    unchanged: int

    @property
    def total(self) -> int:
        return self.inserted + self.updated + self.unchanged

    def as_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "scope_id": self.scope_id,
            "inserted": self.inserted,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "total": self.total,
        }


Record = TypeVar("Record", FinanceAccount, FinanceCategory, FinanceBudget, FinanceTransaction)


class FinanceStore:
    """Persist one scoped, read-only-source snapshot without duplicate rows."""

    _TABLES: ClassVar[dict[type[object], tuple[str, str, tuple[str, ...]]]] = {
        FinanceAccount: ("finance_accounts", "account_id", ("account_id", "name", "currency", "updated_at")),
        FinanceCategory: ("finance_categories", "category_id", ("category_id", "name", "updated_at")),
        FinanceBudget: (
            "finance_budgets", "budget_id",
            ("budget_id", "category_id", "amount_satang", "period_start", "period_end", "updated_at", "currency"),
        ),
        FinanceTransaction: (
            "finance_transactions", "transaction_id",
            ("transaction_id", "account_id", "amount_satang", "occurred_at", "updated_at", "category_id", "description", "currency"),
        ),
    }

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self._create_tables()

    def _create_tables(self) -> None:
        for table, columns in (
            ("finance_accounts", "account_id TEXT NOT NULL, name TEXT NOT NULL, currency TEXT NOT NULL, updated_at TEXT NOT NULL"),
            ("finance_categories", "category_id TEXT NOT NULL, name TEXT NOT NULL, updated_at TEXT NOT NULL"),
            ("finance_budgets", "budget_id TEXT NOT NULL, category_id TEXT, amount_satang INTEGER NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL, updated_at TEXT NOT NULL, currency TEXT NOT NULL"),
            ("finance_transactions", "transaction_id TEXT NOT NULL, account_id TEXT NOT NULL, amount_satang INTEGER NOT NULL, occurred_at TEXT NOT NULL, updated_at TEXT NOT NULL, category_id TEXT, description TEXT NOT NULL, currency TEXT NOT NULL"),
        ):
            self.db.execute(
                f"CREATE TABLE IF NOT EXISTS {table} (source_id TEXT NOT NULL, scope_id TEXT NOT NULL, {columns}, record_json TEXT NOT NULL, PRIMARY KEY(source_id, scope_id, {columns.split(' TEXT', 1)[0]}))"
            )
        self.db.commit()

    def __enter__(self) -> "FinanceStore":
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
        *,
        accounts: Iterable[FinanceAccount | Mapping[str, object]] = (),
        categories: Iterable[FinanceCategory | Mapping[str, object]] = (),
        budgets: Iterable[FinanceBudget | Mapping[str, object]] = (),
        transactions: Iterable[FinanceTransaction | Mapping[str, object]] = (),
    ) -> FinanceSyncResult:
        source_id = _identifier(source_id, "source id")
        scope_id = _identifier(scope_id, "scope id")
        groups = (
            self._coerce(accounts, FinanceAccount, "accounts"),
            self._coerce(categories, FinanceCategory, "categories"),
            self._coerce(budgets, FinanceBudget, "budgets"),
            self._coerce(transactions, FinanceTransaction, "transactions"),
        )
        records = [(record, *self._TABLES[type(record)]) for group in groups for record in group]
        if len(records) > _MAX_BATCH_RECORDS:
            raise FinanceIngestionError("snapshot exceeds the bounded record limit")
        unique: dict[tuple[str, str], tuple[object, str, str, tuple[str, ...]]] = {}
        for record, table, identity, columns in records:
            payload = json.dumps(record.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            key = (table, getattr(record, identity))
            prior = unique.get(key)
            if prior is not None and prior[0] != record:
                raise FinanceIngestionError("conflicting duplicate in snapshot")
            unique[key] = (record, table, identity, columns)

        inserted = updated = unchanged = 0
        try:
            self.db.execute("BEGIN IMMEDIATE")
            for record, table, identity, columns in unique.values():
                record_id = getattr(record, identity)
                payload = json.dumps(record.as_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                existing = self.db.execute(
                    f"SELECT record_json, updated_at FROM {table} WHERE source_id=? AND scope_id=? AND {identity}=?",
                    (source_id, scope_id, record_id),
                ).fetchone()
                if existing is None:
                    self._insert(source_id, scope_id, table, columns, record, payload)
                    inserted += 1
                elif existing["record_json"] == payload:
                    unchanged += 1
                elif self._instant(record.updated_at) > self._instant(existing["updated_at"]):
                    self._update(source_id, scope_id, table, identity, columns, record, payload)
                    updated += 1
                else:
                    raise FinanceIngestionError("record conflicts with stored source revision")
            self.db.commit()
        except (sqlite3.Error, FinanceIngestionError) as exc:
            self.db.rollback()
            if isinstance(exc, FinanceIngestionError):
                raise
            raise FinanceIngestionError("finance snapshot persistence failed") from exc
        return FinanceSyncResult(source_id, scope_id, inserted, updated, unchanged)

    ingest = sync

    def _insert(self, source_id: str, scope_id: str, table: str, columns: tuple[str, ...], record: object, payload: str) -> None:
        names = ("source_id", "scope_id", *columns, "record_json")
        values = (source_id, scope_id, *(getattr(record, name) for name in columns), payload)
        placeholders = ",".join("?" for _ in names)
        self.db.execute(f"INSERT INTO {table} ({','.join(names)}) VALUES ({placeholders})", values)

    def _update(self, source_id: str, scope_id: str, table: str, identity: str, columns: tuple[str, ...], record: object, payload: str) -> None:
        mutable = tuple(name for name in columns if name != identity)
        assignments = ",".join((*[f"{name}=?" for name in mutable], "record_json=?"))
        values = (*(getattr(record, name) for name in mutable), payload, source_id, scope_id, getattr(record, identity))
        self.db.execute(f"UPDATE {table} SET {assignments} WHERE source_id=? AND scope_id=? AND {identity}=?", values)

    @staticmethod
    def _coerce(values: Iterable[Record | Mapping[str, object]], cls: type[Record], label: str) -> tuple[Record, ...]:
        if isinstance(values, (str, bytes, Mapping)):
            raise FinanceIngestionError(f"{label} must be a collection")
        try:
            items = tuple(values)
        except TypeError as exc:
            raise FinanceIngestionError(f"{label} must be a collection") from exc
        if any(isinstance(item, (str, bytes)) for item in items):
            raise FinanceIngestionError(f"{label} contains an invalid record")
        result: list[Record] = []
        for item in items:
            if isinstance(item, cls):
                result.append(item)
            elif isinstance(item, Mapping):
                result.append(cls.from_mapping(item))
            else:
                raise FinanceIngestionError(f"{label} contains an invalid record")
        return tuple(result)

    @staticmethod
    def _instant(value: str) -> float:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()

    def _records(self, source_id: str, scope_id: str, cls: type[Record]) -> tuple[Record, ...]:
        table, identity, columns = self._TABLES[cls]
        rows = self.db.execute(
            f"SELECT record_json FROM {table} WHERE source_id=? AND scope_id=? ORDER BY {identity}",
            (source_id, scope_id),
        ).fetchall()
        result: list[Record] = []
        for row in rows:
            try:
                result.append(cls.from_mapping(json.loads(row["record_json"])))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise FinanceIngestionError("stored finance record is invalid") from exc
        return tuple(result)

    def accounts(self, source_id: str, scope_id: str) -> tuple[FinanceAccount, ...]:
        return self._records(_identifier(source_id, "source id"), _identifier(scope_id, "scope id"), FinanceAccount)

    def categories(self, source_id: str, scope_id: str) -> tuple[FinanceCategory, ...]:
        return self._records(_identifier(source_id, "source id"), _identifier(scope_id, "scope id"), FinanceCategory)

    def budgets(self, source_id: str, scope_id: str) -> tuple[FinanceBudget, ...]:
        return self._records(_identifier(source_id, "source id"), _identifier(scope_id, "scope id"), FinanceBudget)

    def transactions(self, source_id: str, scope_id: str) -> tuple[FinanceTransaction, ...]:
        return self._records(_identifier(source_id, "source id"), _identifier(scope_id, "scope id"), FinanceTransaction)


Account = FinanceAccount
Category = FinanceCategory
Budget = FinanceBudget
Transaction = FinanceTransaction
IngestionStore = FinanceStore

__all__ = [
    "Account",
    "Budget",
    "Category",
    "FinanceAccount",
    "FinanceBudget",
    "FinanceCategory",
    "FinanceIngestionError",
    "FinanceStore",
    "FinanceSyncResult",
    "FinanceTransaction",
    "IngestionStore",
    "Transaction",
]
