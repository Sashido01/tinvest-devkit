# Release 0.1.1

**Date:** 2026-11-03
**Version step:** `0.1.0` → `0.1.1` (patch release)
**Readiness:** Package acceptance and hosted CI are complete. Repository protection, merge, and release publication remain pending.
**Publication:** Pull request [#1](https://github.com/Sashido01/tinvest-devkit/pull/1) is open. The release has not been merged or published.

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
- `main` remains unprotected (`protected: false` and no required checks); the GitHub connection can read rulesets but exposes no ruleset or branch-protection mutation capability. No protection is claimed.

## Limits of this verification

- No live broker connectivity, sandbox request, order flow, or real financial data was exercised; no real API call was necessary for the offline smoke acceptance.
- Local validation was performed on Windows with Python 3.11.15; hosted validation passed on Ubuntu and Windows. macOS behavior was not verified.
- Rust formatting, Clippy, build and tests do not apply because this release adds no Rust code.
- SDK request constructors still emit FIGI deprecation warnings. The pinned SDK was not upgraded without compatibility evidence.

## Files in the release

- Package: `pyproject.toml`, `LICENSE`, `src/tinvest_devkit/client.py`, `src/tinvest_devkit/mapper.py`, `src/tinvest_devkit/models.py`.
- Tests: `tests/test_client.py`, `tests/test_instruments.py`, `tests/test_scaffold.py`.
- Documentation: `README.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`, `docs/SECURITY.md`, `docs/ENGINEERING_DECISIONS.md`, `docs/RUST_ENGINEERING_GUIDE.md`, `docs/TINVEST_API_BASELINE.md`, and this report.

## Git and remaining work

- PR #1 points to `codex/tinvest-devkit-0.1.1` at `3b5f986e3fb174f29c5fb5189a235cfd61241f0c`; CI is green and GitHub reports the PR as mergeable.
- The local workspace is on `codex/tinvest-devkit-reuse` at `04db956`. It has a different commit history and is not synchronized with the PR branch.
- `main` is still at `144753bab8fae80187528f8981327b9c2fe7f0ac`; no `v0.1.1` tag or GitHub Release exists.
- Complete the repository protection and security settings with an owner connection that has repository administration access, then merge PR #1, publish and verify `v0.1.1`, and synchronize local Git without rewriting history.
- No package registry publication is included.

