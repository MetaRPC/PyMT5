# MT5Account - Методы стриминга - Обзор

> Потоки в реальном времени: тики, сделки, обновления прибыли, журнал транзакций. Используйте эту страницу, чтобы выбрать подходящий API для подписок в реальном времени.

## 📁 Что здесь находится

### Обновления цен в реальном времени

* **[on_symbol_tick](./on_symbol_tick.md)** - поток тиков для символов в реальном времени.

### Торговые события

* **[on_trade](./on_trade.md)** - изменения позиций/ордеров (открытие, закрытие, модификация).
* **[on_trade_transaction](./on_trade_transaction.md)** - подробный журнал транзакций (полный аудиторский след).

### Мониторинг позиций

* **[on_position_profit](./on_position_profit.md)** - периодические обновления прибыли/убытка.
* **[on_positions_and_pending_orders_tickets](./on_positions_and_pending_orders_tickets.md)** - периодические списки тикетов (облегчённый вариант).

---

## 📚 Пошаговые руководства

**Примечание:** Методы стриминга - это API на основе асинхронных генераторов. Смотрите страницы отдельных методов для подробных примеров паттернов asyncio и обработки событий.

* **[on_symbol_tick](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_symbol_tick_HOW.md)** - Подробные примеры стриминга тиков
* **[on_trade](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW.md)** - Паттерны мониторинга торговых событий
* **[on_trade_transaction](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW.md)** - Примеры логирования транзакций
* **[on_position_profit](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW.md)** - Паттерны мониторинга P/L
* **[on_positions_and_pending_orders_tickets](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW.md)** - Примеры отслеживания тикетов

---

## 🧭 Простыми словами

* **on_symbol_tick** -> **стриминг живых цен** для символов (обновления bid, ask, объёма).
* **on_trade** -> **мониторинг торговых событий** (позиция открыта/закрыта/изменена).
* **on_trade_transaction** -> **подробный аудиторский журнал** всех торговых операций.
* **on_position_profit** -> **периодические обновления P/L** для открытых позиций.
* **on_positions_and_pending_orders_tickets** -> **периодические списки тикетов** (облегчённый мониторинг).

> Практическое правило: нужны **живые цены** -> `on_symbol_tick`; нужны **уведомления о сделках** -> `on_trade`; нужен **подробный аудит** -> `on_trade_transaction`; нужен **мониторинг P/L** -> `on_position_profit`.

---

## Быстрый выбор

| Если вам нужно...                                | Используйте                                 | Возвращает (асинхронный поток)     | Ключевые входы                      |
| ------------------------------------------------ | ------------------------------------------- | ---------------------------------- | ----------------------------------- |
| Тики цен в реальном времени                      | `on_symbol_tick`                            | OnSymbolTickData                   | Список имён символов                |
| Уведомления о торговых событиях                  | `on_trade`                                  | OnTradeData                        | *(нет)*                             |
| Подробный аудиторский журнал транзакций          | `on_trade_transaction`                      | OnTradeTransactionData             | *(нет)*                             |
| Обновления прибыли/убытка в реальном времени     | `on_position_profit`                        | OnPositionProfitData               | Интервал (мс), флаг ignore_empty    |
| Изменения списка тикетов в реальном времени      | `on_positions_and_pending_orders_tickets`   | OnPositionsAndPendingOrdersTicketsData | Интервал (мс)                   |

---

## ℹ️ Перекрёстные ссылки и нюансы

* **Стриминг = асинхронные генераторы** - Методы возвращают асинхронные генераторы, используйте `async for` для получения данных.
* **Отмена** - Используйте `asyncio.Event` и вызывайте `event.set()`, чтобы корректно остановить потоки.
* **Требуется async/await** - Все методы стриминга должны вызываться с `await` внутри асинхронных функций.
* **on_symbol_tick** - Высокая частота, может генерировать множество обновлений в секунду.
* **on_trade** - Срабатывает при каждом торговом событии (открытие, закрытие, модификация, удаление).
* **on_trade_transaction** - Самый подробный, включает все типы и состояния транзакций.
* **on_position_profit** - Периодические обновления с заданными интервалами (например, каждые 500 мс).
* **Управление ресурсами** - Всегда отменяйте потоки по завершении, чтобы закрыть соединения и освободить ресурсы.
* **Обработка ошибок** - Ошибки выбрасываются как исключения - оборачивайте в try/except для обработки.
* **Автоматическое переподключение** - Все потоки имеют встроенное переподключение через `execute_stream_with_reconnect`.

---

## 🟢 Минимальные сниппеты

```python
import asyncio
from MetaRpcMT5 import MT5Account

# Стриминг живых тиков для EURUSD
async def stream_ticks():
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
        async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
            tick = tick_data.symbol_tick
            print(f"EURUSD: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        await account.channel.close()

asyncio.run(stream_ticks())
```

```python
# Мониторинг торговых событий
async def monitor_trades():
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
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            if event.new_positions:
                print(f"New positions: {len(event.new_positions)}")
            if event.disappeared_positions:
                print(f"Closed positions: {len(event.disappeared_positions)}")

    finally:
        await account.channel.close()

asyncio.run(monitor_trades())
```

```python
# Мониторинг прибыли/убытка позиций
async def monitor_pnl():
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
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            for pos in update.updated_positions:
                print(f"#{pos.ticket} ({pos.position_symbol}): ${pos.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(monitor_pnl())
```

```python
# Мониторинг тикетов позиций
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

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            print(f"Open positions: {len(update.position_tickets)}")
            print(f"Pending orders: {len(update.pending_order_tickets)}")

    finally:
        await account.channel.close()

asyncio.run(monitor_tickets())
```

```python
# Подробный журнал транзакций
async def transaction_log():
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
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction
            print(f"Transaction: Order #{tx.order_ticket}, "
                  f"Deal #{tx.deal_ticket}, State: {tx.order_state}")

    finally:
        await account.channel.close()

asyncio.run(transaction_log())
```

```python
# Несколько потоков с отменой
async def multiple_streams():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    cancel_event = asyncio.Event()

    async def stop_after(seconds):
        await asyncio.sleep(seconds)
        cancel_event.set()

    async def stream_ticks():
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"[TICK] {tick.bid:.5f}")

    async def stream_trades():
        async for trade_data in account.on_trade(
            cancellation_event=cancel_event
        ):
            print(f"[TRADE] Event received")

    try:
        # Запускаем несколько потоков одновременно
        await asyncio.gather(
            stream_ticks(),
            stream_trades(),
            stop_after(30)  # Остановить все через 30 секунд
        )
    finally:
        await account.channel.close()

asyncio.run(multiple_streams())
```

```python
# Использование события отмены для корректного завершения
async def stream_with_cancellation():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    cancel_event = asyncio.Event()

    async def handle_keyboard_interrupt():
        """Wait for Ctrl+C and trigger cancellation"""
        try:
            await asyncio.Event().wait()  # Ждём бесконечно
        except asyncio.CancelledError:
            cancel_event.set()

    try:
        # Создаём задачу для обработки прерывания с клавиатуры
        interrupt_task = asyncio.create_task(handle_keyboard_interrupt())

        # Стриминг с поддержкой отмены
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD", "GBPUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"{tick.symbol}: {tick.bid:.5f}")

        interrupt_task.cancel()

    except KeyboardInterrupt:
        cancel_event.set()
        print("\nGracefully stopping stream...")

    finally:
        await account.channel.close()

asyncio.run(stream_with_cancellation())
```

---

## 📚 См. также

* **Информация о счёте:** [account_summary](../1.%20Account_Information/account_summary.md) - получить текущее состояние счёта
* **Позиции:** [opened_orders](../3.%20Positions_Orders/opened_orders.md) - получить снимок текущих позиций
* **Информация о символе:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - получить снимок текущей цены
