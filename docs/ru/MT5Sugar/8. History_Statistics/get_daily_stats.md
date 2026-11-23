# Получить дневную статистику (`get_daily_stats`)

> **Sugar-метод:** Возвращает полную торговую статистику за конкретный день.

**Информация об API:**

* **Метод:** `sugar.get_daily_stats(target_date)`
* **Возвращает:** Dataclass `DailyStats` с полной статистикой
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_daily_stats(self, target_date: Optional[date] = None) -> DailyStats
```

---

## 🔽 Входные параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|-----------|------|----------|---------|-------------|
| `target_date` | `Optional[date]` | Нет | `None` | Дата, за которую нужна статистика (None = сегодня) |

---

## Возвращаемое значение

Dataclass `DailyStats` со следующими полями:

| Поле | Тип | Описание |
|-------|------|-------------|
| `date` | `date` | Дата этой статистики |
| `deals_count` | `int` | Количество закрытых позиций |
| `profit` | `float` | Суммарная валовая прибыль/убыток |
| `commission` | `float` | Суммарная уплаченная комиссия |
| `swap` | `float` | Суммарный своп (перенос) |
| `volume` | `float` | Суммарный торгуемый объём в лотах |

**Вычисляемое поле:**

- `net_profit = profit + commission + swap` (вычисляется вручную)

---

## 🏛️ Основное

**Что делает:**

- Получает все закрытые позиции за указанный день
- Рассчитывает полную статистику
- Возвращает структурированный объект DailyStats
- Включает разбивку по комиссии и свопу

**Ключевое поведение:**

- По умолчанию берёт сегодняшний день, если дата не указана
- Получает до 10 000 позиций
- Комиссия обычно отрицательная
- Своп может быть положительным или отрицательным
- Возвращает статистику даже при отсутствии сделок (все нули)

---

## ⚡ Под капотом

```
MT5Sugar.get_daily_stats()
    ↓ преобразует date в диапазон datetime
    ↓ вызывает
MT5Service.get_positions_history()
    ↓ перебирает позиции
    ↓ суммирует profit, commission, swap, volume
    ↓ возвращает dataclass DailyStats
```

**Цепочка вызовов:**

1. Sugar преобразует date в диапазон datetime (00:00:00 — 23:59:59)
2. Sugar вызывает Service.get_positions_history() за день
3. Sugar перебирает history_positions
4. Sugar суммирует: profit, commission, swap, volume
5. Возвращает dataclass DailyStats с результатами

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:2061`
- DailyStats: `src/pymt5/mt5_sugar.py:209`
- Service: `src/pymt5/mt5_service.py:810`

---

## Когда использовать

**Используйте `get_daily_stats()`, когда:**

- Нужна полная дневная разбивка
- Отслеживаете расходы на комиссию
- Анализируете чистую прибыль после комиссий
- Отчёты о дневной результативности
- Анализ объёма

**Не используйте, когда:**

- Нужна только валовая прибыль (используйте `get_profit()`)
- Нужны детали сделок (используйте `get_deals()`)
- Нужна статистика за несколько дней (вызывайте несколько раз)

---

## 🔗 Примеры

### Пример 1: Полная статистика за сегодня

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def daily_report():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить статистику за сегодня
    stats = await sugar.get_daily_stats()

    # Рассчитать чистую прибыль
    net_profit = stats.profit + stats.commission + stats.swap

    print(f"Daily Report for {stats.date}:")
    print(f"  Trades: {stats.deals_count}")
    print(f"  Volume: {stats.volume} lots")
    print(f"  Gross Profit: ${stats.profit:.2f}")
    print(f"  Commission: ${stats.commission:.2f}")
    print(f"  Swap: ${stats.swap:.2f}")
    print(f"  Net Profit: ${net_profit:.2f}")

# Вывод:
# Daily Report for 2026-02-03:
#   Trades: 12
#   Volume: 1.5 lots
#   Gross Profit: $180.50
#   Commission: $-15.30
#   Swap: $-2.10
#   Net Profit: $163.10
```

### Пример 2: Сравнение нескольких дней

```python
from datetime import date, timedelta

async def compare_days():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить последние 5 дней
    print("Last 5 Days Performance:")

    for i in range(5):
        target = date.today() - timedelta(days=i)
        stats = await sugar.get_daily_stats(target)

        net = stats.profit + stats.commission + stats.swap

        print(f"{target}: {stats.deals_count} trades, "
              f"${net:+.2f} net P&L")

# Вывод:
# Last 5 Days Performance:
# 2026-02-03: 12 trades, $+163.10 net P&L
# 2026-02-02: 8 trades, $-45.20 net P&L
# 2026-02-01: 15 trades, $+220.50 net P&L
```

### Пример 3: Анализ издержек

```python
async def cost_analysis():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    stats = await sugar.get_daily_stats()

    if stats.deals_count > 0:
        # Рассчитать издержки на сделку
        avg_commission = abs(stats.commission) / stats.deals_count
        total_costs = abs(stats.commission) + abs(stats.swap)
        costs_pct = (total_costs / abs(stats.profit)) * 100 if stats.profit != 0 else 0

        print(f"Cost Analysis:")
        print(f"  Average commission per trade: ${avg_commission:.2f}")
        print(f"  Total trading costs: ${total_costs:.2f}")
        print(f"  Costs as % of gross profit: {costs_pct:.1f}%")
```

---

## Типичные ошибки

**Ошибка 1: Забыть, что комиссия отрицательная**
```python
stats = await sugar.get_daily_stats()

# ОШИБКА: комиссия уже отрицательная, не вычитайте её повторно
net_profit = stats.profit - stats.commission  # НЕВЕРНО!

# ВЕРНО: комиссия отрицательная, поэтому её нужно прибавить
net_profit = stats.profit + stats.commission  # ВЕРНО
```

**Ошибка 2: Непроверка deals_count**
```python
stats = await sugar.get_daily_stats()

# Расчёт среднего без проверки на ноль
avg_profit = stats.profit / stats.deals_count  # ZeroDivisionError, если сделок нет
```

**Решение:** Всегда сначала проверяйте deals_count
```python
stats = await sugar.get_daily_stats()

if stats.deals_count > 0:
    avg_profit = stats.profit / stats.deals_count
else:
    avg_profit = 0.0
```

**Ошибка 3: Ожидание, что исторические данные существуют**
```python
# Запрос даты до создания счёта
stats = await sugar.get_daily_stats(date(2020, 1, 1))
# Возвращает все нули, а не ошибку
```

**Решение:** Проверяйте наличие данных
```python
stats = await sugar.get_daily_stats(date(2020, 1, 1))

if stats.deals_count == 0:
    print("No trades on this date")
```

---

## Полезные советы

**Совет 1: Вспомогательная функция для расчёта чистой прибыли**
```python
def calculate_net(stats):
    """Рассчитать чистую прибыль из DailyStats."""
    return stats.profit + stats.commission + stats.swap

stats = await sugar.get_daily_stats()
net = calculate_net(stats)
print(f"Net profit: ${net:.2f}")
```

**Совет 2: Недельная сводка**
```python
from datetime import date, timedelta

async def weekly_summary():
    """Агрегировать недельную статистику."""
    total_deals = 0
    total_profit = 0.0
    total_commission = 0.0
    total_swap = 0.0
    total_volume = 0.0

    # Получить последние 7 дней
    for i in range(7):
        target = date.today() - timedelta(days=i)
        stats = await sugar.get_daily_stats(target)

        total_deals += stats.deals_count
        total_profit += stats.profit
        total_commission += stats.commission
        total_swap += stats.swap
        total_volume += stats.volume

    net_profit = total_profit + total_commission + total_swap

    print(f"Weekly Summary:")
    print(f"  Total trades: {total_deals}")
    print(f"  Total volume: {total_volume} lots")
    print(f"  Net profit: ${net_profit:.2f}")
```

**Совет 3: Расчёт профит-фактора**
```python
async def profit_factor():
    """Рассчитать профит-фактор (валовая прибыль / валовой убыток)."""
    from datetime import date, timedelta

    gross_profit = 0.0
    gross_loss = 0.0

    # Получить текущий месяц
    for i in range(30):
        target = date.today() - timedelta(days=i)
        deals = await sugar.get_deals(Period.CUSTOM, target, target)

        for deal in deals:
            if deal.profit > 0:
                gross_profit += deal.profit
            else:
                gross_loss += abs(deal.profit)

    if gross_loss > 0:
        pf = gross_profit / gross_loss
        print(f"Profit Factor: {pf:.2f}")
    else:
        print("No losing trades")
```

---

## 📚 См. также

- [get_deals](get_deals.md) - Получить исторические сделки
- [get_profit](get_profit.md) - Получить валовую прибыль за период
- [get_total_profit](../7.%20Position_Information/get_total_profit.md) - Плавающая прибыль
