# Получение строковых свойств счёта

> **Запрос:** определённое свойство счёта строкового типа из терминала **MT5** с помощью идентификатора свойства.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.account_info_string(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountInformation`
* **Proto-определение:** `AccountInfoString` (определено в `mt5-term-api-account-information.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountInformation`
* **Метод:** `AccountInfoString(AccountInfoStringRequest) -> AccountInfoStringReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountInformationStub.AccountInfoString(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить определённое свойство счёта строкового типа по ID (имя, сервер, валюта, компания).
* **Зачем это нужно.** Получить отдельное текстовое свойство счёта, не запрашивая все данные. Полезно для логирования и конфигурации.
* **Когда использовать.** Используйте `account_summary()` для нескольких свойств. Используйте этот метод для запросов одного свойства.

---

## 🎯 Назначение

Используйте его для запроса определённых строковых свойств счёта:

* Получить имя владельца счёта
* Получить имя торгового сервера
* Получить валюту счёта (USD, EUR и т. д.)
* Получить имя брокера/компании
* Проверить подключение к серверу
* Логировать детали счёта

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [account_info_string - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW.md)**

---

## Сигнатура метода

```python
async def account_info_string(
    self,
    property_id: account_info_pb2.AccountInfoStringPropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> str
```

**Сообщение запроса:**

```protobuf
message AccountInfoStringRequest {
  AccountInfoStringPropertyType property_id = 1;
}
```

**Сообщение ответа:**

```protobuf
message AccountInfoStringReply {
  oneof response {
    AccountInfoStringData data = 1;
    Error error = 2;
  }
}

message AccountInfoStringData {
  string requested_value = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                               | Описание                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoStringPropertyType` (enum) | Идентификатор свойства, указывающий, какое свойство получить |
| `deadline`    | `datetime` (необязательно)             | Дедлайн для gRPC-вызова (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                           |

**Варианты дедлайна:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. С дедлайном (рекомендуется)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
    deadline=deadline
)

# 2. С событием отмены
cancel_event = asyncio.Event()
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
    cancellation_event=cancel_event
)

# 3. Без дедлайна (используется таймаут по умолчанию, если настроен)
value = await account.account_info_string(
    property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
)
```

---

## ⬆️ Выход

| Поле              | Тип      | Python-тип  | Описание                                      |
| ----------------- | -------- | ----------- | ------------------------------------------------ |
| `requested_value` | `string` | `str`       | Значение запрошенного свойства счёта      |

**Возвращаемое значение:** Метод напрямую возвращает `str` (извлекается из `AccountInfoStringData.requested_value`).

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В Python-коде следует использовать полный путь класса enum для типобезопасности и ясности:
>
> **Рекомендуется:** `account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY`
> **Также допустимо:** `account_info_pb2.ACCOUNT_CURRENCY` (прямой доступ)
>
> Мы рекомендуем **полный формат** для лучшей поддержки IDE и чтобы избежать путаницы между разными типами свойств.

### `AccountInfoStringPropertyType`

Определено в `mt5-term-api-account-information.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `ACCOUNT_NAME` | 0 | Имя клиента |
| `ACCOUNT_SERVER` | 1 | Имя торгового сервера |
| `ACCOUNT_CURRENCY` | 2 | Валюта счёта (USD, EUR и т. д.) |
| `ACCOUNT_COMPANY` | 3 | Имя компании, обслуживающей счёт |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Рекомендуется: использовать полный путь класса enum
property_id = account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY  # = 2

# Также допустимо: прямой доступ (но менее ясно)
property_id = account_info_pb2.ACCOUNT_CURRENCY  # = 2
```

---

## 🧩 Примечания и советы

* **Предпочитайте account_summary:** Для нескольких свойств используйте вместо этого `account_summary()`, чтобы избежать нескольких обращений к серверу.
* **Требуется подключение:** Перед использованием этого метода необходимо вызвать `connect_by_host_port()` или `connect_by_server_name()`.
* **Формат валюты:** Валюта возвращается в виде 3-буквенного кода (USD, EUR, GBP и т. д.).

---

## 🔗 Примеры использования

### 1) Получить валюту счёта

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

        # Получить валюту
        currency = await account.account_info_string(
            property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
            deadline=deadline
        )

        print(f"Account Currency: {currency}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Получить имя владельца счёта

```python
async def get_account_name(account: MT5Account) -> str:
    """Get account owner name"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    name = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline=deadline
    )

    return name

# Использование:
name = await get_account_name(account)
print(f"Account Name: {name}")
```

### 3) Получить имя торгового сервера

```python
async def get_server_name(account: MT5Account) -> str:
    """Get trading server name"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    return server

# Использование:
server = await get_server_name(account)
print(f"Trading Server: {server}")
```

### 4) Получить имя компании-брокера

```python
async def get_broker_name(account: MT5Account) -> str:
    """Get broker/company name"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    company = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline=deadline
    )

    return company

# Использование:
broker = await get_broker_name(account)
print(f"Broker: {broker}")
```

### 5) Логировать детали счёта

```python
async def log_account_details(account: MT5Account):
    """Log all string account properties"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    # Получить все строковые свойства
    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    # Логировать детали
    print(f"=" * 50)
    print(f"Account Details:")
    print(f"  Owner: {name}")
    print(f"  Server: {server}")
    print(f"  Currency: {currency}")
    print(f"  Broker: {company}")
    print(f"=" * 50)

# Использование:
await log_account_details(account)
```

### 6) Проверить подключение к серверу

```python
async def verify_server_connection(account: MT5Account, expected_server: str) -> bool:
    """
    Verify we're connected to the expected server.

    Args:
        account: MT5Account instance
        expected_server: Expected server name

    Returns:
        True if connected to correct server
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    server = await account.account_info_string(
        property_id=account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline=deadline
    )

    if server.lower() != expected_server.lower():
        print(f"[WARNING] Connected to {server}, expected {expected_server}")
        return False

    print(f"[OK] Confirmed: Connected to {server}")
    return True

# Использование:
if not await verify_server_connection(account, "MetaQuotes-Demo"):
    raise RuntimeError("Wrong server!")
```

### 7) Форматирование на основе валюты

```python
async def format_balance(account: MT5Account, balance: float) -> str:
    """
    Format balance with account currency symbol.

    Args:
        account: MT5Account instance
        balance: Balance amount

    Returns:
        Formatted balance string
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    # Сопоставить коды валют с символами
    currency_symbols = {
        "USD": "$",
        "EUR": "EUR",
        "GBP": "GBP",
        "JPY": "JPY",
        "CHF": "CHF",
        "AUD": "A$",
        "CAD": "C$"
    }

    symbol = currency_symbols.get(currency, currency + " ")

    # Форматировать в зависимости от валюты
    if currency == "JPY":
        # JPY не использует десятичные знаки
        return f"{symbol}{balance:.0f}"
    else:
        return f"{symbol}{balance:.2f}"

# Использование:
balance = 10000.50
formatted = await format_balance(account, balance)
print(f"Balance: {formatted}")  # Вывод: Balance: $10000.50
```

### 8) Сформировать заголовок сессии

```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class SessionInfo:
    timestamp: str
    account_name: str
    broker: str
    server: str
    currency: str

async def get_session_info(account: MT5Account) -> SessionInfo:
    """Get comprehensive session information for logging"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    # Получить все строковые свойства
    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY,
        deadline
    )

    return SessionInfo(
        timestamp=datetime.now().isoformat(),
        account_name=name,
        broker=company,
        server=server,
        currency=currency
    )

# Использование:
session = await get_session_info(account)
print(f"Session started: {session.timestamp}")
print(f"Account: {session.account_name}")
print(f"Broker: {session.broker} ({session.server})")
print(f"Currency: {session.currency}")
```

---

## Распространённые паттерны

### Идентификация счёта

```python
async def get_account_identifier(account: MT5Account) -> str:
    """
    Generate unique account identifier for logging.

    Returns:
        Identifier string: "name@server (broker)"
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    name = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME,
        deadline
    )

    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
        deadline
    )

    company = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY,
        deadline
    )

    identifier = f"{name}@{server} ({company})"
    return identifier

# Использование:
account_id = await get_account_identifier(account)
print(f"Trading as: {account_id}")
# Вывод: Trading as: John Doe@MetaQuotes-Demo (MetaQuotes Software Corp.)
```

### Валидатор валюты

```python
async def validate_account_currency(
    account: MT5Account,
    allowed_currencies: list[str]
) -> bool:
    """
    Validate account currency is in allowed list.

    Args:
        account: MT5Account instance
        allowed_currencies: List of allowed currency codes (e.g., ["USD", "EUR"])

    Returns:
        True if currency is allowed
    """
    currency = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
    )

    if currency not in allowed_currencies:
        print(f"[ERROR] Currency {currency} not allowed. Allowed: {allowed_currencies}")
        return False

    print(f"[OK] Currency {currency} is valid")
    return True

# Использование:
if not await validate_account_currency(account, ["USD", "EUR"]):
    raise ValueError("Account currency not supported")
```

### Проверка окружения сервера

```python
async def get_environment(account: MT5Account) -> str:
    """
    Determine environment (production/demo) based on server name.

    Returns:
        "PRODUCTION", "DEMO", or "UNKNOWN"
    """
    server = await account.account_info_string(
        account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER
    )

    server_lower = server.lower()

    if "demo" in server_lower:
        return "DEMO"
    elif "real" in server_lower or "live" in server_lower:
        return "PRODUCTION"
    else:
        return "UNKNOWN"

# Использование:
env = await get_environment(account)
print(f"Environment: {env}")

if env == "PRODUCTION":
    print("[WARNING] Trading on PRODUCTION server!")
```

---

## 📚 См. также

* [account_summary](./account_summary.md) - Получить все свойства счёта за один вызов (РЕКОМЕНДУЕТСЯ)
* [account_info_double](./account_info_double.md) - Получить определённые свойства счёта типа double
* [account_info_integer](./account_info_integer.md) - Получить определённые целочисленные свойства счёта
