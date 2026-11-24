# Стриминг тикетов позиций и отложенных ордеров

> **Запрос:** подписаться на периодические обновления идентификаторов тикетов позиций и отложенных ордеров.

**Информация об API:**

* **Python API:** `MT5Account.on_positions_and_pending_orders_tickets(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.SubscriptionService`
* **Proto-определение:** `OnPositionsAndPendingOrdersTickets` (определено в `mt5-term-api-subscriptions.proto`)

### RPC

* **Сервис:** `mt5_term_api.SubscriptionService`
* **Метод:** `OnPositionsAndPendingOrdersTickets(OnPositionsAndPendingOrdersTicketsRequest) -> stream OnPositionsAndPendingOrdersTicketsReply`
* **Низкоуровневый клиент (сгенерированный):** `SubscriptionServiceStub.OnPositionsAndPendingOrdersTickets(request, metadata)`

---

## 💬 Только суть

* **Что это.** Периодический поток идентификаторов тикетов для открытых позиций и отложенных ордеров.
* **Зачем это нужно.** Облегчённый мониторинг позиций/ордеров, обнаружение изменений без полных данных.
* **Периодические обновления.** Снимок отправляется с заданными интервалами (например, каждые 1000 мс).

---

## 🎯 Назначение

Используйте для того, чтобы:

* Отслеживать изменения количества позиций и ордеров
* Обнаруживать открытие новых позиций (появление новых тикетов)
* Обнаруживать закрытие позиций (исчезновение тикетов)
* Облегчённая альтернатива `on_trade`, когда вам нужны только идентификаторы тикетов
* Отслеживать жизненный цикл тикетов без получения полных данных позиции
* Строить эффективные системы обнаружения изменений


```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_positions_and_pending_orders_tickets(
        self,
        interval_ms: int,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to updates of position and pending order ticket IDs.

        Yields:
            OnPositionsAndPendingOrdersTicketsData: Snapshot of tickets.
        """
```

**Сообщение запроса:**

```protobuf
message OnPositionsAndPendingOrdersTicketsRequest {
  int32 timer_period_milliseconds = 1;  // Интервал опроса в миллисекундах
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `interval_ms`        | `int`                          | Интервал опроса в миллисекундах               |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены стриминга (опционально)    |

---

## ⬆️ Выход - Асинхронный генератор

Возвращает асинхронный генератор, который выдаёт объекты `OnPositionsAndPendingOrdersTicketsData`.

**Поля OnPositionsAndPendingOrdersTicketsData:**

| Поле                          | Тип                           | Описание                             |
| ----------------------------- | ----------------------------- | ------------------------------------ |
| `position_tickets`            | `repeated uint64`             | Список идентификаторов тикетов открытых позиций |
| `pending_order_tickets`       | `repeated uint64`             | Список идентификаторов тикетов отложенных ордеров |
| `server_time`                 | `google.protobuf.Timestamp`   | Отметка времени сервера              |
| `terminal_instance_guid_id`   | `str`                         | Идентификатор экземпляра терминала   |


---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OnPositionsAndPendingOrdersTickets - Как это работает](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы стриминга `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_stream_with_reconnect`.
* **Асинхронный генератор:** Метод возвращает асинхронный генератор - используйте `async for` для получения данных.
* **Периодические снимки:** Каждое обновление - это полный снимок (не инкрементальные изменения).
* **Облегчённость:** Возвращает только идентификаторы тикетов - используйте это, когда вам не нужны полные данные позиции/ордера.
* **Обнаружение изменений:** Сравнивайте списки тикетов между обновлениями, чтобы обнаруживать новые/закрытые позиции.
* **Интервал опроса:** Выбирайте интервал в зависимости от ваших потребностей - короче = более частые обновления.
* **Эффективность по ресурсам:** Значительно легче, чем `on_trade` или `on_position_profit`.

---

## 🔗 Примеры использования

### 1) Мониторинг изменений тикетов

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_tickets():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_positions = set()
    prev_orders = set()

    try:
        # Опрашиваем каждую секунду
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            current_positions = set(update.position_tickets)
            current_orders = set(update.pending_order_tickets)

            # Обнаруживаем новые позиции
            new_positions = current_positions - prev_positions
            if new_positions:
                print(f"[NEW] Positions: {new_positions}")

            # Обнаруживаем закрытые позиции
            closed_positions = prev_positions - current_positions
            if closed_positions:
                print(f"[CLOSED] Positions: {closed_positions}")

            # Обнаруживаем новые отложенные ордера
            new_orders = current_orders - prev_orders
            if new_orders:
                print(f"[NEW] Orders: {new_orders}")

            # Обнаруживаем удалённые отложенные ордера
            removed_orders = prev_orders - current_orders
            if removed_orders:
                print(f"[REMOVED] Orders: {removed_orders}")

            # Показываем текущее состояние
            print(f"[STATUS] Positions: {len(current_positions)}, "
                  f"Orders: {len(current_orders)}\n")

            prev_positions = current_positions
            prev_orders = current_orders

    except KeyboardInterrupt:
        print("Stopping monitor...")

    finally:
        await account.channel.close()

asyncio.run(monitor_tickets())
```

### 2) Оповещение об изменении количества позиций

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def alert_on_position_changes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_count = 0

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=500
        ):
            current_count = len(update.position_tickets)

            # Оповещаем об изменениях
            if current_count > prev_count:
                print(f"\n[ALERT] {current_count - prev_count} position(s) OPENED")
                print(f"   Total positions: {current_count}")
                print(f"   Tickets: {list(update.position_tickets)}")

            elif current_count < prev_count:
                print(f"\n[ALERT] {prev_count - current_count} position(s) CLOSED")
                print(f"   Remaining positions: {current_count}")
                print(f"   Tickets: {list(update.position_tickets)}")

            prev_count = current_count

    except KeyboardInterrupt:
        print("\nStopping alerts...")

    finally:
        await account.channel.close()

asyncio.run(alert_on_position_changes())
```

### 3) Отслеживание статистики позиций/ордеров

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def track_ticket_statistics(duration_seconds=300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    stats = {
        'max_positions': 0,
        'max_orders': 0,
        'total_opened': 0,
        'total_closed': 0,
        'updates': 0,
    }

    prev_positions = set()
    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000,
            cancellation_event=cancel_event
        ):
            current_positions = set(update.position_tickets)
            stats['updates'] += 1

            # Обновляем максимальные значения
            stats['max_positions'] = max(stats['max_positions'], len(current_positions))
            stats['max_orders'] = max(stats['max_orders'], len(update.pending_order_tickets))

            # Подсчитываем открытые/закрытые
            stats['total_opened'] += len(current_positions - prev_positions)
            stats['total_closed'] += len(prev_positions - current_positions)

            prev_positions = current_positions

        await stop_task

        # Печатаем статистику
        print("\n" + "=" * 60)
        print("TICKET STATISTICS REPORT")
        print("=" * 60)
        print(f"Duration:          {duration_seconds} seconds")
        print(f"Updates received:  {stats['updates']}")
        print(f"Max positions:     {stats['max_positions']}")
        print(f"Max orders:        {stats['max_orders']}")
        print(f"Total opened:      {stats['total_opened']}")
        print(f"Total closed:      {stats['total_closed']}")
        print("=" * 60)

    finally:
        await account.channel.close()

# Отслеживаем в течение 5 минут
asyncio.run(track_ticket_statistics(300))
```

### 4) Ограничитель количества позиций

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def position_count_limiter(max_positions=5):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=500
        ):
            position_count = len(update.position_tickets)

            if position_count >= max_positions:
                print(f"\n[WARNING] Position limit reached!")
                print(f"   Current positions: {position_count}/{max_positions}")
                print(f"   Tickets: {list(update.position_tickets)}")
                print(f"   [BLOCK] New positions should be blocked\n")
            else:
                available = max_positions - position_count
                print(f"[OK] Positions: {position_count}/{max_positions} "
                      f"({available} slots available)")

    except KeyboardInterrupt:
        print("\nStopping limiter...")

    finally:
        await account.channel.close()

# Оповещаем, когда открыто 5 или более позиций
asyncio.run(position_count_limiter(5))
```

### 5) Логгер изменений тикетов в файл

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_ticket_changes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_positions = set()
    prev_orders = set()

    try:
        with open('ticket_changes.log', 'w') as logfile:
            logfile.write("Timestamp,Event,Ticket\n")

            async for update in account.on_positions_and_pending_orders_tickets(
                interval_ms=1000
            ):
                timestamp = datetime.now().isoformat()
                current_positions = set(update.position_tickets)
                current_orders = set(update.pending_order_tickets)

                # Логируем новые позиции
                for ticket in current_positions - prev_positions:
                    logfile.write(f"{timestamp},POSITION_OPENED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Position opened: {ticket}")

                # Логируем закрытые позиции
                for ticket in prev_positions - current_positions:
                    logfile.write(f"{timestamp},POSITION_CLOSED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Position closed: {ticket}")

                # Логируем новые ордера
                for ticket in current_orders - prev_orders:
                    logfile.write(f"{timestamp},ORDER_CREATED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Order created: {ticket}")

                # Логируем удалённые ордера
                for ticket in prev_orders - current_orders:
                    logfile.write(f"{timestamp},ORDER_REMOVED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Order removed: {ticket}")

                prev_positions = current_positions
                prev_orders = current_orders

    except KeyboardInterrupt:
        print("\nStopping logger...")

    finally:
        await account.channel.close()

asyncio.run(log_ticket_changes())
```

### 6) Облегчённая панель мониторинга позиций

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def position_dashboard():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    start_time = datetime.now()

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            # Очищаем экран
            print("\033[2J\033[H")

            runtime = datetime.now() - start_time
            server_time = datetime.fromtimestamp(update.server_time.seconds)

            print("=" * 70)
            print(f"POSITION MONITOR DASHBOARD")
            print("=" * 70)
            print(f"Runtime:     {runtime}")
            print(f"Server time: {server_time}")
            print(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)

            print(f"\nOpen Positions: {len(update.position_tickets)}")
            if update.position_tickets:
                for i, ticket in enumerate(update.position_tickets, 1):
                    print(f"  {i}. Ticket #{ticket}")
            else:
                print("  (none)")

            print(f"\nPending Orders: {len(update.pending_order_tickets)}")
            if update.pending_order_tickets:
                for i, ticket in enumerate(update.pending_order_tickets, 1):
                    print(f"  {i}. Ticket #{ticket}")
            else:
                print("  (none)")

            print("\n" + "=" * 70)
            print("Press Ctrl+C to stop")

    except KeyboardInterrupt:
        print("\n\nStopping dashboard...")

    finally:
        await account.channel.close()

asyncio.run(position_dashboard())
```

---

## 📚 См. также

* [OpenedOrdersTickets](../3.%20Positions_Orders/opened_orders_tickets.md) - Получить снимок тикетов (однократно)
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Получить полные данные позиций (однократно)
* [OnTrade](./on_trade.md) - Стриминг подробных торговых событий
* [OnPositionProfit](./on_position_profit.md) - Стриминг обновлений прибыли позиций
