# Получение общего количества открытых позиций

> **Запрос:** общее количество текущих открытых позиций на торговом счёте.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.positions_total(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.TradeFunctions`
* **Определение в proto:** `PositionsTotal` (определено в `mt5-term-api-trade-functions.proto`)
* **Enum в этом методе:** 0 enum (только простой счётчик)

### RPC

* **Сервис:** `mt5_term_api.TradeFunctions`
* **Метод:** `PositionsTotal(Empty) -> PositionsTotalReply`
* **Низкоуровневый клиент (сгенерированный):** `TradeFunctionsStub.PositionsTotal(request, metadata, timeout)`

## 💬 Только самое важное

* **Что это.** Получить общее количество открытых позиций без загрузки подробных данных о позициях.
* **Зачем это нужно.** Быстрая проверка открытых позиций. Полезно для управления рисками и торговой логики.
* **Когда использовать.** Используйте, когда нужно только количество. Для полных данных о позициях используйте `opened_orders()`.

---

## 🎯 Назначение

Используйте для получения простого количества открытых позиций:

* Проверить, есть ли открытые позиции
* Отслеживать количество позиций перед открытием новых сделок
* Реализовать лимиты позиций (максимальное число одновременных позиций)
* Быстрая проверка состояния без загрузки полных данных о позициях
* Эффективно - минимальный объём передаваемых данных

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [positions_total - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_total_HOW.md)**

---

## Сигнатура метода

```python
async def positions_total(
    self,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> trade_functions_pb2.PositionsTotalData
```

**Сообщение запроса:**

```protobuf
message Empty {
  // Параметры не нужны
}
```

**Сообщение ответа:**

```protobuf
message PositionsTotalReply {
  oneof response {
    PositionsTotalData data = 1;
    Error error = 2;
  }
}

message PositionsTotalData {
  int32 total_positions = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `deadline`    | `datetime` (опционально)   | Крайний срок для вызова gRPC (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (опционально) | Событие для отмены операции                   |

**Дополнительных параметров нет** - этот метод возвращает только общее количество.

**Варианты с deadline:**

```python
from datetime import datetime, timedelta, timezone

# 1. С deadline (рекомендуется)
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
result = await account.positions_total(deadline=deadline)

# 2. С событием отмены
cancel_event = asyncio.Event()
result = await account.positions_total(cancellation_event=cancel_event)

# 3. Без deadline (использует таймаут по умолчанию, если настроен)
result = await account.positions_total()
```

---

## ⬆️ Выход - `PositionsTotalData`

| Поле              | Тип     | Тип Python  | Описание                                          |
| ----------------- | ------- | ----------- | ------------------------------------------------- |
| `total_positions` | `int32` | `int`       | Общее количество текущих открытых позиций         |

**Возвращаемое значение:** Метод возвращает объект `PositionsTotalData`, поле `total_positions` доступно как атрибут.

**Доступ к количеству:**

```python
data = await account.positions_total()
count = data.total_positions
print(f"Open positions: {count}")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Все методы `MT5Account` имеют встроенную защиту от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать неограниченно долго (или до истечения таймаута сервера).
* **Облегчённый:** Этот метод возвращает только количество - для полных данных о позициях используйте `opened_orders()`.
* **Требуется подключение:** Перед использованием этого метода нужно вызвать `connect_by_host_port()` или `connect_by_server_name()`.
* **Количество в реальном времени:** Количество отражает текущее состояние на момент вызова.
* **Потокобезопасность:** Все асинхронные методы безопасно вызывать одновременно из нескольких asyncio-задач.
* **Работа с UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не передан. Для явного контроля (например, в сценариях стриминга) передавайте `id_=uuid4()` в конструктор.

---

## 🔗 Примеры использования

### 1) Получить общее количество открытых позиций

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account

async def main():
    # Создание экземпляра счёта
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    # Сначала подключаемся
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Установить deadline
        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

        # Получить общее количество позиций
        data = await account.positions_total(deadline=deadline)

        print(f"Total open positions: {data.total_positions}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Проверить, есть ли открытые позиции

```python
async def has_open_positions(account: MT5Account) -> bool:
    """
    Check if there are any open positions.

    Returns:
        True if there are open positions
    """
    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    data = await account.positions_total(deadline=deadline)

    has_positions = data.total_positions > 0

    if has_positions:
        print(f"[OK] {data.total_positions} position(s) open")
    else:
        print("[OK] No open positions")

    return has_positions

# Использование:
if await has_open_positions(account):
    print("Account has active positions")
else:
    print("Account is flat")
```

### 3) Проверка лимита позиций

```python
async def check_position_limit(account: MT5Account, max_positions: int = 5) -> bool:
    """
    Check if current position count is below limit.

    Args:
        account: MT5Account instance
        max_positions: Maximum allowed open positions

    Returns:
        True if can open more positions
    """
    data = await account.positions_total()

    current = data.total_positions

    if current >= max_positions:
        print(f"[WARNING] Position limit reached: {current}/{max_positions}")
        return False

    remaining = max_positions - current
    print(f"[OK] Can open {remaining} more position(s)")
    return True

# Использование:
if await check_position_limit(account, max_positions=5):
    # Разместить новый ордер
    pass
else:
    print("Cannot open new position - limit reached")
```

### 4) Отслеживать количество позиций

```python
async def monitor_positions(account: MT5Account, interval: float = 5.0):
    """
    Monitor position count every N seconds.

    Args:
        account: MT5Account instance
        interval: Update interval in seconds
    """
    previous_count = None

    while True:
        try:
            deadline = datetime.now(timezone.utc) + timedelta(seconds=3)
            data = await account.positions_total(deadline=deadline)

            count = data.total_positions

            if previous_count is not None and count != previous_count:
                if count > previous_count:
                    print(f"[+] Position opened: {count} total")
                else:
                    print(f"[-] Position closed: {count} total")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Positions: {count}")

            previous_count = count

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Использование:
# await monitor_positions(account, interval=5.0)  # Обновление каждые 5 секунд
```

### 5) Проверка перед сделкой

```python
async def validate_can_trade(account: MT5Account, max_positions: int = 10) -> bool:
    """
    Validate account can accept new positions.

    Args:
        account: MT5Account instance
        max_positions: Maximum concurrent positions allowed

    Returns:
        True if trading is allowed
    """
    # Получить количество позиций
    data = await account.positions_total()
    count = data.total_positions

    # Проверить лимит позиций
    if count >= max_positions:
        print(f"[ERROR] Position limit exceeded: {count}/{max_positions}")
        return False

    print(f"[OK] Current positions: {count}/{max_positions}")
    return True

# Использование:
if await validate_can_trade(account, max_positions=10):
    # Разместить ордер
    pass
else:
    print("Trading blocked - too many positions")
```

### 6) Ожидание закрытия позиций

```python
async def wait_for_all_closed(
    account: MT5Account,
    timeout_seconds: int = 300,
    check_interval: float = 2.0
):
    """
    Wait until all positions are closed.

    Args:
        account: MT5Account instance
        timeout_seconds: Maximum time to wait
        check_interval: How often to check

    Raises:
        TimeoutError: If positions don't close within timeout
    """
    import time
    start_time = time.time()

    print("Waiting for all positions to close...")

    while True:
        # Проверить таймаут
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            data = await account.positions_total()
            raise TimeoutError(
                f"Timeout: {data.total_positions} position(s) still open after {timeout_seconds}s"
            )

        # Получить количество позиций
        data = await account.positions_total()
        count = data.total_positions

        if count == 0:
            print("[OK] All positions closed")
            return

        print(f"[INFO] Waiting... {count} position(s) still open")
        await asyncio.sleep(check_interval)

# Использование:
try:
    await wait_for_all_closed(account, timeout_seconds=300)
except TimeoutError as e:
    print(f"[ERROR] {e}")
```

### 7) Система оповещений о количестве позиций

```python
async def position_alert_system(
    account: MT5Account,
    warning_threshold: int = 8,
    critical_threshold: int = 10,
    interval: float = 10.0
):
    """
    Alert when position count reaches thresholds.

    Args:
        account: MT5Account instance
        warning_threshold: Warn at this count
        critical_threshold: Critical at this count
        interval: Check interval in seconds
    """
    while True:
        try:
            data = await account.positions_total()
            count = data.total_positions

            if count >= critical_threshold:
                print(f"[CRITICAL] {count} positions - at limit!")
            elif count >= warning_threshold:
                print(f"[WARNING] {count} positions - approaching limit")
            else:
                print(f"[OK] {count} positions")

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Использование:
# await position_alert_system(account, warning_threshold=8, critical_threshold=10)
```

### 8) Сравнить количество позиций с целевым

```python
async def compare_with_target(
    account: MT5Account,
    target_positions: int
) -> dict:
    """
    Compare current positions with target.

    Args:
        account: MT5Account instance
        target_positions: Target number of positions

    Returns:
        Dictionary with comparison data
    """
    data = await account.positions_total()
    current = data.total_positions

    difference = current - target_positions

    result = {
        "current": current,
        "target": target_positions,
        "difference": difference,
        "status": "exact" if difference == 0 else "above" if difference > 0 else "below"
    }

    if difference == 0:
        print(f"[OK] Exactly at target: {current} positions")
    elif difference > 0:
        print(f"[INFO] {abs(difference)} above target ({current}/{target_positions})")
    else:
        print(f"[INFO] {abs(difference)} below target ({current}/{target_positions})")

    return result

# Использование:
result = await compare_with_target(account, target_positions=5)
print(f"Status: {result['status']}")
```

---

## Типовые шаблоны

### Быстрая проверка позиций

```python
async def is_flat(account: MT5Account) -> bool:
    """Check if account has no open positions"""
    data = await account.positions_total()
    return data.total_positions == 0
```

### Защита по лимиту позиций

```python
async def can_open_position(
    account: MT5Account,
    max_concurrent: int = 10
) -> bool:
    """Check if can open another position"""
    data = await account.positions_total()
    return data.total_positions < max_concurrent
```

### Проверка рисков перед торговлей

```python
async def pre_trade_risk_check(account: MT5Account) -> bool:
    """Comprehensive risk check before trading"""
    data = await account.positions_total()

    # Не более 10 одновременных позиций
    if data.total_positions >= 10:
        print("[ERROR] Too many open positions")
        return False

    print(f"[OK] Risk check passed ({data.total_positions} positions)")
    return True
```

---

## 📚 См. также

* [opened_orders](./opened_orders.md) - Получить полные данные обо всех открытых ордерах и позициях
* [opened_orders_tickets](./opened_orders_tickets.md) - Получить только ID тикетов (легче, чем opened_orders)
* [positions_history](./positions_history.md) - Получить историю закрытых позиций
