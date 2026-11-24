# Стриминг торговых событий

> **Запрос:** подписаться на все события, связанные с торговлей: ордера, сделки, позиции.

**Информация об API:**

* **Python API:** `MT5Account.on_trade(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.SubscriptionService`
* **Proto-определение:** `OnTrade` (определено в `mt5-term-api-subscriptions.proto`)

### RPC

* **Сервис:** `mt5_term_api.SubscriptionService`
* **Метод:** `OnTrade(OnTradeRequest) -> stream OnTradeReply`
* **Низкоуровневый клиент (сгенерированный):** `SubscriptionServiceStub.OnTrade(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_trade(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to all trade-related events: orders, deals, positions.

        Yields:
            OnTradeData: Trade event data.
        """
```

**Сообщение запроса:**

```protobuf
message OnTradeRequest {
  // Без параметров - подписка на все торговые события
}
```

## 💬 Только суть

* **Что это.** Поток всей торговой активности на счёте в реальном времени.
* **Зачем это нужно.** Мониторинг сделок, обнаружение изменений позиций, отслеживание исполнения ордеров.
* **Событийно-ориентированный.** Обновления срабатывают немедленно при возникновении торговых событий.

---

## 🎯 Назначение

Используйте для того, чтобы:

* Отслеживать всю торговую активность в реальном времени
* Обнаруживать открытие или закрытие позиций
* Отслеживать жизненный цикл отложенных ордеров
* Строить системы логирования торговых событий
* Реализовывать уведомления о сделках
* Синхронизировать локальное состояние с MT5


---

## 🔽 Вход

| Параметр             | Тип                            | Описание                                      |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `cancellation_event` | `Optional[asyncio.Event]`      | Событие для отмены стриминга (опционально)    |

---

## ⬆️ Выход - Асинхронный генератор

Возвращает асинхронный генератор, который выдаёт объекты `OnTradeData`.

**Поля OnTradeData:**

| Поле                          | Тип                       | Описание                             |
| ----------------------------- | ------------------------- | ------------------------------------ |
| `type`                        | `int`                     | Тип события                          |
| `event_data`                  | `OnTradeEventData`        | Подробная информация о событии       |
| `account_info`                | `OnEventAccountInfo`      | Текущее состояние счёта              |
| `terminal_instance_guid_id`   | `str`                     | Идентификатор экземпляра терминала   |

**Поля OnTradeEventData (все repeated/списки):**

| Поле                          | Тип                               | Описание                             |
| ----------------------------- | --------------------------------- | ------------------------------------ |
| `new_orders`                  | `repeated OnTradeOrderInfo`       | Созданные новые отложенные ордера    |
| `disappeared_orders`          | `repeated OnTradeOrderInfo`       | Удалённые отложенные ордера          |
| `state_changed_orders`        | `repeated OnTradeOrderStateChange`| Ордера с изменениями состояния       |
| `new_positions`               | `repeated OnTradePositionInfo`    | Открытые новые позиции               |
| `disappeared_positions`       | `repeated OnTradePositionInfo`    | Закрытые позиции                     |
| `updated_positions`           | `repeated OnTradePositionUpdate`  | Изменённые позиции                   |
| `new_history_orders`          | `repeated OnTradeHistoryOrderInfo`| Новые исторические ордера            |
| `disappeared_history_orders`  | `repeated OnTradeHistoryOrderInfo`| Удалённые исторические ордера        |
| `updated_history_orders`      | `repeated OnTradeHistoryOrderUpdate`| Обновлённые исторические ордера    |
| `new_history_deals`           | `repeated OnTradeHistoryDealInfo` | Новые сделки в истории               |
| `disappeared_history_deals`   | `repeated OnTradeHistoryDealInfo` | Удалённые из истории сделки          |
| `updated_history_deals`       | `repeated OnTradeHistoryDealUpdate`| Обновлённые в истории сделки        |

**Структура и использование ENUM:**

```
OnTradeData
├── type (MT5_SUB_ENUM_EVENT_GROUP_TYPE) - Event group type
├── event_data (OnTradeEventData)
│   ├── new_positions (list[OnTradePositionInfo])
│   │   └── Uses: SUB_ENUM_POSITION_TYPE, SUB_ENUM_POSITION_REASON
│   ├── disappeared_positions (list[OnTradePositionInfo])
│   │   └── Uses: SUB_ENUM_POSITION_TYPE, SUB_ENUM_POSITION_REASON
│   ├── new_orders (list[OnTradeOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_ORDER_REASON
│   ├── disappeared_orders (list[OnTradeOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_ORDER_REASON
│   ├── new_history_orders (list[OnTradeHistoryOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_DEAL_REASON
│   ├── disappeared_history_orders (list[OnTradeHistoryOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_DEAL_REASON
│   ├── new_history_deals (list[OnTradeHistoryDealInfo])
│   │   └── Uses: SUB_ENUM_DEAL_TYPE, SUB_ENUM_DEAL_ENTRY, SUB_ENUM_DEAL_REASON
│   └── disappeared_history_deals (list[OnTradeHistoryDealInfo])
│       └── Uses: SUB_ENUM_DEAL_TYPE, SUB_ENUM_DEAL_ENTRY, SUB_ENUM_DEAL_REASON
├── account_info (OnEventAccountInfo)
└── terminal_instance_guid_id (str)
```

---

**Enum типа группы событий (MT5_SUB_ENUM_EVENT_GROUP_TYPE):**

Используется в поле `OnTradeData.type`:

| Имя            | Значение | Описание                             |
| -------------- | ----- | ------------------------------------ |
| `OrderProfit`  | 0     | Событие прибыли ордера               |
| `OrderUpdate`  | 1     | Событие обновления ордера            |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.OrderProfit   # = 0
```

---

**Enum, используемые во вложенных структурах:**

Следующие enum используются вложенными типами сообщений внутри `OnTradeEventData`:

| Вложенная структура           | Используется в полях                              | Используемые enum                                                                                              |
| ----------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `OnTradePositionInfo`         | `new_positions`, `disappeared_positions`          | `SUB_ENUM_POSITION_TYPE`, `SUB_ENUM_POSITION_REASON`                                                           |
| `OnTradeOrderInfo`            | `new_orders`, `disappeared_orders`                | `SUB_ENUM_ORDER_TYPE`, `SUB_ENUM_ORDER_STATE`, `SUB_ENUM_ORDER_TYPE_TIME`, `SUB_ENUM_ORDER_TYPE_FILLING`, `SUB_ENUM_ORDER_REASON` |
| `OnTradeHistoryOrderInfo`     | `new_history_orders`, `disappeared_history_orders`| `SUB_ENUM_ORDER_TYPE`, `SUB_ENUM_ORDER_STATE`, `SUB_ENUM_ORDER_TYPE_TIME`, `SUB_ENUM_ORDER_TYPE_FILLING`, `SUB_ENUM_DEAL_REASON`  |
| `OnTradeHistoryDealInfo`      | `new_history_deals`, `disappeared_history_deals`  | `SUB_ENUM_DEAL_TYPE`, `SUB_ENUM_DEAL_ENTRY`, `SUB_ENUM_DEAL_REASON`                                            |

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
| `SUB_POSITION_REASON_CLIENT`   | 0     | Позиция открыта из десктопного терминала|
| `SUB_POSITION_REASON_MOBILE`   | 1     | Позиция открыта из мобильного приложения |
| `SUB_POSITION_REASON_WEB`      | 2     | Позиция открыта из веб-терминала     |
| `SUB_POSITION_REASON_EXPERT`   | 3     | Позиция открыта советником (Expert Advisor) |
| `SUB_POSITION_REASON_SL`       | 4     | Позиция закрыта по стоп-лоссу        |
| `SUB_POSITION_REASON_TP`       | 5     | Позиция закрыта по тейк-профиту      |
| `SUB_POSITION_REASON_SO`       | 6     | Позиция закрыта по Stop Out          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_REASON_CLIENT  # = 0
```

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
subscriptions_pb2.SUB_ORDER_STATE_STARTED   # = 0
```

**Enum типа сделки (SUB_ENUM_DEAL_TYPE):**

| Имя                                   | Значение | Описание                             |
| ------------------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_TYPE_BUY`                   | 0     | Сделка на покупку                    |
| `SUB_DEAL_TYPE_SELL`                  | 1     | Сделка на продажу                    |
| `SUB_DEAL_TYPE_BALANCE`               | 2     | Балансовая операция                  |
| `SUB_DEAL_TYPE_CREDIT`                | 3     | Кредитная операция                   |
| `SUB_DEAL_TYPE_CHARGE`                | 4     | Дополнительное списание              |
| `SUB_DEAL_TYPE_CORRECTION`            | 5     | Коррекция                            |
| `SUB_DEAL_TYPE_BONUS`                 | 6     | Бонус                                |
| `SUB_DEAL_TYPE_COMMISSION`            | 7     | Комиссия                             |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_TYPE_BUY   # = 0
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

**Enum типа входа сделки (SUB_ENUM_DEAL_ENTRY):**

| Имя                        | Значение | Описание                             |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_ENTRY_IN`        | 0     | Вход в рынок                         |
| `SUB_DEAL_ENTRY_OUT`       | 1     | Выход из рынка                       |
| `SUB_DEAL_ENTRY_INOUT`     | 2     | Разворот                             |
| `SUB_DEAL_ENTRY_OUT_BY`    | 3     | Закрытие встречной позицией          |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_ENTRY_IN   # = 0
```

**Enum причины сделки (SUB_ENUM_DEAL_REASON):**

| Имя                                  | Значение | Описание                             |
| ------------------------------------ | ----- | ------------------------------------ |
| `SUB_DEAL_REASON_CLIENT`             | 0     | Сделка из десктопного терминала      |
| `SUB_DEAL_REASON_MOBILE`             | 1     | Сделка из мобильного приложения      |
| `SUB_DEAL_REASON_WEB`                | 2     | Сделка из веб-терминала              |
| `SUB_DEAL_REASON_EXPERT`             | 3     | Сделка советником (Expert Advisor)   |
| `SUB_DEAL_REASON_SL`                 | 4     | Сделка по стоп-лоссу                 |
| `SUB_DEAL_REASON_TP`                 | 5     | Сделка по тейк-профиту               |
| `SUB_DEAL_REASON_SO`                 | 6     | Сделка по Stop Out                   |
| `SUB_DEAL_REASON_ROLLOVER`           | 7     | Сделка по ролловеру                  |
| `SUB_DEAL_REASON_VMARGIN`            | 8     | Сделка по вариационной марже         |
| `SUB_DEAL_REASON_SPLIT`              | 9     | Сделка по сплиту                     |
| `SUB_DEAL_REASON_CORPORATE_ACTION`   | 10    | Сделка по корпоративному действию    |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_REASON_CLIENT   # = 0
```

---


## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**[OnTrade - Как это работает](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW.md)**

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы стриминга `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_stream_with_reconnect`.
* **Асинхронный генератор:** Метод возвращает асинхронный генератор - используйте `async for` для получения данных.
* **Без параметров:** Этот поток подписывается на ВСЕ торговые события автоматически.
* **Всеобъемлющий:** Отслеживает ордера, позиции и сделки (как активные, так и исторические).
* **Событийно-ориентированный:** Обновления приходят немедленно при возникновении событий (не периодически).
* **Несколько списков:** Каждое обновление может содержать несколько типов событий одновременно.
* **Управление ресурсами:** Всегда отменяйте потоки по завершении, чтобы освободить ресурсы.

---

## 🔗 Примеры использования

### 1) Мониторинг всех торговых событий

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_trades():
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
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Новые позиции
            if event.new_positions:
                for pos in event.new_positions:
                    print(f"[NEW POSITION] #{pos.index}")

            # Закрытые позиции
            if event.disappeared_positions:
                for pos in event.disappeared_positions:
                    print(f"[CLOSED POSITION] #{pos.index}")

            # Обновлённые позиции
            if event.updated_positions:
                for pos in event.updated_positions:
                    print(f"[UPDATED POSITION] #{pos.index}")

            # Новые отложенные ордера
            if event.new_orders:
                for order in event.new_orders:
                    print(f"[NEW ORDER] #{order.index}")

            # Удалённые отложенные ордера
            if event.disappeared_orders:
                for order in event.disappeared_orders:
                    print(f"[REMOVED ORDER] #{order.index}")

            # Информация о счёте
            if trade_data.account_info:
                acc = trade_data.account_info
                print(f"[ACCOUNT] Balance: ${acc.balance:.2f}, "
                      f"Equity: ${acc.equity:.2f}\n")

    except KeyboardInterrupt:
        print("Stopping trade monitor...")

    finally:
        await account.channel.close()

asyncio.run(monitor_trades())
```

### 2) Логгер торговых событий

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_trade_events():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    event_count = 0

    try:
        async for trade_data in account.on_trade():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event = trade_data.event_data

            # Логируем новые позиции
            for pos in event.new_positions:
                event_count += 1
                print(f"[{timestamp}] NEW_POSITION | Index: {pos.index}")

            # Логируем закрытые позиции
            for pos in event.disappeared_positions:
                event_count += 1
                print(f"[{timestamp}] CLOSED_POSITION | Index: {pos.index}")

            # Логируем обновлённые позиции
            for pos in event.updated_positions:
                event_count += 1
                print(f"[{timestamp}] UPDATED_POSITION | Index: {pos.index}")

            # Логируем новые отложенные ордера
            for order in event.new_orders:
                event_count += 1
                print(f"[{timestamp}] NEW_ORDER | Index: {order.index}")

            # Логируем изменения состояния ордеров
            for order in event.state_changed_orders:
                event_count += 1
                print(f"[{timestamp}] ORDER_STATE_CHANGE | Index: {order.index}")

            # Логируем новые сделки
            for deal in event.new_history_deals:
                event_count += 1
                print(f"[{timestamp}] NEW_DEAL | Index: {deal.index}")

            if event_count % 10 == 0:
                print(f"\n--- Total events logged: {event_count} ---\n")

    except KeyboardInterrupt:
        print(f"\nStopping logger. Total events: {event_count}")

    finally:
        await account.channel.close()

asyncio.run(log_trade_events())
```

### 3) Трекер открытия/закрытия позиций

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def track_position_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    active_positions = set()
    total_opened = 0
    total_closed = 0

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Отслеживаем новые позиции
            for pos in event.new_positions:
                active_positions.add(pos.index)
                total_opened += 1
                print(f"[OPENED] Position #{pos.index}")
                print(f"   Active: {len(active_positions)}, "
                      f"Total opened: {total_opened}")

            # Отслеживаем закрытые позиции
            for pos in event.disappeared_positions:
                if pos.index in active_positions:
                    active_positions.remove(pos.index)
                total_closed += 1
                print(f"[CLOSED] Position #{pos.index}")
                print(f"   Active: {len(active_positions)}, "
                      f"Total closed: {total_closed}")

            # Показываем текущее состояние
            if event.new_positions or event.disappeared_positions:
                print(f"\n[STATS] Current state:")
                print(f"   Active positions: {len(active_positions)}")
                print(f"   Total opened: {total_opened}")
                print(f"   Total closed: {total_closed}")
                print(f"   Win rate: "
                      f"{(total_closed / total_opened * 100) if total_opened > 0 else 0:.1f}%\n")

    except KeyboardInterrupt:
        print("\nStopping tracker...")

    finally:
        await account.channel.close()

asyncio.run(track_position_lifecycle())
```

### 4) Торговые уведомления в реальном времени

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def trade_notifications():
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
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Уведомляем о новых позициях
            if event.new_positions:
                count = len(event.new_positions)
                print(f"\n[NOTIFICATION] {count} new position(s) opened")

                if trade_data.account_info:
                    print(f"   Current balance: ${trade_data.account_info.balance:.2f}")
                    print(f"   Current equity: ${trade_data.account_info.equity:.2f}")

            # Уведомляем о закрытых позициях
            if event.disappeared_positions:
                count = len(event.disappeared_positions)
                print(f"\n[NOTIFICATION] {count} position(s) closed")

                if trade_data.account_info:
                    print(f"   Current balance: ${trade_data.account_info.balance:.2f}")
                    print(f"   Total profit: ${trade_data.account_info.profit:.2f}")

            # Уведомляем об отложенных ордерах
            if event.new_orders:
                count = len(event.new_orders)
                print(f"\n[NOTIFICATION] {count} pending order(s) created")

            # Уведомляем об исполнении ордеров
            if event.disappeared_orders:
                count = len(event.disappeared_orders)
                print(f"\n[NOTIFICATION] {count} pending order(s) executed/cancelled")

    except KeyboardInterrupt:
        print("\nStopping notifications...")

    finally:
        await account.channel.close()

asyncio.run(trade_notifications())
```

### 5) Сборщик торговой статистики

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def collect_trade_statistics(duration_seconds=300):
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
        'positions_opened': 0,
        'positions_closed': 0,
        'positions_modified': 0,
        'orders_created': 0,
        'orders_removed': 0,
        'deals_executed': 0,
    }

    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for trade_data in account.on_trade(
            cancellation_event=cancel_event
        ):
            event = trade_data.event_data

            stats['positions_opened'] += len(event.new_positions)
            stats['positions_closed'] += len(event.disappeared_positions)
            stats['positions_modified'] += len(event.updated_positions)
            stats['orders_created'] += len(event.new_orders)
            stats['orders_removed'] += len(event.disappeared_orders)
            stats['deals_executed'] += len(event.new_history_deals)

        await stop_task

        # Печатаем итоговую статистику
        print("\n" + "=" * 60)
        print("TRADE STATISTICS REPORT")
        print("=" * 60)
        print(f"Positions opened:     {stats['positions_opened']:>6,}")
        print(f"Positions closed:     {stats['positions_closed']:>6,}")
        print(f"Positions modified:   {stats['positions_modified']:>6,}")
        print(f"Orders created:       {stats['orders_created']:>6,}")
        print(f"Orders removed:       {stats['orders_removed']:>6,}")
        print(f"Deals executed:       {stats['deals_executed']:>6,}")
        print("=" * 60)

    finally:
        await account.channel.close()

# Собираем статистику в течение 5 минут
asyncio.run(collect_trade_statistics(300))
```

### 6) Синхронизатор сделок в реальном времени

```python
import asyncio
from MetaRpcMT5 import MT5Account

class TradeSynchronizer:
    def __init__(self):
        self.positions = {}  # индекс -> данные позиции
        self.orders = {}     # индекс -> данные ордера

    async def sync_trades(self, account):
        """Synchronize local state with MT5 account"""
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Синхронизируем позиции
            for pos in event.new_positions:
                self.positions[pos.index] = pos
                print(f"[SYNC] Added position #{pos.index}")

            for pos in event.disappeared_positions:
                if pos.index in self.positions:
                    del self.positions[pos.index]
                    print(f"[SYNC] Removed position #{pos.index}")

            for pos in event.updated_positions:
                if pos.index in self.positions:
                    # Обновляем данные позиции
                    print(f"[SYNC] Updated position #{pos.index}")

            # Синхронизируем ордера
            for order in event.new_orders:
                self.orders[order.index] = order
                print(f"[SYNC] Added order #{order.index}")

            for order in event.disappeared_orders:
                if order.index in self.orders:
                    del self.orders[order.index]
                    print(f"[SYNC] Removed order #{order.index}")

            # Показываем текущее состояние
            print(f"\n[STATE] Local state: {len(self.positions)} positions, "
                  f"{len(self.orders)} orders\n")

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

    synchronizer = TradeSynchronizer()

    try:
        await synchronizer.sync_trades(account)
    except KeyboardInterrupt:
        print("\nStopping synchronizer...")
    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 См. также

* [OnTradeTransaction](./on_trade_transaction.md) - Более подробные события транзакций
* [OnPositionProfit](./on_position_profit.md) - Стриминг обновлений прибыли позиций
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Получить снимок текущих позиций
* [OrderHistory](../3.%20Positions_Orders/order_history.md) - Получить исторические ордера
