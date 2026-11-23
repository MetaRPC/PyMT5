# Получение истории закрытых позиций

> **Запрос:** исторические закрытые позиции во временном диапазоне с поддержкой сортировки и пагинации.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.positions_history(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Определение в proto:** `PositionsHistory` (определено в `mt5-term-api-account-helper.proto`)
* **Enum в этом методе:** 2 enum, всего 13 констант (1 на входе, 1 на выходе)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `PositionsHistory(PositionsHistoryRequest) -> PositionsHistoryReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.PositionsHistory(request, metadata, timeout)`

## 💬 Только самое важное

* **Что это.** Получить исторические закрытые позиции с фильтрацией по диапазону времени открытия.
* **Зачем это нужно.** Анализировать торговую эффективность, рассчитывать статистику по закрытым позициям.
* **Когда использовать.** Используйте для закрытых позиций. Для истории ордеров/сделок используйте `order_history()`.

---

## 🎯 Назначение

Используйте для получения истории закрытых позиций:

* Получить закрытые позиции в диапазоне дат
* Анализировать эффективность позиций
* Рассчитать прибыль/убыток по позициям
* Просмотреть закрытые сделки
* Фильтровать по времени открытия
* Поддержка пагинации для больших наборов данных

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [positions_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW.md)**

---

## Сигнатура метода

```python
async def positions_history(
    self,
    sort_type: account_helper_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: Optional[datetime] = None,
    open_to: Optional[datetime] = None,
    page: int = 0,
    size: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.PositionsHistoryData
```

**Сообщение запроса:**

```protobuf
message PositionsHistoryRequest {
  AH_ENUM_POSITIONS_HISTORY_SORT_TYPE sort_type = 1;
  optional google.protobuf.Timestamp position_open_time_from = 2;
  optional google.protobuf.Timestamp position_open_time_to = 3;
  optional int32 page_number = 4;
  optional int32 items_per_page = 5;
}
```

**Сообщение ответа:**

```protobuf
message PositionsHistoryReply {
  oneof response {
    PositionsHistoryData data = 1;
    Error error = 2;
  }
}

message PositionsHistoryData {
  repeated PositionHistoryInfo history_positions = 1;
  int32 total_count = 2;
  string next_page_token = 3;
}
```

---

## 🔽 Вход

| Параметр        | Тип                                         | Описание                                             |
| --------------- | ------------------------------------------- | ---------------------------------------------------- |
| `sort_type`     | `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE` (enum, обязательно) | Режим сортировки позиций                |
| `open_from`     | `datetime` (опционально)                       | Начало фильтра по времени открытия (UTC)             |
| `open_to`       | `datetime` (опционально)                       | Конец фильтра по времени открытия (UTC)              |
| `page`          | `int` (опционально)                            | Номер страницы для пагинации (по умолчанию 0)        |
| `size`          | `int` (опционально)                            | Элементов на странице (по умолчанию 0 = все)         |
| `deadline`      | `datetime` (опционально)                       | Крайний срок для вызова gRPC (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (опционально)             | Событие для отмены операции                          |

**Использование:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Получить позиции, открытые за последние 7 дней
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=7)

data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt,
    page=0,
    size=100
)
```

---

## ⬆️ Выход - `PositionsHistoryData`

| Поле                | Тип                            | Тип Python                   | Описание                                 |
| ------------------- | ------------------------------ | ---------------------------- | ---------------------------------------- |
| `history_positions` | `repeated PositionHistoryInfo` | `list[PositionHistoryInfo]`  | Список записей исторических позиций       |
| `total_count`       | `int32`                        | `int`                        | Всего совпавших позиций на всех страницах |
| `next_page_token`   | `string`                       | `str`                        | Курсор для следующей страницы (пусто, если последняя) |

**Каждый PositionHistoryInfo содержит:**

| Поле               | Тип                | Описание                                             |
| ------------------ | ------------------ | ---------------------------------------------------- |
| `index`            | `int32`            | Индекс в наборе результатов                          |
| `position_ticket`  | `uint64`           | ID тикета позиции                                    |
| `order_type`       | `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE` | Тип ордера (BUY, SELL и т.д.)         |
| `open_time`        | `Timestamp`        | Время открытия позиции (время сервера)               |
| `open_time_utc`    | `Timestamp`        | Время открытия позиции (UTC)                         |
| `close_time`       | `Timestamp`        | Время закрытия позиции (время сервера)               |
| `close_time_utc`   | `Timestamp`        | Время закрытия позиции (UTC)                         |
| `volume`           | `double`           | Объём позиции в лотах                                |
| `open_price`       | `double`           | Цена открытия                                        |
| `close_price`      | `double`           | Цена закрытия                                        |
| `stop_loss`        | `double`           | Уровень стоп-лосса                                   |
| `take_profit`      | `double`           | Уровень тейк-профита                                 |
| `market_value`     | `double`           | Рыночная стоимость                                   |
| `commission`       | `double`           | Начисленная комиссия                                 |
| `fee`              | `double`           | Дополнительные сборы                                 |
| `profit`           | `double`           | Прибыль/убыток позиции                               |
| `swap`             | `double`           | Своп (перенос через ночь)                            |
| `comment`          | `string`           | Комментарий                                          |
| `symbol`           | `string`           | Имя символа                                          |
| `magic`            | `int64`            | Magic-номер (идентификатор EA)                       |

---

## 🧱 Связанные enum (из proto)

### `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE`

Определён в `mt5-term-api-account-helper.proto`.

| Constant | Value | Описание |
|----------|-------|-------------|
| `AH_POSITION_OPEN_TIME_ASC` | 0 | Сортировка по времени открытия по возрастанию |
| `AH_POSITION_OPEN_TIME_DESC` | 1 | Сортировка по времени открытия по убыванию |
| `AH_POSITION_TICKET_ASC` | 2 | Сортировка по ID тикета по возрастанию |
| `AH_POSITION_TICKET_DESC` | 3 | Сортировка по ID тикета по убыванию |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.positions_history(
    sort_type=pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt
)
```

### `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE`

Определён в `mt5-term-api-account-helper.proto`. Используется в `PositionHistoryInfo` для указания типа ордера.

| Constant | Value | Описание |
|----------|-------|-------------|
| `AH_ORDER_TYPE_BUY` | 0 | Рыночный ордер Buy |
| `AH_ORDER_TYPE_SELL` | 1 | Рыночный ордер Sell |
| `AH_ORDER_TYPE_BUY_LIMIT` | 2 | Отложенный ордер Buy Limit |
| `AH_ORDER_TYPE_SELL_LIMIT` | 3 | Отложенный ордер Sell Limit |
| `AH_ORDER_TYPE_BUY_STOP` | 4 | Отложенный ордер Buy Stop |
| `AH_ORDER_TYPE_SELL_STOP` | 5 | Отложенный ордер Sell Stop |
| `AH_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Отложенный ордер Buy Stop Limit |
| `AH_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Отложенный ордер Sell Stop Limit |
| `AH_ORDER_TYPE_CLOSE_BY` | 8 | Закрытие встречной позицией |

**Использование:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Отфильтровать позиции на покупку
for pos in data.history_positions:
    if pos.order_type == pb2.AH_ORDER_TYPE_BUY:
        print(f"Buy position: {pos.position_ticket}")
```

---

## 🧩 Примечания и советы

* **Фильтр по времени открытия:** `open_from` и `open_to` фильтруют позиции по времени их открытия, а не закрытия.
* **Пагинация:** Используйте `page` и `size` для больших наборов данных. Установите `size=0`, чтобы получить все результаты.
* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC.
* **Требуется подключение:** Сначала вызовите `connect_by_host_port()` или `connect_by_server_name()`.
* **Потокобезопасность:** Безопасно вызывать одновременно из нескольких asyncio-задач.
* **Работа с UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не передан. Для явного контроля (например, в сценариях стриминга) передавайте `id_=uuid4()` в конструктор.

---

## 🔗 Примеры использования

### 1) Получить закрытые позиции за последние 30 дней

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
        # Последние 30 дней
        to_dt = datetime.now(timezone.utc)
        from_dt = to_dt - timedelta(days=30)

        data = await account.positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
            open_from=from_dt,
            open_to=to_dt,
            size=100
        )

        print(f"Closed positions: {len(data.history_positions)}")

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            print(f"#{pos.position_ticket} {pos.symbol}: "
                  f"${pos.profit:+.2f} "
                  f"({open_time.date()} - {close_time.date()})")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Рассчитать суммарную прибыль по закрытым позициям

```python
async def calculate_closed_profit(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> float:
    """Calculate total profit from closed positions"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt,
        size=0  # Получить все
    )

    total_profit = sum(pos.profit for pos in data.history_positions)
    total_commission = sum(pos.commission for pos in data.history_positions)
    total_swap = sum(pos.swap for pos in data.history_positions)

    net_profit = total_profit - total_commission + total_swap

    print(f"Closed positions statistics:")
    print(f"  Total positions: {len(data.history_positions)}")
    print(f"  Gross profit: ${total_profit:+.2f}")
    print(f"  Commission: ${total_commission:.2f}")
    print(f"  Swap: ${total_swap:+.2f}")
    print(f"  Net profit: ${net_profit:+.2f}")

    return net_profit

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
profit = await calculate_closed_profit(account, from_dt, to_dt)
```

### 3) Проанализировать процент выигрышей

```python
async def analyze_closed_positions(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analyze closed positions performance"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for pos in data.history_positions:
        if pos.profit > 0:
            wins += 1
            total_win_profit += pos.profit
        elif pos.profit < 0:
            losses += 1
            total_loss_profit += pos.profit

    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    avg_win = total_win_profit / wins if wins > 0 else 0
    avg_loss = total_loss_profit / losses if losses > 0 else 0

    result = {
        "total_positions": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": abs(total_win_profit / total_loss_profit) if total_loss_profit != 0 else 0
    }

    print(f"\nPosition Analysis:")
    print(f"  Total: {total}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Avg Win: ${avg_win:.2f}")
    print(f"  Avg Loss: ${avg_loss:.2f}")
    print(f"  Profit Factor: {result['profit_factor']:.2f}")

    return result

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
stats = await analyze_closed_positions(account, from_dt, to_dt)
```

### 4) Получить лучшие и худшие позиции

```python
async def get_best_worst_positions(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    limit: int = 5
):
    """Get best and worst performing positions"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    # Сортировка по прибыли
    sorted_positions = sorted(data.history_positions, key=lambda p: p.profit, reverse=True)

    best = sorted_positions[:limit]
    worst = sorted_positions[-limit:]

    print(f"\nBest {limit} positions:")
    for i, pos in enumerate(best, 1):
        print(f"  {i}. #{pos.position_ticket} {pos.symbol}: ${pos.profit:+.2f}")

    print(f"\nWorst {limit} positions:")
    for i, pos in enumerate(worst, 1):
        print(f"  {i}. #{pos.position_ticket} {pos.symbol}: ${pos.profit:+.2f}")

    return {"best": best, "worst": worst}

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
results = await get_best_worst_positions(account, from_dt, to_dt)
```

### 5) Получить позиции по символу

```python
async def get_symbol_closed_positions(
    account: MT5Account,
    symbol: str,
    from_dt: datetime,
    to_dt: datetime
):
    """Get closed positions for specific symbol"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
        open_from=from_dt,
        open_to=to_dt
    )

    symbol_positions = [
        pos for pos in data.history_positions
        if pos.symbol == symbol
    ]

    total_profit = sum(pos.profit for pos in symbol_positions)

    print(f"\n{symbol} closed positions: {len(symbol_positions)}")
    print(f"Total profit: ${total_profit:+.2f}")

    return symbol_positions

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
eurusd_positions = await get_symbol_closed_positions(account, "EURUSD", from_dt, to_dt)
```

### 6) Экспорт в CSV

```python
import csv

async def export_positions_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "positions_history.csv"
):
    """Export closed positions to CSV"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Symbol', 'Open Time', 'Close Time',
            'Volume', 'Open Price', 'Close Price',
            'Profit', 'Commission', 'Swap', 'Total'
        ])

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            total = pos.profit - pos.commission + pos.swap

            writer.writerow([
                pos.position_ticket,
                pos.symbol,
                open_time.strftime('%Y-%m-%d %H:%M:%S'),
                close_time.strftime('%Y-%m-%d %H:%M:%S'),
                pos.volume,
                pos.open_price,
                pos.close_price,
                pos.profit,
                pos.commission,
                pos.swap,
                total
            ])

    print(f"[OK] Exported {len(data.history_positions)} positions to {filename}")

# Использование:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
await export_positions_to_csv(account, from_dt, to_dt)
```

---

## Типовые шаблоны

### Рассчитать дневную прибыль

```python
from collections import defaultdict

async def get_daily_profit(account: MT5Account, from_dt: datetime, to_dt: datetime):
    """Calculate profit per day from closed positions"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    daily_profit = defaultdict(float)

    for pos in data.history_positions:
        close_date = pos.close_time.ToDatetime().date()
        daily_profit[close_date] += pos.profit

    return dict(daily_profit)
```

### Получить позиции с пагинацией

```python
async def get_all_positions_paginated(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    page_size: int = 100
):
    """Get all positions using pagination"""
    all_positions = []
    page = 0

    while True:
        data = await account.positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
            open_from=from_dt,
            open_to=to_dt,
            page=page,
            size=page_size
        )

        if not data.history_positions:
            break

        all_positions.extend(data.history_positions)
        page += 1

    return all_positions
```

---

## 📚 См. также

* [order_history](./order_history.md) - Получить исторические ордера и сделки
* [opened_orders](./opened_orders.md) - Получить текущие открытые позиции
* [positions_total](./positions_total.md) - Получить количество открытых позиций
