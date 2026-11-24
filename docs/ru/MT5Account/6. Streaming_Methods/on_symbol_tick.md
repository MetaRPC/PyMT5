# Стриминг тиков символов в реальном времени

> **Запрос:** подписаться на тиковые данные в реальном времени для указанных символов.

**Информация об API:**

* **Python API:** `MT5Account.on_symbol_tick(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.SubscriptionService`
* **Proto-определение:** `OnSymbolTick` (определено в `mt5-term-api-subscriptions.proto`)

### RPC

* **Сервис:** `mt5_term_api.SubscriptionService`
* **Метод:** `OnSymbolTick(OnSymbolTickRequest) -> stream OnSymbolTickReply`
* **Низкоуровневый клиент (сгенерированный):** `SubscriptionServiceStub.OnSymbolTick(request, metadata)`

---

## 💬 Только суть

* **Что это.** Поток тиков цен для указанных символов в реальном времени.
* **Зачем это нужно.** Мониторинг живых цен, реализация тиковых стратегий, отслеживание движений рынка.
* **Высокая частота.** Может генерировать множество обновлений в секунду при активной торговле.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Отслеживать изменения цен для символов в реальном времени
* Реализовывать тиковые торговые стратегии
* Отслеживать спреды bid/ask в реальном времени
* Строить панели живых цен
* Немедленно обнаруживать движения цен
* Собирать тиковые данные для анализа


```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_symbol_tick(
        self,
        symbols: list[str],
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time tick data for specified symbols.

        Yields:
            OnSymbolTickData: Async stream of tick data responses.
        """
```

**Сообщение запроса:**

```protobuf
message OnSymbolTickRequest {
  repeated string symbol_names = 1;  // Список символов для подписки
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `symbols`            | `list[str]`                    | Имена символов для подписки (например, ["EURUSD", "GBPUSD"]) |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены стриминга (опционально)    |

---

## ⬆️ Выход - Асинхронный генератор

Возвращает асинхронный генератор, который выдаёт объекты `OnSymbolTickData`.

**Поля OnSymbolTickData:**

| Поле                          | Тип                       | Описание                             |
| ----------------------------- | ------------------------- | ------------------------------------ |
| `symbol_tick`                 | `MrpcSubscriptionMqlTick` | Тиковые данные (см. ниже)            |
| `terminal_instance_guid_id`   | `str`                     | Идентификатор экземпляра терминала   |

**Поля MrpcSubscriptionMqlTick:**

| Поле          | Тип                           | Описание                                 |
| ------------- | ----------------------------- | ---------------------------------------- |
| `symbol`      | `str`                         | Имя символа                              |
| `time`        | `google.protobuf.Timestamp`   | Время последнего обновления цены         |
| `time_msc`    | `int64`                       | Время последнего обновления цены (миллисекунды) |
| `bid`         | `float64`| Текущая цена Bid                         |
| `ask`         | `float64`| Текущая цена Ask                         |
| `last`        | `float64`| Цена последней сделки (Last)             |
| `volume`      | `uint64` | Объём для текущей цены Last              |
| `volume_real` | `float64`| Объём для текущей цены Last (реальный)   |
| `flags`       | `uint32` | Флаги тика (индикация buy/sell)          |


---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OnSymbolTick - Как это работает](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_symbol_tick_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы стриминга `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_stream_with_reconnect`.
* **Асинхронный генератор:** Метод возвращает асинхронный генератор - используйте `async for` для получения данных.
* **Несколько символов:** Вы можете подписаться на несколько символов в одном потоке.
* **Отмена:** Передайте `asyncio.Event` и вызовите `event.set()`, чтобы корректно остановить поток.
* **Высокая частота:** Потоки тиков могут иметь очень высокую частоту - убедитесь, что ваша обработка эффективна.
* **Управление ресурсами:** Всегда отменяйте потоки по завершении, чтобы освободить ресурсы.
* **Обработка ошибок:** Ошибки выбрасываются как исключения - оборачивайте в try/except для обработки.
* **Обработка UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не указан.
  Для явного управления (например, в сценариях стриминга) передайте `id_=uuid4()` в конструктор.

---

## 🔗 Примеры использования

### 1) Мониторинг живых тиков для EURUSD

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_ticks():
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
        # Подписываемся на тики EURUSD
        async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
            tick = tick_data.symbol_tick
            print(f"{tick.symbol}: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, "
                  f"Spread={tick.ask - tick.bid:.5f}")

    except KeyboardInterrupt:
        print("Stopping tick stream...")

    finally:
        await account.channel.close()

# Запуск
asyncio.run(monitor_ticks())
```

### 2) Мониторинг нескольких символов с отменой

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_multiple_symbols():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Создаём событие отмены
    cancel_event = asyncio.Event()

    # Останавливаем через 30 секунд
    async def auto_cancel():
        await asyncio.sleep(30)
        cancel_event.set()
        print("\nStopping stream...")

    try:
        # Запускаем задачу авто-отмены
        cancel_task = asyncio.create_task(auto_cancel())

        # Подписываемся на несколько символов
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            spread_pips = (tick.ask - tick.bid) * 10000  # для 4-значных пар

            print(f"[{tick.time_msc}] {tick.symbol}: "
                  f"Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, "
                  f"Spread={spread_pips:.1f} pips")

        await cancel_task

    finally:
        await account.channel.close()

asyncio.run(monitor_multiple_symbols())
```

### 3) Отслеживание статистики спреда bid-ask

```python
import asyncio
from collections import defaultdict
from MetaRpcMT5 import MT5Account

async def track_spread_stats():
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
    spreads = defaultdict(list)
    cancel_event = asyncio.Event()

    async def stop_after_duration(seconds):
        await asyncio.sleep(seconds)
        cancel_event.set()

    try:
        # Останавливаем через 60 секунд
        stop_task = asyncio.create_task(stop_after_duration(60))

        symbols = ["EURUSD", "GBPUSD"]

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            spread = tick.ask - tick.bid
            spreads[tick.symbol].append(spread)

        await stop_task

        # Печатаем статистику
        print("\n=== Spread Statistics ===")
        for symbol, spread_list in spreads.items():
            avg_spread = sum(spread_list) / len(spread_list)
            min_spread = min(spread_list)
            max_spread = max(spread_list)

            print(f"\n{symbol}:")
            print(f"  Ticks received: {len(spread_list)}")
            print(f"  Average spread: {avg_spread * 10000:.1f} pips")
            print(f"  Min spread: {min_spread * 10000:.1f} pips")
            print(f"  Max spread: {max_spread * 10000:.1f} pips")

    finally:
        await account.channel.close()

asyncio.run(track_spread_stats())
```

### 4) Система ценовых оповещений

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def price_alert_system():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Устанавливаем ценовые оповещения
    alerts = {
        "EURUSD": {"above": 1.1000, "below": 1.0900},
        "GBPUSD": {"above": 1.2700, "below": 1.2500},
    }

    triggered = set()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=list(alerts.keys())
        ):
            tick = tick_data.symbol_tick
            symbol = tick.symbol

            if symbol not in alerts:
                continue

            # Проверяем порог сверху
            if tick.bid >= alerts[symbol]["above"]:
                alert_key = f"{symbol}_above"
                if alert_key not in triggered:
                    print(f"\n[ALERT] {symbol} bid {tick.bid:.5f} "
                          f"is ABOVE {alerts[symbol]['above']:.5f}")
                    triggered.add(alert_key)

            # Проверяем порог снизу
            if tick.bid <= alerts[symbol]["below"]:
                alert_key = f"{symbol}_below"
                if alert_key not in triggered:
                    print(f"\n[ALERT] {symbol} bid {tick.bid:.5f} "
                          f"is BELOW {alerts[symbol]['below']:.5f}")
                    triggered.add(alert_key)

            # Останавливаем, если все оповещения сработали
            if len(triggered) == len(alerts) * 2:
                print("\nAll alerts triggered. Stopping...")
                break

    finally:
        await account.channel.close()

asyncio.run(price_alert_system())
```

### 5) Логгер тиков в реальном времени в CSV

```python
import asyncio
import csv
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_ticks_to_csv():
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

    # Останавливаем через 5 минут
    async def auto_stop():
        await asyncio.sleep(300)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        # Открываем CSV-файл
        with open('ticks.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Symbol', 'Bid', 'Ask', 'Last', 'Volume'])

            tick_count = 0

            async for tick_data in account.on_symbol_tick(
                symbols=["EURUSD"],
                cancellation_event=cancel_event
            ):
                tick = tick_data.symbol_tick

                # Записываем в CSV
                writer.writerow([
                    datetime.fromtimestamp(tick.time_msc / 1000).isoformat(),
                    tick.symbol,
                    tick.bid,
                    tick.ask,
                    tick.last,
                    tick.volume_real
                ])

                tick_count += 1

                if tick_count % 100 == 0:
                    print(f"Logged {tick_count} ticks...")
                    csvfile.flush()  # Сброс на диск

        await stop_task
        print(f"\nTotal ticks logged: {tick_count}")

    finally:
        await account.channel.close()

asyncio.run(log_ticks_to_csv())
```

### 6) Параллельный мониторинг тиков с задачами

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def process_eurusd_ticks(account):
    """Process EURUSD ticks"""
    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        tick = tick_data.symbol_tick
        print(f"[EUR] {tick.bid:.5f}")
        await asyncio.sleep(0.1)  # Ограничиваем вывод

async def process_gbpusd_ticks(account):
    """Process GBPUSD ticks"""
    async for tick_data in account.on_symbol_tick(symbols=["GBPUSD"]):
        tick = tick_data.symbol_tick
        print(f"[GBP] {tick.bid:.5f}")
        await asyncio.sleep(0.1)  # Ограничиваем вывод

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

    try:
        # Запускаем несколько потоков одновременно
        await asyncio.gather(
            process_eurusd_ticks(account),
            process_gbpusd_ticks(account),
        )

    except KeyboardInterrupt:
        print("\nStopping streams...")

    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 См. также

* [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Получить снимок текущего тика (однократно)
* [OnTrade](./on_trade.md) - Стриминг торговых событий
* [OnPositionProfit](./on_position_profit.md) - Стриминг обновлений прибыли позиций
