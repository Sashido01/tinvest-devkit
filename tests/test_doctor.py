from types import SimpleNamespace

from tinvest_devkit.config import Settings
from tinvest_devkit.doctor import (
    render_report,
    run_doctor,
)


class FakeDoctorClient:
    def __init__(
        self,
        *,
        accounts,
        positions=None,
        portfolio=None,
        prices=None,
        accounts_error=None,
        positions_error=None,
        portfolio_error=None,
        prices_error=None,
    ) -> None:
        self.accounts = accounts
        self.positions = (
            positions
            or SimpleNamespace(
                securities=(),
                money=(),
            )
        )
        self.portfolio = (
            portfolio
            or SimpleNamespace(
                positions=(),
            )
        )
        self.prices = prices or []

        self.accounts_error = (
            accounts_error
        )
        self.positions_error = (
            positions_error
        )
        self.portfolio_error = (
            portfolio_error
        )
        self.prices_error = (
            prices_error
        )

        self.position_requests = []
        self.portfolio_requests = []
        self.price_requests = []

    def get_accounts(self):
        if self.accounts_error:
            raise self.accounts_error

        return self.accounts

    def get_positions(
        self,
        *,
        account_id=None,
    ):
        self.position_requests.append(
            account_id
        )

        if self.positions_error:
            raise self.positions_error

        return self.positions

    def get_portfolio(
        self,
        *,
        account_id=None,
    ):
        self.portfolio_requests.append(
            account_id
        )

        if self.portfolio_error:
            raise self.portfolio_error

        return self.portfolio

    def get_last_prices(
        self,
        instrument_ids,
    ):
        self.price_requests.append(
            instrument_ids
        )

        if self.prices_error:
            raise self.prices_error

        return self.prices


def account(account_id: str):
    return SimpleNamespace(
        account_id=account_id,
    )


def test_doctor_ready_for_configured_account(
    tmp_path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "",
        encoding="utf-8",
    )

    portfolio = SimpleNamespace(
        positions=(
            SimpleNamespace(
                instrument_uid="instrument-1"
            ),
        )
    )

    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1")
        ],
        portfolio=portfolio,
    )

    report = run_doctor(
        env_file,
        settings_loader=lambda path: Settings(
            token="secret",
            account_id="account-1",
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is True
    assert report.has_warnings is False
    assert report.summary_status == "READY"

    statuses = {
        check.name: check.status
        for check in report.checks
    }

    assert statuses["Configuration"] == "OK"
    assert statuses["Broker API"] == "OK"
    assert statuses["Accounts"] == "OK"
    assert statuses["Selected account"] == "OK"
    assert statuses["Positions"] == "OK"
    assert statuses["Portfolio"] == "OK"
    assert statuses["Market data"] == "OK"

    assert fake_client.position_requests == [
        "account-1"
    ]

    assert fake_client.portfolio_requests == [
        "account-1"
    ]

    assert fake_client.price_requests == [
        ["instrument-1"]
    ]

    rendered = render_report(report)

    assert "secret" not in rendered
    assert rendered.endswith("READY")


def test_doctor_reports_configuration_failure(
    tmp_path,
) -> None:
    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: (
            (_ for _ in ()).throw(
                ValueError(
                    "TINVEST_TOKEN is required"
                )
            )
        ),
        client_builder=lambda settings: None,
    )

    assert report.ready is False
    assert report.summary_status == "NOT READY"


def test_doctor_rejects_unknown_account(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1")
        ]
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id="missing-account",
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is False

    selected = next(
        check
        for check in report.checks
        if check.name == "Selected account"
    )

    assert selected.status == "FAIL"

    assert fake_client.position_requests == []
    assert fake_client.portfolio_requests == []


def test_doctor_uses_single_account_for_probe(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1")
        ]
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id=None,
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is True
    assert report.has_warnings is True
    assert (
        report.summary_status
        == "READY WITH WARNINGS"
    )

    selected = next(
        check
        for check in report.checks
        if check.name == "Selected account"
    )

    assert selected.status == "WARN"

    assert fake_client.position_requests == [
        "account-1"
    ]

    assert fake_client.portfolio_requests == [
        "account-1"
    ]


def test_doctor_requires_selection_for_multiple_accounts(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1"),
            account("account-2"),
        ]
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id=None,
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is False
    assert report.summary_status == "NOT READY"

    selected = next(
        check
        for check in report.checks
        if check.name == "Selected account"
    )

    assert selected.status == "FAIL"

    assert fake_client.position_requests == []
    assert fake_client.portfolio_requests == []


def test_doctor_reports_broker_api_failure(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[],
        accounts_error=RuntimeError(
            "connection failed"
        ),
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id=None,
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is False

    broker_check = next(
        check
        for check in report.checks
        if check.name == "Broker API"
    )

    assert broker_check.status == "FAIL"
    assert "connection failed" in (
        broker_check.detail
    )


def test_doctor_reports_positions_failure(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1")
        ],
        positions_error=RuntimeError(
            "positions failed"
        ),
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id="account-1",
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is False

    positions = next(
        check
        for check in report.checks
        if check.name == "Positions"
    )

    assert positions.status == "FAIL"


def test_doctor_reports_portfolio_failure(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1")
        ],
        portfolio_error=RuntimeError(
            "portfolio failed"
        ),
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id="account-1",
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is False

    portfolio = next(
        check
        for check in report.checks
        if check.name == "Portfolio"
    )

    assert portfolio.status == "FAIL"


def test_doctor_reports_market_data_failure(
    tmp_path,
) -> None:
    fake_client = FakeDoctorClient(
        accounts=[
            account("account-1")
        ],
        portfolio=SimpleNamespace(
            positions=(
                SimpleNamespace(
                    instrument_uid="instrument-1"
                ),
            )
        ),
        prices_error=RuntimeError(
            "market data failed"
        ),
    )

    report = run_doctor(
        tmp_path / ".env",
        settings_loader=lambda path: Settings(
            token="secret",
            account_id="account-1",
        ),
        client_builder=lambda settings: fake_client,
    )

    assert report.ready is False

    market_data = next(
        check
        for check in report.checks
        if check.name == "Market data"
    )

    assert market_data.status == "FAIL"
