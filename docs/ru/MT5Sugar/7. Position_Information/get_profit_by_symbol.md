# Получить прибыль по символу (`get_profit_by_symbol`)

> **Sugar-метод:** Возвращает суммарную нереализованную прибыль/убыток по конкретному символу.

**Информация об API:**

* **Метод:** `sugar.get_profit_by_symbol(symbol)`
* **Возвращает:** Суммарный плавающий P&L по символу как float
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_profit_by_symbol(self, symbol: str) -> float
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
| `float` | Суммарный плавающий P&L по символу в валюте счёта (положительное = прибыль, отрицательное = убыток) |

---

## 🏛️ Основное

**Что делает:**

- Суммирует прибыль/убыток по всем позициям указанного символа
- Возвращает суммарный нереализованный P&L по этому символу
- Возвращает 0.0, если по символу нет позиций
- Рассчитывается в валюте счёта

**Ключевое поведение:**

- Сопоставление символа чувствительно к регистру
- Включает позиции как BUY, так и SELL
- Возвращает 0.0 при отсутствии подходящих позиций
- Только плавающий (нереализованный) P&L

---

## ⚡ Под капотом

```
MT5Sugar.get_profit_by_symbol()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ фильтрует по символу
    ↓ суммирует pos.profit, где pos.symbol == symbol
    ↓ возвращает сумму
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders()
2. Sugar фильтрует position_infos по символу
3. Суммирует pos.profit для подходящих позиций
4. Возвращает итоговую сумму (0.0 при отсутствии совпадений)

**Связанные файлы:**
- Sugar: `src/pymt5/mt5_sugar.py:1383`
- Service: `src/pymt5/mt5_service.py:742`

---

## Когда использовать

**Используйте `get_profit_by_symbol()`, когда:**

- Отслеживаете результативность по конкретному символу
- Управление рисками на основе символа
- Сравниваете прибыльность по символам
- Стратегии, ориентированные на символ

**Не используйте, когда:**

- Нужна суммарная прибыль по всем символам (используйте `get_total_profit()`)
- Нужна прибыль по конкретной позиции (используйте position.profit)
- Нужна реализованная прибыль (используйте методы истории)

---

## 🔗 Примеры

### Пример 1: Базовый P&L по символу

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def symbol_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить прибыль по EURUSD
    eurusd_profit = await sugar.get_profit_by_symbol("EURUSD")

    if eurusd_profit > 0:
        print(f"EURUSD profit: ${eurusd_profit:.2f}")
    elif eurusd_profit < 0:
        print(f"EURUSD loss: ${abs(eurusd_profit):.2f}")
    else:
        print("EURUSD breakeven or no positions")
```

### Пример 2: Сравнение результативности символов

```python
async def compare_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    print("Symbol Performance:")
    for symbol in symbols:
        profit = await sugar.get_profit_by_symbol(symbol)

        if profit != 0.0:
            status = "profit" if profit > 0 else "loss"
            print(f"  {symbol}: ${profit:+.2f} ({status})")
        else:
            print(f"  {symbol}: no positions")
```

### Пример 3: Стоп-лосс для конкретного символа

```python
import asyncio

async def symbol_stop_loss():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    symbol = "EURUSD"
    max_loss = -50.0  # Закрыть EURUSD, если убыток превысит $50

    # Открыть позиции EURUSD
    await sugar.buy_market(symbol, volume=0.1)

    print(f"Monitoring {symbol} for max loss ${max_loss}...")

    while True:
        profit = await sugar.get_profit_by_symbol(symbol)

        print(f"{symbol} P&L: ${profit:.2f}")

        if profit <= max_loss:
            print(f"Max loss reached, closing all {symbol} positions")

            # Закрыть все позиции по символу
            closed = await sugar.close_all_positions(symbol=symbol)
            print(f"Closed {closed} {symbol} positions")
            break

        await asyncio.sleep(5)
```

---

## Типичные ошибки

**Ошибка 1: Чувствительность символа к регистру**
```python
# ОШИБКА: регистр символа имеет значение
profit = await sugar.get_profit_by_symbol("eurusd")
# Возвращает 0.0, если позиции по "EURUSD"
```

**Решение:** Используйте символы в верхнем регистре
```python
profit = await sugar.get_profit_by_symbol("EURUSD")
```

**Ошибка 2: Ожидание None вместо 0**
```python
# Возвращает 0.0, если позиций нет, а не None
profit = await sugar.get_profit_by_symbol("EURUSD")

if profit:  # 0.0 — ложное значение
    print("Have profit/loss")
```

**Решение:** Сравнивайте явно
```python
profit = await sugar.get_profit_by_symbol("EURUSD")

if profit != 0.0:
    print(f"EURUSD P&L: ${profit:.2f}")
else:
    print("EURUSD flat or no positions")
```

**Ошибка 3: Непроверка наличия позиций**
```python
# Получение прибыли по символу без позиций
profit = await sugar.get_profit_by_symbol("XAUUSD")
# Возвращает 0.0, невозможно различить:
# 1. Нет позиций
# 2. Позиции в безубытке
```

**Решение:** Сначала проверьте количество позиций
```python
count = await sugar.count_open_positions("XAUUSD")

if count > 0:
    profit = await sugar.get_profit_by_symbol("XAUUSD")
    print(f"XAUUSD {count} positions: ${profit:.2f}")
else:
    print("No XAUUSD positions")
```

---

## Полезные советы

**Совет 1: Найти лучший/худший символ по результативности**
```python
# Получить все торгуемые символы
all_positions = await sugar.get_open_positions()
symbols = set(p.symbol for p in all_positions)

# Найти лучший символ
profits = {}
for symbol in symbols:
    profits[symbol] = await sugar.get_profit_by_symbol(symbol)

best_symbol = max(profits, key=profits.get)
worst_symbol = min(profits, key=profits.get)

print(f"Best: {best_symbol} (${profits[best_symbol]:.2f})")
print(f"Worst: {worst_symbol} (${profits[worst_symbol]:.2f})")
```

**Совет 2: Экспозиция по символу вместе с P&L**
```python
async def symbol_exposure(sugar, symbol):
    """Получить полную информацию об экспозиции по символу."""
    count = await sugar.count_open_positions(symbol)
    profit = await sugar.get_profit_by_symbol(symbol)

    positions = await sugar.get_positions_by_symbol(symbol)
    total_volume = sum(p.volume for p in positions)

    return {
        "symbol": symbol,
        "count": count,
        "volume": total_volume,
        "profit": profit
    }

# Использование
exposure = await symbol_exposure(sugar, "EURUSD")
print(f"{exposure['symbol']}: {exposure['count']} pos, "
      f"{exposure['volume']} lots, ${exposure['profit']:.2f}")
```

**Совет 3: Закрыть символ, если он убыточен**
```python
async def close_losing_symbols(sugar, max_loss=-20.0):
    """Закрыть позиции по символам с убытком > порога."""
    all_positions = await sugar.get_open_positions()
    symbols = set(p.symbol for p in all_positions)

    for symbol in symbols:
        profit = await sugar.get_profit_by_symbol(symbol)

        if profit < max_loss:
            closed = await sugar.close_all_positions(symbol=symbol)
            print(f"Closed {closed} {symbol} positions (loss: ${profit:.2f})")
```

---

## 📚 См. также

- [get_total_profit](get_total_profit.md) - Суммарная прибыль по всем символам
- [get_positions_by_symbol](get_positions_by_symbol.md) - Получить позиции по символу
- [count_open_positions](count_open_positions.md) - Подсчёт по символу
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Закрыть все по символу
