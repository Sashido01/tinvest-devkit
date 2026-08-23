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
    def __init__(self) -> None:
        self.requests = []

    def get_last_prices(self, **kwargs):
        self.requests.append(kwargs)

        return SimpleNamespace(
            last_prices=[]
        )


class FakeOperationsService:
    def __init__(self) -> None:
        self.position_requests = []

    def get_positions(self, **kwargs):
        self.position_requests.append(kwargs)

        return SimpleNamespace(
            securities=[]
        )


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
