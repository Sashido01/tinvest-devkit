# Rust engineering practices

**Reviewed:** 2026-11-03

This guide captures Rust practices that transfer well to future broker-facing applications. It describes general engineering boundaries; it does not claim that this repository provides Rust support.

## Practices worth carrying forward

- Separate domain rules, broker transport, persistence and user interface into clear modules or workspace crates. Keep optional server processes outside a desktop application's default startup path.
- Use `rust_decimal::Decimal` or another exact decimal representation for money and quotation calculations. Do not route brokerage values through `f64`.
- Represent timestamps in UTC and validate typed response models at system boundaries.
- Keep local simulation persistence separate from broker read snapshots. Give events stable identities, write transactionally and test replay and reopen behavior with synthetic data.
- Use an operating-system credential provider. Credentials must not appear in command lines, logs, Git history or test fixtures.
- Run formatting, Clippy with warnings denied, workspace tests and release builds as separate quality gates. A successful build does not replace testing a real desktop window at expected sizes and keyboard flows.
- Keep UI and server frameworks out of a broker integration library unless they are explicit product requirements.

## Broker integration boundaries

- Keep transport and authentication behind a small adapter; pin the API contract or SDK version used by the application.
- Keep strategy and account policy out of a general-purpose integration package.
- Resolve instruments and accounts by canonical identifiers. Reject ambiguous ticker-only selection.
- Bound retries and pagination. Do not retry rate-limit or deadline failures without a safe, tested policy.
- Keep live writes out of read-only modules. Any future execution layer needs its own reviewed capability, sandbox lifecycle and reconciliation evidence.
- Treat a custom REST/JSON adapter as application-owned code, not as an official SDK. It carries its own transport, schema, compatibility and security maintenance burden.

## Rust support in this repository

The current product is a Python package built around the official `t-tech-investments` SDK. T-Bank's developer language overview does not list a supported Rust SDK; the official `Tinkoff/investAPI` repository identifies Rust SDKs as community-maintained. This repository therefore documents general Rust engineering practices without claiming Rust broker support or generating a Rust client.

Reconsider a Rust crate only when a concrete consumer, contract-generation source, versioning policy, license review and independent integration test are defined.

## References

- [T-Bank developer overview](https://developer.tbank.ru/invest/intro/intro/)
- [Official `Tinkoff/investAPI` SDK list and protobuf contracts](https://github.com/Tinkoff/investAPI)
