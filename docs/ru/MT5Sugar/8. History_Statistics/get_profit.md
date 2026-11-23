# Получить историческую прибыль (`get_profit`)

> **Sugar-метод:** Рассчитывает суммарную реализованную прибыль/убыток за указанный период времени.

**Информация об API:**

* **Метод:** `sugar.get_profit(period, from_date, to_date)`
* **Возвращает:** Суммарную прибыль как float
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_profit(
    self,
    period: Period = Period.TODAY,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> float
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `period` | `Period` | Нет | `Period.TODAY` | Перечисление периода (TODAY, YESTERDAY, THIS_WEEK, THIS_MONTH, CUSTOM) |
| `from_date` | `Optional[date]` | Нет | `None` | Начальная дата (обязательна, если period=CUSTOM) |
| `to_date` | `Optional[date]` | Нет | `None` | Конечная дата (обязательна, если period=CUSTOM) |

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `float` | Суммарная реализованная прибыль/убыток в валюте счёта (положительное = прибыль, отрицательное = убыток) |

---

## 🏛️ Основное

**Что делает:**

- Получает закрытые позиции за период
- Суммирует поле profit по всем сделкам
- Возвращает суммарный реализованный P&L
- Возвращает 0.0, если сделок нет

**Ключевое поведение:**

- Только закрытые позиции (реализованная прибыль)
- Включает как прибыли, так и убытки
- НЕ вычитает комиссию/своп (используйте `get_daily_stats` для чистой суммы)
- Возвращает 0.0, если сделок нет (не None)

---

## ⚡ Под капотом

```
MT5Sugar.get_profit()
    ↓ вызывает
MT5Sugar.get_deals(period, from_date, to_date)
    ↓ суммирует order.profit по всем сделкам
    ↓ возвращает сумму
```

**Цепочка вызовов:**

1. Sugar вызывает get_deals() для получения позиций
2. Sugar суммирует поле order.profit по всем позициям
3. Возвращает итоговую сумму

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1473`
- Вызывает get_deals: `src/pymt5/mt5_sugar.py:1437`

---

## Удобные методы

Все эти методы внутренне вызывают `get_profit()` с разными периодами:

```python
# Прибыль за сегодня
profit = await sugar.get_profit_today()
# То же, что: await sugar.get_profit(Period.TODAY)

# Прибыль за эту неделю (с понедельника по сегодня)
profit = await sugar.get_profit_this_week()
# То же, что: await sugar.get_profit(Period.THIS_WEEK)

# Прибыль за этот месяц
profit = await sugar.get_profit_this_month()
# То же, что: await sugar.get_profit(Period.THIS_MONTH)

# Произвольный диапазон дат
profit = await sugar.get_profit(Period.CUSTOM, date(2024, 1, 1), date(2024, 1, 31))
```

---

## Когда использовать

**Используйте `get_profit()`, когда:**

- Быстрая проверка прибыли за период
- Отслеживание дневной/недельной/месячной результативности
- Сравнение прибыльности по периодам
- Отчёты о результативности

**Не используйте, когда:**

- Нужны детали сделок (используйте `get_deals()`)
- Нужна разбивка по комиссии/свопу (используйте `get_daily_stats()`)
- Нужна плавающая прибыль (используйте `get_total_profit()`)

---

## 🔗 Примеры

### Пример 1: Результативность за сегодня

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account
from pymt5.constants import Period

async def daily_profit():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить прибыль за сегодня
    profit = await sugar.get_profit(Period.TODAY)
    # Или: profit = await sugar.get_profit_today()

    if profit > 0:
        print(f"Today's profit: ${profit:.2f}")
    elif profit < 0:
        print(f"Today's loss: ${abs(profit):.2f}")
    else:
        print("Breakeven or no trades today")

# Вывод:
# Today's profit: $125.50
```

### Пример 2: Отслеживание недельного прогресса

```python
async def weekly_progress():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить прибыль за эту неделю
    weekly = await sugar.get_profit_this_week()

    # Получить баланс для расчёта процента
    balance = await sugar.get_balance()
    weekly_pct = (weekly / balance) * 100

    print(f"This Week's Performance:")
    print(f"  Profit: ${weekly:.2f}")
    print(f"  Return: {weekly_pct:+.2f}%")
```

### Пример 3: Сравнение месяцев

```python
from datetime import date

async def compare_months():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Сравнить последние 3 месяца
    months = [
        ("January", date(2024, 1, 1), date(2024, 1, 31)),
        ("February", date(2024, 2, 1), date(2024, 2, 29)),
        ("March", date(2024, 3, 1), date(2024, 3, 31))
    ]

    print("Monthly Performance:")
    for name, start, end in months:
        profit = await sugar.get_profit(Period.CUSTOM, start, end)
        print(f"  {name}: ${profit:+.2f}")

# Вывод:
# Monthly Performance:
#   January: $+250.30
#   February: $-45.20
#   March: $+180.50
```

---

## Типичные ошибки

**Ошибка 1: Путаница с плавающей прибылью**
```python
# get_profit() = РЕАЛИЗОВАННАЯ прибыль (закрытые позиции)
realized = await sugar.get_profit_today()

# get_total_profit() = ПЛАВАЮЩАЯ прибыль (открытые позиции)
floating = await sugar.get_total_profit()

# Это разные вещи!
print(f"Realized: ${realized:.2f}")
print(f"Floating: ${floating:.2f}")
```

**Ошибка 2: Ожидание None вместо 0**
```python
# Возвращает 0.0, если сделок нет, а не None
profit = await sugar.get_profit_today()

if profit:  # 0.0 — ложное значение, но корректное
    print("Made profit/loss")
```

**Решение:** Сравнивайте явно
```python
profit = await sugar.get_profit_today()

if profit > 0:
    print(f"Profit: ${profit:.2f}")
elif profit < 0:
    print(f"Loss: ${abs(profit):.2f}")
else:
    print("No trades or breakeven")
```

**Ошибка 3: Неучёт комиссии/свопа**
```python
# get_profit() суммирует только поле order.profit
# Не вычитает комиссию и своп отдельно
profit = await sugar.get_profit_today()
# Это валовая прибыль, а не чистая
```

**Решение:** Используйте get_daily_stats для разбивки
```python
stats = await sugar.get_daily_stats()
print(f"Gross profit: ${stats.total_profit:.2f}")
print(f"Commission: ${stats.total_commission:.2f}")
print(f"Swap: ${stats.total_swap:.2f}")
print(f"Net profit: ${stats.net_profit:.2f}")
```

---

## Полезные советы

**Совет 1: Дневная цель по прибыли**
```python
# Установить дневную цель по прибыли
daily_target = 100.0

profit = await sugar.get_profit_today()

if profit >= daily_target:
    print(f"Target reached: ${profit:.2f}")

    # Прекратить торговлю на сегодня
    await sugar.close_all_positions()
```

**Совет 2: Сравнение сегодня и вчера**
```python
today = await sugar.get_profit_today()
yesterday = await sugar.get_profit(Period.YESTERDAY)

change = today - yesterday
print(f"Today: ${today:.2f}")
print(f"Yesterday: ${yesterday:.2f}")
print(f"Change: ${change:+.2f}")
```

**Совет 3: Прибыль по дням недели**
```python
from datetime import date, timedelta

async def profit_by_weekday():
    """Рассчитать среднюю прибыль по дням недели."""
    from collections import defaultdict

    # Получить данные за последний месяц
    today = date.today()
    start = today.replace(day=1)

    deals = await sugar.get_deals(Period.CUSTOM, start, today)

    by_weekday = defaultdict(list)
    for deal in deals:
        weekday = deal.time_open.weekday()  # 0=Пн, 6=Вс
        by_weekday[weekday].append(deal.profit)

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i, day in enumerate(days):
        if by_weekday[i]:
            avg = sum(by_weekday[i]) / len(by_weekday[i])
            print(f"{day}: ${avg:.2f} avg")
```

---

## 📚 См. также

- [get_deals](get_deals.md) - Получить исторические сделки (позиции)
- [get_daily_stats](get_daily_stats.md) - Полная дневная статистика с комиссией/свопом
- [get_total_profit](../7.%20Position_Information/get_total_profit.md) - Плавающая прибыль (открытые позиции)
