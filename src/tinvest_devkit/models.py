from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Account:
    account_id: str
    name: str
    account_type: int
    status: int


@dataclass(frozen=True)
class Trade:
    trade_id: str
    timestamp: datetime
    quantity: Decimal
    price: Decimal
    currency: str


@dataclass(frozen=True)
class Operation:
    cursor: str
    operation_id: str
    timestamp: datetime
    operation_type: int
    state: int
    name: str
    description: str
    instrument_uid: str | None
    figi: str | None
    quantity: Decimal
    quantity_done: Decimal
    payment: Decimal
    payment_currency: str
    price: Decimal
    price_currency: str
    commission: Decimal
    commission_currency: str
    trades: tuple[Trade, ...]


@dataclass(frozen=True)
class LastPrice:
    instrument_uid: str
    figi: str
    price: Decimal
    timestamp: datetime
    price_type: int


@dataclass(frozen=True)
class SecurityPosition:
    instrument_uid: str
    ticker: str
    figi: str
    balance: Decimal
    blocked: Decimal
    instrument_type: str
