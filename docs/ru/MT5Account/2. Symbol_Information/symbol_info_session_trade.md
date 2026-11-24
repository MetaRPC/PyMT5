# Получение времени торговой сессии символа

> **Запрос:** получить время начала и окончания торговой сессии для символа.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_session_trade(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoSessionTrade` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoSessionTrade(SymbolInfoSessionTradeRequest) -> SymbolInfoSessionTradeReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoSessionTrade(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить время начала и окончания торговой сессии для символа в конкретный день недели.
* **Зачем это нужно.** Знать, когда можно размещать сделки по символам, понимать торговые часы в сравнении с часами котировок.
* **Когда использовать.** Используйте для проверки, когда разрешена торговля, проверки времени размещения ордеров, планирования расписаний автоматической торговли.

---

## 🎯 Назначение

Используйте для запроса расписаний торговых сессий:

* Получить часы торговой сессии символа для каждого дня
* Проверить, когда разрешено размещение ордеров
* Проверить торговые часы в сравнении с часами котировок
* Спланировать расписания автоматической торговли
* Понять перерывы в сессии
* Согласовать с часами работы рынка

---

## 📚 Руководство

Подробное построчное объяснение с примерами см.:
**-> [symbol_info_session_trade - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_session_trade(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoSessionTradeData
```

**Сообщение запроса:**

```protobuf
message SymbolInfoSessionTradeRequest {
  string symbol = 1;
  DayOfWeek day_of_week = 2;
  uint32 session_index = 3;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoSessionTradeReply {
  oneof response {
    SymbolInfoSessionTradeData data = 1;
    Error error = 2;
  }
}

message SymbolInfoSessionTradeData {
  google.protobuf.Timestamp from = 1;
  google.protobuf.Timestamp to = 2;
}
```

---

## 🔽 Вход

| Параметр        | Тип                       | Описание                     |
| --------------- | ------------------------- | ---------------------------- |
| `symbol`        | `str` (обязательно)       | Имя символа                  |
| `day_of_week`   | `DayOfWeek` (enum)        | День недели (SUNDAY, MONDAY и т. д.) |
| `session_index` | `int` (обязательно)       | Индекс сессии (обычно 0 для основной сессии) |
| `deadline`    | `datetime` (необязательно)  | Крайний срок для gRPC-вызова (datetime в UTC) |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции |

---

## ⬆️ Выход

| Поле    | Тип         | Python-тип  | Описание              |
| ------- | ----------- | ----------- | --------------------- |
| `from`  | `Timestamp` | `Timestamp` | Время начала сессии (google.protobuf.Timestamp) |
| `to`    | `Timestamp` | `Timestamp` | Время окончания сессии (google.protobuf.Timestamp)   |

**Возвращаемое значение:** Метод возвращает объект `SymbolInfoSessionTradeData` с полями `from` и `to` типа Timestamp.

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В Python-коде используйте константы напрямую из модуля market_info.

### `DayOfWeek`

Определён в `mt5-term-api-market-info.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `SUNDAY` | 0 | Воскресенье |
| `MONDAY` | 1 | Понедельник |
| `TUESDAY` | 2 | Вторник |
| `WEDNESDAY` | 3 | Среда |
| `THURSDAY` | 4 | Четверг |
| `FRIDAY` | 5 | Пятница |
| `SATURDAY` | 6 | Суббота |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить торговую сессию понедельника
session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)
print(f"Trading hours: {getattr(session, 'from').seconds}s - {session.to.seconds}s")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Тайм-аут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до тайм-аута сервера).
* **Формат Timestamp:** Поля `from` и `to` являются объектами `google.protobuf.Timestamp` с атрибутами `seconds` и `nanos`.
* **Интерпретация времени:** Времена представляют секунды от полуночи (00:00) для указанного дня.
* **Индекс сессии:** У большинства символов одна основная сессия (индекс 0). У некоторых может быть несколько сессий (обеденные перерывы и т. д.).
* **Несколько сессий:** Если у символа несколько торговых сессий в день, используйте разные значения session_index (0, 1, 2...).
* **Часовой пояс:** Времена указаны в часовом поясе сервера брокера, а не в UTC.
* **Нет сессии:** Если сессия не существует, метод может вернуть ошибку или нулевые метки времени.
* **Торговые сессии в сравнении с котировочными:** Торговые сессии (когда можно размещать ордера) могут отличаться от котировочных сессий (когда обновляются цены). Используйте оба метода, чтобы понять полное расписание рынка.

---

## 🔗 Примеры использования

### 1) Получить торговую сессию понедельника

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить торговую сессию понедельника
session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Monday Trade Session:")
print(f"  From: {getattr(session, 'from').seconds}s ({getattr(session, 'from').seconds // 3600}h:{(getattr(session, 'from').seconds % 3600) // 60}m)")
print(f"  To: {session.to.seconds}s ({session.to.seconds // 3600}h:{(session.to.seconds % 3600) // 60}m)")
```

### 2) Получить все недельные торговые сессии

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

days = {
    market_info_pb2.SUNDAY: "Sunday",
    market_info_pb2.MONDAY: "Monday",
    market_info_pb2.TUESDAY: "Tuesday",
    market_info_pb2.WEDNESDAY: "Wednesday",
    market_info_pb2.THURSDAY: "Thursday",
    market_info_pb2.FRIDAY: "Friday",
    market_info_pb2.SATURDAY: "Saturday"
}

print("EURUSD Trade Sessions:")
for day_enum, day_name in days.items():
    try:
        session = await account.symbol_info_session_trade(
            symbol="EURUSD",
            day_of_week=day_enum,
            session_index=0
        )

        from_hours = getattr(session, 'from').seconds // 3600
        from_mins = (getattr(session, 'from').seconds % 3600) // 60
        to_hours = session.to.seconds // 3600
        to_mins = (session.to.seconds % 3600) // 60

        print(f"  {day_name:10s} {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
    except Exception as e:
        print(f"  {day_name:10s} No session")
```

### 3) Сравнить торговые и котировочные сессии

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить торговую сессию
trade_session = await account.symbol_info_session_trade(
    symbol="XAUUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

# Получить котировочную сессию
quote_session = await account.symbol_info_session_quote(
    symbol="XAUUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"XAUUSD Monday Sessions:")
print(f"  Trade: {getattr(trade_session, "from").seconds // 3600:02d}:{(getattr(trade_session, "from").seconds % 3600) // 60:02d} - {trade_session.to.seconds // 3600:02d}:{(trade_session.to.seconds % 3600) // 60:02d}")
print(f"  Quote: {getattr(quote_session, "from").seconds // 3600:02d}:{(getattr(quote_session, "from").seconds % 3600) // 60:02d} - {quote_session.to.seconds // 3600:02d}:{(quote_session.to.seconds % 3600) // 60:02d}")

if getattr(trade_session, "from").seconds != getattr(quote_session, "from").seconds:
    print("  Trade and quote sessions differ!")
```

### 4) Проверить, разрешена ли торговля сейчас

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

async def is_trading_allowed(account, symbol: str) -> bool:
    """Проверить, разрешена ли торговля в текущее время"""
    now = datetime.now(timezone.utc)
    day_of_week = now.weekday() + 1  # Понедельник=1 в datetime, Понедельник=1 в enum
    if day_of_week == 7:  # Воскресенье
        day_of_week = 0

    try:
        session = await account.symbol_info_session_trade(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        # Текущее время в секундах от полуночи
        current_seconds = now.hour * 3600 + now.minute * 60 + now.second

        # Проверить, находимся ли мы в пределах торговой сессии
        if getattr(session, 'from').seconds <= current_seconds <= session.to.seconds:
            return True
        return False
    except Exception:
        return False

# Использование
if await is_trading_allowed(account, "EURUSD"):
    print("Trading is ALLOWED")
else:
    print("Trading is CLOSED")
```

### 5) Получить все сессии для дня (несколько сессий)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_trade_sessions(account, symbol: str, day_of_week: int):
    """Получить все торговые сессии символа в конкретный день"""
    sessions = []
    session_index = 0

    while session_index < 10:  # Максимум 10 сессий
        try:
            session = await account.symbol_info_session_trade(
                symbol=symbol,
                day_of_week=day_of_week,
                session_index=session_index
            )

            # Проверить, действительна ли сессия
            if getattr(session, 'from').seconds == 0 and session.to.seconds == 0:
                break

            sessions.append({
                'index': session_index,
                'from': getattr(session, 'from').seconds,
                'to': session.to.seconds
            })
            session_index += 1
        except Exception:
            break

    return sessions

# Использование
sessions = await get_all_trade_sessions(account, "NIKKEI", market_info_pb2.MONDAY)
print(f"Found {len(sessions)} trade session(s):")
for s in sessions:
    from_h = s['from'] // 3600
    from_m = (s['from'] % 3600) // 60
    to_h = s['to'] // 3600
    to_m = (s['to'] % 3600) // 60
    print(f"  Session {s['index']}: {from_h:02d}:{from_m:02d} - {to_h:02d}:{to_m:02d}")
```

### 6) Получить сессию с тайм-аутом

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    session = await account.symbol_info_session_trade(
        symbol="GBPUSD",
        day_of_week=market_info_pb2.FRIDAY,
        session_index=0,
        deadline=deadline
    )
    print(f"Session retrieved successfully")
except Exception as e:
    print(f"Timeout or error: {e}")
```

---

## 📚 См. также

* [symbol_info_session_quote](./symbol_info_session_quote.md) - Получить время котировочной сессии
* [symbol_info_integer](./symbol_info_integer.md) - Получить другие свойства символа типа integer
* [symbol_info_double](./symbol_info_double.md) - Получить свойства символа типа double
