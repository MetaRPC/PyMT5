# Получение времени котировочной сессии символа

> **Запрос:** получить время начала и окончания котировочной сессии для символа.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_session_quote(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoSessionQuote` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoSessionQuote(SymbolInfoSessionQuoteRequest) -> SymbolInfoSessionQuoteReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoSessionQuote(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить время начала и окончания котировочной сессии для символа в конкретный день недели.
* **Зачем это нужно.** Знать, когда можно получать котировки по символам, понимать часы работы рынка.
* **Когда использовать.** Используйте для проверки доступности котировок символа, планирования расписаний автоматической торговли, проверки времени открытия рынка.

---

## 🎯 Назначение

Используйте для запроса расписаний котировочных сессий:

* Получить часы котировочной сессии символа для каждого дня
* Проверить, когда доступны обновления цен
* Проверить время открытия/закрытия рынка
* Спланировать расписания мониторинга котировок
* Понять перерывы в сессии
* Согласовать с торговыми сессиями

---

## 📚 Руководство

Подробное построчное объяснение с примерами см.:
**-> [symbol_info_session_quote - How it works](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_session_quote(
    self,
    symbol: str,
    day_of_week: market_info_pb2.DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoSessionQuoteData
```

**Сообщение запроса:**

```protobuf
message SymbolInfoSessionQuoteRequest {
  string symbol = 1;
  DayOfWeek day_of_week = 2;
  uint32 session_index = 3;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoSessionQuoteReply {
  oneof response {
    SymbolInfoSessionQuoteData data = 1;
    Error error = 2;
  }
}

message SymbolInfoSessionQuoteData {
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

**Возвращаемое значение:** Метод возвращает объект `SymbolInfoSessionQuoteData` с полями `from` и `to` типа Timestamp.

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

# Получить котировочную сессию понедельника
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)
print(f"From: {getattr(session, 'from').seconds}s, To: {session.to.seconds}s")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Тайм-аут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до тайм-аута сервера).
* **Формат Timestamp:** Поля `from` и `to` являются объектами `google.protobuf.Timestamp` с атрибутами `seconds` и `nanos`.
* **Интерпретация времени:** Времена представляют секунды от полуночи (00:00) для указанного дня.
* **Индекс сессии:** У большинства символов одна основная сессия (индекс 0). У некоторых может быть несколько сессий (обеденные перерывы и т. д.).
* **Несколько сессий:** Если у символа несколько котировочных сессий в день, используйте разные значения session_index (0, 1, 2...).
* **Часовой пояс:** Времена указаны в часовом поясе сервера брокера, а не в UTC.
* **Нет сессии:** Если сессия не существует, метод может вернуть ошибку или нулевые метки времени.

---

## 🔗 Примеры использования

### 1) Получить котировочную сессию понедельника

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить котировочную сессию понедельника
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

print(f"Monday Quote Session:")
print(f"  From: {getattr(session, 'from').seconds}s ({getattr(session, 'from').seconds // 3600}h:{(getattr(session, 'from').seconds % 3600) // 60}m)")
print(f"  To: {session.to.seconds}s ({session.to.seconds // 3600}h:{(session.to.seconds % 3600) // 60}m)")
```

### 2) Получить все недельные котировочные сессии

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

print("EURUSD Quote Sessions:")
for day_enum, day_name in days.items():
    try:
        session = await account.symbol_info_session_quote(
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

### 3) Преобразовать метку времени в читаемое время

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import time

def timestamp_to_time(timestamp) -> time:
    """Преобразовать protobuf Timestamp в datetime.time"""
    total_seconds = timestamp.seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return time(hour=hours, minute=minutes, second=seconds)

# Получить сессию
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

# Преобразовать в объекты time
from_time = timestamp_to_time(getattr(session, 'from'))
to_time = timestamp_to_time(session.to)

print(f"Quote session: {from_time} - {to_time}")
# Вывод: Quote session: 00:00:00 - 23:59:59
```

### 4) Проверить, есть ли у символа котировочная сессия в конкретный день

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def has_quote_session(account, symbol: str, day_of_week: int) -> bool:
    """Проверить, есть ли у символа котировочная сессия в указанный день"""
    try:
        session = await account.symbol_info_session_quote(
            symbol=symbol,
            day_of_week=day_of_week,
            session_index=0
        )

        # Проверить, есть ли у сессии действительные времена (не ноль)
        if getattr(session, 'from').seconds > 0 or session.to.seconds > 0:
            return True
        return False
    except Exception:
        return False

# Использование
if await has_quote_session(account, "EURUSD", market_info_pb2.SATURDAY):
    print("EURUSD has quotes on Saturday")
else:
    print("EURUSD has NO quotes on Saturday")
```

### 5) Получить сессию с тайм-аутом

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    session = await account.symbol_info_session_quote(
        symbol="GBPUSD",
        day_of_week=market_info_pb2.FRIDAY,
        session_index=0,
        deadline=deadline
    )
    print(f"Session retrieved successfully")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 6) Проверить наличие нескольких сессий (обеденные перерывы)

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def get_all_sessions(account, symbol: str, day_of_week: int):
    """Получить все котировочные сессии символа в конкретный день"""
    sessions = []
    session_index = 0

    while session_index < 10:  # Максимум 10 сессий
        try:
            session = await account.symbol_info_session_quote(
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
sessions = await get_all_sessions(account, "NIKKEI", market_info_pb2.MONDAY)
print(f"Found {len(sessions)} quote session(s):")
for s in sessions:
    from_h = s['from'] // 3600
    from_m = (s['from'] % 3600) // 60
    to_h = s['to'] // 3600
    to_m = (s['to'] % 3600) // 60
    print(f"  Session {s['index']}: {from_h:02d}:{from_m:02d} - {to_h:02d}:{to_m:02d}")
```

---

## 📚 См. также

* [symbol_info_session_trade](./symbol_info_session_trade.md) - Получить время торговой сессии
* [symbol_info_integer](./symbol_info_integer.md) - Получить другие свойства символа типа integer
* [symbol_info_double](./symbol_info_double.md) - Получить свойства символа типа double
