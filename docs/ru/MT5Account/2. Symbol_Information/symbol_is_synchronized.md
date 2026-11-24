# Check if Symbol is Synchronized

> **Запрос:** проверить, синхронизированы ли данные символа с сервером.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_is_synchronized(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolIsSynchronized` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolIsSynchronized(SymbolIsSynchronizedRequest) -> SymbolIsSynchronizedReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolIsSynchronized(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Проверить, синхронизированы ли в данный момент рыночные данные символа с сервером брокера.
* **Зачем это нужно.** Убедиться, что символ имеет актуальные корректные данные, прежде чем запрашивать цены или размещать ордера.
* **Когда использовать.** После выбора символа, перед чтением данных тика или при проверке доступности символа.

---

## 🎯 Назначение

Используйте его для проверки доступности данных символа:

* Проверить статус синхронизации символа перед торговлей
* Проверить данные символа после вызова `symbol_select()`
* Убедиться, что данные тика актуальны и корректны
* Диагностировать отсутствующие или устаревшие рыночные данные
* Реализовать логику повторных попыток для выбора символа
* Проверить подключение символа перед операциями

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [symbol_is_synchronized - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_is_synchronized(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolIsSynchronizedData
```

**Сообщение запроса:**

```protobuf
message SymbolIsSynchronizedRequest {
  string symbol = 1;
}
```

**Сообщение ответа:**

```protobuf
message SymbolIsSynchronizedReply {
  oneof response {
    SymbolIsSynchronizedData data = 1;
    Error error = 2;
  }
}

message SymbolIsSynchronizedData {
  bool synchronized = 1;
}
```

---

## 🔽 Вход

| Параметр     | Тип                    | Описание                                             |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbol`      | `str` (обязательно)        | Имя символа для проверки                                    |
| `deadline`    | `datetime` (необязательно)   | Крайний срок для gRPC-вызова (UTC datetime)               |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                    |

---

## ⬆️ Выход

| Поле          | Тип   | Python-тип | Описание                                |
| -------------- | ------ | ----------- | ------------------------------------------ |
| `synchronized` | `bool` | `bool`      | True, если данные символа синхронизированы        |

**Возвращаемое значение:** Метод возвращает объект `SymbolIsSynchronizedData` с булевым полем `synchronized`.

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Доступ к значению:** Возвращаемый объект имеет поле `.synchronized` (а не `.is_synchronized`).
* **Выбор символа:** Если `synchronized` равно `False`, вызовите `symbol_select(symbol, True)`, чтобы добавить символ в Market Watch.
* **Задержка синхронизации:** После выбора символа синхронизация может занять 1-2 секунды.
* **Логика повторных попыток:** Реализуйте опрос с задержками при ожидании синхронизации.
* **Зависимость от данных тика:** Если не синхронизировано, `symbol_info_tick()` может возвращать нулевые или устаревшие значения.
* **Не ошибка:** Возврат `False` — это нормальное состояние, а не ошибка.

---

## 🔗 Примеры использования

### 1) Проверить, синхронизирован ли символ

```python

# Проверить статус синхронизации
result = await account.symbol_is_synchronized(symbol="EURUSD")

if result.synchronized:
    print("Symbol is synchronized")
else:
    print("Symbol is NOT synchronized")
```

### 2) Убедиться, что символ синхронизирован, перед получением тика

```python

async def get_synchronized_tick(account, symbol: str):
    """Получить данные тика, только если символ синхронизирован"""

    # Проверить синхронизацию
    sync_status = await account.symbol_is_synchronized(symbol)

    if not sync_status.synchronized:
        print(f"Symbol {symbol} not synchronized, selecting...")

        # Выбрать символ
        await account.symbol_select(symbol, True)

        # Подождать немного для синхронизации
        import asyncio
        await asyncio.sleep(1)

        # Повторно проверить
        sync_status = await account.symbol_is_synchronized(symbol)

        if not sync_status.synchronized:
            raise RuntimeError(f"Failed to synchronize {symbol}")

    # Теперь безопасно получить тик
    tick = await account.symbol_info_tick(symbol)
    return tick

# Использование
tick = await get_synchronized_tick(account, "EURUSD")
print(f"Bid: {tick.bid}, Ask: {tick.ask}")
```

### 3) Ожидать синхронизации с таймаутом

```python
import asyncio

async def wait_for_synchronization(
    account,
    symbol: str,
    timeout: float = 10.0,
    check_interval: float = 0.5
) -> bool:
    """Ожидать синхронизации символа с таймаутом"""

    start_time = asyncio.get_event_loop().time()

    while True:
        # Проверить текущий статус
        result = await account.symbol_is_synchronized(symbol)

        if result.synchronized:
            print(f"{symbol} synchronized")
            return True

        # Проверить таймаут
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            print(f"Timeout waiting for {symbol} synchronization")
            return False

        # Подождать перед следующей проверкой
        await asyncio.sleep(check_interval)

# Использование
if await wait_for_synchronization(account, "BTCUSD", timeout=10):
    print("Ready to trade")
else:
    print("Symbol not available")
```

### 4) Пакетная проверка нескольких символов

```python

async def check_symbols_sync(account, symbols: list[str]):
    """Проверить статус синхронизации для нескольких символов"""

    results = {}

    for symbol in symbols:
        try:
            sync_status = await account.symbol_is_synchronized(symbol)
            results[symbol] = sync_status.synchronized
        except Exception as e:
            print(f"Error checking {symbol}: {e}")
            results[symbol] = False

    # Отобразить результаты
    print(f"{'Symbol':<10} {'Status':<15}")
    print("=" * 25)
    for symbol, is_synced in results.items():
        status = "Synchronized" if is_synced else "Not synced"
        print(f"{symbol:<10} {status:<15}")

    return results

# Использование
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]
sync_results = await check_symbols_sync(account, symbols)
```

### 5) Выбрать символ и дождаться синхронизации

```python
import asyncio

async def ensure_symbol_synchronized(
    account,
    symbol: str,
    max_retries: int = 5
) -> bool:
    """Выбрать символ и дождаться синхронизации"""

    # Сначала проверить, не синхронизирован ли уже
    result = await account.symbol_is_synchronized(symbol)
    if result.synchronized:
        print(f"{symbol} already synchronized")
        return True

    # Выбрать символ
    print(f"Selecting {symbol}...")
    await account.symbol_select(symbol, True)

    # Повторять с экспоненциальной задержкой
    for attempt in range(max_retries):
        await asyncio.sleep(0.5 * (attempt + 1))  # 0.5s, 1s, 1.5s, 2s, 2.5s

        result = await account.symbol_is_synchronized(symbol)
        if result.synchronized:
            print(f"{symbol} synchronized after {attempt + 1} attempt(s)")
            return True

        print(f"Attempt {attempt + 1}/{max_retries}: still waiting...")

    print(f"Failed to synchronize {symbol} after {max_retries} attempts")
    return False

# Использование
if await ensure_symbol_synchronized(account, "EURUSD"):
    tick = await account.symbol_info_tick("EURUSD")
    print(f"Tick: {tick.bid}/{tick.ask}")
```

### 6) Проверить синхронизацию с параметром таймаута

```python
from datetime import datetime, timedelta, timezone

# Установить крайний срок для вызова
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    result = await account.symbol_is_synchronized(
        symbol="GBPUSD",
        deadline=deadline
    )

    if result.synchronized:
        print("Symbol is synchronized")
    else:
        print("Symbol needs synchronization")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 7) Проверить перед торговой операцией

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import asyncio

async def validate_symbol_ready(account, symbol: str) -> bool:
    """
    Комплексная проверка готовности символа к торговле.
    Возвращает True, только если символ существует, выбран и синхронизирован.
    """

    # Шаг 1: Проверить, существует ли символ
    exists = await account.symbol_exist(symbol)
    if not exists.exists:
        print(f"Symbol {symbol} does not exist")
        return False
    print(f"Symbol exists")

    # Шаг 2: Проверить, выбран ли он
    select_status = await account.symbol_info_integer(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_SELECT
    )

    if not select_status.value:
        print(f"Symbol not selected, adding to Market Watch...")
        await account.symbol_select(symbol, True)
        await asyncio.sleep(1)

    # Шаг 3: Проверить синхронизацию
    sync_status = await account.symbol_is_synchronized(symbol)
    if not sync_status.synchronized:
        print(f"Waiting for synchronization...")

        # Ждать до 5 секунд
        for i in range(10):
            await asyncio.sleep(0.5)
            sync_status = await account.symbol_is_synchronized(symbol)
            if sync_status.synchronized:
                break

        if not sync_status.synchronized:
            print(f"Symbol {symbol} failed to synchronize")
            return False

    print(f"Symbol {symbol} is ready for trading")
    return True

# Использование
if await validate_symbol_ready(account, "EURUSD"):
    # Безопасно размещать ордера
    print("Proceeding with trade...")
else:
    print("Cannot trade - symbol not ready")
```

---

## 📚 См. также

* [symbol_select](./symbol_select.md) - Выбрать/снять выбор символа в Market Watch
* [symbol_exist](./symbol_exist.md) - Проверить, существует ли символ
* [symbol_info_tick](./symbol_info_tick.md) - Получить текущие данные тика (требует синхронизированного символа)
* [symbol_info_integer](./symbol_info_integer.md) - Получить целочисленные свойства символа
