from datetime import datetime, timezone
from decimal import Decimal

from t_tech.invest import (
    LastPrice as SdkLastPrice,
    MoneyValue,
    Quotation,
)

from tinvest_devkit.mapper import (
    map_last_price,
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
