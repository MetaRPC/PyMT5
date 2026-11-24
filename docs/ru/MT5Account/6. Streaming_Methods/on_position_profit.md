# Стриминг прибыли/убытка позиций в реальном времени

> **Запрос:** подписаться на обновления прибыли/убытка открытых позиций в реальном времени.

**Информация об API:**

* **Python API:** `MT5Account.on_position_profit(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.SubscriptionService`
* **Proto-определение:** `OnPositionProfit` (определено в `mt5-term-api-subscriptions.proto`)

### RPC

* **Сервис:** `mt5_term_api.SubscriptionService`
* **Метод:** `OnPositionProfit(OnPositionProfitRequest) -> stream OnPositionProfitReply`
* **Низкоуровневый клиент (сгенерированный):** `SubscriptionServiceStub.OnPositionProfit(request, metadata)`

---

## 💬 Только суть

* **Что это.** Периодический поток обновлений прибыли/убытка позиций.
* **Зачем это нужно.** Мониторинг P&L, реализация логики стоп-лосса, отслеживание производительности счёта.
* **Периодические обновления.** Обновления отправляются с заданными интервалами (например, каждые 500 мс).

---

## 🎯 Назначение

Используйте для того, чтобы:

* Отслеживать прибыль/убыток открытых позиций в реальном времени
* Реализовывать динамическую логику стоп-лосса и тейк-профита
* Отслеживать производительность счёта в реальном времени
* Настраивать оповещения о прибыли/убытке
* Строить панели P&L в реальном времени
* Немедленно обнаруживать изменения позиций

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OnPositionProfit - Как это работает](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW.md)**

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_position_profit(
        self,
        interval_ms: int,
        ignore_empty: bool = True,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time profit updates for open positions.

        Yields:
            OnPositionProfitData: Profit update data.
        """
```

**Сообщение запроса:**

```protobuf
message OnPositionProfitRequest {
  int32 timer_period_milliseconds = 1;  // Интервал опроса в миллисекундах
  bool ignore_empty_data = 2;           // Пропускать кадры без изменений (по умолчанию: true)
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `interval_ms`        | `int`                          | Интервал опроса сервера в миллисекундах       |
| `ignore_empty`       | `bool`                         | Пропускать кадры без изменений (по умолчанию True) |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены стриминга (опционально)    |

---

## ⬆️ Выход - Асинхронный генератор

Возвращает асинхронный генератор, который выдаёт объекты `OnPositionProfitData`.

**Поля OnPositionProfitData:**

| Поле                          | Тип                                    | Описание                             |
| ----------------------------- | -------------------------------------- | ------------------------------------ |
| `type`                        | `int`                                  | Тип обновления                       |
| `new_positions`               | `repeated OnPositionProfitPositionInfo`| Вновь открытые позиции               |
| `updated_positions`           | `repeated OnPositionProfitPositionInfo`| Позиции с изменениями прибыли        |
| `deleted_positions`           | `repeated OnPositionProfitPositionInfo`| Закрытые позиции                     |
| `account_info`                | `OnEventAccountInfo`                   | Текущая информация о счёте           |
| `terminal_instance_guid_id`   | `str`                                  | Идентификатор экземпляра терминала   |

**Поля OnPositionProfitPositionInfo:**

| Поле              | Тип      | Описание                                 |
| ----------------- | -------- | ---------------------------------------- |
| `index`           | `int32`  | Индекс позиции в списке                  |
| `ticket`          | `uint64` | Номер тикета позиции                     |
| `profit`          | `double` | Текущая прибыль/убыток                   |
| `position_symbol` | `string` | Торговый символ                          |

**Поля OnEventAccountInfo:**

| Поле              | Тип      | Описание                                 |
| ----------------- | -------- | ---------------------------------------- |
| `balance`         | `double` | Баланс счёта                             |
| `equity`          | `double` | Средства (equity) счёта                  |
| `profit`          | `double` | Общая прибыль                            |
| `margin`          | `double` | Использованная маржа                     |
| `margin_free`     | `double` | Свободная маржа                          |

**Enum типа позиции (SUB_ENUM_POSITION_TYPE):**

| Имя                       | Значение | Описание                             |
| ------------------------- | ----- | ------------------------------------ |
| `SUB_POSITION_TYPE_BUY`   | 0     | Позиция на покупку (long)            |
| `SUB_POSITION_TYPE_SELL`  | 1     | Позиция на продажу (short)           |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

# Доступ к значениям enum
subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
subscriptions_pb2.SUB_POSITION_TYPE_SELL  # = 1
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы стриминга `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_stream_with_reconnect`.
* **Асинхронный генератор:** Метод возвращает асинхронный генератор - используйте `async for` для получения данных.
* **Интервал опроса:** Выбирайте интервал в зависимости от ваших потребностей - более короткие интервалы = более частые обновления, но выше нагрузка.
* **Игнорирование пустых:** Установите `ignore_empty=True`, чтобы пропускать обновления, когда ничего не изменилось (рекомендуется).
* **Три списка:** Каждое обновление содержит `new_positions`, `updated_positions` и `deleted_positions`.
* **Информация о счёте:** Каждое обновление включает текущий баланс, средства (equity) и маржу счёта.
* **Управление ресурсами:** Всегда отменяйте потоки по завершении, чтобы освободить ресурсы.

---

## 🔗 Примеры использования

### 1) Мониторинг P&L всех позиций

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_positions_pnl():
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
        # Опрашиваем каждые 500 мс, пропускаем пустые обновления
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            # Новые позиции
            if update.new_positions:
                for pos in update.new_positions:
                    print(f"[NEW] Position #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L={pos.profit:.2f}")

            # Обновлённые позиции (прибыль изменилась)
            if update.updated_positions:
                for pos in update.updated_positions:
                    print(f"[UPDATE] Position #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L={pos.profit:.2f}")

            # Закрытые позиции
            if update.deleted_positions:
                for pos in update.deleted_positions:
                    print(f"[CLOSED] Position #{pos.ticket} ({pos.position_symbol}): "
                          f"Final P&L={pos.profit:.2f}")

            # Сводка по счёту
            if update.account_info:
                acc = update.account_info
                print(f"[ACCOUNT] Balance={acc.balance:.2f}, "
                      f"Equity={acc.equity:.2f}, Profit={acc.profit:.2f}\n")

    except KeyboardInterrupt:
        print("Stopping stream...")

    finally:
        await account.channel.close()

asyncio.run(monitor_positions_pnl())
```

### 2) Панель общего P&L в реальном времени

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def realtime_pnl_dashboard():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Отслеживаем все позиции
    positions = {}  # тикет -> (символ, прибыль)

    try:
        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True
        ):
            # Добавляем новые позиции
            for pos in update.new_positions:
                positions[pos.ticket] = (pos.position_symbol, pos.profit)

            # Обновляем существующие позиции
            for pos in update.updated_positions:
                positions[pos.ticket] = (pos.position_symbol, pos.profit)

            # Удаляем закрытые позиции
            for pos in update.deleted_positions:
                if pos.ticket in positions:
                    del positions[pos.ticket]

            # Вычисляем общий P&L
            total_profit = sum(profit for _, profit in positions.values())

            # Отображаем панель
            print("\033[2J\033[H")  # Очистить экран
            print("=" * 60)
            print(f"REAL-TIME P&L DASHBOARD")
            print("=" * 60)

            if update.account_info:
                acc = update.account_info
                print(f"Balance:  ${acc.balance:,.2f}")
                print(f"Equity:   ${acc.equity:,.2f}")
                print(f"Margin:   ${acc.margin:,.2f}")
                print(f"Free:     ${acc.free_margin:,.2f}")
                print(f"Profit:   ${acc.profit:,.2f}")
                print("-" * 60)

            print(f"\nOpen Positions: {len(positions)}")
            print(f"Total P&L: ${total_profit:,.2f}\n")

            # Показываем отдельные позиции
            for ticket, (symbol, profit) in sorted(positions.items()):
                status = "[+]" if profit >= 0 else "[-]"
                print(f"{status} #{ticket} {symbol:8s} ${profit:>10,.2f}")

    except KeyboardInterrupt:
        print("\nStopping dashboard...")

    finally:
        await account.channel.close()

asyncio.run(realtime_pnl_dashboard())
```

### 3) Автоматический стоп-лосс по целевой прибыли

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2

async def auto_take_profit(target_profit: float = 100.0):
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
            # Проверяем обновлённые позиции на достижение целевой прибыли
            for pos in update.updated_positions:
                if pos.profit >= target_profit:
                    print(f"\n[TARGET] Profit reached for #{pos.ticket}: "
                          f"${pos.profit:.2f}")

                    # Закрываем позицию
                    close_req = trading_pb2.OrderCloseRequest(
                        ticket=pos.ticket,
                        volume=0,  # Закрыть всё
                        deviation=20,
                        comment="Auto TP"
                    )

                    result = await account.order_close(close_req)

                    if result.error.error_type == 0:  # Успех
                        print(f"[SUCCESS] Position #{pos.ticket} closed")
                    else:
                        print(f"[FAILED] Could not close #{pos.ticket}: "
                              f"{result.error.description}")

    except KeyboardInterrupt:
        print("\nStopping auto TP...")

    finally:
        await account.channel.close()

# Закрываем позиции, когда они достигают прибыли $100
asyncio.run(auto_take_profit(100.0))
```

### 4) Защита лимита убытков

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2

async def loss_limit_protection(max_loss: float = -50.0):
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
            # Проверяем на чрезмерные убытки
            for pos in update.updated_positions:
                if pos.profit <= max_loss:
                    print(f"\n[WARNING] Loss limit exceeded for #{pos.ticket}: "
                          f"${pos.profit:.2f}")

                    # Экстренное закрытие
                    close_req = trading_pb2.OrderCloseRequest(
                        ticket=pos.ticket,
                        volume=0,
                        deviation=50,  # Разрешаем большее проскальзывание для экстренного случая
                        comment="Emergency stop"
                    )

                    result = await account.order_close(close_req)

                    if result.error.error_type == 0:
                        print(f"[EMERGENCY] Position #{pos.ticket} closed")
                    else:
                        print(f"[FAILED] Could not close: {result.error.description}")

    except KeyboardInterrupt:
        print("\nStopping loss protection...")

    finally:
        await account.channel.close()

# Закрываем позиции, когда их убыток превышает $50
asyncio.run(loss_limit_protection(-50.0))
```

### 5) Трекер статистики P&L

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def track_pnl_stats(duration_seconds: int = 300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Хранилище статистики
    stats = {}  # тикет -> {max_profit, max_loss, updates_count, symbol}

    prev_positions = set()
    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True,
            cancellation_event=cancel_event
        ):
            current_positions = set(update.position_tickets)
            stats['updates'] += 1

            # Добавляем новые позиции
            for pos in update.new_positions:
                stats[pos.ticket] = {
                    'symbol': pos.position_symbol,
                    'max_profit': pos.profit,
                    'max_loss': pos.profit,
                    'updates': 1,
                    'current': pos.profit
                }

            # Обновляем статистику
            for pos in update.updated_positions:
                if pos.ticket in stats:
                    s = stats[pos.ticket]
                    s['max_profit'] = max(s['max_profit'], pos.profit)
                    s['max_loss'] = min(s['max_loss'], pos.profit)
                    s['updates'] += 1
                    s['current'] = pos.profit

            # Отмечаем удалённые позиции
            for pos in update.deleted_positions:
                if pos.ticket in stats:
                    stats[pos.ticket]['closed'] = True
                    stats[pos.ticket]['final_profit'] = pos.profit

        await stop_task

        # Печатаем статистику
        print("\n" + "=" * 70)
        print("P&L STATISTICS REPORT")
        print("=" * 70)

        for ticket, s in stats.items():
            status = "CLOSED" if s.get('closed') else "OPEN"
            print(f"\nPosition #{ticket} ({s['symbol']}) - {status}")
            print(f"  Max profit:    ${s['max_profit']:>10,.2f}")
            print(f"  Max loss:      ${s['max_loss']:>10,.2f}")
            print(f"  Updates:       {s['updates']:>10,}")
            if s.get('closed'):
                print(f"  Final P&L:     ${s['final_profit']:>10,.2f}")
            else:
                print(f"  Current P&L:   ${s['current']:>10,.2f}")

        print("=" * 70)

    finally:
        await account.channel.close()

# Отслеживаем статистику в течение 5 минут
asyncio.run(track_pnl_stats(300))
```

### 6) Оповещение об общей прибыли счёта

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def total_profit_alert(target: float = 500.0):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    alerted = False

    try:
        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True
        ):
            if update.account_info:
                total_profit = update.account_info.profit

                # Проверяем, достигнута ли цель
                if total_profit >= target and not alerted:
                    print(f"\n[TARGET REACHED]")
                    print(f"Total account profit: ${total_profit:.2f}")
                    print(f"Balance: ${update.account_info.balance:.2f}")
                    print(f"Equity: ${update.account_info.equity:.2f}")
                    alerted = True
                    break

                # Показываем прогресс
                progress = (total_profit / target) * 100
                print(f"\rProfit: ${total_profit:>8.2f} "
                      f"({progress:>5.1f}% of target)", end="")

    except KeyboardInterrupt:
        print("\nStopping alert...")

    finally:
        await account.channel.close()

# Оповещаем, когда общая прибыль достигает $500
asyncio.run(total_profit_alert(500.0))
```

---

## 📚 См. также

* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Получить полные детали позиций (снимок)
* [OrderClose](../5.%20Trading_Operations/order_close.md) - Закрыть позиции
* [OnSymbolTick](./on_symbol_tick.md) - Стриминг обновлений цен
* [AccountSummary](../1.%20Account_Information/account_summary.md) - Получить информацию о счёте (снимок)
