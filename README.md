# tinvest-devkit

Reusable read-only development tools for Python projects that use the T-Invest API.

tinvest-devkit provides a small application-facing layer over the official t-tech-investments SDK. It keeps SDK-specific structures out of application code and provides reusable models, configuration, mapping and network reliability helpers.

## Features

- read-only T-Invest client;
- account discovery;
- paginated operation history loading;
- security positions;
- last market prices;
- MoneyValue and Quotation conversion to Decimal;
- application-owned data models;
- .env configuration;
- optional account ID;
- retry for transient gRPC UNAVAILABLE errors;
- unit tests without real broker access.

## Safety

tinvest-devkit is intentionally read-only.

It does not provide methods for:

- placing orders;
- cancelling orders;
- creating stop orders;
- modifying brokerage accounts.

Use a read-only T-Invest token whenever possible.

Never commit a real token or .env file.

## Requirements

- Python 3.11+
- t-tech-investments==1.49.3

The T-Invest Python SDK is distributed through the T-Bank package index rather than the default PyPI index.

## Installation

Clone the repository:

    git clone https://github.com/Sashido01/tinvest-devkit.git
    cd tinvest-devkit

Create a virtual environment in PowerShell:

    python -m venv .venv
    $PY = Join-Path $PWD ".venv\Scripts\python.exe"

Install dependencies:

    & $PY -m pip install --upgrade pip
    & $PY -m pip install -r requirements.txt
    & $PY -m pip install -r requirements-dev.txt

Install tinvest-devkit in editable mode:

    & $PY -m pip install -e . --index-url "https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple"

Run tests:

    & $PY -m pytest

## Configuration

Create .env from .env.example.

Example:

    TINVEST_TOKEN=
    TINVEST_ACCOUNT_ID=

TINVEST_TOKEN is required.

TINVEST_ACCOUNT_ID is optional for account discovery and can be required for account-specific operations.

The real .env file is excluded from Git.

## Quick start

Python example:

    from tinvest_devkit.client import TInvestReadClient
    from tinvest_devkit.config import load_settings

    settings = load_settings()
    client = TInvestReadClient(settings)

    for account in client.get_accounts():
        print(
            account.account_id,
            account.name,
            account.status,
        )

## Load operation history

If TINVEST_ACCOUNT_ID is configured:

    operations = client.get_all_operations()

    for operation in operations:
        print(
            operation.timestamp,
            operation.operation_type,
            operation.description,
        )

An account can also be supplied explicitly:

    operations = client.get_all_operations(
        account_id="your-account-id"
    )

The client follows T-Invest cursor pagination until the complete available operation history has been loaded.

## Last prices

    prices = client.get_last_prices(
        [
            "instrument-uid-1",
            "instrument-uid-2",
        ]
    )

    for price in prices:
        print(
            price.instrument_uid,
            price.price,
            price.timestamp,
        )

## Security positions

    positions = client.get_security_positions()

    for position in positions:
        print(
            position.ticker,
            position.balance,
            position.instrument_uid,
        )

## Decimal precision

Financial values are represented using Python Decimal.

SDK values represented as units and nano are converted without using float.

Available helpers:

    from tinvest_devkit.mapper import (
        money_value_to_decimal,
        quotation_to_decimal,
    )

## Retry behavior

Temporary T-Invest API failures with gRPC status UNAVAILABLE are retried automatically.

Default configuration:

    attempts: 3
    delays: 0.5 s, 1.0 s

Authentication and other non-transient errors are not retried.

Retry parameters can be changed:

    client = TInvestReadClient(
        settings,
        retry_attempts=5,
        retry_delay_seconds=1.0,
    )

## Project structure

    tinvest-devkit/
    |
    +-- docs/
    +-- examples/
    +-- src/
    |   +-- tinvest_devkit/
    |       +-- __init__.py
    |       +-- client.py
    |       +-- config.py
    |       +-- mapper.py
    |       +-- models.py
    +-- tests/
    +-- .env.example
    +-- .gitignore
    +-- pyproject.toml
    +-- pytest.ini
    +-- requirements-dev.txt
    +-- requirements.txt

## Scope

This repository contains reusable infrastructure for T-Invest integrations.

Application-specific concerns should remain in applications built on top of this package, including:

- portfolio accounting;
- P&L rules;
- databases;
- investment strategies;
- user-specific analytics;
- dashboards and interfaces.

## Testing

Tests use fake SDK services and do not require access to a real brokerage account.

Run:

    python -m pytest

The current tests cover configuration, Decimal conversion, market-price mapping, read-only client behavior and transient API retries.

## License

License information will be added before the first tagged release.

## Disclaimer

This is an independent developer utility project.

It is not an official T-Bank or T-Invest product and does not provide investment advice.
