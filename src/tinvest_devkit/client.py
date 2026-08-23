from __future__ import annotations

import time
from decimal import Decimal
from typing import Any, Callable, TypeVar

import grpc
from t_tech.invest import (
    Client,
    GetOperationsByCursorRequest,
    OperationState,
)
from t_tech.invest.exceptions import RequestError

from tinvest_devkit.config import Settings
from tinvest_devkit.mapper import (
    map_last_price,
    map_operation_item,
)
from tinvest_devkit.models import (
    Account,
    LastPrice,
    Operation,
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
            account_id
            or self.settings.account_id
        )

        if not resolved_account_id:
            raise ValueError(
                "account_id is required"
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

    def get_security_positions(
        self,
        *,
        account_id: str | None = None,
    ) -> list[SecurityPosition]:
        resolved_account_id = (
            account_id
            or self.settings.account_id
        )

        if not resolved_account_id:
            raise ValueError(
                "account_id is required"
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
