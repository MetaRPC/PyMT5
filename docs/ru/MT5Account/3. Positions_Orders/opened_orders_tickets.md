# Получение ID тикетов открытых ордеров и позиций

> **Запрос:** ID тикетов всех текущих открытых ордеров и позиций (облегчённая альтернатива полным данным).

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.opened_orders_tickets(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Определение в proto:** `OpenedOrdersTickets` (определено в `mt5-term-api-account-helper.proto`)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `OpenedOrdersTickets(OpenedOrdersTicketsRequest) -> OpenedOrdersTicketsReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.OpenedOrdersTickets(request, metadata, timeout)`

## 💬 Только самое важное

* **Что это.** Получить только ID тикетов открытых ордеров и позиций без полных данных.
* **Зачем это нужно.** Облегчённая проверка того, какие ордера/позиции существуют. Эффективнее, чем `opened_orders()`.
* **Когда использовать.** Используйте, когда нужны только ID тикетов. Для полных данных используйте `opened_orders()`.

---

## 🎯 Назначение

Используйте для получения только ID тикетов:

* Проверить, какие ордера/позиции открыты сейчас
* Отслеживать ID тикетов для последующих запросов
* Эффективно отслеживать новые/закрытые ордера
* Более лёгкая нагрузка, чем полный `opened_orders()`
* Быстрая проверка наличия перед получением полных данных

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [opened_orders_tickets - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_tickets_HOW.md)**

---

## Сигнатура метода

```python
async def opened_orders_tickets(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OpenedOrdersTicketsData
```

**Сообщение запроса:**

```protobuf
message OpenedOrdersTicketsRequest {
  // Пусто - параметры не нужны
}
```

**Сообщение ответа:**

```protobuf
message OpenedOrdersTicketsReply {
  oneof response {
    OpenedOrdersTicketsData data = 1;
    Error error = 2;
  }
}

message OpenedOrdersTicketsData {
  repeated int64 opened_orders_tickets = 1;
  repeated int64 opened_position_tickets = 2;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `deadline`    | `datetime` (опционально)   | Крайний срок для вызова gRPC (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (опционально) | Событие для отмены операции                   |

**Дополнительных параметров нет** - этот метод возвращает только ID тикетов.

**Варианты с deadline:**

```python
from datetime import datetime, timedelta, timezone

# С deadline
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
data = await account.opened_orders_tickets(deadline=deadline)

# Без deadline
data = await account.opened_orders_tickets()
```

---

## ⬆️ Выход - `OpenedOrdersTicketsData`

| Поле                        | Тип                 | Тип Python     | Описание                                         |
| --------------------------- | ------------------- | -------------- | ------------------------------------------------ |
| `opened_orders_tickets`     | `repeated int64`    | `list[int]`    | Список ID тикетов отложенных ордеров             |
| `opened_position_tickets`   | `repeated int64`    | `list[int]`    | Список ID тикетов открытых позиций               |

**Возвращаемое значение:** Метод возвращает объект `OpenedOrdersTicketsData`, оба списка доступны как атрибуты.

---

## 🧱 Связанные enum (из proto)

Этот метод не использует enum.

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных ошибок gRPC.
* **Облегчённый:** Возвращаются только ID тикетов - нагрузка намного меньше, чем у `opened_orders()`.
* **Два отдельных списка:** Тикеты ордеров и тикеты позиций находятся в отдельных списках.
* **Требуется подключение:** Сначала нужно вызвать `connect_by_host_port()` или `connect_by_server_name()`.
* **Потокобезопасность:** Безопасно вызывать одновременно из нескольких asyncio-задач.
* **Работа с UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не передан. Для явного контроля (например, в сценариях стриминга) передавайте `id_=uuid4()` в конструктор.

---

## 🔗 Примеры использования

### 1) Получить все ID тикетов

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account

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
        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
        data = await account.opened_orders_tickets(deadline=deadline)

        print(f"Order tickets: {data.opened_orders_tickets}")
        print(f"Position tickets: {data.opened_position_tickets}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Проверить существование тикета

```python
async def ticket_exists(account: MT5Account, ticket: int) -> bool:
    """Check if ticket ID exists in opened orders/positions"""
    data = await account.opened_orders_tickets()

    exists = (
        ticket in data.opened_orders_tickets or
        ticket in data.opened_position_tickets
    )

    if exists:
        print(f"[OK] Ticket #{ticket} found")
    else:
        print(f"[INFO] Ticket #{ticket} not found")

    return exists

# Использование:
if await ticket_exists(account, 123456):
    print("Order/position still open")
```

### 3) Отслеживать изменения тикетов

```python
async def monitor_tickets(account: MT5Account, interval: float = 5.0):
    """Monitor for changes in ticket IDs"""
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders_tickets()

            current_tickets = set(data.opened_orders_tickets + data.opened_position_tickets)

            if previous_tickets:
                new = current_tickets - previous_tickets
                closed = previous_tickets - current_tickets

                for ticket in new:
                    print(f"[+] New ticket: #{ticket}")
                for ticket in closed:
                    print(f"[-] Closed ticket: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Использование:
# await monitor_tickets(account, interval=5.0)
```

### 4) Получить все тикеты вместе

```python
async def get_all_tickets(account: MT5Account) -> list[int]:
    """Get all order and position tickets combined"""
    data = await account.opened_orders_tickets()

    all_tickets = list(data.opened_orders_tickets) + list(data.opened_position_tickets)

    print(f"[OK] Total tickets: {len(all_tickets)}")
    return all_tickets

# Использование:
tickets = await get_all_tickets(account)
print(f"All tickets: {tickets}")
```

### 5) Сравнить с предыдущим снимком

```python
async def compare_tickets(
    account: MT5Account,
    previous_orders: list[int],
    previous_positions: list[int]
) -> dict:
    """Compare current tickets with previous snapshot"""
    data = await account.opened_orders_tickets()

    result = {
        "new_orders": list(set(data.opened_orders_tickets) - set(previous_orders)),
        "closed_orders": list(set(previous_orders) - set(data.opened_orders_tickets)),
        "new_positions": list(set(data.opened_position_tickets) - set(previous_positions)),
        "closed_positions": list(set(previous_positions) - set(data.opened_position_tickets))
    }

    if result["new_orders"]:
        print(f"[+] New orders: {result['new_orders']}")
    if result["closed_orders"]:
        print(f"[-] Closed orders: {result['closed_orders']}")
    if result["new_positions"]:
        print(f"[+] New positions: {result['new_positions']}")
    if result["closed_positions"]:
        print(f"[-] Closed positions: {result['closed_positions']}")

    return result

# Использование:
# prev_orders = [12345, 12346]
# prev_positions = [12347]
# changes = await compare_tickets(account, prev_orders, prev_positions)
```

---

## Типовые шаблоны

### Быстрая проверка количества

```python
async def get_tickets_count(account: MT5Account) -> dict:
    """Get count of orders and positions"""
    data = await account.opened_orders_tickets()
    return {
        "orders": len(data.opened_orders_tickets),
        "positions": len(data.opened_position_tickets),
        "total": len(data.opened_orders_tickets) + len(data.opened_position_tickets)
    }
```

### Операции над множествами тикетов

```python
async def get_ticket_sets(account: MT5Account) -> tuple:
    """Get ticket IDs as sets for easy comparison"""
    data = await account.opened_orders_tickets()
    return (
        set(data.opened_orders_tickets),
        set(data.opened_position_tickets)
    )
```

---

## 📚 См. также

* [opened_orders](./opened_orders.md) - Получить полные данные об ордерах и позициях
* [positions_total](./positions_total.md) - Получить только количество (ещё легче)
* [positions_history](./positions_history.md) - Получить историю закрытых позиций
