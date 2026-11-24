# Получение текущих открытых ордеров и позиций

> **Запрос:** полный снимок всех текущих открытых ордеров и позиций с полными деталями.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.opened_orders(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Определение в proto:** `OpenedOrders` (определено в `mt5-term-api-account-helper.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `OpenedOrders(OpenedOrdersRequest) -> OpenedOrdersReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.OpenedOrders(request, metadata, timeout)`

## 💬 Только самое важное

* **Что это.** Получить исчерпывающие данные обо всех отложенных ордерах и открытых позициях.
* **Зачем это нужно.** Полный обзор текущего торгового состояния с полными деталями ордеров/позиций.
* **Когда использовать.** Используйте для полных данных. Для простого количества используйте `positions_total()`, для только ID тикетов - `opened_orders_tickets()`.

---

## 🎯 Назначение

Используйте для получения подробной информации о текущих ордерах и позициях:

* Получить все отложенные ордера (Buy Limit, Sell Stop и т.д.)
* Получить все открытые позиции (Buy/Sell с P/L)
* Отслеживать текущее торговое состояние
* Реализовать логику управления позициями
* Отображать текущие ордера/позиции в интерфейсе
* Рассчитать совокупную экспозицию

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [opened_orders - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW.md)**

---

## Сигнатура метода

```python
async def opened_orders(
    self,
    sort_mode: account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE = account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OpenedOrdersData
```

**Сообщение запроса:**

```protobuf
message OpenedOrdersRequest {
  BMT5_ENUM_OPENED_ORDER_SORT_TYPE inputSortMode = 1;
}
```

**Сообщение ответа:**

```protobuf
message OpenedOrdersReply {
  oneof response {
    OpenedOrdersData data = 1;
    Error error = 2;
  }
}

message OpenedOrdersData {
  repeated OpenedOrderInfo opened_orders = 1;
  repeated PositionInfo position_infos = 2;
}
```

---

## 🔽 Вход

| Параметр      | Тип                               | Описание                                                |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `sort_mode`   | `BMT5_ENUM_OPENED_ORDER_SORT_TYPE` (enum) | Режим сортировки ордеров (по времени или ID тикета) |
| `deadline`    | `datetime` (опционально)             | Крайний срок для вызова gRPC (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (опционально) | Событие для отмены операции                   |

**Варианты с deadline:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# С режимом сортировки и deadline
deadline = datetime.now(timezone.utc) + timedelta(seconds=5)
data = await account.opened_orders(
    sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline=deadline
)

# Сортировка по умолчанию (по времени открытия по возрастанию)
data = await account.opened_orders()
```

---

## ⬆️ Выход - `OpenedOrdersData`

| Поле              | Тип                         | Тип Python                | Описание                                 |
| ----------------- | --------------------------- | ------------------------- | ---------------------------------------- |
| `opened_orders`   | `repeated OpenedOrderInfo`  | `list[OpenedOrderInfo]`   | Список отложенных ордеров                 |
| `position_infos`  | `repeated PositionInfo`     | `list[PositionInfo]`      | Список открытых позиций                   |

**Возвращаемое значение:** Метод возвращает объект `OpenedOrdersData`, оба списка доступны как атрибуты.

### `OpenedOrderInfo` (элемент `opened_orders`) — отложенный ордер

| Поле                   | Тип                           | Описание                                               |
| ---------------------- | ----------------------------- | ------------------------------------------------------ |
| `index`                | `uint32`                      | Индекс в списке результатов, начиная с нуля            |
| `ticket`               | `uint64`                      | Тикет ордера (уникальный id)                           |
| `price_current`        | `double`                      | Текущая рыночная цена                                  |
| `price_open`           | `double`                      | Запрошенная/открытая цена ордера                       |
| `stop_limit`           | `double`                      | Цена срабатывания стоп-лимита                          |
| `stop_loss`            | `double`                      | Цена стоп-лосса                                        |
| `take_profit`          | `double`                      | Цена тейк-профита                                      |
| `volume_current`       | `double`                      | Оставшийся (неисполненный) объём в лотах               |
| `volume_initial`       | `double`                      | Начальный объём в лотах                                |
| `magic_number`         | `int64`                       | Magic-номер советника (Expert Advisor)                 |
| `reason`               | `int32`                       | Код причины создания ордера                            |
| `type`                 | `BMT5_ENUM_ORDER_TYPE`        | Тип ордера (buy/sell/limit/stop/…)                     |
| `state`                | `BMT5_ENUM_ORDER_STATE`       | Состояние ордера (размещён/исполнен/…)                 |
| `time_expiration`      | `Timestamp`                   | Время истечения (время сервера)                        |
| `time_setup`           | `Timestamp`                   | Время размещения (время сервера)                       |
| `time_done`            | `Timestamp`                   | Время исполнения/отмены (время сервера)                |
| `type_filling`         | `BMT5_ENUM_ORDER_TYPE_FILLING`| Политика исполнения                                    |
| `type_time`            | `BMT5_ENUM_ORDER_TYPE_TIME`   | Политика истечения                                     |
| `position_id`          | `int64`                       | ID позиции, к которой относится этот ордер             |
| `position_by_id`       | `int64`                       | ID встречной позиции (для close-by)                    |
| `symbol`               | `string`                      | Торговый символ                                        |
| `external_id`          | `string`                      | Внешний id на стороне брокера                          |
| `comment`              | `string`                      | Комментарий ордера                                     |
| `account_login`        | `int64`                       | Логин счёта (владелец)                                 |
| `time_expiration_utc`  | `Timestamp`                   | Время истечения (UTC)                                  |
| `time_setup_utc`       | `Timestamp`                   | Время размещения (UTC)                                 |
| `time_done_utc`        | `Timestamp`                   | Время исполнения/отмены (UTC)                          |

### `PositionInfo` (элемент `position_infos`) — открытая позиция

| Поле                    | Тип                         | Описание                                    |
| ----------------------- | --------------------------- | ------------------------------------------- |
| `index`                 | `uint32`                    | Индекс в списке результатов, начиная с нуля |
| `ticket`                | `uint64`                    | Тикет позиции (уникальный id)               |
| `open_time`             | `Timestamp`                 | Время открытия позиции (время сервера)      |
| `volume`                | `double`                    | Объём позиции в лотах                       |
| `price_open`            | `double`                    | Цена открытия                               |
| `stop_loss`             | `double`                    | Цена стоп-лосса                             |
| `take_profit`           | `double`                    | Цена тейк-профита                           |
| `price_current`         | `double`                    | Текущая рыночная цена                       |
| `swap`                  | `double`                    | Накопленный своп                            |
| `profit`                | `double`                    | Текущая плавающая прибыль/убыток            |
| `last_update_time`      | `Timestamp`                 | Время последнего обновления (время сервера) |
| `type`                  | `BMT5_ENUM_POSITION_TYPE`   | Тип позиции (buy/sell)                      |
| `magic_number`          | `int64`                     | Magic-номер советника (Expert Advisor)      |
| `identifier`            | `int64`                     | Идентификатор позиции                       |
| `reason`                | `BMT5_ENUM_POSITION_REASON` | Причина открытия позиции                    |
| `symbol`                | `string`                    | Торговый символ                             |
| `comment`               | `string`                    | Комментарий позиции                         |
| `external_id`           | `string`                    | Внешний id на стороне брокера               |
| `position_commission`   | `double`                    | Комиссия по позиции                         |
| `account_login`         | `int64`                     | Логин счёта (владелец)                      |
| `open_time_utc`         | `Timestamp`                 | Время открытия позиции (UTC)                |
| `last_update_time_utc`  | `Timestamp`                 | Время последнего обновления (UTC)           |

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В коде Python вы можете использовать enum из модуля account_helper_pb2. Этот метод использует **7 enum** с **40 константами** в сумме.

### `BMT5_ENUM_OPENED_ORDER_SORT_TYPE`

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC` | 0 | Сортировка по времени открытия (сначала старые) |
| `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_DESC` | 1 | Сортировка по времени открытия (сначала новые) |
| `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_ASC` | 2 | Сортировка по ID тикета (по возрастанию) |
| `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_DESC` | 3 | Сортировка по ID тикета (по убыванию) |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.opened_orders(
    sort_mode=pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
```

### `BMT5_ENUM_ORDER_TYPE` (для поля `OpenedOrderInfo.type`)

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_TYPE_BUY` | 0 | Рыночный ордер Buy (длинная позиция) |
| `BMT5_ORDER_TYPE_SELL` | 1 | Рыночный ордер Sell (короткая позиция) |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Отложенный ордер Buy Limit |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Отложенный ордер Sell Limit |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Отложенный ордер Buy Stop |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Отложенный ордер Sell Stop |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Ордер Buy Stop Limit |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Ордер Sell Stop Limit |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Ордер на закрытие встречной позицией |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип ордера
for order in data.opened_orders:
    if order.type == pb2.BMT5_ORDER_TYPE_BUY_LIMIT:
        print(f"Buy Limit order: {order.ticket}")
```

### `BMT5_ENUM_ORDER_STATE` (для поля `OpenedOrderInfo.state`)

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_STATE_STARTED` | 0 | Ордер проверен, но ещё не принят брокером |
| `BMT5_ORDER_STATE_PLACED` | 1 | Ордер принят |
| `BMT5_ORDER_STATE_CANCELED` | 2 | Ордер отменён клиентом |
| `BMT5_ORDER_STATE_PARTIAL` | 3 | Ордер исполнен частично |
| `BMT5_ORDER_STATE_FILLED` | 4 | Ордер исполнен полностью |
| `BMT5_ORDER_STATE_REJECTED` | 5 | Ордер отклонён |
| `BMT5_ORDER_STATE_EXPIRED` | 6 | Ордер истёк |
| `BMT5_ORDER_STATE_REQUEST_ADD` | 7 | Ордер регистрируется (размещение в торговой системе) |
| `BMT5_ORDER_STATE_REQUEST_MODIFY` | 8 | Ордер изменяется (изменение параметров) |
| `BMT5_ORDER_STATE_REQUEST_CANCEL` | 9 | Ордер удаляется (удаление из торговой системы) |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить состояние ордера
for order in data.opened_orders:
    if order.state == pb2.BMT5_ORDER_STATE_PLACED:
        print(f"Order {order.ticket} is active")
```

### `BMT5_ENUM_ORDER_TYPE_FILLING` (для поля `OpenedOrderInfo.type_filling`)

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill - исполнить полностью или отменить |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel - исполнить доступный объём |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Режим исполнения Return |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel - разместить ордер в стакане |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип исполнения
for order in data.opened_orders:
    if order.type_filling == pb2.BMT5_ORDER_FILLING_FOK:
        print(f"Order {order.ticket} uses Fill-or-Kill")
```

### `BMT5_ENUM_ORDER_TYPE_TIME` (для поля `OpenedOrderInfo.type_time`)

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_TIME_GTC` | 0 | Good Till Cancelled (действует до отмены) |
| `BMT5_ORDER_TIME_DAY` | 1 | Good Till Day (до конца дня) |
| `BMT5_ORDER_TIME_SPECIFIED` | 2 | Good Till Specified (до указанного времени) |
| `BMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Good Till Specified day (до конца указанного дня) |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип срока действия
for order in data.opened_orders:
    if order.type_time == pb2.BMT5_ORDER_TIME_GTC:
        print(f"Order {order.ticket} is GTC")
```

### `BMT5_ENUM_POSITION_TYPE` (для поля `PositionInfo.type`)

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_POSITION_TYPE_BUY` | 0 | Позиция Buy (длинная) |
| `BMT5_POSITION_TYPE_SELL` | 1 | Позиция Sell (короткая) |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип позиции
for pos in data.position_infos:
    if pos.type == pb2.BMT5_POSITION_TYPE_BUY:
        print(f"Long position: {pos.ticket}")
```

### `BMT5_ENUM_POSITION_REASON` (для поля `PositionInfo.reason`)

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_POSITION_REASON_CLIENT` | 0 | Позиция открыта вручную клиентом |
| `BMT5_POSITION_REASON_MOBILE` | 1 | Позиция открыта через мобильное приложение |
| `BMT5_POSITION_REASON_WEB` | 2 | Позиция открыта через веб-платформу |
| `BMT5_POSITION_REASON_EXPERT` | 3 | Позиция открыта советником (Expert Advisor) |
| `ORDER_REASON_SL` | 4 | Позиция закрыта по стоп-лоссу |
| `ORDER_REASON_TP` | 5 | Позиция закрыта по тейк-профиту |
| `ORDER_REASON_SO` | 6 | Позиция закрыта по Stop Out |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить причину позиции
for pos in data.position_infos:
    if pos.reason == pb2.BMT5_POSITION_REASON_EXPERT:
        print(f"Position {pos.ticket} opened by EA")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать неограниченно долго (или до истечения таймаута сервера).
* **Два отдельных списка:** Ордера и позиции возвращаются в отдельных списках - проверяйте оба.
* **Требуется подключение:** Перед использованием этого метода нужно вызвать `connect_by_host_port()` или `connect_by_server_name()`.
* **Полные данные:** Этот метод возвращает полную информацию об ордерах/позициях - для более лёгкой нагрузки используйте `opened_orders_tickets()`.
* **Потокобезопасность:** Все асинхронные методы безопасно вызывать одновременно из нескольких asyncio-задач.
* **Работа с UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не передан. Для явного контроля (например, в сценариях стриминга) передавайте `id_=uuid4()` в конструктор.

---

## 🔗 Примеры использования

### 1) Получить все открытые ордера и позиции

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def main():
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

        data = await account.opened_orders(
            sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
            deadline=deadline
        )

        print(f"Pending orders: {len(data.opened_orders)}")
        print(f"Open positions: {len(data.position_infos)}")

        # Показать позиции
        for pos in data.position_infos:
            print(f"Position #{pos.ticket} {pos.symbol}: "
                  f"{pos.volume} lots @ {pos.price_open}, P/L: ${pos.profit:.2f}")

        # Показать ордера
        for order in data.opened_orders:
            print(f"Order #{order.ticket} {order.symbol}: "
                  f"{order.volume_initial} lots @ {order.price_open}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Подсчитать ордера и позиции отдельно

```python
async def get_opened_summary(account: MT5Account) -> dict:
    """Get summary of opened orders and positions"""
    data = await account.opened_orders()

    summary = {
        "orders_count": len(data.opened_orders),
        "positions_count": len(data.position_infos),
        "total_count": len(data.opened_orders) + len(data.position_infos)
    }

    print(f"[OK] Pending orders: {summary['orders_count']}")
    print(f"[OK] Open positions: {summary['positions_count']}")
    print(f"[OK] Total: {summary['total_count']}")

    return summary

# Использование:
summary = await get_opened_summary(account)
```

### 3) Рассчитать суммарную плавающую P/L

```python
async def get_total_profit(account: MT5Account) -> float:
    """Calculate total floating profit/loss from all positions"""
    data = await account.opened_orders()

    total_profit = sum(pos.profit for pos in data.position_infos)

    print(f"Total floating P/L: ${total_profit:+.2f}")
    return total_profit

# Использование:
profit = await get_total_profit(account)
if profit < 0:
    print(f"[WARNING] Account in loss: ${profit:.2f}")
```

### 4) Найти позиции по символу

```python
async def get_positions_by_symbol(
    account: MT5Account,
    symbol: str
) -> list:
    """Get all open positions for specific symbol"""
    data = await account.opened_orders()

    positions = [
        pos for pos in data.position_infos
        if pos.symbol == symbol
    ]

    print(f"[OK] Found {len(positions)} position(s) for {symbol}")
    return positions

# Использование:
eurusd_positions = await get_positions_by_symbol(account, "EURUSD")
for pos in eurusd_positions:
    print(f"  #{pos.ticket}: {pos.volume} lots, P/L: ${pos.profit:.2f}")
```

### 5) Отобразить позиции с деталями

```python
async def display_positions(account: MT5Account):
    """Display all positions with formatted output"""
    data = await account.opened_orders()

    if not data.position_infos:
        print("[INFO] No open positions")
        return

    print(f"\n{'='*80}")
    print(f"OPEN POSITIONS ({len(data.position_infos)})")
    print(f"{'='*80}")
    print(f"{'Ticket':<12} {'Symbol':<10} {'Volume':<8} {'Price':<10} {'Current':<10} {'Profit':<12}")
    print(f"{'-'*80}")

    for pos in data.position_infos:
        type_str = "BUY" if pos.type == 0 else "SELL"
        print(f"{pos.ticket:<12} {pos.symbol:<10} {pos.volume:<8.2f} "
              f"{pos.price_open:<10.5f} {pos.price_current:<10.5f} ${pos.profit:+11.2f}")

    total = sum(pos.profit for pos in data.position_infos)
    print(f"{'-'*80}")
    print(f"{'TOTAL:':<62} ${total:+11.2f}")
    print(f"{'='*80}\n")

# Использование:
await display_positions(account)
```

### 6) Отслеживать новые ордера/позиции

```python
async def monitor_opened(account: MT5Account, interval: float = 5.0):
    """Monitor for changes in orders/positions"""
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders()

            # Собрать все текущие тикеты
            current_tickets = set()
            for order in data.opened_orders:
                current_tickets.add(("ORDER", order.ticket))
            for pos in data.position_infos:
                current_tickets.add(("POSITION", pos.ticket))

            # Обнаружить новые элементы
            if previous_tickets:
                new_items = current_tickets - previous_tickets
                closed_items = previous_tickets - current_tickets

                for item_type, ticket in new_items:
                    print(f"[+] New {item_type}: #{ticket}")

                for item_type, ticket in closed_items:
                    print(f"[-] Closed {item_type}: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Использование:
# await monitor_opened(account, interval=5.0)
```

### 7) Получить позиции, отсортированные по прибыли

```python
async def get_worst_positions(account: MT5Account, limit: int = 5):
    """Get positions with worst performance"""
    data = await account.opened_orders()

    # Сортировка по прибыли (сначала худшие)
    sorted_positions = sorted(
        data.position_infos,
        key=lambda p: p.profit
    )

    worst = sorted_positions[:limit]

    print(f"\nWorst {limit} positions:")
    for i, pos in enumerate(worst, 1):
        print(f"{i}. #{pos.ticket} {pos.symbol}: ${pos.profit:+.2f}")

    return worst

# Использование:
worst = await get_worst_positions(account, limit=5)
```

### 8) Проверить, есть ли открытая позиция по символу

```python
async def has_position_for_symbol(
    account: MT5Account,
    symbol: str
) -> bool:
    """Check if symbol has open position"""
    data = await account.opened_orders()

    has_pos = any(pos.symbol == symbol for pos in data.position_infos)

    if has_pos:
        print(f"[OK] Position found for {symbol}")
    else:
        print(f"[INFO] No position for {symbol}")

    return has_pos

# Использование:
if not await has_position_for_symbol(account, "EURUSD"):
    print("Can open new EURUSD position")
```

---

## Типовые шаблоны

### Быстрый поиск позиции

```python
async def get_position_by_ticket(account: MT5Account, ticket: int):
    """Find specific position by ticket"""
    data = await account.opened_orders()
    for pos in data.position_infos:
        if pos.ticket == ticket:
            return pos
    return None
```

### Рассчитать экспозицию по символам

```python
async def get_symbol_exposure(account: MT5Account) -> dict:
    """Calculate total volume per symbol"""
    data = await account.opened_orders()

    exposure = {}
    for pos in data.position_infos:
        exposure[pos.symbol] = exposure.get(pos.symbol, 0) + pos.volume

    return exposure
```

---

## 📚 См. также

* [positions_total](./positions_total.md) - Получить только количество (быстрее)
* [opened_orders_tickets](./opened_orders_tickets.md) - Получить только ID тикетов
* [positions_history](./positions_history.md) - Получить историю закрытых позиций
* [order_history](./order_history.md) - Получить исторические ордера
