# MT5Account - Positions & Orders - Overview

> Manage open positions, pending orders, and historical trading data. Query tick values and analyze trading performance.

## 📁 What lives here

* **[positions_total](./positions_total.md)** - **count only** of open positions (lightweight check).
* **[opened_orders](./opened_orders.md)** - **full details** of all pending orders and open positions.
* **[opened_orders_tickets](./opened_orders_tickets.md)** - **ticket IDs only** of opened orders/positions (lighter than full details).
* **[order_history](./order_history.md)** - **historical orders and deals** within time range with pagination.
* **[positions_history](./positions_history.md)** - **historical closed positions** filtered by open time.
* **[tick_value_with_size](./tick_value_with_size.md)** - **tick values and contract sizes** for multiple symbols (for P/L calculation).

---

## 📚 Step-by-step tutorials

Want detailed explanations with line-by-line code breakdown? Check these guides:

* **[positions_total - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_total_HOW.md)**
* **[opened_orders - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW.md)**
* **[opened_orders_tickets - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_tickets_HOW.md)**
* **[order_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW.md)**
* **[positions_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW.md)**
* **[tick_value_with_size - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW.md)**

---

## 🧭 Plain English

* **positions_total** - quick **count** of how many positions are open (no details).
* **opened_orders** - get **complete snapshot** of all pending orders and open positions.
* **opened_orders_tickets** - get **just ticket IDs** (more efficient than full details).
* **order_history** - get **past orders/deals** within a date range.
* **positions_history** - get **closed positions** with profit/loss data.
* **tick_value_with_size** - get **tick values** for calculating profit per pip.

> Rule of thumb: need **count only** - `positions_total()`; need **ticket IDs** - `opened_orders_tickets()`; need **full details** - `opened_orders()`; need **history** - `order_history()` or `positions_history()`.

---

## Quick choose

| If you need                                          | Use                       | Returns                    | Key inputs                          |
| ---------------------------------------------------- | ------------------------- | -------------------------- | ----------------------------------- |
| Count of open positions                              | `positions_total`         | PositionsTotalData (count) | *(none)*                            |
| Full details of open orders/positions                | `opened_orders`           | OpenedOrdersData (lists)   | Sort mode (optional)                |
| Just ticket IDs of opened items                      | `opened_orders_tickets`   | Lists of ticket IDs        | *(none)*                            |
| Historical orders within time range                  | `order_history`           | OrdersHistoryData          | from_dt, to_dt, sort mode, page     |
| Historical closed positions                          | `positions_history`       | PositionsHistoryData       | sort_type, open time range, page    |
| Tick values and contract sizes                       | `tick_value_with_size`    | TickValueWithSizeData      | List of symbol names                |

---

## ℹ️ Cross-refs & gotchas

* **positions_total** - fastest way to check if any positions exist (just count, no details).
* **opened_orders vs opened_orders_tickets** - use tickets version for lighter payload when you only need IDs.
* **order_history vs positions_history** - order_history gets orders/deals; positions_history gets closed positions.
* **Pagination** - order_history and positions_history support pagination for large datasets (use page and size parameters).
* **Time filters** - order_history uses close time; positions_history uses open time.
* **Tick value** - needed for calculating P/L per pip/tick; multiply by pip movement and lot size.
* **Contract size** - usually 100,000 for major forex pairs, 100 for metals (varies by symbol).

---

## 🟢 Minimal snippets

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
from datetime import datetime, timedelta
import asyncio

# Get count of open positions
data = await account.positions_total()
print(f"Open positions: {data.total_positions}")
```

```python
# Get all open orders and positions
data = await account.opened_orders()

print(f"Pending orders: {len(data.opened_orders)}")
print(f"Open positions: {len(data.position_infos)}")

# Show positions
for pos in data.position_infos:
    print(f"Position #{pos.ticket} {pos.symbol}: ${pos.profit:+.2f}")
```

```python
# Get just ticket IDs (lightweight)
data = await account.opened_orders_tickets()

print(f"Order tickets: {data.opened_orders_tickets}")
print(f"Position tickets: {data.opened_position_tickets}")
```

```python
# Get last 7 days order history
to_dt = datetime.utcnow()
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
# Get closed positions from last 30 days
to_dt = datetime.utcnow()
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
# Get tick values for symbols
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
data = await account.tick_value_with_size(symbols=symbols)

for info in data.symbol_tick_size_infos:
    print(f"{info.Name}: Tick Value=${info.TradeTickValue:.2f}, "
          f"Contract Size={info.TradeContractSize:.0f}")
```

```python
# Check if can open new position (position limit)
data = await account.positions_total()

max_positions = 10
if data.total_positions >= max_positions:
    print("[WARNING] Position limit reached!")
else:
    print(f"[OK] Can open {max_positions - data.total_positions} more position(s)")
```

```python
# Calculate total floating P/L
data = await account.opened_orders()

total_profit = sum(pos.profit for pos in data.position_infos)
print(f"Total floating P/L: ${total_profit:+.2f}")

if total_profit < 0:
    print("[WARNING] Account in drawdown")
```

```python
# Monitor for new positions
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
# Analyze trading performance
async def analyze_performance(days: int = 30):
    """Analyze trading performance for last N days"""
    to_dt = datetime.utcnow()
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
# Calculate profit per pip for position sizing
async def calculate_position_size(
    symbol: str,
    risk_amount: float,
    sl_pips: float
) -> float:
    """Calculate position size based on risk"""
    # Get tick value
    data = await account.tick_value_with_size(symbols=[symbol])
    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Assuming 1 lot
    profit_per_pip = info.TradeTickValue * 10  # 10 ticks per pip

    # Calculate lot size
    lots = risk_amount / (sl_pips * profit_per_pip)

    print(f"Position sizing for {symbol}:")
    print(f"  Risk: ${risk_amount:.2f}")
    print(f"  SL: {sl_pips} pips")
    print(f"  Lot size: {lots:.2f}")

    return lots

# Usage:
# lot_size = await calculate_position_size("EURUSD", risk_amount=100, sl_pips=50)
```

---

## 📚 See also

* **Account Information:** [Account_Information.Overview](../1. Account_Information/Account_Information.Overview.md) - get account balance, equity, leverage
* **Symbol Information:** [Symbol_Information.Overview](../2. Symbol_Information/Symbol_Information.Overview.md) - get symbol prices and parameters
* **Trading Operations:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - place and manage trades
