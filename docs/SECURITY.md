# Security

## Purpose

`tinvest-devkit` работает с брокерским API и потенциально использует реальные
учётные данные T-Invest.

Главный принцип безопасности проекта:

~~~text
credentials stay local
broker access stays read-only
private financial data does not enter Git
~~~

## Secrets

Никогда не добавляйте в Git:

- T-Invest access token;
- реальный `.env`;
- brokerage account exports;
- production databases;
- private financial information;
- необработанные приватные API responses;
- логи, содержащие токены или чувствительные данные.

Репозиторий содержит только:

~~~text
.env.example
~~~

Реальный `.env` исключён через `.gitignore`.

## Generated projects

Команда:

~~~text
tinvest-devkit new
~~~

создаёт только `.env.example`.

Scaffold намеренно не создаёт настоящий `.env` и не копирует токены из
окружения devkit в новый проект.

После генерации проекта пользователь самостоятельно создаёт локальный `.env`.

## Token permissions

Используйте read-only T-Invest token, когда это возможно.

`TInvestReadClient` намеренно предоставляет только операции чтения.

Для account-scoped чтений используйте `client.for_account(account_id)`. Этот
вызов отдельно получает список доступных счетов и требует ровно одно совпадение
по брокерскому ID. Полученный scope содержит только чтение портфеля, позиций и
операций. Это не подтверждение владения счетом и не замена прав токена: API
может в любой момент отказать в доступе.

Чтение операций ограничено 100 страницами по умолчанию и прекращается при
повторе cursor. Превышение предела приводит к ошибке, а не к выдаче неполного
результата как полного.

В текущий публичный клиент не входят:

- placing orders;
- cancelling orders;
- stop orders;
- account modification;
- другие broker write operations.

Read-only contract является частью архитектуры проекта.

## Environment variables

Основные переменные:

~~~text
TINVEST_TOKEN=
TINVEST_ACCOUNT_ID=
~~~

`TINVEST_TOKEN` является секретом.

`TINVEST_ACCOUNT_ID` не является токеном, но идентификатор реального
брокерского счёта также не следует без необходимости публиковать в:

- issues;
- screenshots;
- logs;
- documentation examples;
- test fixtures.

## Environment doctor

Команда:

~~~text
tinvest-devkit doctor
~~~

может выполнять реальные read-only запросы к T-Invest API.

Doctor не должен печатать значение токена.

В текущей реализации configuration check сообщает только о том, что токен
загружен.

Перед публикацией doctor output всё равно следует проверить на наличие:

- account identifiers;
- количества реальных позиций;
- других сведений, которые пользователь не хочет раскрывать.

## Tests

Обычный unit-test suite не должен требовать реальный брокерский токен.

Для тестирования используются:

- fake SDK clients;
- fake services;
- fake command runners;
- temporary directories.

Реальное API connectivity проверяется отдельно через doctor.

Нельзя добавлять реальные token values или реальные приватные broker payloads
в тестовые fixtures.

## Bootstrap

Bootstrap нового проекта:

- создаёт `.venv`;
- устанавливает зависимости;
- устанавливает локальный `tinvest-devkit`;
- устанавливает generated project;
- при необходимости инициализирует Git;
- запускает тесты и compile checks.

Bootstrap не должен переносить credentials из devkit repository в generated
project.

## Git

Перед commit нового проекта необходимо проверить:

~~~text
git status
~~~

и убедиться, что среди staged/untracked файлов нет:

- `.env`;
- databases с реальными данными;
- broker exports;
- временных диагностических файлов;
- секретов в логах.

## Accidental credential exposure

Если T-Invest token был опубликован:

1. немедленно отозвать token;
2. создать новый token;
3. удалить секрет из рабочих файлов;
4. проверить Git history;
5. считать старый token скомпрометированным даже после удаления файла;
6. не публиковать старый token повторно в issue или commit message.

Простое удаление токена из последнего commit не делает уже опубликованный
token безопасным.

## Logs and screenshots

Перед публикацией логов или screenshots необходимо проверить отсутствие:

- token values;
- account IDs;
- персональных финансовых данных;
- приватных API responses;
- локальных `.env` contents.

## Dependency source

T-Invest SDK устанавливается из source archive организации
[Invest-SDK](https://github.com/Invest-SDK/invest-python) на commit
`5b3bcca6af9d3a4e0bc347261ee6f6493acfe814`. Это временный официальный
GitHub-маршрут, объявленный [T-Bank](https://www.tbank.ru/invest/social/profile/T_InvestAPI/f1923306-7574-4360-9757-6b3a0013318c/)
после недоступности package registry. Требование закрепляет SHA-256 архива.

Не заменяйте этот источник сторонним индексом или зеркалом без отдельной
проверки происхождения пакета.

## Security reports

Не создавайте публичный issue, содержащий реальные credentials или приватные
финансовые данные.

При описании проблемы используйте sanitised output и искусственные
идентификаторы.

