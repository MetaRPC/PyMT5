# Получить суммарную плавающую прибыль (`get_total_profit`)

> **Sugar-метод:** Возвращает суммарную нереализованную прибыль/убыток по всем открытым позициям.

**Информация об API:**

* **Метод:** `sugar.get_total_profit()`
* **Возвращает:** Суммарный плавающий P&L как float
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_total_profit(self) -> float
```

---

## 🔽 Входные параметры

Отсутствуют

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `float` | Суммарная плавающая прибыль/убыток в валюте счёта (положительное = прибыль, отрицательное = убыток) |

---

## 🏛️ Основное

**Что делает:**

- Суммирует прибыль/убыток по всем открытым позициям
- Возвращает суммарный нереализованный P&L
- Возвращает 0.0, если позиций нет
- Рассчитывается в валюте счёта (USD, EUR и т. д.)

**Ключевое поведение:**

- Включает ВСЕ открытые позиции
- Положительное = суммарная прибыль
- Отрицательное = суммарный убыток
- Возвращает 0.0, если позиций нет (не None)
- Только плавающий (нереализованный) P&L

---

## ⚡ Под капотом

```
MT5Sugar.get_total_profit()
    ↓ вызывает
MT5Service.get_opened_orders(sort_mode=0)
    ↓ суммирует все значения pos.profit
    ↓ возвращает сумму
```

**Цепочка вызовов:**

1. Sugar вызывает Service.get_opened_orders()
2. Sugar перебирает position_infos
3. Суммирует pos.profit по каждой позиции
4. Возвращает итоговую сумму

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1377`
- Service: `src/pymt5/mt5_service.py:742`

---

## Когда использовать

**Используйте `get_total_profit()`, когда:**

- Отслеживаете общую результативность счёта
- Управление рисками (закрыть всё, если убыток слишком велик)
- Отслеживание дневной прибыли/убытка
- Лимиты P&L по всему счёту

**Не используйте, когда:**

- Нужна прибыль по конкретному символу (используйте `get_profit_by_symbol()`)
- Нужна реализованная прибыль (используйте методы истории)
- Нужно свойство плавающей прибыли (используйте `get_floating_profit()`)

---

## 🔗 Примеры

### Пример 1: Базовая проверка P&L

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def check_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить суммарную прибыль
    total = await sugar.get_total_profit()

    if total > 0:
        print(f"Total profit: ${total:.2f}")
    elif total < 0:
        print(f"Total loss: ${abs(total):.2f}")
    else:
        print("Breakeven or no positions")
```

### Пример 2: Стоп-лосс для всех позиций

```python
import asyncio

async def stop_loss_monitor():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    max_loss = -100.0  # Закрыть всё, если убыток превысит $100

    while True:
        total_profit = await sugar.get_total_profit()

        print(f"Current P&L: ${total_profit:.2f}")

        if total_profit <= max_loss:
            print(f"Max loss reached (${total_profit:.2f}), closing all positions")
            closed = await sugar.close_all_positions()
            print(f"Closed {closed} positions")
            break

        await asyncio.sleep(5)
```

### Пример 3: Цель по прибыли

```python
async def profit_target():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Открыть несколько позиций
    await sugar.buy_market("EURUSD", volume=0.1)
    await sugar.buy_market("GBPUSD", volume=0.1)

    target_profit = 50.0

    print(f"Monitoring for ${target_profit} total profit...")

    while True:
        total = await sugar.get_total_profit()

        if total >= target_profit:
            print(f"Target reached: ${total:.2f}")

            # Закрыть всё и зафиксировать прибыль
            await sugar.close_all_positions()
            break

        print(f"Current: ${total:.2f} / ${target_profit:.2f}")
        await asyncio.sleep(5)
```

---

## Типичные ошибки

**Ошибка 1: Путаница со свойством floating_profit**
```python
# Оба делают одно и то же, но с разным синтаксисом
total1 = await sugar.get_total_profit()      # Метод
total2 = await sugar.get_floating_profit()   # Тоже метод (Account_Properties)

# Используйте get_floating_profit() из группы Account_Properties
```

**Ошибка 2: Ожидание None вместо 0**
```python
# Возвращает 0.0, если позиций нет, а не None
profit = await sugar.get_total_profit()

if profit:  # 0.0 — ложное значение, но корректное
    print("Have profit/loss")
```

**Решение:** Сравнивайте явно
```python
profit = await sugar.get_total_profit()

if profit != 0.0:
    print(f"P&L: ${profit:.2f}")
else:
    print("No P&L or no positions")
```

**Ошибка 3: Использование для реализованной прибыли**
```python
# ОШИБКА: get_total_profit() показывает только ОТКРЫТЫЕ позиции
# Прибыль по закрытым позициям не включается
profit = await sugar.get_total_profit()
# Это только плавающая (нереализованная) прибыль
```

**Решение:** Используйте методы истории для реализованной прибыли
```python
# Плавающая прибыль (открытые позиции)
floating = await sugar.get_total_profit()

# Реализованная прибыль (закрытые сегодня)
# realized = await sugar.get_profit_today()

print(f"Floating: ${floating:.2f}")
# print(f"Realized: ${realized:.2f}")
```

---

## Полезные советы

**Совет 1: Расчёт процента прибыли**

```python
balance = await sugar.get_balance()
profit = await sugar.get_total_profit()

profit_pct = (profit / balance) * 100

print(f"Floating P&L: ${profit:.2f} ({profit_pct:+.2f}%)")
```

**Совет 2: Сравнение с использованной маржей**
```python
margin = await sugar.get_margin()
profit = await sugar.get_total_profit()

if margin > 0:
    return_on_margin = (profit / margin) * 100
    print(f"Return on margin: {return_on_margin:+.2f}%")
```

**Совет 3: Логирование изменений прибыли**
```python
import asyncio

async def log_profit_changes():
    previous = await sugar.get_total_profit()

    while True:
        await asyncio.sleep(10)

        current = await sugar.get_total_profit()
        change = current - previous

        if abs(change) >= 1.0:  # Логировать, если изменение >= $1
            print(f"P&L changed: ${previous:.2f} → ${current:.2f} "
                  f"({change:+.2f})")
            previous = current
```

---

## 📚 См. также

- [get_profit_by_symbol](get_profit_by_symbol.md) - Прибыль по конкретному символу
- [get_floating_profit](../2.%20Account_Properties/get_floating_profit.md) - То же, что get_total_profit
- [get_open_positions](get_open_positions.md) - Получить все позиции
- [close_all_positions](../6.%20Position_Management/close_all_positions.md) - Закрыть все
