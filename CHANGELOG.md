# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- application-owned positions and portfolio snapshot models;
- mapping for positions and portfolio API responses;
- read-only positions and portfolio client operations;
- historical candle model, mapping and client support;
- repository line-ending policy through `.gitattributes`;
- `tinvest-devkit doctor` environment and API readiness diagnostics;
- `tinvest-devkit new` project scaffolding;
- automatic generated-project bootstrap;
- optional bootstrap without Git initialization;
- optional scaffold-only mode;
- architecture, development, security and troubleshooting documentation.

### Changed

- expanded `TInvestReadClient` beyond the initial account, operations, last-price and security-position functionality;
- expanded application-owned mapping for positions, portfolio and historical market data;
- added account-ID resolution for account-specific client methods;
- expanded regression coverage for client, mapping, doctor, scaffold and bootstrap behavior;
- updated public documentation to match the current CLI and read-only API surface.

### Safety

- generated projects create `.env.example` but never a real `.env`;
- generated projects do not copy credentials from the devkit repository;
- doctor output hides token values;
- the public broker client remains intentionally read-only.

### Validation

Current local development checkpoint:

- Python 3.11.15;
- `t-tech-investments==1.49.3`;
- full regression: 61 passed;
- `compileall`: OK;
- `git diff --check`: OK;
- real doctor smoke test: READY;
- real temporary generated-project bootstrap: OK.

The test count is a snapshot of the current development state and is not a permanent contract.

## 0.1.0

### Added

- initial reusable `tinvest-devkit` package;
- `.env` configuration;
- account discovery;
- paginated operation history;
- last-price loading;
- security positions;
- application-owned models;
- `Quotation` and `MoneyValue` to `Decimal` conversion;
- transient gRPC `UNAVAILABLE` retry handling;
- unit-test infrastructure;
- read-only safety boundary;
- initial examples and security documentation.
