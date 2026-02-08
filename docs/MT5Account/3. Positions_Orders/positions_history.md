# Get Historical Closed Positions

> **Request:** historical closed positions within a time range with sorting and pagination support.

**API Information:**

* **Low-level API:** `MT5Account.positions_history(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountHelper`
* **Proto definition:** `PositionsHistory` (defined in `mt5-term-api-account-helper.proto`)
* **Enums in this method:** 2 enums with 13 total constants (1 input, 1 output)

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `PositionsHistory(PositionsHistoryRequest) -> PositionsHistoryReply`
* **Low-level client (generated):** `AccountHelperStub.PositionsHistory(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get historical closed positions filtered by open time range.
* **Why you need it.** Analyze trading performance, calculate statistics on closed positions.
* **When to use.** Use this for closed positions. Use `order_history()` for order/deal history.

---

## 🎯 Purpose

Use it to retrieve historical closed positions:

* Get closed positions within date range
* Analyze position performance
* Calculate profit/loss by position
* Review closed trades
* Filter by open time
* Pagination support for large datasets

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [positions_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW.md)**

---

## Method Signature

```python
async def positions_history(
    self,
    sort_type: account_helper_pb2.AH_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: Optional[datetime] = None,
    open_to: Optional[datetime] = None,
    page: int = 0,
    size: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.PositionsHistoryData
```

**Request message:**

```protobuf
message PositionsHistoryRequest {
  AH_ENUM_POSITIONS_HISTORY_SORT_TYPE sort_type = 1;
  optional google.protobuf.Timestamp position_open_time_from = 2;
  optional google.protobuf.Timestamp position_open_time_to = 3;
  optional int32 page_number = 4;
  optional int32 items_per_page = 5;
}
```

**Reply message:**

```protobuf
message PositionsHistoryReply {
  oneof response {
    PositionsHistoryData data = 1;
    Error error = 2;
  }
}

message PositionsHistoryData {
  repeated PositionHistoryInfo history_positions = 1;
}
```

---

## 🔽 Input

| Parameter       | Type                                        | Description                                          |
| --------------- | ------------------------------------------- | ---------------------------------------------------- |
| `sort_type`     | `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE` (enum, required) | Sort mode for positions                 |
| `open_from`     | `datetime` (optional)                       | Start of open time filter (UTC)                      |
| `open_to`       | `datetime` (optional)                       | End of open time filter (UTC)                        |
| `page`          | `int` (optional)                            | Page number for pagination (default 0)               |
| `size`          | `int` (optional)                            | Items per page (default 0 = all)                     |
| `deadline`      | `datetime` (optional)                       | Deadline for the gRPC call (UTC datetime)            |
| `cancellation_event` | `asyncio.Event` (optional)             | Event to cancel the operation                        |

**Usage:**

```python
from datetime import datetime, timedelta
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get positions opened in last 7 days
to_dt = datetime.utcnow()
from_dt = to_dt - timedelta(days=7)

data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt,
    page=0,
    size=100
)
```

---

## ⬆️ Output - `PositionsHistoryData`

| Field               | Type                           | Python Type                  | Description                              |
| ------------------- | ------------------------------ | ---------------------------- | ---------------------------------------- |
| `history_positions` | `repeated PositionHistoryInfo` | `list[PositionHistoryInfo]`  | List of historical position records      |

**Each PositionHistoryInfo contains:**

| Field              | Type               | Description                                          |
| ------------------ | ------------------ | ---------------------------------------------------- |
| `index`            | `int32`            | Index in the result set                              |
| `position_ticket`  | `uint64`           | Position ticket ID                                   |
| `order_type`       | `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE` | Order type (BUY, SELL, etc.)          |
| `open_time`        | `Timestamp`        | Position open time                                   |
| `close_time`       | `Timestamp`        | Position close time                                  |
| `volume`           | `double`           | Position volume in lots                              |
| `open_price`       | `double`           | Open price                                           |
| `close_price`      | `double`           | Close price                                          |
| `stop_loss`        | `double`           | Stop loss level                                      |
| `take_profit`      | `double`           | Take profit level                                    |
| `market_value`     | `double`           | Market value                                         |
| `commission`       | `double`           | Commission charged                                   |
| `fee`              | `double`           | Additional fees                                      |
| `profit`           | `double`           | Position profit/loss                                 |
| `swap`             | `double`           | Swap (rollover)                                      |
| `comment`          | `string`           | Comment                                              |
| `symbol`           | `string`           | Symbol name                                          |
| `magic`            | `int64`            | Magic number (EA identifier)                         |

---

## 🧱 Related enums (from proto)

### `AH_ENUM_POSITIONS_HISTORY_SORT_TYPE`

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `AH_POSITION_OPEN_TIME_ASC` | 0 | Sort by open time ascending |
| `AH_POSITION_OPEN_TIME_DESC` | 1 | Sort by open time descending |
| `AH_POSITION_TICKET_ASC` | 2 | Sort by ticket ID ascending |
| `AH_POSITION_TICKET_DESC` | 3 | Sort by ticket ID descending |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.positions_history(
    sort_type=pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt
)
```

### `AH_ENUM_POSITIONS_HISTORY_ORDER_TYPE`

Defined in `mt5-term-api-account-helper.proto`. Used in `PositionHistoryInfo` to indicate order type.

| Constant | Value | Description |
|----------|-------|-------------|
| `AH_ORDER_TYPE_BUY` | 0 | Market Buy order |
| `AH_ORDER_TYPE_SELL` | 1 | Market Sell order |
| `AH_ORDER_TYPE_BUY_LIMIT` | 2 | Buy Limit pending order |
| `AH_ORDER_TYPE_SELL_LIMIT` | 3 | Sell Limit pending order |
| `AH_ORDER_TYPE_BUY_STOP` | 4 | Buy Stop pending order |
| `AH_ORDER_TYPE_SELL_STOP` | 5 | Sell Stop pending order |
| `AH_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Buy Stop Limit pending order |
| `AH_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Sell Stop Limit pending order |
| `AH_ORDER_TYPE_CLOSE_BY` | 8 | Close by opposite position |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Filter buy positions
for pos in data.history_positions:
    if pos.order_type == pb2.AH_ORDER_TYPE_BUY:
        print(f"Buy position: {pos.position_ticket}")
```

---

## 🧩 Notes & Tips

* **Filter by open time:** The `open_from` and `open_to` filter positions by when they were opened, not closed.
* **Pagination:** Use `page` and `size` for large datasets. Set `size=0` to get all results.
* **Automatic reconnection:** Built-in protection against transient gRPC errors.
* **Connection required:** Call `connect_by_host_port()` or `connect_by_server_name()` first.
* **Thread safety:** Safe to call concurrently from multiple asyncio tasks.
* **UUID handling:** The terminal instance UUID is auto-generated by the server if not provided. For explicit control (e.g., in streaming scenarios), pass `id_=uuid4()` to constructor.

---

## 🔗 Usage Examples

### 1) Get last 30 days closed positions

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

async def main():
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        # Last 30 days
        to_dt = datetime.utcnow()
        from_dt = to_dt - timedelta(days=30)

        data = await account.positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
            open_from=from_dt,
            open_to=to_dt,
            size=100
        )

        print(f"Closed positions: {len(data.history_positions)}")

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            print(f"#{pos.position_ticket} {pos.symbol}: "
                  f"${pos.profit:+.2f} "
                  f"({open_time.date()} - {close_time.date()})")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Calculate total profit from closed positions

```python
async def calculate_closed_profit(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> float:
    """Calculate total profit from closed positions"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt,
        size=0  # Get all
    )

    total_profit = sum(pos.profit for pos in data.history_positions)
    total_commission = sum(pos.commission for pos in data.history_positions)
    total_swap = sum(pos.swap for pos in data.history_positions)

    net_profit = total_profit - total_commission + total_swap

    print(f"Closed positions statistics:")
    print(f"  Total positions: {len(data.history_positions)}")
    print(f"  Gross profit: ${total_profit:+.2f}")
    print(f"  Commission: ${total_commission:.2f}")
    print(f"  Swap: ${total_swap:+.2f}")
    print(f"  Net profit: ${net_profit:+.2f}")

    return net_profit

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
profit = await calculate_closed_profit(account, from_dt, to_dt)
```

### 3) Analyze win rate

```python
async def analyze_closed_positions(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analyze closed positions performance"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for pos in data.history_positions:
        if pos.profit > 0:
            wins += 1
            total_win_profit += pos.profit
        elif pos.profit < 0:
            losses += 1
            total_loss_profit += pos.profit

    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    avg_win = total_win_profit / wins if wins > 0 else 0
    avg_loss = total_loss_profit / losses if losses > 0 else 0

    result = {
        "total_positions": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": abs(total_win_profit / total_loss_profit) if total_loss_profit != 0 else 0
    }

    print(f"\nPosition Analysis:")
    print(f"  Total: {total}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Avg Win: ${avg_win:.2f}")
    print(f"  Avg Loss: ${avg_loss:.2f}")
    print(f"  Profit Factor: {result['profit_factor']:.2f}")

    return result

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
stats = await analyze_closed_positions(account, from_dt, to_dt)
```

### 4) Get best and worst positions

```python
async def get_best_worst_positions(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    limit: int = 5
):
    """Get best and worst performing positions"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    # Sort by profit
    sorted_positions = sorted(data.history_positions, key=lambda p: p.profit, reverse=True)

    best = sorted_positions[:limit]
    worst = sorted_positions[-limit:]

    print(f"\nBest {limit} positions:")
    for i, pos in enumerate(best, 1):
        print(f"  {i}. #{pos.position_ticket} {pos.symbol}: ${pos.profit:+.2f}")

    print(f"\nWorst {limit} positions:")
    for i, pos in enumerate(worst, 1):
        print(f"  {i}. #{pos.position_ticket} {pos.symbol}: ${pos.profit:+.2f}")

    return {"best": best, "worst": worst}

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
results = await get_best_worst_positions(account, from_dt, to_dt)
```

### 5) Get positions by symbol

```python
async def get_symbol_closed_positions(
    account: MT5Account,
    symbol: str,
    from_dt: datetime,
    to_dt: datetime
):
    """Get closed positions for specific symbol"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
        open_from=from_dt,
        open_to=to_dt
    )

    symbol_positions = [
        pos for pos in data.history_positions
        if pos.symbol == symbol
    ]

    total_profit = sum(pos.profit for pos in symbol_positions)

    print(f"\n{symbol} closed positions: {len(symbol_positions)}")
    print(f"Total profit: ${total_profit:+.2f}")

    return symbol_positions

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
eurusd_positions = await get_symbol_closed_positions(account, "EURUSD", from_dt, to_dt)
```

### 6) Export to CSV

```python
import csv

async def export_positions_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "positions_history.csv"
):
    """Export closed positions to CSV"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Symbol', 'Open Time', 'Close Time',
            'Volume', 'Open Price', 'Close Price',
            'Profit', 'Commission', 'Swap', 'Total'
        ])

        for pos in data.history_positions:
            open_time = pos.open_time.ToDatetime()
            close_time = pos.close_time.ToDatetime()
            total = pos.profit - pos.commission + pos.swap

            writer.writerow([
                pos.position_ticket,
                pos.symbol,
                open_time.strftime('%Y-%m-%d %H:%M:%S'),
                close_time.strftime('%Y-%m-%d %H:%M:%S'),
                pos.volume,
                pos.open_price,
                pos.close_price,
                pos.profit,
                pos.commission,
                pos.swap,
                total
            ])

    print(f"[OK] Exported {len(data.history_positions)} positions to {filename}")

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
await export_positions_to_csv(account, from_dt, to_dt)
```

---

## Common Patterns

### Calculate daily profit

```python
from collections import defaultdict

async def get_daily_profit(account: MT5Account, from_dt: datetime, to_dt: datetime):
    """Calculate profit per day from closed positions"""
    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    daily_profit = defaultdict(float)

    for pos in data.history_positions:
        close_date = pos.close_time.ToDatetime().date()
        daily_profit[close_date] += pos.profit

    return dict(daily_profit)
```

### Get positions with pagination

```python
async def get_all_positions_paginated(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    page_size: int = 100
):
    """Get all positions using pagination"""
    all_positions = []
    page = 0

    while True:
        data = await account.positions_history(
            sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
            open_from=from_dt,
            open_to=to_dt,
            page=page,
            size=page_size
        )

        if not data.history_positions:
            break

        all_positions.extend(data.history_positions)
        page += 1

    return all_positions
```

---

## 📚 See also

* [order_history](./order_history.md) - Get historical orders and deals
* [opened_orders](./opened_orders.md) - Get currently open positions
* [positions_total](./positions_total.md) - Get count of open positions
