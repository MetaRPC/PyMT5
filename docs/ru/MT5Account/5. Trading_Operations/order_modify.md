# Изменение ордера или позиции

> **Запрос:** Изменить Stop Loss, Take Profit, цену или срок действия ордера/позиции.

**Информация об API:**

* **Python API:** `MT5Account.order_modify(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.TradingHelper`
* **Proto-определение:** `OrderModify` (определено в `mt5-term-api-trading-helper.proto`)
* **Enum'ы в этом методе:** 1 enum с 4 константами (1 вход)

### RPC

* **Сервис:** `mt5_term_api.TradingHelper`
* **Метод:** `OrderModify(OrderModifyRequest) -> OrderModifyReply`
* **Низкоуровневый клиент (сгенерированный):** `TradingHelperStub.OrderModify(request, metadata)`


## 💬 Только самое главное

* **Что это.** Изменяет SL/TP, цену или срок действия существующих ордеров/позиций.
* **Зачем это нужно.** Корректировка уровней управления рисками или параметров отложенных ордеров.
* **Установить в ноль.** Используйте 0 для удаления SL или TP.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Добавить или изменить уровни Stop Loss
* Добавить или изменить уровни Take Profit
* Изменить цены отложенных ордеров
* Обновить время истечения ордеров
* Корректировать трейлинг-стопы
* Удалить SL/TP (установив в 0)


```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

class MT5Account:
    # ...

    async def order_modify(
        self,
        request: trading_pb2.OrderModifyRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Modifies an existing order or position asynchronously.

        Returns:
            OrderModifyData: Response containing updated order/deal info.
        """
```

**Сообщение запроса:**

```protobuf
OrderModifyRequest {
  uint64 ticket = 1;                             // Тикет ордера/позиции для изменения
  double stop_loss = 2;                          // Новая цена стоп-лосса (0 = удалить)
  double take_profit = 3;                        // Новая цена тейк-профита (0 = удалить)
  double price = 4;                              // Новая цена (для отложенных ордеров)
  TMT5_ENUM_ORDER_TYPE_TIME expiration_time_type = 5;  // Новый тип истечения
  google.protobuf.Timestamp expiration_time = 6;       // Новое время истечения
  double stop_limit = 8;                         // Новая цена stop-limit
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderModifyRequest`           | Запрос на изменение (см. поля выше)           |
| `deadline`           | `Optional[datetime]`           | Крайний срок операции (опционально)           |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены запроса (опционально)       |

---

## ⬆️ Выход

Возвращает объект `OrderModifyData`.

**Поля OrderModifyData:**

| Поле                          | Тип       | Описание                             |
| ----------------------------- | --------- | ------------------------------------ |
| `returned_code`               | `int32`   | Код возврата (10009 = успех)         |
| `returned_string_code`        | `string`  | Строковый код возврата               |
| `returned_code_description`   | `string`  | Описание кода возврата               |
| `deal`                        | `uint64`  | Тикет сделки (если исполнено)        |
| `order`                       | `uint64`  | Тикет ордера                         |
| `volume`                      | `double`  | Объём                                |
| `price`                       | `double`  | Цена исполнения                      |
| `bid`                         | `double`  | Текущая цена bid                     |
| `ask`                         | `double`  | Текущая цена ask                     |
| `comment`                     | `string`  | Комментарий брокера                  |
| `request_id`                  | `uint64`  | ID запроса                           |
| `ret_code_external`           | `uint32`  | Внешний код возврата                 |

---

## 🧱 Связанные enum'ы (из proto)

### `TMT5_ENUM_ORDER_TYPE_TIME`

Используется в `OrderModifyRequest` для указания типа срока действия.

| Имя константы                   | Значение | Описание                             |
| ------------------------------- | ----- | ------------------------------------ |
| `TMT5_ORDER_TIME_GTC`           | 0     | Действует до отмены                  |
| `TMT5_ORDER_TIME_DAY`           | 1     | Действует до конца текущего торгового дня |
| `TMT5_ORDER_TIME_SPECIFIED`     | 2     | Действует до указанной даты          |
| `TMT5_ORDER_TIME_SPECIFIED_DAY` | 3     | Действует до указанного дня          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Доступ к значениям enum
trading_pb2.TMT5_ORDER_TIME_GTC            # = 0
trading_pb2.TMT5_ORDER_TIME_DAY            # = 1
trading_pb2.TMT5_ORDER_TIME_SPECIFIED      # = 2
trading_pb2.TMT5_ORDER_TIME_SPECIFIED_DAY  # = 3
```

---


## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OrderModify - Как это работает](../HOW_IT_WORK/5. Trading_Operations_HOW/order_modify_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Ноль для удаления:** Задайте `stop_loss=0` или `take_profit=0`, чтобы удалить их.
* **Отложенные ордера:** Можно изменять цену и срок действия отложенных ордеров.
* **Рыночные позиции:** Для рыночных позиций можно изменять только SL/TP.
* **Минимальная дистанция:** Брокер требует минимальную дистанцию от текущей цены для SL/TP.
* **Уровень заморозки (freeze level):** Нельзя изменять ордера слишком близко к рыночной цене (настройка брокера).

---

## 🔗 Примеры использования

### 1) Добавление Stop Loss к позиции

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def add_stop_loss():
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
        # Получить текущую цену
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)
        current_bid = tick_data.tick.bid

        # Установить SL на 50 пипсов ниже текущей цены
        pip_size = 0.0001
        sl_price = current_bid - (50 * pip_size)

        # Изменить позицию, добавив SL
        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=sl_price,
            take_profit=0,  # Оставить текущий TP или без TP
            price=0         # Не используется для рыночных позиций
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Stop Loss added at {sl_price:.5f}")

    finally:
        await account.channel.close()

asyncio.run(add_stop_loss())
```

### 2) Изменение одновременно SL и TP

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def modify_sl_tp():
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
        # Получить текущую цену
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)
        current_bid = tick_data.tick.bid

        pip_size = 0.0001
        new_sl = current_bid - (30 * pip_size)  # SL 30 пипсов
        new_tp = current_bid + (60 * pip_size)  # TP 60 пипсов (R:R 2:1)

        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=new_sl,
            take_profit=new_tp,
            price=0
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Modified SL/TP!")
        print(f"  New SL: {new_sl:.5f}")
        print(f"  New TP: {new_tp:.5f}")

    finally:
        await account.channel.close()

asyncio.run(modify_sl_tp())
```

### 3) Удаление Stop Loss

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def remove_stop_loss():
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
        # Установить SL в 0, чтобы удалить его
        request = trading_pb2.OrderModifyRequest(
            ticket=123456,
            stop_loss=0,     # Удалить SL
            take_profit=0,   # Оставить текущий TP
            price=0
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Stop Loss removed!")

    finally:
        await account.channel.close()

asyncio.run(remove_stop_loss())
```

### 4) Изменение цены отложенного ордера

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def modify_pending_order_price():
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
        # Получить текущую цену
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)
        current_bid = tick_data.tick.bid

        # Новая цена BUY LIMIT (на 15 пипсов ниже текущей)
        pip_size = 0.0001
        new_price = current_bid - (15 * pip_size)

        request = trading_pb2.OrderModifyRequest(
            ticket=789012,  # Тикет отложенного ордера
            stop_loss=0,
            take_profit=0,
            price=new_price  # Новая цена входа
        )

        result = await account.order_modify(request)
        print(f"[SUCCESS] Pending order price updated to {new_price:.5f}")

    finally:
        await account.channel.close()

asyncio.run(modify_pending_order_price())
```

### 5) Реализация трейлинг-стопа

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def trailing_stop(ticket: int, trail_distance_pips: int):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    pip_size = 0.0001
    last_sl = None

    try:
        while True:
            # Получить текущую цену
            tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
            tick_data = await account.symbol_info_tick(tick_req)
            current_bid = tick_data.tick.bid

            # Рассчитать новый SL
            new_sl = current_bid - (trail_distance_pips * pip_size)

            # Обновлять только если новый SL выше (для BUY)
            if last_sl is None or new_sl > last_sl:
                request = trading_pb2.OrderModifyRequest(
                    ticket=ticket,
                    stop_loss=new_sl,
                    take_profit=0,
                    price=0
                )

                result = await account.order_modify(request)
                print(f"[TRAIL] SL updated to {new_sl:.5f}")
                last_sl = new_sl

            await asyncio.sleep(1)  # Проверять каждую секунду

    except KeyboardInterrupt:
        print("\nTrailing stop stopped")

    finally:
        await account.channel.close()

# Трейлинг-стоп на 30 пипсов позади цены
asyncio.run(trailing_stop(123456, 30))
```

### 6) Перевод Stop Loss в безубыток

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2

async def move_to_breakeven(ticket: int, breakeven_trigger_pips: int):
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
        # Получить сведения о позиции
        positions_req = account_pb2.OpenedOrdersRequest()
        positions_data = await account.opened_orders(positions_req)

        position = next((p for p in positions_data.positions if p.ticket == ticket), None)

        if not position:
            print(f"[ERROR] Position #{ticket} not found")
            return

        entry_price = position.price_open
        pip_size = 0.0001

        # Проверить, достигла ли прибыль уровня срабатывания
        profit_pips = (position.price_current - entry_price) / pip_size

        if profit_pips >= breakeven_trigger_pips:
            # Перевести SL в безубыток
            request = trading_pb2.OrderModifyRequest(
                ticket=ticket,
                stop_loss=entry_price,  # Установить SL на цену входа
                take_profit=0,
                price=0
            )

            result = await account.order_modify(request)
            print(f"[BREAKEVEN] SL moved to entry price {entry_price:.5f}")
            print(f"  Current profit: {profit_pips:.1f} pips")
        else:
            print(f"[WAITING] Profit {profit_pips:.1f} pips < trigger {breakeven_trigger_pips} pips")

    finally:
        await account.channel.close()

# Перевести в безубыток, когда прибыль достигнет 20 пипсов
asyncio.run(move_to_breakeven(123456, 20))
```

---

## 📚 См. также

* [OrderSend](./order_send.md) - Открытие позиций
* [OrderClose](./order_close.md) - Закрытие позиций
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Получить сведения о позициях
