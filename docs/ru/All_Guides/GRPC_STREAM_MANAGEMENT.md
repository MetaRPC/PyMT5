# Руководство по стримингу gRPC и управлению подписками

> **Полное руководство** по работе с подписками в реальном времени в PyMT5

Этот документ охватывает:

- ✅ **Как правильно подписываться** на потоки рыночных данных
- ✅ **Как останавливать подписки** без утечек ресурсов
- ✅ **Типовые паттерны** от простых до продвинутых
- ✅ **Архитектура** и встроенные механизмы безопасности
- ✅ **Устранение неполадок** и лучшие практики

---

## Оглавление

1. [Быстрый старт — простая подписка](#quick-start-simple-subscription)
2. [Доступные методы стриминга](#available-streaming-methods)
3. [Полные паттерны (от простого к продвинутому)](#complete-patterns-simple-advanced)
4. [Проблема: почему потоками нужно управлять](#problem-why-streams-need-management)
5. [Решения и лучшие практики](#solutions-and-best-practices)
6. [Продвинутые примеры с enum](#advanced-examples-with-enums)
7. [Несколько одновременных потоков](#multiple-concurrent-streams)
8. [Архитектура и безопасность](#architecture-notes)
9. [Устранение неполадок](#troubleshooting-and-async-task-leaks)

---

## Быстрый старт — простая подписка

### 1️⃣ Простейший паттерн (автоматический таймаут)

**Используйте asyncio.wait_for** — автоматически останавливается по истечении времени:

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def main():
    # Настройка соединения
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # ✅ Стриминг в течение 10 секунд — останавливается автоматически!
    try:
        async def process_ticks():
            tick_count = 0
            async for tick_data in account.on_symbol_tick(symbols=["EURUSD", "GBPUSD"]):
                tick_count += 1
                tick = tick_data.symbol_tick
                print(f"[{tick_count}] {tick.symbol}: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")

                if tick_count >= 10:
                    break

        await asyncio.wait_for(process_ticks(), timeout=10.0)
        print("Stream finished")

    finally:
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(main())
```

**Когда использовать:** быстрые примеры, тестирование, короткие сессии мониторинга

---

### 2️⃣ Паттерн ручного управления

**Для полного контроля** — вы решаете, когда остановить:

```python
async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # ✅ Создать событие отмены
    cancel_event = asyncio.Event()

    async def monitor_prices():
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"Price: {tick.bid:.5f}")

    # Запустить мониторинг в фоне
    monitor_task = asyncio.create_task(monitor_prices())

    # ... выполнить другую работу ...

    # Остановить при необходимости
    await asyncio.sleep(5)
    cancel_event.set()  # Сигнал потоку остановиться
    await asyncio.sleep(0.5)  # Дать потоку время на очистку

    try:
        await account.disconnect()
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")

asyncio.run(main())
```

**Когда использовать:** долгосрочный мониторинг, фоновые службы, продакшн-приложения

---

## Доступные методы стриминга

### MT5Account (низкоуровневые потоки)

Все методы стриминга возвращают **асинхронные генераторы**, которые отдают объекты данных.

| Метод | Описание | Возвращает (асинхронный генератор) |
|--------|-------------|---------------------------|
| `on_symbol_tick()` | Ценовые тики в реальном времени для символов | `OnSymbolTickData` |
| `on_trade()` | Торговые события (ордера исполнены, изменены и т. д.) | `OnTradeData` |
| `on_position_profit()` | Обновления P&L позиций | `OnPositionProfitData` |
| `on_positions_and_pending_orders_tickets()` | Тикеты ордеров/позиций | `OnPositionsAndPendingOrdersTicketsData` |
| `on_trade_transaction()` | Низкоуровневые события торговых транзакций | `OnTradeTransactionData` |

**Все поддерживают параметр `cancellation_event` для корректной остановки!**

**Документация:**

- [Обзор методов стриминга](../MT5Account/MT5Account.Master.Overview.md)
- [on_symbol_tick](../MT5Account/MT5Account.Master.Overview.md)
- [on_trade](../MT5Account/MT5Account.Master.Overview.md)

**Примеры:**

- `examples/1_lowlevel/03_streaming_methods.py` — примеры низкоуровневого стриминга

- `examples/2_service/05_service_streaming.py` — примеры стриминга среднего уровня

---

## Полные паттерны (от простого к продвинутому)

### Паттерн 1: быстрый пример (5-10 секунд)

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def quick_stream_example():
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
        # ✅ Автоматический таймаут — идеально для тестирования
        async def process():
            count = 0
            async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
                tick = tick_data.symbol_tick
                count += 1
                print(f"Tick #{count}: {tick.bid:.5f}")

                if count >= 5:
                    break

        await asyncio.wait_for(process(), timeout=10.0)

    finally:
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(quick_stream_example())
# Останавливается после 5 тиков или 10 секунд автоматически ✅
```

---

### Паттерн 2: стриминг с ограничением по событиям

```python
async def event_limited_streaming():
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
    max_events = 100
    count = 0

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            count += 1
            tick = tick_data.symbol_tick
            print(f"[{count}] {tick.symbol}: {tick.bid:.5f}")

            if count >= max_events:
                print(f"Max events ({max_events}) reached - stopping")
                cancel_event.set()
                break

    finally:
        await asyncio.sleep(0.5)  # Ожидание корректной очистки
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(event_limited_streaming())
```

---

### Паттерн 3: остановка по условию

```python
async def condition_based_stop():
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

    try:
        # ✅ Остановка при выполнении определённого условия
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"Price: {tick.bid:.5f}")

            # Остановить, если цена пересекает порог
            if tick.bid > 1.10000:
                print("Target price reached!")
                cancel_event.set()
                break

    finally:
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(condition_based_stop())
```

---

### Паттерн 4: фоновая служба с ручным управлением

```python
class PriceMonitor:
    def __init__(self, account: MT5Account):
        self.account = account
        self.cancel_event = asyncio.Event()
        self.task = None

    async def start(self, symbols: list[str]):
        """Запустить мониторинг в фоне"""
        self.task = asyncio.create_task(self._monitor_prices(symbols))

    async def _monitor_prices(self, symbols: list[str]):
        """Внутренний цикл мониторинга"""
        async for tick_data in self.account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=self.cancel_event
        ):
            tick = tick_data.symbol_tick
            self._process_tick(tick)

    def _process_tick(self, tick):
        """Обработать каждый тик"""
        print(f"{tick.symbol}: {tick.bid:.5f} / {tick.ask:.5f}")
        # Ваша логика здесь...

    async def stop(self):
        """Корректно остановить мониторинг"""
        self.cancel_event.set()

        if self.task:
            await asyncio.sleep(0.5)  # Дать время на очистку
            await self.task

# Использование:
async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    monitor = PriceMonitor(account)
    await monitor.start(["EURUSD", "GBPUSD"])

    print("Monitoring... Press Ctrl+C to stop")
    await asyncio.sleep(30)  # Мониторинг в течение 30 секунд

    await monitor.stop()
    try:
        await account.disconnect()
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")

asyncio.run(main())
```

---

## Проблема: почему потоками нужно управлять

При работе со стримингом gRPC в PyMT5 критически важно понимать жизненный цикл потока:

**Подписки на потоки** (`on_symbol_tick`, `on_trade` и т. д.) — это **активные асинхронные задачи с сетевыми соединениями**, которые продолжают работать, пока их явно не остановят.

---

## Объяснение проблемы

### Что происходит без правильной очистки

```python
# ❌ ПЛОХО: поток работает вечно
async def bad_example():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    count = 0
    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        count += 1
        print(f"Tick: {tick_data.symbol_tick.bid:.5f}")

        if count >= 10:
            break  # ❌ ПРОБЛЕМА: поток всё ещё работает в фоне!
                   # ❌ ПРОБЛЕМА: соединение gRPC не закрыто!

    # ❌ Поток продолжает потреблять ресурсы
    # ❌ Сетевое соединение остаётся открытым
    # ❌ Память постепенно накапливается
```

**Результат:**

- Фоновая асинхронная задача продолжает потреблять ресурсы
- Терминал MT5 продолжает отправлять обновления
- **Утечка асинхронных задач** — задачи накапливаются в цикле событий
- Сетевое соединение остаётся открытым
- Множество брошенных потоков = **серьёзная утечка ресурсов**

---

## Решения и лучшие практики

## Решение 1: всегда используйте cancellation_event ✅

### Паттерн 1: создавайте cancellation_event заранее

```python
async def proper_cancellation():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    # ✅ КРИТИЧНО: создать событие отмены
    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event  # ✅ Передать в поток
        ):
            tick = tick_data.symbol_tick
            print(f"Price: {tick.bid:.5f}")

            if some_condition:
                cancel_event.set()  # ✅ ПРАВИЛЬНО: сигнал остановиться
                break

    finally:
        # ✅ КРИТИЧНО: дать потоку время на очистку
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(proper_cancellation())
```

### Паттерн 2: таймаут с asyncio.wait_for

```python
async def timeout_pattern():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async def stream_with_limit():
            async for tick_data in account.on_symbol_tick(
                symbols=["EURUSD"],
                cancellation_event=cancel_event
            ):
                print(f"Price: {tick_data.symbol_tick.bid:.5f}")

        # ✅ Автоматически останавливается через 30 секунд
        await asyncio.wait_for(stream_with_limit(), timeout=30.0)

    except asyncio.TimeoutError:
        print("Stream reached timeout")
        cancel_event.set()

    finally:
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(timeout_pattern())
```

---

## Решение 2: всегда выполняйте очистку в блоке finally ✅

**КРИТИЧНО:** всегда отключайтесь и дожидайтесь очистки потока

### ✅ ПРАВИЛЬНО — корректная очистка

```python
async def proper_cleanup():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            # Обработка данных...
            pass

    finally:
        # ✅ КРИТИЧНО: правильная последовательность очистки
        # Шаг 1: сигнализировать всем потокам остановиться
        cancel_event.set()

        # Шаг 2: дождаться корректной очистки (0.5-1.0 секунды)
        await asyncio.sleep(0.5)

        # Шаг 3: закрыть канал gRPC
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(proper_cleanup())
```

---

## Типичные ошибки при стриминге

### ❌ Ошибка 1: нет события отмены

```python
# ❌ НЕПРАВИЛЬНО: нет способа корректно остановить поток
async def bad():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        print(tick_data.symbol_tick.bid)
        # Если хотите остановить — ВЫ НЕ СМОЖЕТЕ остановить корректно!
```

**Исправление:**
```python
# ✅ ПРАВИЛЬНО: можно корректно остановить в любой момент
async def good():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    async for tick_data in account.on_symbol_tick(
        symbols=["EURUSD"],
        cancellation_event=cancel_event
    ):
        print(tick_data.symbol_tick.bid)
        # Теперь можно вызвать cancel_event.set() для остановки
```

---

### ❌ Ошибка 2: break без очистки

```python
# ❌ НЕПРАВИЛЬНО: break не очищает ресурсы
async def bad():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        if some_condition:
            break  # ❌ Поток всё ещё работает!

    # ❌ Нет очистки — утечка ресурсов!
```

**Исправление:**
```python
# ✅ ПРАВИЛЬНО: корректная очистка в finally
async def good():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            if some_condition:
                cancel_event.set()
                break

    finally:
        await asyncio.sleep(0.5)  # ✅ Время на очистку
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")
```

---

### ❌ Ошибка 3: нет отключения

```python
# ❌ НЕПРАВИЛЬНО: канал никогда не закрывается
async def bad():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    async for tick_data in account.on_symbol_tick(
        symbols=["EURUSD"],
        cancellation_event=cancel_event
    ):
        # Обработка...
        pass

    # ❌ Забыли отключиться — утечка соединения!
```

**Исправление:**
```python
# ✅ ПРАВИЛЬНО: всегда отключайтесь в finally
async def good():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            # Обработка...
            pass

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        await account.disconnect()  # ✅ КРИТИЧНО: закрывает канал gRPC
```

---

## Продвинутые примеры с enum

### Пример 1: фильтрация торговых событий по типу

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as sub_pb2

async def filter_trade_events():
    """
    Мониторинг торговых событий и фильтрация по типу с помощью enum protobuf.
    Показывает, как работать с SUB_ENUM_TRADE_TRANSACTION_TYPE.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    # ✅ Использование enum protobuf для фильтрации
    ORDER_ADD = sub_pb2.SUB_TRADE_TRANSACTION_ORDER_ADD
    ORDER_DELETE = sub_pb2.SUB_TRADE_TRANSACTION_ORDER_DELETE
    DEAL_ADD = sub_pb2.SUB_TRADE_TRANSACTION_DEAL_ADD

    try:
        print("Monitoring trade transactions (filtered by type)...")

        async for tx_data in account.on_trade_transaction(cancellation_event=cancel_event):
            if tx_data.trade_transaction:
                tx = tx_data.trade_transaction

                # ✅ Фильтрация по типу транзакции с помощью enum
                if tx.type == ORDER_ADD:
                    print(f"[NEW ORDER] Ticket={tx.order_ticket}, Symbol={tx.symbol}, "
                          f"Price={tx.price:.5f}, Volume={tx.volume:.2f}")

                elif tx.type == ORDER_DELETE:
                    print(f"[ORDER DELETED] Ticket={tx.order_ticket}")

                elif tx.type == DEAL_ADD:
                    print(f"[NEW DEAL] Deal={tx.deal_ticket}, Order={tx.order_ticket}, "
                          f"Symbol={tx.symbol}, Price={tx.price:.5f}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(filter_trade_events())
```

---

### Пример 2: сортировка и фильтрация позиций по прибыли

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def sort_positions_by_profit():
    """
    Мониторинг прибыли позиций и сортировка по P&L.
    Показывает продвинутую обработку данных при стриминге.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        print("Monitoring positions (sorted by profit)...")
        print("-" * 60)

        async for profit_data in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True,
            cancellation_event=cancel_event
        ):
            # ✅ Собрать все обновлённые позиции
            positions = list(profit_data.updated_positions)

            if not positions:
                continue

            # ✅ Сортировка по прибыли (по убыванию — прибыльные первыми)
            positions_sorted = sorted(positions, key=lambda p: p.profit, reverse=True)

            print(f"\n[UPDATE] Total positions: {len(positions_sorted)}")
            print(f"{'Symbol':<10} {'Ticket':<10} {'Profit':<12} {'Status':<10}")
            print("-" * 60)

            # ✅ Показать топ-5 прибыльных и топ-5 убыточных
            for pos in positions_sorted[:5]:  # Топ-5 прибыльных
                status = "✅ PROFIT" if pos.profit > 0 else "❌ LOSS"
                print(f"{pos.position_symbol:<10} {pos.ticket:<10} {pos.profit:>10.2f}  {status:<10}")

            if len(positions_sorted) > 10:
                print("   ... middle positions omitted ...")

            for pos in positions_sorted[-5:]:  # Топ-5 убыточных
                status = "✅ PROFIT" if pos.profit > 0 else "❌ LOSS"
                print(f"{pos.position_symbol:<10} {pos.ticket:<10} {pos.profit:>10.2f}  {status:<10}")

            # ✅ Рассчитать статистику
            total_profit = sum(p.profit for p in positions_sorted)
            winners = sum(1 for p in positions_sorted if p.profit > 0)
            losers = sum(1 for p in positions_sorted if p.profit < 0)

            print("-" * 60)
            print(f"Total P&L: {total_profit:+.2f} | Winners: {winners} | Losers: {losers}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(sort_positions_by_profit())
```

---

### Пример 3: фильтрация ордеров по состоянию и типу

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as sub_pb2

async def filter_orders_by_state():
    """
    Мониторинг торговых событий и фильтрация ордеров по состоянию и типу.
    Показывает сложную фильтрацию с использованием нескольких enum.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    # ✅ Определить значения enum для фильтрации
    ORDER_STATE_PLACED = sub_pb2.SUB_ORDER_STATE_PLACED
    ORDER_STATE_FILLED = sub_pb2.SUB_ORDER_STATE_FILLED
    ORDER_STATE_CANCELED = sub_pb2.SUB_ORDER_STATE_CANCELED

    ORDER_TYPE_BUY_LIMIT = sub_pb2.SUB_ORDER_TYPE_BUY_LIMIT
    ORDER_TYPE_SELL_LIMIT = sub_pb2.SUB_ORDER_TYPE_SELL_LIMIT

    try:
        print("Monitoring pending orders (filtered by state)...")
        print("-" * 70)

        async for trade_data in account.on_trade(cancellation_event=cancel_event):
            event = trade_data.event_data

            # ✅ Обработка новых ордеров — фильтруем только отложенные лимитные ордера
            for order in event.new_orders:
                if order.order_type in [ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT]:
                    order_type_str = "BUY LIMIT" if order.order_type == ORDER_TYPE_BUY_LIMIT else "SELL LIMIT"
                    print(f"[NEW PENDING] {order_type_str} #{order.ticket}: "
                          f"{order.symbol} @ {order.price_open:.5f} "
                          f"Vol={order.volume_initial:.2f} SL={order.stop_loss:.5f}")

            # ✅ Обработка ордеров со сменой состояния — показываем только исполненные или отменённые
            for state_change in event.state_changed_orders:
                current = state_change.current_order
                previous = state_change.previous_order

                if current.state == ORDER_STATE_FILLED:
                    print(f"[FILLED] Order #{current.ticket} was filled: "
                          f"{current.symbol} @ {current.price_current:.5f}")

                elif current.state == ORDER_STATE_CANCELED:
                    print(f"[CANCELED] Order #{current.ticket} was cancelled: "
                          f"{current.symbol}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(filter_orders_by_state())
```

---

### Пример 4: агрегация тиков по нескольким символам с сортировкой

```python
import asyncio
from collections import defaultdict
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def aggregate_and_sort_ticks():
    """
    Агрегация тиков от нескольких символов и сортировка по спреду.
    Показывает продвинутую обработку данных для нескольких символов.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    # ✅ Отслеживать последний тик для каждого символа
    latest_ticks = {}
    tick_counts = defaultdict(int)

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]

    try:
        print(f"Monitoring {len(symbols)} symbols, sorting by spread...")
        print("-" * 80)

        update_interval = 5  # Печатать отсортированные результаты каждые 5 тиков
        total_ticks = 0

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick

            # ✅ Обновить последний тик для символа
            latest_ticks[tick.symbol] = tick
            tick_counts[tick.symbol] += 1
            total_ticks += 1

            # ✅ Каждые N тиков показывать отсортированную сводку
            if total_ticks % update_interval == 0:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tick Summary (sorted by spread):")
                print("-" * 80)
                print(f"{'Rank':<6} {'Symbol':<10} {'Bid':<12} {'Ask':<12} {'Spread':<10} {'Ticks':<8}")
                print("-" * 80)

                # ✅ Рассчитать спреды и отсортировать
                symbol_spreads = []
                for symbol, tick in latest_ticks.items():
                    spread = tick.ask - tick.bid
                    symbol_spreads.append((symbol, tick, spread))

                # Сортировка по спреду (по возрастанию — самый узкий первым)
                symbol_spreads.sort(key=lambda x: x[2])

                # ✅ Отобразить отсортированные результаты
                for rank, (symbol, tick, spread) in enumerate(symbol_spreads, 1):
                    spread_pips = spread * 10000  # Для 4-значных пар
                    print(f"{rank:<6} {symbol:<10} {tick.bid:<12.5f} {tick.ask:<12.5f} "
                          f"{spread_pips:<10.1f} {tick_counts[symbol]:<8}")

                print("-" * 80)
                print(f"Total ticks received: {total_ticks}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(aggregate_and_sort_ticks())
```

---

## Несколько одновременных потоков

### Пример: запуск нескольких потоков одновременно

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def multiple_concurrent_streams():
    """
    Запуск нескольких методов стриминга одновременно.
    Показывает правильное управление несколькими потоками.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    # ✅ Единое событие отмены для ВСЕХ потоков
    cancel_event = asyncio.Event()

    async def stream_ticks():
        """Мониторинг данных тиков"""
        try:
            async for tick_data in account.on_symbol_tick(
                symbols=["EURUSD"],
                cancellation_event=cancel_event
            ):
                tick = tick_data.symbol_tick
                print(f"[TICK] {tick.symbol}: {tick.bid:.5f}")
        except Exception as e:
            print(f"[TICK ERROR] {e}")

    async def stream_trades():
        """Мониторинг торговых событий"""
        try:
            async for trade_data in account.on_trade(cancellation_event=cancel_event):
                print(f"[TRADE] Event received: {trade_data.type}")
        except Exception as e:
            print(f"[TRADE ERROR] {e}")

    async def stream_profits():
        """Мониторинг прибыли позиций"""
        try:
            async for profit_data in account.on_position_profit(
                interval_ms=2000,
                ignore_empty=True,
                cancellation_event=cancel_event
            ):
                total_positions = len(profit_data.updated_positions)
                print(f"[PROFIT] {total_positions} positions updated")
        except Exception as e:
            print(f"[PROFIT ERROR] {e}")

    async def auto_stop(duration: float):
        """Автоматическая остановка через заданное время"""
        await asyncio.sleep(duration)
        print(f"\n[STOP] Auto-stopping after {duration} seconds...")
        cancel_event.set()

    try:
        print("Starting multiple concurrent streams...")
        print("-" * 60)

        # ✅ Запустить все потоки одновременно
        await asyncio.gather(
            stream_ticks(),
            stream_trades(),
            stream_profits(),
            auto_stop(30.0)  # Остановить все через 30 секунд
        )

    finally:
        # ✅ Убедиться, что событие отмены установлено
        cancel_event.set()

        # ✅ Дождаться очистки всех потоков
        await asyncio.sleep(0.5)

        # ✅ Отключиться (закрывает канал)
        try:
            await account.disconnect()
            print("[DONE] All streams stopped gracefully")
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(multiple_concurrent_streams())
```

---

## Примечания по архитектуре

### Как работает стриминг Python в MT5Account

**🔑 Критически важное понимание:**

**ВСЕ методы стриминга** (`on_symbol_tick`, `on_trade`, `on_position_profit`, `on_trade_transaction`, `on_positions_and_pending_orders_tickets`) внутренне используют **один и тот же скрытый механизм**: `execute_stream_with_reconnect`.

Вот почему:
- Поведение цикла while применяется ко **ВСЕМ** операциям стриминга
- Механизм `cancellation_event` требуется для **ВСЕХ** методов стриминга
- Правила очистки ресурсов **идентичны** для всех операций стриминга

**Пользователи не видят это напрямую** — когда вы вызываете `account.on_symbol_tick()`, внутри он вызывает `execute_stream_with_reconnect`, который содержит бесконечный цикл переподключения.

**Поток данных:**

```
User code (async for loop)
    ↓
Async generator (yields data)
    ↓
execute_stream_with_reconnect (background async task)
    ↓
gRPC ClientStream
    ↓
Network (to MT5 terminal)
```

**Распространение отмены:**
```
User code → cancellation_event → async generator → gRPC call → Network
```

**Когда вы устанавливаете cancellation_event:**

1. Пользователь вызывает `cancel_event.set()` в своём коде
2. Цикл while проверяет условие на следующей итерации:
   ```python
   while cancellation_event is None or not cancellation_event.is_set():
   # После .set() → оба условия False → цикл ОСТАНАВЛИВАЕТСЯ
   ```
3. Текущая итерация завершается (async for отдаёт последние данные)
4. Выполняется блок `finally` → `stream.cancel()` закрывает поток gRPC ✅
5. Цикл прерывается (новые потоки не создаются)
6. Сетевое соединение закрывается
7. Ресурсы освобождаются ✅

**Ключевой момент:** цикл while проверяет `cancellation_event.is_set()` **на каждой итерации**. Вызов `.set()` заставляет цикл завершиться после окончания текущего потока.

### Механизм очистки MT5Account

⚠️ **Важно:** этот механизм **внутренний для ВСЕХ методов стриминга**. Когда вы вызываете любой метод стриминга (`on_symbol_tick`, `on_trade` и т. д.), на самом деле вы используете `execute_stream_with_reconnect` за кулисами.

Метод `execute_stream_with_reconnect` имеет встроенную логику переподключения с автоматической очисткой потоков:

```python
# В MT5Account (реальная структура)
async def execute_stream_with_reconnect(..., cancellation_event):
    # ⚠️ КРИТИЧНО: Бесконечный цикл переподключения
    while cancellation_event is None or not cancellation_event.is_set():
        reconnect_required = False
        stream = None

        try:
            stream = stream_invoker(request, headers)
            async for response in stream:
                # Отдаём данные пользователю
                yield data

        except grpc.aio.AioRpcError as ex:
            if ex.code() == grpc.StatusCode.UNAVAILABLE:
                reconnect_required = True  # Сетевая ошибка → пробуем переподключиться
            else:
                raise

        finally:
            if stream:
                stream.cancel()  # ✅ ВСЕГДА закрывает текущий поток gRPC

        # Логика переподключения
        if reconnect_required:
            await asyncio.sleep(0.5)
            await self.reconnect()
            # ⚠️ Цикл продолжается → создаёт НОВЫЙ поток
        else:
            break  # Выход только здесь
```

**Что это означает:**

✅ **Что он ДЕЛАЕТ:**
- Автоматически закрывает текущий поток gRPC (в блоке `finally`)
- Обрабатывает сетевые ошибки с автоматическим переподключением
- Очищает ресурсы для каждого отдельного потока

⚠️ **Чего он НЕ делает:**
- **Останавливает цикл переподключения** без `cancellation_event`
- **Предотвращает создание новых потоков**

**Критически важное понимание:**

```python
# ❌ БЕЗ cancellation_event:
async for tick in account.on_symbol_tick(["EURUSD"]):  # Нет cancellation_event!
    if count >= 10:
        break  # Пользователь прерывает → текущий поток закрывается ✅
                # НО цикл while продолжается → создаёт НОВЫЙ поток ❌
                # → УТЕЧКА: брошенный поток продолжает работать

# ✅ С cancellation_event:
cancel_event = asyncio.Event()
async for tick in account.on_symbol_tick(["EURUSD"], cancellation_event=cancel_event):
    if count >= 10:
        cancel_event.set()  # Останавливает цикл while ✅
        break               # Текущий поток закрывается ✅
                            # → ЧИСТО: новые потоки не создаются
```

**Итог:**

- ✅ `stream.cancel()` очищает **текущий** поток
- ❌ **Только** `cancellation_event.set()` останавливает **цикл переподключения while**
- 🔑 **Как это работает**: `while cancellation_event is None or not cancellation_event.is_set()` проверяется на каждой итерации
- 🔴 **Без cancellation_event** → условие while всегда True → цикл работает вечно → **УТЕЧКА**
- 🔴 **С cancellation_event, но без .set()** → условие while остаётся True → цикл работает вечно → **УТЕЧКА**
- ✅ **С cancellation_event.set()** → условие while становится False → цикл останавливается → **ЧИСТО**
- ✅ **Вы ОБЯЗАНЫ вызвать `disconnect()`**, чтобы освободить соединение gRPC (он закрывает канал)

---

## Рекомендации

### ✅ ДЕЛАЙТЕ:

1. **Всегда используйте `cancellation_event`** с методами стриминга
2. **Всегда вызывайте `cancel_event.set()`** перед выходом
3. **Всегда используйте блоки `try/finally`** для очистки
4. **Всегда ждите 0.5-1.0 секунды** после установки cancellation_event
5. **Всегда отключайтесь** в блоке finally: `await account.disconnect()`
6. **Используйте `asyncio.wait_for()`** для автоматических таймаутов
7. **Используйте `asyncio.gather()`** для одновременного запуска нескольких потоков

### ❌ НЕ ДЕЛАЙТЕ:

1. **Никогда не запускайте стриминг без cancellation_event**
2. **Никогда не прерывайте цикл без установки cancellation_event**
3. **Никогда не забывайте блок finally** с кодом очистки
4. **Никогда не пропускайте период ожидания** после отмены
5. **Никогда не оставляйте канал открытым** после стриминга
6. **Никогда не игнорируйте исключения** из потоков

---

## Устранение неполадок и утечки асинхронных задач

### Проверка на утечки задач

```python
import asyncio

async def check_task_leaks():
    # Перед стримингом
    before = len(asyncio.all_tasks())
    print(f"Tasks before: {before}")

    # Ваш код стриминга здесь...
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        count = 0
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            count += 1
            if count >= 5:
                break

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.disconnect()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

    # После стриминга (немного подождать очистки)
    await asyncio.sleep(1.0)
    after = len(asyncio.all_tasks())
    print(f"Tasks after: {after}")
    print(f"Leaked tasks: {after - before}")
    # Должно быть 0-1 при правильной очистке

asyncio.run(check_task_leaks())
```

### Отладка ожидающих задач

```python
import asyncio

async def debug_pending_tasks():
    # Получить все задачи
    tasks = asyncio.all_tasks()

    print(f"Total pending tasks: {len(tasks)}")
    print("-" * 60)

    for i, task in enumerate(tasks, 1):
        print(f"Task {i}: {task.get_name()}")
        print(f"  Coro: {task.get_coro()}")
        print(f"  Done: {task.done()}")
        if not task.done():
            print(f"  ⚠️  STILL RUNNING!")
        print()
```

### Типичные паттерны утечек

1. **Неиспользование cancellation_event:**
   ```python
   # ❌ Утечка: поток никогда не останавливается
   async for data in account.on_symbol_tick(symbols=["EURUSD"]):
       # Забыли параметр cancellation_event
       pass
   ```

2. **Неустановка cancellation_event:**
   ```python
   # ❌ Утечка: поток продолжает работать после break
   cancel_event = asyncio.Event()
   async for data in account.on_symbol_tick(symbols=["EURUSD"], cancellation_event=cancel_event):
       if condition:
           break  # Забыли cancel_event.set()
   ```

3. **Незакрытие канала:**
   ```python
   # ❌ Утечка: соединение остаётся открытым
   cancel_event.set()
   await asyncio.sleep(0.5)
   # Забыли await account.disconnect()
   ```

---

## См. также

* **[Обзор методов стриминга](../MT5Account/MT5Account.Master.Overview.md)** — полная документация по методам стриминга
* **[on_symbol_tick](../MT5Account/MT5Account.Master.Overview.md)** — справочник по стримингу тиков
* **[on_trade](../MT5Account/MT5Account.Master.Overview.md)** — справочник по торговым событиям
* **[Документация Python asyncio](https://docs.python.org/3/library/asyncio.html)** — официальное руководство по asyncio
* **[gRPC Python](https://grpc.io/docs/languages/python/)** — официальное руководство по gRPC для Python

---

**Помните:** потоки — мощные инструменты для рыночных данных в реальном времени, но они требуют правильного управления жизненным циклом. Освойте cancellation_event, всегда выполняйте очистку в блоках finally — и ваш код стриминга будет надёжным и без утечек. Удачного стриминга! 🚀
