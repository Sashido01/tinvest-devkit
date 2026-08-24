from __future__ import annotations

import time
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, TypeVar

import grpc
from t_tech.invest import (
    CandleInterval,
    Client,
    GetOperationsByCursorRequest,
    OperationState,
)
from t_tech.invest.exceptions import RequestError

from tinvest_devkit.config import Settings
from tinvest_devkit.mapper import (
    map_historic_candle,
    map_last_price,
    map_operation_item,
    map_portfolio_response,
    map_positions_response,
)
from tinvest_devkit.models import (
    Account,
    HistoricCandle,
    LastPrice,
    Operation,
    PortfolioSnapshot,
    PositionsSnapshot,
    SecurityPosition,
)


T = TypeVar("T")


class TInvestReadClient:
    def __init__(
        self,
        settings: Settings,
        client_factory: Callable[
            [str],
            Any,
        ] = Client,
        *,
        retry_attempts: int = 3,
        retry_delay_seconds: float = 0.5,
        sleep_func: Callable[
            [float],
            None,
        ] = time.sleep,
    ) -> None:
        if retry_attempts < 1:
            raise ValueError(
                "retry_attempts must be at least 1"
            )

        if retry_delay_seconds < 0:
            raise ValueError(
                "retry_delay_seconds must not be negative"
            )

        self.settings = settings
        self.client_factory = (
            client_factory
        )
        self.retry_attempts = (
            retry_attempts
        )
        self.retry_delay_seconds = (
            retry_delay_seconds
        )
        self.sleep_func = sleep_func

    def _call_with_retry(
        self,
        operation: Callable[[], T],
    ) -> T:
        for attempt in range(
            1,
            self.retry_attempts + 1,
        ):
            try:
                return operation()

            except RequestError as error:
                should_retry = (
                    error.code
                    == grpc.StatusCode.UNAVAILABLE
                    and attempt
                    < self.retry_attempts
                )

                if not should_retry:
                    raise

                delay = (
                    self.retry_delay_seconds
                    * (2 ** (attempt - 1))
                )

                self.sleep_func(delay)

        raise RuntimeError(
            "retry loop ended unexpectedly"
        )

    def _resolve_account_id(
        self,
        account_id: str | None,
    ) -> str:
        resolved_account_id = (
            account_id
            or self.settings.account_id
        )

        if not resolved_account_id:
            raise ValueError(
                "account_id is required"
            )

        return resolved_account_id

    def get_accounts(
        self,
    ) -> list[Account]:
        with self.client_factory(
            self.settings.token
        ) as client:
            response = (
                self._call_with_retry(
                    client.users.get_accounts
                )
            )

        return [
            Account(
                account_id=account.id,
                name=account.name,
                account_type=int(
                    account.type
                ),
                status=int(
                    account.status
                ),
            )
            for account in response.accounts
        ]

    def get_all_operations(
        self,
        *,
        account_id: str | None = None,
    ) -> list[Operation]:
        resolved_account_id = (
            self._resolve_account_id(
                account_id
            )
        )

        operations: list[
            Operation
        ] = []

        cursor = ""

        with self.client_factory(
            self.settings.token
        ) as client:
            while True:
                request = (
                    GetOperationsByCursorRequest(
                        account_id=(
                            resolved_account_id
                        ),
                        cursor=cursor,
                        limit=1000,
                        state=(
                            OperationState
                            .OPERATION_STATE_EXECUTED
                        ),
                        without_commissions=False,
                        without_trades=False,
                    )
                )

                response = (
                    self._call_with_retry(
                        lambda: (
                            client.operations
                            .get_operations_by_cursor(
                                request
                            )
                        )
                    )
                )

                operations.extend(
                    map_operation_item(
                        item
                    )
                    for item
                    in response.items
                )

                if not response.has_next:
                    break

                if not response.next_cursor:
                    raise ValueError(
                        "has_next=True "
                        "without next_cursor"
                    )

                cursor = (
                    response.next_cursor
                )

        return operations

    def get_last_prices(
        self,
        instrument_ids: list[str],
    ) -> list[LastPrice]:
        if not instrument_ids:
            return []

        with self.client_factory(
            self.settings.token
        ) as client:
            response = (
                self._call_with_retry(
                    lambda: (
                        client.market_data
                        .get_last_prices(
                            instrument_id=(
                                instrument_ids
                            )
                        )
                    )
                )
            )

        return [
            map_last_price(value)
            for value
            in response.last_prices
        ]

    def get_historical_candles(
        self,
        instrument_id: str,
        *,
        from_: datetime,
        to: datetime,
        interval: CandleInterval = (
            CandleInterval.CANDLE_INTERVAL_DAY
        ),
        limit: int | None = None,
    ) -> list[HistoricCandle]:
        if not instrument_id.strip():
            raise ValueError(
                "instrument_id is required"
            )

        if from_ >= to:
            raise ValueError(
                "from_ must be earlier than to"
            )

        with self.client_factory(
            self.settings.token
        ) as client:
            response = (
                self._call_with_retry(
                    lambda: (
                        client.market_data
                        .get_candles(
                            instrument_id=(
                                instrument_id
                            ),
                            from_=from_,
                            to=to,
                            interval=interval,
                            limit=limit,
                        )
                    )
                )
            )

        return [
            map_historic_candle(value)
            for value in response.candles
        ]

    def get_positions(
        self,
        *,
        account_id: str | None = None,
    ) -> PositionsSnapshot:
        resolved_account_id = (
            self._resolve_account_id(
                account_id
            )
        )

        with self.client_factory(
            self.settings.token
        ) as client:
            response = (
                self._call_with_retry(
                    lambda: (
                        client.operations
                        .get_positions(
                            account_id=(
                                resolved_account_id
                            )
                        )
                    )
                )
            )

        return map_positions_response(
            response
        )

    def get_portfolio(
        self,
        *,
        account_id: str | None = None,
    ) -> PortfolioSnapshot:
        resolved_account_id = (
            self._resolve_account_id(
                account_id
            )
        )

        with self.client_factory(
            self.settings.token
        ) as client:
            response = (
                self._call_with_retry(
                    lambda: (
                        client.operations
                        .get_portfolio(
                            account_id=(
                                resolved_account_id
                            )
                        )
                    )
                )
            )

        return map_portfolio_response(
            response
        )

    def get_security_positions(
        self,
        *,
        account_id: str | None = None,
    ) -> list[SecurityPosition]:
        resolved_account_id = (
            self._resolve_account_id(
                account_id
            )
        )

        with self.client_factory(
            self.settings.token
        ) as client:
            response = (
                self._call_with_retry(
                    lambda: (
                        client.operations
                        .get_positions(
                            account_id=(
                                resolved_account_id
                            )
                        )
                    )
                )
            )

        return [
            SecurityPosition(
                instrument_uid=(
                    security.instrument_uid
                ),
                ticker=security.ticker,
                figi=security.figi,
                balance=Decimal(
                    security.balance
                ),
                blocked=Decimal(
                    security.blocked
                ),
                instrument_type=(
                    security.instrument_type
                ),
            )
            for security
            in response.securities
        ]
