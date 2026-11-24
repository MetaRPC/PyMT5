# Get Symbol Integer Property

> **Запрос:** получить значение свойства целочисленного типа для символа.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_integer(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoInteger` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoInteger(SymbolInfoIntegerRequest) -> SymbolInfoIntegerReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoInteger(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить одно значение свойства целочисленного типа для символа (DIGITS, SPREAD, TRADE_MODE и т. д.).
* **Зачем это нужно.** Получить конкретные целочисленные свойства символа, не запрашивая все данные символа.
* **Когда использовать.** Используйте `symbol_params_many()` для нескольких свойств. Этот метод используйте для запроса одного свойства.

---

## 🎯 Назначение

Используйте его для запроса конкретных целочисленных свойств символа:

* Получить количество знаков символа (десятичных разрядов)
* Проверить текущий спред в пунктах
* Запросить торговые режимы и режимы исполнения
* Получить временные метки (время начала, истечения)
* Проверить параметры объёма
* Получить уровни стопов и заморозки торговли
* Запросить настройки переноса свопов
* Отслеживать режимы ордеров и заполнения

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [symbol_info_integer - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_integer(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoIntegerProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoIntegerData
```

**Сообщение запроса:**

```protobuf
message SymbolInfoIntegerRequest {
  string symbol = 1;
  SymbolInfoIntegerProperty type = 2;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoIntegerReply {
  oneof response {
    SymbolInfoIntegerData data = 1;
    Error error = 2;
  }
}

message SymbolInfoIntegerData {
  int64 value = 1;
}
```

---

## 🔽 Вход

| Параметр   | Тип                              | Описание                               |
| ----------- | --------------------------------- | ----------------------------------------- |
| `symbol`    | `str` (обязательно)                  | Имя символа                               |
| `property`  | `SymbolInfoIntegerProperty` (enum) | Свойство для получения (DIGITS, SPREAD и т. д.) |
| `deadline`    | `datetime` (необязательно)             | Крайний срок для gRPC-вызова (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции |

---

## ⬆️ Выход

| Поле   | Тип    | Python-тип | Описание                        |
| ------- | ------- | ----------- | ---------------------------------- |
| `value` | `int64` | `int`       | Целочисленное значение свойства  |

**Возвращаемое значение:** Метод возвращает объект `SymbolInfoIntegerData` с полем `value`, содержащим запрошенное свойство.

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В Python-коде используйте полный путь enum из модуля market_info.

### `SymbolInfoIntegerProperty`

Определено в `mt5-term-api-market-info.proto`.

### Статус и отображение символа

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_EXIST` | 6 | Флаг существования символа |
| `SYMBOL_SELECT` | 7 | Символ выбран в MarketWatch |
| `SYMBOL_VISIBLE` | 8 | Символ виден в MarketWatch |
| `SYMBOL_SUBSCRIPTION_DELAY` | 0 | Задержка подписки |
| `SYMBOL_CUSTOM` | 3 | Флаг пользовательского символа |
| `SYMBOL_BACKGROUND_COLOR` | 4 | Цвет фона |
| `SYMBOL_CHART_MODE` | 5 | Режим графика |

### Классификация

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_SECTOR` | 1 | Сектор |
| `SYMBOL_INDUSTRY` | 2 | Отрасль |

### Время и точность

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_TIME` | 15 | Время последней котировки |
| `SYMBOL_TIME_MSC` | 16 | Время последней котировки в миллисекундах |
| `SYMBOL_DIGITS` | 17 | Знаков после десятичной точки |
| `SYMBOL_START_TIME` | 23 | Время начала символа |
| `SYMBOL_EXPIRATION_TIME` | 24 | Время истечения символа |

### Спред и объём

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_SPREAD` | 19 | Значение спреда в пунктах |
| `SYMBOL_SPREAD_FLOAT` | 18 | Флаг плавающего спреда |
| `SYMBOL_VOLUME` | 12 | Объём последней сделки |
| `SYMBOL_VOLUMEHIGH` | 13 | Максимальный объём за день |
| `SYMBOL_VOLUMELOW` | 14 | Минимальный объём за день |
| `SYMBOL_TICKS_BOOKDEPTH` | 20 | Максимальное число заявок, отображаемых в DOM |

### Данные сессии

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_SESSION_DEALS` | 9 | Число сделок в текущей сессии |
| `SYMBOL_SESSION_BUY_ORDERS` | 10 | Число ордеров на покупку |
| `SYMBOL_SESSION_SELL_ORDERS` | 11 | Число ордеров на продажу |

### Торговые свойства

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_TRADE_CALC_MODE` | 21 | Режим расчёта цены контракта |
| `SYMBOL_TRADE_MODE` | 22 | Разрешённый режим торговли по символу |
| `SYMBOL_TRADE_STOPS_LEVEL` | 25 | Минимальная дистанция для стопов |
| `SYMBOL_TRADE_FREEZE_LEVEL` | 26 | Дистанция заморозки торговых операций |
| `SYMBOL_TRADE_EXEMODE` | 27 | Режим исполнения сделок |

### Режимы ордеров и истечения

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_EXPIRATION_MODE` | 31 | Флаги разрешённых режимов истечения |
| `SYMBOL_FILLING_MODE` | 32 | Флаги разрешённых режимов заполнения |
| `SYMBOL_ORDER_MODE` | 33 | Флаги разрешённых типов ордеров |
| `SYMBOL_ORDER_GTC_MODE` | 34 | Истечение отложенных ордеров в режиме GTC |

### Своп и маржа

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_SWAP_MODE` | 28 | Модель расчёта свопа |
| `SYMBOL_SWAP_ROLLOVER3DAYS` | 29 | День недели для начисления тройного свопа |
| `SYMBOL_MARGIN_HEDGED_USE_LEG` | 30 | Расчёт маржи при хеджировании по большей ноге |

### Опционы

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_OPTION_MODE` | 35 | Тип опциона |
| `SYMBOL_OPTION_RIGHT` | 36 | Право опциона (Call/Put) |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить количество знаков символа
digits_data = await account.symbol_info_integer("EURUSD", market_info_pb2.SYMBOL_DIGITS)
print(f"Digits: {digits_data.value}")

# Проверить спред
spread_data = await account.symbol_info_integer("EURUSD", market_info_pb2.SYMBOL_SPREAD)
print(f"Spread: {spread_data.value} points")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Доступ к значению:** Возвращаемый объект `SymbolInfoIntegerData` имеет поле `.value`, содержащее целое число.
* **Торговые режимы:** Свойства режимов возвращают целочисленные флаги — обратитесь к документации MT5 за значениями флагов.
* **Временные метки:** Свойства TIME и TIME_MSC возвращают Unix-метки времени (секунды или миллисекунды).
* **Единицы спреда:** SYMBOL_SPREAD возвращает спред в пунктах, а не в пипсах.
* **Булевы флаги:** Свойства, такие как SYMBOL_EXIST, SYMBOL_SELECT, SYMBOL_VISIBLE, возвращают 0 или 1.

---

## 🔗 Примеры использования

### 1) Получить количество знаков и спред символа

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить количество знаков (десятичных разрядов)
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)
print(f"Digits: {result.value}")  # Вывод: Digits: 5

# Получить спред в пунктах
spread_result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_SPREAD
)
print(f"Spread: {spread_result.value} points")  # Вывод: Spread: 10 points
```

### 2) Проверить, выбран ли символ в MarketWatch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="GBPUSD",
    property=market_info_pb2.SYMBOL_SELECT
)

if result.value:
    print("Symbol is in MarketWatch")
else:
    print("Symbol is NOT in MarketWatch")
```

### 3) Получить торговый режим

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_TRADE_MODE
)

# Сопоставить с названиями торговых режимов
trade_modes = {
    0: "DISABLED",
    1: "LONG_ONLY",
    2: "SHORT_ONLY",
    3: "CLOSE_ONLY",
    4: "FULL"
}

mode_name = trade_modes.get(result.value, "UNKNOWN")
print(f"Trade mode: {mode_name} (value: {result.value})")
```

### 4) Получить временную метку последней котировки

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime

# Получить временную метку в секундах
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TIME
)

# Преобразовать в datetime
quote_time = datetime.utcfromtimestamp(result.value)
print(f"Last quote time: {quote_time}")

# Или получить временную метку в миллисекундах
result_msc = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TIME_MSC
)
quote_time_msc = datetime.utcfromtimestamp(result_msc.value / 1000)
print(f"Last quote time (ms precision): {quote_time_msc}")
```

### 5) Проверить уровень стопов перед размещением ордера

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TRADE_STOPS_LEVEL
)

stops_level = result.value
print(f"Minimum stops level: {stops_level} points")
print(f"SL/TP must be at least {stops_level} points away from current price")
```

### 6) Получить уровень заморозки

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TRADE_FREEZE_LEVEL
)

freeze_level = result.value
if freeze_level > 0:
    print(f"Freeze level: {freeze_level} points")
    print(f"Orders cannot be modified when price is within {freeze_level} points")
else:
    print("No freeze level set")
```

### 7) Проверить разрешённые типы ордеров

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="BTCUSD",
    property=market_info_pb2.SYMBOL_ORDER_MODE
)

# ORDER_MODE — это битовое поле
order_flags = result.value

# Проверить конкретные типы ордеров (пример значений флагов)
if order_flags & 1:
    print("Market orders allowed")
if order_flags & 2:
    print("Limit orders allowed")
if order_flags & 4:
    print("Stop orders allowed")
if order_flags & 8:
    print("Stop Limit orders allowed")
```

---

## 📚 См. также

* [symbol_info_double](./symbol_info_double.md) - Получить свойства типа double
* [symbol_info_string](./symbol_info_string.md) - Получить строковые свойства
* [symbol_params_many](./symbol_params_many.md) - Получить все параметры символа сразу
