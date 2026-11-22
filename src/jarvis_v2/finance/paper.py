"""Separate hypothetical cash, order and position ledger."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3

from .ingestion import FinanceIngestionError, _currency, _identifier, _satang, _text, _timestamp


class PaperLedgerError(FinanceIngestionError):
    """Raised when a paper-only ledger operation cannot be applied."""


def _quantity(value: object, label: str = "quantity") -> int:
    if type(value) is not int or value <= 0 or value > 10**12:
        raise PaperLedgerError(f"invalid {label}")
    return value


@dataclass(frozen=True)
class PaperFillPolicy:
    """Deterministic paper-only execution rules."""

    spread_bps: int = 0
    fee_bps: int = 0
    slippage_bps: int = 0
    max_fill_quantity: int | None = None
    enforce_market_hours: bool = False
    market_open_hour: int = 9
    market_close_hour: int = 16

    def __post_init__(self) -> None:
        for label, value in (("spread", self.spread_bps), ("fee", self.fee_bps), ("slippage", self.slippage_bps)):
            if type(value) is not int or value < 0 or value > 10_000:
                raise PaperLedgerError(f"{label} basis points are invalid")
        if self.max_fill_quantity is not None:
            _quantity(self.max_fill_quantity, "maximum fill quantity")
        if type(self.enforce_market_hours) is not bool:
            raise PaperLedgerError("market-hours flag is invalid")
        if type(self.market_open_hour) is not int or not 0 <= self.market_open_hour < 24:
            raise PaperLedgerError("market open hour is invalid")
        if type(self.market_close_hour) is not int or not 0 <= self.market_close_hour <= 24:
            raise PaperLedgerError("market close hour is invalid")
        if self.market_open_hour >= self.market_close_hour:
            raise PaperLedgerError("market hours are reversed")

    def validate(self, filled_at: str) -> None:
        if not self.enforce_market_hours:
            return
        moment = datetime.fromisoformat(filled_at.replace("Z", "+00:00"))
        if moment.weekday() >= 5 or not self.market_open_hour <= moment.hour < self.market_close_hour:
            raise PaperLedgerError("paper market is closed")


@dataclass(frozen=True)
class PaperAccount:
    account_id: str
    scope_id: str
    currency: str
    cash_satang: int
    created_at: str

    def __post_init__(self) -> None:
        _identifier(self.account_id, "paper account id")
        _identifier(self.scope_id, "paper scope id")
        _currency(self.currency)
        _satang(self.cash_satang, "paper cash", nonnegative=True)
        _timestamp(self.created_at, "paper account timestamp")

    def as_dict(self) -> dict[str, object]:
        return {
            "account_id": self.account_id,
            "person_id": self.scope_id,
            "currency": self.currency,
            "cash_satang": self.cash_satang,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class PaperOrder:
    order_id: str
    account_id: str
    symbol: str
    side: str
    quantity: int
    price_satang: int
    status: str
    created_at: str
    filled_price_satang: int | None = None
    fee_satang: int = 0
    filled_at: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.order_id, "paper order id")
        _identifier(self.account_id, "paper order account id")
        _identifier(self.symbol, "paper symbol")
        if self.side not in {"buy", "sell"}:
            raise PaperLedgerError("paper order side is invalid")
        _quantity(self.quantity)
        _satang(self.price_satang, "paper order price", nonnegative=True)
        if self.price_satang == 0:
            raise PaperLedgerError("paper order price must be positive")
        if self.status not in {"pending", "filled"}:
            raise PaperLedgerError("paper order status is invalid")
        _timestamp(self.created_at, "paper order timestamp")
        if self.status == "pending" and (self.filled_price_satang is not None or self.fee_satang or self.filled_at is not None):
            raise PaperLedgerError("pending paper order has fill data")
        if self.status == "filled":
            if self.filled_price_satang is None:
                raise PaperLedgerError("filled paper order lacks fill price")
            _satang(self.filled_price_satang, "paper fill price", nonnegative=True)
            if self.filled_price_satang == 0:
                raise PaperLedgerError("paper fill price must be positive")
            _satang(self.fee_satang, "paper fee", nonnegative=True)
            if self.filled_at is None:
                raise PaperLedgerError("filled paper order lacks fill timestamp")
            _timestamp(self.filled_at, "paper fill timestamp")

    @property
    def notional_satang(self) -> int:
        return self.quantity * self.price_satang

    def as_dict(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "account_id": self.account_id,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "price_satang": self.price_satang,
            "status": self.status,
            "created_at": self.created_at,
            "filled_price_satang": self.filled_price_satang,
            "fee_satang": self.fee_satang,
            "filled_at": self.filled_at,
        }


@dataclass(frozen=True)
class PaperPosition:
    account_id: str
    symbol: str
    quantity: int
    average_price_satang: int
    updated_at: str

    def __post_init__(self) -> None:
        _identifier(self.account_id, "paper position account id")
        _identifier(self.symbol, "paper position symbol")
        _quantity(self.quantity)
        _satang(self.average_price_satang, "paper position price", nonnegative=True)
        _timestamp(self.updated_at, "paper position timestamp")

    def as_dict(self) -> dict[str, object]:
        return {
            "account_id": self.account_id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "average_price_satang": self.average_price_satang,
            "updated_at": self.updated_at,
        }


class PaperLedger:
    """Persist only hypothetical state; no real-account table is touched."""

    def __init__(self, database: str | Path | sqlite3.Connection):
        self._owns_connection = not isinstance(database, sqlite3.Connection)
        self.db = sqlite3.connect(str(database)) if self._owns_connection else database
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS paper_accounts (
                account_id TEXT PRIMARY KEY, scope_id TEXT NOT NULL, currency TEXT NOT NULL,
                cash_satang INTEGER NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS paper_orders (
                order_id TEXT PRIMARY KEY, account_id TEXT NOT NULL, symbol TEXT NOT NULL,
                side TEXT NOT NULL, quantity INTEGER NOT NULL, price_satang INTEGER NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL, filled_price_satang INTEGER,
                fee_satang INTEGER NOT NULL DEFAULT 0, filled_at TEXT,
                FOREIGN KEY(account_id) REFERENCES paper_accounts(account_id)
            );
            CREATE TABLE IF NOT EXISTS paper_positions (
                account_id TEXT NOT NULL, symbol TEXT NOT NULL, quantity INTEGER NOT NULL,
                average_price_satang INTEGER NOT NULL, updated_at TEXT NOT NULL,
                PRIMARY KEY(account_id, symbol),
                FOREIGN KEY(account_id) REFERENCES paper_accounts(account_id)
            );"""
        )
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(paper_orders)")}
        if "filled_price_satang" not in columns:
            self.db.execute("ALTER TABLE paper_orders ADD COLUMN filled_price_satang INTEGER")
        if "fee_satang" not in columns:
            self.db.execute("ALTER TABLE paper_orders ADD COLUMN fee_satang INTEGER NOT NULL DEFAULT 0")
        if "filled_at" not in columns:
            self.db.execute("ALTER TABLE paper_orders ADD COLUMN filled_at TEXT")
        self.db.commit()

    def __enter__(self) -> "PaperLedger":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_connection:
            self.db.close()

    def open_account(self, account: PaperAccount) -> PaperAccount:
        if not isinstance(account, PaperAccount):
            raise PaperLedgerError("paper account is invalid")
        existing = self.db.execute("SELECT * FROM paper_accounts WHERE account_id=?", (account.account_id,)).fetchone()
        if existing is not None:
            prior = self._account(existing)
            if prior != account:
                raise PaperLedgerError("paper account registration conflict")
            return prior
        self.db.execute(
            "INSERT INTO paper_accounts(account_id,scope_id,currency,cash_satang,created_at) VALUES(?,?,?,?,?)",
            (account.account_id, account.scope_id, account.currency, account.cash_satang, account.created_at),
        )
        self.db.commit()
        return account

    def place_order(self, order: PaperOrder) -> PaperOrder:
        if not isinstance(order, PaperOrder) or order.status != "pending":
            raise PaperLedgerError("new paper order must be pending")
        if self.db.execute("SELECT 1 FROM paper_accounts WHERE account_id=?", (order.account_id,)).fetchone() is None:
            raise PaperLedgerError("paper account does not exist")
        existing = self.db.execute("SELECT * FROM paper_orders WHERE order_id=?", (order.order_id,)).fetchone()
        if existing is not None:
            prior = self._order(existing)
            if prior != order:
                raise PaperLedgerError("paper order registration conflict")
            return prior
        self.db.execute(
            "INSERT INTO paper_orders(order_id,account_id,symbol,side,quantity,price_satang,status,created_at,filled_price_satang,fee_satang,filled_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (order.order_id, order.account_id, order.symbol, order.side, order.quantity, order.price_satang, order.status, order.created_at, None, 0, None),
        )
        self.db.commit()
        return order

    def fill_order(self, order_id: str, *, filled_at: str, policy: PaperFillPolicy | None = None) -> PaperOrder:
        _identifier(order_id, "paper order id")
        _timestamp(filled_at, "paper fill timestamp")
        policy = PaperFillPolicy() if policy is None else policy
        if not isinstance(policy, PaperFillPolicy):
            raise PaperLedgerError("paper fill policy is invalid")
        policy.validate(filled_at)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute("SELECT * FROM paper_orders WHERE order_id=?", (order_id,)).fetchone()
            if row is None:
                raise PaperLedgerError("paper order does not exist")
            order = self._order(row)
            if order.status == "filled":
                self.db.commit()
                return order
            account_row = self.db.execute("SELECT * FROM paper_accounts WHERE account_id=?", (order.account_id,)).fetchone()
            account = self._account(account_row)
            if policy.max_fill_quantity is not None and order.quantity > policy.max_fill_quantity:
                raise PaperLedgerError("paper market has insufficient liquidity")
            spread = order.price_satang * policy.spread_bps // 20_000
            slippage = order.price_satang * policy.slippage_bps // 10_000
            filled_price = order.price_satang + spread + slippage if order.side == "buy" else max(1, order.price_satang - spread - slippage)
            notional = order.quantity * filled_price
            fee = notional * policy.fee_bps // 10_000
            position_row = self.db.execute(
                "SELECT * FROM paper_positions WHERE account_id=? AND symbol=?", (order.account_id, order.symbol),
            ).fetchone()
            prior_quantity = 0 if position_row is None else position_row["quantity"]
            if order.side == "buy":
                if account.cash_satang < notional + fee:
                    raise PaperLedgerError("paper account has insufficient cash")
                cash = account.cash_satang - notional - fee
                quantity = prior_quantity + order.quantity
                prior_average = 0 if position_row is None else position_row["average_price_satang"]
                average = ((prior_quantity * prior_average) + notional) // quantity
            else:
                if prior_quantity < order.quantity:
                    raise PaperLedgerError("paper position is insufficient")
                cash = account.cash_satang + notional - fee
                quantity = prior_quantity - order.quantity
                average = 0 if quantity == 0 else position_row["average_price_satang"]
            self.db.execute("UPDATE paper_accounts SET cash_satang=? WHERE account_id=?", (cash, order.account_id))
            if quantity:
                self.db.execute(
                    "INSERT INTO paper_positions(account_id,symbol,quantity,average_price_satang,updated_at) VALUES(?,?,?,?,?) "
                    "ON CONFLICT(account_id,symbol) DO UPDATE SET quantity=excluded.quantity,average_price_satang=excluded.average_price_satang,updated_at=excluded.updated_at",
                    (order.account_id, order.symbol, quantity, average, filled_at),
                )
            else:
                self.db.execute("DELETE FROM paper_positions WHERE account_id=? AND symbol=?", (order.account_id, order.symbol))
            self.db.execute(
                "UPDATE paper_orders SET status='filled',filled_price_satang=?,fee_satang=?,filled_at=? WHERE order_id=?",
                (filled_price, fee, filled_at, order_id),
            )
            self.db.commit()
            return PaperOrder(
                order.order_id, order.account_id, order.symbol, order.side, order.quantity,
                order.price_satang, "filled", order.created_at, filled_price, fee, filled_at,
            )
        except (sqlite3.Error, PaperLedgerError) as exc:
            self.db.rollback()
            if isinstance(exc, PaperLedgerError):
                raise
            raise PaperLedgerError("paper order persistence failed") from exc

    def account(self, account_id: str) -> PaperAccount:
        _identifier(account_id, "paper account id")
        row = self.db.execute("SELECT * FROM paper_accounts WHERE account_id=?", (account_id,)).fetchone()
        if row is None:
            raise PaperLedgerError("paper account does not exist")
        return self._account(row)

    def accounts(self) -> tuple[PaperAccount, ...]:
        return tuple(self._account(row) for row in self.db.execute(
            "SELECT * FROM paper_accounts ORDER BY account_id"
        ))

    def orders(self, account_id: str) -> tuple[PaperOrder, ...]:
        _identifier(account_id, "paper account id")
        return tuple(self._order(row) for row in self.db.execute("SELECT * FROM paper_orders WHERE account_id=? ORDER BY order_id", (account_id,)))

    def positions(self, account_id: str) -> tuple[PaperPosition, ...]:
        _identifier(account_id, "paper account id")
        return tuple(self._position(row) for row in self.db.execute("SELECT * FROM paper_positions WHERE account_id=? ORDER BY symbol", (account_id,)))

    @staticmethod
    def _account(row: sqlite3.Row) -> PaperAccount:
        return PaperAccount(row["account_id"], row["scope_id"], row["currency"], row["cash_satang"], row["created_at"])

    @staticmethod
    def _order(row: sqlite3.Row) -> PaperOrder:
        return PaperOrder(
            row["order_id"], row["account_id"], row["symbol"], row["side"], row["quantity"],
            row["price_satang"], row["status"], row["created_at"], row["filled_price_satang"],
            row["fee_satang"], row["filled_at"],
        )

    @staticmethod
    def _position(row: sqlite3.Row) -> PaperPosition:
        return PaperPosition(row["account_id"], row["symbol"], row["quantity"], row["average_price_satang"], row["updated_at"])


__all__ = ["PaperAccount", "PaperFillPolicy", "PaperLedger", "PaperLedgerError", "PaperOrder", "PaperPosition"]
