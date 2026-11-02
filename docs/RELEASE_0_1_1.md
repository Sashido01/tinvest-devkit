# Release 0.1.1

**Date:** 2026-11-03
**Version step:** `0.1.0` → `0.1.1` (patch release)
**Readiness:** Package acceptance, hosted CI, CodeQL analysis, repository protection, and PR #1 merge are complete. The source release is version `0.1.1`; package registry publication is excluded.
**Publication:** Pull request [#1](https://github.com/Sashido01/tinvest-devkit/pull/1) was merged into `main` at `427fb193f2e1dcfbad15d86a8c2881f94857a0a7`. The annotated tag [`v0.1.1`](https://github.com/Sashido01/tinvest-devkit/releases/tag/v0.1.1) points to release commit `2c2d7d578b01fad964c92178eb6111ac103b8c85`; the GitHub Release is published.

## What changed

- Added canonical instrument lookup by UID and ambiguity-safe exact ticker resolution with an application-owned `Instrument` model and exact `Decimal` price increment mapping.
- Added immutable account-scoped read-only access. The selected broker account ID must match exactly one account from `GetAccounts`; position and portfolio responses are checked against that ID.
- Bounded operation cursor pagination, rejected repeated cursors, and made incomplete history fail with a dedicated error.
- Kept the Python public surface additive and the client read-only. No order placement, cancellation, strategy, account policy, or live execution support was added.
- Recorded engineering boundaries, current official API references, and transferable Rust practices. This package does not claim Rust broker support or generate a Rust client.
- Added the Apache-2.0 license text already declared by package metadata and advanced the package version from 0.1.0 to 0.1.1.
- Kept SDK `1.49.3` and pinned installation to the matching upstream `Invest-SDK` source commit and SHA-256 archive digest after GitHub-hosted runners failed TLS validation against the official package registry.
- Kept the scaffold creation unit test offline by passing `--no-bootstrap`; bootstrap planning remains tested separately with fake runners.

## Validation evidence

- Full suite on Python 3.11.15: **79 passed**. The SDK emitted 16 deprecation warnings for FIGI request fields in existing API request construction.
- Generated a clean starter project and completed the full bootstrap sequence: all 8 commands succeeded, including a fresh virtual environment, installation of SDK `1.49.3`, devkit `0.1.1`, and pytest, generated-project installation, tests and compile checks.
- The bootstrapped project passed **4 tests** using synthetic data. They covered generated package import, selected-account routing, mismatched-account rejection and exact decimal instrument mapping.
- Ran the generated project's doctor without a token: it reported `NOT READY` at configuration and returned exit code 1 before a broker request, as expected.
- `compileall` passed for `src` and `tests`; `pip check` reported no broken requirements; `git diff --check` passed.
- Built the 0.1.1 wheel and verified that the client module and license text were included.
- The generated smoke directory was removed after verification. Tests used synthetic data; no broker token or real API request was used.
- Repeated the generated-project bootstrap from the pinned GitHub source: bootstrap succeeded, the generated smoke test passed (**1 passed**), and `pip check` and `compileall` passed. Doctor stopped at missing credentials before any API request.

## GitHub Actions status

- CI run [#3](https://github.com/Sashido01/tinvest-devkit/actions/runs/41532972996) confirmed that both hosted runners reject the registry certificate chain as untrusted. TLS verification remains enabled.
- CI run [#4](https://github.com/Sashido01/tinvest-devkit/actions/runs/41534573980) completed successfully for Ubuntu and Windows on PR head `3b5f986e3fb174f29c5fb5189a235cfd61241f0c` after package metadata switched to the exact official SDK source commit and verified archive SHA-256.
- PR CI [#8](https://github.com/Sashido01/tinvest-devkit/actions/runs/41536406995) and CodeQL [#2](https://github.com/Sashido01/tinvest-devkit/actions/runs/41536406900) passed on PR head `e92cfca42c58d6910b15e2c55fcc3cc522221785`.
- Main push CI [run](https://github.com/Sashido01/tinvest-devkit/actions/runs/41538471982) and CodeQL [run](https://github.com/Sashido01/tinvest-devkit/actions/runs/41538472114) passed on merge commit `427fb193f2e1dcfbad15d86a8c2881f94857a0a7`.
- Dependabot version updates are configured weekly for Python dependencies and GitHub Actions in `.github/dependabot.yml`.
- Active Ruleset `Protect main` requires PRs and successful Windows CI, Ubuntu CI, and CodeQL checks; it blocks branch deletion and non-fast-forward updates and has no bypass actors.

## Limits of this verification

- No live broker connectivity, sandbox request, order flow, or real financial data was exercised; no real API call was necessary for the offline smoke acceptance.
- Local validation was performed on Windows with Python 3.11.15; hosted validation passed on Ubuntu and Windows. macOS behavior was not verified.
- Rust formatting, Clippy, build and tests do not apply because this release adds no Rust code.
- SDK request constructors still emit FIGI deprecation warnings. The pinned SDK was not upgraded without compatibility evidence.

## Files in the release

- Package: `pyproject.toml`, `LICENSE`, `src/tinvest_devkit/client.py`, `src/tinvest_devkit/mapper.py`, `src/tinvest_devkit/models.py`.
- Tests: `tests/test_client.py`, `tests/test_instruments.py`, `tests/test_scaffold.py`.
- Documentation: `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/SECURITY.md`, `docs/ENGINEERING_DECISIONS.md`, `docs/RUST_ENGINEERING_GUIDE.md`, `docs/TINVEST_API_BASELINE.md`, and this report.

## Git and publication

- PR #1 is merged; `main` reached `427fb193f2e1dcfbad15d86a8c2881f94857a0a7` and `pyproject.toml` declares `0.1.1`.
- The active branch ruleset and all three required checks were verified before the merge. CI and CodeQL also passed on the resulting `main` merge commit.
- The local `main` was fast-forwarded to `origin/main` at the merge commit and was clean at verification.
- Tag `v0.1.1` and GitHub Release `v0.1.1` are published for commit `2c2d7d578b01fad964c92178eb6111ac103b8c85`. No package registry publication is included.

