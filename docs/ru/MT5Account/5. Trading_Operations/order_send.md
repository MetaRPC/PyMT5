# Отправка рыночного или отложенного ордера

> **Запрос:** Отправить рыночный или отложенный ордер на торговый сервер.

**Информация об API:**

* **Python API:** `MT5Account.order_send(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.TradingHelper`
* **Proto-определение:** `OrderSend` (определено в `mt5-term-api-trading-helper.proto`)
* **Enum'ы в этом методе:** 2 enum'а с 13 константами (2 входа)

### RPC

* **Сервис:** `mt5_term_api.TradingHelper`
* **Метод:** `OrderSend(OrderSendRequest) -> OrderSendReply`
* **Низкоуровневый клиент (сгенерированный):** `TradingHelperStub.OrderSend(request, metadata)`

---

## 💬 Только самое главное

* **Что это.** Отправляет рыночные или отложенные ордера на торговый сервер MT5.
* **Зачем это нужно.** Основной метод для открытия позиций и размещения отложенных ордеров.
* **Код успеха.** Код возврата 10009 означает успех.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Открывать рыночные позиции (BUY или SELL)
* Размещать отложенные ордера (LIMIT, STOP, STOP_LIMIT)
* Устанавливать уровни Stop Loss и Take Profit
* Указывать срок действия ордера
* Добавлять комментарии к ордерам и magic-номера

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OrderSend - Как это работает](../HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW.md)**

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

class MT5Account:
    # ...

    async def order_send(
        self,
        request: trading_pb2.OrderSendRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trading_pb2.OrderSendData:
        """
        Sends a market or pending order to the trading server asynchronously.

        Returns:
            OrderSendData: Response with deal/order confirmation data.
        """
```

**Сообщение запроса:**

```protobuf
message OrderSendRequest {
  string symbol = 1;                             // Торговый символ
  TMT5_ENUM_ORDER_TYPE operation = 2;            // Тип ордера (BUY, SELL, BUY_LIMIT и т.д.)
  double volume = 3;                             // Объём ордера в лотах
  double price = 4;                              // Цена ордера (для отложенных ордеров)
  uint64 slippage = 5;                           // Макс. проскальзывание в пунктах
  double stop_loss = 6;                          // Цена стоп-лосса (необязательно)
  double take_profit = 7;                        // Цена тейк-профита (необязательно)
  string comment = 8;                            // Комментарий к ордеру
  uint64 expert_id = 9;                          // ID советника (magic number)
  double stop_limit_price = 10;                  // Цена stop-limit (для ордеров STOP_LIMIT)
  TMT5_ENUM_ORDER_TYPE_TIME expiration_time_type = 11;  // Тип истечения (GTC, DAY и т.д.)
  google.protobuf.Timestamp expiration_time = 12;       // Время истечения
}
```

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `request`            | `OrderSendRequest`             | Запрос ордера (см. поля выше)                 |
| `deadline`           | `Optional[datetime]`           | Крайний срок операции (опционально)           |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены запроса (опционально)       |

---

## ⬆️ Выход

Возвращает объект `OrderSendData`.

**Поля OrderSendData:**

| Поле                          | Тип       | Описание                             |
| ----------------------------- | --------- | ------------------------------------ |
| `returned_code`               | `uint32`  | Код возврата (10009 = успех)         |
| `deal`                        | `uint32`  | Тикет сделки (для рыночных ордеров)  |
| `order`                       | `uint32`  | Тикет ордера (для отложенных ордеров)|
| `volume`                      | `double`  | Исполненный объём                    |
| `price`                       | `double`  | Цена исполнения                      |
| `bid`                         | `double`  | Текущая цена Bid                     |
| `ask`                         | `double`  | Текущая цена Ask                     |
| `comment`                     | `string`  | Комментарий брокера                  |
| `request_id`                  | `uint32`  | ID запроса                           |
| `ret_code_external`           | `uint64`  | Внешний код возврата                 |
| `returned_string_code`        | `string`  | Строковый код возврата               |
| `returned_code_description`   | `string`  | Описание кода возврата               |

---

## 🧱 Связанные enum'ы (из proto)

### `TMT5_ENUM_ORDER_TYPE`

Используется в `OrderSendRequest` для указания типа ордера.

| Имя константы                     | Значение | Описание                             |
| --------------------------------- | ----- | ------------------------------------ |
| `TMT5_ORDER_TYPE_BUY`             | 0     | Рыночный ордер на покупку            |
| `TMT5_ORDER_TYPE_SELL`            | 1     | Рыночный ордер на продажу            |
| `TMT5_ORDER_TYPE_BUY_LIMIT`       | 2     | Отложенный ордер buy limit           |
| `TMT5_ORDER_TYPE_SELL_LIMIT`      | 3     | Отложенный ордер sell limit          |
| `TMT5_ORDER_TYPE_BUY_STOP`        | 4     | Отложенный ордер buy stop            |
| `TMT5_ORDER_TYPE_SELL_STOP`       | 5     | Отложенный ордер sell stop           |
| `TMT5_ORDER_TYPE_BUY_STOP_LIMIT`  | 6     | Отложенный ордер buy stop limit      |
| `TMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7     | Отложенный ордер sell stop limit     |
| `TMT5_ORDER_TYPE_CLOSE_BY`        | 8     | Закрытие встречной позицией          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Доступ к значениям enum
trading_pb2.TMT5_ORDER_TYPE_BUY             # = 0
trading_pb2.TMT5_ORDER_TYPE_SELL            # = 1
trading_pb2.TMT5_ORDER_TYPE_BUY_LIMIT       # = 2
trading_pb2.TMT5_ORDER_TYPE_SELL_LIMIT      # = 3
trading_pb2.TMT5_ORDER_TYPE_BUY_STOP        # = 4
trading_pb2.TMT5_ORDER_TYPE_SELL_STOP       # = 5
trading_pb2.TMT5_ORDER_TYPE_BUY_STOP_LIMIT  # = 6
trading_pb2.TMT5_ORDER_TYPE_SELL_STOP_LIMIT # = 7
trading_pb2.TMT5_ORDER_TYPE_CLOSE_BY        # = 8
```

### `TMT5_ENUM_ORDER_TYPE_TIME`

Используется в `OrderSendRequest` для указания срока жизни ордера.

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

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных gRPC-ошибок с автоматическим переподключением через `execute_with_reconnect`.
* **Код возврата:** Всегда проверяйте `returned_code == 10009` для подтверждения успеха.
* **Рыночный vs отложенный:** Используйте operation 0 (BUY) или 1 (SELL) для рыночных ордеров, другие коды для отложенных ордеров.
* **Проскальзывание:** Задавайте подходящее проскальзывание для рыночных ордеров, чтобы допустить движение цены.
* **Объём:** Объём указывается в лотах (например, 0.01 = 1 микролот).
* **SL/TP:** Можно задать при размещении ордера или изменить позже.
* **Magic-номер:** Используйте `expert_id` для идентификации ордеров вашего советника (EA).
* **Проверка:** Используйте `order_check` перед отправкой для проверки ордера.

---

## 🔗 Примеры использования

### 1) Отправка рыночного ордера BUY

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def market_buy():
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
        # Создать запрос рыночного ордера BUY
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,  # 0.01 лота (1 микролот)
            price=0,      # 0 для рыночных ордеров
            slippage=20,  # 20 пунктов макс. проскальзывание
            stop_loss=0,  # Без SL
            take_profit=0,  # Без TP
            comment="Market BUY",
            expert_id=12345
        )

        # Отправить ордер
        result = await account.order_send(request)

        # Проверить результат
        if result.returned_code == 10009:
            print(f"[SUCCESS] Order executed!")
            print(f"  Deal: #{result.deal}")
            print(f"  Volume: {result.volume}")
            print(f"  Price: {result.price}")
            print(f"  Bid: {result.bid}, Ask: {result.ask}")
        else:
            print(f"[FAILED] Code: {result.returned_code}")
            print(f"  Description: {result.returned_code_description}")
            print(f"  Comment: {result.comment}")

    finally:
        await account.channel.close()

asyncio.run(market_buy())
```

### 2) Отправка рыночного ордера с SL/TP

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def market_order_with_sl_tp():
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
        # Сначала получить текущую цену
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_ask = tick_data.tick.ask
        current_bid = tick_data.tick.bid

        # Рассчитать уровни SL/TP (50 пипсов)
        pip_size = 0.0001
        sl_price = current_ask - (50 * pip_size)  # На 50 пипсов ниже
        tp_price = current_ask + (50 * pip_size)  # На 50 пипсов выше

        # Создать ордер BUY с SL/TP
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,
            price=0,
            slippage=20,
            stop_loss=sl_price,
            take_profit=tp_price,
            comment="BUY with SL/TP",
            expert_id=12345
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] Order with SL/TP executed!")
            print(f"  Entry: {result.price:.5f}")
            print(f"  SL: {sl_price:.5f}")
            print(f"  TP: {tp_price:.5f}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(market_order_with_sl_tp())
```

### 3) Размещение отложенного ордера BUY LIMIT

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def buy_limit_order():
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

        # Разместить BUY LIMIT на 20 пипсов ниже текущей цены
        pip_size = 0.0001
        limit_price = current_bid - (20 * pip_size)

        # Создать ордер BUY LIMIT
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY_LIMIT,
            volume=0.01,
            price=limit_price,
            slippage=0,  # Не используется для отложенных ордеров
            stop_loss=0,
            take_profit=0,
            comment="BUY LIMIT order",
            expert_id=12345
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] BUY LIMIT order placed!")
            print(f"  Order: #{result.order}")
            print(f"  Price: {limit_price:.5f}")
            print(f"  Current: {current_bid:.5f}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(buy_limit_order())
```

### 4) Размещение ордера BUY STOP со сроком действия

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

async def buy_stop_with_expiration():
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

        current_ask = tick_data.tick.ask

        # Разместить BUY STOP на 20 пипсов выше текущей цены
        pip_size = 0.0001
        stop_price = current_ask + (20 * pip_size)

        # Установить срок действия 1 час от текущего момента
        from google.protobuf.timestamp_pb2 import Timestamp
        expiration = datetime.now() + timedelta(hours=1)
        expiration_timestamp = Timestamp()
        expiration_timestamp.FromDatetime(expiration)

        # Создать ордер BUY STOP
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY_STOP,
            volume=0.01,
            price=stop_price,
            slippage=0,
            stop_loss=0,
            take_profit=0,
            comment="BUY STOP 1h expiry",
            expert_id=12345,
            expiration_time_type=trading_pb2.TMT5_ORDER_TIME_SPECIFIED
        )
        request.expiration_time.CopyFrom(expiration_timestamp)

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[SUCCESS] BUY STOP order placed!")
            print(f"  Order: #{result.order}")
            print(f"  Price: {stop_price:.5f}")
            print(f"  Expires: {expiration.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[FAILED] {result.returned_code_description}")

    finally:
        await account.channel.close()

asyncio.run(buy_stop_with_expiration())
```

### 5) Несколько ордеров с обработкой ошибок

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def multiple_orders():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    orders = [
        ("EURUSD", 0.01, "EUR order"),
        ("GBPUSD", 0.01, "GBP order"),
        ("USDJPY", 0.01, "JPY order"),
    ]

    successful = 0
    failed = 0

    try:
        for symbol, volume, comment in orders:
            request = trading_pb2.OrderSendRequest(
                symbol=symbol,
                operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
                volume=volume,
                price=0,
                slippage=20,
                comment=comment,
                expert_id=12345
            )

            try:
                result = await account.order_send(request)

                if result.returned_code == 10009:
                    successful += 1
                    print(f"[OK] {symbol}: Deal #{result.deal} @ {result.price}")
                else:
                    failed += 1
                    print(f"[FAIL] {symbol}: {result.returned_code_description}")

            except Exception as e:
                failed += 1
                print(f"[ERROR] {symbol}: {e}")

        print(f"\n[SUMMARY] Successful: {successful}, Failed: {failed}")

    finally:
        await account.channel.close()

asyncio.run(multiple_orders())
```

### 6) Ордер с логикой повторов

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

async def order_with_retry():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    max_retries = 3
    retry_delay = 1.0  # секунды

    try:
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,
            price=0,
            slippage=20,
            comment="Order with retry",
            expert_id=12345
        )

        for attempt in range(1, max_retries + 1):
            print(f"[ATTEMPT {attempt}/{max_retries}]")

            result = await account.order_send(request)

            if result.returned_code == 10009:
                print(f"[SUCCESS] Order executed on attempt {attempt}!")
                print(f"  Deal: #{result.deal}")
                print(f"  Price: {result.price}")
                break
            else:
                print(f"[FAILED] Code: {result.returned_code}")
                print(f"  Description: {result.returned_code_description}")

                if attempt < max_retries:
                    print(f"  Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"  Max retries reached. Giving up.")

    finally:
        await account.channel.close()

asyncio.run(order_with_retry())
```

---

## 📚 См. также

* [OrderCheck](./order_check.md) - Проверка ордера перед отправкой
* [OrderModify](./order_modify.md) - Изменение существующих ордеров
* [OrderClose](./order_close.md) - Закрытие позиций
* [OrderCalcMargin](./order_calc_margin.md) - Расчёт необходимой маржи
* [OrderCalcProfit](./order_calc_profit.md) - Расчёт потенциальной прибыли/убытка
