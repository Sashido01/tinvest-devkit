from __future__ import annotations

from decimal import Decimal

from t_tech.invest import (
    LastPrice as SdkLastPrice,
    MoneyValue,
    OperationItem,
    Quotation,
)

from tinvest_devkit.models import (
    LastPrice,
    Operation,
    Trade,
)


NANO_FACTOR = Decimal("1000000000")


def quotation_to_decimal(
    value: Quotation,
) -> Decimal:
    return Decimal(value.units) + (
        Decimal(value.nano) / NANO_FACTOR
    )


def money_value_to_decimal(
    value: MoneyValue,
) -> Decimal:
    return Decimal(value.units) + (
        Decimal(value.nano) / NANO_FACTOR
    )


def map_last_price(
    value: SdkLastPrice,
) -> LastPrice:
    return LastPrice(
        instrument_uid=value.instrument_uid,
        figi=value.figi,
        price=quotation_to_decimal(
            value.price
        ),
        timestamp=value.time,
        price_type=int(
            value.last_price_type
        ),
    )


def map_operation_item(
    item: OperationItem,
) -> Operation:
    trades = tuple(
        Trade(
            trade_id=trade.num,
            timestamp=trade.date,
            quantity=Decimal(
                trade.quantity
            ),
            price=money_value_to_decimal(
                trade.price
            ),
            currency=trade.price.currency,
        )
        for trade in item.trades_info.trades
    )

    return Operation(
        cursor=item.cursor,
        operation_id=item.id,
        timestamp=item.date,
        operation_type=int(item.type),
        state=int(item.state),
        name=item.name,
        description=item.description,
        instrument_uid=(
            item.instrument_uid or None
        ),
        figi=item.figi or None,
        quantity=Decimal(
            item.quantity
        ),
        quantity_done=Decimal(
            item.quantity_done
        ),
        payment=money_value_to_decimal(
            item.payment
        ),
        payment_currency=(
            item.payment.currency
        ),
        price=money_value_to_decimal(
            item.price
        ),
        price_currency=(
            item.price.currency
        ),
        commission=money_value_to_decimal(
            item.commission
        ),
        commission_currency=(
            item.commission.currency
        ),
        trades=trades,
    )
