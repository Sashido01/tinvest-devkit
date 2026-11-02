# Engineering decisions

**Reviewed:** 2026-11-03

This note records the scope and evidence for the 0.1.1 changes in this repository.

## Decisions

| Area | Decision | Evidence and boundary |
|---|---|---|
| Money mapping | Keep API models independent and map monetary values to `Decimal`. | Existing mapper tests cover positive and negative values. |
| Instrument identity | Use canonical UIDs and reject ambiguous ticker-only selection. | Added `Instrument`, UID lookup, exact ticker filtering and synthetic tests for ambiguity, class-code selection and decimal tick size. |
| Account selection | Require an exact broker account ID and expose an immutable read-only scope. | Synthetic tests cover multiple accounts, unknown or duplicate IDs, and mismatched response IDs. This is validation, not an authorization system. |
| Operation history | Bound cursor pagination and fail closed on repeated cursors or page-limit exhaustion. | Tests cover loop detection, limits and invalid bounds; incomplete results are not returned. |
| Retries | Retry only bounded `UNAVAILABLE` errors. | Rate limits and deadline failures are not retried automatically. See the dated API contract snapshot. |
| Candle data | Preserve UTC timestamps, interval-specific request windows and candle completeness. | Strategy, timeframe policy and provenance remain responsibilities of the consuming application. |
| Write operations | Keep order placement, cancellation, reconciliation and execution state outside this read-only package. | No live execution behavior is implemented or claimed. |
| Rust support | Document transferable engineering practices without adding a Rust API client or scaffold. | Current supported product is the Python package; see `RUST_ENGINEERING_GUIDE.md` and official SDK references. |

## Public API additions

```python
accounts = client.get_accounts()
scope = client.for_account(accounts[0].account_id)
portfolio = scope.get_portfolio()
positions = scope.get_positions()
operations = scope.get_all_operations(max_pages=100)
```

`for_account` explicitly reads the account list, validates one exact ID match, then returns a read-only scope. Position and portfolio snapshots must echo the selected ID. The scope neither caches nor persists account data. API token permissions remain controlled by the broker.

`get_all_operations` raises `OperationPaginationError` when a cursor repeats or the configured page bound is exceeded. It never returns an incomplete result as if it were complete.

## Baseline and validation

The 0.1.0 baseline used Python 3.11+, pinned `t-tech-investments==1.49.3`, and provided account discovery, read-only position/portfolio/price/candle reads, cursor pagination, `Decimal` models, bounded `UNAVAILABLE` retry, a doctor command and a project scaffold. Package metadata declared Apache-2.0; the matching license text is now included.

The baseline suite had 61 tests. The scaffold test attempted online dependency bootstrap and failed when the package-index connection terminated during TLS. It now uses `--no-bootstrap`, keeping the ordinary unit suite deterministic; bootstrap orchestration remains covered by fake-runner tests. An independent clean-project bootstrap later succeeded. See `RELEASE_0_1_1.md` for its validation evidence and platform limits.

## Scope exclusions

- No broker order placement/cancellation, reconciliation, event stream consumer or live state machine.
- No strategy, account-specific risk policy, private persistence schema or PAPER ledger.
- No Rust package or second implementation of the official client.
- No dependency upgrade without compatibility evidence and regression coverage.
- No automatic retry for rate limits, deadlines or ambiguous failures.
