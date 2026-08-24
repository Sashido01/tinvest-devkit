from datetime import datetime, timezone
from decimal import Decimal

from t_tech.invest import (
    HistoricCandle as SdkHistoricCandle,
    LastPrice as SdkLastPrice,
    MoneyValue,
    PortfolioPosition as SdkPortfolioPosition,
    PortfolioResponse,
    PositionsResponse,
    PositionsSecurities,
    Quotation,
)

from tinvest_devkit.mapper import (
    map_historic_candle,
    map_last_price,
    map_portfolio_response,
    map_positions_response,
    money_value_to_decimal,
    quotation_to_decimal,
)


def test_money_value_to_decimal() -> None:
    value = MoneyValue(
        currency="rub",
        units=163,
        nano=50_000_000,
    )

    assert (
        money_value_to_decimal(value)
        == Decimal("163.05")
    )


def test_negative_money_value_to_decimal() -> None:
    value = MoneyValue(
        currency="rub",
        units=-326,
        nano=-100_000_000,
    )

    assert (
        money_value_to_decimal(value)
        == Decimal("-326.1")
    )


def test_quotation_to_decimal() -> None:
    value = Quotation(
        units=1,
        nano=250_000_000,
    )

    assert (
        quotation_to_decimal(value)
        == Decimal("1.25")
    )


def test_map_last_price() -> None:
    timestamp = datetime(
        2026,
        8,
        24,
        10,
        0,
        tzinfo=timezone.utc,
    )

    value = SdkLastPrice(
        figi="TESTFIGI",
        price=Quotation(
            units=100,
            nano=500_000_000,
        ),
        time=timestamp,
        instrument_uid="instrument-1",
        last_price_type=1,
    )

    result = map_last_price(value)

    assert result.instrument_uid == "instrument-1"
    assert result.figi == "TESTFIGI"
    assert result.price == Decimal("100.5")
    assert result.timestamp == timestamp
    assert result.price_type == 1

def test_map_positions_response() -> None:
    response = PositionsResponse(
        money=[
            MoneyValue(
                currency="rub",
                units=125,
                nano=500_000_000,
            )
        ],
        blocked=[
            MoneyValue(
                currency="rub",
                units=10,
                nano=0,
            )
        ],
        securities=[
            PositionsSecurities(
                figi="TESTFIGI",
                blocked=1,
                balance=43,
                position_uid="position-1",
                instrument_uid="instrument-1",
                exchange_blocked=False,
                instrument_type="etf",
                ticker="TEST",
            )
        ],
        limits_loading_in_progress=False,
        futures=[],
        options=[],
        account_id="account-1",
    )

    result = map_positions_response(
        response
    )

    assert result.account_id == "account-1"
    assert result.money[0].currency == "rub"
    assert (
        result.money[0].amount
        == Decimal("125.5")
    )
    assert (
        result.blocked_money[0].amount
        == Decimal("10")
    )
    assert result.securities[0].ticker == "TEST"
    assert (
        result.securities[0].balance
        == Decimal("43")
    )


def test_map_portfolio_response() -> None:
    position = SdkPortfolioPosition(
        figi="TESTFIGI",
        instrument_type="etf",
        quantity=Quotation(
            units=43,
            nano=0,
        ),
        average_position_price=MoneyValue(
            currency="rub",
            units=161,
            nano=120_000_000,
        ),
        expected_yield=Quotation(
            units=83,
            nano=80_000_000,
        ),
        current_price=MoneyValue(
            currency="rub",
            units=163,
            nano=50_000_000,
        ),
        average_position_price_fifo=MoneyValue(
            currency="rub",
            units=161,
            nano=120_000_000,
        ),
        quantity_lots=Quotation(
            units=43,
            nano=0,
        ),
        blocked=False,
        blocked_lots=Quotation(
            units=0,
            nano=0,
        ),
        position_uid="position-1",
        instrument_uid="instrument-1",
        expected_yield_fifo=Quotation(
            units=83,
            nano=80_000_000,
        ),
        daily_yield=MoneyValue(
            currency="rub",
            units=1,
            nano=290_000_000,
        ),
        ticker="TEST",
    )

    zero = MoneyValue(
        currency="rub",
        units=0,
        nano=0,
    )

    response = PortfolioResponse(
        total_amount_shares=zero,
        total_amount_bonds=zero,
        total_amount_etf=MoneyValue(
            currency="rub",
            units=7011,
            nano=150_000_000,
        ),
        total_amount_currencies=MoneyValue(
            currency="rub",
            units=71,
            nano=930_000_000,
        ),
        total_amount_futures=zero,
        expected_yield=Quotation(
            units=1,
            nano=180_000_000,
        ),
        positions=[position],
        account_id="account-1",
        total_amount_options=zero,
        total_amount_sp=zero,
        total_amount_portfolio=MoneyValue(
            currency="rub",
            units=7083,
            nano=80_000_000,
        ),
        virtual_positions=[],
        daily_yield=MoneyValue(
            currency="rub",
            units=1,
            nano=290_000_000,
        ),
        daily_yield_relative=Quotation(
            units=0,
            nano=20_000_000,
        ),
        total_amount_dfa=zero,
    )

    result = map_portfolio_response(
        response
    )

    assert result.account_id == "account-1"
    assert (
        result.total_amount_portfolio
        == Decimal("7083.08")
    )
    assert result.currency == "rub"
    assert result.expected_yield == Decimal("1.18")
    assert len(result.positions) == 1
    assert (
        result.positions[0].quantity
        == Decimal("43")
    )
    assert (
        result.positions[0].current_price
        == Decimal("163.05")
    )

def test_map_historic_candle() -> None:
    timestamp = datetime(
        2026,
        8,
        24,
        10,
        0,
        tzinfo=timezone.utc,
    )

    value = SdkHistoricCandle(
        open=Quotation(
            units=100,
            nano=0,
        ),
        high=Quotation(
            units=110,
            nano=0,
        ),
        low=Quotation(
            units=95,
            nano=0,
        ),
        close=Quotation(
            units=105,
            nano=500_000_000,
        ),
        volume=12345,
        time=timestamp,
        is_complete=True,
        candle_source=1,
        volume_buy=7000,
        volume_sell=5345,
    )

    result = map_historic_candle(
        value
    )

    assert result.timestamp == timestamp
    assert result.open == Decimal("100")
    assert result.high == Decimal("110")
    assert result.low == Decimal("95")
    assert result.close == Decimal("105.5")
    assert result.volume == 12345
    assert result.is_complete is True
    assert result.candle_source == 1
    assert result.volume_buy == 7000
    assert result.volume_sell == 5345
