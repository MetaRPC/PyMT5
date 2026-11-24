# Получить позицию по тикету (`get_position_by_ticket`)

> **Sugar-метод:** Возвращает конкретную позицию по номеру тикета.

**Информация об API:**

* **Метод:** `sugar.get_position_by_ticket(ticket)`
* **Возвращает:** Объект позиции или `None`, если не найдена
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_position_by_ticket(self, ticket: int)
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `ticket` | `int` | Да | - | Номер тикета позиции для поиска |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `PositionInfo \| None` | Объект позиции, если найдена, `None`, если не найдена |

---

## 🏛️ Основное

**Что делает:**

- Ищет позицию с конкретным номером тикета
- Возвращает полную информацию о позиции, если найдена
- Возвращает `None`, если позиция не найдена
- Ищет среди всех открытых позиций

**Ключевое поведение:**

- Возвращает None (не исключение), если не найдена
- Ищет только среди открытых позиций (не закрытых)
- Возвращает первое совпадение (тикеты уникальны)
- Полный объект позиции со всеми полями

---

## ⚡ Под капотом

```
MT5Sugar.get_position_by_ticket()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ перебирает position_infos
    ↓ сопоставляет ticket
    ↓ возвращает позицию или None
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders()
2. Sugar перебирает список position_infos
3. Сравнивает каждый pos.ticket с целевым тикетом
4. Возвращает объект позиции при совпадении
5. Возвращает None, если совпадение не найдено

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1343`
- Service: `src/pymt5/mt5_service.py:742`

---

## Когда использовать

**Используйте `get_position_by_ticket()`, когда:**

- Нужны детали конкретной позиции
- Есть номер тикета из предыдущей операции
- Проверяете, открыта ли ещё конкретная позиция
- Отслеживаете конкретную сделку

**Не используйте, когда:**

- Нужны все позиции (используйте `get_open_positions()`)
- Проверяете только наличие (используйте `has_open_position()`)
- Нужны позиции по символу (используйте `get_positions_by_symbol()`)

---

## 🔗 Примеры

### Пример 1: Проверка статуса позиции

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_position():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Открыть позицию
    ticket = await sugar.buy_market(volume=0.1)
    print(f"Opened position #{ticket}")

    # Позже: получить детали позиции
    position = await sugar.get_position_by_ticket(ticket)

    if position:
        print(f"Position found:")
        print(f"  Symbol: {position.symbol}")
        print(f"  Volume: {position.volume}")
        print(f"  Profit: ${position.profit:.2f}")
    else:
        print(f"Position #{ticket} not found (already closed?)")
```

### Пример 2: Мониторинг позиции до достижения цели

```python
import asyncio

async def monitor_until_target():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Открыть позицию
    ticket = await sugar.buy_market(volume=0.1)
    target_profit = 50.0

    print(f"Monitoring position #{ticket} until ${target_profit} profit")

    while True:
        position = await sugar.get_position_by_ticket(ticket)

        if position is None:
            print("Position closed (SL/TP hit or manually closed)")
            break

        print(f"Current profit: ${position.profit:.2f}")

        if position.profit >= target_profit:
            print("Target reached, closing position")
            await sugar.close_position(ticket)
            break

        await asyncio.sleep(5)
```

### Пример 3: Проверка нескольких позиций

```python
async def verify_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Открыть несколько позиций
    tickets = []
    for _ in range(3):
        ticket = await sugar.buy_market(volume=0.01)
        tickets.append(ticket)

    # Позже: проверить, что все ещё открыты
    still_open = []
    closed = []

    for ticket in tickets:
        position = await sugar.get_position_by_ticket(ticket)

        if position:
            still_open.append(ticket)
        else:
            closed.append(ticket)

    print(f"Still open: {len(still_open)}")
    print(f"Closed: {len(closed)}")
```

---

## Типичные ошибки

**Ошибка 1: Непроверка на None**
```python
# ОШИБКА: падает, если позиция закрыта
position = await sugar.get_position_by_ticket(ticket)
profit = position.profit  # AttributeError, если None
```

**Решение:** Всегда проверяйте на None
```python
position = await sugar.get_position_by_ticket(ticket)

if position:
    profit = position.profit
else:
    print("Position not found")
```

**Ошибка 2: Использование неправильного тикета**
```python
# Тикет из размещения ордера (отложенный ордер)
order_ticket = await sugar.buy_limit(price=1.0840)

# ОШИБКА: тикет отложенного ордера != тикет позиции
position = await sugar.get_position_by_ticket(order_ticket)
# Возвращает None, пока ордер не исполнится
```

**Решение:** Различайте тикеты ордеров и позиций
```python
# Когда лимитный ордер исполняется, он становится позицией с ТЕМ ЖЕ тикетом
order_ticket = await sugar.buy_limit(price=1.0840)

# Дождитесь исполнения ордера...
# После чего он становится позицией
position = await sugar.get_position_by_ticket(order_ticket)
```

**Ошибка 3: Повторные вызовы в плотном цикле**
```python
# Неэффективно: повторное получение всех позиций
while True:
    pos = await sugar.get_position_by_ticket(ticket)
    # Получает ВСЕ позиции на каждой итерации
    await asyncio.sleep(0.1)  # 10 раз в секунду!
```

**Решение:** Используйте разумный интервал опроса
```python
while True:
    pos = await sugar.get_position_by_ticket(ticket)
    await asyncio.sleep(5)  # Раз в 5 секунд
```

---

## Полезные советы

**Совет 1: Кэширование данных позиции**

```python
# Избегайте повторных запросов
position = await sugar.get_position_by_ticket(ticket)

if position:
    # Использовать кэшированные данные для нескольких операций
    symbol = position.symbol
    volume = position.volume
    profit = position.profit

    print(f"{symbol}: {volume} lots = ${profit:.2f}")
```

**Совет 2: Отслеживание позиции в ходе операций**
```python
# Открыть и отслеживать позицию
ticket = await sugar.buy_market(volume=0.1)
entry_price = (await sugar.get_position_by_ticket(ticket)).price_open

# Спустя некоторое время
position = await sugar.get_position_by_ticket(ticket)

if position:
    pips_moved = (position.price_current - entry_price) / 0.0001
    print(f"Moved {pips_moved:.1f} pips from entry")
```

**Совет 3: Пакетная проверка нескольких тикетов**

```python
async def check_tickets(sugar, tickets):
    """Эффективно проверить несколько тикетов."""
    # Получить все позиции один раз
    all_positions = await sugar.get_open_positions()
    ticket_set = set(tickets)

    # Фильтровать в памяти
    found = [p for p in all_positions if p.ticket in ticket_set]

    return found

# Использование
tickets = [123456, 123457, 123458]
positions = await check_tickets(sugar, tickets)
print(f"Found {len(positions)} of {len(tickets)} positions")
```

---

## 📚 См. также

- [get_open_positions](get_open_positions.md) - Получить все позиции
- [get_positions_by_symbol](get_positions_by_symbol.md) - Фильтровать по символу
- [has_open_position](has_open_position.md) - Проверить наличие позиций
- [close_position](../6.%20Position_Management/close_position.md) - Закрыть позицию
