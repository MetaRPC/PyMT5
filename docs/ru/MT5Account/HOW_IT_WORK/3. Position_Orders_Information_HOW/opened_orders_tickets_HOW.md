## opened_orders_tickets — Как это работает

---

## 📌 Обзор

Этот пример показывает, как использовать низкоуровневый асинхронный метод `opened_orders_tickets()` для отслеживания **изменений состояния торгового счёта по идентификаторам (ticket ID)**.

В отличие от `opened_orders()`, который возвращает подробную информацию, этот метод предназначен для **лёгкого мониторинга изменений**:

* появление новых ордеров или позиций
* закрытие существующих

Он особенно полезен для фонового мониторинга и реактивной логики.

---

## Сигнатура метода

```python
async def opened_orders_tickets(
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Ключевые моменты:

* метод асинхронный и вызывается с `await`
* не принимает параметров фильтрации
* возвращает только идентификаторы (тикеты)
* не содержит подробной информации об ордерах или позициях

---

## 🧩 Пример кода — Мониторинг изменений по тикетам

```python
async def monitor_tickets(account: MT5Account, interval: float = 5.0):
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders_tickets()

            current_tickets = set(
                data.opened_orders_tickets + data.opened_position_tickets
            )

            if previous_tickets:
                new = current_tickets - previous_tickets
                closed = previous_tickets - current_tickets

                for ticket in new:
                    print(f"[+] New ticket: #{ticket}")
                for ticket in closed:
                    print(f"[-] Closed ticket: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)
```

Этот пример реализует простой цикл наблюдения для отслеживания изменений торгового состояния.

---

## 🟢 Подробное объяснение

---

### 1️⃣ Хранение предыдущего состояния

```python
previous_tickets = set()
```

* `set` используется для быстрого сравнения
* в нём хранятся тикеты из предыдущей итерации

---

### 2️⃣ Получение текущего списка тикетов

```python
data = await account.opened_orders_tickets()
```

На этом шаге:

* выполняется один асинхронный вызов
* сервер возвращает:

  * `opened_orders_tickets`
  * `opened_position_tickets`

Это два независимых списка числовых идентификаторов.

---

### 3️⃣ Объединение ордеров и позиций

```python
current_tickets = set(
    data.opened_orders_tickets + data.opened_position_tickets
)
```

Здесь:

* списки объединяются
* преобразуются в `set`
* формируется текущее состояние тикетов счёта

---

### 4️⃣ Сравнение состояний

```python
new = current_tickets - previous_tickets
closed = previous_tickets - current_tickets
```

Используется стандартная логика операций над множествами:

* `new` — тикеты, появившиеся с момента последнего опроса
* `closed` — тикеты, которые исчезли

---

### 5️⃣ Реакция на изменения

```python
for ticket in new:
    print(f"[+] New ticket: #{ticket}")
```

Пользовательский код:

* сам решает, как реагировать
* может логировать, обновлять UI, запускать логику

Метод API не интерпретирует изменения.

---

### 6️⃣ Обновление состояния

```python
previous_tickets = current_tickets
```

Текущее состояние сохраняется для следующей итерации цикла.

---

## Роль низкоуровневого метода

Чёткая граница ответственности:

**`opened_orders_tickets()`**:

* возвращает только идентификаторы ордеров и позиций
* не содержит цен, объёмов или прибыли
* не отслеживает изменения во времени

**`monitor_tickets()`**:

* реализует цикл опроса
* сравнивает состояния
* определяет, что появилось и что исчезло
* принимает решения

---

## Итог

Этот пример демонстрирует паттерн **лёгкого мониторинга состояния**:

> **получить идентификаторы → сравнить состояния → отреагировать на изменения**

Метод `opened_orders_tickets()` предоставляет минимальный набор данных для отслеживания изменений, а вся логика мониторинга и интерпретации реализуется на стороне пользовательского кода.
