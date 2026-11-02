from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, TypeVar

import grpc
from t_tech.invest import (
    CandleInterval,
    Client,
    GetOperationsByCursorRequest,
    InstrumentIdType,
    OperationState,
)
from t_tech.invest.exceptions import RequestError

from tinvest_devkit.config import Settings
from tinvest_devkit.mapper import (
    map_historic_candle,
    map_instrument,
    map_last_price,
    map_operation_item,
    map_portfolio_response,
    map_positions_response,
)
from tinvest_devkit.models import (
    Account,
    HistoricCandle,
    Instrument,
    LastPrice,
    Operation,
    PortfolioSnapshot,
    PositionsSnapshot,
    SecurityPosition,
)


T = TypeVar("T")

DEFAULT_MAX_OPERATION_PAGES = 100


class OperationPaginationError(RuntimeError):
    """Raised when broker cursor pagination cannot be completed safely."""


class AccountScopeError(ValueError):
    """Raised when an exact broker account ID cannot be safely selected."""


class InstrumentResolutionError(ValueError):
    def __init__(
        self,
        message: str,
        *,
        candidates: tuple[Instrument, ...] = (),
    ) -> None:
        super().__init__(message)
        self.candidates = candidates


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

    def get_instrument(self, instrument_uid: str) -> Instrument:
        if not isinstance(instrument_uid, str) or not instrument_uid.strip():
            raise ValueError("instrument_uid is required")
        with self.client_factory(self.settings.token) as client:
            response = self._call_with_retry(
                lambda: client.instruments.get_instrument_by(
                    id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_UID,
                    id=instrument_uid,
                )
            )
        raw_instrument = getattr(response, "instrument", None)
        if raw_instrument is None:
            raise InstrumentResolutionError(
                "GetInstrumentBy response has no instrument"
            )
        instrument = map_instrument(raw_instrument)
        if instrument.uid != instrument_uid:
            raise InstrumentResolutionError(
                "GetInstrumentBy returned a different instrument UID"
            )
        return instrument

    def resolve_instrument(
        self,
        ticker: str,
        *,
        class_code: str | None = None,
    ) -> Instrument:
        normalized_ticker = ticker.strip()
        if not normalized_ticker:
            raise ValueError("ticker is required")
        with self.client_factory(self.settings.token) as client:
            response = self._call_with_retry(
                lambda: client.instruments.find_instrument(
                    query=normalized_ticker
                )
            )
        raw_matches = [
            value
            for value in response.instruments
            if value.ticker.casefold() == normalized_ticker.casefold()
            and (
                class_code is None
                or value.class_code.casefold() == class_code.casefold()
            )
        ]
        matches = [
            map_instrument(value)
            for value in raw_matches
        ]
        by_uid = {value.uid: value for value in matches}
        if any(
            previous != current
            for uid, current in by_uid.items()
            for previous in matches
            if previous.uid == uid
        ):
            raise InstrumentResolutionError(
                "FindInstrument returned conflicting metadata for one UID"
            )
        if not by_uid:
            suffix = f" in class {class_code!r}" if class_code else ""
            raise InstrumentResolutionError(
                f"No T-Invest instrument found for ticker {normalized_ticker!r}{suffix}."
            )
        if len(by_uid) > 1:
            candidates = tuple(
                sorted(by_uid.values(), key=lambda item: (item.class_code, item.uid))
            )
            raise InstrumentResolutionError(
                f"Ticker {normalized_ticker!r} is ambiguous; specify class_code.",
                candidates=candidates,
            )
        return next(iter(by_uid.values()))

    def for_account(
        self,
        account_id: str,
    ) -> AccountReadScope:
        """Validate and bind account-scoped reads to one broker account ID.

        This performs an explicit ``GetAccounts`` read and requires exactly one
        matching broker ID. The returned scope is narrower and read-only.
        """
        if not isinstance(account_id, str) or not account_id.strip():
            raise ValueError("account_id is required")
        matches = [
            account
            for account in self.get_accounts()
            if account.account_id == account_id
        ]
        if not matches:
            raise AccountScopeError(
                "account_id is not present in GetAccounts response"
            )
        if len(matches) != 1:
            raise AccountScopeError(
                "account_id is not unique in GetAccounts response"
            )
        return AccountReadScope(self, matches[0])

    def get_all_operations(
        self,
        *,
        account_id: str | None = None,
        max_pages: int = DEFAULT_MAX_OPERATION_PAGES,
    ) -> list[Operation]:
        if (
            isinstance(max_pages, bool)
            or not isinstance(max_pages, int)
            or max_pages < 1
        ):
            raise ValueError("max_pages must be at least 1")

        resolved_account_id = (
            self._resolve_account_id(
                account_id
            )
        )

        operations: list[
            Operation
        ] = []

        cursor = ""
        seen_cursors = {cursor}
        pages_read = 0

        with self.client_factory(
            self.settings.token
        ) as client:
            while True:
                pages_read += 1
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
                    raise OperationPaginationError(
                        "has_next=True "
                        "without next_cursor"
                    )

                if response.next_cursor in seen_cursors:
                    raise OperationPaginationError(
                        "broker returned a repeated operation cursor"
                    )

                if pages_read >= max_pages:
                    raise OperationPaginationError(
                        f"operation history exceeded max_pages={max_pages}"
                    )

                cursor = (
                    response.next_cursor
                )
                seen_cursors.add(cursor)

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


@dataclass(frozen=True)
class AccountReadScope:
    """Read-only facade whose account-scoped methods use one broker ID."""

    _client: TInvestReadClient
    account: Account

    @property
    def account_id(self) -> str:
        return self.account.account_id

    def get_positions(self) -> PositionsSnapshot:
        snapshot = self._client.get_positions(account_id=self.account_id)
        if snapshot.account_id != self.account_id:
            raise AccountScopeError(
                "GetPositions response account_id does not match the selected account"
            )
        return snapshot

    def get_security_positions(self) -> list[SecurityPosition]:
        return list(self.get_positions().securities)

    def get_portfolio(self) -> PortfolioSnapshot:
        snapshot = self._client.get_portfolio(account_id=self.account_id)
        if snapshot.account_id != self.account_id:
            raise AccountScopeError(
                "GetPortfolio response account_id does not match the selected account"
            )
        return snapshot

    def get_all_operations(
        self,
        *,
        max_pages: int = DEFAULT_MAX_OPERATION_PAGES,
    ) -> list[Operation]:
        return self._client.get_all_operations(
            account_id=self.account_id,
            max_pages=max_pages,
        )
