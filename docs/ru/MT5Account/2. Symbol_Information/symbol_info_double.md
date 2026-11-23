# Get Symbol Double Property

> **Запрос:** получить значение свойства типа double для символа.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_double(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoDouble` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoDouble(SymbolInfoDoubleRequest) -> SymbolInfoDoubleReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoDouble(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить одно значение свойства типа double для символа (BID, ASK, VOLUME и т. д.).
* **Зачем это нужно.** Получить конкретные числовые свойства символа, не запрашивая все данные символа.
* **Когда использовать.** Используйте `symbol_params_many()` для нескольких свойств. Этот метод используйте для запроса одного свойства.

---

## 🎯 Назначение

Используйте его для запроса конкретных свойств символа типа double:

* Получить текущие цены BID/ASK
* Проверить торговые объёмы
* Получить требования к марже
* Получить ставки свопов
* Запросить стоимость тика и размеры контрактов
* Отслеживать цены и лимиты сессии

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [symbol_info_double - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_double(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoDoubleProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Сообщение запроса:**

```protobuf
message SymbolInfoDoubleRequest {
  string symbol = 1;
  SymbolInfoDoubleProperty type = 2;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoDoubleReply {
  oneof response {
    SymbolInfoDoubleData data = 1;
    Error error = 2;
  }
}

message SymbolInfoDoubleData {
  double value = 1;
}
```

---

## 🔽 Вход

| Параметр   | Тип                            | Описание                          |
| ----------- | ------------------------------- | ------------------------------------ |
| `symbol`    | `str` (обязательно)                | Имя символа                          |
| `property`  | `SymbolInfoDoubleProperty` (enum) | Свойство для получения (BID, ASK и т. д.) |
| `deadline`    | `datetime` (необязательно)   | Крайний срок для gRPC-вызова (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                    |

---

## ⬆️ Выход - `SymbolInfoDoubleData`

| Поле   | Тип     | Python-тип | Описание                          |
| ------- | -------- | ----------- | ------------------------------------ |
| `value` | `double` | `float`     | Значение запрошенного свойства  |

**Возвращаемое значение:** Метод возвращает объект `SymbolInfoDoubleData`. Доступ к числовому значению осуществляется через атрибут `.value`.

## 🧱 Связанные enum (из proto)

> **Примечание:** В Python-коде используйте полный путь enum из модуля market_info.

### `SymbolInfoDoubleProperty`

Определено в `mt5-term-api-market-info.proto`.

### Свойства цены

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_BID` | 0 | Текущая цена Bid |
| `SYMBOL_BIDHIGH` | 1 | Максимальный Bid за день |
| `SYMBOL_BIDLOW` | 2 | Минимальный Bid за день |
| `SYMBOL_ASK` | 3 | Текущая цена Ask |
| `SYMBOL_ASKHIGH` | 4 | Максимальный Ask за день |
| `SYMBOL_ASKLOW` | 5 | Минимальный Ask за день |
| `SYMBOL_LAST` | 6 | Цена последней сделки |
| `SYMBOL_LASTHIGH` | 7 | Максимальный Last за день |
| `SYMBOL_LASTLOW` | 8 | Минимальный Last за день |

### Свойства объёма

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_VOLUME_REAL` | 9 | Реальный объём за день |
| `SYMBOL_VOLUMEHIGH_REAL` | 10 | Максимальный реальный объём за день |
| `SYMBOL_VOLUMELOW_REAL` | 11 | Минимальный реальный объём за день |
| `SYMBOL_VOLUME_MIN` | 22 | Минимальный объём для сделки |
| `SYMBOL_VOLUME_MAX` | 23 | Максимальный объём для сделки |
| `SYMBOL_VOLUME_STEP` | 24 | Минимальный шаг изменения объёма |
| `SYMBOL_VOLUME_LIMIT` | 25 | Максимальный допустимый совокупный объём |

### Торговые свойства

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_POINT` | 13 | Значение пункта символа |
| `SYMBOL_TRADE_TICK_VALUE` | 14 | Рассчитанная стоимость тика для позиции |
| `SYMBOL_TRADE_TICK_VALUE_PROFIT` | 15 | Рассчитанная стоимость тика для прибыли |
| `SYMBOL_TRADE_TICK_VALUE_LOSS` | 16 | Рассчитанная стоимость тика для убытка |
| `SYMBOL_TRADE_TICK_SIZE` | 17 | Минимальное изменение цены |
| `SYMBOL_TRADE_CONTRACT_SIZE` | 18 | Размер торгового контракта |
| `SYMBOL_TRADE_ACCRUED_INTEREST` | 19 | Накопленный процент |
| `SYMBOL_TRADE_FACE_VALUE` | 20 | Номинальная стоимость |
| `SYMBOL_TRADE_LIQUIDITY_RATE` | 21 | Коэффициент ликвидности |

### Ставки свопов

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_SWAP_LONG` | 26 | Значение свопа для длинной позиции |
| `SYMBOL_SWAP_SHORT` | 27 | Значение свопа для короткой позиции |
| `SYMBOL_SWAP_SUNDAY` | 28 | Значение свопа за воскресенье |
| `SYMBOL_SWAP_MONDAY` | 29 | Значение свопа за понедельник |
| `SYMBOL_SWAP_TUESDAY` | 30 | Значение свопа за вторник |
| `SYMBOL_SWAP_WEDNESDAY` | 31 | Значение свопа за среду |
| `SYMBOL_SWAP_THURSDAY` | 32 | Значение свопа за четверг |
| `SYMBOL_SWAP_FRIDAY` | 33 | Значение свопа за пятницу |
| `SYMBOL_SWAP_SATURDAY` | 34 | Значение свопа за субботу |

### Требования к марже

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_MARGIN_INITIAL` | 35 | Начальная маржа |
| `SYMBOL_MARGIN_MAINTENANCE` | 36 | Поддерживающая маржа |
| `SYMBOL_MARGIN_HEDGED` | 48 | Маржа при хеджировании |

### Свойства сессии

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_SESSION_VOLUME` | 37 | Суммарный объём текущей сессии |
| `SYMBOL_SESSION_TURNOVER` | 38 | Суммарный оборот текущей сессии |
| `SYMBOL_SESSION_INTEREST` | 39 | Суммарный открытый интерес |
| `SYMBOL_SESSION_BUY_ORDERS_VOLUME` | 40 | Текущий объём ордеров на покупку |
| `SYMBOL_SESSION_SELL_ORDERS_VOLUME` | 41 | Текущий объём ордеров на продажу |
| `SYMBOL_SESSION_OPEN` | 42 | Цена открытия текущей сессии |
| `SYMBOL_SESSION_CLOSE` | 43 | Цена закрытия текущей сессии |
| `SYMBOL_SESSION_AW` | 44 | Средневзвешенная цена |
| `SYMBOL_SESSION_PRICE_SETTLEMENT` | 45 | Расчётная цена текущей сессии |
| `SYMBOL_SESSION_PRICE_LIMIT_MIN` | 46 | Минимальная цена текущей сессии |
| `SYMBOL_SESSION_PRICE_LIMIT_MAX` | 47 | Максимальная цена текущей сессии |

### Аналитика цены и опционы

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SYMBOL_OPTION_STRIKE` | 12 | Страйк-цена опциона |
| `SYMBOL_PRICE_CHANGE` | 49 | Изменение цены в % |
| `SYMBOL_PRICE_VOLATILITY` | 50 | Волатильность цены в % |
| `SYMBOL_PRICE_THEORETICAL` | 51 | Теоретическая цена опциона |
| `SYMBOL_PRICE_DELTA` | 52 | Дельта опциона/варранта |
| `SYMBOL_PRICE_THETA` | 53 | Тета опциона/варранта |
| `SYMBOL_PRICE_GAMMA` | 54 | Гамма опциона/варранта |
| `SYMBOL_PRICE_VEGA` | 55 | Вега опциона/варранта |
| `SYMBOL_PRICE_RHO` | 56 | Ро опциона/варранта |
| `SYMBOL_PRICE_OMEGA` | 57 | Омега опциона/варранта |
| `SYMBOL_PRICE_SENSITIVITY` | 58 | Чувствительность опциона/варранта |
| `SYMBOL_COUNT` | 59 | Общее количество свойств |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Доступ к ценовым константам
bid_property = market_info_pb2.SYMBOL_BID  # = 0
ask_property = market_info_pb2.SYMBOL_ASK  # = 3

# Использование в вызове метода
bid_data = await account.symbol_info_double("EURUSD", market_info_pb2.SYMBOL_BID)
print(f"BID: {bid_data.value}")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Доступность свойств:** Не все свойства доступны для всех символов. Проверяйте документацию брокера для свойств, специфичных для символа.
* **Стоимость тика:** Используйте свойства `SYMBOL_TRADE_TICK_VALUE` для точных расчётов прибыли/убытка.
* **Лимиты объёма:** Всегда проверяйте `SYMBOL_VOLUME_MIN`, `SYMBOL_VOLUME_MAX` и `SYMBOL_VOLUME_STEP` перед размещением ордеров.

---

## 🔗 Примеры использования

### 1) Получить цены BID и ASK

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить цену BID (краткий формат - рекомендуется)
bid_data = await account.symbol_info_double("EURUSD", market_info_pb2.SYMBOL_BID)
print(f"BID: {bid_data.value}")

# Получить цену ASK
ask_data = await account.symbol_info_double(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_ASK
)
print(f"ASK: {ask_data.value}")

# Рассчитать спред
spread = ask_data.value - bid_data.value
print(f"Spread: {spread:.5f}")
```

### 2) Получить лимиты объёма для торговли

```python
async def get_volume_limits(account: MT5Account, symbol: str):
    """Получить ограничения по объёму для символа"""

    # Получить минимальный объём
    min_vol_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_MIN
    )

    # Получить максимальный объём
    max_vol_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_MAX
    )

    # Получить шаг объёма
    step_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_STEP
    )

    print(f"Volume limits for {symbol}:")
    print(f"  Min: {min_vol_data.value:.2f} lots")
    print(f"  Max: {max_vol_data.value:.2f} lots")
    print(f"  Step: {step_data.value:.2f} lots")

    return {
        "min": min_vol_data.value,
        "max": max_vol_data.value,
        "step": step_data.value
    }

# Использование:
limits = await get_volume_limits(account, "EURUSD")
```

### 3) Получить ставки свопов

```python
async def get_swap_info(account: MT5Account, symbol: str):
    """Получить ставки свопов для длинной и короткой позиций"""

    # Получить своп для длинной позиции
    long_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_LONG
    )

    # Получить своп для короткой позиции
    short_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_SHORT
    )

    print(f"Swap for {symbol}:")
    print(f"  Long: {long_swap_data.value:.2f}")
    print(f"  Short: {short_swap_data.value:.2f}")

    return {
        "long": long_swap_data.value,
        "short": short_swap_data.value
    }

# Использование:
swaps = await get_swap_info(account, "GBPUSD")
```

### 4) Получить размер тика и размер контракта

```python
async def get_trading_specs(account: MT5Account, symbol: str):
    """Получить размер тика и размер контракта для точных расчётов"""

    # Получить размер тика (минимальное изменение цены)
    tick_size_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_TRADE_TICK_SIZE
    )

    # Получить размер контракта
    contract_size_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_TRADE_CONTRACT_SIZE
    )

    # Получить значение пункта
    point_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_POINT
    )

    print(f"Trading specs for {symbol}:")
    print(f"  Tick size: {tick_size_data.value}")
    print(f"  Contract size: {contract_size_data.value}")
    print(f"  Point value: {point_data.value}")

    return {
        "tick_size": tick_size_data.value,
        "contract_size": contract_size_data.value,
        "point": point_data.value
    }

# Использование:
specs = await get_trading_specs(account, "EURUSD")
```

### 5) Проверить, находится ли цена в пределах лимитов сессии

```python
async def check_price_limits(account: MT5Account, symbol: str, price: float) -> bool:
    """Проверить, находится ли цена в пределах лимитов текущей сессии"""

    # Получить лимиты цены сессии
    min_price_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SESSION_PRICE_LIMIT_MIN
    )

    max_price_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SESSION_PRICE_LIMIT_MAX
    )

    min_price = min_price_data.value
    max_price = max_price_data.value

    if min_price <= price <= max_price:
        print(f"[OK] Price {price} is within limits [{min_price}, {max_price}]")
        return True
    else:
        print(f"[ERROR] Price {price} is outside limits [{min_price}, {max_price}]")
        return False

# Использование:
is_valid = await check_price_limits(account, "EURUSD", 1.08500)
```

---

## Распространённые паттерны

### Проверить объём перед ордером

```python
async def validate_volume(account: MT5Account, symbol: str, volume: float) -> bool:
    """Проверить, соответствует ли объём требованиям символа"""

    min_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_MIN)
    max_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_MAX)
    step_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_STEP)

    min_vol = min_data.value
    max_vol = max_data.value
    step = step_data.value

    # Проверить диапазон
    if volume < min_vol or volume > max_vol:
        print(f"[ERROR] Volume {volume} outside range [{min_vol}, {max_vol}]")
        return False

    # Проверить шаг
    if (volume - min_vol) % step != 0:
        print(f"[ERROR] Volume {volume} doesn't match step {step}")
        return False

    return True
```

### Получить текущую рыночную цену

```python
async def get_market_price(account: MT5Account, symbol: str, side: str) -> float:
    """Получить текущую рыночную цену для покупки или продажи"""

    if side.upper() == "BUY":
        # Для ордеров на покупку используйте цену ASK
        data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_ASK)
    else:
        # Для ордеров на продажу используйте цену BID
        data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_BID)

    return data.value
```

---

## 📚 См. также

* [symbol_info_integer](./symbol_info_integer.md) - Получить целочисленные свойства
* [symbol_info_string](./symbol_info_string.md) - Получить строковые свойства
* [symbol_params_many](./symbol_params_many.md) - Получить все параметры символа сразу
