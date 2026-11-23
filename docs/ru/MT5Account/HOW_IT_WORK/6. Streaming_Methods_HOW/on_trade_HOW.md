## on_trade — Как это работает

---

## 📌 Обзор

`on_trade()` — это низкоуровневый стриминговый метод для подписки на **все торговые события счёта** в реальном времени.

Он предоставляет единый поток изменений, относящихся к:

* позициям
* ордерам
* сделкам

Метод не разделяет события на разные потоки и не выполняет бизнес-логику. Он лишь **фиксирует факт изменения торгового состояния**, оставляя интерпретацию и реакцию полностью на стороне пользователя.

В этом примере `on_trade()` используется как **универсальный торговый логгер**, отслеживающий и отображающий все типы торговых событий.

---

## Сигнатура метода

```python
async def on_trade(
    cancellation_event: Optional[asyncio.Event] = None,
):
    -> AsyncIterator[OnTradeData]
```

Ключевые особенности:

* асинхронный стриминговый метод (`async for`)
* возвращает поток торговых событий счёта
* объединяет позиции, ордера и сделки
* не имеет встроенного таймаута
* может быть остановлен через `cancellation_event` или внешнее прерывание

---

## 🧩 Пример кода — Логгер торговых событий

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_trade_events():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    event_count = 0

    try:
        async for trade_data in account.on_trade():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event = trade_data.event_data

            for pos in event.new_positions:
                event_count += 1
                print(f"[{timestamp}] NEW_POSITION | Index: {pos.index}")

            for pos in event.disappeared_positions:
                event_count += 1
                print(f"[{timestamp}] CLOSED_POSITION | Index: {pos.index}")

            for pos in event.updated_positions:
                event_count += 1
                print(f"[{timestamp}] UPDATED_POSITION | Index: {pos.index}")

            for order in event.new_orders:
                event_count += 1
                print(f"[{timestamp}] NEW_ORDER | Index: {order.index}")

            for order in event.state_changed_orders:
                event_count += 1
                print(f"[{timestamp}] ORDER_STATE_CHANGE | Index: {order.index}")

            for deal in event.new_history_deals:
                event_count += 1
                print(f"[{timestamp}] NEW_DEAL | Index: {deal.index}")

            if event_count % 10 == 0:
                print(f"\n--- Total events logged: {event_count} ---\n")

    except KeyboardInterrupt:
        print(f"\nStopping logger. Total events: {event_count}")

    finally:
        await account.channel.close()

asyncio.run(log_trade_events())
```

---

## 🟢 Подробное объяснение

---

### 1️⃣ Подписка на торговые события

```python
async for trade_data in account.on_trade():
```

Создаётся подписка на поток торговых изменений:

* сервер присылает обновления по любому торговому событию
* поток работает непрерывно
* каждая итерация — это **пакет изменений**, а не одно событие

---

### 2️⃣ Контейнер событий `event_data`

```python
event = trade_data.event_data
```

`event_data` содержит списки изменений, сгруппированные по типам:

* `new_positions`
* `disappeared_positions`
* `updated_positions`
* `new_orders`
* `state_changed_orders`
* `new_history_deals`

Каждый список может быть пустым или содержать несколько элементов.

---

### 3️⃣ Обработка событий как списков

```python
for pos in event.new_positions:
```

Одно торговое обновление может включать **несколько событий одного типа**.

Поэтому:

* обработка всегда выполняется через циклы
* нельзя предполагать один объект на обновление
* код устойчив к высокой торговой активности

---

### 4️⃣ Логирование фактов событий

Для каждого обнаруженного события:

* записывается локальное время
* инкрементируется счётчик событий
* отображается тип события и его индекс

Пример записи журнала:

```
[2026-02-05 12:01:22] NEW_POSITION | Index: 123456
```

---

### 5️⃣ Счётчик событий

```python
event_count += 1
```

Счётчик используется для:

* мониторинга активности потока
* отладочной статистики
* периодического вывода состояния логгера

```python
if event_count % 10 == 0:
```

Каждые 10 событий отображается промежуточная сводка.

---

### 6️⃣ Завершение потока

В этом примере поток считается бесконечным:

* завершение выполняется вручную (`Ctrl+C`)
* `KeyboardInterrupt` явно перехватывается
* соединение корректно закрывается

---

## Итоговая модель ответственности

**`on_trade()`**:

* поставляет торговые события
* объединяет позиции, ордера и сделки
* не интерпретирует изменения
* не принимает торговых решений

**Пользовательский код**:

* выбирает, какие события обрабатывать
* реализует логику реакции или логирования
* управляет временем жизни потока

---

## Итог

Этот пример иллюстрирует паттерн стриминга единого потока торговых событий:

**подписаться → получать торговые события → классифицировать по типу → обрабатывать каждую категорию**

Ключевые моменты:

* `on_trade()` поставляет единый поток всей торговой активности (позиции, ордера, сделки)
* каждое обновление может содержать несколько типов событий одновременно
* пользовательский код отвечает за:
  * перебор списков событий (`new_positions`, `disappeared_positions` и т. д.)
  * классификацию типов событий
  * реализацию бизнес-логики для каждого типа события
  * логирование или реакцию на изменения

API выступает исчерпывающим источником торговых событий, объединяя позиции, ордера и сделки в единый поток, тогда как вся обработка событий и бизнес-логика полностью остаются на стороне пользователя.
