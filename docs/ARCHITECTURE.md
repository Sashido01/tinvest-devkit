# Architecture

## Purpose

`tinvest-devkit` — reusable read-only infrastructure layer между Python
application и официальным T-Invest SDK.

Основная архитектурная цель:

~~~text
не допускать прямой зависимости application code
от SDK-specific response structures
~~~

Devkit должен предоставлять:

- стабильные application-owned models;
- read-only API facade;
- mapping SDK → own models;
- configuration loading;
- environment diagnostics;
- project scaffolding;
- automatic bootstrap.

## Main boundary

Основной runtime flow:

~~~text
Application
    |
    v
TInvestReadClient
    |
    v
t-tech-investments SDK
    |
    v
T-Invest API
~~~

Ответы возвращаются через отдельный mapping layer:

~~~text
T-Invest API
    |
    v
SDK response objects
    |
    v
mapper.py
    |
    v
models.py
    |
    v
Application
~~~

Application не должна использовать raw SDK responses как свою domain model.

Account-scoped operations can be narrowed with `TInvestReadClient.for_account`.
That factory explicitly reads `GetAccounts`, requires one exact broker-ID match,
and returns `AccountReadScope`, which does not accept a replacement account ID
on its read methods. The scope is a convenience and fail-closed routing aid; the
broker token remains the actual authorization boundary.

Operation cursor paging has a finite page budget and rejects repeated cursors.
Callers receive either a complete result within the configured budget or an
exception, never an apparently complete partial list.

## Package structure

Основные модули:

~~~text
tinvest_devkit/
|
+-- __main__.py
+-- bootstrap.py
+-- client.py
+-- config.py
+-- doctor.py
+-- mapper.py
+-- models.py
+-- scaffold.py
~~~

## config.py

Responsibilities:

- загрузка `.env`;
- чтение `TINVEST_TOKEN`;
- чтение optional `TINVEST_ACCOUNT_ID`;
- validation required settings;
- создание immutable `Settings`.

Configuration layer не выполняет API requests.

Принцип:

~~~text
configuration
!=
network access
~~~

## models.py

`models.py` содержит application-owned representations.

На текущем этапе представлены модели:

- `Account`;
- `Trade`;
- `Operation`;
- `LastPrice`;
- `SecurityPosition`;
- `MoneyPosition`;
- `PositionsSnapshot`;
- `PortfolioPosition`;
- `PortfolioSnapshot`;
- `HistoricCandle`;
- `Instrument`.

Эти структуры принадлежат devkit, а не SDK.

Это позволяет:

- изолировать applications от изменений SDK;
- тестировать код без protobuf objects;
- контролировать финансовые типы;
- использовать `Decimal`;
- сохранять стабильный internal contract.

## mapper.py

Mapper отвечает за преобразование SDK representations в собственные модели.

Основные задачи:

- `Quotation` → `Decimal`;
- `MoneyValue` → `Decimal`;
- SDK LastPrice → `LastPrice`;
- SDK operation → `Operation`;
- SDK positions → own positions models;
- SDK portfolio → own portfolio models;
- SDK historic candle → `HistoricCandle`.

Instrument lookup prefers canonical UID. Ticker search is a discovery aid only:
the exact ticker is matched case-insensitively, and more than one UID requires
the caller to provide `class_code`. Lot, currency and minimum price increment
remain metadata; this library does not decide whether a trade is appropriate.

Mapper не должен содержать application-specific accounting rules.

Принцип:

~~~text
SDK structure
→ own reusable structure
~~~

а не:

~~~text
SDK structure
→ portfolio accounting
~~~

## Decimal boundary

Финансовые значения должны преобразовываться напрямую:

~~~text
units + nano
→ Decimal
~~~

Использование `float` как промежуточного финансового представления
не допускается.

## client.py

`TInvestReadClient` — основной public broker facade.

Текущие read operations:

- `get_accounts`;
- `get_all_operations`;
- `get_last_prices`;
- `get_historical_candles`;
- `get_positions`;
- `get_portfolio`;
- `get_security_positions`.

Client также содержит:

- account ID resolution;
- cursor pagination;
- transient API retry;
- application-owned mapping.

## Read-only contract

Client намеренно не содержит:

- order placement;
- order cancellation;
- stop order creation;
- account modification;
- другие broker writes.

Read-only поведение является архитектурным ограничением, а не временным
отсутствием функций.

Если в будущем потребуется write-support, он должен быть выделен отдельно,
а не добавлен незаметно в `TInvestReadClient`.

## Retry layer

Network retry относится к reusable infrastructure.

Текущая логика повторяет transient gRPC `UNAVAILABLE`.

Non-transient errors не должны автоматически повторяться без явного правила.

Пример:

~~~text
UNAVAILABLE
→ retry

UNAUTHENTICATED
→ fail immediately
~~~

## Operation history

История операций загружается через cursor pagination.

Flow:

~~~text
GetOperationsByCursor
    |
    v
page 1
    |
    v
next_cursor
    |
    v
page N
    |
    v
has_next = false
~~~

Client возвращает application-owned `Operation`.

## Market data

Current market-data layer включает:

- last prices;
- historical candles.

Для актуальных requests должен использоваться `instrument_id`,
когда SDK предоставляет такую возможность.

Deprecated FIGI request fields не должны использоваться только потому,
что они всё ещё присутствуют в SDK classes.

## Positions

Есть два уровня API:

~~~text
get_positions()
→ complete PositionsSnapshot

get_security_positions()
→ convenience list of securities only
~~~

`PositionsSnapshot` включает как минимум:

- account ID;
- money positions;
- blocked money positions;
- securities;
- loading status.

## Portfolio

`get_portfolio()` возвращает application-owned `PortfolioSnapshot`.

Broker portfolio snapshot является broker fact.

Devkit не превращает его автоматически в user-specific accounting model.

Например следующие вещи не являются задачей reusable client layer:

- realized P&L rules;
- FIFO / weighted-average accounting policy;
- taxation;
- investment performance metrics.

## doctor.py

Doctor является operational diagnostics layer.

Цель:

~~~text
до запуска application
проверить готовность T-Invest environment
~~~

Doctor проверяет:

- Python;
- SDK;
- `.env`;
- configuration;
- API connectivity;
- accounts;
- selected account;
- positions;
- portfolio;
- market data.

Doctor не является частью обычной business logic application.

## Doctor result states

Логическая модель:

~~~text
FAIL exists
→ NOT READY

no FAIL + WARN exists
→ READY WITH WARNINGS

no FAIL + no WARN
→ READY
~~~

При нескольких доступных accounts отсутствие выбранного account ID является
blocking condition.

При одном account он может использоваться только для diagnostic probe с
warning.

## scaffold.py

Scaffold отвечает только за filesystem generation нового проекта.

Он создаёт:

- `.env.example`;
- `.gitignore`;
- `.gitattributes`;
- `pyproject.toml`;
- `pytest.ini`;
- README;
- architecture document;
- `src` package;
- starter `main.py`;
- starter tests.

Scaffold не должен:

- создавать настоящий `.env`;
- копировать credentials;
- устанавливать packages;
- выполнять broker API calls.

## scaffold / bootstrap separation

Архитектурно это разные этапы:

~~~text
scaffold
→ files

bootstrap
→ environment
~~~

Это разделение важно для unit testing.

Scaffold можно тестировать полностью через temporary directory без network,
pip и Git.

## bootstrap.py

Bootstrap отвечает за подготовку generated project.

Текущая последовательность:

~~~text
create .venv
→ upgrade pip
→ install SDK dependencies
→ install local tinvest-devkit editable
→ install pytest
→ install generated project editable
→ optional git init
→ pytest
→ compileall
~~~

Absolute local path к devkit используется только во время bootstrap.

Он не должен сохраняться как machine-specific project configuration.

## Bootstrap command model

Bootstrap сначала строит последовательность commands, затем выполняет её
через runner.

Это позволяет unit tests проверять execution plan без реального запуска:

- `venv`;
- `pip`;
- Git;
- pytest.

## __main__.py

CLI layer должен оставаться тонким.

Он связывает reusable services:

~~~text
CLI
|
+-- doctor
|
+-- new
      |
      +-- scaffold
      |
      +-- bootstrap
~~~

CLI не должен содержать собственную broker accounting logic.

## new command

Default behavior:

~~~text
tinvest-devkit new ProjectName
~~~

выполняет:

~~~text
scaffold
+
bootstrap
~~~

Дополнительные режимы:

~~~text
--no-bootstrap
→ scaffold only

--no-git
→ bootstrap without Git initialization
~~~

## Generated application boundary

Generated application использует devkit как reusable integration dependency.

В application должны оставаться:

- domain models конкретного проекта;
- persistence;
- P&L rules;
- analytics;
- strategies;
- UI;
- web services;
- bots;
- project-specific business logic.

## What should not migrate into devkit

Не следует переносить в devkit только потому, что код уже однажды понадобился:

- SQLite schema конкретного проекта;
- portfolio accounting одного приложения;
- dashboard logic;
- user-specific reports;
- investment strategy;
- tax assumptions;
- project-specific frontend.

Критерий переноса:

~~~text
reusable across independent T-Invest projects
~~~

## Testing architecture

Unit tests используют:

- fake SDK clients;
- fake SDK services;
- fake command runners;
- `tmp_path`;
- monkeypatch.

Это позволяет normal regression suite работать без:

- T-Invest token;
- реального broker account;
- реального network;
- постоянного создания virtual environments.

## Live verification

Реальные integration checks отделены от unit regression.

Используются два smoke-level сценария:

~~~text
doctor
→ real broker connectivity

temporary generated project
→ real bootstrap verification
~~~

После smoke test временный проект должен удаляться.

## Failure boundaries

Ошибки должны возникать максимально близко к своему слою.

Примеры:

~~~text
missing token
→ config / doctor

invalid account
→ client / doctor

SDK mapping mismatch
→ mapper

existing target directory
→ scaffold

pip / Git / venv failure
→ bootstrap
~~~

Нельзя скрывать такие ошибки общим successful status.

## Security architecture

Главные правила:

~~~text
read-only broker client

credentials never generated

credentials never copied

real .env never committed
~~~

Doctor может читать real credentials, но не должен их выводить.

## Line endings

Repository line endings определяются `.gitattributes`.

Основная политика:

~~~text
Python / Markdown / config
→ LF

PowerShell / CMD / BAT
→ CRLF

databases / images
→ binary
~~~

Это снижает platform-specific diff noise.

## Current architectural direction

Следующие улучшения reusable layer должны ориентироваться прежде всего на:

- более полное reusable read-only API coverage;
- stable models;
- SDK compatibility;
- deterministic tests;
- project bootstrap reliability;
- diagnostics;
- developer documentation.

Расширение UI или application-specific accounting не является задачей
`tinvest-devkit`.
