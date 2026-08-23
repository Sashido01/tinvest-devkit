# Security

## Secrets

Never commit T-Invest access tokens, .env files, brokerage account exports, production databases or private financial data.

The repository contains only .env.example.

## Token permissions

Use a read-only T-Invest token whenever possible.

The public client in this project intentionally exposes only read operations.

## Exposed credentials

If a token is accidentally exposed, revoke it through T-Invest immediately and create a new token.

Do not publish exposed credentials in GitHub issues, logs or screenshots.

## Security reports

Do not open a public issue containing access tokens, account identifiers, personal financial information or private API responses.
