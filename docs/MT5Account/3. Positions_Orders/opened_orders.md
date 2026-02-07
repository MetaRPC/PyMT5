# Get Currently Opened Orders and Positions

> **Request:** complete snapshot of all currently opened orders and positions with full details.

**API Information:**

* **Low-level API:** `MT5Account.opened_orders(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.AccountHelper`
* **Proto definition:** `OpenedOrders` (defined in `mt5-term-api-account-helper.proto`)

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `OpenedOrders(OpenedOrdersRequest) -> OpenedOrdersReply`
* **Low-level client (generated):** `AccountHelperStub.OpenedOrders(request, metadata, timeout)`

## 💬 Just the essentials

* **What it is.** Get comprehensive details of all pending orders and open positions.
* **Why you need it.** Complete overview of current trading state with full order/position details.
* **When to use.** Use this for full details. Use `positions_total()` for just counts, `opened_orders_tickets()` for ticket IDs only.

---

## 🎯 Purpose

Use it to get detailed information about current orders and positions:

* Get all pending orders (Buy Limit, Sell Stop, etc.)
* Get all open positions (Buy/Sell with P/L)
* Monitor current trading state
* Implement position management logic
* Display current orders/positions in UI
* Calculate total exposure

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**-> [opened_orders - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW.md)**

---

## Method Signature

```python
async def opened_orders(
    self,
    sort_mode: account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE = account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OpenedOrdersData
```

**Request message:**

```protobuf
message OpenedOrdersRequest {
  BMT5_ENUM_OPENED_ORDER_SORT_TYPE inputSortMode = 1;
}
```

**Reply message:**

```protobuf
message OpenedOrdersReply {
  oneof response {
    OpenedOrdersData data = 1;
    Error error = 2;
  }
}

message OpenedOrdersData {
  repeated OpenedOrderInfo opened_orders = 1;
  repeated PositionInfo position_infos = 2;
}
```

---

## 🔽 Input

| Parameter     | Type                              | Description                                             |
| ------------- | --------------------------------- | ------------------------------------------------------- |
| `sort_mode`   | `BMT5_ENUM_OPENED_ORDER_SORT_TYPE` (enum) | Sort mode for orders (by time or ticket ID) |
| `deadline`    | `datetime` (optional)             | Deadline for the gRPC call (UTC datetime)              |
| `cancellation_event` | `asyncio.Event` (optional) | Event to cancel the operation                    |

**Deadline options:**

```python
from datetime import datetime, timedelta
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# With sort mode and deadline
deadline = datetime.utcnow() + timedelta(seconds=5)
data = await account.opened_orders(
    sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline=deadline
)

# Default sort (by open time ascending)
data = await account.opened_orders()
```

---

## ⬆️ Output - `OpenedOrdersData`

| Field             | Type                        | Python Type               | Description                              |
| ----------------- | --------------------------- | ------------------------- | ---------------------------------------- |
| `opened_orders`   | `repeated OpenedOrderInfo`  | `list[OpenedOrderInfo]`   | List of pending orders                   |
| `position_infos`  | `repeated PositionInfo`     | `list[PositionInfo]`      | List of open positions                   |

**Return value:** The method returns `OpenedOrdersData` object with both lists accessible as attributes.

---

## 🧱 Related enums (from proto)

> **Note:** In Python code, you can use the enum from account_helper_pb2 module. This method uses **7 enums** with **40 total constants**.

### `BMT5_ENUM_OPENED_ORDER_SORT_TYPE`

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC` | 0 | Sort by open time (oldest first) |
| `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_DESC` | 1 | Sort by open time (newest first) |
| `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_ASC` | 2 | Sort by ticket ID (ascending) |
| `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_DESC` | 3 | Sort by ticket ID (descending) |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.opened_orders(
    sort_mode=pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
```

### `BMT5_ENUM_ORDER_TYPE` (for field `OpenedOrderInfo.type`)

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_TYPE_BUY` | 0 | Market Buy order (long position) |
| `BMT5_ORDER_TYPE_SELL` | 1 | Market Sell order (short position) |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Buy Limit pending order |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Sell Limit pending order |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Buy Stop pending order |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Sell Stop pending order |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Buy Stop Limit order |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Sell Stop Limit order |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Order to close by opposite position |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check order type
for order in data.opened_orders:
    if order.type == pb2.BMT5_ORDER_TYPE_BUY_LIMIT:
        print(f"Buy Limit order: {order.ticket}")
```

### `BMT5_ENUM_ORDER_STATE` (for field `OpenedOrderInfo.state`)

Defined in `mt5-term-api-account-helper.proto`.

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
| `BMT5_ORDER_STATE_REQUEST_MODIFY` | 8 | Order is being modified (changing parameters) |
| `BMT5_ORDER_STATE_REQUEST_CANCEL` | 9 | Order is being deleted (deleting from trading system) |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check order state
for order in data.opened_orders:
    if order.state == pb2.BMT5_ORDER_STATE_PLACED:
        print(f"Order {order.ticket} is active")
```

### `BMT5_ENUM_ORDER_TYPE_FILLING` (for field `OpenedOrderInfo.type_filling`)

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill - fill completely or cancel |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel - fill available volume |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Return execution mode |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel - place order in book |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check filling type
for order in data.opened_orders:
    if order.type_filling == pb2.BMT5_ORDER_FILLING_FOK:
        print(f"Order {order.ticket} uses Fill-or-Kill")
```

### `BMT5_ENUM_ORDER_TYPE_TIME` (for field `OpenedOrderInfo.type_time`)

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_ORDER_TIME_GTC` | 0 | Good Till Cancelled |
| `BMT5_ORDER_TIME_DAY` | 1 | Good Till Day (until end of day) |
| `BMT5_ORDER_TIME_SPECIFIED` | 2 | Good Till Specified time |
| `BMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Good Till Specified day (until end of specified day) |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check time type
for order in data.opened_orders:
    if order.type_time == pb2.BMT5_ORDER_TIME_GTC:
        print(f"Order {order.ticket} is GTC")
```

### `BMT5_ENUM_POSITION_TYPE` (for field `PositionInfo.type`)

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_POSITION_TYPE_BUY` | 0 | Buy position (long) |
| `BMT5_POSITION_TYPE_SELL` | 1 | Sell position (short) |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check position type
for pos in data.position_infos:
    if pos.type == pb2.BMT5_POSITION_TYPE_BUY:
        print(f"Long position: {pos.ticket}")
```

### `BMT5_ENUM_POSITION_REASON` (for field `PositionInfo.reason`)

Defined in `mt5-term-api-account-helper.proto`.

| Constant | Value | Description |
|----------|-------|-------------|
| `BMT5_POSITION_REASON_CLIENT` | 0 | Position opened manually by client |
| `BMT5_POSITION_REASON_MOBILE` | 1 | Position opened via mobile application |
| `BMT5_POSITION_REASON_WEB` | 2 | Position opened via web platform |
| `BMT5_POSITION_REASON_EXPERT` | 3 | Position opened by Expert Advisor |
| `ORDER_REASON_SL` | 4 | Position closed by Stop Loss |
| `ORDER_REASON_TP` | 5 | Position closed by Take Profit |
| `ORDER_REASON_SO` | 6 | Position closed by Stop Out |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Check position reason
for pos in data.position_infos:
    if pos.reason == pb2.BMT5_POSITION_REASON_EXPERT:
        print(f"Position {pos.ticket} opened by EA")
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_with_reconnect`.
* **Default timeout:** If `deadline` is `None`, the method will wait indefinitely (or until server timeout).
* **Two separate lists:** Orders and positions are returned in separate lists - check both.
* **Connection required:** You must call `connect_by_host_port()` or `connect_by_server_name()` before using this method.
* **Full details:** This method returns complete order/position information - use `opened_orders_tickets()` for lighter payload.
* **Thread safety:** All async methods are safe to call concurrently from multiple asyncio tasks.
* **UUID handling:** The terminal instance UUID is auto-generated by the server if not provided. For explicit control (e.g., in streaming scenarios), pass `id_=uuid4()` to constructor.

---

## 🔗 Usage Examples

### 1) Get all opened orders and positions

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
        deadline = datetime.utcnow() + timedelta(seconds=5)

        data = await account.opened_orders(
            sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
            deadline=deadline
        )

        print(f"Pending orders: {len(data.opened_orders)}")
        print(f"Open positions: {len(data.position_infos)}")

        # Show positions
        for pos in data.position_infos:
            print(f"Position #{pos.ticket} {pos.symbol}: "
                  f"{pos.volume} lots @ {pos.price_open}, P/L: ${pos.profit:.2f}")

        # Show orders
        for order in data.opened_orders:
            print(f"Order #{order.ticket} {order.symbol}: "
                  f"{order.volume_initial} lots @ {order.price_open}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Count orders and positions separately

```python
async def get_opened_summary(account: MT5Account) -> dict:
    """Get summary of opened orders and positions"""
    data = await account.opened_orders()

    summary = {
        "orders_count": len(data.opened_orders),
        "positions_count": len(data.position_infos),
        "total_count": len(data.opened_orders) + len(data.position_infos)
    }

    print(f"[OK] Pending orders: {summary['orders_count']}")
    print(f"[OK] Open positions: {summary['positions_count']}")
    print(f"[OK] Total: {summary['total_count']}")

    return summary

# Usage:
summary = await get_opened_summary(account)
```

### 3) Calculate total floating P/L

```python
async def get_total_profit(account: MT5Account) -> float:
    """Calculate total floating profit/loss from all positions"""
    data = await account.opened_orders()

    total_profit = sum(pos.profit for pos in data.position_infos)

    print(f"Total floating P/L: ${total_profit:+.2f}")
    return total_profit

# Usage:
profit = await get_total_profit(account)
if profit < 0:
    print(f"[WARNING] Account in loss: ${profit:.2f}")
```

### 4) Find positions by symbol

```python
async def get_positions_by_symbol(
    account: MT5Account,
    symbol: str
) -> list:
    """Get all open positions for specific symbol"""
    data = await account.opened_orders()

    positions = [
        pos for pos in data.position_infos
        if pos.symbol == symbol
    ]

    print(f"[OK] Found {len(positions)} position(s) for {symbol}")
    return positions

# Usage:
eurusd_positions = await get_positions_by_symbol(account, "EURUSD")
for pos in eurusd_positions:
    print(f"  #{pos.ticket}: {pos.volume} lots, P/L: ${pos.profit:.2f}")
```

### 5) Display positions with details

```python
async def display_positions(account: MT5Account):
    """Display all positions with formatted output"""
    data = await account.opened_orders()

    if not data.position_infos:
        print("[INFO] No open positions")
        return

    print(f"\n{'='*80}")
    print(f"OPEN POSITIONS ({len(data.position_infos)})")
    print(f"{'='*80}")
    print(f"{'Ticket':<12} {'Symbol':<10} {'Volume':<8} {'Price':<10} {'Current':<10} {'Profit':<12}")
    print(f"{'-'*80}")

    for pos in data.position_infos:
        type_str = "BUY" if pos.type == 0 else "SELL"
        print(f"{pos.ticket:<12} {pos.symbol:<10} {pos.volume:<8.2f} "
              f"{pos.price_open:<10.5f} {pos.price_current:<10.5f} ${pos.profit:+11.2f}")

    total = sum(pos.profit for pos in data.position_infos)
    print(f"{'-'*80}")
    print(f"{'TOTAL:':<62} ${total:+11.2f}")
    print(f"{'='*80}\n")

# Usage:
await display_positions(account)
```

### 6) Monitor for new orders/positions

```python
async def monitor_opened(account: MT5Account, interval: float = 5.0):
    """Monitor for changes in orders/positions"""
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders()

            # Collect all current tickets
            current_tickets = set()
            for order in data.opened_orders:
                current_tickets.add(("ORDER", order.ticket))
            for pos in data.position_infos:
                current_tickets.add(("POSITION", pos.ticket))

            # Detect new items
            if previous_tickets:
                new_items = current_tickets - previous_tickets
                closed_items = previous_tickets - current_tickets

                for item_type, ticket in new_items:
                    print(f"[+] New {item_type}: #{ticket}")

                for item_type, ticket in closed_items:
                    print(f"[-] Closed {item_type}: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)

# Usage:
# await monitor_opened(account, interval=5.0)
```

### 7) Get positions sorted by profit

```python
async def get_worst_positions(account: MT5Account, limit: int = 5):
    """Get positions with worst performance"""
    data = await account.opened_orders()

    # Sort by profit (worst first)
    sorted_positions = sorted(
        data.position_infos,
        key=lambda p: p.profit
    )

    worst = sorted_positions[:limit]

    print(f"\nWorst {limit} positions:")
    for i, pos in enumerate(worst, 1):
        print(f"{i}. #{pos.ticket} {pos.symbol}: ${pos.profit:+.2f}")

    return worst

# Usage:
worst = await get_worst_positions(account, limit=5)
```

### 8) Check if symbol has open position

```python
async def has_position_for_symbol(
    account: MT5Account,
    symbol: str
) -> bool:
    """Check if symbol has open position"""
    data = await account.opened_orders()

    has_pos = any(pos.symbol == symbol for pos in data.position_infos)

    if has_pos:
        print(f"[OK] Position found for {symbol}")
    else:
        print(f"[INFO] No position for {symbol}")

    return has_pos

# Usage:
if not await has_position_for_symbol(account, "EURUSD"):
    print("Can open new EURUSD position")
```

---

## Common Patterns

### Quick position lookup

```python
async def get_position_by_ticket(account: MT5Account, ticket: int):
    """Find specific position by ticket"""
    data = await account.opened_orders()
    for pos in data.position_infos:
        if pos.ticket == ticket:
            return pos
    return None
```

### Calculate exposure by symbol

```python
async def get_symbol_exposure(account: MT5Account) -> dict:
    """Calculate total volume per symbol"""
    data = await account.opened_orders()

    exposure = {}
    for pos in data.position_infos:
        exposure[pos.symbol] = exposure.get(pos.symbol, 0) + pos.volume

    return exposure
```

---

## 📚 See also

* [positions_total](./positions_total.md) - Get count only (faster)
* [opened_orders_tickets](./opened_orders_tickets.md) - Get ticket IDs only
* [positions_history](./positions_history.md) - Get historical closed positions
* [order_history](./order_history.md) - Get historical orders
