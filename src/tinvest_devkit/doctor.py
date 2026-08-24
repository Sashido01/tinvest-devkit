from __future__ import annotations

import platform
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Callable

from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import Settings, load_settings


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[DoctorCheck, ...]

    @property
    def ready(self) -> bool:
        return not any(
            check.status == "FAIL"
            for check in self.checks
        )

    @property
    def has_warnings(self) -> bool:
        return any(
            check.status == "WARN"
            for check in self.checks
        )

    @property
    def summary_status(self) -> str:
        if not self.ready:
            return "NOT READY"

        if self.has_warnings:
            return "READY WITH WARNINGS"

        return "READY"


def _sdk_version() -> str:
    try:
        return version(
            "t-tech-investments"
        )
    except PackageNotFoundError:
        return "not installed"


def run_doctor(
    env_path: str | Path = ".env",
    *,
    settings_loader: Callable[
        [str | Path],
        Settings,
    ] = load_settings,
    client_builder: Callable[
        [Settings],
        TInvestReadClient,
    ] = TInvestReadClient,
) -> DoctorReport:
    checks: list[DoctorCheck] = []

    checks.append(
        DoctorCheck(
            name="Python",
            status="OK",
            detail=platform.python_version(),
        )
    )

    sdk_version = _sdk_version()

    checks.append(
        DoctorCheck(
            name="T-Invest SDK",
            status=(
                "OK"
                if sdk_version != "not installed"
                else "FAIL"
            ),
            detail=sdk_version,
        )
    )

    env_file = Path(env_path)

    checks.append(
        DoctorCheck(
            name=".env",
            status=(
                "OK"
                if env_file.exists()
                else "WARN"
            ),
            detail=(
                str(env_file)
                if env_file.exists()
                else (
                    "file not found; "
                    "environment variables may still be used"
                )
            ),
        )
    )

    try:
        settings = settings_loader(
            env_path
        )
    except Exception as error:
        checks.append(
            DoctorCheck(
                name="Configuration",
                status="FAIL",
                detail=str(error),
            )
        )

        return DoctorReport(
            checks=tuple(checks)
        )

    checks.append(
        DoctorCheck(
            name="Configuration",
            status="OK",
            detail=(
                "TINVEST_TOKEN loaded; "
                "token value is hidden"
            ),
        )
    )

    client = client_builder(settings)

    try:
        accounts = client.get_accounts()
    except Exception as error:
        checks.append(
            DoctorCheck(
                name="Broker API",
                status="FAIL",
                detail=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            )
        )

        return DoctorReport(
            checks=tuple(checks)
        )

    checks.append(
        DoctorCheck(
            name="Broker API",
            status="OK",
            detail="connection succeeded",
        )
    )

    if not accounts:
        checks.append(
            DoctorCheck(
                name="Accounts",
                status="FAIL",
                detail=(
                    "no brokerage accounts "
                    "available for this token"
                ),
            )
        )

        return DoctorReport(
            checks=tuple(checks)
        )

    checks.append(
        DoctorCheck(
            name="Accounts",
            status="OK",
            detail=(
                f"{len(accounts)} account(s) available"
            ),
        )
    )

    selected_account_id: str | None = None

    if settings.account_id:
        matching_account = next(
            (
                account
                for account in accounts
                if account.account_id
                == settings.account_id
            ),
            None,
        )

        if matching_account is None:
            checks.append(
                DoctorCheck(
                    name="Selected account",
                    status="FAIL",
                    detail=(
                        "TINVEST_ACCOUNT_ID "
                        "does not match an available account"
                    ),
                )
            )

            return DoctorReport(
                checks=tuple(checks)
            )

        selected_account_id = (
            settings.account_id
        )

        checks.append(
            DoctorCheck(
                name="Selected account",
                status="OK",
                detail=(
                    "configured account is available"
                ),
            )
        )

    elif len(accounts) == 1:
        selected_account_id = (
            accounts[0].account_id
        )

        checks.append(
            DoctorCheck(
                name="Selected account",
                status="WARN",
                detail=(
                    "TINVEST_ACCOUNT_ID is not configured; "
                    "the only available account "
                    "is used for diagnostics"
                ),
            )
        )

    else:
        checks.append(
            DoctorCheck(
                name="Selected account",
                status="FAIL",
                detail=(
                    "TINVEST_ACCOUNT_ID is required "
                    "because multiple accounts are available"
                ),
            )
        )

        return DoctorReport(
            checks=tuple(checks)
        )

    try:
        positions = client.get_positions(
            account_id=selected_account_id
        )

        checks.append(
            DoctorCheck(
                name="Positions",
                status="OK",
                detail=(
                    f"{len(positions.securities)} security "
                    f"position(s), "
                    f"{len(positions.money)} money position(s)"
                ),
            )
        )
    except Exception as error:
        checks.append(
            DoctorCheck(
                name="Positions",
                status="FAIL",
                detail=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            )
        )

    portfolio = None

    try:
        portfolio = client.get_portfolio(
            account_id=selected_account_id
        )

        checks.append(
            DoctorCheck(
                name="Portfolio",
                status="OK",
                detail=(
                    f"{len(portfolio.positions)} "
                    "portfolio position(s)"
                ),
            )
        )
    except Exception as error:
        checks.append(
            DoctorCheck(
                name="Portfolio",
                status="FAIL",
                detail=(
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            )
        )

    if portfolio is not None:
        instrument_ids = [
            position.instrument_uid
            for position in portfolio.positions
            if position.instrument_uid
        ]

        if instrument_ids:
            try:
                client.get_last_prices(
                    instrument_ids[:1]
                )

                checks.append(
                    DoctorCheck(
                        name="Market data",
                        status="OK",
                        detail=(
                            "last-price request succeeded"
                        ),
                    )
                )
            except Exception as error:
                checks.append(
                    DoctorCheck(
                        name="Market data",
                        status="FAIL",
                        detail=(
                            f"{type(error).__name__}: "
                            f"{error}"
                        ),
                    )
                )
        else:
            checks.append(
                DoctorCheck(
                    name="Market data",
                    status="WARN",
                    detail=(
                        "no portfolio instrument "
                        "available for market-data probe"
                    ),
                )
            )

    return DoctorReport(
        checks=tuple(checks)
    )


def render_report(
    report: DoctorReport,
) -> str:
    lines = [
        "T-Invest Devkit Doctor",
        "=" * 40,
    ]

    for check in report.checks:
        lines.append(
            f"[{check.status}] "
            f"{check.name}: "
            f"{check.detail}"
        )

    lines.append("=" * 40)
    lines.append(
        report.summary_status
    )

    return "\n".join(lines)


def main(
    env_path: str | Path = ".env",
) -> int:
    report = run_doctor(
        env_path
    )

    print(
        render_report(report)
    )

    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
