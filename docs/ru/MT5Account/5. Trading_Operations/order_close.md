# Закрытие позиции или ордера

> **Запрос:** Закрыть рыночную позицию или удалить отложенный ордер.

**Информация об API:**

* **Python API:** `MT5Account.order_close(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.TradingHelper`
* **Proto-определение:** `OrderClose` (определено в `mt5-term-api-trading-helper.proto`)
* **Enum'ы в этом методе:** 1 enum с 3 константами (1 выход)

### RPC

* **Сервис:** `mt5_term_api.TradingHelper`
* **Метод:** `OrderClose(OrderCloseRequest) -> OrderCloseReply`
* **Низкоуровневый клиент (сгенерированный):** `TradingHelperStub.OrderClose(request, metadata)`


## 💬 Только самое главное

* **Что это.** Закрывает рыночные позиции или удаляет отложенные ордера.
* **Зачем это нужно.** Выход из позиций или отмена отложенных ордеров.
* **Частичное закрытие.** Задайте volume < объёма позиции для частичного закрытия, либо 0 для закрытия всего.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Закрыть рыночные позиции полностью или частично
* Удалить отложенные ордера
* Быстро выйти из убыточных позиций
* Зафиксировать прибыль по прибыльным позициям
* Отменить неисполненные отложенные ордера


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


class MT5Account:
    # ...

    async def order_close(
        self,
        request: trading_pb2.OrderCloseRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Closes a market or pending order asynchronously.

        Returns:
            OrderCloseData: The close result and return codes.
        """
```

**Сообщение запроса:**

```protobuf
OrderCloseRequest {
  uint64 ticket = 1;      // Тикет ордера/позиции для закрытия
  double volume = 2;      // Объём для закрытия (0 = закрыть всё)
  int32 slippage = 5;     // Макс. проскальзывание в пунктах
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderCloseRequest`            | Запрос на закрытие (см. поля выше)            |
| `deadline`           | `Optional[datetime]`           | Крайний срок операции (опционально)           |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены запроса (опционально)       |

---

## ⬆️ Выход

Возвращает объект `OrderCloseData`.

**Поля OrderCloseData:**

| Поле                          | Тип       | Описание                             |
| ----------------------------- | --------- | ------------------------------------ |
| `returned_code`               | `int32`   | Код возврата (10009 = успех)         |
| `returned_string_code`        | `string`  | Строковый код возврата               |
| `returned_code_description`   | `string`  | Описание кода возврата               |
| `close_mode`                  | `int32`   | Использованный режим закрытия        |

---

## 🧱 Связанные enum'ы (из proto)

### `MRPC_ORDER_CLOSE_MODE`

Используется в `OrderCloseData` для указания режима закрытия.

| Имя константы                      | Значение | Описание                             |
| ---------------------------------- | ----- | ------------------------------------ |
| `MRPC_MARKET_ORDER_CLOSE`          | 0     | Полное закрытие позиции              |
| `MRPC_MARKET_ORDER_PARTIAL_CLOSE`  | 1     | Частичное закрытие позиции           |
| `MRPC_PENDING_ORDER_REMOVE`        | 2     | Удаление отложенного ордера          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Доступ к значениям enum
trading_pb2.MRPC_MARKET_ORDER_CLOSE          # = 0
trading_pb2.MRPC_MARKET_ORDER_PARTIAL_CLOSE  # = 1
trading_pb2.MRPC_PENDING_ORDER_REMOVE        # = 2
```

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OrderClose - Как это работает](../HOW_IT_WORK/5. Trading_Operations_HOW/order_close_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Код возврата:** Всегда проверяйте `returned_code == 10009` для подтверждения успеха.
* **Закрыть всё:** Задайте `volume = 0`, чтобы закрыть всю позицию.
* **Частичное закрытие:** Задайте `volume` в конкретном размере для частичного закрытия.
* **Проскальзывание:** Задавайте подходящее проскальзывание для рыночных позиций, чтобы допустить движение цены.
* **Отложенные ордера:** Проскальзывание игнорируется при закрытии отложенных ордеров.
* **Номер тикета:** Получите тикет из `opened_orders` или отслеживайте его при открытии позиций.
  
---

## 🔗 Примеры использования

### 1) Закрытие всей позиции

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def close_position():
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
        # Закрыть позицию с тикетом 123456
        request = trading_pb2.OrderCloseRequest(
            ticket=123456,
            volume=0,  # 0 = закрыть всё
            slippage=20  # 20 пунктов макс. проскальзывание
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Position closed!")
            print(f"  Mode: {result.close_mode}")
        else:
            print(f"[FAILED] Code: {result.returned_code}")
            print(f"  Description: {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(close_position())
```

### 2) Закрытие всех открытых позиций

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def close_all_positions():
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
        # Получить все открытые позиции
        request = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(request)

        closed_count = 0
        failed_count = 0

        # Закрыть каждую позицию
        for position in positions_data.positions:
            close_req = trading_pb2.OrderCloseRequest(
                ticket=position.ticket,
                volume=0,  # Закрыть всё
                slippage=20
            )

            result = await account.order_close(close_req)

            if result.returned_code == 10009:
                closed_count += 1
                print(f"[CLOSED] Position #{position.ticket}")
            else:
                failed_count += 1
                print(f"[FAILED] Position #{position.ticket}: "
                      f"{result.returned_code_description}")

        print(f"\n[SUMMARY] Closed: {closed_count}, Failed: {failed_count}")

    finally:
        await account.channel.close()

asyncio.run(close_all_positions())
```

### 3) Частичное закрытие позиции

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def partial_close():
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
        # Закрыть половину позиции в 0.10 лотов
        request = trading_pb2.OrderCloseRequest(
            ticket=123456,
            volume=0.05,  # Закрыть 0.05 лотов
            slippage=20
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Partial close executed!")
            print(f"  Closed volume: 0.05 lots")
            print(f"  Remaining: 0.05 lots")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(partial_close())
```

### 4) Удаление отложенного ордера

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def delete_pending_order():
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
        # Удалить отложенный ордер
        request = trading_pb2.OrderCloseRequest(
            ticket=789012,
            volume=0,
            slippage=0  # Проскальзывание не используется для отложенных ордеров
        )

        result = await account.order_close(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Pending order deleted!")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(delete_pending_order())
```

### 5) Закрытие позиций по символу

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def close_by_symbol(symbol: str):
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
        # Получить все открытые позиции
        request = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(request)

        closed = []
        failed = []

        # Закрыть позиции по конкретному символу
        for position in positions_data.positions:
            if position.symbol == symbol:
                close_req = trading_pb2.OrderCloseRequest(
                    ticket=position.ticket,
                    volume=0,
                    slippage=20
                )

                result = await account.order_close(close_req)

                if result.returned_code == 10009:
                    closed.append(position.ticket)
                    print(f"[CLOSED] {symbol} position #{position.ticket}")
                else:
                    failed.append(position.ticket)
                    print(f"[FAILED] #{position.ticket}: "
                          f"{result.returned_code_description}")

        print(f"\n[{symbol}] Closed: {len(closed)}, Failed: {len(failed)}")

    finally:
        await account.channel.close()

# Закрыть все позиции EURUSD
asyncio.run(close_by_symbol("EURUSD"))
```

### 6) Закрытие с повторами и обработкой ошибок

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def close_with_retry(ticket: int, max_retries=3):
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
        for attempt in range(1, max_retries + 1):
            print(f"[ATTEMPT {attempt}/{max_retries}]")

            request = trading_pb2.OrderCloseRequest(
                ticket=ticket,
                volume=0,
                slippage=30  # Допустить более высокое проскальзывание при повторах
            )

            try:
                result = await account.order_close(request)

                if result.returned_code == 10009:
                    print(f"[SUCCESS] Position closed on attempt {attempt}!")
                    return True
                else:
                    print(f"[FAILED] Code: {result.returned_code}")
                    print(f"  Description: {result.returned_code_description}")

                    if attempt < max_retries:
                        print(f"  Retrying in 1 second...")
                        await asyncio.sleep(1)

            except Exception as e:
                print(f"[ERROR] {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)

        print(f"[GIVING UP] Failed to close position after {max_retries} attempts")
        return False

    finally:
        await account.channel.close()

asyncio.run(close_with_retry(123456))
```

---

## 📚 См. также

* [OrderSend](./order_send.md) - Открытие позиций
* [OrderModify](./order_modify.md) - Изменение позиций/ордеров
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Получить открытые позиции
