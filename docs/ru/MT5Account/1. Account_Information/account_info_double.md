# Получение свойств счёта типа double

> **Запрос:** определённое свойство счёта типа double из терминала **MT5** с помощью идентификатора свойства.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.account_info_double(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountInformation`
* **Proto-определение:** `AccountInfoDouble` (определено в `mt5-term-api-account-information.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountInformation`
* **Метод:** `AccountInfoDouble(AccountInfoDoubleRequest) -> AccountInfoDoubleReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountInformationStub.AccountInfoDouble(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить определённое свойство счёта типа double по ID (баланс, средства (equity), маржа и т. д.).
* **Зачем это нужно.** Получить отдельную метрику счёта, не запрашивая все данные. Полезно для точечных проверок.
* **Когда использовать.** Используйте `account_summary()` для нескольких свойств. Используйте этот метод для запросов одного свойства.

---

## 🎯 Назначение

Используйте его для запроса определённых числовых свойств счёта:

* Проверить баланс счёта перед торговлей
* Отслеживать использование маржи и уровень маржи
* Проверить наличие свободной маржи
* Отслеживать плавающую прибыль/убыток
* Отслеживать уровни margin call и stop out

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [account_info_double - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW.md)**

---

## Сигнатура метода

```python
async def account_info_double(
    self,
    property_id: account_info_pb2.AccountInfoDoublePropertyType,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> float
```

**Сообщение запроса:**

```protobuf
message AccountInfoDoubleRequest {
  AccountInfoDoublePropertyType property_id = 1;
}
```

**Сообщение ответа:**

```protobuf
message AccountInfoDoubleReply {
  oneof response {
    AccountInfoDoubleData data = 1;
    Error error = 2;
  }
}

message AccountInfoDoubleData {
  double requested_value = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                               | Описание                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `property_id` | `AccountInfoDoublePropertyType` (enum) | Идентификатор свойства, указывающий, какое свойство получить |
| `deadline`    | `datetime` (необязательно)             | Дедлайн для gRPC-вызова (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                           |

**Варианты дедлайна:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. С дедлайном (рекомендуется)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
value = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    deadline=deadline
)

# 2. С событием отмены
cancel_event = asyncio.Event()
value = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    cancellation_event=cancel_event
)

# Позже: cancel_event.set()

# 3. Без дедлайна (используется таймаут по умолчанию, если настроен)
value = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE
)
```

---

## ⬆️ Выход

| Поле              | Тип       | Python-тип  | Описание                                      |
| ----------------- | --------- | ----------- | ------------------------------------------------ |
| `requested_value` | `double`  | `float`     | Значение запрошенного свойства счёта      |

**Возвращаемое значение:** Метод напрямую возвращает `float` (извлекается из `AccountInfoDoubleData.requested_value`).

---

## 🧱 Связанные enum (из proto)

> **💡 Примечание:** В таблицах показаны упрощённые имена констант для читаемости.
> В Python-коде можно использовать как полную, так и короткую форму:
>
> **Полный формат:** `account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE`
> **Короткий формат:** `account_info_pb2.ACCOUNT_BALANCE`
>
> Обе формы допустимы в Python protobuf. Для простоты мы рекомендуем **короткий формат**.

### `AccountInfoDoublePropertyType`

Определено в `mt5-term-api-account-information.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `ACCOUNT_BALANCE` | 0 | Баланс счёта в валюте депозита |
| `ACCOUNT_CREDIT` | 1 | Кредит счёта в валюте депозита |
| `ACCOUNT_PROFIT` | 2 | Текущая прибыль счёта в валюте депозита |
| `ACCOUNT_EQUITY` | 3 | Средства (equity) счёта в валюте депозита |
| `ACCOUNT_MARGIN` | 4 | Использованная маржа счёта в валюте депозита |
| `ACCOUNT_MARGIN_FREE` | 5 | Свободная маржа счёта в валюте депозита |
| `ACCOUNT_MARGIN_LEVEL` | 6 | Уровень маржи счёта в процентах |
| `ACCOUNT_MARGIN_SO_CALL` | 7 | Уровень margin call (в % или валюте депозита) |
| `ACCOUNT_MARGIN_SO_SO` | 8 | Уровень margin stop out (в % или валюте депозита) |
| `ACCOUNT_MARGIN_INITIAL` | 9 | Начальная маржа (зарезервирована под отложенные ордера) |
| `ACCOUNT_MARGIN_MAINTENANCE` | 10 | Поддерживающая маржа (минимально зарезервированные средства (equity)) |
| `ACCOUNT_ASSETS` | 11 | Текущие активы счёта |
| `ACCOUNT_LIABILITIES` | 12 | Текущие обязательства счёта |
| `ACCOUNT_COMMISSION_BLOCKED` | 13 | Текущая сумма заблокированной комиссии |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Доступ к константам напрямую
property_id = account_info_pb2.ACCOUNT_BALANCE  # = 0
# или использовать полное имя enum
property_id = account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE  # = 0
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Типы свойств:** Уровни margin call и stop out могут быть в процентах или в валюте депозита в зависимости от настроек счёта.
* **Потокобезопасность:** Все async-методы безопасно вызывать параллельно из нескольких asyncio-задач.

---

## 🔗 Примеры использования

### 1) Получить баланс счёта

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

        # Получить баланс
        balance = await account.account_info_double(
            property_id=account_info_pb2.ACCOUNT_BALANCE,
            deadline=deadline
        )

        print(f"Account Balance: ${balance:.2f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Получить текущие средства (equity)

```python
async def get_equity(account: MT5Account) -> float:
    """Get current account equity"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    equity = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_EQUITY,
        deadline=deadline
    )

    return equity

# Использование:
equity = await get_equity(account)
print(f"Current Equity: ${equity:.2f}")
```

### 3) Проверить уровень маржи перед торговлей

```python
async def check_margin_level(account: MT5Account, min_level: float = 200.0) -> bool:
    """
    Check if margin level is above minimum threshold.

    Args:
        account: MT5Account instance
        min_level: Minimum required margin level (%)

    Returns:
        True if margin level is sufficient

    Raises:
        ValueError: If margin level is below minimum
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    margin_level = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    print(f"Margin Level: {margin_level:.2f}%")

    if margin_level < min_level:
        raise ValueError(
            f"Margin level {margin_level:.2f}% is below minimum {min_level:.2f}%"
        )

    return True

# Использование:
try:
    await check_margin_level(account, min_level=200.0)
    print("[OK] Safe to trade")
except ValueError as e:
    print(f"[ERROR] Cannot trade: {e}")
```

### 4) Получить свободную маржу

```python
async def get_free_margin(account: MT5Account) -> float:
    """Get available free margin"""
    # Без дедлайна - используется таймаут по умолчанию
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    return free_margin

# Использование:
free_margin = await get_free_margin(account)
print(f"Free Margin: ${free_margin:.2f}")
```

### 5) Мониторинг плавающей прибыли/убытка

```python
async def monitor_profit(account: MT5Account, interval: float = 5.0):
    """Monitor floating P/L every N seconds"""
    while True:
        try:
            deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

            profit = await account.account_info_double(
                property_id=account_info_pb2.ACCOUNT_PROFIT,
                deadline=deadline
            )

            sign = "+" if profit >= 0 else ""
            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] Floating P/L: {sign}${profit:.2f}")

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(interval)

# Использование:
# await monitor_profit(account, interval=5.0)  # Обновление каждые 5 секунд
```

### 6) Проверить несколько свойств последовательно

```python
from dataclasses import dataclass

@dataclass
class MarginInfo:
    used_margin: float
    free_margin: float
    margin_level: float

async def get_margin_info(account: MT5Account) -> MarginInfo:
    """Get comprehensive margin information"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    # Получить использованную маржу
    used_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN,
        deadline=deadline
    )

    # Получить свободную маржу
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE,
        deadline=deadline
    )

    # Получить уровень маржи
    margin_level = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    return MarginInfo(
        used_margin=used_margin,
        free_margin=free_margin,
        margin_level=margin_level
    )

# Использование:
info = await get_margin_info(account)
print(f"Margin Info:")
print(f"  Used: ${info.used_margin:.2f}")
print(f"  Free: ${info.free_margin:.2f}")
print(f"  Level: {info.margin_level:.2f}%")

# Примечание: Для лучшей производительности используйте вместо этого account_summary()
# чтобы получить все свойства за один вызов
```

### 7) С событием отмены

```python
async def get_balance_cancellable(account: MT5Account, cancel_event: asyncio.Event) -> float:
    """Get balance with cancellation support"""
    try:
        balance = await account.account_info_double(
            property_id=account_info_pb2.ACCOUNT_BALANCE,
            cancellation_event=cancel_event
        )
        return balance
    except asyncio.CancelledError:
        print("Operation cancelled")
        raise

# Использование:
cancel_event = asyncio.Event()

# Запустить операцию
task = asyncio.create_task(get_balance_cancellable(account, cancel_event))

# Отменить через 1 секунду
await asyncio.sleep(1)
cancel_event.set()

try:
    balance = await task
except asyncio.CancelledError:
    print("Cancelled by user")
```

---

## 🔧 Распространённые паттерны

### Безопасная проверка для торговли

```python
async def can_trade(account: MT5Account, required_margin: float) -> bool:
    """
    Check if account has enough free margin to trade.

    Args:
        account: MT5Account instance
        required_margin: Required margin for the trade

    Returns:
        True if sufficient margin available
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE,
        deadline=deadline
    )

    if free_margin < required_margin:
        print(f"[ERROR] Insufficient margin: need ${required_margin:.2f}, have ${free_margin:.2f}")
        return False

    print(f"[OK] Sufficient margin: ${free_margin:.2f} available")
    return True
```

### Система предупреждений об уровне маржи

```python
async def check_margin_warning(account: MT5Account):
    """Check margin level and warn if too low"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    level = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline=deadline
    )

    if level < 100:
        print(f"[CRITICAL] Margin level {level:.2f}% - Stop out imminent!")
    elif level < 200:
        print(f"[WARNING] Margin level {level:.2f}% - Margin call zone")
    elif level < 500:
        print(f"[CAUTION] Margin level {level:.2f}% - Monitor closely")
    else:
        print(f"[OK] Margin level {level:.2f}%")
```

### Проверка состояния счёта

```python
async def check_account_health(account: MT5Account):
    """Comprehensive account health check"""
    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Получить все критичные метрики
    balance = await account.account_info_double(
        account_info_pb2.ACCOUNT_BALANCE,
        deadline
    )

    equity = await account.account_info_double(
        account_info_pb2.ACCOUNT_EQUITY,
        deadline
    )

    profit = await account.account_info_double(
        account_info_pb2.ACCOUNT_PROFIT,
        deadline
    )

    margin_level = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_LEVEL,
        deadline
    )

    print(f"Account Health Report:")
    print(f"  Balance: ${balance:.2f}")
    print(f"  Equity: ${equity:.2f}")
    print(f"  Floating P/L: ${profit:+.2f}")
    print(f"  Margin Level: {margin_level:.2f}%")

    # Оценка состояния
    if margin_level > 500 and equity >= balance:
        print("  Status: [HEALTHY]")
    elif margin_level > 200:
        print("  Status: [MODERATE]")
    else:
        print("  Status: [RISKY]")
```

---

## 📚 См. также

* [account_summary](./account_summary.md) - Получить все свойства счёта за один вызов (РЕКОМЕНДУЕТСЯ)
* [account_info_integer](./account_info_integer.md) - Получить определённые целочисленные свойства счёта
* [account_info_string](./account_info_string.md) - Получить определённые строковые свойства счёта
