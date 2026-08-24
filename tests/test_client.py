from datetime import datetime, timezone
from types import SimpleNamespace

import grpc
import pytest
from t_tech.invest.exceptions import RequestError

from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import Settings


class FakeUsersService:
    def __init__(
        self,
        accounts=None,
        errors=None,
    ) -> None:
        self.accounts = accounts or []
        self.errors = list(errors or [])
        self.calls = 0

    def get_accounts(self):
        self.calls += 1

        if self.errors:
            raise self.errors.pop(0)

        return SimpleNamespace(
            accounts=self.accounts
        )


class FakeMarketDataService:
    def __init__(
        self,
        *,
        candles_response=None,
    ) -> None:
        self.requests = []
        self.candle_requests = []
        self.candles_response = (
            candles_response
        )

    def get_last_prices(self, **kwargs):
        self.requests.append(kwargs)

        return SimpleNamespace(
            last_prices=[]
        )

    def get_candles(self, **kwargs):
        self.candle_requests.append(kwargs)

        if self.candles_response is not None:
            return self.candles_response

        return SimpleNamespace(
            candles=[]
        )


class FakeOperationsService:
    def __init__(
        self,
        *,
        positions_response=None,
        portfolio_response=None,
    ) -> None:
        self.position_requests = []
        self.portfolio_requests = []
        self.positions_response = (
            positions_response
        )
        self.portfolio_response = (
            portfolio_response
        )

    def get_positions(self, **kwargs):
        self.position_requests.append(kwargs)

        if self.positions_response is not None:
            return self.positions_response

        return SimpleNamespace(
            securities=[]
        )

    def get_portfolio(self, **kwargs):
        self.portfolio_requests.append(kwargs)

        return self.portfolio_response


class FakeSdkClient:
    users_service = None
    market_data_service = None
    operations_service = None

    def __init__(self, token: str) -> None:
        self.token = token
        self.users = FakeSdkClient.users_service
        self.market_data = (
            FakeSdkClient.market_data_service
        )
        self.operations = (
            FakeSdkClient.operations_service
        )

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False


def make_settings(
    account_id: str | None = "account-1",
) -> Settings:
    return Settings(
        token="test-token",
        account_id=account_id,
    )


def unavailable_error() -> RequestError:
    return RequestError(
        grpc.StatusCode.UNAVAILABLE,
        "temporary failure",
        None,
    )


def test_get_accounts_maps_accounts() -> None:
    FakeSdkClient.users_service = FakeUsersService(
        accounts=[
            SimpleNamespace(
                id="account-1",
                name="Test",
                type=1,
                status=2,
            )
        ]
    )

    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
    )

    accounts = client.get_accounts()

    assert len(accounts) == 1
    assert accounts[0].account_id == "account-1"
    assert accounts[0].name == "Test"


def test_unavailable_is_retried() -> None:
    service = FakeUsersService(
        errors=[
            unavailable_error(),
            unavailable_error(),
        ]
    )

    FakeSdkClient.users_service = service

    delays = []

    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
        retry_attempts=3,
        retry_delay_seconds=0.5,
        sleep_func=delays.append,
    )

    assert client.get_accounts() == []
    assert service.calls == 3
    assert delays == [0.5, 1.0]


def test_non_transient_error_is_not_retried() -> None:
    service = FakeUsersService(
        errors=[
            RequestError(
                grpc.StatusCode.UNAUTHENTICATED,
                "invalid token",
                None,
            )
        ]
    )

    FakeSdkClient.users_service = service

    delays = []

    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
        sleep_func=delays.append,
    )

    with pytest.raises(RequestError):
        client.get_accounts()

    assert service.calls == 1
    assert delays == []


def test_get_last_prices_empty_input() -> None:
    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
    )

    assert client.get_last_prices([]) == []


def test_get_last_prices_passes_ids() -> None:
    service = FakeMarketDataService()

    FakeSdkClient.market_data_service = service

    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
    )

    result = client.get_last_prices(
        [
            "instrument-1",
            "instrument-2",
        ]
    )

    assert result == []

    assert service.requests == [
        {
            "instrument_id": [
                "instrument-1",
                "instrument-2",
            ]
        }
    ]


def test_positions_use_settings_account_id() -> None:
    service = FakeOperationsService()

    FakeSdkClient.operations_service = service

    client = TInvestReadClient(
        make_settings("account-xyz"),
        client_factory=FakeSdkClient,
    )

    result = client.get_security_positions()

    assert result == []

    assert service.position_requests == [
        {
            "account_id": "account-xyz",
        }
    ]


def test_positions_require_account_id() -> None:
    client = TInvestReadClient(
        make_settings(None),
        client_factory=FakeSdkClient,
    )

    with pytest.raises(
        ValueError,
        match="account_id is required",
    ):
        client.get_security_positions()

def test_get_positions_returns_snapshot() -> None:
    service = FakeOperationsService(
        positions_response=SimpleNamespace(
            account_id="account-xyz",
            money=[],
            blocked=[],
            securities=[],
            limits_loading_in_progress=False,
        )
    )

    FakeSdkClient.operations_service = service

    client = TInvestReadClient(
        make_settings("account-xyz"),
        client_factory=FakeSdkClient,
    )

    result = client.get_positions()

    assert result.account_id == "account-xyz"
    assert result.money == ()
    assert result.blocked_money == ()
    assert result.securities == ()

    assert service.position_requests == [
        {
            "account_id": "account-xyz",
        }
    ]


def test_get_portfolio_passes_account_id(
    monkeypatch,
) -> None:
    expected = object()

    service = FakeOperationsService(
        portfolio_response=object()
    )

    FakeSdkClient.operations_service = service

    monkeypatch.setattr(
        "tinvest_devkit.client.map_portfolio_response",
        lambda response: expected,
    )

    client = TInvestReadClient(
        make_settings("account-xyz"),
        client_factory=FakeSdkClient,
    )

    result = client.get_portfolio()

    assert result is expected

    assert service.portfolio_requests == [
        {
            "account_id": "account-xyz",
        }
    ]


def test_get_portfolio_requires_account_id() -> None:
    client = TInvestReadClient(
        make_settings(None),
        client_factory=FakeSdkClient,
    )

    with pytest.raises(
        ValueError,
        match="account_id is required",
    ):
        client.get_portfolio()

def test_get_historical_candles_uses_instrument_id(
    monkeypatch,
) -> None:
    expected = object()

    service = FakeMarketDataService(
        candles_response=SimpleNamespace(
            candles=[object()]
        )
    )

    FakeSdkClient.market_data_service = service

    monkeypatch.setattr(
        "tinvest_devkit.client.map_historic_candle",
        lambda value: expected,
    )

    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
    )

    from_time = datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    )

    to_time = datetime(
        2026,
        8,
        24,
        tzinfo=timezone.utc,
    )

    result = client.get_historical_candles(
        "instrument-1",
        from_=from_time,
        to=to_time,
    )

    assert result == [expected]

    request = service.candle_requests[0]

    assert request["instrument_id"] == "instrument-1"
    assert "figi" not in request
    assert request["from_"] == from_time
    assert request["to"] == to_time


def test_historical_candles_require_instrument_id() -> None:
    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
    )

    with pytest.raises(
        ValueError,
        match="instrument_id is required",
    ):
        client.get_historical_candles(
            "   ",
            from_=datetime(
                2026,
                8,
                1,
                tzinfo=timezone.utc,
            ),
            to=datetime(
                2026,
                8,
                2,
                tzinfo=timezone.utc,
            ),
        )


def test_historical_candles_validate_date_range() -> None:
    client = TInvestReadClient(
        make_settings(),
        client_factory=FakeSdkClient,
    )

    timestamp = datetime(
        2026,
        8,
        24,
        tzinfo=timezone.utc,
    )

    with pytest.raises(
        ValueError,
        match="from_ must be earlier than to",
    ):
        client.get_historical_candles(
            "instrument-1",
            from_=timestamp,
            to=timestamp,
        )
