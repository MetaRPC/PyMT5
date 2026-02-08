# Stream Trade Events

> **Request:** subscribe to all trade-related events: orders, deals, positions.

**API Information:**

* **Python API:** `MT5Account.on_trade(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.SubscriptionService`
* **Proto definition:** `OnTrade` (defined in `mt5-term-api-subscriptions.proto`)

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnTrade(OnTradeRequest) -> stream OnTradeReply`
* **Low-level client (generated):** `SubscriptionServiceStub.OnTrade(request, metadata)`

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_trade(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to all trade-related events: orders, deals, positions.

        Yields:
            OnTradeData: Trade event data.
        """
```

**Request message:**

```protobuf
message OnTradeRequest {
  // No parameters - subscribes to all trade events
}
```

## 💬 Just the essentials

* **What it is.** Real-time stream of all trading activity on the account.
* **Why you need it.** Monitor trades, detect position changes, track order execution.
* **Event-driven.** Updates triggered immediately when trading events occur.

---

## 🎯 Purpose

Use it to:

* Monitor all trading activity in real-time
* Detect when positions are opened or closed
* Track pending order lifecycle
* Build trade event logging systems
* Implement trade notifications
* Synchronize local state with MT5


---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel streaming (optional)          |

---

## ⬆️ Output - Async Generator

Returns an async generator that yields `OnTradeData` objects.

**OnTradeData fields:**

| Field                         | Type                      | Description                          |
| ----------------------------- | ------------------------- | ------------------------------------ |
| `type`                        | `int`                     | Event type                           |
| `event_data`                  | `OnTradeEventData`        | Detailed event information           |
| `account_info`                | `OnEventAccountInfo`      | Current account state                |
| `terminal_instance_guid_id`   | `str`                     | Terminal instance identifier         |

**OnTradeEventData fields (all are repeated/lists):**

| Field                         | Type                              | Description                          |
| ----------------------------- | --------------------------------- | ------------------------------------ |
| `new_orders`                  | `repeated OnTradeOrderInfo`       | New pending orders created           |
| `disappeared_orders`          | `repeated OnTradeOrderInfo`       | Pending orders removed               |
| `state_changed_orders`        | `repeated OnTradeOrderStateChange`| Orders with state changes            |
| `new_positions`               | `repeated OnTradePositionInfo`    | New positions opened                 |
| `disappeared_positions`       | `repeated OnTradePositionInfo`    | Positions closed                     |
| `updated_positions`           | `repeated OnTradePositionUpdate`  | Positions modified                   |
| `new_history_orders`          | `repeated OnTradeHistoryOrderInfo`| New historical orders                |
| `disappeared_history_orders`  | `repeated OnTradeHistoryOrderInfo`| Historical orders removed            |
| `updated_history_orders`      | `repeated OnTradeHistoryOrderUpdate`| Historical orders updated          |
| `new_history_deals`           | `repeated OnTradeHistoryDealInfo` | New deals in history                 |
| `disappeared_history_deals`   | `repeated OnTradeHistoryDealInfo` | Deals removed from history           |
| `updated_history_deals`       | `repeated OnTradeHistoryDealUpdate`| Deals updated in history            |

**Structure and ENUMs usage:**

```
OnTradeData
├── type (MT5_SUB_ENUM_EVENT_GROUP_TYPE) - Event group type
├── event_data (OnTradeEventData)
│   ├── new_positions (list[OnTradePositionInfo])
│   │   └── Uses: SUB_ENUM_POSITION_TYPE, SUB_ENUM_POSITION_REASON
│   ├── disappeared_positions (list[OnTradePositionInfo])
│   │   └── Uses: SUB_ENUM_POSITION_TYPE, SUB_ENUM_POSITION_REASON
│   ├── new_orders (list[OnTradeOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_ORDER_REASON
│   ├── disappeared_orders (list[OnTradeOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_ORDER_REASON
│   ├── new_history_orders (list[OnTradeHistoryOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_DEAL_REASON
│   ├── disappeared_history_orders (list[OnTradeHistoryOrderInfo])
│   │   └── Uses: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │              SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │              SUB_ENUM_DEAL_REASON
│   ├── new_history_deals (list[OnTradeHistoryDealInfo])
│   │   └── Uses: SUB_ENUM_DEAL_TYPE, SUB_ENUM_DEAL_ENTRY, SUB_ENUM_DEAL_REASON
│   └── disappeared_history_deals (list[OnTradeHistoryDealInfo])
│       └── Uses: SUB_ENUM_DEAL_TYPE, SUB_ENUM_DEAL_ENTRY, SUB_ENUM_DEAL_REASON
├── account_info (OnEventAccountInfo)
└── terminal_instance_guid_id (str)
```

---

**Event group type enum (MT5_SUB_ENUM_EVENT_GROUP_TYPE):**

Used in `OnTradeData.type` field:

| Name           | Value | Description                          |
| -------------- | ----- | ------------------------------------ |
| `OrderProfit`  | 0     | Order profit event                   |
| `OrderUpdate`  | 1     | Order update event                   |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.OrderProfit   # = 0
```

---

**Enums used in nested structures:**

The following enums are used by the nested message types inside `OnTradeEventData`:

| Nested Structure              | Used in Fields                                    | Enums Used                                                                                                      |
| ----------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `OnTradePositionInfo`         | `new_positions`, `disappeared_positions`          | `SUB_ENUM_POSITION_TYPE`, `SUB_ENUM_POSITION_REASON`                                                           |
| `OnTradeOrderInfo`            | `new_orders`, `disappeared_orders`                | `SUB_ENUM_ORDER_TYPE`, `SUB_ENUM_ORDER_STATE`, `SUB_ENUM_ORDER_TYPE_TIME`, `SUB_ENUM_ORDER_TYPE_FILLING`, `SUB_ENUM_ORDER_REASON` |
| `OnTradeHistoryOrderInfo`     | `new_history_orders`, `disappeared_history_orders`| `SUB_ENUM_ORDER_TYPE`, `SUB_ENUM_ORDER_STATE`, `SUB_ENUM_ORDER_TYPE_TIME`, `SUB_ENUM_ORDER_TYPE_FILLING`, `SUB_ENUM_DEAL_REASON`  |
| `OnTradeHistoryDealInfo`      | `new_history_deals`, `disappeared_history_deals`  | `SUB_ENUM_DEAL_TYPE`, `SUB_ENUM_DEAL_ENTRY`, `SUB_ENUM_DEAL_REASON`                                            |

**Position type enum (SUB_ENUM_POSITION_TYPE):**

| Name                       | Value | Description                          |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_POSITION_TYPE_BUY`    | 0     | Buy position                         |
| `SUB_POSITION_TYPE_SELL`   | 1     | Sell position                        |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
```

**Position reason enum (SUB_ENUM_POSITION_REASON):**

| Name                           | Value | Description                          |
| ------------------------------ | ----- | ------------------------------------ |
| `SUB_POSITION_REASON_CLIENT`   | 0     | Position opened from desktop terminal|
| `SUB_POSITION_REASON_MOBILE`   | 1     | Position opened from mobile app      |
| `SUB_POSITION_REASON_WEB`      | 2     | Position opened from web terminal    |
| `SUB_POSITION_REASON_EXPERT`   | 3     | Position opened by Expert Advisor    |
| `SUB_POSITION_REASON_SL`       | 4     | Position closed by Stop Loss         |
| `SUB_POSITION_REASON_TP`       | 5     | Position closed by Take Profit       |
| `SUB_POSITION_REASON_SO`       | 6     | Position closed by Stop Out          |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_POSITION_REASON_CLIENT  # = 0
```

**Order type enum (SUB_ENUM_ORDER_TYPE):**

| Name                              | Value | Description                          |
| --------------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_TYPE_BUY`              | 0     | Market buy order                     |
| `SUB_ORDER_TYPE_SELL`             | 1     | Market sell order                    |
| `SUB_ORDER_TYPE_BUY_LIMIT`        | 2     | Buy limit pending order              |
| `SUB_ORDER_TYPE_SELL_LIMIT`       | 3     | Sell limit pending order             |
| `SUB_ORDER_TYPE_BUY_STOP`         | 4     | Buy stop pending order               |
| `SUB_ORDER_TYPE_SELL_STOP`        | 5     | Sell stop pending order              |
| `SUB_ORDER_TYPE_BUY_STOP_LIMIT`   | 6     | Buy stop limit pending order         |
| `SUB_ORDER_TYPE_SELL_STOP_LIMIT`  | 7     | Sell stop limit pending order        |
| `SUB_ORDER_TYPE_CLOSE_BY`         | 8     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_TYPE_BUY   # = 0
```

**Order state enum (SUB_ENUM_ORDER_STATE):**

| Name                              | Value | Description                          |
| --------------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_STATE_STARTED`         | 0     | Order checked, but not yet accepted  |
| `SUB_ORDER_STATE_PLACED`          | 1     | Order accepted                       |
| `SUB_ORDER_STATE_CANCELED`        | 2     | Order canceled by client             |
| `SUB_ORDER_STATE_PARTIAL`         | 3     | Order partially executed             |
| `SUB_ORDER_STATE_FILLED`          | 4     | Order fully executed                 |
| `SUB_ORDER_STATE_REJECTED`        | 5     | Order rejected                       |
| `SUB_ORDER_STATE_EXPIRED`         | 6     | Order expired                        |
| `SUB_ORDER_STATE_REQUEST_ADD`     | 7     | Order being registered               |
| `SUB_ORDER_STATE_REQUEST_MODIFY`  | 8     | Order being modified                 |
| `SUB_ORDER_STATE_REQUEST_CANCEL`  | 9     | Order being deleted                  |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_STATE_STARTED   # = 0
```

**Deal type enum (SUB_ENUM_DEAL_TYPE):**

| Name                                  | Value | Description                          |
| ------------------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_TYPE_BUY`                   | 0     | Buy deal                             |
| `SUB_DEAL_TYPE_SELL`                  | 1     | Sell deal                            |
| `SUB_DEAL_TYPE_BALANCE`               | 2     | Balance operation                    |
| `SUB_DEAL_TYPE_CREDIT`                | 3     | Credit operation                     |
| `SUB_DEAL_TYPE_CHARGE`                | 4     | Additional charge                    |
| `SUB_DEAL_TYPE_CORRECTION`            | 5     | Correction                           |
| `SUB_DEAL_TYPE_BONUS`                 | 6     | Bonus                                |
| `SUB_DEAL_TYPE_COMMISSION`            | 7     | Commission                           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_TYPE_BUY   # = 0
```

**Order time type enum (SUB_ENUM_ORDER_TYPE_TIME):**

| Name                           | Value | Description                          |
| ------------------------------ | ----- | ------------------------------------ |
| `SUB_ORDER_TIME_GTC`           | 0     | Good till cancel                     |
| `SUB_ORDER_TIME_DAY`           | 1     | Good till current trading day        |
| `SUB_ORDER_TIME_SPECIFIED`     | 2     | Good till specified date             |
| `SUB_ORDER_TIME_SPECIFIED_DAY` | 3     | Good till specified day              |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_TIME_GTC   # = 0
```

**Order filling type enum (SUB_ENUM_ORDER_TYPE_FILLING):**

| Name                         | Value | Description                          |
| ---------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_FILLING_FOK`      | 0     | Fill or Kill                         |
| `SUB_ORDER_FILLING_IOC`      | 1     | Immediate or Cancel                  |
| `SUB_ORDER_FILLING_BOC`      | 2     | Book or Cancel                       |
| `SUB_ORDER_FILLING_RETURN`   | 3     | Return                               |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_FILLING_FOK   # = 0
```

**Order reason enum (SUB_ENUM_ORDER_REASON):**

| Name                         | Value | Description                          |
| ---------------------------- | ----- | ------------------------------------ |
| `SUB_ORDER_REASON_CLIENT`    | 0     | Order placed from desktop terminal   |
| `SUB_ORDER_REASON_MOBILE`    | 2     | Order placed from mobile app         |
| `SUB_ORDER_REASON_WEB`       | 3     | Order placed from web terminal       |
| `SUB_ORDER_REASON_EXPERT`    | 4     | Order placed by Expert Advisor       |
| `SUB_ORDER_REASON_SL`        | 5     | Order triggered by Stop Loss         |
| `SUB_ORDER_REASON_TP`        | 6     | Order triggered by Take Profit       |
| `SUB_ORDER_REASON_SO`        | 7     | Order triggered by Stop Out          |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_ORDER_REASON_CLIENT   # = 0
```

**Deal entry type enum (SUB_ENUM_DEAL_ENTRY):**

| Name                       | Value | Description                          |
| -------------------------- | ----- | ------------------------------------ |
| `SUB_DEAL_ENTRY_IN`        | 0     | Entry into market                    |
| `SUB_DEAL_ENTRY_OUT`       | 1     | Exit from market                     |
| `SUB_DEAL_ENTRY_INOUT`     | 2     | Reverse                              |
| `SUB_DEAL_ENTRY_OUT_BY`    | 3     | Close by opposite position           |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_ENTRY_IN   # = 0
```

**Deal reason enum (SUB_ENUM_DEAL_REASON):**

| Name                                 | Value | Description                          |
| ------------------------------------ | ----- | ------------------------------------ |
| `SUB_DEAL_REASON_CLIENT`             | 0     | Deal from desktop terminal           |
| `SUB_DEAL_REASON_MOBILE`             | 1     | Deal from mobile app                 |
| `SUB_DEAL_REASON_WEB`                | 2     | Deal from web terminal               |
| `SUB_DEAL_REASON_EXPERT`             | 3     | Deal by Expert Advisor               |
| `SUB_DEAL_REASON_SL`                 | 4     | Deal by Stop Loss                    |
| `SUB_DEAL_REASON_TP`                 | 5     | Deal by Take Profit                  |
| `SUB_DEAL_REASON_SO`                 | 6     | Deal by Stop Out                     |
| `SUB_DEAL_REASON_ROLLOVER`           | 7     | Deal by rollover                     |
| `SUB_DEAL_REASON_VMARGIN`            | 8     | Deal by variation margin             |
| `SUB_DEAL_REASON_SPLIT`              | 9     | Deal by split                        |
| `SUB_DEAL_REASON_CORPORATE_ACTION`   | 10    | Deal by corporate action             |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
subscriptions_pb2.SUB_DEAL_REASON_CLIENT   # = 0
```

---


## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OnTrade - How it works](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` streaming methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_stream_with_reconnect`.
* **Async generator:** The method returns an async generator - use `async for` to consume data.
* **No parameters:** This stream subscribes to ALL trade events automatically.
* **Comprehensive:** Tracks orders, positions, and deals (both active and historical).
* **Event-driven:** Updates arrive immediately when events occur (not periodic).
* **Multiple lists:** Each update may contain multiple types of events simultaneously.
* **Resource management:** Always cancel streams when done to free resources.

---

## 🔗 Usage Examples

### 1) Monitor all trade events

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_trades():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # New positions
            if event.new_positions:
                for pos in event.new_positions:
                    print(f"[NEW POSITION] #{pos.index}")

            # Closed positions
            if event.disappeared_positions:
                for pos in event.disappeared_positions:
                    print(f"[CLOSED POSITION] #{pos.index}")

            # Updated positions
            if event.updated_positions:
                for pos in event.updated_positions:
                    print(f"[UPDATED POSITION] #{pos.index}")

            # New pending orders
            if event.new_orders:
                for order in event.new_orders:
                    print(f"[NEW ORDER] #{order.index}")

            # Removed pending orders
            if event.disappeared_orders:
                for order in event.disappeared_orders:
                    print(f"[REMOVED ORDER] #{order.index}")

            # Account info
            if trade_data.account_info:
                acc = trade_data.account_info
                print(f"[ACCOUNT] Balance: ${acc.balance:.2f}, "
                      f"Equity: ${acc.equity:.2f}\n")

    except KeyboardInterrupt:
        print("Stopping trade monitor...")

    finally:
        await account.channel.close()

asyncio.run(monitor_trades())
```

### 2) Trade event logger

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_trade_events():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    event_count = 0

    try:
        async for trade_data in account.on_trade():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event = trade_data.event_data

            # Log new positions
            for pos in event.new_positions:
                event_count += 1
                print(f"[{timestamp}] NEW_POSITION | Index: {pos.index}")

            # Log closed positions
            for pos in event.disappeared_positions:
                event_count += 1
                print(f"[{timestamp}] CLOSED_POSITION | Index: {pos.index}")

            # Log updated positions
            for pos in event.updated_positions:
                event_count += 1
                print(f"[{timestamp}] UPDATED_POSITION | Index: {pos.index}")

            # Log new pending orders
            for order in event.new_orders:
                event_count += 1
                print(f"[{timestamp}] NEW_ORDER | Index: {order.index}")

            # Log order state changes
            for order in event.state_changed_orders:
                event_count += 1
                print(f"[{timestamp}] ORDER_STATE_CHANGE | Index: {order.index}")

            # Log new deals
            for deal in event.new_history_deals:
                event_count += 1
                print(f"[{timestamp}] NEW_DEAL | Index: {deal.index}")

            if event_count % 10 == 0:
                print(f"\n--- Total events logged: {event_count} ---\n")

    except KeyboardInterrupt:
        print(f"\nStopping logger. Total events: {event_count}")

    finally:
        await account.channel.close()

asyncio.run(log_trade_events())
```

### 3) Position opened/closed tracker

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def track_position_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    active_positions = set()
    total_opened = 0
    total_closed = 0

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Track new positions
            for pos in event.new_positions:
                active_positions.add(pos.index)
                total_opened += 1
                print(f"[OPENED] Position #{pos.index}")
                print(f"   Active: {len(active_positions)}, "
                      f"Total opened: {total_opened}")

            # Track closed positions
            for pos in event.disappeared_positions:
                if pos.index in active_positions:
                    active_positions.remove(pos.index)
                total_closed += 1
                print(f"[CLOSED] Position #{pos.index}")
                print(f"   Active: {len(active_positions)}, "
                      f"Total closed: {total_closed}")

            # Show current state
            if event.new_positions or event.disappeared_positions:
                print(f"\n[STATS] Current state:")
                print(f"   Active positions: {len(active_positions)}")
                print(f"   Total opened: {total_opened}")
                print(f"   Total closed: {total_closed}")
                print(f"   Win rate: "
                      f"{(total_closed / total_opened * 100) if total_opened > 0 else 0:.1f}%\n")

    except KeyboardInterrupt:
        print("\nStopping tracker...")

    finally:
        await account.channel.close()

asyncio.run(track_position_lifecycle())
```

### 4) Real-time trade notifications

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def trade_notifications():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Notify on new positions
            if event.new_positions:
                count = len(event.new_positions)
                print(f"\n[NOTIFICATION] {count} new position(s) opened")

                if trade_data.account_info:
                    print(f"   Current balance: ${trade_data.account_info.balance:.2f}")
                    print(f"   Current equity: ${trade_data.account_info.equity:.2f}")

            # Notify on closed positions
            if event.disappeared_positions:
                count = len(event.disappeared_positions)
                print(f"\n[NOTIFICATION] {count} position(s) closed")

                if trade_data.account_info:
                    print(f"   Current balance: ${trade_data.account_info.balance:.2f}")
                    print(f"   Total profit: ${trade_data.account_info.profit:.2f}")

            # Notify on pending orders
            if event.new_orders:
                count = len(event.new_orders)
                print(f"\n[NOTIFICATION] {count} pending order(s) created")

            # Notify on order execution
            if event.disappeared_orders:
                count = len(event.disappeared_orders)
                print(f"\n[NOTIFICATION] {count} pending order(s) executed/cancelled")

    except KeyboardInterrupt:
        print("\nStopping notifications...")

    finally:
        await account.channel.close()

asyncio.run(trade_notifications())
```

### 5) Trade statistics collector

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def collect_trade_statistics(duration_seconds=300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    stats = {
        'positions_opened': 0,
        'positions_closed': 0,
        'positions_modified': 0,
        'orders_created': 0,
        'orders_removed': 0,
        'deals_executed': 0,
    }

    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for trade_data in account.on_trade(
            cancellation_event=cancel_event
        ):
            event = trade_data.event_data

            stats['positions_opened'] += len(event.new_positions)
            stats['positions_closed'] += len(event.disappeared_positions)
            stats['positions_modified'] += len(event.updated_positions)
            stats['orders_created'] += len(event.new_orders)
            stats['orders_removed'] += len(event.disappeared_orders)
            stats['deals_executed'] += len(event.new_history_deals)

        await stop_task

        # Print final statistics
        print("\n" + "=" * 60)
        print("TRADE STATISTICS REPORT")
        print("=" * 60)
        print(f"Positions opened:     {stats['positions_opened']:>6,}")
        print(f"Positions closed:     {stats['positions_closed']:>6,}")
        print(f"Positions modified:   {stats['positions_modified']:>6,}")
        print(f"Orders created:       {stats['orders_created']:>6,}")
        print(f"Orders removed:       {stats['orders_removed']:>6,}")
        print(f"Deals executed:       {stats['deals_executed']:>6,}")
        print("=" * 60)

    finally:
        await account.channel.close()

# Collect statistics for 5 minutes
asyncio.run(collect_trade_statistics(300))
```

### 6) Real-time trade synchronizer

```python
import asyncio
from MetaRpcMT5 import MT5Account

class TradeSynchronizer:
    def __init__(self):
        self.positions = {}  # index -> position data
        self.orders = {}     # index -> order data

    async def sync_trades(self, account):
        """Synchronize local state with MT5 account"""
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Sync positions
            for pos in event.new_positions:
                self.positions[pos.index] = pos
                print(f"[SYNC] Added position #{pos.index}")

            for pos in event.disappeared_positions:
                if pos.index in self.positions:
                    del self.positions[pos.index]
                    print(f"[SYNC] Removed position #{pos.index}")

            for pos in event.updated_positions:
                if pos.index in self.positions:
                    # Update position data
                    print(f"[SYNC] Updated position #{pos.index}")

            # Sync orders
            for order in event.new_orders:
                self.orders[order.index] = order
                print(f"[SYNC] Added order #{order.index}")

            for order in event.disappeared_orders:
                if order.index in self.orders:
                    del self.orders[order.index]
                    print(f"[SYNC] Removed order #{order.index}")

            # Show current state
            print(f"\n[STATE] Local state: {len(self.positions)} positions, "
                  f"{len(self.orders)} orders\n")

async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    synchronizer = TradeSynchronizer()

    try:
        await synchronizer.sync_trades(account)
    except KeyboardInterrupt:
        print("\nStopping synchronizer...")
    finally:
        await account.channel.close()

asyncio.run(main())
```

---

## 📚 See also

* [OnTradeTransaction](./on_trade_transaction.md) - More detailed transaction events
* [OnPositionProfit](./on_position_profit.md) - Stream position profit updates
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Get current positions snapshot
* [OrderHistory](../3.%20Positions_Orders/order_history.md) - Get historical orders
