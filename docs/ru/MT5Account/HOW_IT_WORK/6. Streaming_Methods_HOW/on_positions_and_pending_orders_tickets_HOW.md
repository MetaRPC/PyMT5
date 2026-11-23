## on_positions_and_pending_orders_tickets — Как это работает

---

## 📌 Обзор

Этот пример демонстрирует **полный сценарий использования** стримингового низкоуровневого метода `on_positions_and_pending_orders_tickets()` для отслеживания изменений торгового состояния счёта и преобразования этих изменений в пользовательские события.

Ключевая идея примера:

> Сервер **не сообщает, что именно произошло** — он лишь возвращает текущее состояние.
> Вся интерпретация выполняется на стороне клиента.

---

## Сигнатура метода

```python
async def on_positions_and_pending_orders_tickets(
    interval_ms: int,
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnPositionsAndPendingOrdersTicketsData]
```

---

## 🧩 Пример кода — Логгер изменений тикетов в файл

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_ticket_changes():
    prev_positions = set()
    prev_orders = set()

    with open('ticket_changes.log', 'w') as logfile:
        logfile.write("Timestamp,Event,Ticket\n")

        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            timestamp = datetime.now().isoformat()

            current_positions = set(update.position_tickets)
            current_orders = set(update.pending_order_tickets)

            for ticket in current_positions - prev_positions:
                logfile.write(f"{timestamp},POSITION_OPENED,{ticket}\n")
                logfile.flush()

            for ticket in prev_positions - current_positions:
                logfile.write(f"{timestamp},POSITION_CLOSED,{ticket}\n")
                logfile.flush()

            for ticket in current_orders - prev_orders:
                logfile.write(f"{timestamp},ORDER_CREATED,{ticket}\n")
                logfile.flush()

            for ticket in prev_orders - current_orders:
                logfile.write(f"{timestamp},ORDER_REMOVED,{ticket}\n")
                logfile.flush()

            prev_positions = current_positions
            prev_orders = current_orders

asyncio.run(log_ticket_changes())
```

---

## 🟢 Подробное пошаговое объяснение

---

### 1️⃣ Инициализация пользовательского состояния

```python
prev_positions = set()
prev_orders = set()
```

Пользовательский код заранее создаёт **локальное состояние**, которое будет использоваться для сравнения.

Метод API **не хранит историю** и ничего не знает о предыдущих вызовах.

---

### 2️⃣ Открытие файла журнала

```python
with open('ticket_changes.log', 'w') as logfile:
```

Это целиком зона ответственности пользователя:

* формат файла
* способ хранения
* политика записи

API в этом не участвует.

---

### 3️⃣ Подписка на стриминговые обновления

```python
async for update in account.on_positions_and_pending_orders_tickets(...):
```

На этой стадии:

* создаётся долгоживущий поток
* сервер периодически присылает **полный снимок**
* цикл продолжается до отмены

---

### 4️⃣ Получение текущего снимка

```python
current_positions = set(update.position_tickets)
current_orders = set(update.pending_order_tickets)
```

Каждое обновление содержит:

* полный список идентификаторов тикетов позиций
* полный список идентификаторов тикетов отложенных ордеров

Это **состояние**, а не событие.

---

### 5️⃣ Пользовательская логика diff

```python
current_positions - prev_positions
prev_positions - current_positions
```

Здесь происходит ключевая работа пользователя:

* определить, что появилось
* определить, что исчезло

API **намеренно** не делает этого за пользователя.

---

### 6️⃣ Интерпретация diff как событий

```python
POSITION_OPENED
POSITION_CLOSED
ORDER_CREATED
ORDER_REMOVED
```

На этой стадии пользователь:

* придаёт изменениям смысл
* вводит собственные типы событий
* решает, что считать важным

---

### 7️⃣ Запись результата

```python
logfile.write(...)
logfile.flush()
```

Результат обработки:

* сохраняется
* может быть передан дальше
* может использоваться для аудита

---

### 8️⃣ Обновление базового состояния

```python
prev_positions = current_positions
prev_orders = current_orders
```

Это замыкает цикл обработки и готовит код к следующему снимку.

---

## Роль низкоуровневого метода

**`on_positions_and_pending_orders_tickets()`**:

* возвращает текущее состояние идентификаторов тикетов
* не анализирует изменения
* не классифицирует события

**Пользовательская логика**:

* хранит состояние
* вычисляет diff
* интерпретирует события
* решает, что с ними делать

---

## Итог

Этот метод — основа для построения **логики на основе состояния**:

* логгеры
* аудит
* оповещения
* синхронизация с внешними системами

Он намеренно остаётся низкоуровневым и делегирует всю семантику пользователю.
