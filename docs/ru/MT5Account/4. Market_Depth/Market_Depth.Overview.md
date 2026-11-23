# MT5Account - Стакан (глубина рынка) - Обзор

> Подписывайтесь, получайте и управляйте данными стакана (Depth of Market, DOM): отслеживайте стакан ордеров, анализируйте ликвидность, следите за уровнями bid/ask.

## 📁 Что здесь находится

### Операции с DOM

* **[market_book_add](./market_book_add.md)** - подписаться на обновления DOM для символа.
* **[market_book_get](./market_book_get.md)** - получить текущие данные DOM.
* **[market_book_release](./market_book_release.md)** - отписаться от обновлений DOM.

---

## 📚 Пошаговые руководства

**Примечание:** Все операции с DOM являются асинхронными методами. Подробные примеры смотрите на страницах отдельных методов.

* **[market_book_add](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW.md)** - Примеры подписки
* **[market_book_get](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW.md)** - Шаблоны анализа DOM
* **[market_book_release](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW.md)** - Примеры освобождения ресурсов

---

## 🧭 Простыми словами

* **market_book_add** -> **подписаться** на рыночные данные Level 2 (стакан ордеров).
* **market_book_get** -> **получить** текущий снимок DOM с уровнями bid/ask.
* **market_book_release** -> **отписаться** и освободить ресурсы по завершении.

> Правило большого пальца: **подпишитесь один раз** через `market_book_add`, **опрашивайте повторно** через `market_book_get`, **выполните очистку** через `market_book_release`.

---

## Быстрый выбор

| Если вам нужно...                                | Используйте           | Возвращает                 | Ключевые входные данные             |
| ------------------------------------------------ | --------------------- | -------------------------- | ----------------------------------- |
| Подписаться на обновления DOM                    | `market_book_add`     | MarketBookAddData          | symbol                              |
| Получить текущий снимок стакана ордеров          | `market_book_get`     | MarketBookGetData          | symbol                              |
| Отписаться от DOM                                | `market_book_release` | MarketBookReleaseData      | symbol                              |
| Проанализировать ликвидность bid/ask             | `market_book_get`     | MarketBookGetData          | symbol                              |
| Отслеживать поток ордеров                        | `market_book_get`     | MarketBookGetData          | symbol (в цикле)                    |
| Найти уровни поддержки/сопротивления             | `market_book_get`     | MarketBookGetData          | symbol                              |

---

## ℹ️ Перекрёстные ссылки и подводные камни

* **Поддержка брокером:** Не все брокеры предоставляют данные DOM - уточните у вашего брокера.
* **Требуется подписка:** Необходимо вызвать `market_book_add` перед `market_book_get`.
* **Символ должен быть выбран:** Убедитесь, что символ находится в Market Watch перед подпиской.
* **Всегда освобождайте:** Вызывайте `market_book_release` по завершении, чтобы освободить ресурсы.
* **Пустые данные:** Возвращает пустой список, если данные DOM недоступны или нет подписки.
* **Асинхронные методы:** Все операции с DOM асинхронны - используйте `await`.
* **Автоматическое переподключение:** Все методы имеют встроенное переподключение через `execute_with_reconnect`.
* **По отдельным символам:** Подписывайтесь/отписывайтесь для каждого символа отдельно.
* **Enum типа:** В `MrpcMqlBookInfo` тип 1 = ордера на SELL, тип 2 = ордера на BUY.
* **Поля объёма:** Используйте `volume_real` (double) вместо `volume` (int64).
* **Данные в реальном времени:** DOM обновляется в реальном времени, вызывайте `market_book_get` повторно для мониторинга.

---

## 🟢 Минимальные фрагменты

```python
import asyncio
from MetaRpcMT5 import MT5Account

# Подписаться на DOM
async def subscribe_dom():
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
        # Подписаться на DOM для EURUSD
        result = await account.market_book_add("EURUSD")

        if result.opened_successfully:
            print(f"[SUCCESS] Subscribed to EURUSD DOM")
        else:
            print(f"[FAILED] Could not subscribe")

    finally:
        await account.channel.close()

asyncio.run(subscribe_dom())
```

```python
# Получить данные DOM
async def get_dom():
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
        # Сначала подписаться
        await account.market_book_add("EURUSD")

        # Получить снимок DOM
        dom_data = await account.market_book_get("EURUSD")

        print(f"[DOM] EURUSD has {len(dom_data.mql_book_infos)} levels")

        for entry in dom_data.mql_book_infos[:5]:  # Показать первые 5
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{entry_type:<6} {entry.price:.5f} Vol: {entry.volume_real:.2f}")

    finally:
        await account.channel.close()

asyncio.run(get_dom())
```

```python
# Отписаться от DOM
async def unsubscribe_dom():
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
        # Подписаться
        await account.market_book_add("EURUSD")

        # Выполнить анализ...
        dom_data = await account.market_book_get("EURUSD")
        print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} levels")

        # Отписаться по завершении
        result = await account.market_book_release("EURUSD")

        if result.closed_successfully:
            print(f"[SUCCESS] DOM released")

    finally:
        await account.channel.close()

asyncio.run(unsubscribe_dom())
```

```python
# Полный рабочий процесс DOM
async def dom_workflow():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbol = "EURUSD"

    try:
        # 1. Подписаться на DOM
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] Could not subscribe to {symbol}")
            return

        print(f"[1] Subscribed to {symbol} DOM")

        # 2. Мониторинг DOM в течение 10 секунд
        print(f"[2] Monitoring DOM...")

        for i in range(10):
            dom_data = await account.market_book_get(symbol)

            # Рассчитать ликвидность
            sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
            buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

            print(f"  [{i+1}/10] Levels: {len(dom_data.mql_book_infos)}, "
                  f"BUY: {buy_volume:.2f}, SELL: {sell_volume:.2f}")

            await asyncio.sleep(1)

        # 3. Отписаться
        release_result = await account.market_book_release(symbol)
        if release_result.closed_successfully:
            print(f"[3] DOM released successfully")

    finally:
        await account.channel.close()

asyncio.run(dom_workflow())
```

```python
# Проанализировать спред bid/ask
async def analyze_spread():
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
        symbol = "EURUSD"

        # Подписаться и получить DOM
        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Разделить ордера на покупку и продажу
        sell_orders = [e for e in dom_data.mql_book_infos if e.type in [0, 2]]
        buy_orders = [e for e in dom_data.mql_book_infos if e.type in [1, 3]]

        if sell_orders and buy_orders:
            best_ask = min(sell_orders, key=lambda x: x.price)
            best_bid = max(buy_orders, key=lambda x: x.price)

            spread = best_ask.price - best_bid.price
            spread_pips = spread / 0.0001

            print(f"[SPREAD] {symbol}")
            print(f"  Best Bid: {best_bid.price:.5f}")
            print(f"  Best Ask: {best_ask.price:.5f}")
            print(f"  Spread: {spread_pips:.1f} pips")

        # Очистка
        await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(analyze_spread())
```

```python
# Мониторинг нескольких символов
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

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    try:
        # Подписаться на все символы
        for symbol in symbols:
            result = await account.market_book_add(symbol)
            if result.opened_successfully:
                print(f"[SUBSCRIBED] {symbol}")

        # Мониторинг всех символов
        print("\n[MONITORING] DOM for all symbols:")

        for _ in range(5):  # Мониторинг в течение 5 итераций
            print("\n" + "="*50)

            for symbol in symbols:
                dom_data = await account.market_book_get(symbol)

                sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
                buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

                print(f"{symbol:<8} Levels: {len(dom_data.mql_book_infos):<4} "
                      f"BUY: {buy_volume:>8.2f}  SELL: {sell_volume:>8.2f}")

            await asyncio.sleep(2)

        # Отписаться от всех символов
        print("\n[RELEASING] All subscriptions...")
        for symbol in symbols:
            await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(monitor_multiple_symbols())
```

```python
# Контекстный менеджер для автоматической очистки
from contextlib import asynccontextmanager

@asynccontextmanager
async def dom_subscription(account, symbol):
    """Context manager for automatic DOM subscription cleanup"""
    try:
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"Failed to subscribe to {symbol} DOM")
        yield
    finally:
        await account.market_book_release(symbol)

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
        # DOM автоматически освобождается при выходе
        async with dom_subscription(account, "EURUSD"):
            dom_data = await account.market_book_get("EURUSD")
            print(f"[DOM] {len(dom_data.mql_book_infos)} levels")

    finally:
        await account.channel.close()

asyncio.run(main())
```

```python
# Найти ключевые уровни ликвидности
async def find_key_levels():
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
        symbol = "EURUSD"

        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Найти топ-5 уровней по объёму
        sorted_levels = sorted(dom_data.mql_book_infos,
                             key=lambda x: x.volume_real,
                             reverse=True)

        print(f"[KEY LEVELS] {symbol} - Top 5 volume levels:\n")

        for i, entry in enumerate(sorted_levels[:5], 1):
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{i}. {entry_type:<6} {entry.price:.5f} - {entry.volume_real:.2f} lots")

        # Очистка
        await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(find_key_levels())
```

---

## 📚 См. также

* **Символы:** [symbol_select](../2.%20Symbol_Information/symbol_select.md) - добавьте символ в Market Watch перед подпиской
* **Цены:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - получите текущие цены тиков
* **Стриминг:** [on_symbol_tick](../6.%20Streaming_Methods/on_symbol_tick.md) - поток тиков в реальном времени
