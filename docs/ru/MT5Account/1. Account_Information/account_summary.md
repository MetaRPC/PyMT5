# Получение полной сводки по счёту

> **Запрос:** полный снимок счёта со **всеми основными свойствами** за один вызов (баланс, средства (equity), кредитное плечо, валюта, время сервера и т. д.).

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.account_summary(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Proto-определение:** `AccountSummary` (определено в `mt5-term-api-account-helper.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `AccountSummary(AccountSummaryRequest) -> AccountSummaryReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.AccountSummary(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить полный снимок счёта со всеми основными свойствами за один вызов.
* **Зачем это нужно.** Наиболее эффективный способ получить несколько свойств счёта (баланс, средства (equity), кредитное плечо и т. д.).
* **Когда использовать.** Используйте это для общей информации о счёте. Используйте методы `account_info_*` только для отдельных конкретных свойств.

---

## 🎯 Назначение

Используйте его для получения исчерпывающей информации о счёте:

* **РЕКОМЕНДУЕМЫЙ** метод для получения обзора счёта
* Получить баланс, средства (equity), кредит за один вызов
* Проверить логин, имя, сервер, компанию счёта
* Получить кредитное плечо и режим торговли (demo/real)
* Получить валюту счёта
* Получить время сервера со смещением UTC
* Эффективно - одно обращение к серверу вместо нескольких вызовов

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [account_summary - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW.md)**

---

## Сигнатура метода

```python
async def account_summary(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Сообщение запроса:**

```protobuf
message AccountSummaryRequest {
  // Пусто - параметры не нужны
}
```

**Сообщение ответа:**

```protobuf
message AccountSummaryReply {
  oneof response {
    AccountSummaryData data = 1;
    Error error = 2;
  }
}

message AccountSummaryData {
  int64 account_login = 1;
  double account_balance = 2;
  double account_equity = 3;
  string account_user_name = 4;
  int64 account_leverage = 5;
  MrpcEnumAccountTradeMode account_trade_mode = 6;
  string account_company_name = 7;
  string account_currency = 8;
  google.protobuf.Timestamp server_time = 9;
  int64 utc_timezone_server_time_shift_minutes = 10;
  double account_credit = 11;
  double account_margin = 12;
  int32 server_utc_offset_seconds = 13;
  google.protobuf.Timestamp server_time_utc = 14;
  double account_margin_free = 15;
  double account_margin_level = 16;
  MrpcEnumAccountMarginMode account_margin_mode = 17;
  bool account_trade_allowed = 18;
  bool account_trade_expert = 19;
  bool terminal_connected = 20;
  bool terminal_trade_allowed = 21;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `deadline`    | `datetime` (необязательно)   | Дедлайн для gRPC-вызова (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                    |

**property_id не требуется** - этот метод возвращает все доступные свойства.

**Варианты дедлайна:**

```python
from datetime import datetime, timedelta, timezone

# 1. С дедлайном (рекомендуется)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
summary = await account.account_summary(deadline=deadline)

# 2. С событием отмены
cancel_event = asyncio.Event()
summary = await account.account_summary(cancellation_event=cancel_event)

# 3. Без дедлайна (используется таймаут по умолчанию, если настроен)
summary = await account.account_summary()
```

---

## ⬆️ Выход - `AccountSummaryData`

| Поле                                   | Тип                         | Python-тип  | Описание                                          |
| -------------------------------------- | --------------------------- | ----------- | ---------------------------------------------------- |
| `account_login`                        | `int64`                     | `int`       | Номер счёта                                       |
| `account_balance`                      | `double`                    | `float`     | Баланс счёта в валюте депозита                  |
| `account_equity`                       | `double`                    | `float`     | Средства (equity) счёта (баланс + плавающая прибыль/убыток)      |
| `account_user_name`                    | `string`                    | `str`       | Имя владельца счёта                                   |
| `account_leverage`                     | `int64`                     | `int`       | Кредитное плечо счёта (например, 100 для 1:100)              |
| `account_trade_mode`                   | `MrpcEnumAccountTradeMode`  | `int`       | Режим торговли: 0=DEMO, 1=CONTEST, 2=REAL               |
| `account_company_name`                 | `string`                    | `str`       | Имя брокера/компании                                  |
| `account_currency`                     | `string`                    | `str`       | Валюта счёта (USD, EUR и т. д.)                    |
| `server_time`                          | `google.protobuf.Timestamp` | `Timestamp` | Текущее время сервера                                  |
| `utc_timezone_server_time_shift_minutes` | `int64`                   | `int`       | Смещение часового пояса сервера от UTC (в минутах)         |
| `account_credit`                       | `double`                    | `float`     | Кредит счёта в валюте депозита                   |
| `account_margin`                       | `double`                    | `float`     | Используемая в данный момент маржа (валюта депозита)             |
| `server_utc_offset_seconds`            | `int32`                     | `int`       | Смещение часового пояса сервера от UTC (в секундах)         |
| `server_time_utc`                      | `google.protobuf.Timestamp` | `Timestamp` | Текущее время сервера в UTC                            |
| `account_margin_free`                  | `double`                    | `float`     | Доступная свободная маржа (валюта депозита)             |
| `account_margin_level`                 | `double`                    | `float`     | Уровень маржи в процентах                              |
| `account_margin_mode`                  | `MrpcEnumAccountMarginMode` | `int`       | Режим расчёта маржи                              |
| `account_trade_allowed`                | `bool`                      | `bool`      | Разрешена ли торговля на счёте            |
| `account_trade_expert`                 | `bool`                      | `bool`      | Разрешена ли торговля советнику (Expert Advisor)            |
| `terminal_connected`                   | `bool`                      | `bool`      | Подключён ли терминал к серверу      |
| `terminal_trade_allowed`               | `bool`                      | `bool`      | Разрешена ли торговля в терминале           |

**Возвращаемое значение:** Метод возвращает объект `AccountSummaryData` со всеми полями, доступными как атрибуты.

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В таблицах показаны упрощённые имена констант для читаемости.
> В Python-коде используйте полный путь enum из модуля account_helper.

### `MrpcEnumAccountTradeMode`

Определено в `mt5-term-api-account-helper.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `MRPC_ACCOUNT_TRADE_MODE_DEMO` | 0 | Демо-счёт |
| `MRPC_ACCOUNT_TRADE_MODE_CONTEST` | 1 | Конкурсный счёт |
| `MRPC_ACCOUNT_TRADE_MODE_REAL` | 2 | Реальный счёт |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Доступ к константам
mode = account_helper_pb2.MRPC_ACCOUNT_TRADE_MODE_DEMO  # = 0
# Проверить режим счёта
if summary.account_trade_mode == account_helper_pb2.MRPC_ACCOUNT_TRADE_MODE_REAL:
    print("Real account - be careful!")
```

---

## 🧩 Примечания и советы

* **РЕКОМЕНДУЕМЫЙ метод:** Это наиболее эффективный способ получить информацию о счёте - используйте его вместо нескольких вызовов `account_info_*`.
* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Требуется подключение:** Перед использованием этого метода необходимо вызвать `connect_by_host_port()` или `connect_by_server_name()`.
* **Информация о марже включена:** Этот метод уже возвращает `account_margin`, `account_margin_free` и `account_margin_level` (а также `account_margin_mode`) — отдельные вызовы `account_info_double()` для них не нужны.
* **Время сервера:** Поле `server_time` - это protobuf Timestamp - конвертируйте с помощью `.ToDatetime()` или `.seconds`.

---

## 🔗 Примеры использования

### 1) Получить полную сводку по счёту

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def main():
    # Создать экземпляр счёта
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="your-server.com:443"
    )

    # Сначала подключиться
    await account.connect_by_server_name("MetaQuotes-Demo")

    try:
        # Установить дедлайн
        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

        # Получить сводку
        summary = await account.account_summary(deadline=deadline)

        # Доступ к полям
        print(f"Account Summary:")
        print(f"  Login: {summary.account_login}")
        print(f"  Name: {summary.account_user_name}")
        print(f"  Balance: ${summary.account_balance:.2f}")
        print(f"  Equity: ${summary.account_equity:.2f}")
        print(f"  Credit: ${summary.account_credit:.2f}")
        print(f"  Currency: {summary.account_currency}")
        print(f"  Leverage: 1:{summary.account_leverage}")
        print(f"  Broker: {summary.account_company_name}")

        # Режим торговли
        mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
        mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")
        print(f"  Mode: {mode}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Вывести отформатированную информацию о счёте

```python
async def print_account_info(account: MT5Account):
    """Print nicely formatted account information"""
    summary = await account.account_summary()

    # Определить тип счёта
    mode_names = {
        0: "DEMO",
        1: "CONTEST",
        2: "REAL"
    }
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    # Рассчитать плавающую прибыль/убыток
    floating_pnl = summary.account_equity - summary.account_balance

    print(f"\n{'='*60}")
    print(f"ACCOUNT INFORMATION")
    print(f"{'='*60}")
    print(f"Account:     #{summary.account_login} ({summary.account_user_name})")
    print(f"Type:        {mode}")
    print(f"Broker:      {summary.account_company_name}")
    print(f"Currency:    {summary.account_currency}")
    print(f"Leverage:    1:{summary.account_leverage}")
    print(f"")
    print(f"Balance:     ${summary.account_balance:,.2f}")
    print(f"Credit:      ${summary.account_credit:,.2f}")
    print(f"Equity:      ${summary.account_equity:,.2f}")
    print(f"Floating:    ${floating_pnl:+,.2f}")
    print(f"{'='*60}\n")

# Использование:
await print_account_info(account)
```

### 3) Проверить состояние счёта

```python
async def check_account_health(account: MT5Account) -> dict:
    """
    Comprehensive account health check.

    Returns:
        Dictionary with health metrics and status
    """
    summary = await account.account_summary()

    # Рассчитать метрики
    balance = summary.account_balance
    equity = summary.account_equity
    floating_pnl = equity - balance
    pnl_percent = (floating_pnl / balance * 100) if balance > 0 else 0

    # Определить состояние
    if summary.account_trade_mode == 0:
        account_type = "DEMO"
    elif summary.account_trade_mode == 2:
        account_type = "REAL"
    else:
        account_type = "CONTEST"

    # Оценка состояния
    if equity > balance and pnl_percent > 5:
        status = "EXCELLENT"
    elif equity > balance:
        status = "HEALTHY"
    elif abs(pnl_percent) < 5:
        status = "NEUTRAL"
    elif pnl_percent < -10:
        status = "CRITICAL"
    else:
        status = "WARNING"

    health = {
        "status": status,
        "account_type": account_type,
        "balance": balance,
        "equity": equity,
        "floating_pnl": floating_pnl,
        "pnl_percent": pnl_percent,
        "leverage": summary.account_leverage,
        "currency": summary.account_currency
    }

    print(f"Account Health: {status}")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Equity: ${equity:,.2f}")
    print(f"  P/L: ${floating_pnl:+,.2f} ({pnl_percent:+.2f}%)")

    return health

# Использование:
health = await check_account_health(account)
if "CRITICAL" in health["status"]:
    print("[WARNING] Account needs attention!")
```

### 4) Получить время сервера

```python
async def get_server_time(account: MT5Account):
    """Get server time and timezone info"""
    summary = await account.account_summary()

    # Текущее время сервера в UTC (однозначное, с часовым поясом)
    from datetime import timezone, timedelta
    server_utc = summary.server_time_utc.ToDatetime(tzinfo=timezone.utc)

    # Смещение часового пояса сервера относительно UTC
    tz_offset_minutes = summary.utc_timezone_server_time_shift_minutes
    tz_offset_hours = tz_offset_minutes / 60

    # Локальное время сервера = UTC сервера + смещение
    server_local = server_utc + timedelta(minutes=tz_offset_minutes)

    print(f"Server time (UTC): {server_utc}")
    print(f"UTC offset: {tz_offset_hours:+.1f} hours")
    print(f"Server local time: {server_local}")

    return server_utc

# Использование:
server_time = await get_server_time(account)
```

### 5) Проверить счёт перед торговлей

```python
async def validate_for_trading(account: MT5Account) -> bool:
    """
    Validate account is ready for trading.

    Returns:
        True if account passes all checks
    """
    summary = await account.account_summary()

    # Проверка 1: Минимальный баланс
    min_balance = 100
    if summary.account_balance < min_balance:
        print(f"[ERROR] Balance too low: ${summary.account_balance:.2f} < ${min_balance}")
        return False

    # Проверка 2: Средства (equity) > Баланс (нет значительных убытков)
    if summary.account_equity < summary.account_balance * 0.5:
        pnl = summary.account_equity - summary.account_balance
        print(f"[ERROR] Heavy losses: ${pnl:.2f}")
        return False

    # Проверка 3: Разумное кредитное плечо
    if summary.account_leverage < 10 or summary.account_leverage > 500:
        print(f"[WARNING] Unusual leverage: 1:{summary.account_leverage}")

    # Проверка 4: Поддерживаемая валюта
    supported_currencies = ["USD", "EUR", "GBP"]
    if summary.account_currency not in supported_currencies:
        print(f"[WARNING] Unsupported currency: {summary.account_currency}")

    print(f"[OK] Account validation passed:")
    print(f"   Balance: ${summary.account_balance:.2f}")
    print(f"   Equity: ${summary.account_equity:.2f}")
    print(f"   Leverage: 1:{summary.account_leverage}")

    return True

# Использование:
if await validate_for_trading(account):
    # Начать торговлю
    pass
else:
    print("Cannot trade on this account")
```

### 6) Логировать начало сессии

```python
import logging
from datetime import datetime

async def log_session_start(account: MT5Account):
    """Log session start with full account details"""
    summary = await account.account_summary()

    # Настроить логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Получить название режима
    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    # Логировать информацию о сессии
    logging.info("=" * 60)
    logging.info("TRADING SESSION STARTED")
    logging.info(f"Account: #{summary.account_login} ({summary.account_user_name})")
    logging.info(f"Broker: {summary.account_company_name}")
    logging.info(f"Mode: {mode}")
    logging.info(f"Balance: {summary.account_balance:.2f} {summary.account_currency}")
    logging.info(f"Leverage: 1:{summary.account_leverage}")

    # Время сервера
    server_time = summary.server_time.ToDatetime()
    logging.info(f"Server Time: {server_time}")
    logging.info("=" * 60)

# Использование:
await log_session_start(account)
```

### 7) Мониторинг средств (equity) счёта

```python
async def monitor_equity(account: MT5Account, interval: float = 10.0):
    """
    Monitor account equity changes.

    Args:
        account: MT5Account instance
        interval: Update interval in seconds
    """
    previous_equity = None

    while True:
        try:
            summary = await account.account_summary()

            equity = summary.account_equity
            balance = summary.account_balance
            floating = equity - balance

            # Рассчитать изменение
            if previous_equity is not None:
                change = equity - previous_equity
                change_pct = (change / previous_equity * 100) if previous_equity > 0 else 0

                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Equity: ${equity:,.2f} | "
                      f"Floating: ${floating:+,.2f} | "
                      f"Change: ${change:+.2f} ({change_pct:+.2f}%)")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Equity: ${equity:,.2f} | "
                      f"Floating: ${floating:+,.2f}")

            previous_equity = equity

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)

# Использование:
# await monitor_equity(account, interval=10.0)  # Обновление каждые 10 секунд
```

### 8) Сравнить несколько счетов

```python
from dataclasses import dataclass

@dataclass
class AccountSummary:
    login: int
    name: str
    balance: float
    equity: float
    leverage: int
    currency: str
    mode: str

async def compare_accounts(accounts: list[MT5Account]) -> list[AccountSummary]:
    """
    Get summaries for multiple accounts.

    Args:
        accounts: List of MT5Account instances

    Returns:
        List of AccountSummary objects
    """
    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    summaries = []

    for account in accounts:
        summary = await account.account_summary()

        summaries.append(AccountSummary(
            login=summary.account_login,
            name=summary.account_user_name,
            balance=summary.account_balance,
            equity=summary.account_equity,
            leverage=summary.account_leverage,
            currency=summary.account_currency,
            mode=mode_names.get(summary.account_trade_mode, "UNKNOWN")
        ))

    # Вывести сравнение
    print("\nAccount Comparison:")
    print("-" * 80)
    for s in summaries:
        pnl = s.equity - s.balance
        print(f"#{s.login:10} | {s.name:20} | {s.mode:8} | "
              f"${s.balance:10,.2f} | ${s.equity:10,.2f} | ${pnl:+10,.2f}")
    print("-" * 80)

    return summaries

# Использование:
# account1 = MT5Account(...)
# account2 = MT5Account(...)
# summaries = await compare_accounts([account1, account2])
```

---

## Распространённые паттерны

### Проверка инициализации счёта

```python
async def initialize_account(account: MT5Account):
    """Initialize and validate account connection"""
    # Подключиться
    await account.connect_by_server_name("MetaQuotes-Demo")

    # Получить сводку, чтобы проверить подключение
    summary = await account.account_summary()

    print(f"[OK] Connected to account #{summary.account_login}")
    print(f"   Balance: ${summary.account_balance:.2f} {summary.account_currency}")

    # Вернуть сводку для дальнейшего использования
    return summary
```

### Оценка риска

```python
async def assess_trading_risk(account: MT5Account) -> str:
    """Assess trading risk level"""
    summary = await account.account_summary()

    # Рассчитать факторы риска
    balance = summary.account_balance
    equity = summary.account_equity
    leverage = summary.account_leverage

    # Оценка риска
    if leverage > 200:
        risk = "HIGH"
    elif leverage > 100:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    # Проверить текущие убытки
    if equity < balance * 0.9:
        risk = "HIGH"

    print(f"Risk Assessment: {risk}")
    print(f"  Leverage: 1:{leverage}")
    print(f"  Balance: ${balance:.2f}")
    print(f"  Equity: ${equity:.2f}")

    return risk
```

---

## 📚 См. также

* [account_info_double](./account_info_double.md) - Получить определённые свойства счёта типа double (маржа и т. д.)
* [account_info_integer](./account_info_integer.md) - Получить определённые целочисленные свойства счёта
* [account_info_string](./account_info_string.md) - Получить определённые строковые свойства счёта
