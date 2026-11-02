# Development

## Purpose

Этот документ описывает разработку самого `tinvest-devkit`.

Devkit является reusable infrastructure layer для независимых Python-проектов,
работающих с T-Invest API.

Основной принцип разработки:

~~~text
reusable infrastructure
→ tinvest-devkit

application-specific logic
→ отдельный application repository
~~~

## Requirements

Для разработки нужны:

- Python 3.11+;
- Git;
- доступ к GitHub для загрузки закреплённого официального SDK source archive;
- PowerShell для приведённых Windows-команд.

Текущая базовая версия SDK:

~~~text
t-tech-investments==1.49.3, source commit `5b3bcca6`
~~~

## Development environment

Перейти в repository:

~~~powershell
Set-Location "<repository-directory>"
~~~

Создать virtual environment:

~~~powershell
python -m venv .venv
~~~

Определить Python virtual environment:

~~~powershell
$PY = Join-Path $PWD ".venv\Scripts\python.exe"
~~~

Обновить pip:

~~~powershell
& $PY -m pip install --upgrade pip
~~~

Установить runtime dependencies:

~~~powershell
& $PY -m pip install -r requirements.txt
~~~

Установить development dependencies:

~~~powershell
& $PY -m pip install -r requirements-dev.txt
~~~

Установить devkit editable:

~~~powershell
& $PY -m pip install -e .
~~~

## Normal regression

Основной automated regression:

~~~powershell
& $PY -m pytest
~~~

Текущая development baseline на момент актуализации документации:

~~~text
61 passed
~~~

Это число является snapshot текущего состояния, а не permanent invariant.

Количество тестов будет увеличиваться вместе с проектом.

## Targeted tests

Client:

~~~powershell
& $PY -m pytest ".\tests\test_client.py" -q
~~~

Config:

~~~powershell
& $PY -m pytest ".\tests\test_config.py" -q
~~~

Mapper:

~~~powershell
& $PY -m pytest ".\tests\test_mapper.py" -q
~~~

Doctor:

~~~powershell
& $PY -m pytest ".\tests\test_doctor.py" -q
~~~

Scaffold:

~~~powershell
& $PY -m pytest ".\tests\test_scaffold.py" -q
~~~

Bootstrap:

~~~powershell
& $PY -m pytest ".\tests\test_bootstrap.py" -q
~~~

## Compile check

После изменений Python code:

~~~powershell
& $PY -m compileall -q src tests
~~~

Успешный результат не должен возвращать non-zero exit code.

## Git whitespace check

До staging:

~~~powershell
git diff --check
~~~

После staging:

~~~powershell
git diff --cached --check
~~~

Обе проверки должны быть чистыми перед commit.

## Git status

Перед commit:

~~~powershell
git status
~~~

Проверить:

- какие файлы modified;
- какие файлы new;
- отсутствие `.env`;
- отсутствие databases с реальными данными;
- отсутствие случайных temporary directories;
- отсутствие nested repositories.

## Development workflow

Рекомендуемый порядок:

~~~text
inspect current state
→ implement one logical change
→ targeted tests
→ full regression
→ compileall
→ git diff --check
→ inspect diff
→ commit
~~~

Один commit должен представлять один логический этап.

## Client changes

При добавлении новой read-only T-Invest operation:

1. изучить фактический SDK API;
2. проверить method signature;
3. проверить request fields;
4. проверить response model;
5. определить reusable own model;
6. добавить mapper;
7. добавить client method;
8. покрыть fake-service tests;
9. запустить targeted tests;
10. запустить full regression.

Не следует строить implementation на предположении о структуре SDK.

## SDK inspection

`t-tech-investments` использует Python dataclass-like models.

При необходимости SDK structure можно проверять через:

~~~python
import dataclasses
import inspect
~~~

Полезные проверки:

~~~python
print(inspect.signature(SomeSdkType))

for field in dataclasses.fields(SomeSdkType):
    print(field.name, field.type)
~~~

Нельзя предполагать наличие protobuf `DESCRIPTOR`, если текущая версия SDK
использует собственные dataclass models.

## Mapper changes

Mapper должен решать только reusable representation problem:

~~~text
SDK representation
→ devkit representation
~~~

Mapper не должен реализовывать:

- portfolio accounting;
- tax rules;
- investment strategy;
- user-specific P&L;
- database persistence.

## Decimal

Financial values должны оставаться `Decimal`.

Нельзя использовать:

~~~python
float(...)
~~~

как промежуточный шаг для canonical financial value.

Правильный reusable conversion:

~~~text
units
+
nano / 1_000_000_000
→ Decimal
~~~

## Read-only contract

`TInvestReadClient` является read-only API facade.

Не добавлять в него:

- post order;
- cancel order;
- stop order;
- modify account;
- другие write operations.

Если write support когда-либо понадобится, он должен иметь отдельный public
boundary и отдельную safety model.

## Retry behavior

Retry должен применяться только к подтверждённым transient errors.

Текущий подтверждённый retry case:

~~~text
grpc.StatusCode.UNAVAILABLE
~~~

Не следует автоматически retry:

~~~text
UNAUTHENTICATED
INVALID_ARGUMENT
PERMISSION_DENIED
~~~

без отдельной подтверждённой причины.

## Doctor development

Doctor предназначен для operational diagnostics.

При изменениях doctor необходимо проверить:

- token value не печатается;
- ошибки configuration различаются с network errors;
- multiple-account case обрабатывается явно;
- exit code соответствует readiness;
- real API test выполняется отдельно от unit regression.

Unit tests doctor не должны требовать настоящий T-Invest account.

## Real doctor smoke test

Для реальной проверки можно использовать существующий `.env` application:

~~~powershell
tinvest-devkit doctor --env "<application-directory>/.env"
~~~

Успешный full check должен завершаться:

~~~text
READY
~~~

и exit code:

~~~text
0
~~~

Не публиковать real account identifiers без необходимости.

## Scaffold development

Scaffold должен быть deterministic filesystem generator.

Он должен создавать только project files.

Scaffold не должен:

- устанавливать packages;
- запускать network;
- создавать `.venv`;
- создавать настоящий `.env`;
- копировать credentials.

Scaffold tests должны использовать temporary directories.

## Scaffold smoke test

После изменения scaffold:

1. создать temporary destination;
2. выполнить `tinvest-devkit new ... --no-bootstrap`;
3. проверить tree;
4. проверить `pyproject.toml`;
5. проверить starter source;
6. убедиться, что `.env` отсутствует;
7. удалить temporary project.

## Bootstrap development

Bootstrap является executor layer для подготовки generated environment.

Он должен оставаться отделённым от scaffold.

Execution plan должен быть тестируемым без реального запуска commands.

Для этого используются:

- `BootstrapCommand`;
- fake runner;
- unit tests.

## Real bootstrap smoke test

Изменения bootstrap требуют реального temporary smoke test.

Нужно проверить:

~~~text
project scaffold
→ .venv created
→ dependencies installed
→ local devkit installed
→ generated project installed
→ Git initialized
→ pytest passed
→ compileall passed
~~~

После проверки temporary project необходимо удалить.

## CLI development

`__main__.py` должен оставаться thin orchestration layer.

CLI связывает:

~~~text
doctor

new
→ scaffold
→ bootstrap
~~~

CLI не должен содержать собственную implementation SDK mapping или accounting.

## Project generation

Default command:

~~~text
tinvest-devkit new ProjectName
~~~

выполняет scaffold и bootstrap.

Special modes:

~~~text
--no-bootstrap
~~~

создаёт только files.

~~~text
--no-git
~~~

выполняет bootstrap без Git initialization.

## Generated pyproject

Generated project может содержать dependency declaration на `tinvest-devkit`.

При local bootstrap текущий devkit устанавливается editable из local devkit
repository.

Machine-specific absolute devkit path не должен сохраняться в generated
project source или permanent configuration.

## Documentation changes

Когда public behavior меняется, проверить необходимость обновления:

- `README.md`;
- `docs/ARCHITECTURE.md`;
- `docs/SECURITY.md`;
- `docs/DEVELOPMENT.md`;
- troubleshooting documentation;
- changelog.

Documentation должна отражать фактическую implementation, а не planned API.

## SDK warnings

Текущая версия `t-tech-investments==1.49.3` может выдавать
`DeprecationWarning` при import generated SDK request classes, содержащих
deprecated FIGI fields.

Перед suppression warning необходимо определить его источник.

Если devkit code уже использует `instrument_id`, SDK-generated warning сам по
себе не означает defect devkit.

## Line endings

Line-ending policy хранится в `.gitattributes`.

Основные правила:

~~~text
.py / .md / .toml / .ini
→ LF

.ps1 / .cmd / .bat
→ CRLF
~~~

Не следует вручную нормализовать весь repository без необходимости.

## Temporary artifacts

После tests и smoke runs не должны оставаться:

- generated projects;
- temporary clone;
- nested `.git`;
- accidental `.env`;
- build artifacts вне ignore rules.

Перед commit всегда проверять:

~~~powershell
git status --short
~~~

## Commit policy

Рекомендуемые категории:

~~~text
feat:
fix:
test:
docs:
chore:
refactor:
~~~

Пример:

~~~text
feat: add historical candle support
~~~

или:

~~~text
docs: update developer documentation
~~~

## Before commit checklist

Перед каждым commit:

1. targeted tests passed;
2. full regression passed;
3. compileall passed;
4. `git diff --check` passed;
5. staged files inspected;
6. no secrets;
7. no temporary artifacts;
8. commit message соответствует изменению.

## Push

Push выполняется после формирования стабильной local checkpoint.

Перед push полезно проверить:

~~~powershell
git status
git log --oneline --decorate --graph -10
~~~

Рабочее дерево должно быть clean.

