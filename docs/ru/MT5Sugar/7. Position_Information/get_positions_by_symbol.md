# Получить позиции по символу (`get_positions_by_symbol`)

> **Sugar-метод:** Возвращает все позиции по конкретному символу.

**Информация об API:**

* **Метод:** `sugar.get_positions_by_symbol(symbol)`
* **Возвращает:** Список позиций по символу (может быть пустым)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_positions_by_symbol(self, symbol: str)
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `symbol` | `str` | Да | - | Торговый символ (например, "EURUSD") |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `list[PositionInfo]` | Список позиций по символу (пустой список, если их нет) |

---

## 🏛️ Основное

**Что делает:**

- Фильтрует все открытые позиции по символу
- Возвращает список подходящих позиций
- Возвращает пустой список при отсутствии совпадений
- Сопоставление символа чувствительно к регистру

**Ключевое поведение:**

- Возвращает список (может быть пустым)
- Требуется точное совпадение символа
- Включает позиции как BUY, так и SELL
- Поддерживаются несколько позиций по одному символу

---

## ⚡ Под капотом

```
MT5Sugar.get_positions_by_symbol()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ фильтрует position_infos
    ↓ pos.symbol == symbol
    ↓ возвращает отфильтрованный список
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders()
2. Sugar фильтрует position_infos по символу
3. Возвращает список подходящих позиций
4. Возвращает пустой список при отсутствии совпадений

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1353`
- Service: `src/pymt5/mt5_service.py:742`

---

## Когда использовать

**Используйте `get_positions_by_symbol()`, когда:**

- Управляете позициями по конкретному символу
- Рассчитываете экспозицию по конкретному символу
- Закрываете все позиции по символу
- Стратегии, ориентированные на символ

**Не используйте, когда:**

- Нужны все позиции (используйте `get_open_positions()`)
- Нужно только количество (используйте `count_open_positions(symbol)`)
- Проверяете только наличие (используйте `has_open_position(symbol)`)

---

## 🔗 Примеры

### Пример 1: Получить позиции EURUSD

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def eurusd_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить все позиции EURUSD
    eurusd_positions = await sugar.get_positions_by_symbol("EURUSD")

    if not eurusd_positions:
        print("No EURUSD positions")
    else:
        print(f"EURUSD positions: {len(eurusd_positions)}")

        for pos in eurusd_positions:
            direction = "BUY" if pos.type == 0 else "SELL"
            print(f"  #{pos.ticket}: {direction} {pos.volume} lots, "
                  f"${pos.profit:.2f}")

# Вывод:
# EURUSD positions: 2
#   #123456: BUY 0.1 lots, $12.50
#   #123457: SELL 0.05 lots, -$3.20
```

### Пример 2: Закрыть все позиции по символу

```python
async def close_symbol_positions():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "GBPUSD"

    # Получить все позиции GBPUSD
    positions = await sugar.get_positions_by_symbol(symbol)

    print(f"Closing {len(positions)} {symbol} positions...")

    closed = 0
    for pos in positions:
        success = await sugar.close_position(pos.ticket)

        if success:
            closed += 1
            print(f"Closed #{pos.ticket}")

    print(f"Closed {closed}/{len(positions)} positions")
```

### Пример 3: Анализ экспозиции по символу

```python
async def symbol_exposure():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    positions = await sugar.get_positions_by_symbol(symbol)

    if positions:
        # Рассчитать чистую экспозицию
        buy_volume = sum(p.volume for p in positions if p.type == 0)
        sell_volume = sum(p.volume for p in positions if p.type == 1)
        net_volume = buy_volume - sell_volume

        # Рассчитать P&L
        total_profit = sum(p.profit for p in positions)

        print(f"{symbol} Exposure:")
        print(f"  BUY: {buy_volume} lots")
        print(f"  SELL: {sell_volume} lots")
        print(f"  NET: {net_volume:+.2f} lots")
        print(f"  P&L: ${total_profit:.2f}")
```

---

## Типичные ошибки

**Ошибка 1: Чувствительность к регистру**
```python
# ОШИБКА: регистр символа имеет значение
positions = await sugar.get_positions_by_symbol("eurusd")
# Возвращает [], если позиции по "EURUSD"
```

**Решение:** Используйте имена символов в верхнем регистре
```python
positions = await sugar.get_positions_by_symbol("EURUSD")
# или
symbol = "eurusd".upper()
positions = await sugar.get_positions_by_symbol(symbol)
```

**Ошибка 2: Предположение, что список никогда не пуст**
```python
# ОШИБКА: падает, если позиций нет
positions = await sugar.get_positions_by_symbol("EURUSD")
first = positions[0]  # IndexError, если пусто
```

**Решение:** Проверяйте, не пуст ли список
```python
positions = await sugar.get_positions_by_symbol("EURUSD")

if positions:
    first = positions[0]
else:
    print("No EURUSD positions")
```

**Ошибка 3: Изменение во время итерации**
```python
# ОШИБКА: закрытие позиций во время итерации
positions = await sugar.get_positions_by_symbol("EURUSD")

for pos in positions:
    await sugar.close_position(pos.ticket)
    # Список не обновится во время итерации
```

**Решение:** Сначала соберите тикеты
```python
positions = await sugar.get_positions_by_symbol("EURUSD")
tickets = [p.ticket for p in positions]

for ticket in tickets:
    await sugar.close_position(ticket)
```

---

## Полезные советы

**Совет 1: Рассчитать чистую позицию**
```python
positions = await sugar.get_positions_by_symbol("EURUSD")

# Рассчитать чистую экспозицию (BUY - SELL)
net = sum(
    p.volume if p.type == 0 else -p.volume
    for p in positions
)

if net > 0:
    print(f"Net LONG: {net} lots")
elif net < 0:
    print(f"Net SHORT: {abs(net)} lots")
else:
    print("Flat (hedged)")
```

**Совет 2: Найти крупнейшую позицию**
```python
positions = await sugar.get_positions_by_symbol("EURUSD")

if positions:
    largest = max(positions, key=lambda p: p.volume)
    print(f"Largest position: #{largest.ticket} ({largest.volume} lots)")
```

**Совет 3: Проверить все символы сразу**
```python
async def analyze_all_symbols(sugar):
    """Проанализировать экспозицию по всем торгуемым символам."""
    all_positions = await sugar.get_open_positions()

    # Сгруппировать по символу
    symbols = set(p.symbol for p in all_positions)

    for symbol in symbols:
        symbol_positions = await sugar.get_positions_by_symbol(symbol)

        total_volume = sum(p.volume for p in symbol_positions)
        total_profit = sum(p.profit for p in symbol_positions)

        print(f"{symbol}: {len(symbol_positions)} pos, "
              f"{total_volume} lots, ${total_profit:.2f}")
```

---

## 📚 См. также

- [get_open_positions](get_open_positions.md) - Получить все позиции
- [get_position_by_ticket](get_position_by_ticket.md) - Получить конкретную позицию
- [count_open_positions](count_open_positions.md) - Подсчёт по символу
- [get_profit_by_symbol](get_profit_by_symbol.md) - Прибыль по символу
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Закрыть все по символу
