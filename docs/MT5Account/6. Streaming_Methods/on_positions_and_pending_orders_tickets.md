# Stream Position and Pending Order Tickets

> **Request:** subscribe to periodic updates of position and pending order ticket IDs.

**API Information:**

* **Python API:** `MT5Account.on_positions_and_pending_orders_tickets(...)` (defined in `package/helpers/mt5_account.py`)
* **gRPC service:** `mt5_term_api.SubscriptionService`
* **Proto definition:** `OnPositionsAndPendingOrdersTickets` (defined in `mt5-term-api-subscriptions.proto`)

### RPC

* **Service:** `mt5_term_api.SubscriptionService`
* **Method:** `OnPositionsAndPendingOrdersTickets(OnPositionsAndPendingOrdersTicketsRequest) -> stream OnPositionsAndPendingOrdersTicketsReply`
* **Low-level client (generated):** `SubscriptionServiceStub.OnPositionsAndPendingOrdersTickets(request, metadata)`

---

## 💬 Just the essentials

* **What it is.** Periodic stream of ticket IDs for open positions and pending orders.
* **Why you need it.** Lightweight monitoring of positions/orders, detect changes without full data.
* **Periodic updates.** Snapshot sent at specified intervals (e.g., every 1000ms).

---

## 🎯 Purpose

Use it to:

* Monitor position and order count changes
* Detect when new positions are opened (new tickets appear)
* Detect when positions are closed (tickets disappear)
* Lightweight alternative to `on_trade` when you only need ticket IDs
* Track ticket lifecycle without fetching full position data
* Build efficient change detection systems


```python
from MetaRpcMT5 import MT5Account

class MT5Account:
    # ...

    async def on_positions_and_pending_orders_tickets(
        self,
        interval_ms: int,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Subscribes to updates of position and pending order ticket IDs.

        Yields:
            OnPositionsAndPendingOrdersTicketsData: Snapshot of tickets.
        """
```

**Request message:**

```protobuf
message OnPositionsAndPendingOrdersTicketsRequest {
  int32 timer_period_milliseconds = 1;  // Polling interval in milliseconds
}
```

---

## 🔽 Input

| Parameter            | Type                           | Description                                   |
| -------------------- | ------------------------------ | --------------------------------------------- |
| `interval_ms`        | `int`                          | Polling interval in milliseconds              |
| `cancellation_event` | `Optional[asyncio.Event]`      | Event to cancel streaming (optional)          |

---

## ⬆️ Output - Async Generator

Returns an async generator that yields `OnPositionsAndPendingOrdersTicketsData` objects.

**OnPositionsAndPendingOrdersTicketsData fields:**

| Field                         | Type                          | Description                          |
| ----------------------------- | ----------------------------- | ------------------------------------ |
| `position_tickets`            | `repeated uint64`             | List of open position ticket IDs     |
| `pending_order_tickets`       | `repeated uint64`             | List of pending order ticket IDs     |
| `server_time`                 | `google.protobuf.Timestamp`   | Server timestamp                     |
| `terminal_instance_guid_id`   | `str`                         | Terminal instance identifier         |


---

## 📚 Tutorial

For a detailed line-by-line explanation with examples, see:
**[OnPositionsAndPendingOrdersTickets - How it works](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW.md)**

---

## 🧩 Notes & Tips

* **Automatic reconnection:** All `MT5Account` streaming methods have built-in protection against transient gRPC errors with automatic reconnection via `execute_stream_with_reconnect`.
* **Async generator:** The method returns an async generator - use `async for` to consume data.
* **Periodic snapshots:** Each update is a complete snapshot (not incremental changes).
* **Lightweight:** Only returns ticket IDs - use this when you don't need full position/order data.
* **Change detection:** Compare ticket lists between updates to detect new/closed positions.
* **Polling interval:** Choose interval based on your needs - shorter = more frequent updates.
* **Resource efficient:** Much lighter than `on_trade` or `on_position_profit`.

---

## 🔗 Usage Examples

### 1) Monitor ticket changes

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def monitor_tickets():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_positions = set()
    prev_orders = set()

    try:
        # Poll every second
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            current_positions = set(update.position_tickets)
            current_orders = set(update.pending_order_tickets)

            # Detect new positions
            new_positions = current_positions - prev_positions
            if new_positions:
                print(f"[NEW] Positions: {new_positions}")

            # Detect closed positions
            closed_positions = prev_positions - current_positions
            if closed_positions:
                print(f"[CLOSED] Positions: {closed_positions}")

            # Detect new pending orders
            new_orders = current_orders - prev_orders
            if new_orders:
                print(f"[NEW] Orders: {new_orders}")

            # Detect removed pending orders
            removed_orders = prev_orders - current_orders
            if removed_orders:
                print(f"[REMOVED] Orders: {removed_orders}")

            # Show current state
            print(f"[STATUS] Positions: {len(current_positions)}, "
                  f"Orders: {len(current_orders)}\n")

            prev_positions = current_positions
            prev_orders = current_orders

    except KeyboardInterrupt:
        print("Stopping monitor...")

    finally:
        await account.channel.close()

asyncio.run(monitor_tickets())
```

### 2) Alert on position count changes

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def alert_on_position_changes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_count = 0

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=500
        ):
            current_count = len(update.position_tickets)

            # Alert on changes
            if current_count > prev_count:
                print(f"\n[ALERT] {current_count - prev_count} position(s) OPENED")
                print(f"   Total positions: {current_count}")
                print(f"   Tickets: {list(update.position_tickets)}")

            elif current_count < prev_count:
                print(f"\n[ALERT] {prev_count - current_count} position(s) CLOSED")
                print(f"   Remaining positions: {current_count}")
                print(f"   Tickets: {list(update.position_tickets)}")

            prev_count = current_count

    except KeyboardInterrupt:
        print("\nStopping alerts...")

    finally:
        await account.channel.close()

asyncio.run(alert_on_position_changes())
```

### 3) Track position/order statistics

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def track_ticket_statistics(duration_seconds=300):
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
        'max_positions': 0,
        'max_orders': 0,
        'total_opened': 0,
        'total_closed': 0,
        'updates': 0,
    }

    prev_positions = set()
    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000,
            cancellation_event=cancel_event
        ):
            current_positions = set(update.position_tickets)
            stats['updates'] += 1

            # Update max counts
            stats['max_positions'] = max(stats['max_positions'], len(current_positions))
            stats['max_orders'] = max(stats['max_orders'], len(update.pending_order_tickets))

            # Count opened/closed
            stats['total_opened'] += len(current_positions - prev_positions)
            stats['total_closed'] += len(prev_positions - current_positions)

            prev_positions = current_positions

        await stop_task

        # Print statistics
        print("\n" + "=" * 60)
        print("TICKET STATISTICS REPORT")
        print("=" * 60)
        print(f"Duration:          {duration_seconds} seconds")
        print(f"Updates received:  {stats['updates']}")
        print(f"Max positions:     {stats['max_positions']}")
        print(f"Max orders:        {stats['max_orders']}")
        print(f"Total opened:      {stats['total_opened']}")
        print(f"Total closed:      {stats['total_closed']}")
        print("=" * 60)

    finally:
        await account.channel.close()

# Track for 5 minutes
asyncio.run(track_ticket_statistics(300))
```

### 4) Position count limiter

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def position_count_limiter(max_positions=5):
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
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=500
        ):
            position_count = len(update.position_tickets)

            if position_count >= max_positions:
                print(f"\n[WARNING] Position limit reached!")
                print(f"   Current positions: {position_count}/{max_positions}")
                print(f"   Tickets: {list(update.position_tickets)}")
                print(f"   [BLOCK] New positions should be blocked\n")
            else:
                available = max_positions - position_count
                print(f"[OK] Positions: {position_count}/{max_positions} "
                      f"({available} slots available)")

    except KeyboardInterrupt:
        print("\nStopping limiter...")

    finally:
        await account.channel.close()

# Alert when 5 or more positions are open
asyncio.run(position_count_limiter(5))
```

### 5) Ticket change logger to file

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def log_ticket_changes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_positions = set()
    prev_orders = set()

    try:
        with open('ticket_changes.log', 'w') as logfile:
            logfile.write("Timestamp,Event,Ticket\n")

            async for update in account.on_positions_and_pending_orders_tickets(
                interval_ms=1000
            ):
                timestamp = datetime.now().isoformat()
                current_positions = set(update.position_tickets)
                current_orders = set(update.pending_order_tickets)

                # Log new positions
                for ticket in current_positions - prev_positions:
                    logfile.write(f"{timestamp},POSITION_OPENED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Position opened: {ticket}")

                # Log closed positions
                for ticket in prev_positions - current_positions:
                    logfile.write(f"{timestamp},POSITION_CLOSED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Position closed: {ticket}")

                # Log new orders
                for ticket in current_orders - prev_orders:
                    logfile.write(f"{timestamp},ORDER_CREATED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Order created: {ticket}")

                # Log removed orders
                for ticket in prev_orders - current_orders:
                    logfile.write(f"{timestamp},ORDER_REMOVED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Order removed: {ticket}")

                prev_positions = current_positions
                prev_orders = current_orders

    except KeyboardInterrupt:
        print("\nStopping logger...")

    finally:
        await account.channel.close()

asyncio.run(log_ticket_changes())
```

### 6) Lightweight position monitor dashboard

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def position_dashboard():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    start_time = datetime.now()

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            # Clear screen
            print("\033[2J\033[H")

            runtime = datetime.now() - start_time
            server_time = datetime.fromtimestamp(update.server_time.seconds)

            print("=" * 70)
            print(f"POSITION MONITOR DASHBOARD")
            print("=" * 70)
            print(f"Runtime:     {runtime}")
            print(f"Server time: {server_time}")
            print(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)

            print(f"\nOpen Positions: {len(update.position_tickets)}")
            if update.position_tickets:
                for i, ticket in enumerate(update.position_tickets, 1):
                    print(f"  {i}. Ticket #{ticket}")
            else:
                print("  (none)")

            print(f"\nPending Orders: {len(update.pending_order_tickets)}")
            if update.pending_order_tickets:
                for i, ticket in enumerate(update.pending_order_tickets, 1):
                    print(f"  {i}. Ticket #{ticket}")
            else:
                print("  (none)")

            print("\n" + "=" * 70)
            print("Press Ctrl+C to stop")

    except KeyboardInterrupt:
        print("\n\nStopping dashboard...")

    finally:
        await account.channel.close()

asyncio.run(position_dashboard())
```

---

## 📚 See also

* [OpenedOrdersTickets](../3.%20Positions_Orders/opened_orders_tickets.md) - Get ticket snapshot (one-time)
* [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Get full position data (one-time)
* [OnTrade](./on_trade.md) - Stream detailed trade events
* [OnPositionProfit](./on_position_profit.md) - Stream position profit updates
