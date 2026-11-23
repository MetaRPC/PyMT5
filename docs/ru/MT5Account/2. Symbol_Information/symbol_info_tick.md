# Получение текущего тика символа

> **Запрос:** получить данные текущего тика для символа (bid, ask, last, объём, время).

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_tick(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoTick` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoTick(SymbolInfoTickRequest) -> SymbolInfoTickRequestReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoTick(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить последний снимок тика для символа с ценами bid/ask, объёмом и метками времени.
* **Зачем это нужно.** Получить данные о ценах в реальном времени для котировок, расчёта спреда, проверки актуальности перед торговлей.
* **Когда использовать.** Используйте для одиночных запросов тика. Для непрерывных обновлений используйте метод стриминга `on_symbol_tick()`.

---

## 🎯 Назначение

Используйте для получения текущих рыночных данных:

* Отображать текущие цены bid/ask в UI
* Рассчитывать текущий спред
* Проверять актуальность котировки (возраст тика)
* Получать цену и объёмы последней сделки
* Проверять рыночные данные перед размещением ордера
* Отслеживать метки времени тиков для оценки задержки

---

## 📚 Руководство

Подробное построчное объяснение с примерами см.:
**-> [symbol_info_tick - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_tick(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.MrpcMqlTick
```

**Сообщение запроса:**

```protobuf
message SymbolInfoTickRequest {
  string symbol = 1;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoTickRequestReply {
  oneof response {
    MrpcMqlTick data = 1;
    Error error = 2;
  }
}

message MrpcMqlTick {
  int64 time = 1;
  double bid = 2;
  double ask = 3;
  double last = 4;
  uint64 volume = 5;
  int64 time_msc = 6;
  uint32 flags = 7;
  double volume_real = 8;
}
```

---

## 🔽 Вход

| Параметр    | Тип                     | Описание             |
| ----------- | ----------------------- | -------------------- |
| `symbol`    | `str` (обязательно)     | Имя символа          |
| `deadline`    | `datetime` (необязательно)        | Крайний срок для gRPC-вызова (datetime в UTC) |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции |

---

## ⬆️ Выход

| Поле          | Тип      | Python-тип  | Описание                                         |
| ------------- | -------- | ----------- | ------------------------------------------------ |
| `time`        | `int64`  | `int`       | Время тика, Unix, в часовом поясе сервера брокера (секунды)             |
| `time_utc`    | `int64`  | `int`       | `time` в UTC (тот же момент)     |
| `bid`         | `double` | `float`     | Текущая лучшая цена bid                          |
| `ask`         | `double` | `float`     | Текущая лучшая цена ask                          |
| `last`        | `double` | `float`     | Цена последней сделки (если применимо)           |
| `volume`      | `uint64` | `int`       | Тиковый объём (количество тиков)                 |
| `time_msc`    | `int64`  | `int`       | Время тика в часовом поясе сервера брокера (миллисекунды)        |
| `time_msc_utc`| `int64`  | `int`       | `time_msc` в UTC (тот же момент)|
| `flags`       | `uint32` | `int`       | Битовая маска флагов тика (флаги тика MT5)       |
| `volume_real` | `double` | `float`     | Реальный объём (если предоставлен брокером)      |

**Возвращаемое значение:** Метод возвращает объект `MrpcMqlTick` со всеми полями данных тика.

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Тайм-аут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до тайм-аута сервера).
* **Синхронизация символа:** Символ должен быть выбран и синхронизирован для получения действительных данных. Если bid/ask равны нулю, сначала вызовите `symbol_select()` и `symbol_is_synchronized()`.
* **Поля времени:** `time` (секунды) и `time_msc` (миллисекунды) — метки времени Unix в часовом поясе сервера брокера. Для тех же моментов в UTC используйте `time_utc` / `time_msc_utc`.
* **Расчёт спреда:** Спред = `ask - bid`. Средняя цена = `(ask + bid) / 2`.
* **Поля объёма:** `volume` — это количество тиков (uint64), `volume_real` — фактический торгуемый объём (double).
* **Поле flags:** Битовая маска, указывающая свойства тика (изменение bid, изменение ask, изменение last, изменение объёма).
* **Проверка актуальности:** Сравните `time` с текущей меткой времени для обнаружения устаревших данных.
* **Нулевые значения:** Если данные тика нулевые, символ может быть не синхронизирован или не выбран.

---

## 🔗 Примеры использования

### 1) Получить текущие bid/ask и спред

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить текущий тик
tick = await account.symbol_info_tick(symbol="EURUSD")

print(f"Symbol: EURUSD")
print(f"  Bid: {tick.bid}")
print(f"  Ask: {tick.ask}")
print(f"  Spread: {tick.ask - tick.bid}")
print(f"  Mid: {(tick.bid + tick.ask) / 2}")
```

### 2) Проверить актуальность тика

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Получить тик и проверить его возраст
tick = await account.symbol_info_tick(symbol="XAUUSD")

if tick.time_utc > 0:
    current_time = datetime.now(timezone.utc).timestamp()
    age_seconds = int(current_time - tick.time_utc)

    print(f"Tick age: {age_seconds} seconds")

    if age_seconds > 5:
        print("Warning: Tick data may be stale!")
    else:
        print("Tick data is fresh")
else:
    print("No tick time available")
```

### 3) Убедиться, что символ синхронизирован перед получением тика

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

symbol = "BTCUSD"

# Проверить, синхронизирован ли символ
sync_status = await account.symbol_is_synchronized(symbol)

if not sync_status.is_synchronized:
    print(f"Symbol {symbol} not synchronized, selecting...")

    # Выбрать символ
    await account.symbol_select(symbol, True)

    # Дождаться синхронизации
    sync_status = await account.symbol_is_synchronized(symbol)
    print(f"Synchronized: {sync_status.is_synchronized}")

# Теперь получить тик
tick = await account.symbol_info_tick(symbol)
print(f"{symbol} - Bid: {tick.bid}, Ask: {tick.ask}")
```

### 4) Показать информацию об объёме

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить тик с данными об объёме
tick = await account.symbol_info_tick(symbol="EURUSD")

print(f"Volume Information:")
print(f"  Tick volume (count): {tick.volume}")
print(f"  Real volume: {tick.volume_real}")
print(f"  Last trade price: {tick.last}")
```

### 5) Преобразовать метки времени в читаемый формат

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Получить тик
tick = await account.symbol_info_tick(symbol="GBPUSD")

# Преобразовать метки времени
if tick.time_utc > 0:
    time_dt = datetime.fromtimestamp(tick.time_utc, tz=timezone.utc)
    print(f"Tick time: {time_dt.isoformat()}")

if tick.time_msc_utc > 0:
    time_msc_dt = datetime.fromtimestamp(tick.time_msc_utc / 1000, tz=timezone.utc)
    print(f"Tick time (ms): {time_msc_dt.isoformat()}")
    print(f"Milliseconds precision: {tick.time_msc_utc % 1000}ms")
```

### 6) Получить тик с тайм-аутом

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone
import asyncio

# Создать событие отмены
cancel_event = asyncio.Event()

# Задать крайний срок
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    tick = await account.symbol_info_tick(
        symbol="EURUSD",
        deadline=deadline,
        cancellation_event=cancel_event
    )
    print(f"Tick retrieved: Bid={tick.bid}, Ask={tick.ask}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 7) Проверить данные тика перед торговлей

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

async def validate_tick(account, symbol: str) -> bool:
    """Проверить, что данные тика актуальны и действительны для торговли"""
    try:
        tick = await account.symbol_info_tick(symbol)

        # Проверить, что bid/ask не равны нулю
        if tick.bid <= 0 or tick.ask <= 0:
            print(f"Invalid prices: bid={tick.bid}, ask={tick.ask}")
            return False

        # Проверить, что спред разумный (не ноль, не слишком широкий)
        spread = tick.ask - tick.bid
        if spread <= 0:
            print(f"Invalid spread: {spread}")
            return False

        # Проверить актуальность тика (менее 10 секунд)
        if tick.time_utc > 0:
            current_time = datetime.now(timezone.utc).timestamp()
            age = current_time - tick.time_utc

            if age > 10:
                print(f"Tick too old: {age} seconds")
                return False

        print(f"Tick validation passed")
        return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False

# Использование
if await validate_tick(account, "EURUSD"):
    print("Ready to place order")
else:
    print("Tick validation failed, cannot trade")
```

---

## 📚 См. также

* [symbol_is_synchronized](./symbol_is_synchronized.md) - Проверить статус синхронизации символа
* [symbol_select](./symbol_select.md) - Выбрать/отменить выбор символа в Market Watch
* [on_symbol_tick](../6. Streaming_Methods/on_symbol_tick.md) - Подписаться на обновления тиков в реальном времени
* [symbol_info_double](./symbol_info_double.md) - Получить свойства символа типа double
