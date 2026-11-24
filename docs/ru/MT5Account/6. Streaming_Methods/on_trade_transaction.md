# Стриминг событий торговых транзакций

> **Запрос:** подписаться на события торговых транзакций в реальном времени (подробный аудиторский след).

**Информация об API:**

* **Python API:** `MT5Account.on_trade_transaction(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.SubscriptionService`
* **Proto-определение:** `OnTradeTransaction` (определено в `mt5-term-api-subscriptions.proto`)

### RPC

* **Сервис:** `mt5_term_api.SubscriptionService`
* **Метод:** `OnTradeTransaction(OnTradeTransactionRequest) -> stream OnTradeTransactionReply`
* **Низкоуровневый клиент (сгенерированный):** `SubscriptionServiceStub.OnTradeTransaction(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_trade_transaction(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time trade transaction events.

        Yields:
            OnTradeTransactionData: Trade transaction data.
        """
```

**Сообщение запроса:**

```protobuf
message OnTradeTransactionRequest {
  // Без параметров - подписка на все торговые транзакции
}
```

## 💬 Только суть

* **Что это.** Поток подробных событий торговых транзакций в реальном времени (самый всеобъемлющий).
* **Зачем это нужно.** Полный аудиторский след, подробное логирование транзакций, верификация сделок.
* **Событийно-ориентированный.** Обновления срабатывают немедленно при каждом событии транзакции.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Строить полные аудиторские журналы сделок
* Отслеживать подробный жизненный цикл транзакций
* Детально контролировать изменения состояния ордеров
* Верифицировать исполнение сделок
* Отлаживать торговые операции
* Реализовывать логику на основе транзакций
* Создавать подробные торговые журналы

---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены стриминга (опционально)    |

---

## ⬆️ Выход - Асинхронный генератор

Возвращает асинхронный генератор, который выдаёт объекты `OnTradeTransactionData`.

**Поля OnTradeTransactionData:**

| Поле                          | Тип                       | Описание                             |
| ----------------------------- | ------------------------- | ------------------------------------ |
| `type`                        | `int`                     | Тип транзакции                       |
| `trade_transaction`           | `MqlTradeTransaction`     | Подробная информация о транзакции    |
| `trade_request`               | `MqlTradeRequest`         | Исходный торговый запрос             |
| `trade_result`                | `MqlTradeResult`          | Результат исполнения сделки          |
| `account_info`                | `OnEventAccountInfo`      | Текущее состояние счёта              |
| `terminal_instance_guid_id`   | `str`                     | Идентификатор экземпляра терминала   |

**Enum типа ордера (SUB_ENUM_ORDER_TYPE):**

| Имя                               | Значение | Описание                             |
| --------------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_TYPE_BUY`              | 0     | Рыночный ордер на покупку            |
| `SUB_ORDER_TYPE_SELL`             | 1     | Рыночный ордер на продажу            |
| `SUB_ORDER_TYPE_BUY_LIMIT`        | 2     | Отложенный ордер buy limit           |
| `SUB_ORDER_TYPE_SELL_LIMIT`       | 3     | Отложенный ордер sell limit          |
| `SUB_ORDER_TYPE_BUY_STOP`         | 4     | Отложенный ордер buy stop            |
| `SUB_ORDER_TYPE_SELL_STOP`        | 5     | Отложенный ордер sell stop           |
| `SUB_ORDER_TYPE_BUY_STOP_LIMIT`   | 6     | Отложенный ордер buy stop limit      |
| `SUB_ORDER_TYPE_SELL_STOP_LIMIT`  | 7     | Отложенный ордер sell stop limit     |
| `SUB_ORDER_TYPE_CLOSE_BY`         | 8     | Закрытие встречной позицией          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_TYPE_BUY   # = 0
```

**Enum состояния ордера (SUB_ENUM_ORDER_STATE):**

| Имя                               | Значение | Описание                             |
| --------------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_STATE_STARTED`         | 0     | Ордер проверен, но ещё не принят     |
| `SUB_ORDER_STATE_PLACED`          | 1     | Ордер принят                         |
| `SUB_ORDER_STATE_CANCELED`        | 2     | Ордер отменён клиентом               |
| `SUB_ORDER_STATE_PARTIAL`         | 3     | Ордер исполнен частично              |
| `SUB_ORDER_STATE_FILLED`          | 4     | Ордер исполнен полностью             |
| `SUB_ORDER_STATE_REJECTED`        | 5     | Ордер отклонён                       |
| `SUB_ORDER_STATE_EXPIRED`         | 6     | Срок ордера истёк                    |
| `SUB_ORDER_STATE_REQUEST_ADD`     | 7     | Ордер регистрируется                 |
| `SUB_ORDER_STATE_REQUEST_MODIFY`  | 8     | Ордер модифицируется                 |
| `SUB_ORDER_STATE_REQUEST_CANCEL`  | 9     | Ордер удаляется                      |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_STATE_FILLED   # = 4
```

**Enum типа сделки (SUB_ENUM_DEAL_TYPE):**

| Имя                                       | Значение | Описание                             |
| ----------------------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_TYPE_BUY`                       | 0     | Сделка на покупку                    |
| `SUB_DEAL_TYPE_SELL`                      | 1     | Сделка на продажу                    |
| `SUB_DEAL_TYPE_BALANCE`                   | 2     | Балансовая операция                  |
| `SUB_DEAL_TYPE_CREDIT`                    | 3     | Кредитная операция                   |
| `SUB_DEAL_TYPE_CHARGE`                    | 4     | Дополнительное списание              |
| `SUB_DEAL_TYPE_CORRECTION`                | 5     | Коррекция                            |
| `SUB_DEAL_TYPE_BONUS`                     | 6     | Бонус                                |
| `SUB_DEAL_TYPE_COMMISSION`                | 7     | Комиссия                             |
| `SUB_DEAL_TYPE_COMMISSION_DAILY`          | 8     | Ежедневная комиссия                  |
| `SUB_DEAL_TYPE_COMMISSION_MONTHLY`        | 9     | Ежемесячная комиссия                 |
| `SUB_DEAL_TYPE_COMMISSION_AGENT_DAILY`    | 10    | Ежедневная агентская комиссия        |
| `SUB_DEAL_TYPE_COMMISSION_AGENT_MONTHLY`  | 11    | Ежемесячная агентская комиссия       |
| `SUB_DEAL_TYPE_INTEREST`                  | 12    | Процентная ставка                    |
| `SUB_DEAL_TYPE_BUY_CANCELED`              | 13    | Отменённая сделка на покупку         |
| `SUB_DEAL_TYPE_SELL_CANCELED`             | 14    | Отменённая сделка на продажу         |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_TYPE_BUY   # = 0
```

**Enum входа сделки (SUB_ENUM_DEAL_ENTRY):**

| Имя                        | Значение | Описание                             |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_ENTRY_IN`        | 0     | Вход в позицию                       |
| `SUB_DEAL_ENTRY_OUT`       | 1     | Выход из позиции                     |
| `SUB_DEAL_ENTRY_INOUT`     | 2     | Разворот позиции                     |
| `SUB_DEAL_ENTRY_OUT_BY`    | 3     | Закрытие встречной позицией          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_ENTRY_IN   # = 0
```

**Enum причины сделки (SUB_ENUM_DEAL_REASON):**

| Имя                                   | Значение | Описание                             |
| ------------------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_REASON_CLIENT`              | 0     | Сделка размещена из десктопного терминала |
| `SUB_DEAL_REASON_MOBILE`              | 1     | Сделка размещена из мобильного приложения |
| `SUB_DEAL_REASON_WEB`                 | 2     | Сделка размещена из веб-терминала    |
| `SUB_DEAL_REASON_EXPERT`              | 3     | Сделка размещена советником (Expert Advisor) |
| `SUB_DEAL_REASON_SL`                  | 4     | Сделка из-за срабатывания стоп-лосса  |
| `SUB_DEAL_REASON_TP`                  | 5     | Сделка из-за срабатывания тейк-профита |
| `SUB_DEAL_REASON_SO`                  | 6     | Сделка из-за Stop Out                |
| `SUB_DEAL_REASON_ROLLOVER`            | 7     | Сделка из-за ролловера               |
| `SUB_DEAL_REASON_VMARGIN`             | 8     | Сделка из-за вариационной маржи      |
| `SUB_DEAL_REASON_SPLIT`               | 9     | Сделка из-за сплита                  |
| `SUB_DEAL_REASON_CORPORATE_ACTION`    | 10    | Сделка из-за корпоративного действия |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_REASON_CLIENT   # = 0
```

**Enum времени действия ордера (SUB_ENUM_ORDER_TYPE_TIME):**

| Имя                            | Значение | Описание                             |
| ------------------------------ | ----- | ------------------------------------ |
| `SUB_ORDER_TIME_GTC`           | 0     | Действителен до отмены               |
| `SUB_ORDER_TIME_DAY`           | 1     | Действителен до конца текущего торгового дня |
| `SUB_ORDER_TIME_SPECIFIED`     | 2     | Действителен до указанной даты       |
| `SUB_ORDER_TIME_SPECIFIED_DAY` | 3     | Действителен до указанного дня       |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_TIME_GTC   # = 0
```

**Enum типа исполнения ордера (SUB_ENUM_ORDER_TYPE_FILLING):**

| Имя                          | Значение | Описание                             |
| ---------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_FILLING_FOK`      | 0     | Fill or Kill                         |
| `SUB_ORDER_FILLING_IOC`      | 1     | Immediate or Cancel                  |
| `SUB_ORDER_FILLING_BOC`      | 2     | Book or Cancel                       |
| `SUB_ORDER_FILLING_RETURN`   | 3     | Return                               |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_FILLING_FOK   # = 0
```

**Enum причины ордера (SUB_ENUM_ORDER_REASON):**

| Имя                          | Значение | Описание                             |
| ---------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_REASON_CLIENT`    | 0     | Ордер размещён из десктопного терминала |
| `SUB_ORDER_REASON_MOBILE`    | 2     | Ордер размещён из мобильного приложения |
| `SUB_ORDER_REASON_WEB`       | 3     | Ордер размещён из веб-терминала      |
| `SUB_ORDER_REASON_EXPERT`    | 4     | Ордер размещён советником (Expert Advisor) |
| `SUB_ORDER_REASON_SL`        | 5     | Ордер сработал по стоп-лоссу         |
| `SUB_ORDER_REASON_TP`        | 6     | Ордер сработал по тейк-профиту       |
| `SUB_ORDER_REASON_SO`        | 7     | Ордер сработал по Stop Out           |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_REASON_CLIENT   # = 0
```

**Enum типа позиции (SUB_ENUM_POSITION_TYPE):**

| Имя                        | Значение | Описание                             |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_POSITION_TYPE_BUY`    | 0     | Позиция на покупку                   |
| `SUB_POSITION_TYPE_SELL`   | 1     | Позиция на продажу                   |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
```

**Enum причины позиции (SUB_ENUM_POSITION_REASON):**

| Имя                            | Значение | Описание                             |
| ------------------------------ | ----- | ------------------------------------ |
| `SUB_POSITION_REASON_CLIENT`   | 0     | Позиция из десктопного терминала     |
| `SUB_POSITION_REASON_MOBILE`   | 2     | Позиция из мобильного приложения     |
| `SUB_POSITION_REASON_WEB`      | 3     | Позиция из веб-терминала             |
| `SUB_POSITION_REASON_EXPERT`   | 4     | Позиция от советника (Expert Advisor)|

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_REASON_CLIENT   # = 0
```

---

**Поля MqlTradeTransaction (частичный список):**

| Поле                       | Тип      | Описание                                 |
| -------------------------- | -------- | ---------------------------------------- |
| `deal_ticket`              | `uint64` | Номер тикета сделки                      |
| `order_ticket`             | `uint64` | Номер тикета ордера                      |
| `symbol`                   | `string` | Торговый символ                          |
| `type`                     | `enum`   | Тип транзакции                           |
| `order_type`               | `enum`   | Тип ордера (market, limit, stop и т. д.) |
| `order_state`              | `enum`   | Состояние ордера (started, placed и т. д.) |
| `deal_type`                | `enum`   | Тип сделки (buy, sell)                   |
| `order_time_type`          | `enum`   | Тип времени действия ордера (GTC, DAY и т. д.) |
| `price`                    | `double` | Цена                                     |
| `price_stop_loss`          | `double` | Цена стоп-лосса                          |
| `price_take_profit`        | `double` | Цена тейк-профита                        |
| `volume`                   | `double` | Объём                                    |
| `position_ticket`          | `uint64` | Тикет позиции                            |

**Поля MqlTradeRequest:**

| Поле          | Тип      | Описание                                 |
| ------------- | -------- | ---------------------------------------- |
| `action`      | `enum`   | Тип торговой операции                    |
| `magic`       | `uint64` | ID советника (Expert Advisor)            |
| `order`       | `uint64` | Тикет ордера                             |
| `symbol`      | `string` | Торговый символ                          |
| `volume`      | `double` | Запрошенный объём                        |
| `price`       | `double` | Цена                                     |

**Поля MqlTradeResult:**

| Поле                           | Тип      | Описание                                 |
| ------------------------------ | -------- | ---------------------------------------- |
| `trade_return_int_code`        | `int32`  | Внутренний код возврата                  |
| `trade_return_code`            | `uint32` | Код возврата операции                    |
| `deal_ticket`                  | `uint64` | Тикет сделки                             |
| `order_ticket`                 | `uint64` | Тикет ордера                             |
| `deal_volume`                  | `double` | Объём сделки                             |
| `deal_price`                   | `double` | Цена сделки                              |
| `current_bid`                  | `double` | Текущая цена Bid                         |
| `current_ask`                  | `double` | Текущая цена Ask                         |
| `broker_comment_to_operation`  | `string` | Комментарий брокера                      |
| `terminal_dispatch_request_id` | `uint32` | ID запроса терминала                     |
| `return_code_external`         | `int32`  | Внешний код возврата (брокера)           |

---


## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OnTradeTransaction - Как это работает](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы стриминга `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_stream_with_reconnect`.
* **Асинхронный генератор:** Метод возвращает асинхронный генератор - используйте `async for` для получения данных.
* **Самый подробный:** Это самый всеобъемлющий поток транзакций - включает полные данные запроса/результата.
* **Без параметров:** Подписывается на ВСЕ торговые транзакции автоматически.
* **Событийно-ориентированный:** Обновления приходят немедленно при возникновении транзакций (не периодически).
* **Полный жизненный цикл:** Отслеживает размещение, модификацию, исполнение и отмену ордеров.
* **Включает неудачи:** Получает события как для успешных, так и для неудачных транзакций.
* **Ресурсоёмкий:** Самый подробный поток - используйте `on_trade`, если вам не нужен такой уровень детализации.

---

## 🔗 Примеры использования

### 1) Базовый монитор транзакций

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_transactions():
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
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            print(f"\n[TRANSACTION EVENT]")
            print(f"   Type: {tx.type}")
            print(f"   Symbol: {tx.symbol}")
            print(f"   Order: #{tx.order_ticket}")
            print(f"   Deal: #{tx.deal_ticket}")
            print(f"   Position: #{tx.position_ticket}")
            print(f"   Price: {tx.price}")
            print(f"   Volume: {tx.volume}")
            print(f"   Order state: {tx.order_state}")

            # Показываем запрос, если доступен
            if tx_data.trade_request and tx_data.trade_request.symbol:
                req = tx_data.trade_request
                print(f"\n   Request:")
                print(f"     Symbol: {req.symbol}")
                print(f"     Volume: {req.volume}")
                print(f"     Price: {req.price}")

            # Показываем результат, если доступен
            if tx_data.trade_result and tx_data.trade_result.trade_return_code != 0:
                res = tx_data.trade_result
                print(f"\n   Result:")
                print(f"     Return code: {res.trade_return_code}")
                print(f"     Comment: {res.broker_comment_to_operation}")

    except KeyboardInterrupt:
        print("\nStopping transaction monitor...")

    finally:
        await account.channel.close()

asyncio.run(monitor_transactions())
```

### 2) Полный аудиторский журнал транзакций

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def audit_log():
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
        with open('trade_audit.log', 'w') as logfile:
            logfile.write("Timestamp,Type,Symbol,Order,Deal,Position,Price,Volume,State\n")

            async for tx_data in account.on_trade_transaction():
                tx = tx_data.trade_transaction
                timestamp = datetime.now().isoformat()

                # Записываем в аудиторский журнал
                logfile.write(
                    f"{timestamp},"
                    f"{tx.type},"
                    f"{tx.symbol},"
                    f"{tx.order_ticket},"
                    f"{tx.deal_ticket},"
                    f"{tx.position_ticket},"
                    f"{tx.price},"
                    f"{tx.volume},"
                    f"{tx.order_state}\n"
                )
                logfile.flush()

                print(f"[{timestamp}] Logged transaction: "
                      f"Order #{tx.order_ticket}, Deal #{tx.deal_ticket}")

    except KeyboardInterrupt:
        print("\nStopping audit log...")

    finally:
        await account.channel.close()

asyncio.run(audit_log())
```

### 3) Трекер жизненного цикла ордера

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def track_order_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    order_states = {}  # тикет ордера -> список состояний

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            if tx.order_ticket > 0:
                # Отслеживаем изменения состояния ордера
                if tx.order_ticket not in order_states:
                    order_states[tx.order_ticket] = []

                order_states[tx.order_ticket].append({
                    'state': tx.order_state,
                    'type': tx.type,
                    'price': tx.price,
                    'volume': tx.volume
                })

                print(f"\n[LIFECYCLE] Order #{tx.order_ticket}:")
                for i, state in enumerate(order_states[tx.order_ticket], 1):
                    print(f"   {i}. State: {state['state']}, "
                          f"Type: {state['type']}, "
                          f"Price: {state['price']}")

    except KeyboardInterrupt:
        print("\nStopping lifecycle tracker...")
        print(f"\nTracked {len(order_states)} orders")

    finally:
        await account.channel.close()

asyncio.run(track_order_lifecycle())
```

### 4) Монитор неудачных транзакций

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_failed_transactions():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    failed_count = 0

    try:
        async for tx_data in account.on_trade_transaction():
            # Проверяем на неудачные транзакции
            if tx_data.trade_result and tx_data.trade_result.trade_return_code != 10009:  # Не DONE
                failed_count += 1
                res = tx_data.trade_result
                tx = tx_data.trade_transaction

                print(f"\n[FAILED TRANSACTION #{failed_count}]")
                print(f"   Return code: {res.trade_return_code}")
                print(f"   Comment: {res.broker_comment_to_operation}")
                print(f"   Symbol: {tx.symbol}")
                print(f"   Order: #{tx.order_ticket}")
                print(f"   Requested volume: {tx.volume}")
                print(f"   Price: {tx.price}")

                if tx_data.trade_request:
                    req = tx_data.trade_request
                    print(f"\n   Original request:")
                    print(f"     Action: {req.action}")
                    print(f"     Symbol: {req.symbol}")
                    print(f"     Volume: {req.volume}")

    except KeyboardInterrupt:
        print(f"\n\nStopping monitor. Total failed: {failed_count}")

    finally:
        await account.channel.close()

asyncio.run(monitor_failed_transactions())
```

### 5) Сборщик статистики транзакций

```python
import asyncio
from collections import defaultdict
from MetaRpcMT5 import MT5Account

async def collect_transaction_stats(duration_seconds=300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    stats = {
        'total_transactions': 0,
        'by_type': defaultdict(int),
        'by_state': defaultdict(int),
        'by_symbol': defaultdict(int),
        'successful': 0,
        'failed': 0,
    }

    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for tx_data in account.on_trade_transaction(
            cancellation_event=cancel_event
        ):
            tx = tx_data.trade_transaction
            stats['total_transactions'] += 1
            stats['by_type'][tx.type] += 1
            stats['by_state'][tx.order_state] += 1

            if tx.symbol:
                stats['by_symbol'][tx.symbol] += 1

            # Проверяем успех/неудачу
            if tx_data.trade_result:
                if tx_data.trade_result.trade_return_code == 10009:  # DONE
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1

        await stop_task

        # Печатаем статистику
        print("\n" + "=" * 70)
        print("TRANSACTION STATISTICS REPORT")
        print("=" * 70)
        print(f"Total transactions:  {stats['total_transactions']:>6,}")
        print(f"Successful:          {stats['successful']:>6,}")
        print(f"Failed:              {stats['failed']:>6,}")

        print("\nBy Type:")
        for tx_type, count in sorted(stats['by_type'].items()):
            print(f"  Type {tx_type}: {count:>6,}")

        print("\nBy State:")
        for state, count in sorted(stats['by_state'].items()):
            print(f"  State {state}: {count:>6,}")

        print("\nBy Symbol:")
        for symbol, count in sorted(stats['by_symbol'].items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {symbol}: {count:>6,}")

        print("=" * 70)

    finally:
        await account.channel.close()

# Собираем статистику в течение 5 минут
asyncio.run(collect_transaction_stats(300))
```

### 6) Торговый журнал в реальном времени

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def trade_journal():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    journal_entries = []

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            # Создаём запись журнала
            entry = {
                'timestamp': datetime.now(),
                'type': tx.type,
                'symbol': tx.symbol,
                'order_ticket': tx.order_ticket,
                'deal_ticket': tx.deal_ticket,
                'position_ticket': tx.position_ticket,
                'price': tx.price,
                'volume': tx.volume,
                'order_state': tx.order_state,
                'sl': tx.price_stop_loss,
                'tp': tx.price_take_profit,
            }

            # Добавляем информацию о результате, если доступна
            if tx_data.trade_result:
                entry['retcode'] = tx_data.trade_result.trade_return_code
                entry['comment'] = tx_data.trade_result.broker_comment_to_operation

            # Добавляем баланс счёта
            if tx_data.account_info:
                entry['balance'] = tx_data.account_info.balance
                entry['equity'] = tx_data.account_info.equity

            journal_entries.append(entry)

            # Отображаем запись
            print(f"\n{'=' * 70}")
            print(f"JOURNAL ENTRY #{len(journal_entries)}")
            print(f"{'=' * 70}")
            print(f"Time:       {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Symbol:     {entry['symbol']}")
            print(f"Type:       {entry['type']}")
            print(f"Order:      #{entry['order_ticket']}")
            print(f"Deal:       #{entry['deal_ticket']}")
            print(f"Position:   #{entry['position_ticket']}")
            print(f"Price:      {entry['price']}")
            print(f"Volume:     {entry['volume']}")
            print(f"SL:         {entry['sl']}")
            print(f"TP:         {entry['tp']}")
            print(f"State:      {entry['order_state']}")

            if 'balance' in entry:
                print(f"Balance:    ${entry['balance']:.2f}")
                print(f"Equity:     ${entry['equity']:.2f}")

            # Периодически сохраняем журнал
            if len(journal_entries) % 10 == 0:
                print(f"\n[SAVED] {len(journal_entries)} entries to journal")

    except KeyboardInterrupt:
        print(f"\n\nStopping journal. Total entries: {len(journal_entries)}")

        # Экспортируем журнал
        with open('trade_journal.txt', 'w') as f:
            f.write("TRADE JOURNAL\n")
            f.write("=" * 70 + "\n\n")
            for i, entry in enumerate(journal_entries, 1):
                f.write(f"Entry #{i}\n")
                f.write(f"  Time: {entry['timestamp']}\n")
                f.write(f"  Symbol: {entry['symbol']}\n")
                f.write(f"  Order: #{entry['order_ticket']}\n")
                f.write(f"  Price: {entry['price']}\n")
                f.write("\n")

        print(f"Journal exported to trade_journal.txt")

    finally:
        await account.channel.close()

asyncio.run(trade_journal())
```

---

## 📚 См. также

* [OnTrade](./on_trade.md) - Более простой поток торговых событий (менее подробный)
* [OrderSend](../5.%20Trading_Operations/order_send.md) - Отправить торговые ордера
* [OrderCheck](../5.%20Trading_Operations/order_check.md) - Проверить ордер перед отправкой
* [OrderHistory](../3.%20Positions_Orders/order_history.md) - Получить исторические ордера
