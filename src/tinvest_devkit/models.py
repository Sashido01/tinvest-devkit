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

@dataclass(frozen=True)
class MoneyPosition:
    currency: str
    amount: Decimal


@dataclass(frozen=True)
class PositionsSnapshot:
    account_id: str
    money: tuple[MoneyPosition, ...]
    blocked_money: tuple[MoneyPosition, ...]
    securities: tuple[SecurityPosition, ...]
    limits_loading_in_progress: bool


@dataclass(frozen=True)
class PortfolioPosition:
    instrument_uid: str
    position_uid: str
    ticker: str
    figi: str
    instrument_type: str
    quantity: Decimal
    quantity_lots: Decimal
    blocked: bool
    blocked_lots: Decimal
    average_position_price: Decimal
    average_position_price_currency: str
    average_position_price_fifo: Decimal
    average_position_price_fifo_currency: str
    current_price: Decimal
    current_price_currency: str
    expected_yield: Decimal
    expected_yield_fifo: Decimal
    daily_yield: Decimal
    daily_yield_currency: str


@dataclass(frozen=True)
class PortfolioSnapshot:
    account_id: str
    total_amount_shares: Decimal
    total_amount_bonds: Decimal
    total_amount_etf: Decimal
    total_amount_currencies: Decimal
    total_amount_futures: Decimal
    total_amount_options: Decimal
    total_amount_sp: Decimal
    total_amount_dfa: Decimal
    total_amount_portfolio: Decimal
    currency: str
    expected_yield: Decimal
    daily_yield: Decimal
    daily_yield_currency: str
    daily_yield_relative: Decimal
    positions: tuple[PortfolioPosition, ...]
