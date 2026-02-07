# Get Historical Orders

> **Request:** historical order data within a specified time range with pagination support.

**API Information:**

* **Low-level API:** `MT5Account.order_history(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountHelper`
* **Proto definition:** `OrderHistory` (defined in `mt5-term-api-account-helper.proto`)
* **Enums in this method:** 8 enums with 66 total constants (1 input, 7 output)

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `OrderHistory(OrderHistoryRequest) -> OrderHistoryReply`
* **Low-level client (generated):** `AccountHelperStub.OrderHistory(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get historical orders and deals within a time range with sorting and pagination.
* **Why you need it.** Analyze trading history, calculate statistics, audit orders.
* **When to use.** Use this for order history. Use `positions_history()` for closed positions.

---

## 🎯 Purpose

Use it to retrieve historical trading data:

* Get past orders and deals within date range
* Analyze trading performance
* Calculate profit/loss statistics
* Audit trading activity
* Export trading history
* Pagination support for large datasets

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [order_history - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW.md)**

---

## Method Signature

```python
async def order_history(
    self,
    from_dt: datetime,
    to_dt: datetime,
    sort_mode: account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_ASC,
    page_number: int = 0,
    items_per_page: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OrdersHistoryData
```

**Request message:**

```protobuf
message OrderHistoryRequest {
  google.protobuf.Timestamp inputFrom = 1;
  google.protobuf.Timestamp inputTo = 2;
  BMT5_ENUM_ORDER_HISTORY_SORT_TYPE inputSortMode = 3;
  int32 pageNumber = 4;
  int32 itemsPerPage = 5;
}
```

**Reply message:**

```protobuf
message OrderHistoryReply {
  oneof response {
    OrdersHistoryData data = 1;
    Error error = 2;
  }
}

message OrdersHistoryData {
  int32 arrayTotal = 1;
  int32 pageNumber = 2;
  int32 itemsPerPage = 3;
  repeated HistoryData history_data = 4;
}
```

---

## 🔽 Input

| Parameter       | Type                                 | Description                                          |
| --------------- | ------------------------------------ | ---------------------------------------------------- |
| `from_dt`       | `datetime` (required)                | Start time for history query (server time)           |
| `to_dt`         | `datetime` (required)                | End time for history query (server time)             |
| `sort_mode`     | `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE` (enum) | Sort mode (by time or ticket ID)           |
| `page_number`   | `int` (optional)                     | Page number for pagination (default 0)               |
| `items_per_page`| `int` (optional)                     | Items per page (default 0 = all)                     |
| `deadline`      | `datetime` (optional)                | Deadline for the gRPC call (UTC datetime)            |
| `cancellation_event` | `asyncio.Event` (optional)      | Event to cancel the operation                        |

**Usage:**

```python
from datetime import datetime, timedelta
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Get last 7 days history
to_dt = datetime.utcnow()
from_dt = to_dt - timedelta(days=7)

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
    page_number=0,
    items_per_page=100
)
```

---

## ⬆️ Output - `OrdersHistoryData`

| Field           | Type                    | Python Type           | Description                              |
| --------------- | ----------------------- | --------------------- | ---------------------------------------- |
| `arrayTotal`    | `int32`                 | `int`                 | Total number of records (all pages)      |
| `pageNumber`    | `int32`                 | `int`                 | Current page number                      |
| `itemsPerPage`  | `int32`                 | `int`                 | Items per page                           |
| `history_data`  | `repeated HistoryData`  | `list[HistoryData]`   | List of historical order/deal records    |

**Each HistoryData contains:**

| Field           | Type               | Description                                          |
| --------------- | ------------------ | ---------------------------------------------------- |
| `index`         | `uint32`           | Index in the result set                              |
| `history_order` | `OrderHistoryData` | Order details (if applicable)                        |
| `history_deal`  | `DealHistoryData`  | Deal details (if applicable)                         |

**OrderHistoryData fields:**

- `ticket` (uint64) - Order ticket number
- `setup_time` (Timestamp) - Order setup time
- `done_time` (Timestamp) - Order execution time
- `state` (BMT5_ENUM_ORDER_STATE) - Order state
- `price_current` (double) - Current price
- `price_open` (double) - Order open price
- `stop_limit` (double) - Stop limit price
- `stop_loss` (double) - Stop loss level
- `take_profit` (double) - Take profit level
- `volume_current` (double) - Current volume
- `volume_initial` (double) - Initial volume
- `magic_number` (int64) - Expert Advisor ID
- `type` (BMT5_ENUM_ORDER_TYPE) - Order type
- `time_expiration` (Timestamp) - Order expiration time
- `type_filling` (BMT5_ENUM_ORDER_TYPE_FILLING) - Filling type
- `type_time` (BMT5_ENUM_ORDER_TYPE_TIME) - Order lifetime
- `position_id` (uint64) - Position ticket
- `symbol` (string) - Symbol name
- `external_id` (string) - External ID
- `comment` (string) - Order comment
- `account_login` (int64) - Account login

**DealHistoryData fields:**

- `ticket` (uint64) - Deal ticket number
- `profit` (double) - Deal profit
- `commission` (double) - Commission
- `fee` (double) - Additional fee
- `price` (double) - Deal price
- `stop_loss` (double) - Stop loss level at deal time
- `take_profit` (double) - Take profit level at deal time
- `swap` (double) - Swap
- `volume` (double) - Deal volume
- `entry_type` (BMT5_ENUM_DEAL_ENTRY_TYPE) - Entry type
- `time` (Timestamp) - Deal time
- `type` (BMT5_ENUM_DEAL_TYPE) - Deal type
- `reason` (BMT5_ENUM_DEAL_REASON) - Deal reason
- `position_id` (uint64) - Position ID
- `comment` (string) - Deal comment
- `symbol` (string) - Symbol name
- `external_id` (string) - External ID
- `account_login` (int64) - Account login

---

## 🧱 Related enums (from proto)

### `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE`

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_SORT_BY_OPEN_TIME_ASC` | 0 | Sort by open time ascending |
| `BMT5_SORT_BY_OPEN_TIME_DESC` | 1 | Sort by open time descending |
| `BMT5_SORT_BY_CLOSE_TIME_ASC` | 2 | Sort by close time ascending |
| `BMT5_SORT_BY_CLOSE_TIME_DESC` | 3 | Sort by close time descending |
| `BMT5_SORT_BY_ORDER_TICKET_ID_ASC` | 4 | Sort by ticket ID ascending |
| `BMT5_SORT_BY_ORDER_TICKET_ID_DESC` | 5 | Sort by ticket ID descending |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=pb2.BMT5_SORT_BY_CLOSE_TIME_DESC
)
```

### `BMT5_ENUM_ORDER_STATE`

Defined in `mt5-term-api-account-helper.proto`. Used in `OrderHistoryData` to indicate order state.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_STATE_STARTED` | 0 | Order checked, but not yet accepted by broker |
| `BMT5_ORDER_STATE_PLACED` | 1 | Order accepted |
| `BMT5_ORDER_STATE_CANCELED` | 2 | Order canceled by client |
| `BMT5_ORDER_STATE_PARTIAL` | 3 | Order partially executed |
| `BMT5_ORDER_STATE_FILLED` | 4 | Order fully executed |
| `BMT5_ORDER_STATE_REJECTED` | 5 | Order rejected |
| `BMT5_ORDER_STATE_EXPIRED` | 6 | Order expired |
| `BMT5_ORDER_STATE_REQUEST_ADD` | 7 | Order is being registered (placing to trading system) |
| `BMT5_ORDER_STATE_REQUEST_MODIFY` | 8 | Order is being modified (changing its parameters) |
| `BMT5_ORDER_STATE_REQUEST_CANCEL` | 9 | Order is being deleted (deleting from trading system) |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check order state in history
for item in data.history_data:
    if item.history_order.state == pb2.BMT5_ORDER_STATE_FILLED:
        print(f"Order {item.history_order.ticket} was filled")
```

### `BMT5_ENUM_ORDER_TYPE`

Defined in `mt5-term-api-account-helper.proto`. Used in `OrderHistoryData` to indicate order type.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_TYPE_BUY` | 0 | Market Buy order |
| `BMT5_ORDER_TYPE_SELL` | 1 | Market Sell order |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Buy Limit pending order |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Sell Limit pending order |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Buy Stop pending order |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Sell Stop pending order |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Buy Stop Limit pending order |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Sell Stop Limit pending order |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Close by opposite position |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Filter buy orders
for item in data.history_data:
    if item.history_order.type == pb2.BMT5_ORDER_TYPE_BUY:
        print(f"Buy order: {item.history_order.ticket}")
```

### `BMT5_ENUM_ORDER_TYPE_FILLING`

Defined in `mt5-term-api-account-helper.proto`. Used in `OrderHistoryData` to indicate order filling type.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Return |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check filling type
for item in data.history_data:
    if item.history_order.type_filling == pb2.BMT5_ORDER_FILLING_FOK:
        print(f"FOK order: {item.history_order.ticket}")
```

### `BMT5_ENUM_ORDER_TYPE_TIME`

Defined in `mt5-term-api-account-helper.proto`. Used in `OrderHistoryData` to indicate order lifetime.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_TIME_GTC` | 0 | Good till cancel |
| `BMT5_ORDER_TIME_DAY` | 1 | Good till current trade day |
| `BMT5_ORDER_TIME_SPECIFIED` | 2 | Good till specified date |
| `BMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Good till specified day |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check time type
for item in data.history_data:
    if item.history_order.type_time == pb2.BMT5_ORDER_TIME_GTC:
        print(f"GTC order: {item.history_order.ticket}")
```

### `BMT5_ENUM_DEAL_ENTRY_TYPE`

Defined in `mt5-term-api-account-helper.proto`. Used in `DealHistoryData` to indicate deal entry type.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_DEAL_ENTRY_IN` | 0 | Entry in |
| `BMT5_DEAL_ENTRY_OUT` | 1 | Entry out |
| `BMT5_DEAL_ENTRY_INOUT` | 2 | Reverse |
| `BMT5_DEAL_ENTRY_OUT_BY` | 3 | Close by |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check deal entry type
for item in data.history_data:
    if item.history_deal.entry_type == pb2.BMT5_DEAL_ENTRY_IN:
        print(f"Entry in deal: {item.history_deal.ticket}")
```

### `BMT5_ENUM_DEAL_TYPE`

Defined in `mt5-term-api-account-helper.proto`. Used in `DealHistoryData` to indicate deal type.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_DEAL_TYPE_BUY` | 0 | Buy |
| `BMT5_DEAL_TYPE_SELL` | 1 | Sell |
| `BMT5_DEAL_TYPE_BALANCE` | 2 | Balance |
| `BMT5_DEAL_TYPE_CREDIT` | 3 | Credit |
| `BMT5_DEAL_TYPE_CHARGE` | 4 | Additional charge |
| `BMT5_DEAL_TYPE_CORRECTION` | 5 | Correction |
| `BMT5_DEAL_TYPE_BONUS` | 6 | Bonus |
| `BMT5_DEAL_TYPE_COMMISSION` | 7 | Additional commission |
| `BMT5_DEAL_TYPE_COMMISSION_DAILY` | 8 | Daily commission |
| `BMT5_DEAL_TYPE_COMMISSION_MONTHLY` | 9 | Monthly commission |
| `BMT5_DEAL_TYPE_COMMISSION_AGENT_DAILY` | 10 | Daily agent commission |
| `BMT5_DEAL_TYPE_COMMISSION_AGENT_MONTHLY` | 11 | Monthly agent commission |
| `BMT5_DEAL_TYPE_INTEREST` | 12 | Interest rate |
| `BMT5_DEAL_TYPE_BUY_CANCELED` | 13 | Canceled buy deal |
| `BMT5_DEAL_TYPE_SELL_CANCELED` | 14 | Canceled sell deal |
| `BMT5_DEAL_DIVIDEND` | 15 | Dividend |
| `BMT5_DEAL_DIVIDEND_FRANKED` | 16 | Franked dividend |
| `BMT5_DEAL_TAX` | 17 | Tax |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Filter buy/sell deals
for item in data.history_data:
    if item.history_deal.type == pb2.BMT5_DEAL_TYPE_BUY:
        print(f"Buy deal: {item.history_deal.ticket}")
    elif item.history_deal.type == pb2.BMT5_DEAL_TYPE_BALANCE:
        print(f"Balance operation: {item.history_deal.ticket}")
```

### `BMT5_ENUM_DEAL_REASON`

Defined in `mt5-term-api-account-helper.proto`. Used in `DealHistoryData` to indicate deal reason.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_DEAL_REASON_CLIENT` | 0 | Deal placed manually |
| `BMT5_DEAL_REASON_MOBILE` | 1 | Deal placed from mobile |
| `BMT5_DEAL_REASON_WEB` | 2 | Deal placed from web |
| `BMT5_DEAL_REASON_EXPERT` | 3 | Deal placed by expert |
| `BMT5_DEAL_REASON_SL` | 4 | Deal placed due to Stop Loss |
| `BMT5_DEAL_REASON_TP` | 5 | Deal placed due to Take Profit |
| `BMT5_DEAL_REASON_SO` | 6 | Deal placed due to Stop Out |
| `BMT5_DEAL_REASON_ROLLOVER` | 7 | Deal due to rollover |
| `BMT5_DEAL_REASON_VMARGIN` | 8 | Deal due to variation margin |
| `BMT5_DEAL_REASON_SPLIT` | 9 | Deal due to split |
| `BMT5_DEAL_REASON_CORPORATE_ACTION` | 10 | Deal due to corporate action |

**Usage:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check deal reason
for item in data.history_data:
    if item.history_deal.reason == pb2.BMT5_DEAL_REASON_SL:
        print(f"Stop Loss deal: {item.history_deal.ticket}")
    elif item.history_deal.reason == pb2.BMT5_DEAL_REASON_EXPERT:
        print(f"EA deal: {item.history_deal.ticket}")
```

---

## 🧩 Notes & Tips

* **Server time:** The `from_dt` and `to_dt` parameters use server time, not UTC.
* **Pagination:** Use `page_number` and `items_per_page` for large datasets. Set `items_per_page=0` to get all results.
* **Total count:** The `arrayTotal` field shows total records across all pages.
* **Automatic reconnection:** Built-in protection against transient gRPC errors.
* **Connection required:** Call `connect_by_host_port()` or `connect_by_server_name()` first.
* **Thread safety:** Safe to call concurrently from multiple asyncio tasks.
* **UUID handling:** The terminal instance UUID is auto-generated by the server if not provided. 
  For explicit control (e.g., in streaming scenarios), pass `id_=uuid4()` to constructor.
  
---

## 🔗 Usage Examples

### 1) Get last 7 days history

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
        # Last 7 days
        to_dt = datetime.utcnow()
        from_dt = to_dt - timedelta(days=7)

        data = await account.order_history(
            from_dt=from_dt,
            to_dt=to_dt,
            sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
            items_per_page=100
        )

        print(f"Total records: {data.arrayTotal}")
        print(f"Returned: {len(data.history_data)} records")

        for item in data.history_data:
            if item.history_deal:
                deal = item.history_deal
                print(f"Deal #{deal.ticket}: ${deal.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Get history with pagination

```python
async def get_all_history_paginated(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    page_size: int = 100
):
    """Get all history records using pagination"""
    all_records = []
    page = 0

    while True:
        data = await account.order_history(
            from_dt=from_dt,
            to_dt=to_dt,
            sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_ASC,
            page_number=page,
            items_per_page=page_size
        )

        print(f"[OK] Page {page + 1}: {len(data.history_data)} records")

        all_records.extend(data.history_data)

        # Check if we got all records
        if len(all_records) >= data.arrayTotal:
            break

        page += 1

    print(f"[OK] Total records retrieved: {len(all_records)}")
    return all_records

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
history = await get_all_history_paginated(account, from_dt, to_dt)
```

### 3) Calculate total profit for period

```python
async def calculate_period_profit(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> float:
    """Calculate total profit for time period"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0  # Get all
    )

    total_profit = 0.0
    for item in data.history_data:
        if item.history_deal:
            total_profit += item.history_deal.profit

    print(f"Total profit ({from_dt.date()} to {to_dt.date()}): ${total_profit:+.2f}")
    return total_profit

# Usage:
from_dt = datetime(2024, 1, 1)
to_dt = datetime(2024, 1, 31)
profit = await calculate_period_profit(account, from_dt, to_dt)
```

### 4) Get today's trading history

```python
async def get_today_history(account: MT5Account):
    """Get all trades from today"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    data = await account.order_history(
        from_dt=today_start,
        to_dt=now,
        sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC
    )

    print(f"\nToday's trading activity:")
    print(f"Total records: {data.arrayTotal}")

    for item in data.history_data:
        if item.history_deal:
            deal = item.history_deal
            time = deal.time.ToDatetime()
            print(f"  {time.strftime('%H:%M:%S')} - "
                  f"#{deal.ticket} {deal.symbol}: ${deal.profit:+.2f}")

    return data

# Usage:
await get_today_history(account)
```

### 5) Export history to CSV

```python
import csv

async def export_history_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "order_history.csv"
):
    """Export order history to CSV file"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Time', 'Symbol', 'Type', 'Volume',
            'Price', 'Profit', 'Commission', 'Swap'
        ])

        for item in data.history_data:
            if item.history_deal:
                deal = item.history_deal
                time = deal.time.ToDatetime()
                writer.writerow([
                    deal.ticket,
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    deal.symbol,
                    deal.type,
                    deal.volume,
                    deal.price,
                    deal.profit,
                    deal.commission,
                    deal.swap
                ])

    print(f"[OK] Exported {data.arrayTotal} records to {filename}")

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
await export_history_to_csv(account, from_dt, to_dt)
```

### 6) Get winning vs losing trades

```python
async def analyze_win_loss(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analyze winning vs losing trades"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for item in data.history_data:
        if item.history_deal:
            profit = item.history_deal.profit
            if profit > 0:
                wins += 1
                total_win_profit += profit
            elif profit < 0:
                losses += 1
                total_loss_profit += profit

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    result = {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_win_profit": total_win_profit,
        "total_loss_profit": total_loss_profit,
        "net_profit": total_win_profit + total_loss_profit
    }

    print(f"\nTrading Statistics:")
    print(f"  Total trades: {total_trades}")
    print(f"  Wins: {wins} ({win_rate:.1f}%)")
    print(f"  Losses: {losses}")
    print(f"  Win profit: ${total_win_profit:.2f}")
    print(f"  Loss profit: ${total_loss_profit:.2f}")
    print(f"  Net profit: ${result['net_profit']:+.2f}")

    return result

# Usage:
from_dt = datetime.utcnow() - timedelta(days=30)
to_dt = datetime.utcnow()
stats = await analyze_win_loss(account, from_dt, to_dt)
```

---

## Common Patterns

### Get history for specific symbol

```python
async def get_symbol_history(
    account: MT5Account,
    symbol: str,
    from_dt: datetime,
    to_dt: datetime
):
    """Filter history by symbol"""
    data = await account.order_history(from_dt=from_dt, to_dt=to_dt)

    symbol_deals = [
        item for item in data.history_data
        if item.history_deal and item.history_deal.symbol == symbol
    ]

    return symbol_deals
```

### Calculate daily profit

```python
from collections import defaultdict

async def get_daily_profit(account: MT5Account, from_dt: datetime, to_dt: datetime):
    """Calculate profit per day"""
    data = await account.order_history(from_dt=from_dt, to_dt=to_dt, items_per_page=0)

    daily_profit = defaultdict(float)

    for item in data.history_data:
        if item.history_deal:
            deal = item.history_deal
            date = deal.time.ToDatetime().date()
            daily_profit[date] += deal.profit

    return dict(daily_profit)
```

---

## 📚 See also

* [positions_history](./positions_history.md) - Get historical closed positions
* [opened_orders](./opened_orders.md) - Get currently open orders
* [positions_total](./positions_total.md) - Get count of open positions
