# Troubleshooting

## Purpose

Этот документ содержит типовые проблемы при установке, настройке,
диагностике и использовании `tinvest-devkit`.

Сначала рекомендуется выполнить:

~~~powershell
tinvest-devkit doctor
~~~

или:

~~~powershell
python -m tinvest_devkit doctor
~~~

## t-tech-investments cannot be installed

T-Invest SDK распространяется через T-Bank package index.

Если обычный PyPI не находит пакет, установите зависимости из repository:

~~~powershell
python -m pip install -r requirements.txt
~~~

Для editable installation самого devkit:

~~~powershell
python -m pip install -e . --index-url "https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple"
~~~

Текущая поддерживаемая версия:

~~~text
t-tech-investments==1.49.3
~~~

## TINVEST_TOKEN is required

Создайте локальный `.env` на основе `.env.example`:

~~~text
TINVEST_TOKEN=
TINVEST_ACCOUNT_ID=
~~~

После `TINVEST_TOKEN=` укажите настоящий read-only token.

Не записывайте реальный token в `.env.example`.

## TINVEST_ACCOUNT_ID is required

Некоторые client methods требуют конкретный brokerage account.

Укажите account через `.env`:

~~~text
TINVEST_ACCOUNT_ID=your-account-id
~~~

или передайте его явно поддерживаемому client method.

## I do not know the account ID

Получите список accounts:

~~~python
from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import load_settings

settings = load_settings()
client = TInvestReadClient(settings)

for account in client.get_accounts():
    print(account.account_id, account.name)
~~~

Если accounts несколько, не следует автоматически считать первый account нужным.

## Doctor reports multiple accounts

Если доступно несколько brokerage accounts и `TINVEST_ACCOUNT_ID` не указан,
doctor не может безопасно выбрать нужный account.

Укажите его явно в `.env` и повторите:

~~~powershell
tinvest-devkit doctor
~~~

## Broker API connection failed

Возможные причины:

- network unavailable;
- T-Invest service unavailable;
- invalid or revoked token;
- DNS or TLS problem;
- temporary gRPC failure.

Сначала повторите `tinvest-devkit doctor` и исправьте первый реальный FAIL.

## gRPC UNAVAILABLE

`grpc.StatusCode.UNAVAILABLE` обычно означает transient network/API problem.

`TInvestReadClient` автоматически выполняет retry.

Текущие defaults:

~~~text
attempts: 3
delays: 0.5 s, 1.0 s
~~~

Если все attempts завершились `UNAVAILABLE`, проверьте network и доступность
T-Invest API.

## UNAUTHENTICATED

Authentication errors не являются transient и автоматически не повторяются.

Проверьте:

- правильность token;
- не был ли token revoked;
- нет ли лишних пробелов;
- используется ли правильный `.env`.

## Doctor says NOT READY

Это означает наличие blocking failure.

Типичные причины:

- missing token;
- SDK unavailable;
- broker connection failed;
- configured account unavailable;
- multiple accounts without explicit selection;
- positions request failed;
- portfolio request failed;
- market-data probe failed.

## READY WITH WARNINGS

Это означает, что blocking failures отсутствуют, но есть warning.

Warning следует прочитать, даже если environment уже пригоден для работы.

## READY

`READY` означает, что текущий doctor check прошёл без blocking failures.

Это не гарантирует, что любой будущий API call никогда не завершится ошибкой:
network и broker service остаются внешними dependencies.

## DeprecationWarning about FIGI

В `t-tech-investments==1.49.3` могут появляться warnings вроде:

~~~text
DeprecationWarning: GetCandlesRequest.figi is deprecated
~~~

Важно различать:

~~~text
SDK class содержит deprecated FIGI field
!=
tinvest-devkit использует deprecated FIGI request parameter
~~~

Devkit market-data methods должны использовать `instrument_id`, когда SDK
предоставляет его.

Не подавляйте warning до проверки его фактического источника.

## Tests pass but warnings remain

Пример текущего development snapshot:

~~~text
61 passed, 16 warnings
~~~

Это означает, что tests прошли, а warnings были зарегистрированы.

Warning сам по себе не равен failing test.

## No module named tinvest_devkit

Проверьте, что package установлен в используемый Python environment:

~~~powershell
$PY = Join-Path $PWD ".venv\Scripts\python.exe"
& $PY -m pip install -e . --index-url "https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple"
& $PY -m tinvest_devkit --help
~~~

## Console script tinvest-devkit is not found

В Windows executable обычно находится:

~~~text
.venv\Scripts\tinvest-devkit.exe
~~~

Если файла нет, переустановите editable package в текущий `.venv`.

## Project already exists

`tinvest-devkit new` не перезаписывает существующий target directory.

Используйте другое имя или destination, либо удалите старый temporary project
после проверки его содержимого.

## Project name is rejected

Допустимы letters, digits, hyphen и underscore.

Имя должно начинаться с буквы или цифры.

Недопустимые примеры:

~~~text
-project
_project
bad name
project/path
project!
~~~

## Generated package name differs from project name

Hyphen преобразуется в underscore для Python package.

Пример:

~~~text
Demo-Invest
→
demo_invest
~~~

## I only want project files

Используйте:

~~~powershell
tinvest-devkit new MyProject --no-bootstrap
~~~

Будет создан scaffold без `.venv`, package installation и Git initialization.

## I do not want automatic Git initialization

Используйте:

~~~powershell
tinvest-devkit new MyProject --no-git
~~~

Environment bootstrap выполнится без `git init`.

## Bootstrap fails while creating venv

Проверьте:

~~~powershell
python --version
~~~

Требуется Python 3.11+.

Также проверьте filesystem permissions и свободное место.

## Bootstrap fails during pip install

Проверьте:

- network;
- доступность T-Bank package index;
- pip;
- Python version.

Bootstrap намеренно не скрывает failure внешней command.

## Bootstrap fails because Git is unavailable

Если Git не нужен, используйте `--no-git`.

Если Git нужен, проверьте:

~~~powershell
git --version
~~~

## Generated project tests fail

Перейдите в generated project и используйте его `.venv`:

~~~powershell
$PY = Join-Path $PWD ".venv\Scripts\python.exe"
& $PY -m pytest
& $PY -m compileall -q src tests
~~~

## Generated project cannot install tinvest-devkit from PyPI

На текущем development этапе bootstrap устанавливает local devkit editable из
локального repository.

Generated project source при этом не должен хранить machine-specific absolute
local path.

## .env was accidentally committed

Если token попал в опубликованный Git history:

1. revoke token;
2. create new token;
3. remove `.env` from tracked files;
4. verify `.gitignore`;
5. inspect Git history;
6. never reuse exposed token.

## Accidental nested repository

Если внутри devkit случайно появился второй repository, сначала проверьте его:

~~~powershell
git -C ".\tinvest-devkit" status
git -C ".\tinvest-devkit" log -3 --oneline
~~~

Удалять nested repository можно только после подтверждения, что там нет
нужных uncommitted changes.

## git diff --stat does not show untracked files

Это normal Git behavior.

Новые файлы смотрите через:

~~~powershell
git status --short
~~~

После staging они появятся в:

~~~powershell
git diff --cached --stat
~~~

## LF will be replaced by CRLF

Repository использует `.gitattributes`.

Проверить policy:

~~~powershell
git check-attr -a -- README.md
git ls-files --eol
~~~

Основная политика:

~~~text
Python / Markdown / TOML / INI
→ LF

PowerShell / CMD / BAT
→ CRLF
~~~

## PowerShell shows >>

`>>` означает, что PowerShell ожидает продолжение unfinished expression.

Частые причины:

- незакрытая строка;
- незакрытая quote;
- незакрытая parenthesis;
- незакрытый script block;
- незакрытый here-string.

Для отмены текущего unfinished input нажмите физически `Ctrl+C`.

## PowerShell says else is not recognized

Это может произойти, если `else` отправлен отдельным input fragment после уже
завершившегося `if`.

Для пошаговой interactive работы лучше избегать раздельной отправки
`if`/`else`.

## Safe file generation in interactive PowerShell

Для больших Markdown-файлов в этом проекте предпочтительно не использовать
PowerShell here-string, если сам документ содержит примеры here-string.

Безопаснее передавать содержимое как Base64 и декодировать его перед записью.

## Before reporting a problem

Перед публикацией issue:

- удалите token;
- скройте account identifiers;
- удалите private financial data;
- приложите точный error;
- укажите Python version;
- укажите SDK version;
- укажите devkit commit.

Полезные команды:

~~~powershell
python --version
git rev-parse --short HEAD
git status
~~~
