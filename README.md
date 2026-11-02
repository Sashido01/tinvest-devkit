# tinvest-devkit

**Version 0.1.1**

Reusable read-only development tools for Python projects that use the T-Invest API.

`tinvest-devkit` provides an application-facing layer over the official
`t-tech-investments` SDK and reusable tooling for creating, bootstrapping
and validating T-Invest projects.

The package keeps SDK-specific structures out of application code and provides
configuration, application-owned models, mapping, read-only API access,
environment diagnostics and automatic project setup.

## Current status

Current local development release:

- Python 3.11+;
- `t-tech-investments==1.49.3` (pinned; update only after compatibility checks);
- read-only broker integration;
- application-owned models;
- `Decimal` financial values;
- CLI commands `doctor` and `new`;
- automatic project scaffold and bootstrap;
- 79 automated tests in the current suite.
- explicit validated account scopes and bounded operation pagination.

## Features

- read-only T-Invest client;
- account discovery;
- complete paginated operation history loading;
- current security positions;
- current money positions;
- canonical instrument metadata by UID;
- ticker resolution with explicit `class_code` for ambiguous results;
- positions snapshots;
- portfolio snapshots;
- last market prices;
- historical candles;
- `MoneyValue` and `Quotation` conversion to `Decimal`;
- application-owned data models;
- `.env` configuration;
- optional account selection;
- account-bound read-only scope using exact broker IDs;
- bounded cursor pagination with repeat detection;
- retry for transient gRPC `UNAVAILABLE` errors;
- environment and API readiness diagnostics;
- new-project scaffolding;
- automatic virtual environment creation;
- automatic dependency installation;
- optional Git initialization;
- tests without real broker access.

The account scope validates the chosen broker ID with an explicit account-list
request and exposes only account-scoped reads. It does not persist account
information or replace token permissions.

Instrument lookup returns the canonical UID, lot size, currency and exact
`Decimal` price increment. Ticker search never picks the first result when the
same ticker maps to multiple instruments.

## Safety

`tinvest-devkit` is intentionally read-only.

The public client does not provide methods for:

- placing orders;
- cancelling orders;
- creating stop orders;
- modifying brokerage accounts.

Use a read-only T-Invest token whenever possible.

Never commit a real token, `.env` file, brokerage export,
production database or private financial data.

See `docs/SECURITY.md`.

The package is licensed under Apache-2.0; see `LICENSE`.

Engineering decisions and supported boundaries are documented in
`docs/ENGINEERING_DECISIONS.md`, `docs/TINVEST_API_BASELINE.md` and
`docs/RUST_ENGINEERING_GUIDE.md`.

## Requirements

- Python 3.11+;
- Git when automatic Git initialization is required;
- access to GitHub to download the pinned official SDK source archive.

The current supported SDK version is:

~~~text
t-tech-investments==1.49.3
~~~

The SDK dependency is pinned to commit `5b3bcca6` in the
[Invest-SDK source repository](https://github.com/Invest-SDK/invest-python),
with an archive SHA-256 check. T-Bank announced this GitHub location while its
package registry is unavailable. The package name and version remain
`t-tech-investments==1.49.3`.

## Development installation

Clone the repository:

~~~text
git clone https://github.com/Sashido01/tinvest-devkit.git
cd tinvest-devkit
~~~

Create a virtual environment in PowerShell:

~~~powershell
python -m venv .venv
$PY = Join-Path $PWD ".venv\Scripts\python.exe"
~~~

Install dependencies:

~~~powershell
& $PY -m pip install --upgrade pip
& $PY -m pip install -r requirements.txt
& $PY -m pip install -r requirements-dev.txt
~~~

Install `tinvest-devkit` in editable mode:

~~~powershell
& $PY -m pip install -e .
~~~

Run tests:

~~~powershell
& $PY -m pytest
~~~

## CLI

After installation:

~~~powershell
tinvest-devkit --help
~~~

The package currently provides two commands:

~~~text
doctor
new
~~~

The same interface is available through Python:

~~~powershell
python -m tinvest_devkit --help
~~~

## Create a new T-Invest project

The main workflow is:

~~~powershell
tinvest-devkit new MyInvestProject
~~~

By default this performs both project generation and environment bootstrap.

Conceptually:

~~~text
tinvest-devkit new
    |
    +--> scaffold project files
    |
    +--> create .venv
    |
    +--> install dependencies
    |
    +--> install local tinvest-devkit
    |
    +--> install generated project
    |
    +--> initialize Git
    |
    +--> run pytest
    |
    +--> run compileall
    |
    +--> ready for development
~~~

Create a project in another directory:

~~~powershell
tinvest-devkit new MyInvestProject --destination "<projects-directory>"
~~~

Create project files only:

~~~powershell
tinvest-devkit new MyInvestProject --no-bootstrap
~~~

Bootstrap without Git initialization:

~~~powershell
tinvest-devkit new MyInvestProject --no-git
~~~

The scaffold refuses to overwrite an existing target directory.

It also never creates a real `.env` file and never copies credentials.

## Generated project structure

A generated project contains:

~~~text
MyInvestProject/
|
+-- docs/
|   +-- ARCHITECTURE.md
|
+-- src/
|   +-- myinvestproject/
|       +-- __init__.py
|       +-- main.py
|
+-- tests/
|   +-- __init__.py
|   +-- test_smoke.py
|
+-- .env.example
+-- .gitattributes
+-- .gitignore
+-- pyproject.toml
+-- pytest.ini
+-- README.md
~~~

The generated starter already imports `tinvest-devkit` and contains
a minimal read-only T-Invest connection example.

## Configuration

Create `.env` from `.env.example`.

Example:

~~~text
TINVEST_TOKEN=
TINVEST_ACCOUNT_ID=
~~~

`TINVEST_TOKEN` is required.

`TINVEST_ACCOUNT_ID` is optional for account discovery.

Account-specific client operations require either:

- `TINVEST_ACCOUNT_ID` in settings; or
- an account ID passed explicitly to the client method.

The real `.env` file is ignored by Git.

## Environment doctor

Before developing against a real brokerage account, run:

~~~powershell
tinvest-devkit doctor
~~~

A specific environment file can be checked:

~~~powershell
tinvest-devkit doctor --env "<project-directory>/.env"
~~~

The doctor checks:

- Python;
- installed T-Invest SDK;
- environment file;
- configuration;
- broker API connectivity;
- available accounts;
- selected account;
- positions;
- portfolio;
- market-data access.

Token values are not printed.

A successful full diagnostic ends with:

~~~text
READY
~~~

and exits with code `0`.

If only one brokerage account exists and no account ID is configured,
the doctor can use that account for diagnostics and report a warning.

If several accounts are available, explicit account selection is required.

## Python quick start

~~~python
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
~~~

## Account discovery

~~~python
accounts = client.get_accounts()

for account in accounts:
    print(
        account.account_id,
        account.name,
    )
~~~

## Complete operation history

~~~python
operations = client.get_all_operations()

for operation in operations:
    print(
        operation.timestamp,
        operation.operation_type,
        operation.description,
    )
~~~

An account can also be supplied explicitly:

~~~python
operations = client.get_all_operations(
    account_id="your-account-id",
)
~~~

The client follows cursor pagination until the complete available
executed operation history has been loaded.

Commission and trade details are included in the raw application-owned
operation model when returned by the broker.

## Last prices

~~~python
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
~~~

Current calls use instrument UID through `instrument_id`.

## Historical candles

~~~python
from datetime import datetime, timezone

candles = client.get_historical_candles(
    "instrument-uid",
    from_=datetime(
        2026,
        8,
        1,
        tzinfo=timezone.utc,
    ),
    to=datetime(
        2026,
        8,
        24,
        tzinfo=timezone.utc,
    ),
)
~~~

Historical-candle requests use `instrument_id` rather than the deprecated
FIGI request field.

## Positions snapshot

~~~python
positions = client.get_positions()
~~~

The returned application-owned snapshot contains:

- account ID;
- money positions;
- blocked money positions;
- security positions;
- loading-state metadata.

Get only security positions:

~~~python
securities = client.get_security_positions()

for position in securities:
    print(
        position.ticker,
        position.balance,
        position.instrument_uid,
    )
~~~

## Portfolio snapshot

~~~python
portfolio = client.get_portfolio()

for position in portfolio.positions:
    print(
        position.ticker,
        position.quantity,
        position.current_price,
    )
~~~

Portfolio data is mapped into application-owned snapshot models.

Raw SDK response objects are not intended to become the application model.

## Decimal precision

Financial values use Python `Decimal`.

SDK values represented as `units` and `nano` are converted without
passing through `float`.

Available helpers:

~~~python
from tinvest_devkit.mapper import (
    money_value_to_decimal,
    quotation_to_decimal,
)
~~~

## Retry behavior

Transient T-Invest API failures with gRPC status `UNAVAILABLE`
are retried automatically.

Current defaults:

~~~text
attempts: 3
delay 1: 0.5 seconds
delay 2: 1.0 seconds
~~~

Authentication and other non-transient errors are not retried automatically.

Retry configuration can be changed:

~~~python
client = TInvestReadClient(
    settings,
    retry_attempts=5,
    retry_delay_seconds=1.0,
)
~~~

## Application-owned models

Current reusable model groups include:

- `Account`;
- `Trade`;
- `Operation`;
- `LastPrice`;
- `SecurityPosition`;
- `MoneyPosition`;
- `PositionsSnapshot`;
- `PortfolioPosition`;
- `PortfolioSnapshot`;
- `HistoricCandle`.

## Architecture boundary

The intended integration boundary is:

~~~text
T-Invest API
    |
    v
t-tech-investments SDK
    |
    v
tinvest-devkit
    |
    +--> mapping
    |
    +--> application-owned models
    |
    +--> read-only client
    |
    v
application
~~~

Applications built on top of the devkit should keep application-specific
logic in their own repositories.

Examples:

- portfolio accounting;
- P&L rules;
- SQLite databases;
- investment strategies;
- user-specific analytics;
- dashboards;
- bots and interfaces.

## Repository structure

~~~text
tinvest-devkit/
|
+-- docs/
|   +-- SECURITY.md
|
+-- examples/
|   +-- accounts.py
|   +-- operations.py
|   +-- positions.py
|
+-- src/
|   +-- tinvest_devkit/
|       +-- __init__.py
|       +-- __main__.py
|       +-- bootstrap.py
|       +-- client.py
|       +-- config.py
|       +-- doctor.py
|       +-- mapper.py
|       +-- models.py
|       +-- scaffold.py
|
+-- tests/
|
+-- .env.example
+-- .gitattributes
+-- .gitignore
+-- pyproject.toml
+-- pytest.ini
+-- requirements-dev.txt
+-- requirements.txt
~~~

## Testing

The normal regression suite uses fake SDK services and fake command runners
where possible.

It does not require access to a real brokerage account.

Run:

~~~powershell
python -m pytest
~~~

Real broker connectivity is verified separately with:

~~~powershell
tinvest-devkit doctor --env ".env"
~~~

Bootstrap changes should additionally be checked with a temporary real
generated project.

## Known SDK warnings

`t-tech-investments==1.49.3` currently emits several
`DeprecationWarning` messages during import for SDK request structures
that still define deprecated FIGI fields.

These warnings are produced by the installed SDK itself.

They do not currently indicate a failing `tinvest-devkit` test.

Devkit market-data requests should prefer `instrument_id`.

## License

Apache-2.0.

## Disclaimer

This is an independent developer utility project.

It is not an official T-Bank or T-Invest product.

It does not provide investment advice.

