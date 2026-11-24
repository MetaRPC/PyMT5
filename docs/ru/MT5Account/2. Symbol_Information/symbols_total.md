# Получить общее количество символов

> **Запрос:** общее количество доступных символов на торговой платформе.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbols_total(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolsTotal` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolsTotal(SymbolsTotalRequest) -> SymbolsTotalReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolsTotal(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить общее количество символов, доступных на платформе.
* **Зачем это нужно.** Проверить, сколько символов доступно: все символы или только символы Market Watch.
* **Когда использовать.** Используйте для быстрого подсчёта символов. Для перебора символов предпочитайте `symbol_params_many()` (один вызов) вместо множества вызовов `symbol_name()`.

---

## 🎯 Назначение

Используйте для получения количества символов:

* Проверить общее количество символов на платформе
* Подсчитать символы в Market Watch
* Проверить доступность символов
* Быстрая проверка перед перебором символов
* Отслеживать изменения списка символов

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [symbols_total - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW.md)**

---

## Сигнатура метода

```python
async def symbols_total(
    self,
    selected_only: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolsTotalData
```

**Сообщение запроса:**

```protobuf
message SymbolsTotalRequest {
  bool mode = 1;
}
```

**Сообщение ответа:**

```protobuf
message SymbolsTotalReply {
  oneof response {
    SymbolsTotalData data = 1;
    Error error = 2;
  }
}

message SymbolsTotalData {
  int32 total = 1;
}
```

**Сопоставление параметров:**
- Python-параметр `selected_only` сопоставляется с protobuf-полем `mode`

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `selected_only` | `bool` (обязательный) | True = считать только символы Market Watch, False = считать все |
| `deadline`    | `datetime` (необязательно) | Крайний срок для gRPC-вызова (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                  |

**Использование:**

```python
from datetime import datetime, timedelta

# Подсчитать все символы
data = await account.symbols_total(selected_only=False)

# Подсчитать только символы Market Watch
data = await account.symbols_total(selected_only=True)
```

---

## ⬆️ Выход - `SymbolsTotalData`

| Поле    | Тип     | Python-тип  | Описание                                         |
| ------- | ------- | ----------- | ------------------------------------------------ |
| `total` | `int32` | `int`       | Общее количество символов                        |

**Возвращаемое значение:** Метод возвращает объект `SymbolsTotalData` с полем `total`.

---

## 🧱 Связанные enum (из proto)

Этот метод не использует enum.

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC.
* **Market Watch vs Все:** `selected_only=True` считает только символы, видимые в Market Watch; `False` считает все доступные символы.
* **Требуется подключение:** Сначала вызовите `connect_by_host_port()` или `connect_by_server_name()`.
* **Потокобезопасность:** Безопасно вызывать одновременно из нескольких задач asyncio.
* **Производительность:** Это лёгкий вызов - используйте его свободно для проверки перед операциями.
* **Тип возврата:** Метод возвращает protobuf-объект `SymbolsTotalData` (Python-тип соответствует типам полей).

---

## 🔗 Примеры использования

### 1) Получить общее количество символов

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5.mt5_account import MT5Account

async def main():
    account = MT5Account(
        account_number=12345678,
        password="your_password",
        host="your-server.com:443"
    )

    await account.connect_by_server_name("MetaQuotes-Demo")

    try:
        # Подсчитать все символы
        data_all = await account.symbols_total(selected_only=False)
        print(f"Total symbols available: {data_all.total}")

        # Подсчитать символы Market Watch
        data_mw = await account.symbols_total(selected_only=True)
        print(f"Market Watch symbols: {data_mw.total}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Сравнить Market Watch со всеми символами

```python
async def compare_symbol_counts(account: MT5Account):
    """Compare Market Watch vs all available symbols"""
    # Получить количества
    all_symbols = await account.symbols_total(selected_only=False)
    mw_symbols = await account.symbols_total(selected_only=True)

    print(f"\nSymbol Statistics:")
    print(f"  All available: {all_symbols.total}")
    print(f"  Market Watch: {mw_symbols.total}")
    print(f"  Not in Market Watch: {all_symbols.total - mw_symbols.total}")

    return {
        "all": all_symbols.total,
        "market_watch": mw_symbols.total,
        "hidden": all_symbols.total - mw_symbols.total
    }

# Использование:
stats = await compare_symbol_counts(account)
```

### 3) Проверить доступность символов

```python
async def has_symbols(account: MT5Account) -> bool:
    """Check if any symbols are available"""
    data = await account.symbols_total(selected_only=False)

    if data.total > 0:
        print(f"[OK] {data.total} symbols available")
        return True
    else:
        print("[WARNING] No symbols available")
        return False

# Использование:
if await has_symbols(account):
    print("Ready to trade")
```

### 4) Отслеживать изменения количества символов

```python
async def monitor_symbol_count(account: MT5Account, interval: float = 60.0):
    """Monitor for changes in symbol count"""
    previous_count = None

    while True:
        try:
            data = await account.symbols_total(selected_only=True)
            count = data.total

            if previous_count is not None and count != previous_count:
                if count > previous_count:
                    print(f"[+] Symbol added to Market Watch: {count} total")
                else:
                    print(f"[-] Symbol removed from Market Watch: {count} total")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Market Watch: {count} symbols")

            previous_count = count

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Использование:
# await monitor_symbol_count(account, interval=60.0)
```

### 5) Проверка перед перебором

```python
async def iterate_symbols_safe(account: MT5Account):
    """Safely iterate through symbols with validation"""
    # Сначала проверить количество
    data = await account.symbols_total(selected_only=True)

    if data.total == 0:
        print("[WARNING] No symbols in Market Watch")
        return []

    print(f"[OK] Found {data.total} symbols")

    # Теперь безопасно перебирать
    symbols = []
    for i in range(data.total):
        symbol_name = await account.symbol_name(index=i, selected=True)
        symbols.append(symbol_name.name)

    return symbols

# Использование:
symbols = await iterate_symbols_safe(account)
print(f"Symbols: {symbols}")
```

### 6) Рассчитать использование Market Watch

```python
async def calculate_mw_usage(account: MT5Account) -> dict:
    """Calculate Market Watch usage statistics"""
    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    total = all_data.total
    used = mw_data.total
    usage_pct = (used / total * 100) if total > 0 else 0

    result = {
        "total_available": total,
        "in_market_watch": used,
        "usage_percent": usage_pct
    }

    print(f"\nMarket Watch Usage:")
    print(f"  Using {used} of {total} symbols ({usage_pct:.1f}%)")

    return result

# Использование:
usage = await calculate_mw_usage(account)
```

### 7) Дождаться загрузки символов

```python
async def wait_for_symbols(
    account: MT5Account,
    min_symbols: int = 1,
    timeout_seconds: int = 30,
    check_interval: float = 1.0
):
    """Wait until minimum number of symbols available"""
    import time
    start_time = time.time()

    print(f"Waiting for at least {min_symbols} symbol(s)...")

    while True:
        # Проверить тайм-аут
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Timeout: symbols not loaded after {timeout_seconds}s")

        # Проверить количество символов
        data = await account.symbols_total(selected_only=False)
        count = data.total

        if count >= min_symbols:
            print(f"[OK] {count} symbols loaded")
            return count

        print(f"[INFO] Waiting... ({count} symbols)")
        await asyncio.sleep(check_interval)

# Использование:
try:
    count = await wait_for_symbols(account, min_symbols=10)
except TimeoutError as e:
    print(f"[ERROR] {e}")
```

### 8) Логировать статистику символов

```python
import logging

async def log_symbol_statistics(account: MT5Account):
    """Log comprehensive symbol statistics"""
    logging.basicConfig(level=logging.INFO)

    all_data = await account.symbols_total(selected_only=False)
    mw_data = await account.symbols_total(selected_only=True)

    logging.info("=" * 60)
    logging.info("SYMBOL STATISTICS")
    logging.info("=" * 60)
    logging.info(f"Total symbols available: {all_data.total}")
    logging.info(f"Market Watch symbols: {mw_data.total}")
    logging.info(f"Hidden symbols: {all_data.total - mw_data.total}")
    logging.info("=" * 60)

# Использование:
await log_symbol_statistics(account)
```

---

## Распространённые паттерны

### Быстрая проверка количества

```python
async def get_mw_symbol_count(account: MT5Account) -> int:
    """Get Market Watch symbol count"""
    data = await account.symbols_total(selected_only=True)
    return data.total
```

### Проверка загрузки символов

```python
async def symbols_loaded(account: MT5Account) -> bool:
    """Check if symbols are loaded"""
    data = await account.symbols_total(selected_only=False)
    return data.total > 0
```

---

## 📚 См. также

* [symbol_params_many](./symbol_params_many.md) - Получить полные параметры для всех символов (РЕКОМЕНДУЕТСЯ для перебора)
* [symbol_name](./symbol_name.md) - Получить имя символа по индексу
* [symbol_exist](./symbol_exist.md) - Проверить существование конкретного символа
* [symbol_select](./symbol_select.md) - Добавить/удалить символ из Market Watch
