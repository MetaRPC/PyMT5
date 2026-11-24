# Подписка на стакан (глубину рынка, DOM)

> **Запрос:** Подписаться на обновления стакана (Depth of Market, стакан ордеров) для символа.

**Информация об API:**

* **Python API:** `MT5Account.market_book_add(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `MarketBookAdd` (определено в `mt5-term-api-market-info.proto`)
* **Enum'ы в этом методе:** 0 enum'ов (простой булев результат)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `MarketBookAdd(MarketBookAddRequest) -> MarketBookAddReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.MarketBookAdd(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def market_book_add(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookAddData:
        """
        Opens the Depth of Market (DOM) for a symbol and subscribes to updates.

        Returns:
            MarketBookAddData: Subscription result.
        """
```

**Сообщение запроса:**

```protobuf
MarketBookAddRequest {
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

Возвращает объект `MarketBookAddData`.

**Поля MarketBookAddData:**

| Поле                   | Тип    | Описание                             |
| ---------------------- | ------ | ------------------------------------ |
| `opened_successfully`  | `bool` | True, если подписка прошла успешно   |

---

## 💬 Только суть

* **Что это.** Подписывается на рыночные данные Level 2 (стакан ордеров) для символа.
* **Зачем это нужно.** Требуется перед вызовом `market_book_get` для получения данных DOM.
* **Однократная подписка.** Вызывайте один раз для каждого символа, затем используйте `market_book_get` для получения данных.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Подписаться на обновления стакана (DOM)
* Включить доступ к данным Level 2 для символа
* Подготовиться к анализу стакана ордеров
* Отслеживать уровни ликвидности bid/ask
* Анализировать микроструктуру рынка

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[market_book_add - How it works](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Требуется подписка:** Необходимо вызвать это перед `market_book_get`.
* **Символ должен быть выбран:** Убедитесь, что символ находится в Market Watch перед подпиской.
* **Поддержка брокером:** Не все брокеры предоставляют данные DOM.
* **Освобождение ресурсов:** Вызывайте `market_book_release` по завершении, чтобы отписаться.
* **Одна подписка:** Для каждого символа достаточно подписаться один раз.
* **Проверяйте успех:** Всегда проверяйте `opened_successfully == True`.

---

## 🔗 Примеры использования

### 1) Подписка на DOM для EURUSD

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        # Подписаться на DOM
        result = await account.market_book_add("EURUSD")

        if result.opened_successfully:
            print(f"[SUCCESS] Subscribed to EURUSD DOM")
        else:
            print(f"[FAILED] Could not subscribe to DOM")

    finally:
        await account.channel.close()

asyncio.run(subscribe_dom())
```

### 2) Подписка и проверка

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def subscribe_and_verify():
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

        # Сначала убедиться, что символ выбран в Market Watch
        await account.symbol_select(symbol=symbol, select=True)
        print(f"[1] Symbol {symbol} selected in Market Watch")

        # Теперь подписаться на DOM
        result = await account.market_book_add(symbol)

        if result.opened_successfully:
            print(f"[2] Successfully subscribed to {symbol} DOM")

            # Проверить, получив данные DOM
            dom_data = await account.market_book_get(symbol)
            print(f"[3] DOM has {len(dom_data.mql_book_infos)} levels")
        else:
            print(f"[2] Failed to subscribe to DOM")

    finally:
        await account.channel.close()

asyncio.run(subscribe_and_verify())
```

### 3) Подписка на несколько символов

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def subscribe_multiple():
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
        for symbol in symbols:
            result = await account.market_book_add(symbol)

            if result.opened_successfully:
                print(f"[OK] {symbol} - DOM subscribed")
            else:
                print(f"[FAIL] {symbol} - Could not subscribe")

    finally:
        await account.channel.close()

asyncio.run(subscribe_multiple())
```

### 4) Подписка с обработкой ошибок

```python
import asyncio
from MetaRpcMT5 import MT5Account, ApiExceptionMT5

async def subscribe_with_error_handling():
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
        # Подписаться на DOM
        result = await account.market_book_add(symbol)

        if result.opened_successfully:
            print(f"[SUCCESS] Subscribed to {symbol} DOM")
            return True
        else:
            print(f"[WARNING] Subscription returned false")
            return False

    except ApiExceptionMT5 as e:
        print(f"[API ERROR] {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

    finally:
        await account.channel.close()

asyncio.run(subscribe_with_error_handling())
```

### 5) Проверка поддержки DOM брокером

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def check_dom_support():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

    try:
        print("Checking DOM support for symbols:\n")
        print(f"{'Symbol':<10} {'DOM Support':<15}")
        print("-" * 30)

        for symbol in test_symbols:
            try:
                result = await account.market_book_add(symbol)

                if result.opened_successfully:
                    # Попытаться получить данные DOM
                    dom_data = await account.market_book_get(symbol)

                    if len(dom_data.mql_book_infos) > 0:
                        print(f"{symbol:<10} {'YES ('+str(len(dom_data.mql_book_infos))+' levels)':<15}")
                    else:
                        print(f"{symbol:<10} {'NO DATA':<15}")

                    # Очистка
                    await account.market_book_release(symbol)
                else:
                    print(f"{symbol:<10} {'NOT SUPPORTED':<15}")

            except Exception as e:
                print(f"{symbol:<10} {'ERROR':<15}")

    finally:
        await account.channel.close()

asyncio.run(check_dom_support())
```

### 6) Подписка и мониторинг DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_dom(symbol: str, duration: int = 10):
    """Subscribe and monitor DOM for specified duration"""
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
        # Подписаться на DOM
        result = await account.market_book_add(symbol)

        if not result.opened_successfully:
            print(f"[FAILED] Could not subscribe to {symbol} DOM")
            return

        print(f"[SUBSCRIBED] Monitoring {symbol} DOM for {duration} seconds\n")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            # Получить текущее состояние DOM
            dom_data = await account.market_book_get(symbol)

            # Очистить экран
            print("\033[2J\033[H")

            print(f"=== {symbol} Market Depth ===")
            print(f"Total levels: {len(dom_data.mql_book_infos)}\n")

            print(f"{'Type':<10} {'Price':<15} {'Volume':<15}")
            print("-" * 45)

            for book_entry in dom_data.mql_book_infos[:10]:  # Показать первые 10 уровней
                entry_type = "BUY" if book_entry.type in [1, 3] else "SELL"
                print(f"{entry_type:<10} {book_entry.price:<15.5f} {book_entry.volume_real:<15.2f}")

            await asyncio.sleep(1)  # Обновлять каждую секунду

        # Отписаться по завершении
        await account.market_book_release(symbol)
        print(f"\n[UNSUBSCRIBED] Stopped monitoring {symbol} DOM")

    finally:
        await account.channel.close()

asyncio.run(monitor_dom("EURUSD", duration=10))
```

---

## 📚 См. также

* [MarketBookGet](./market_book_get.md) - Получить текущие данные DOM
* [MarketBookRelease](./market_book_release.md) - Отписаться от DOM
* [SymbolSelect](../2.%20Symbol_Information/symbol_select.md) - Добавить символ в Market Watch
