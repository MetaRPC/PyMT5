## symbol_info_session_quote — Как это работает

---

## 📌 Обзор

Этот пример демонстрирует, как получить **сессии котировок** для торгового символа с помощью низкоуровневого асинхронного метода `symbol_info_session_quote()`.

Метод используется для определения того, **в какие часы терминал публикует котировки** по конкретному символу в определённый день недели.

Важно:

* Это касается *котировок*, а не доступности торговли
* Сессии могут различаться по дням недели
* В один день может быть несколько сессий

---

## Сигнатура метода

```python
async def symbol_info_session_quote(
    symbol: str,
    day_of_week: DayOfWeek,
    session_index: int,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* Метод асинхронный и должен вызываться с `await`
* `symbol` — имя торгового символа (например, `"EURUSD"`)
* `day_of_week` — конкретный день недели
* `session_index` — индекс сессии внутри дня (нумерация начинается с `0`)
* Метод возвращает объект со временем начала и окончания сессии

---

## 🧩 Пример кода — Получение всех недельных сессий котировок

```python
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

        from_hours = getattr(session, "from").seconds // 3600
        from_mins = (getattr(session, "from").seconds % 3600) // 60
        to_hours = session.to.seconds // 3600
        to_mins = (session.to.seconds % 3600) // 60

        print(f"  {day_name:10s} {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
    except Exception:
        print(f"  {day_name:10s} No session")
```

В этом примере для каждого дня недели запрашивается **первая сессия котировок (`session_index = 0`)**.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Перебор дней недели

```python
for day_enum, day_name in days.items():
```

Код последовательно перебирает все дни недели.

* `day_enum` используется при вызове API
* `day_name` используется только для форматированного вывода

Каждый день обрабатывается независимо.

---

### 2️⃣ Запрос сессии котировок

```python
session = await account.symbol_info_session_quote(
    symbol="EURUSD",
    day_of_week=day_enum,
    session_index=0
)
```

На этом шаге выполняется один асинхронный вызов.

Метод отвечает на вопрос:

> *Есть ли у этого символа в этот день сессия котировок с индексом 0?*

Если сессия существует:

* Возвращается объект со временем начала и окончания

Если сессии нет:

* Сервер возвращает ошибку
* Управление переходит в `except`

---

### 3️⃣ Формат времени сессии

```python
from_hours = getattr(session, "from").seconds // 3600
from_mins = (getattr(session, "from").seconds % 3600) // 60
```

Время начала и окончания сессии возвращается как **количество секунд от начала дня**.

Преобразование в формат `HH:MM` выполняется полностью на стороне пользовательского кода.

API возвращает только сырые значения времени.

---

### 4️⃣ Вывод информации о сессии

```python
print(f"  {day_name:10s} {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
```

Если сессия существует:

* Выводится день недели
* Выводится интервал котировок

Это чисто визуальное представление данных.

---

### 5️⃣ Обработка отсутствующей сессии

```python
except Exception:
    print(f"  {day_name:10s} No session")
```

Если у данного дня нет сессии котировок с индексом `0`:

* Исключение перехватывается
* Выводится сообщение `No session`

Отсутствие сессии считается нормальной ситуацией.

---

## Итог

В этом примере `symbol_info_session_quote()` используется для получения информации о сессиях котировок для торгового символа.

Метод возвращает время начала и окончания одной сессии для указанного дня недели и индекса, а вся логика перебора дней, форматирования времени и обработки отсутствующих сессий остаётся на стороне пользовательского кода.
