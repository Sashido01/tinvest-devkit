# Release 0.1.1

**Date:** 2026-11-03
**Version step:** `0.1.0` → `0.1.1` (patch release)
**Readiness:** Local acceptance complete; GitHub CI and repository protection are pending.
**Publication:** Pull request [#1](https://github.com/Sashido01/tinvest-devkit/pull/1) is open. The release has not been merged or published.

## What changed

- Added canonical instrument lookup by UID and ambiguity-safe exact ticker resolution with an application-owned `Instrument` model and exact `Decimal` price increment mapping.
- Added immutable account-scoped read-only access. The selected broker account ID must match exactly one account from `GetAccounts`; position and portfolio responses are checked against that ID.
- Bounded operation cursor pagination, rejected repeated cursors, and made incomplete history fail with a dedicated error.
- Kept the Python public surface additive and the client read-only. No order placement, cancellation, strategy, account policy, or live execution support was added.
- Recorded engineering boundaries, current official API references, and transferable Rust practices. This package does not claim Rust broker support or generate a Rust client.
- Added the Apache-2.0 license text already declared by package metadata and advanced the package version from 0.1.0 to 0.1.1.
- Kept the scaffold creation unit test offline by passing `--no-bootstrap`; bootstrap planning remains tested separately with fake runners.

## Validation evidence

- Full suite on Python 3.11.15: **79 passed**. The SDK emitted 16 deprecation warnings for FIGI request fields in existing API request construction.
- Generated a clean starter project and completed the full bootstrap sequence: all 8 commands succeeded, including a fresh virtual environment, installation of SDK `1.49.3`, devkit `0.1.1`, and pytest, generated-project installation, tests and compile checks.
- The bootstrapped project passed **4 tests** using synthetic data. They covered generated package import, selected-account routing, mismatched-account rejection and exact decimal instrument mapping.
- Ran the generated project's doctor without a token: it reported `NOT READY` at configuration and returned exit code 1 before a broker request, as expected.
- `compileall` passed for `src` and `tests`; `pip check` reported no broken requirements; `git diff --check` passed.
- Built the 0.1.1 wheel and verified that the client module and license text were included.
- The generated smoke directory was removed after verification. Tests used synthetic data; no broker token or real API request was used.

## Limits of this verification

- No live broker connectivity, sandbox request, order flow, or real financial data was exercised; no real API call was necessary for the offline smoke acceptance.
- Validation was performed on Windows with Python 3.11.15. Linux and macOS behavior was not verified.
- Rust formatting, Clippy, build and tests do not apply because this release adds no Rust code.
- SDK request constructors still emit FIGI deprecation warnings. The pinned SDK was not upgraded without compatibility evidence.

## Files in the release

- Package: `pyproject.toml`, `LICENSE`, `src/tinvest_devkit/client.py`, `src/tinvest_devkit/mapper.py`, `src/tinvest_devkit/models.py`.
- Tests: `tests/test_client.py`, `tests/test_instruments.py`, `tests/test_scaffold.py`.
- Documentation: `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/SECURITY.md`, `docs/ENGINEERING_DECISIONS.md`, `docs/RUST_ENGINEERING_GUIDE.md`, `docs/TINVEST_API_BASELINE.md`, and this report.

## Git and next action

The implementation is recorded in local scoped commits on a dedicated working branch:

- `5a84b59` — keep scaffold generation test offline;
- `125f1cd` — add scoped account and instrument reads;
- `486afb5` — document reusable API and Rust boundaries.
- `ed5b223` — advance the package from 0.1.0 to 0.1.1 and consolidate changelog history.

This report describes the current PR-based publication path. The release is not complete until CI has run successfully, repository protection is verified, and the pull request is merged. No package registry publication is included.

