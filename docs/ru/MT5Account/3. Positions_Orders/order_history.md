# Получение истории ордеров

> **Запрос:** исторические данные об ордерах в заданном временном диапазоне с поддержкой пагинации.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.order_history(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Определение в proto:** `OrderHistory` (определено в `mt5-term-api-account-helper.proto`)
* **Enum в этом методе:** 8 enum, всего 66 констант (1 на входе, 7 на выходе)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `OrderHistory(OrderHistoryRequest) -> OrderHistoryReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.OrderHistory(request, metadata, timeout)`

## 💬 Только самое важное

* **Что это.** Получить исторические ордера и сделки во временном диапазоне с сортировкой и пагинацией.
* **Зачем это нужно.** Анализировать историю торговли, рассчитывать статистику, проводить аудит ордеров.
* **Когда использовать.** Используйте для истории ордеров. Для закрытых позиций используйте `positions_history()`.

---

## 🎯 Назначение

Используйте для получения исторических торговых данных:

* Получить прошлые ордера и сделки в диапазоне дат
* Анализировать торговую эффективность
* Рассчитать статистику прибыли/убытка
* Проводить аудит торговой активности
* Экспортировать историю торговли
* Поддержка пагинации для больших наборов данных

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [order_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW.md)**

---

## Сигнатура метода

```python
async def order_history(
    self,
    from_dt: datetime,
    to_dt: datetime,
    sort_mode: account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_ASC,
    page_number: int = 0,
    items_per_page: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OrdersHistoryData
```

**Сообщение запроса:**

```protobuf
message OrderHistoryRequest {
  google.protobuf.Timestamp inputFrom = 1;
  google.protobuf.Timestamp inputTo = 2;
  BMT5_ENUM_ORDER_HISTORY_SORT_TYPE inputSortMode = 3;
  int32 pageNumber = 4;
  int32 itemsPerPage = 5;
}
```

**Сообщение ответа:**

```protobuf
message OrderHistoryReply {
  oneof response {
    OrdersHistoryData data = 1;
    Error error = 2;
  }
}

message OrdersHistoryData {
  int32 arrayTotal = 1;
  int32 pageNumber = 2;
  int32 itemsPerPage = 3;
  repeated HistoryData history_data = 4;
}
```

---

## 🔽 Вход

| Параметр        | Тип                                  | Описание                                             |
| --------------- | ------------------------------------ | ---------------------------------------------------- |
| `from_dt`       | `datetime` (обязательно)                | Начальное время запроса истории (время сервера)      |
| `to_dt`         | `datetime` (обязательно)                | Конечное время запроса истории (время сервера)       |
| `sort_mode`     | `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE` (enum) | Режим сортировки (по времени или ID тикета)    |
| `page_number`   | `int` (опционально)                     | Номер страницы для пагинации (по умолчанию 0)        |
| `items_per_page`| `int` (опционально)                     | Элементов на странице (по умолчанию 0 = все)         |
| `deadline`      | `datetime` (опционально)                | Крайний срок для вызова gRPC (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (опционально)      | Событие для отмены операции                          |

**Использование:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получить историю за последние 7 дней
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=7)

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
    page_number=0,
    items_per_page=100
)
```

---

## ⬆️ Выход - `OrdersHistoryData`

| Поле            | Тип                     | Тип Python            | Описание                                 |
| --------------- | ----------------------- | --------------------- | ---------------------------------------- |
| `arrayTotal`    | `int32`                 | `int`                 | Общее количество записей (все страницы)  |
| `pageNumber`    | `int32`                 | `int`                 | Номер текущей страницы                   |
| `itemsPerPage`  | `int32`                 | `int`                 | Элементов на странице                    |
| `history_data`  | `repeated HistoryData`  | `list[HistoryData]`   | Список исторических записей ордеров/сделок |
| `next_page_token` | `string`              | `str`                 | Курсор для следующей страницы (пусто, если последняя) |

**Каждый HistoryData содержит:**

| Поле            | Тип                | Описание                                             |
| --------------- | ------------------ | ---------------------------------------------------- |
| `index`         | `uint32`           | Индекс в наборе результатов                          |
| `history_order` | `OrderHistoryData` | Данные ордера (если применимо)                       |
| `history_deal`  | `DealHistoryData`  | Данные сделки (если применимо)                       |

**Поля OrderHistoryData:**

- `ticket` (uint64) - Номер тикета ордера
- `setup_time` (Timestamp) - Время размещения ордера
- `done_time` (Timestamp) - Время исполнения ордера
- `state` (BMT5_ENUM_ORDER_STATE) - Состояние ордера
- `price_current` (double) - Текущая цена
- `price_open` (double) - Цена открытия ордера
- `stop_limit` (double) - Цена стоп-лимита
- `stop_loss` (double) - Уровень стоп-лосса
- `take_profit` (double) - Уровень тейк-профита
- `volume_current` (double) - Текущий объём
- `volume_initial` (double) - Начальный объём
- `magic_number` (int64) - ID советника (Expert Advisor)
- `type` (BMT5_ENUM_ORDER_TYPE) - Тип ордера
- `time_expiration` (Timestamp) - Время истечения ордера
- `type_filling` (BMT5_ENUM_ORDER_TYPE_FILLING) - Тип исполнения
- `type_time` (BMT5_ENUM_ORDER_TYPE_TIME) - Срок жизни ордера
- `position_id` (uint64) - Тикет позиции
- `symbol` (string) - Имя символа
- `external_id` (string) - Внешний ID
- `comment` (string) - Комментарий ордера
- `account_login` (int64) - Логин счёта
- `setup_time_utc` (Timestamp) - Время размещения ордера (UTC)
- `done_time_utc` (Timestamp) - Время исполнения ордера (UTC)
- `time_expiration_utc` (Timestamp) - Время истечения ордера (UTC)

**Поля DealHistoryData:**

- `ticket` (uint64) - Номер тикета сделки
- `profit` (double) - Прибыль сделки
- `commission` (double) - Комиссия
- `fee` (double) - Дополнительный сбор
- `price` (double) - Цена сделки
- `stop_loss` (double) - Уровень стоп-лосса на момент сделки
- `take_profit` (double) - Уровень тейк-профита на момент сделки
- `swap` (double) - Своп
- `volume` (double) - Объём сделки
- `entry_type` (BMT5_ENUM_DEAL_ENTRY_TYPE) - Тип входа
- `time` (Timestamp) - Время сделки
- `type` (BMT5_ENUM_DEAL_TYPE) - Тип сделки
- `reason` (BMT5_ENUM_DEAL_REASON) - Причина сделки
- `position_id` (uint64) - ID позиции
- `comment` (string) - Комментарий сделки
- `symbol` (string) - Имя символа
- `external_id` (string) - Внешний ID
- `account_login` (int64) - Логин счёта
- `time_utc` (Timestamp) - Время сделки (UTC)
- `order` (uint64) - Тикет ордера, породившего сделку
- `magic` (int64) - Magic-номер советника (Expert Advisor)

---

## 🧱 Связанные enum (из proto)

### `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE`

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_SORT_BY_OPEN_TIME_ASC` | 0 | Сортировка по времени открытия по возрастанию |
| `BMT5_SORT_BY_OPEN_TIME_DESC` | 1 | Сортировка по времени открытия по убыванию |
| `BMT5_SORT_BY_CLOSE_TIME_ASC` | 2 | Сортировка по времени закрытия по возрастанию |
| `BMT5_SORT_BY_CLOSE_TIME_DESC` | 3 | Сортировка по времени закрытия по убыванию |
| `BMT5_SORT_BY_ORDER_TICKET_ID_ASC` | 4 | Сортировка по ID тикета по возрастанию |
| `BMT5_SORT_BY_ORDER_TICKET_ID_DESC` | 5 | Сортировка по ID тикета по убыванию |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=pb2.BMT5_SORT_BY_CLOSE_TIME_DESC
)
```

### `BMT5_ENUM_ORDER_STATE`

Определён в `mt5-term-api-account-helper.proto`. Используется в `OrderHistoryData` для указания состояния ордера.

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
| `BMT5_ORDER_STATE_REQUEST_MODIFY` | 8 | Ордер изменяется (изменение его параметров) |
| `BMT5_ORDER_STATE_REQUEST_CANCEL` | 9 | Ордер удаляется (удаление из торговой системы) |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить состояние ордера в истории
for item in data.history_data:
    if item.history_order.state == pb2.BMT5_ORDER_STATE_FILLED:
        print(f"Order {item.history_order.ticket} was filled")
```

### `BMT5_ENUM_ORDER_TYPE`

Определён в `mt5-term-api-account-helper.proto`. Используется в `OrderHistoryData` для указания типа ордера.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_TYPE_BUY` | 0 | Рыночный ордер Buy |
| `BMT5_ORDER_TYPE_SELL` | 1 | Рыночный ордер Sell |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Отложенный ордер Buy Limit |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Отложенный ордер Sell Limit |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Отложенный ордер Buy Stop |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Отложенный ордер Sell Stop |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Отложенный ордер Buy Stop Limit |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Отложенный ордер Sell Stop Limit |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Закрытие встречной позицией |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Отфильтровать ордера на покупку
for item in data.history_data:
    if item.history_order.type == pb2.BMT5_ORDER_TYPE_BUY:
        print(f"Buy order: {item.history_order.ticket}")
```

### `BMT5_ENUM_ORDER_TYPE_FILLING`

Определён в `mt5-term-api-account-helper.proto`. Используется в `OrderHistoryData` для указания типа исполнения ордера.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Return |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип исполнения
for item in data.history_data:
    if item.history_order.type_filling == pb2.BMT5_ORDER_FILLING_FOK:
        print(f"FOK order: {item.history_order.ticket}")
```

### `BMT5_ENUM_ORDER_TYPE_TIME`

Определён в `mt5-term-api-account-helper.proto`. Используется в `OrderHistoryData` для указания срока жизни ордера.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_ORDER_TIME_GTC` | 0 | Действует до отмены |
| `BMT5_ORDER_TIME_DAY` | 1 | Действует до конца текущего торгового дня |
| `BMT5_ORDER_TIME_SPECIFIED` | 2 | Действует до указанной даты |
| `BMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Действует до указанного дня |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип срока действия
for item in data.history_data:
    if item.history_order.type_time == pb2.BMT5_ORDER_TIME_GTC:
        print(f"GTC order: {item.history_order.ticket}")
```

### `BMT5_ENUM_DEAL_ENTRY_TYPE`

Определён в `mt5-term-api-account-helper.proto`. Используется в `DealHistoryData` для указания типа входа сделки.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_DEAL_ENTRY_IN` | 0 | Вход в рынок |
| `BMT5_DEAL_ENTRY_OUT` | 1 | Выход из рынка |
| `BMT5_DEAL_ENTRY_INOUT` | 2 | Разворот |
| `BMT5_DEAL_ENTRY_OUT_BY` | 3 | Закрытие встречной |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить тип входа сделки
for item in data.history_data:
    if item.history_deal.entry_type == pb2.BMT5_DEAL_ENTRY_IN:
        print(f"Entry in deal: {item.history_deal.ticket}")
```

### `BMT5_ENUM_DEAL_TYPE`

Определён в `mt5-term-api-account-helper.proto`. Используется в `DealHistoryData` для указания типа сделки.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_DEAL_TYPE_BUY` | 0 | Buy |
| `BMT5_DEAL_TYPE_SELL` | 1 | Sell |
| `BMT5_DEAL_TYPE_BALANCE` | 2 | Баланс |
| `BMT5_DEAL_TYPE_CREDIT` | 3 | Кредит |
| `BMT5_DEAL_TYPE_CHARGE` | 4 | Дополнительное списание |
| `BMT5_DEAL_TYPE_CORRECTION` | 5 | Коррекция |
| `BMT5_DEAL_TYPE_BONUS` | 6 | Бонус |
| `BMT5_DEAL_TYPE_COMMISSION` | 7 | Дополнительная комиссия |
| `BMT5_DEAL_TYPE_COMMISSION_DAILY` | 8 | Дневная комиссия |
| `BMT5_DEAL_TYPE_COMMISSION_MONTHLY` | 9 | Месячная комиссия |
| `BMT5_DEAL_TYPE_COMMISSION_AGENT_DAILY` | 10 | Дневная агентская комиссия |
| `BMT5_DEAL_TYPE_COMMISSION_AGENT_MONTHLY` | 11 | Месячная агентская комиссия |
| `BMT5_DEAL_TYPE_INTEREST` | 12 | Процентная ставка |
| `BMT5_DEAL_TYPE_BUY_CANCELED` | 13 | Отменённая сделка покупки |
| `BMT5_DEAL_TYPE_SELL_CANCELED` | 14 | Отменённая сделка продажи |
| `BMT5_DEAL_DIVIDEND` | 15 | Дивиденд |
| `BMT5_DEAL_DIVIDEND_FRANKED` | 16 | Франкированный дивиденд |
| `BMT5_DEAL_TAX` | 17 | Налог |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Отфильтровать сделки покупки/продажи
for item in data.history_data:
    if item.history_deal.type == pb2.BMT5_DEAL_TYPE_BUY:
        print(f"Buy deal: {item.history_deal.ticket}")
    elif item.history_deal.type == pb2.BMT5_DEAL_TYPE_BALANCE:
        print(f"Balance operation: {item.history_deal.ticket}")
```

### `BMT5_ENUM_DEAL_REASON`

Определён в `mt5-term-api-account-helper.proto`. Используется в `DealHistoryData` для указания причины сделки.

| Constant | Value | Описание |
|----------|-------|-------------|
| `BMT5_DEAL_REASON_CLIENT` | 0 | Сделка размещена вручную |
| `BMT5_DEAL_REASON_MOBILE` | 1 | Сделка размещена с мобильного |
| `BMT5_DEAL_REASON_WEB` | 2 | Сделка размещена из веба |
| `BMT5_DEAL_REASON_EXPERT` | 3 | Сделка размещена советником |
| `BMT5_DEAL_REASON_SL` | 4 | Сделка размещена из-за стоп-лосса |
| `BMT5_DEAL_REASON_TP` | 5 | Сделка размещена из-за тейк-профита |
| `BMT5_DEAL_REASON_SO` | 6 | Сделка размещена из-за Stop Out |
| `BMT5_DEAL_REASON_ROLLOVER` | 7 | Сделка из-за ролловера |
| `BMT5_DEAL_REASON_VMARGIN` | 8 | Сделка из-за вариационной маржи |
| `BMT5_DEAL_REASON_SPLIT` | 9 | Сделка из-за сплита |
| `BMT5_DEAL_REASON_CORPORATE_ACTION` | 10 | Сделка из-за корпоративного действия |

**Использование:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Проверить причину сделки
for item in data.history_data:
    if item.history_deal.reason == pb2.BMT5_DEAL_REASON_SL:
        print(f"Stop Loss deal: {item.history_deal.ticket}")
    elif item.history_deal.reason == pb2.BMT5_DEAL_REASON_EXPERT:
        print(f"EA deal: {item.history_deal.ticket}")
```

---

## 🧩 Примечания и советы

* **Время сервера:** Параметры `from_dt` и `to_dt` используют время сервера, а не UTC.
* **Пагинация:** Используйте `page_number` и `items_per_page` для больших наборов данных. Установите `items_per_page=0`, чтобы получить все результаты.
* **Общее количество:** Поле `arrayTotal` показывает общее количество записей на всех страницах.
* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC.
* **Требуется подключение:** Сначала вызовите `connect_by_host_port()` или `connect_by_server_name()`.
* **Потокобезопасность:** Безопасно вызывать одновременно из нескольких asyncio-задач.
* **Работа с UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не передан.
  Для явного контроля (например, в сценариях стриминга) передавайте `id_=uuid4()` в конструктор.
  
---

## 🔗 Примеры использования

### 1) Получить историю за последние 7 дней

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
        # Последние 7 дней
        to_dt = datetime.now(timezone.utc)
        from_dt = to_dt - timedelta(days=7)

        data = await account.order_history(
            from_dt=from_dt,
            to_dt=to_dt,
            sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
            items_per_page=100
        )

        print(f"Total records: {data.arrayTotal}")
        print(f"Returned: {len(data.history_data)} records")

        for item in data.history_data:
            if item.history_deal:
                deal = item.history_deal
                print(f"Deal #{deal.ticket}: ${deal.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Получить историю с пагинацией

```python
async def get_all_history_paginated(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    page_size: int = 100
):
    """Get all history records using pagination"""
    all_records = []
    page = 0

    while True:
        data = await account.order_history(
            from_dt=from_dt,
            to_dt=to_dt,
            sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_ASC,
            page_number=page,
            items_per_page=page_size
        )

        print(f"[OK] Page {page + 1}: {len(data.history_data)} records")

        all_records.extend(data.history_data)

        # Проверить, получили ли мы все записи
        if len(all_records) >= data.arrayTotal:
            break

        page += 1

    print(f"[OK] Total records retrieved: {len(all_records)}")
    return all_records

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
history = await get_all_history_paginated(account, from_dt, to_dt)
```

### 3) Рассчитать суммарную прибыль за период

```python
async def calculate_period_profit(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> float:
    """Calculate total profit for time period"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0  # Получить все
    )

    total_profit = 0.0
    for item in data.history_data:
        if item.history_deal:
            total_profit += item.history_deal.profit

    print(f"Total profit ({from_dt.date()} to {to_dt.date()}): ${total_profit:+.2f}")
    return total_profit

# Использование:
from_dt = datetime(2024, 1, 1)
to_dt = datetime(2024, 1, 31)
profit = await calculate_period_profit(account, from_dt, to_dt)
```

### 4) Получить историю торговли за сегодня

```python
async def get_today_history(account: MT5Account):
    """Get all trades from today"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    data = await account.order_history(
        from_dt=today_start,
        to_dt=now,
        sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC
    )

    print(f"\nToday's trading activity:")
    print(f"Total records: {data.arrayTotal}")

    for item in data.history_data:
        if item.history_deal:
            deal = item.history_deal
            time = deal.time.ToDatetime()
            print(f"  {time.strftime('%H:%M:%S')} - "
                  f"#{deal.ticket} {deal.symbol}: ${deal.profit:+.2f}")

    return data

# Использование:
await get_today_history(account)
```

### 5) Экспорт истории в CSV

```python
import csv

async def export_history_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "order_history.csv"
):
    """Export order history to CSV file"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Time', 'Symbol', 'Type', 'Volume',
            'Price', 'Profit', 'Commission', 'Swap'
        ])

        for item in data.history_data:
            if item.history_deal:
                deal = item.history_deal
                time = deal.time.ToDatetime()
                writer.writerow([
                    deal.ticket,
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    deal.symbol,
                    deal.type,
                    deal.volume,
                    deal.price,
                    deal.profit,
                    deal.commission,
                    deal.swap
                ])

    print(f"[OK] Exported {data.arrayTotal} records to {filename}")

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
await export_history_to_csv(account, from_dt, to_dt)
```

### 6) Получить выигрышные и проигрышные сделки

```python
async def analyze_win_loss(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analyze winning vs losing trades"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for item in data.history_data:
        if item.history_deal:
            profit = item.history_deal.profit
            if profit > 0:
                wins += 1
                total_win_profit += profit
            elif profit < 0:
                losses += 1
                total_loss_profit += profit

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    result = {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_win_profit": total_win_profit,
        "total_loss_profit": total_loss_profit,
        "net_profit": total_win_profit + total_loss_profit
    }

    print(f"\nTrading Statistics:")
    print(f"  Total trades: {total_trades}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Win profit: ${total_win_profit:.2f}")
    print(f"  Loss profit: ${total_loss_profit:.2f}")
    print(f"  Net profit: ${result['net_profit']:+.2f}")

    return result

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
stats = await analyze_win_loss(account, from_dt, to_dt)
```

---

## Типовые шаблоны

### Получить историю по конкретному символу

```python
async def get_symbol_history(
    account: MT5Account,
    symbol: str,
    from_dt: datetime,
    to_dt: datetime
):
    """Filter history by symbol"""
    data = await account.order_history(from_dt=from_dt, to_dt=to_dt)

    symbol_deals = [
        item for item in data.history_data
        if item.history_deal and item.history_deal.symbol == symbol
    ]

    return symbol_deals
```

### Рассчитать дневную прибыль

```python
from collections import defaultdict

async def get_daily_profit(account: MT5Account, from_dt: datetime, to_dt: datetime):
    """Calculate profit per day"""
    data = await account.order_history(from_dt=from_dt, to_dt=to_dt, items_per_page=0)

    daily_profit = defaultdict(float)

    for item in data.history_data:
        if item.history_deal:
            deal = item.history_deal
            date = deal.time.ToDatetime().date()
            daily_profit[date] += deal.profit

    return dict(daily_profit)
```

---

## 📚 См. также

* [positions_history](./positions_history.md) - Получить историю закрытых позиций
* [opened_orders](./opened_orders.md) - Получить текущие открытые ордера
* [positions_total](./positions_total.md) - Получить количество открытых позиций
