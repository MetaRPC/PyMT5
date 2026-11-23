# Добавить или удалить символ из Market Watch

> **Запрос:** добавить или удалить символ из окна Market Watch, чтобы сделать его доступным для торговли и подписок на данные.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_select(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolSelect` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolSelect(SymbolSelectRequest) -> SymbolSelectReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolSelect(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Добавить или удалить символ из окна Market Watch (делает символ доступным/недоступным для торговли и подписок).
* **Зачем это нужно.** Требуется перед торговлей или подпиской на данные символа - MT5 разрешает операции только над символами в Market Watch.
* **Когда использовать.** Перед любыми торговыми операциями или подписками на данные для символа; при очистке неиспользуемых символов.

---

## 🎯 Назначение

Используйте для управления Market Watch:

* Добавить символ в Market Watch перед торговлей
* Включить символ для подписок на котировки
* Удалить неиспользуемые символы для снижения накладных расходов
* Программно подготовить торговую среду
* Очистить Market Watch после торговой сессии
* Проверить доступность символа для операций

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [symbol_select - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_select(
    self,
    symbol: str,
    select: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolSelectData
```

**Сообщение запроса:**

```protobuf
message SymbolSelectRequest {
  string symbol = 1;
  bool select = 2;
}
```

**Сообщение ответа:**

```protobuf
message SymbolSelectReply {
  oneof response {
    SymbolSelectData data = 1;
    Error error = 2;
  }
}

message SymbolSelectData {
  bool success = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbol`      | `str` (обязательный)    | Имя символа (например, "EURUSD", "BTCUSD")              |
| `select`      | `bool` (обязательный)   | `True` = добавить в Market Watch, `False` = удалить      |
| `deadline`    | `datetime` (необязательно) | Крайний срок для gRPC-вызова (UTC datetime)           |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                  |

---

## ⬆️ Выход

| Поле      | Тип    | Python-тип  | Описание                                                 |
| --------- | ------ | ----------- | -------------------------------------------------------- |
| `success` | `bool` | `bool`      | `True`, если операция успешна, `False`, если не удалась   |

**Возвращаемое значение:** Метод возвращает объект `SymbolSelectData` со статусом успеха.

---

## 🧱 Связанные enum

Этот метод не использует enum.

---

## 🧩 Примечания и советы

* **Требуется перед торговлей:** Символ ДОЛЖЕН быть в Market Watch, прежде чем вы сможете торговать им или подписаться на его данные.
* **Идемпотентная операция:** Добавление уже выбранного символа или удаление уже удалённого символа возвращает success.
* **Несуществующие символы:** Выбор несуществующего символа возвращает `success=False`.
* **Управление Market Watch:** Используйте это для программного управления тем, какие символы видны в MT5.
* **Производительность:** Удаление неиспользуемых символов из Market Watch может улучшить производительность и снизить сетевой трафик.
* **Группы символов:** Некоторые брокеры организуют символы в группы - убедитесь, что имя символа точное, включая суффиксы.
* **Чувствительность к регистру:** Имена символов чувствительны к регистру (обычно в верхнем регистре).
* **Индикатор успеха:** Всегда проверяйте `data.success`, чтобы убедиться, что операция завершилась успешно.

---

## 🔗 Примеры использования

### 1) Добавить символ в Market Watch (РЕКОМЕНДУЕТСЯ)

```python
from MetaRpcMT5.mt5_account import MT5Account

async def add_to_market_watch(account: MT5Account, symbol: str):
    """Add symbol to Market Watch before trading"""

    # Добавить символ
    data = await account.symbol_select(symbol=symbol, select=True)

    if data.success:
        print(f"{symbol} added to Market Watch")
        return True
    else:
        print(f"Failed to add {symbol} to Market Watch")
        return False

# Использование
success = await add_to_market_watch(account, "EURUSD")
```

### 2) Удалить символ из Market Watch

```python
async def remove_from_market_watch(account: MT5Account, symbol: str):
    """Remove symbol from Market Watch to clean up"""

    # Удалить символ
    data = await account.symbol_select(symbol=symbol, select=False)

    if data.success:
        print(f"{symbol} removed from Market Watch")
        return True
    else:
        print(f"Failed to remove {symbol}")
        return False

# Использование
await remove_from_market_watch(account, "GBPJPY")
```

### 3) Добавить несколько символов с обработкой ошибок

```python
async def add_symbols_batch(account: MT5Account, symbols: list[str]):
    """Add multiple symbols to Market Watch"""

    results = {'added': [], 'failed': []}

    for symbol in symbols:
        data = await account.symbol_select(symbol=symbol, select=True)

        if data.success:
            results['added'].append(symbol)
            print(f"{symbol}")
        else:
            results['failed'].append(symbol)
            print(f"{symbol}")

    print(f"\nAdded: {len(results['added'])}, Failed: {len(results['failed'])}")
    return results

# Использование
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
results = await add_symbols_batch(account, symbols)
```

### 4) Настроить торговую среду

```python
async def setup_trading_symbols(account: MT5Account):
    """Setup symbols before trading session"""

    # Определить необходимые символы
    required_symbols = [
        "EURUSD", "GBPUSD", "USDJPY",
        "AUDUSD", "USDCAD", "NZDUSD"
    ]

    print("Setting up trading environment...")

    for symbol in required_symbols:
        data = await account.symbol_select(symbol=symbol, select=True)

        if data.success:
            print(f"  {symbol} ready")
        else:
            print(f"  {symbol} FAILED - check symbol name")
            return False

    print("All symbols ready for trading!")
    return True

# Использование
if await setup_trading_symbols(account):
    print("Starting trading strategy...")
```

### 5) Очистить неиспользуемые символы

```python
async def cleanup_market_watch(account: MT5Account, keep_symbols: list[str]):
    """Remove all symbols except specified ones"""

    # Получить все символы, сейчас находящиеся в Market Watch

    # Получить общее количество символов
    total_data = await account.symbols_total(selected_only=True)
    total = total_data.total

    removed = []
    # Сначала соберите все имена: при удалении индексы сдвигаются,
    # поэтому не удаляйте во время обхода списка по индексу.
    symbols = []
    for i in range(total):
        name_data = await account.symbol_name(index=i, selected=True)
        symbols.append(name_data.name)

    # Затем отдельным циклом удалите те, которых нет в списке сохраняемых
    for symbol in symbols:
        if symbol not in keep_symbols:
            data = await account.symbol_select(symbol=symbol, select=False)
            if data.success:
                removed.append(symbol)
                print(f"Removed: {symbol}")

    print(f"\nRemoved {len(removed)} symbols from Market Watch")
    return removed

# Использование
keep = ["EURUSD", "GBPUSD", "USDJPY"]
await cleanup_market_watch(account, keep)
```

### 6) Проверить выбор символа с тайм-аутом

```python
from datetime import datetime, timedelta, timezone

async def select_symbol_with_timeout(
    account: MT5Account,
    symbol: str,
    select: bool,
    timeout_seconds: int = 5
):
    """Select symbol with timeout"""

    # Рассчитать крайний срок
    deadline = datetime.now(timezone.utc) + timedelta(seconds=timeout_seconds)

    try:
        data = await account.symbol_select(
            symbol=symbol,
            select=select,
            deadline=deadline
        )

        action = "added to" if select else "removed from"
        verb = "add" if select else "remove"
        if data.success:
            print(f"{symbol} {action} Market Watch")
        else:
            print(f"Failed to {verb} {symbol}")

        return data.success

    except Exception as e:
        print(f"Timeout or error selecting {symbol}: {e}")
        return False

# Использование
success = await select_symbol_with_timeout(account, "EURUSD", True, timeout_seconds=3)
```

### 7) Подготовить символы для стратегии

```python
async def prepare_symbols_for_strategy(
    account: MT5Account,
    strategy_symbols: dict[str, bool]
):
    """
    Prepare Market Watch for trading strategy

    Args:
        strategy_symbols: Dict of {symbol: should_select}
    """

    print("Configuring Market Watch for strategy...")

    success_count = 0
    fail_count = 0

    for symbol, should_select in strategy_symbols.items():
        action = "Adding" if should_select else "Removing"

        data = await account.symbol_select(
            symbol=symbol,
            select=should_select
        )

        if data.success:
            status = "[OK]"
            success_count += 1
        else:
            status = "[FAIL]"
            fail_count += 1

        action_word = "to" if should_select else "from"
        print(f"{status} {action} {symbol} {action_word} Market Watch")

    print(f"\nResults: {success_count} succeeded, {fail_count} failed")

    if fail_count > 0:
        print("WARNING: Some symbols failed - check symbol names")
        return False

    return True

# Использование
strategy_config = {
    "EURUSD": True,   # Добавить
    "GBPUSD": True,   # Добавить
    "USDJPY": True,   # Добавить
    "XAUUSD": False,  # Удалить
    "BTCUSD": False   # Удалить
}

if await prepare_symbols_for_strategy(account, strategy_config):
    print("Market Watch configured successfully!")
```

---

## 📚 См. также

* [symbol_exist](./symbol_exist.md) - Проверить существование символа на сервере
* [symbol_name](./symbol_name.md) - Получить имя символа по индексу
* [symbols_total](./symbols_total.md) - Получить общее количество символов
* [symbol_info_tick](./symbol_info_tick.md) - Получить данные тика символа (требует, чтобы символ был сначала выбран)
