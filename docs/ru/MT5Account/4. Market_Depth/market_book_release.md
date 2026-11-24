# Отписка от стакана (глубины рынка)

> **Запрос:** Отписаться от обновлений стакана (Depth of Market, стакан ордеров) для символа.

**Информация об API:**

* **Python API:** `MT5Account.market_book_release(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `MarketBookRelease` (определено в `mt5-term-api-market-info.proto`)
* **Enum'ы в этом методе:** 0 enum'ов (простой булев результат)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `MarketBookRelease(MarketBookReleaseRequest) -> MarketBookReleaseReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.MarketBookRelease(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def market_book_release(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookReleaseData:
        """
        Closes the Depth of Market (DOM) for a symbol and unsubscribes from updates.

        Returns:
            MarketBookReleaseData: Unsubscription result.
        """
```

**Сообщение запроса:**

```protobuf
MarketBookReleaseRequest {
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

Возвращает объект `MarketBookReleaseData`.

**Поля MarketBookReleaseData:**

| Поле                   | Тип    | Описание                             |
| ---------------------- | ------ | ------------------------------------ |
| `closed_successfully`  | `bool` | True, если отписка прошла успешно    |

---

## 💬 Только суть

* **Что это.** Отписывается от рыночных данных Level 2 (стакан ордеров) для символа.
* **Зачем это нужно.** Освобождение ресурсов и прекращение получения обновлений DOM, когда они больше не нужны.
* **Лучшая практика.** Всегда вызывайте по завершении мониторинга DOM, чтобы освободить ресурсы.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Отписаться от обновлений DOM
* Освободить системные ресурсы
* Выполнить очистку после анализа DOM
* Остановить мониторинг глубины рынка
* Управлять жизненным циклом подписки
* Снизить использование пропускной способности

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[MarketBookRelease - How it works](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Освобождение ресурсов:** Всегда вызывайте это по завершении мониторинга DOM.
* **Нет ошибки при отсутствии подписки:** Безопасно вызывать, даже если подписки в данный момент нет.
* **По отдельным символам:** Каждый символ нужно освобождать отдельно.
* **В паре с add:** Каждому `market_book_add` должен соответствовать `market_book_release`.
* **Очистка сессии:** Подписки сохраняются до явного освобождения или завершения сессии.
* **Проверяйте успех:** Всегда проверяйте `closed_successfully == True`.

---

## 🔗 Примеры использования

### 1) Базовая отписка

```python
import asyncio
from MetaRpcMT5 import MT5Account

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
        symbol = "EURUSD"

        # Подписаться на DOM
        add_result = await account.market_book_add(symbol)
        if add_result.opened_successfully:
            print(f"[SUBSCRIBED] {symbol} DOM")

        # Выполнить какой-то анализ...
        dom_data = await account.market_book_get(symbol)
        print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} DOM levels")

        # Отписаться по завершении
        release_result = await account.market_book_release(symbol)
        if release_result.closed_successfully:
            print(f"[UNSUBSCRIBED] {symbol} DOM released")

    finally:
        await account.channel.close()

asyncio.run(unsubscribe_dom())
```

### 2) Шаблон контекстного менеджера

```python
import asyncio
from MetaRpcMT5 import MT5Account
from contextlib import asynccontextmanager

@asynccontextmanager
async def dom_subscription(account, symbol):
    """Context manager for automatic DOM subscription cleanup"""
    try:
        # Подписаться
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"Failed to subscribe to {symbol} DOM")

        print(f"[SUBSCRIBED] {symbol} DOM")
        yield
    finally:
        # Всегда освобождать при выходе
        await account.market_book_release(symbol)
        print(f"[RELEASED] {symbol} DOM")

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
        async with dom_subscription(account, "EURUSD"):
            # DOM активен здесь
            dom_data = await account.market_book_get("EURUSD")
            print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} DOM levels")
        # DOM автоматически освобождается здесь

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 3) Освобождение нескольких символов

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def release_multiple_symbols():
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
        # Подписаться на несколько символов
        print("[SUBSCRIBING] To multiple symbols...")
        for symbol in symbols:
            result = await account.market_book_add(symbol)
            if result.opened_successfully:
                print(f"  [OK] {symbol} subscribed")

        # Выполнить анализ...
        await asyncio.sleep(5)

        # Освободить все символы
        print("\n[RELEASING] All subscriptions...")
        for symbol in symbols:
            result = await account.market_book_release(symbol)
            if result.closed_successfully:
                print(f"  [OK] {symbol} released")

    finally:
        await account.channel.close()

asyncio.run(release_multiple_symbols())
```

### 4) Обработка ошибок и очистка

```python
import asyncio
from MetaRpcMT5 import MT5Account, ApiExceptionMT5

async def safe_dom_usage():
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
    subscribed = False

    try:
        # Подписаться
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] Failed to subscribe to {symbol}")
            return

        subscribed = True
        print(f"[SUBSCRIBED] {symbol} DOM")

        # Выполнить анализ
        dom_data = await account.market_book_get(symbol)
        print(f"[ANALYSIS] {len(dom_data.mql_book_infos)} levels")

    except ApiExceptionMT5 as e:
        print(f"[API ERROR] {e}")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

    finally:
        # Всегда выполнять очистку, если была подписка
        if subscribed:
            try:
                release_result = await account.market_book_release(symbol)
                if release_result.closed_successfully:
                    print(f"[CLEANUP] {symbol} DOM released successfully")
                else:
                    print(f"[WARNING] Failed to release {symbol} DOM")
            except Exception as e:
                print(f"[CLEANUP ERROR] {e}")

        await account.channel.close()

asyncio.run(safe_dom_usage())
```

### 5) Класс менеджера подписок

```python
import asyncio
from MetaRpcMT5 import MT5Account

class DOMSubscriptionManager:
    def __init__(self, account):
        self.account = account
        self.active_subscriptions = set()

    async def subscribe(self, symbol: str):
        """Subscribe to DOM with tracking"""
        result = await self.account.market_book_add(symbol)

        if result.opened_successfully:
            self.active_subscriptions.add(symbol)
            print(f"[SUBSCRIBED] {symbol} (Total: {len(self.active_subscriptions)})")
            return True
        else:
            print(f"[FAILED] Could not subscribe to {symbol}")
            return False

    async def unsubscribe(self, symbol: str):
        """Unsubscribe from DOM"""
        if symbol not in self.active_subscriptions:
            print(f"[WARNING] {symbol} not in active subscriptions")
            return False

        result = await self.account.market_book_release(symbol)

        if result.closed_successfully:
            self.active_subscriptions.remove(symbol)
            print(f"[UNSUBSCRIBED] {symbol} (Remaining: {len(self.active_subscriptions)})")
            return True
        else:
            print(f"[FAILED] Could not unsubscribe from {symbol}")
            return False

    async def release_all(self):
        """Release all active subscriptions"""
        print(f"[RELEASING] All {len(self.active_subscriptions)} subscriptions...")

        for symbol in list(self.active_subscriptions):
            await self.unsubscribe(symbol)

        print(f"[DONE] All subscriptions released")

    def list_active(self):
        """List all active subscriptions"""
        return list(self.active_subscriptions)

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

    manager = DOMSubscriptionManager(account)

    try:
        # Подписаться на несколько символов
        await manager.subscribe("EURUSD")
        await manager.subscribe("GBPUSD")
        await manager.subscribe("USDJPY")

        print(f"\n[ACTIVE] Subscriptions: {manager.list_active()}")

        # Выполнить анализ...
        await asyncio.sleep(5)

        # Освободить конкретный символ
        await manager.unsubscribe("GBPUSD")

        # Освободить все оставшиеся
        await manager.release_all()

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 6) Вспомогательная функция временного снимка DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def get_dom_snapshot(account, symbol: str):
    """
    Helper function to get a quick DOM snapshot with automatic cleanup.
    Subscribe -> Get data -> Release
    """
    try:
        # Подписаться
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] Failed to subscribe to {symbol}")
            return None

        # Получить данные DOM
        dom_data = await account.market_book_get(symbol)

        return dom_data

    finally:
        # Всегда освобождать
        try:
            await account.market_book_release(symbol)
        except Exception as e:
            print(f"[WARNING] Cleanup error: {e}")

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
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        for symbol in symbols:
            print(f"\n[SNAPSHOT] Getting {symbol} DOM...")

            dom_data = await get_dom_snapshot(account, symbol)

            if dom_data:
                sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
                buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

                print(f"  Levels: {len(dom_data.mql_book_infos)}")
                print(f"  BUY volume: {buy_volume:.2f} lots")
                print(f"  SELL volume: {sell_volume:.2f} lots")

            await asyncio.sleep(1)  # Краткая пауза между снимками

    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 См. также

* [MarketBookAdd](./market_book_add.md) - Подписаться на обновления DOM
* [MarketBookGet](./market_book_get.md) - Получить данные DOM
* [SymbolSelect](../2.%20Symbol_Information/symbol_select.md) - Управление символами Market Watch
