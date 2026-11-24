# Получить исторические сделки (`get_deals`)

> **Sugar-метод:** Извлекает закрытые позиции (сделки) за указанный период времени.

**Информация об API:**

* **Метод:** `sugar.get_deals(period, from_date, to_date)`
* **Возвращает:** Список объектов закрытых позиций
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_deals(
    self,
    period: Period = Period.TODAY,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List
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
| `List` | Список объектов закрытых позиций (пустой список, если сделок нет) |

---

## 🏛️ Основное

**Что делает:**

- Получает закрытые позиции из истории
- Поддерживает предопределённые периоды через перечисление Period
- Возвращает полные детали позиций (ticket, symbol, profit, commission, swap и т. д.)
- Получает до 10 000 позиций за запрос

**Ключевое поведение:**

- Использует positions_history (включает profit/commission/swap)
- Сортируется по времени открытия по возрастанию
- Возвращает пустой список, если сделок нет
- Период CUSTOM требует from_date и to_date

---

## ⚡ Под капотом

```
MT5Sugar.get_deals()
    ↓ преобразует period в диапазон datetime
MT5Sugar._get_period_range()
    ↓ вызывает
MT5Service.get_positions_history()
    ↓ вызывает
MT5Account.positions_history()
    ↓ gRPC protobuf
AccountHelperService.PositionsHistory()
    ↓ терминал MT5
```

**Цепочка вызовов:**

1. Sugar преобразует перечисление Period в диапазон datetime
2. Sugar вызывает Service.get_positions_history() с диапазоном дат
3. Service перенаправляет в Account.positions_history()
4. Account отправляет gRPC-запрос в терминал
5. Возвращает список history_positions (до 10 000)

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1437`
- Service: `src/pymt5/mt5_service.py:810`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1475`

---

## Удобные методы

Все эти методы внутренне вызывают `get_deals()` с разными периодами:

```python
# Сделки за сегодня
deals = await sugar.get_deals_today()
# То же, что: await sugar.get_deals(Period.TODAY)

# Сделки за вчера
deals = await sugar.get_deals_yesterday()
# То же, что: await sugar.get_deals(Period.YESTERDAY)

# Сделки за эту неделю (с понедельника по сегодня)
deals = await sugar.get_deals_this_week()
# То же, что: await sugar.get_deals(Period.THIS_WEEK)

# Сделки за этот месяц
deals = await sugar.get_deals_this_month()
# То же, что: await sugar.get_deals(Period.THIS_MONTH)

# Произвольный диапазон дат
deals = await sugar.get_deals_date_range(date(2024, 1, 1), date(2024, 1, 31))
# То же, что: await sugar.get_deals(Period.CUSTOM, date(2024, 1, 1), date(2024, 1, 31))
```

---

## Когда использовать

**Используйте `get_deals()`, когда:**

- Анализируете торговую историю
- Рассчитываете статистику (винрейт, средняя прибыль и т. д.)
- Просматриваете прошлые сделки
- Ведёте торговый журнал

**Не используйте, когда:**

- Нужна только суммарная прибыль (используйте `get_profit()`)
- Нужны текущие открытые позиции (используйте `get_open_positions()`)
- Нужны данные в реальном времени (это исторические данные)

---

## 🔗 Примеры

### Пример 1: Сделки за сегодня

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account
from pymt5.constants import Period

async def todays_deals():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить сделки за сегодня
    deals = await sugar.get_deals(Period.TODAY)
    # Или: deals = await sugar.get_deals_today()

    print(f"Today's deals: {len(deals)}")

    for deal in deals:
        print(f"#{deal.ticket}: {deal.symbol} {deal.volume} lots, "
              f"Profit: ${deal.profit:.2f}")

# Вывод:
# Today's deals: 5
# #123456: EURUSD 0.1 lots, Profit: $12.50
# #123457: GBPUSD 0.05 lots, Profit: -$3.20
```

### Пример 2: Результативность за эту неделю

```python
from datetime import date

async def weekly_performance():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить сделки за эту неделю
    deals = await sugar.get_deals_this_week()

    if deals:
        # Рассчитать статистику
        total_trades = len(deals)
        winning = sum(1 for d in deals if d.profit > 0)
        losing = sum(1 for d in deals if d.profit < 0)
        win_rate = (winning / total_trades) * 100

        total_profit = sum(d.profit for d in deals)

        print(f"This Week's Performance:")
        print(f"  Total trades: {total_trades}")
        print(f"  Win rate: {win_rate:.1f}%")
        print(f"  Total P&L: ${total_profit:.2f}")
```

### Пример 3: Анализ произвольного диапазона дат

```python
from datetime import date

async def january_analysis():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить сделки за январь 2024
    deals = await sugar.get_deals(
        period=Period.CUSTOM,
        from_date=date(2024, 1, 1),
        to_date=date(2024, 1, 31)
    )
    # Или: deals = await sugar.get_deals_date_range(date(2024, 1, 1), date(2024, 1, 31))

    # Анализ по символу
    from collections import defaultdict
    by_symbol = defaultdict(list)

    for deal in deals:
        by_symbol[deal.symbol].append(deal)

    print("January 2024 by Symbol:")
    for symbol, symbol_deals in by_symbol.items():
        profit = sum(d.profit for d in symbol_deals)
        print(f"  {symbol}: {len(symbol_deals)} trades, ${profit:.2f}")
```

---

## Типичные ошибки

**Ошибка 1: Отсутствие from_date/to_date для периода CUSTOM**
```python
# ОШИБКА: CUSTOM требует дат
try:
    deals = await sugar.get_deals(Period.CUSTOM)
except ValueError as e:
    print(e)  # "from_date and to_date required for CUSTOM period"
```

**Решение:** Всегда указывайте даты для CUSTOM
```python
deals = await sugar.get_deals(
    Period.CUSTOM,
    from_date=date(2024, 1, 1),
    to_date=date(2024, 1, 31)
)
```

**Ошибка 2: Предположение, что список никогда не пуст**
```python
# ОШИБКА: падает, если сделок нет
deals = await sugar.get_deals_today()
first_deal = deals[0]  # IndexError, если пусто
```

**Решение:** Проверяйте, не пуст ли список
```python
deals = await sugar.get_deals_today()

if deals:
    first_deal = deals[0]
else:
    print("No deals today")
```

**Ошибка 3: Превышение лимита в 10 000 позиций**
```python
# Получить сделки за весь год
deals = await sugar.get_deals(
    Period.CUSTOM,
    from_date=date(2023, 1, 1),
    to_date=date(2023, 12, 31)
)
# Возвращает максимум 10 000 позиций
```

**Решение:** Разбивайте большие диапазоны дат
```python
# Получать сделки помесячно для больших диапазонов
from datetime import date, timedelta

all_deals = []
start = date(2023, 1, 1)
end = date(2023, 12, 31)

current = start
while current <= end:
    month_end = min(current.replace(day=28) + timedelta(days=4), end)
    month_end = month_end.replace(day=1) - timedelta(days=1)

    deals = await sugar.get_deals(Period.CUSTOM, current, month_end)
    all_deals.extend(deals)

    current = month_end + timedelta(days=1)
```

---

## Полезные советы

**Совет 1: Расчёт винрейта**

```python
deals = await sugar.get_deals_today()

if deals:
    winners = [d for d in deals if d.profit > 0]
    losers = [d for d in deals if d.profit < 0]

    win_rate = (len(winners) / len(deals)) * 100
    print(f"Win rate: {win_rate:.1f}%")
```

**Совет 2: Найти лучшую/худшую сделку**
```python
deals = await sugar.get_deals_this_week()

if deals:
    best = max(deals, key=lambda d: d.profit)
    worst = min(deals, key=lambda d: d.profit)

    print(f"Best trade: #{best.ticket} ${best.profit:.2f}")
    print(f"Worst trade: #{worst.ticket} ${worst.profit:.2f}")
```

**Совет 3: Средняя прибыль на сделку**
```python
deals = await sugar.get_deals_this_month()

if deals:
    total_profit = sum(d.profit for d in deals)
    avg_profit = total_profit / len(deals)

    print(f"Average per trade: ${avg_profit:.2f}")
```

---

## 📚 См. также

- [get_profit](get_profit.md) - Получить суммарную прибыль за период
- [get_daily_stats](get_daily_stats.md) - Полная дневная статистика
- [get_open_positions](../7.%20Position_Information/get_open_positions.md) - Текущие позиции
