# Получить все открытые позиции (`get_open_positions`)

> **Sugar-метод:** Возвращает список всех текущих открытых позиций.

**Информация об API:**

* **Метод:** `sugar.get_open_positions()`
* **Возвращает:** Список объектов позиций
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_open_positions(self)
```

---

## 🔽 Входные параметры

Отсутствуют

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `list[PositionInfo]` | Список всех открытых позиций (пустой список, если их нет) |

---

## 🏛️ Основное

**Что делает:**

- Получает все текущие открытые позиции из терминала
- Возвращает их в виде списка Python
- Каждая позиция содержит полную информацию (ticket, symbol, volume, profit и т. д.)
- Возвращает пустой список, если открытых позиций нет

**Ключевое поведение:**

- Возвращает реальные объекты позиций (не сводку)
- Список может быть пустым (нет позиций)
- Каждая позиция имеет: ticket, symbol, type, volume, price_open, profit, sl, tp и т. д.
- Сортируется по режиму сортировки по умолчанию (0)

---

## ⚡ Под капотом

```
MT5Sugar.get_open_positions()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ вызывает
MT5Account.opened_orders()
    ↓ gRPC protobuf
TradingHelperService.OpenedOrders()
    ↓ терминал MT5
    ↓ возвращает список position_infos
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders() с sort_mode=0
2. Service перенаправляет в Account.opened_orders()
3. Account отправляет gRPC-запрос в терминал
4. Терминал возвращает все открытые позиции
5. Sugar преобразует position_infos в список Python
6. Возвращает список (может быть пустым)

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1338`
- Service: `src/pymt5/mt5_service.py:742`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1316`

---

## Когда использовать

**Используйте `get_open_positions()`, когда:**

- Нужно перебрать все позиции
- Проверяете детали позиций
- Строите собственные фильтры позиций
- Отслеживаете все активные сделки

**Не используйте, когда:**

- Нужно только количество позиций (используйте `count_open_positions()`)
- Проверяете только наличие позиций (используйте `has_open_position()`)
- Нужна только конкретная позиция (используйте `get_position_by_ticket()`)

---

## 🔗 Примеры

### Пример 1: Вывод списка всех позиций

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def list_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить все позиции
    positions = await sugar.get_open_positions()

    if not positions:
        print("No open positions")
    else:
        print(f"Open positions: {len(positions)}")

        for pos in positions:
            print(f"#{pos.ticket}: {pos.symbol} {pos.volume} lots, "
                  f"Profit: ${pos.profit:.2f}")

# Вывод:
# Open positions: 3
# #123456: EURUSD 0.1 lots, Profit: $12.50
# #123457: GBPUSD 0.05 lots, Profit: -$5.30
# #123458: USDJPY 0.2 lots, Profit: $25.80
```

### Пример 2: Расчёт статистики

```python
async def position_statistics():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    positions = await sugar.get_open_positions()

    if positions:
        # Рассчитать статистику
        total_volume = sum(pos.volume for pos in positions)
        total_profit = sum(pos.profit for pos in positions)
        profitable = sum(1 for pos in positions if pos.profit > 0)
        losing = sum(1 for pos in positions if pos.profit < 0)

        print(f"Total positions: {len(positions)}")
        print(f"Total volume: {total_volume} lots")
        print(f"Total profit: ${total_profit:.2f}")
        print(f"Profitable: {profitable}, Losing: {losing}")
```

### Пример 3: Закрыть все прибыльные позиции

```python
async def close_profitable():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    positions = await sugar.get_open_positions()

    closed_count = 0
    for pos in positions:
        if pos.profit > 0:
            success = await sugar.close_position(pos.ticket)

            if success:
                closed_count += 1
                print(f"Closed #{pos.ticket} with ${pos.profit:.2f} profit")

    print(f"Closed {closed_count} profitable positions")
```

---

## Типичные ошибки

**Ошибка 1: Предположение, что список позиций никогда не пуст**
```python
# ОШИБКА: падает, если позиций нет
positions = await sugar.get_open_positions()
first_position = positions[0]  # IndexError, если пусто
```

**Решение:** Всегда проверяйте, не пуст ли список
```python
positions = await sugar.get_open_positions()

if positions:
    first_position = positions[0]
else:
    print("No positions open")
```

**Ошибка 2: Изменение во время итерации**
```python
# ОШИБКА: изменение списка во время итерации
positions = await sugar.get_open_positions()

for pos in positions:
    await sugar.close_position(pos.ticket)
    # Список может измениться во время итерации
```

**Решение:** Итерируйте по копии или сначала соберите тикеты
```python
positions = await sugar.get_open_positions()
tickets = [pos.ticket for pos in positions]

for ticket in tickets:
    await sugar.close_position(ticket)
```

**Ошибка 3: Необработка типов позиций**
```python
# Все позиции трактуются как BUY
for pos in positions:
    # pos.type может быть SELL!
    pass
```

**Решение:** Проверяйте тип позиции
```python
for pos in positions:
    if pos.type == 0:  # BUY
        print(f"BUY position: {pos.symbol}")
    else:  # SELL
        print(f"SELL position: {pos.symbol}")
```

---

## Полезные советы

**Совет 1: Фильтрация по нескольким критериям**
```python
positions = await sugar.get_open_positions()

# Получить крупные прибыльные позиции по EUR
eur_profitable = [
    pos for pos in positions
    if 'EUR' in pos.symbol
    and pos.profit > 0
    and pos.volume >= 0.1
]

print(f"Found {len(eur_profitable)} large profitable EUR positions")
```

**Совет 2: Группировка по символу**
```python
from collections import defaultdict

positions = await sugar.get_open_positions()

# Сгруппировать позиции по символу
by_symbol = defaultdict(list)
for pos in positions:
    by_symbol[pos.symbol].append(pos)

for symbol, symbol_positions in by_symbol.items():
    total_volume = sum(p.volume for p in symbol_positions)
    total_profit = sum(p.profit for p in symbol_positions)
    print(f"{symbol}: {len(symbol_positions)} pos, "
          f"{total_volume} lots, ${total_profit:.2f}")
```

**Совет 3: Сортировка по прибыли**

```python
positions = await sugar.get_open_positions()

# Сортировка по прибыли (по убыванию)
sorted_positions = sorted(positions, key=lambda p: p.profit, reverse=True)

print("Best performers:")
for pos in sorted_positions[:3]:
    print(f"#{pos.ticket}: ${pos.profit:.2f}")
```

---

## 📚 См. также

- [get_position_by_ticket](get_position_by_ticket.md) - Получить конкретную позицию
- [get_positions_by_symbol](get_positions_by_symbol.md) - Фильтровать по символу
- [count_open_positions](count_open_positions.md) - Получить количество позиций
- [has_open_position](has_open_position.md) - Проверить наличие позиций
