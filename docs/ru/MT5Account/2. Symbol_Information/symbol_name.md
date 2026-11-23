# Получить имя символа по индексу

> **Запрос:** получить имя символа по позиции индекса.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_name(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolName` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolName(SymbolNameRequest) -> SymbolNameReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolName(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить имя символа по его числовой позиции индекса в списке символов.
* **Зачем это нужно.** Перечислять символы последовательно, программно перебирать доступные символы.
* **Когда использовать.** Используйте вместе с `symbols_total()` для перебора всех символов или символов Market Watch.

---

## 🎯 Назначение

Используйте для перечисления символов:

* Перебирать все доступные символы
* Получать символы Market Watch по позиции
* Программно строить списки символов
* Реализовать UI выбора символов
* Обнаруживать доступные торговые инструменты
* Сопоставлять позиции индекса с именами символов

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [symbol_name - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_name(
    self,
    index: int,
    selected: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolNameData
```

**Сообщение запроса:**

```protobuf
message SymbolNameRequest {
  uint32 index = 1;
  bool selected = 2;
}
```

**Сообщение ответа:**

```protobuf
message SymbolNameReply {
  oneof response {
    SymbolNameData data = 1;
    Error error = 2;
  }
}

message SymbolNameData {
  string name = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `index`       | `int` (обязательный)    | Индекс символа (с нуля, начиная с 0)                    |
| `selected`    | `bool` (обязательный)   | True = только Market Watch, False = все доступные символы |
| `deadline`    | `datetime` (необязательно) | Крайний срок для gRPC-вызова (UTC datetime)           |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                  |

---

## ⬆️ Выход

| Поле   | Тип      | Python-тип  | Описание                           |
| ------ | -------- | ----------- | ---------------------------------- |
| `name` | `string` | `str`       | Имя символа по указанному индексу  |

**Возвращаемое значение:** Метод возвращает объект `SymbolNameData` с полем `name`, содержащим имя символа.

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Тайм-аут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до тайм-аута сервера).
* **Доступ к значению:** У возвращённого объекта есть поле `.name`, содержащее строку имени символа.
* **Диапазон индекса:** Допустимые индексы от 0 до `symbols_total() - 1`. Индексы вне диапазона вызовут ошибку.
* **Selected vs все:** Используйте `selected=True` для символов Market Watch, `selected=False` для всех символов брокера.
* **Зависимость от порядка:** Порядок символов может меняться между вызовами, если Market Watch изменяется.
* **Индексация с нуля:** Первый символ находится по индексу 0, а не 1.
* **Комбинируйте с symbols_total:** Всегда сначала вызывайте `symbols_total()`, чтобы получить допустимый диапазон индексов.

---

## 🔗 Примеры использования

### 1) Получить все символы Market Watch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_market_watch_symbols(account) -> list[str]:
    """Get list of all symbols in Market Watch"""

    # Получить общее количество символов Market Watch
    count_data = await account.symbols_total(selected_only=True)
    total = count_data.total

    print(f"Found {total} symbols in Market Watch")

    # Перебрать и собрать все имена символов
    symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=True)
        symbols.append(symbol_data.name)

    return symbols

# Использование
mw_symbols = await get_all_market_watch_symbols(account)
print(f"Market Watch symbols: {mw_symbols}")
```

### 2) Получить все доступные символы от брокера

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_broker_symbols(account) -> list[str]:
    """Get list of ALL symbols available from broker"""

    # Получить общее количество всех символов
    count_data = await account.symbols_total(selected_only=False)
    total = count_data.total

    print(f"Found {total} total symbols from broker")

    # Перебрать и собрать все имена символов
    symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=False)
        symbols.append(symbol_data.name)

    return symbols

# Использование
all_symbols = await get_all_broker_symbols(account)
print(f"Total symbols available: {len(all_symbols)}")
```

### 3) Вывести первые 10 символов Market Watch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def print_first_symbols(account, count: int = 10):
    """Display first N symbols from Market Watch"""

    print(f"First {count} Market Watch symbols:")
    print("=" * 40)

    for i in range(count):
        try:
            symbol_data = await account.symbol_name(index=i, selected=True)
            print(f"{i+1:3d}. {symbol_data.name}")
        except Exception as e:
            print(f"[ERROR] Index {i}: {e}")
            break

# Использование
await print_first_symbols(account, count=10)
```

### 4) Найти символы по шаблону

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def find_symbols_by_pattern(account, pattern: str, selected_only: bool = True) -> list[str]:
    """Find symbols matching a text pattern"""

    # Получить общее количество
    count_data = await account.symbols_total(selected_only=selected_only)
    total = count_data.total

    # Поиск совпадающих символов
    matching_symbols = []
    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=selected_only)

        if pattern.upper() in symbol_data.name.upper():
            matching_symbols.append(symbol_data.name)

    return matching_symbols

# Использование
usd_symbols = await find_symbols_by_pattern(account, "USD")
print(f"Found {len(usd_symbols)} symbols containing 'USD': {usd_symbols}")
```

### 5) Сравнить Market Watch со всеми доступными символами

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def compare_symbol_lists(account):
    """Compare Market Watch symbols with all available symbols"""

    # Получить символы Market Watch
    mw_count = await account.symbols_total(selected_only=True)
    mw_total = mw_count.total

    # Получить все символы брокера
    all_count = await account.symbols_total(selected_only=False)
    all_total = all_count.total

    print(f"Symbol Statistics:")
    print(f"  Market Watch: {mw_total} symbols")
    print(f"  Available from broker: {all_total} symbols")
    print(f"  Not in Market Watch: {all_total - mw_total} symbols")

# Использование
await compare_symbol_lists(account)
```

### 6) Получить символы с обработкой ошибок

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_symbols_safe(account, selected_only: bool = True) -> list[str]:
    """Get symbols with robust error handling"""

    symbols = []

    try:
        # Получить общее количество
        count_data = await account.symbols_total(selected_only=selected_only)
        total = count_data.total

        # Перебрать с обработкой ошибок
        for i in range(total):
            try:
                symbol_data = await account.symbol_name(index=i, selected=selected_only)
                symbols.append(symbol_data.name)
            except Exception as e:
                print(f"Error getting symbol at index {i}: {e}")
                # Продолжить со следующим символом
                continue

        print(f"Successfully retrieved {len(symbols)} out of {total} symbols")

    except Exception as e:
        print(f"Error getting symbol count: {e}")

    return symbols

# Использование
symbols = await get_symbols_safe(account, selected_only=True)
```

### 7) Получить имя символа с тайм-аутом

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

# Установить крайний срок
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    symbol_data = await account.symbol_name(
        index=0,
        selected=True,
        deadline=deadline
    )
    print(f"First symbol: {symbol_data.name}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 8) Построить словарь символов с метаданными

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def build_symbol_dict(account) -> dict:
    """Build dictionary mapping indices to symbol info"""

    count_data = await account.symbols_total(selected_only=True)
    total = count_data.total

    symbol_dict = {}

    for i in range(total):
        symbol_data = await account.symbol_name(index=i, selected=True)
        symbol_name = symbol_data.name

        # Получить дополнительную информацию
        digits_data = await account.symbol_info_integer(
            symbol=symbol_name,
            property=market_info_pb2.SYMBOL_DIGITS
        )

        symbol_dict[i] = {
            'name': symbol_name,
            'index': i,
            'digits': digits_data.value
        }

    return symbol_dict

# Использование
symbols_info = await build_symbol_dict(account)
for idx, info in symbols_info.items():
    print(f"{idx}: {info['name']} (digits={info['digits']})")
```

---

## 📚 См. также

* [symbols_total](./symbols_total.md) - Получить общее количество символов (используйте перед вызовом symbol_name)
* [symbol_exist](./symbol_exist.md) - Проверить существование конкретного символа
* [symbol_select](./symbol_select.md) - Добавить/удалить символы из Market Watch
