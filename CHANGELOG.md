# Changelog

All notable changes to this project are documented in this file.

## 0.1.1 — 2026-11-03

### Added

- exact broker-ID validation and immutable account-scoped read-only client;
- canonical instrument metadata lookup and ambiguity-safe ticker resolution;
- bounded operation pagination with cursor-loop detection;
- engineering decisions and dated official T-Invest contract snapshot;
- Rust engineering guide covering transferable practices and SDK support boundaries;
- canonical Apache-2.0 license text matching the package metadata.

### Fixed

- project scaffold creation test no longer starts online dependency bootstrap; bootstrap behavior remains covered separately with fake runners.

### Safety

- account scope exposes only read-only account operations and never selects the first account implicitly;
- incomplete operation history raises a dedicated error instead of returning a partial list.

## 0.1.0

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
- initial reusable package, `.env` configuration, account discovery, paginated operation history, last-price loading and security positions;
- application-owned models, exact `Decimal` conversion, bounded transient gRPC retry, unit tests, read-only boundary, starter examples and security documentation.

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
