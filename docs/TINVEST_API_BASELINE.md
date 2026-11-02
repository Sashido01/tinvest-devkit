# T-Invest API contract snapshot

**Verified:** 2026-11-03 against the official T-Bank developer portal and the official `Tinkoff/investAPI` contract repository. Recheck links before SDK or protocol upgrades; this is a dated snapshot, not a generated contract.

## Protocol and SDK

- T-Invest exposes gRPC, a REST proxy, gRPC-web and WebSocket endpoints. This devkit currently uses unary gRPC through the official Python SDK; it does not implement streams.
- Official Python package: `t-tech-investments`, version `1.49.3`. The official T-Bank account announced a temporary move to the `Invest-SDK` GitHub organization when its package registry became unavailable. This repository pins the matching upstream commit and its archive SHA-256; recheck the official installation channel before changing the source.
- T-Bank's language list and official SDK references do not provide a supported Rust SDK; the official GitHub repository labels Rust as community/unofficial. This Python devkit does not claim Rust API support; general Rust engineering practices are recorded separately.
- The official contract repository contains the protobuf schema. Do not hand-copy generated SDK types into application code.
- Token types include read-only, full-access and sandbox. The devkit contract remains read-only; use a read-only token where available.

## Methods used by the devkit

| Method | Contract detail relevant here |
|---|---|
| `UsersService/GetAccounts` | Returns account IDs. Use broker IDs as identity; do not select the first account implicitly. |
| `OperationsService/GetPositions` / `GetPortfolio` | Account ID is required. Each account read is issued separately. |
| `OperationsService/GetOperationsByCursor` | Account ID is required; `limit` defaults to 100 and maxes at 1000; `has_next`/`next_cursor` drive pagination. The devkit additionally caps total pages. |
| `InstrumentsService/GetInstrumentBy` / `FindInstrument` | UID is the canonical instrument key; `GetInstrumentBy` supports UID, FIGI and ticker plus class code. Find results are filtered by exact ticker; ticker alone can be ambiguous. Metadata includes lot, currency, minimum price increment and API-trade availability. |
| `MarketDataService/GetCandles` | `from`/`to` are UTC timestamps and instrument ID can be UID, FIGI or ticker plus class code. Interval duration and result count limits vary by interval. |

## Deadlines, retries and limits

The official portal recommends per-method gRPC deadlines (for example, `GetPortfolio` 1500 ms, `GetPositions` 1000 ms, `GetCandles` 500 ms). The current Python SDK methods used here do not expose a per-call timeout argument in their public signatures, so this repository does **not** claim to enforce those deadlines. Deadline support requires a deliberate SDK/interceptor design and dedicated tests.

The official API distinguishes `UNAVAILABLE` (service unavailable) from `RESOURCE_EXHAUSTED` (including request-rate limits). The devkit retries only bounded `UNAVAILABLE`; it does not automatically retry rate-limit failures. Read-only status alone is not a reason to create request bursts.

## Official references

- [Available protocols and endpoints](https://developer.tbank.ru/invest/intro/developer/protocols/)
- [Token types and authorization](https://developer.tbank.ru/invest/intro/intro/token)
- [Official SDK distribution](https://developer.tbank.ru/invest/release/new_sdk_repo)
- [Official protobuf contracts](https://github.com/Tinkoff/investAPI/tree/main/src/docs/contracts)
- [GetAccounts account-list contract](https://developer.tbank.ru/invest/api/users-service-get-accounts)
- [Account service methods and multi-account isolation](https://developer.tbank.ru/invest/services/accounts/users)
- [GetInstrumentBy instrument metadata](https://developer.tbank.ru/invest/api/instruments-service-get-instrument-by)
- [FindInstrument search contract](https://developer.tbank.ru/invest/api/instruments-service-find-instrument)
- [Instrument identifiers and ticker/class-code rules](https://developer.tbank.ru/invest/intro/intro/faq_identification)
- [GetPositions and GetPortfolio service methods](https://developer.tbank.ru/invest/services/operations/methods)
- [GetOperationsByCursor contract and pagination](https://developer.tbank.ru/invest/api/operations-service-get-operations-by-cursor)
- [GetCandles contract and interval limits](https://developer.tbank.ru/invest/api/market-data-service-get-candles)
- [Historical candle guidance](https://developer.tbank.ru/invest/intro/intro/load_history)
- [Recommended deadlines](https://developer.tbank.ru/invest/intro/developer/deadlines)
- [API limits](https://developer.tbank.ru/invest/intro/intro/limits)
- [gRPC error codes](https://developer.tbank.ru/invest/intro/developer/error-codes/errors)

