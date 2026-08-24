from __future__ import annotations

from decimal import Decimal

from t_tech.invest import (
    HistoricCandle as SdkHistoricCandle,
    LastPrice as SdkLastPrice,
    MoneyValue,
    OperationItem,
    PortfolioResponse,
    PositionsResponse,
    Quotation,
)

from tinvest_devkit.models import (
    HistoricCandle,
    LastPrice,
    MoneyPosition,
    Operation,
    PortfolioPosition,
    PortfolioSnapshot,
    PositionsSnapshot,
    SecurityPosition,
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

def map_security_position(
    security,
) -> SecurityPosition:
    return SecurityPosition(
        instrument_uid=security.instrument_uid,
        ticker=security.ticker,
        figi=security.figi,
        balance=Decimal(
            security.balance
        ),
        blocked=Decimal(
            security.blocked
        ),
        instrument_type=security.instrument_type,
    )


def map_money_position(
    value: MoneyValue,
) -> MoneyPosition:
    return MoneyPosition(
        currency=value.currency,
        amount=money_value_to_decimal(
            value
        ),
    )


def map_positions_response(
    response: PositionsResponse,
) -> PositionsSnapshot:
    return PositionsSnapshot(
        account_id=response.account_id,
        money=tuple(
            map_money_position(value)
            for value in response.money
        ),
        blocked_money=tuple(
            map_money_position(value)
            for value in response.blocked
        ),
        securities=tuple(
            map_security_position(security)
            for security in response.securities
        ),
        limits_loading_in_progress=(
            response.limits_loading_in_progress
        ),
    )


def map_portfolio_position(
    value,
) -> PortfolioPosition:
    return PortfolioPosition(
        instrument_uid=value.instrument_uid,
        position_uid=value.position_uid,
        ticker=value.ticker,
        figi=value.figi,
        instrument_type=value.instrument_type,
        quantity=quotation_to_decimal(
            value.quantity
        ),
        quantity_lots=quotation_to_decimal(
            value.quantity_lots
        ),
        blocked=value.blocked,
        blocked_lots=quotation_to_decimal(
            value.blocked_lots
        ),
        average_position_price=(
            money_value_to_decimal(
                value.average_position_price
            )
        ),
        average_position_price_currency=(
            value.average_position_price.currency
        ),
        average_position_price_fifo=(
            money_value_to_decimal(
                value.average_position_price_fifo
            )
        ),
        average_position_price_fifo_currency=(
            value.average_position_price_fifo.currency
        ),
        current_price=money_value_to_decimal(
            value.current_price
        ),
        current_price_currency=(
            value.current_price.currency
        ),
        expected_yield=quotation_to_decimal(
            value.expected_yield
        ),
        expected_yield_fifo=(
            quotation_to_decimal(
                value.expected_yield_fifo
            )
        ),
        daily_yield=money_value_to_decimal(
            value.daily_yield
        ),
        daily_yield_currency=(
            value.daily_yield.currency
        ),
    )


def map_portfolio_response(
    response: PortfolioResponse,
) -> PortfolioSnapshot:
    return PortfolioSnapshot(
        account_id=response.account_id,
        total_amount_shares=(
            money_value_to_decimal(
                response.total_amount_shares
            )
        ),
        total_amount_bonds=(
            money_value_to_decimal(
                response.total_amount_bonds
            )
        ),
        total_amount_etf=(
            money_value_to_decimal(
                response.total_amount_etf
            )
        ),
        total_amount_currencies=(
            money_value_to_decimal(
                response.total_amount_currencies
            )
        ),
        total_amount_futures=(
            money_value_to_decimal(
                response.total_amount_futures
            )
        ),
        total_amount_options=(
            money_value_to_decimal(
                response.total_amount_options
            )
        ),
        total_amount_sp=(
            money_value_to_decimal(
                response.total_amount_sp
            )
        ),
        total_amount_dfa=(
            money_value_to_decimal(
                response.total_amount_dfa
            )
        ),
        total_amount_portfolio=(
            money_value_to_decimal(
                response.total_amount_portfolio
            )
        ),
        currency=(
            response.total_amount_portfolio.currency
        ),
        expected_yield=quotation_to_decimal(
            response.expected_yield
        ),
        daily_yield=money_value_to_decimal(
            response.daily_yield
        ),
        daily_yield_currency=(
            response.daily_yield.currency
        ),
        daily_yield_relative=(
            quotation_to_decimal(
                response.daily_yield_relative
            )
        ),
        positions=tuple(
            map_portfolio_position(value)
            for value in response.positions
        ),
    )

def map_historic_candle(
    value: SdkHistoricCandle,
) -> HistoricCandle:
    return HistoricCandle(
        timestamp=value.time,
        open=quotation_to_decimal(
            value.open
        ),
        high=quotation_to_decimal(
            value.high
        ),
        low=quotation_to_decimal(
            value.low
        ),
        close=quotation_to_decimal(
            value.close
        ),
        volume=value.volume,
        is_complete=value.is_complete,
        candle_source=int(
            value.candle_source
        ),
        volume_buy=value.volume_buy,
        volume_sell=value.volume_sell,
    )
