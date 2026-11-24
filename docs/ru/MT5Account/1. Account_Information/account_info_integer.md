# Получение целочисленных свойств счёта

> **Запрос:** определённое свойство счёта целочисленного типа из терминала **MT5** с помощью идентификатора свойства.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.account_info_integer(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountInformation`
* **Proto-определение:** `AccountInfoInteger` (определено в `mt5-term-api-account-information.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountInformation`
* **Метод:** `AccountInfoInteger(AccountInfoIntegerRequest) -> AccountInfoIntegerReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountInformationStub.AccountInfoInteger(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить определённое свойство счёта целочисленного типа по ID (логин, кредитное плечо, режим торговли и т. д.).
* **Зачем это нужно.** Получить отдельную настройку счёта, не запрашивая все данные. Полезно для проверок конфигурации.
* **Когда использовать.** Используйте `account_summary()` для нескольких свойств. Используйте этот метод для запросов одного свойства.

---

## 🎯 Назначение

Используйте его для запроса определённых целочисленных свойств счёта:

* Получить номер логина счёта
* Проверить кредитное плечо счёта
* Проверить разрешения на торговлю (разрешена торговля, разрешён эксперт)
* Проверить режим торговли счёта (demo/real/contest)
* Получить лимит максимального количества отложенных ордеров
* Проверить режим расчёта маржи
* Проверить настройки FIFO-закрытия и хеджирования

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [account_info_integer - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW.md)**

---

## Сигнатура метода

```python
async def account_info_integer(
    self,
    property_id: account_info_pb2.AccountInfoIntegerPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> int
```

**Сообщение запроса:**

```protobuf
message AccountInfoIntegerRequest {
  AccountInfoIntegerPropertyType property_id = 1;
}
```

**Сообщение ответа:**

```protobuf
message AccountInfoIntegerReply {
  oneof response {
    AccountInfoIntegerData data = 1;
    Error error = 2;
  }
}

message AccountInfoIntegerData {
  int64 requested_value = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                               | Описание                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoIntegerPropertyType` (enum) | Идентификатор свойства, указывающий, какое свойство получить |
| `deadline`    | `datetime` (необязательно)             | Дедлайн для gRPC-вызова (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                           |

**Варианты дедлайна:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. С дедлайном (рекомендуется)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
value = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE,
    deadline=deadline
)

# 2. С событием отмены
cancel_event = asyncio.Event()
value = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE,
    cancellation_event=cancel_event
)

# 3. Без дедлайна (используется таймаут по умолчанию, если настроен)
value = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE
)
```

---

## ⬆️ Выход

| Поле              | Тип     | Python-тип  | Описание                                      |
| ----------------- | ------- | ----------- | ------------------------------------------------ |
| `requested_value` | `int64` | `int`       | Значение запрошенного свойства счёта      |

**Возвращаемое значение:** Метод напрямую возвращает `int` (извлекается из `AccountInfoIntegerData.requested_value`).

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В таблицах показаны упрощённые имена констант для читаемости.
> В Python-коде можно использовать как полную, так и короткую форму:
>
> **Полный формат:** `account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE`
> **Короткий формат:** `account_info_pb2.ACCOUNT_LEVERAGE`
>
> Обе формы допустимы в Python protobuf. Для простоты мы рекомендуем **короткий формат**.

### `AccountInfoIntegerPropertyType`

Определено в `mt5-term-api-account-information.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `ACCOUNT_LOGIN` | 0 | Номер счёта |
| `ACCOUNT_TRADE_MODE` | 1 | Режим торговли счёта (demo/real/contest) |
| `ACCOUNT_LEVERAGE` | 2 | Кредитное плечо счёта |
| `ACCOUNT_LIMIT_ORDERS` | 3 | Максимально допустимое количество активных отложенных ордеров |
| `ACCOUNT_MARGIN_SO_MODE` | 4 | Режим задания минимально допустимой маржи |
| `ACCOUNT_TRADE_ALLOWED` | 5 | Разрешена торговля для текущего счёта |
| `ACCOUNT_TRADE_EXPERT` | 6 | Разрешена торговля для советника (Expert Advisor) |
| `ACCOUNT_MARGIN_MODE` | 7 | Режим расчёта маржи |
| `ACCOUNT_CURRENCY_DIGITS` | 8 | Количество знаков после запятой для валюты счёта |
| `ACCOUNT_FIFO_CLOSE` | 9 | Флаг того, что позиция может быть закрыта только по правилу FIFO |
| `ACCOUNT_HEDGE_ALLOWED` | 10 | Хеджирование разрешено |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Доступ к константам напрямую
property_id = account_info_pb2.ACCOUNT_LEVERAGE  # = 2
# или использовать полное имя enum
property_id = account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE  # = 2
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Предпочитайте account_summary:** Для нескольких свойств используйте вместо этого `account_summary()`, чтобы избежать нескольких обращений к серверу.
* **Требуется подключение:** Перед использованием этого метода необходимо вызвать `connect_by_host_port()` или `connect_by_server_name()`.
* **Булевы значения:** Такие свойства, как `TRADE_ALLOWED`, `TRADE_EXPERT`, `FIFO_CLOSE`, `HEDGE_ALLOWED`, возвращают 1 (true) или 0 (false).
* **Потокобезопасность:** Все async-методы безопасно вызывать параллельно из нескольких asyncio-задач.
* **Обработка UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не указан.
  Для явного управления (например, в сценариях стриминга) передайте `id_=uuid4()` в конструктор.

---

## 🔗 Примеры использования

### 1) Получить кредитное плечо счёта

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

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

        # Получить кредитное плечо
        leverage = await account.account_info_integer(
            property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
            deadline=deadline
        )

        print(f"Account Leverage: 1:{leverage}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Получить номер логина счёта

```python
async def get_account_login(account: MT5Account) -> int:
    """Get account login number"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    login = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LOGIN,
        deadline=deadline
    )

    return login

# Использование:
login = await get_account_login(account)
print(f"Account Login: {login}")
```

### 3) Проверить, разрешена ли торговля

```python
async def is_trading_allowed(account: MT5Account) -> bool:
    """
    Check if trading is allowed for this account.

    Returns:
        True if trading is allowed, False otherwise
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    trade_allowed = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
        deadline=deadline
    )

    # Возвращает 1 (true) или 0 (false)
    is_allowed = bool(trade_allowed)

    if is_allowed:
        print("[OK] Trading is allowed")
    else:
        print("[ERROR] Trading is disabled")

    return is_allowed

# Использование:
if await is_trading_allowed(account):
    # Разместить ордера
    pass
else:
    print("Cannot trade on this account")
```

### 4) Проверить разрешения для советника (Expert Advisor)

```python
async def is_ea_allowed(account: MT5Account) -> bool:
    """Check if Expert Advisors are allowed to trade"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    ea_allowed = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_EXPERT,
        deadline=deadline
    )

    return bool(ea_allowed)

# Использование:
if await is_ea_allowed(account):
    print("[OK] Expert Advisors can trade")
else:
    print("[ERROR] Expert Advisors are disabled")
```

### 5) Получить лимит максимального количества отложенных ордеров

```python
async def get_max_pending_orders(account: MT5Account) -> int:
    """Get maximum allowed number of pending orders"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    limit = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LIMIT_ORDERS,
        deadline=deadline
    )

    return limit

# Использование:
max_orders = await get_max_pending_orders(account)
print(f"Maximum pending orders: {max_orders}")

if max_orders == 0:
    print("[WARNING] No limit on pending orders (or unlimited)")
```

### 6) Проверить тип счёта (demo/real/contest)

```python
async def get_account_type(account: MT5Account) -> str:
    """
    Get account trade mode.

    Returns:
        "DEMO", "CONTEST", or "REAL"
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    trade_mode = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_MODE,
        deadline=deadline
    )

    # Сопоставить с читаемыми названиями
    mode_map = {
        0: "DEMO",
        1: "CONTEST",
        2: "REAL"
    }

    mode_name = mode_map.get(trade_mode, f"UNKNOWN ({trade_mode})")
    print(f"Account Type: {mode_name}")

    return mode_name

# Использование:
account_type = await get_account_type(account)

if account_type == "DEMO":
    print("[WARNING] Running on demo account")
elif account_type == "REAL":
    print("[CRITICAL] Running on real account - be careful!")
```

### 7) Проверить настройки хеджирования

```python
async def check_hedging_settings(account: MT5Account):
    """Check if hedging and FIFO close are enabled"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Проверить, разрешено ли хеджирование
    hedge_allowed = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_HEDGE_ALLOWED,
        deadline=deadline
    )

    # Проверить правило FIFO-закрытия
    fifo_close = await account.account_info_integer(
        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_FIFO_CLOSE,
        deadline=deadline
    )

    print(f"Hedging Settings:")
    print(f"  Hedging allowed: {'Yes' if hedge_allowed else 'No'}")
    print(f"  FIFO close: {'Enabled' if fifo_close else 'Disabled'}")

    return {
        "hedge_allowed": bool(hedge_allowed),
        "fifo_close": bool(fifo_close)
    }

# Использование:
settings = await check_hedging_settings(account)

if settings["hedge_allowed"]:
    print("[OK] Can open opposite positions on same symbol")
else:
    print("[INFO] Cannot hedge - only netting mode")
```

---

## Распространённые паттерны

### Проверка перед торговлей

```python
async def validate_account_for_trading(account: MT5Account) -> bool:
    """
    Validate account is ready for trading.

    Returns:
        True if account is ready to trade
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Проверить, разрешена ли торговля
    trade_allowed = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,
        deadline
    )

    if not trade_allowed:
        print("[ERROR] Trading is disabled on this account")
        return False

    # Проверить, что кредитное плечо разумное
    leverage = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,
        deadline
    )

    if leverage < 1:
        print("[ERROR] Invalid leverage setting")
        return False

    print(f"[OK] Account ready to trade (Leverage: 1:{leverage})")
    return True
```

### Проверка типа счёта

```python
async def require_demo_account(account: MT5Account):
    """Ensure we're running on demo account (safety check)"""
    trade_mode = await account.account_info_integer(
        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_MODE
    )

    if trade_mode != 0:  # 0 = DEMO
        raise RuntimeError(
            f"[CRITICAL] This script requires DEMO account! Current mode: {trade_mode}"
        )

    print("[OK] Confirmed: Running on DEMO account")
```

---

## 📚 См. также

* [account_summary](./account_summary.md) - Получить все свойства счёта за один вызов (РЕКОМЕНДУЕТСЯ)
* [account_info_double](./account_info_double.md) - Получить определённые свойства счёта типа double
* [account_info_string](./account_info_string.md) - Получить определённые строковые свойства счёта
