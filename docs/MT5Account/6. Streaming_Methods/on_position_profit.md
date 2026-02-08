# Stream Real-Time Position Profit/Loss

> **Request:** subscribe to real-time profit/loss updates for open positions.

**API Information:**

* **Python API:** `MT5Account.on_position_profit(...)` (defined in `package/MetaRpcMT5/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.SubscriptionService`
* **Proto definition:** `OnPositionProfit` (defined in `mt5-term-api-subscriptions.proto`)

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnPositionProfit(OnPositionProfitRequest) -> stream OnPositionProfitReply`
* **Low-level client (generated):** `SubscriptionServiceStub.OnPositionProfit(request, metadata)`

---

## 💬 Just the essentials

* **What it is.** Periodic stream of position profit/loss updates.
* **Why you need it.** Monitor P&L, implement stop-loss logic, track account performance.
* **Periodic updates.** Updates sent at specified intervals (e.g., every 500ms).

---

## 🎯 Purpose

Use it to:

* Monitor real-time profit/loss for open positions
* Implement dynamic stop-loss and take-profit logic
* Track account performance in real-time
* Set up profit/loss alerts
* Build real-time P&L dashboards
* Detect position changes immediately

---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OnPositionProfit - How it works](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW.md)**

```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_position_profit(
        self,
        interval_ms: int,
        ignore_empty: bool = True,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to real-time profit updates for open positions.

        Yields:
            OnPositionProfitData: Profit update data.
        """
```

**Request message:**

```protobuf
message OnPositionProfitRequest {
  int32 timer_period_milliseconds = 1;  // Polling interval in milliseconds
  bool ignore_empty_data = 2;           // Skip frames with no changes (default: true)
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `interval_ms`        | `int`                          | Interval in milliseconds to poll the server   |
| `ignore_empty`       | `bool`                         | Skip frames with no change (default: True)    |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel streaming (optional)          |

---

## ⬆️ Output - Async Generator

Returns an async generator that yields `OnPositionProfitData` objects.

**OnPositionProfitData fields:**

| Field                         | Type                                   | Description                          |
| ----------------------------- | -------------------------------------- | ------------------------------------ |
| `type`                        | `int`                                  | Update type                          |
| `new_positions`               | `repeated OnPositionProfitPositionInfo`| Newly opened positions               |
| `updated_positions`           | `repeated OnPositionProfitPositionInfo`| Positions with profit changes        |
| `deleted_positions`           | `repeated OnPositionProfitPositionInfo`| Closed positions                     |
| `account_info`                | `OnEventAccountInfo`                   | Current account information          |
| `terminal_instance_guid_id`   | `str`                                  | Terminal instance identifier         |

**OnPositionProfitPositionInfo fields:**

| Field             | Type     | Description                              |
| ----------------- | -------- | ---------------------------------------- |
| `index`           | `int32`  | Position index in the list               |
| `ticket`          | `uint64` | Position ticket number                   |
| `profit`          | `double` | Current profit/loss                      |
| `position_symbol` | `string` | Trading symbol                           |

**OnEventAccountInfo fields:**

| Field             | Type     | Description                              |
| ----------------- | -------- | ---------------------------------------- |
| `balance`         | `double` | Account balance                          |
| `equity`          | `double` | Account equity                           |
| `profit`          | `double` | Total profit                             |
| `margin`          | `double` | Used margin                              |
| `margin_free`     | `double` | Free margin                              |

**Position type enum (SUB_ENUM_POSITION_TYPE):**

| Name                      | Value | Description                          |
| ------------------------- | ----- | ------------------------------------ |
| `SUB_POSITION_TYPE_BUY`   | 0     | Buy position (long)                  |
| `SUB_POSITION_TYPE_SELL`  | 1     | Sell position (short)                |

**Usage:**
```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

# Access enum values
subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
subscriptions_pb2.SUB_POSITION_TYPE_SELL  # = 1
```

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` streaming methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_stream_with_reconnect`.
* **Async generator:** The method returns an async generator - use `async for` to consume data.
* **Polling interval:** Choose interval based on your needs - shorter intervals = more frequent updates but higher load.
* **Ignore empty:** Set `ignore_empty=True` to skip updates when nothing changed (recommended).
* **Three lists:** Each update contains `new_positions`, `updated_positions`, and `deleted_positions`.
* **Account info:** Each update includes current account balance, equity, and margin.
* **Resource management:** Always cancel streams when done to free resources.

---

## 🔗 Usage Examples

### 1) Monitor all positions P&L

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_positions_pnl():
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
        # Poll every 500ms, skip empty updates
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            # New positions
            if update.new_positions:
                for pos in update.new_positions:
                    print(f"[NEW] Position #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L={pos.profit:.2f}")

            # Updated positions (profit changed)
            if update.updated_positions:
                for pos in update.updated_positions:
                    print(f"[UPDATE] Position #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L={pos.profit:.2f}")

            # Closed positions
            if update.deleted_positions:
                for pos in update.deleted_positions:
                    print(f"[CLOSED] Position #{pos.ticket} ({pos.position_symbol}): "
                          f"Final P&L={pos.profit:.2f}")

            # Account summary
            if update.account_info:
                acc = update.account_info
                print(f"[ACCOUNT] Balance={acc.balance:.2f}, "
                      f"Equity={acc.equity:.2f}, Profit={acc.profit:.2f}\n")

    except KeyboardInterrupt:
        print("Stopping stream...")

    finally:
        await account.channel.close()

asyncio.run(monitor_positions_pnl())
```

### 2) Real-time total P&L dashboard

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def realtime_pnl_dashboard():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Track all positions
    positions = {}  # ticket -> (symbol, profit)

    try:
        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True
        ):
            # Add new positions
            for pos in update.new_positions:
                positions[pos.ticket] = (pos.position_symbol, pos.profit)

            # Update existing positions
            for pos in update.updated_positions:
                positions[pos.ticket] = (pos.position_symbol, pos.profit)

            # Remove closed positions
            for pos in update.deleted_positions:
                if pos.ticket in positions:
                    del positions[pos.ticket]

            # Calculate total P&L
            total_profit = sum(profit for _, profit in positions.values())

            # Display dashboard
            print("\033[2J\033[H")  # Clear screen
            print("=" * 60)
            print(f"REAL-TIME P&L DASHBOARD")
            print("=" * 60)

            if update.account_info:
                acc = update.account_info
                print(f"Balance:  ${acc.balance:,.2f}")
                print(f"Equity:   ${acc.equity:,.2f}")
                print(f"Margin:   ${acc.margin:,.2f}")
                print(f"Free:     ${acc.margin_free:,.2f}")
                print(f"Profit:   ${acc.profit:,.2f}")
                print("-" * 60)

            print(f"\nOpen Positions: {len(positions)}")
            print(f"Total P&L: ${total_profit:,.2f}\n")

            # Show individual positions
            for ticket, (symbol, profit) in sorted(positions.items()):
                status = "[+]" if profit >= 0 else "[-]"
                print(f"{status} #{ticket} {symbol:8s} ${profit:>10,.2f}")

    except KeyboardInterrupt:
        print("\nStopping dashboard...")

    finally:
        await account.channel.close()

asyncio.run(realtime_pnl_dashboard())
```

### 3) Auto stop-loss on profit target

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2

async def auto_take_profit(target_profit: float = 100.0):
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
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            # Check updated positions for profit target
            for pos in update.updated_positions:
                if pos.profit >= target_profit:
                    print(f"\n[TARGET] Profit reached for #{pos.ticket}: "
                          f"${pos.profit:.2f}")

                    # Close position
                    close_req = trading_pb2.OrderCloseRequest(
                        ticket=pos.ticket,
                        volume=0,  # Close all
                        deviation=20,
                        comment="Auto TP"
                    )

                    result = await account.order_close(close_req)

                    if result.error.error_type == 0:  # Success
                        print(f"[SUCCESS] Position #{pos.ticket} closed")
                    else:
                        print(f"[FAILED] Could not close #{pos.ticket}: "
                              f"{result.error.description}")

    except KeyboardInterrupt:
        print("\nStopping auto TP...")

    finally:
        await account.channel.close()

# Close positions when they reach $100 profit
asyncio.run(auto_take_profit(100.0))
```

### 4) Loss limit protection

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2

async def loss_limit_protection(max_loss: float = -50.0):
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
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            # Check for excessive losses
            for pos in update.updated_positions:
                if pos.profit <= max_loss:
                    print(f"\n[WARNING] Loss limit exceeded for #{pos.ticket}: "
                          f"${pos.profit:.2f}")

                    # Emergency close
                    close_req = trading_pb2.OrderCloseRequest(
                        ticket=pos.ticket,
                        volume=0,
                        deviation=50,  # Allow higher slippage for emergency
                        comment="Emergency stop"
                    )

                    result = await account.order_close(close_req)

                    if result.error.error_type == 0:
                        print(f"[EMERGENCY] Position #{pos.ticket} closed")
                    else:
                        print(f"[FAILED] Could not close: {result.error.description}")

    except KeyboardInterrupt:
        print("\nStopping loss protection...")

    finally:
        await account.channel.close()

# Close positions when they lose more than $50
asyncio.run(loss_limit_protection(-50.0))
```

### 5) P&L statistics tracker

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def track_pnl_stats(duration_seconds: int = 300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Statistics storage
    stats = {}  # ticket -> {max_profit, max_loss, updates_count, symbol}

    prev_positions = set()
    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True,
            cancellation_event=cancel_event
        ):
            current_positions = set(update.position_tickets)
            stats['updates'] += 1

            # Add new positions
            for pos in update.new_positions:
                stats[pos.ticket] = {
                    'symbol': pos.position_symbol,
                    'max_profit': pos.profit,
                    'max_loss': pos.profit,
                    'updates': 1,
                    'current': pos.profit
                }

            # Update statistics
            for pos in update.updated_positions:
                if pos.ticket in stats:
                    s = stats[pos.ticket]
                    s['max_profit'] = max(s['max_profit'], pos.profit)
                    s['max_loss'] = min(s['max_loss'], pos.profit)
                    s['updates'] += 1
                    s['current'] = pos.profit

            # Mark deleted positions
            for pos in update.deleted_positions:
                if pos.ticket in stats:
                    stats[pos.ticket]['closed'] = True
                    stats[pos.ticket]['final_profit'] = pos.profit

        await stop_task

        # Print statistics
        print("\n" + "=" * 70)
        print("P&L STATISTICS REPORT")
        print("=" * 70)

        for ticket, s in stats.items():
            status = "CLOSED" if s.get('closed') else "OPEN"
            print(f"\nPosition #{ticket} ({s['symbol']}) - {status}")
            print(f"  Max profit:    ${s['max_profit']:>10,.2f}")
            print(f"  Max loss:      ${s['max_loss']:>10,.2f}")
            print(f"  Updates:       {s['updates']:>10,}")
            if s.get('closed'):
                print(f"  Final P&L:     ${s['final_profit']:>10,.2f}")
            else:
                print(f"  Current P&L:   ${s['current']:>10,.2f}")

        print("=" * 70)

    finally:
        await account.channel.close()

# Track statistics for 5 minutes
asyncio.run(track_pnl_stats(300))
```

### 6) Total account profit alert

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def total_profit_alert(target: float = 500.0):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    alerted = False

    try:
        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True
        ):
            if update.account_info:
                total_profit = update.account_info.profit

                # Check if target reached
                if total_profit >= target and not alerted:
                    print(f"\n[TARGET REACHED]")
                    print(f"Total account profit: ${total_profit:.2f}")
                    print(f"Balance: ${update.account_info.balance:.2f}")
                    print(f"Equity: ${update.account_info.equity:.2f}")
                    alerted = True
                    break

                # Show progress
                progress = (total_profit / target) * 100
                print(f"\rProfit: ${total_profit:>8.2f} "
                      f"({progress:>5.1f}% of target)", end="")

    except KeyboardInterrupt:
        print("\nStopping alert...")

    finally:
        await account.channel.close()

# Alert when total profit reaches $500
asyncio.run(total_profit_alert(500.0))
```

---

## 📚 See also

* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Get full position details (snapshot)
* [OrderClose](../5.%20Trading_Operations/order_close.md) - Close positions
* [OnSymbolTick](./on_symbol_tick.md) - Stream price updates
* [AccountSummary](../1.%20Account_Information/account_summary.md) - Get account info (snapshot)
