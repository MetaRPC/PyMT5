# MT5Account - Позиции и ордера - Обзор

> Управление открытыми позициями, отложенными ордерами и историческими торговыми данными. Запрос стоимости тика и анализ торговой эффективности.

## 📁 Что здесь находится

* **[positions_total](./positions_total.md)** - **только количество** открытых позиций (облегчённая проверка).
* **[opened_orders](./opened_orders.md)** - **полные данные** обо всех отложенных ордерах и открытых позициях.
* **[opened_orders_tickets](./opened_orders_tickets.md)** - **только ID тикетов** открытых ордеров/позиций (легче, чем полные данные).
* **[order_history](./order_history.md)** - **исторические ордера и сделки** во временном диапазоне с пагинацией.
* **[positions_history](./positions_history.md)** - **исторические закрытые позиции** с фильтрацией по времени открытия.
* **[tick_value_with_size](./tick_value_with_size.md)** - **стоимость тика и размеры контрактов** для нескольких символов (для расчёта P/L).

---

## 📚 Пошаговые руководства

Нужны подробные объяснения с построчным разбором кода? Загляните в эти руководства:

* **[positions_total - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_total_HOW.md)**
* **[opened_orders - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW.md)**
* **[opened_orders_tickets - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_tickets_HOW.md)**
* **[order_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW.md)**
* **[positions_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW.md)**
* **[tick_value_with_size - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW.md)**

---

## 🧭 Простыми словами

* **positions_total** - быстрое **количество** того, сколько позиций открыто (без деталей).
* **opened_orders** - получить **полный снимок** всех отложенных ордеров и открытых позиций.
* **opened_orders_tickets** - получить **только ID тикетов** (эффективнее, чем полные данные).
* **order_history** - получить **прошлые ордера/сделки** в диапазоне дат.
* **positions_history** - получить **закрытые позиции** с данными о прибыли/убытке.
* **tick_value_with_size** - получить **стоимость тика** для расчёта прибыли на пункт.

> Правило большого пальца: нужно **только количество** - `positions_total()`; нужны **ID тикетов** - `opened_orders_tickets()`; нужны **полные данные** - `opened_orders()`; нужна **история** - `order_history()` или `positions_history()`.

---

## Быстрый выбор

| Если вам нужно                                       | Используйте               | Возвращает                 | Ключевые входные данные             |
| ---------------------------------------------------- | ------------------------- | -------------------------- | ----------------------------------- |
| Количество открытых позиций                          | `positions_total`         | PositionsTotalData (count) | *(нет)*                             |
| Полные данные об открытых ордерах/позициях            | `opened_orders`           | OpenedOrdersData (lists)   | Режим сортировки (опционально)      |
| Только ID тикетов открытых элементов                 | `opened_orders_tickets`   | Lists of ticket IDs        | *(нет)*                             |
| Исторические ордера во временном диапазоне            | `order_history`           | OrdersHistoryData          | from_dt, to_dt, режим сортировки, страница |
| Исторические закрытые позиции                        | `positions_history`       | PositionsHistoryData       | sort_type, диапазон времени открытия, страница |
| Стоимость тика и размеры контрактов                  | `tick_value_with_size`    | TickValueWithSizeData      | Список имён символов                |

---

## ℹ️ Перекрёстные ссылки и подводные камни

* **positions_total** - самый быстрый способ проверить, есть ли позиции (только количество, без деталей).
* **opened_orders vs opened_orders_tickets** - используйте версию с тикетами для более лёгкой нагрузки, когда нужны только ID.
* **order_history vs positions_history** - order_history получает ордера/сделки; positions_history получает закрытые позиции.
* **Пагинация** - order_history и positions_history поддерживают пагинацию для больших наборов данных (используйте параметры page и size).
* **Фильтры по времени** - order_history использует время закрытия; positions_history использует время открытия.
* **Стоимость тика** - нужна для расчёта P/L на пункт/тик; умножьте на движение в пунктах и размер лота.
* **Размер контракта** - обычно 100 000 для основных форекс-пар, 100 для металлов (зависит от символа).

---

## 🟢 Минимальные фрагменты

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
from datetime import datetime, timedelta, timezone
import asyncio

# Получить количество открытых позиций
data = await account.positions_total()
print(f"Open positions: {data.total_positions}")
```

```python
# Получить все открытые ордера и позиции
data = await account.opened_orders()

print(f"Pending orders: {len(data.opened_orders)}")
print(f"Open positions: {len(data.position_infos)}")

# Показать позиции
for pos in data.position_infos:
    print(f"Position #{pos.ticket} {pos.symbol}: ${pos.profit:+.2f}")
```

```python
# Получить только ID тикетов (облегчённо)
data = await account.opened_orders_tickets()

print(f"Order tickets: {data.opened_orders_tickets}")
print(f"Position tickets: {data.opened_position_tickets}")
```

```python
# Получить историю ордеров за последние 7 дней
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=7)

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
    items_per_page=100
)

print(f"Total orders: {data.arrayTotal}")
for item in data.history_data:
    if item.history_deal:
        print(f"Deal: ${item.history_deal.profit:.2f}")
```

```python
# Получить закрытые позиции за последние 30 дней
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=30)

data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt
)

total_profit = sum(pos.profit for pos in data.history_positions)
print(f"Closed positions: {len(data.history_positions)}")
print(f"Total profit: ${total_profit:+.2f}")
```

```python
# Получить стоимость тика для символов
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
data = await account.tick_value_with_size(symbols=symbols)

for info in data.symbol_tick_size_infos:
    print(f"{info.Name}: Tick Value=${info.TradeTickValue:.2f}, "
          f"Contract Size={info.TradeContractSize:.0f}")
```

```python
# Проверить, можно ли открыть новую позицию (лимит позиций)
data = await account.positions_total()

max_positions = 10
if data.total_positions >= max_positions:
    print("[WARNING] Position limit reached!")
else:
    print(f"[OK] Can open {max_positions - data.total_positions} more position(s)")
```

```python
# Рассчитать суммарную плавающую P/L
data = await account.opened_orders()

total_profit = sum(pos.profit for pos in data.position_infos)
print(f"Total floating P/L: ${total_profit:+.2f}")

if total_profit < 0:
    print("[WARNING] Account in drawdown")
```

```python
# Отслеживать новые позиции
async def monitor_positions(interval: float = 5.0):
    """Monitor for position changes"""
    previous_tickets = set()

    while True:
        data = await account.opened_orders_tickets()
        current_tickets = set(data.opened_position_tickets)

        new = current_tickets - previous_tickets
        closed = previous_tickets - current_tickets

        for ticket in new:
            print(f"[+] New position: #{ticket}")
        for ticket in closed:
            print(f"[-] Closed position: #{ticket}")

        previous_tickets = current_tickets
        await asyncio.sleep(interval)

# await monitor_positions()
```

```python
# Анализ торговой эффективности
async def analyze_performance(days: int = 30):
    """Analyze trading performance for last N days"""
    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(days=days)

    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    wins = sum(1 for pos in data.history_positions if pos.profit > 0)
    losses = sum(1 for pos in data.history_positions if pos.profit < 0)
    total = wins + losses

    win_rate = (wins / total * 100) if total > 0 else 0
    total_profit = sum(pos.profit for pos in data.history_positions)

    print(f"\nPerformance (last {days} days):")
    print(f"  Total trades: {total}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Net profit: ${total_profit:+.2f}")

# await analyze_performance(days=30)
```

```python
# Рассчитать прибыль на пункт для расчёта размера позиции
async def calculate_position_size(
    symbol: str,
    risk_amount: float,
    sl_pips: float
) -> float:
    """Calculate position size based on risk"""
    # Получить стоимость тика
    data = await account.tick_value_with_size(symbols=[symbol])
    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Предполагая 1 лот
    profit_per_pip = info.TradeTickValue * 10  # 10 тиков на пункт

    # Рассчитать размер лота
    lots = risk_amount / (sl_pips * profit_per_pip)

    print(f"Position sizing for {symbol}:")
    print(f"  Risk: ${risk_amount:.2f}")
    print(f"  SL: {sl_pips} pips")
    print(f"  Lot size: {lots:.2f}")

    return lots

# Использование:
# lot_size = await calculate_position_size("EURUSD", risk_amount=100, sl_pips=50)
```

---

## 📚 См. также

* **Информация о счёте:** [Account_Information.Overview](../1. Account_Information/Account_Information.Overview.md) - получить баланс, средства (equity), кредитное плечо счёта
* **Информация о символах:** [Symbol_Information.Overview](../2. Symbol_Information/Symbol_Information.Overview.md) - получить цены и параметры символов
* **Торговые операции:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - размещать и управлять сделками
