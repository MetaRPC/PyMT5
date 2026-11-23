# Получение данных стакана (глубины рынка)

> **Запрос:** Получить текущие данные стакана (Depth of Market, стакан ордеров) для символа с подпиской.

**Информация об API:**

* **Python API:** `MT5Account.market_book_get(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `MarketBookGet` (определено в `mt5-term-api-market-info.proto`)
* **Enum'ы в этом методе:** 1 enum с 4 константами (1 на выходе)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `MarketBookGet(MarketBookGetRequest) -> MarketBookGetReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.MarketBookGet(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def market_book_get(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookGetData:
        """
        Gets the current Depth of Market (DOM) data for a symbol.

        Returns:
            MarketBookGetData: A list of book entries for the symbol's DOM.
        """
```

**Сообщение запроса:**

```protobuf
MarketBookGetRequest {
  string symbol = 1;  // Имя символа
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `symbol`             | `str`                          | Имя символа (например, "EURUSD")              |
| `deadline`           | `Optional[datetime]`           | Крайний срок для операции (необязательно)     |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены запроса (необязательно)    |

---

## ⬆️ Выход

Возвращает объект `MarketBookGetData`.

**Поля MarketBookGetData:**

| Поле                   | Тип                      | Описание                             |
| ---------------------- | ------------------------ | ------------------------------------ |
| `mql_book_infos`       | `list[MrpcMqlBookInfo]`  | Список записей стакана ордеров       |

**Поля MrpcMqlBookInfo:**

| Поле                   | Тип       | Описание                             |
| ---------------------- | --------- | ------------------------------------ |
| `type`                 | `BookType` | Тип ордера (enum)                   |
| `price`                | `double`  | Уровень цены                         |
| `volume`               | `int64`   | Объём в лотах (устаревшее)           |
| `volume_real`          | `double`  | Реальный объём в лотах               |

---

## 🧱 Связанные enum'ы (из proto)

### `BookType`

Используется в `MrpcMqlBookInfo` для указания типа записи стакана ордеров.

| Имя константы           | Значение | Описание                             |
| ----------------------- | ----- | ------------------------------------ |
| `BOOK_TYPE_SELL`        | 0     | Ордер на продажу                     |
| `BOOK_TYPE_BUY`         | 1     | Ордер на покупку                     |
| `BOOK_TYPE_SELL_MARKET` | 2     | Ордер на продажу по рыночной цене    |
| `BOOK_TYPE_BUY_MARKET`  | 3     | Ордер на покупку по рыночной цене    |

**Использование:**
```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_pb2

# Доступ к значениям enum
market_pb2.BOOK_TYPE_SELL        # = 0
market_pb2.BOOK_TYPE_BUY         # = 1
```

---

## 💬 Только суть

* **Что это.** Получает текущие рыночные данные Level 2 (стакан ордеров) для символа.
* **Зачем это нужно.** Анализ глубины рынка, ликвидности bid/ask и потока ордеров.
* **Требуется подписка.** Необходимо сначала вызвать `market_book_add`.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Получить текущий снимок DOM
* Проанализировать уровни ликвидности bid/ask
* Отслеживать глубину стакана ордеров
* Определить зоны поддержки/сопротивления
* Рассчитать объём на уровнях цен
* Обнаружить крупные ордера (обнаружение айсбергов)
* Провести анализ микроструктуры рынка

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[MarketBookGet - How it works](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Требуется подписка:** Необходимо вызвать `market_book_add` перед этим методом.
* **Пустые данные:** Возвращает пустой список, если данные DOM недоступны.
* **Поддержка брокером:** Не все брокеры предоставляют данные DOM.
* **Снимок в реальном времени:** Возвращает текущее состояние на момент запроса.
* **Поля объёма:** Используйте `volume_real` (double) вместо `volume` (int64).
* **Уровни цен:** Отсортированы по цене (сначала лучшие bid/ask).

---

## 🔗 Примеры использования

### 1) Получение текущих данных DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        # Сначала подписаться на DOM
        await account.market_book_add("EURUSD")

        # Получить данные DOM
        dom_data = await account.market_book_get("EURUSD")

        print(f"[DOM] EURUSD Market Depth:")
        print(f"Total levels: {len(dom_data.mql_book_infos)}\n")

        print(f"{'Type':<10} {'Price':<15} {'Volume':<15}")
        print("-" * 45)

        for entry in dom_data.mql_book_infos[:10]:  # Показать первые 10 уровней
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{entry_type:<10} {entry.price:<15.5f} {entry.volume_real:<15.2f}")

    finally:
        await account.channel.close()

asyncio.run(get_dom())
```

### 2) Анализ спреда bid/ask

```python
import asyncio
from MetaRpcMT5 import MT5Account

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

        if not dom_data.mql_book_infos:
            print(f"[WARNING] No DOM data available for {symbol}")
            return

        # Разделить ордера на покупку и продажу
        sell_orders = [e for e in dom_data.mql_book_infos if e.type in [0, 2]]
        buy_orders = [e for e in dom_data.mql_book_infos if e.type in [1, 3]]

        if sell_orders and buy_orders:
            best_ask = min(sell_orders, key=lambda x: x.price)
            best_bid = max(buy_orders, key=lambda x: x.price)

            spread = best_ask.price - best_bid.price
            spread_pips = spread / 0.0001

            print(f"[SPREAD ANALYSIS] {symbol}")
            print(f"  Best Bid: {best_bid.price:.5f} (Volume: {best_bid.volume_real:.2f})")
            print(f"  Best Ask: {best_ask.price:.5f} (Volume: {best_ask.volume_real:.2f})")
            print(f"  Spread: {spread:.5f} ({spread_pips:.1f} pips)")

    finally:
        await account.channel.close()

asyncio.run(analyze_spread())
```

### 3) Расчёт общей ликвидности

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def calculate_liquidity():
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

        # Рассчитать общий объём по сторонам
        sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
        buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])
        total_volume = sell_volume + buy_volume

        print(f"[LIQUIDITY] {symbol}")
        print(f"  Total DOM levels: {len(dom_data.mql_book_infos)}")
        print(f"  BUY side volume: {buy_volume:.2f} lots")
        print(f"  SELL side volume: {sell_volume:.2f} lots")
        print(f"  Total volume: {total_volume:.2f} lots")

        if total_volume > 0:
            buy_percent = (buy_volume / total_volume) * 100
            sell_percent = (sell_volume / total_volume) * 100
            print(f"\n  BUY: {buy_percent:.1f}% | SELL: {sell_percent:.1f}%")

            if buy_percent > 60:
                print("  [SIGNAL] Strong BUY side liquidity")
            elif sell_percent > 60:
                print("  [SIGNAL] Strong SELL side liquidity")
            else:
                print("  [SIGNAL] Balanced liquidity")

    finally:
        await account.channel.close()

asyncio.run(calculate_liquidity())
```

### 4) Поиск уровней поддержки/сопротивления

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        sorted_levels = sorted(dom_data.mql_book_infos, key=lambda x: x.volume_real, reverse=True)

        print(f"[KEY LEVELS] {symbol} - Highest Volume Levels:\n")
        print(f"{'Rank':<6} {'Type':<10} {'Price':<15} {'Volume':<15}")
        print("-" * 50)

        for i, entry in enumerate(sorted_levels[:5], 1):
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{i:<6} {entry_type:<10} {entry.price:<15.5f} {entry.volume_real:<15.2f}")

        print("\n[NOTE] Large volume clusters may act as support/resistance")

    finally:
        await account.channel.close()

asyncio.run(find_key_levels())
```

### 5) Мониторинг дисбаланса DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_imbalance(duration: int = 30):
    """Monitor DOM imbalance for specified duration"""
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
        print(f"[MONITORING] {symbol} DOM imbalance for {duration} seconds\n")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            dom_data = await account.market_book_get(symbol)

            # Рассчитать дисбаланс
            sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
            buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

            if sell_volume + buy_volume > 0:
                imbalance = ((buy_volume - sell_volume) / (buy_volume + sell_volume)) * 100

                # Очистить экран
                print("\033[2J\033[H")

                print(f"=== {symbol} DOM Imbalance ===\n")
                print(f"BUY:  {buy_volume:>8.2f} lots")
                print(f"SELL: {sell_volume:>8.2f} lots")
                print(f"\nImbalance: {imbalance:+.2f}%")

                if imbalance > 20:
                    print("\n[SIGNAL] Strong BUY pressure")
                elif imbalance < -20:
                    print("\n[SIGNAL] Strong SELL pressure")
                else:
                    print("\n[SIGNAL] Balanced market")

            await asyncio.sleep(1)

        await account.market_book_release(symbol)
        print(f"\n[STOPPED] Monitoring ended")

    finally:
        await account.channel.close()

asyncio.run(monitor_imbalance(duration=30))
```

### 6) Анализ объёма по цене (Volume at Price, VAP)

```python
import asyncio
from MetaRpcMT5 import MT5Account
from collections import defaultdict

async def volume_at_price():
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

        # Сгруппировать объём по ценовым корзинам (например, диапазоны по 5 пипсов)
        pip_range = 5
        pip_size = 0.0001
        bin_size = pip_range * pip_size

        volume_bins = defaultdict(float)

        for entry in dom_data.mql_book_infos:
            # Округлить цену до ближайшей корзины
            bin_price = round(entry.price / bin_size) * bin_size
            volume_bins[bin_price] += entry.volume_real

        # Отсортировать по цене
        sorted_bins = sorted(volume_bins.items(), key=lambda x: x[0])

        print(f"[VOLUME AT PRICE] {symbol} ({pip_range} pip bins)\n")
        print(f"{'Price Range':<20} {'Volume':<15} {'Bar':<30}")
        print("-" * 70)

        max_volume = max(volume_bins.values()) if volume_bins else 1

        for price, volume in sorted_bins[:15]:  # Показать топ-15 корзин
            bar_length = int((volume / max_volume) * 30)
            bar = "#" * bar_length
            print(f"{price:.5f}-{price+bin_size:.5f}  {volume:>8.2f} lots  {bar}")

    finally:
        await account.channel.close()

asyncio.run(volume_at_price())
```

---

## 📚 См. также

* [MarketBookAdd](./market_book_add.md) - Подписаться на обновления DOM
* [MarketBookRelease](./market_book_release.md) - Отписаться от DOM
* [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Получить текущие цены тиков
