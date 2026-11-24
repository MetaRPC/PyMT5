# Get Symbol String Property

> **Запрос:** получить значение свойства строкового типа для символа.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_string(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoString` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoString(SymbolInfoStringRequest) -> SymbolInfoStringReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoString(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить одно значение свойства строкового типа для символа (DESCRIPTION, CURRENCY_BASE, PATH и т. д.).
* **Зачем это нужно.** Получить конкретные текстовые свойства символа, такие как коды валют, описания и метаданные.
* **Когда использовать.** Используйте `symbol_params_many()` для нескольких свойств. Этот метод используйте для запроса одного свойства.

---

## 🎯 Назначение

Используйте его для запроса конкретных строковых свойств символа:

* Получить описание символа и отображаемые имена
* Получить коды валют (базовая, прибыли, маржи)
* Проверить путь символа и категоризацию
* Получить информацию о бирже и ISIN
* Запросить формулу и метаданные символа
* Проверить информацию о банке и стране

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [symbol_info_string - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_string(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoStringProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoStringData
```

**Сообщение запроса:**

```protobuf
message SymbolInfoStringRequest {
  string symbol = 1;
  SymbolInfoStringProperty type = 2;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoStringReply {
  oneof response {
    SymbolInfoStringData data = 1;
    Error error = 2;
  }
}

message SymbolInfoStringData {
  string value = 1;
}
```

---

## 🔽 Вход

| Параметр   | Тип                             | Описание                                    |
| ----------- | -------------------------------- | ---------------------------------------------- |
| `symbol`    | `str` (обязательно)                 | Имя символа                                    |
| `property`  | `SymbolInfoStringProperty` (enum) | Свойство для получения (DESCRIPTION, PATH и т. д.) |
| `deadline`    | `datetime` (необязательно)             | Крайний срок для gRPC-вызова (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции |

---

## ⬆️ Выход

| Поле   | Тип     | Python-тип | Описание                        |
| ------- | -------- | ----------- | ---------------------------------- |
| `value` | `string` | `str`       | Строковое значение свойства   |

**Возвращаемое значение:** Метод возвращает объект `SymbolInfoStringData` с полем `value`, содержащим запрошенное свойство.

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В Python-коде используйте полный путь enum из модуля market_info.

### `SymbolInfoStringProperty`

Определено в `mt5-term-api-market-info.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_BASIS` | 0 | Базис символа |
| `SYMBOL_CATEGORY` | 1 | Категория символа |
| `SYMBOL_COUNTRY` | 2 | Страна символа |
| `SYMBOL_SECTOR_NAME` | 3 | Название сектора |
| `SYMBOL_INDUSTRY_NAME` | 4 | Название отрасли |
| `SYMBOL_CURRENCY_BASE` | 5 | Базовая валюта |
| `SYMBOL_CURRENCY_PROFIT` | 6 | Валюта прибыли |
| `SYMBOL_CURRENCY_MARGIN` | 7 | Валюта маржи |
| `SYMBOL_BANK` | 8 | Банк-поставщик котировок |
| `SYMBOL_DESCRIPTION` | 9 | Описание символа |
| `SYMBOL_EXCHANGE` | 10 | Название биржи |
| `SYMBOL_FORMULA` | 11 | Формула для пользовательских символов |
| `SYMBOL_ISIN` | 12 | Код ISIN |
| `SYMBOL_PAGE` | 13 | URL веб-страницы |
| `SYMBOL_PATH` | 14 | Путь символа в дереве символов |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить описание символа
desc = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_DESCRIPTION)
print(f"Description: {desc.value}")

# Получить валютную пару
base = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_CURRENCY_BASE)
profit = await account.symbol_info_string("EURUSD", market_info_pb2.SYMBOL_CURRENCY_PROFIT)
print(f"Pair: {base.value}/{profit.value}")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Доступ к значению:** Возвращаемый объект `SymbolInfoStringData` имеет поле `.value`, содержащее строку.
* **Свойства валют:** CURRENCY_BASE, CURRENCY_PROFIT и CURRENCY_MARGIN необходимы для расчётов маржи и прибыли.
* **Формат пути:** SYMBOL_PATH использует обратные слэши в качестве разделителей (например, "Forex\\Majors\\EURUSD").
* **Пустые значения:** Некоторые свойства могут возвращать пустые строки, если не заданы брокером.
* **Коды ISIN:** Доступны только для ценных бумаг, таких как акции и облигации.

---

## 🔗 Примеры использования

### 1) Получить описание символа

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить описание символа
result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DESCRIPTION
)
print(f"Description: {result.value}")  # Вывод: Description: Euro vs US Dollar
```

### 2) Получить валютную тройку (базовая, прибыли, маржи)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить все три кода валют
base = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_BASE
)

profit = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
)

margin = await account.symbol_info_string(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_CURRENCY_MARGIN
)

print(f"XAUUSD Currencies:")
print(f"  Base: {base.value}")      # XAU (золото)
print(f"  Profit: {profit.value}")  # USD
print(f"  Margin: {margin.value}")  # USD
```

### 3) Получить путь символа и разобрать иерархию

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_PATH
)

# Разобрать иерархию пути
path = result.value
folders = path.split("\\")

print(f"Symbol Path: {path}")
print(f"Hierarchy: {' > '.join(folders)}")
# Вывод: Hierarchy: Forex > Majors > EURUSD
```

### 4) Получить код ISIN для акций

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="AAPL",
    property=market_info_pb2.SYMBOL_ISIN
)

if result.value:
    print(f"AAPL ISIN: {result.value}")
else:
    print("ISIN not available")
```

### 5) Получить название биржи

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_string(
    symbol="BTCUSD",
    property=market_info_pb2.SYMBOL_EXCHANGE
)

print(f"Exchange: {result.value}")
```

### 6) Отобразить метаданные символа

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def display_symbol_metadata(account, symbol: str):
    """Отобразить полные строковые метаданные для символа"""

    # Получить описание
    desc = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_DESCRIPTION
    )

    # Получить путь
    path = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_PATH
    )

    # Получить валюты
    base_curr = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_CURRENCY_BASE
    )

    profit_curr = await account.symbol_info_string(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_CURRENCY_PROFIT
    )

    print(f"Symbol Metadata: {symbol}")
    print(f"  Description: {desc.value}")
    print(f"  Path: {path.value}")
    print(f"  Base Currency: {base_curr.value}")
    print(f"  Profit Currency: {profit_curr.value}")

# Использование
await display_symbol_metadata(account, "EURUSD")
```

### 7) Получить символ с таймаутом

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    result = await account.symbol_info_string(
        symbol="GBPUSD",
        property=market_info_pb2.SYMBOL_DESCRIPTION,
        deadline=deadline
    )
    print(f"Description: {result.value}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

---

## 📚 См. также

* [symbol_info_double](./symbol_info_double.md) - Получить свойства типа double
* [symbol_info_integer](./symbol_info_integer.md) - Получить целочисленные свойства
* [symbol_params_many](./symbol_params_many.md) - Получить все параметры символа сразу
