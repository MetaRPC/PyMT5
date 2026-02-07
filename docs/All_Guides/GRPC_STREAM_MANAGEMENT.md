# gRPC Streaming and Subscription Management Guide

> **Complete guide** to working with real-time subscriptions in PyMT5

This document covers:

- ✅ **How to subscribe properly** to market data streams
- ✅ **How to stop subscriptions** without resource leaks
- ✅ **Common patterns** from simple to advanced
- ✅ **Architecture** and built-in safety mechanisms
- ✅ **Troubleshooting** and best practices

---

## Table of Contents

1. [Quick Start - Simple Subscription](#quick-start---simple-subscription)
2. [Available Streaming Methods](#available-streaming-methods)
3. [Complete Patterns (Simple → Advanced)](#complete-patterns-simple--advanced)
4. [Problem: Why Streams Need Management](#problem-why-streams-need-management)
5. [Solutions and Best Practices](#solutions-and-best-practices)
6. [Advanced Examples with Enums](#advanced-examples-with-enums)
7. [Multiple Concurrent Streams](#multiple-concurrent-streams)
8. [Architecture and Safety](#architecture-notes)
9. [Troubleshooting](#troubleshooting-and-async-task-leaks)

---

## Quick Start - Simple Subscription

### 1️⃣ Simplest Pattern (Auto-timeout)

**Use asyncio.wait_for** - automatically stops after time expires:

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def main():
    # Setup connection
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # ✅ Stream for 10 seconds - stops automatically!
    try:
        async def process_ticks():
            tick_count = 0
            async for tick_data in account.on_symbol_tick(symbols=["EURUSD", "GBPUSD"]):
                tick_count += 1
                tick = tick_data.symbol_tick
                print(f"[{tick_count}] {tick.symbol}: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")

                if tick_count >= 10:
                    break

        await asyncio.wait_for(process_ticks(), timeout=10.0)
        print("Stream finished")

    finally:
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(main())
```

**When to use:** Quick examples, testing, short monitoring sessions

---

### 2️⃣ Manual Control Pattern

**For full control** - you decide when to stop:

```python
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

    # ✅ Create cancellation event
    cancel_event = asyncio.Event()

    async def monitor_prices():
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"Price: {tick.bid:.5f}")

    # Start monitoring in background
    monitor_task = asyncio.create_task(monitor_prices())

    # ... do other work ...

    # Stop when needed
    await asyncio.sleep(5)
    cancel_event.set()  # Signal stream to stop
    await asyncio.sleep(0.5)  # Give stream time to cleanup

    try:
        await account.channel.close()
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")

asyncio.run(main())
```

**When to use:** Long-term monitoring, background services, production applications

---

## Available Streaming Methods

### MT5Account (Low-level Streams)

All streaming methods return **async generators** that yield data objects.

| Method | Description | Returns (async generator) |
|--------|-------------|---------------------------|
| `on_symbol_tick()` | Real-time price ticks for symbols | `OnSymbolTickData` |
| `on_trade()` | Trade events (orders executed, modified, etc.) | `OnTradeData` |
| `on_position_profit()` | Position P&L updates | `OnPositionProfitData` |
| `on_positions_and_pending_orders_tickets()` | Order/position tickets | `OnPositionsAndPendingOrdersTicketsData` |
| `on_trade_transaction()` | Low-level trade transaction events | `OnTradeTransactionData` |

**All support `cancellation_event` parameter for graceful stopping!**

**Documentation:**
- [Streaming Methods Overview](../MT5Account/6.%20Streaming_Methods/Streaming_Methods.Overview.md)
- [on_symbol_tick](../MT5Account/6.%20Streaming_Methods/on_symbol_tick.md)
- [on_trade](../MT5Account/6.%20Streaming_Methods/on_trade.md)

**Examples:**

- `examples/1_lowlevel/03_streaming_methods.py` - Low-level streaming examples

- `examples/2_service/05_service_streaming.py` - Mid-level streaming examples

---

## Complete Patterns (Simple → Advanced)

### Pattern 1: Quick Example (5-10 seconds)

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def quick_stream_example():
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
        # ✅ Auto-timeout - perfect for testing
        async def process():
            count = 0
            async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
                tick = tick_data.symbol_tick
                count += 1
                print(f"Tick #{count}: {tick.bid:.5f}")

                if count >= 5:
                    break

        await asyncio.wait_for(process(), timeout=10.0)

    finally:
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(quick_stream_example())
# Stops after 5 ticks or 10 seconds automatically ✅
```

---

### Pattern 2: Event-limited Streaming

```python
async def event_limited_streaming():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    cancel_event = asyncio.Event()
    max_events = 100
    count = 0

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            count += 1
            tick = tick_data.symbol_tick
            print(f"[{count}] {tick.symbol}: {tick.bid:.5f}")

            if count >= max_events:
                print(f"Max events ({max_events}) reached - stopping")
                cancel_event.set()
                break

    finally:
        await asyncio.sleep(0.5)  # Wait for graceful cleanup
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(event_limited_streaming())
```

---

### Pattern 3: Condition-based Stop

```python
async def condition_based_stop():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    cancel_event = asyncio.Event()

    try:
        # ✅ Stop when specific condition is met
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"Price: {tick.bid:.5f}")

            # Stop if price crosses threshold
            if tick.bid > 1.10000:
                print("Target price reached!")
                cancel_event.set()
                break

    finally:
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(condition_based_stop())
```

---

### Pattern 4: Background Service with Manual Control

```python
class PriceMonitor:
    def __init__(self, account: MT5Account):
        self.account = account
        self.cancel_event = asyncio.Event()
        self.task = None

    async def start(self, symbols: list[str]):
        """Start monitoring in background"""
        self.task = asyncio.create_task(self._monitor_prices(symbols))

    async def _monitor_prices(self, symbols: list[str]):
        """Internal monitoring loop"""
        async for tick_data in self.account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=self.cancel_event
        ):
            tick = tick_data.symbol_tick
            self._process_tick(tick)

    def _process_tick(self, tick):
        """Process each tick"""
        print(f"{tick.symbol}: {tick.bid:.5f} / {tick.ask:.5f}")
        # Your logic here...

    async def stop(self):
        """Stop monitoring gracefully"""
        self.cancel_event.set()

        if self.task:
            await asyncio.sleep(0.5)  # Give time to cleanup
            await self.task

# Usage:
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

    monitor = PriceMonitor(account)
    await monitor.start(["EURUSD", "GBPUSD"])

    print("Monitoring... Press Ctrl+C to stop")
    await asyncio.sleep(30)  # Monitor for 30 seconds

    await monitor.stop()
    try:
        await account.channel.close()
    except Exception as e:
        print(f"⚠️  Disconnect warning: {e}")

asyncio.run(main())
```

---

## Problem: Why Streams Need Management

When working with gRPC streaming in PyMT5, understanding the stream lifecycle is critical:

**Stream subscriptions** (`on_symbol_tick`, `on_trade`, etc.) are **active async tasks with network connections** that continue running until explicitly stopped.

---

## Problem Explanation

### What Happens Without Proper Cleanup

```python
# ❌ BAD: Stream continues running forever
async def bad_example():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    count = 0
    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        count += 1
        print(f"Tick: {tick_data.symbol_tick.bid:.5f}")

        if count >= 10:
            break  # ❌ PROBLEM: Stream still running in background!
                   # ❌ PROBLEM: gRPC connection not closed!

    # ❌ Stream continues consuming resources
    # ❌ Network connection stays open
    # ❌ Memory gradually accumulates
```

**Result:**

- Background async task continues consuming resources
- MT5 terminal continues sending updates
- **Async task leak** - tasks accumulate in event loop
- Network connection stays open
- Multiple abandoned streams = **serious resource leak**

---

## Solutions and Best Practices

## Solution 1: Always Use cancellation_event ✅

### Pattern 1: Create cancellation_event early

```python
async def proper_cancellation():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    # ✅ CRITICAL: Create cancellation event
    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event  # ✅ Pass to stream
        ):
            tick = tick_data.symbol_tick
            print(f"Price: {tick.bid:.5f}")

            if some_condition:
                cancel_event.set()  # ✅ CORRECT: Signal to stop
                break

    finally:
        # ✅ CRITICAL: Give stream time to cleanup
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(proper_cancellation())
```

### Pattern 2: Timeout with asyncio.wait_for

```python
async def timeout_pattern():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async def stream_with_limit():
            async for tick_data in account.on_symbol_tick(
                symbols=["EURUSD"],
                cancellation_event=cancel_event
            ):
                print(f"Price: {tick_data.symbol_tick.bid:.5f}")

        # ✅ Automatically stops after 30 seconds
        await asyncio.wait_for(stream_with_limit(), timeout=30.0)

    except asyncio.TimeoutError:
        print("Stream reached timeout")
        cancel_event.set()

    finally:
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(timeout_pattern())
```

---

## Solution 2: Always Cleanup in finally Block ✅

**CRITICAL:** Always close channel and wait for stream cleanup

### ✅ CORRECT - Proper Cleanup

```python
async def proper_cleanup():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            # Process data...
            pass

    finally:
        # ✅ CRITICAL: Proper cleanup sequence
        # Step 1: Signal all streams to stop
        cancel_event.set()

        # Step 2: Wait for graceful cleanup (0.5-1.0 seconds)
        await asyncio.sleep(0.5)

        # Step 3: Close gRPC channel
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(proper_cleanup())
```

---

## Common Streaming Mistakes

### ❌ Mistake 1: No Cancellation Event

```python
# ❌ WRONG: No way to stop stream gracefully
async def bad():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        print(tick_data.symbol_tick.bid)
        # If you want to stop - YOU CAN'T stop gracefully!
```

**Fix:**
```python
# ✅ CORRECT: Can stop gracefully anytime
async def good():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    async for tick_data in account.on_symbol_tick(
        symbols=["EURUSD"],
        cancellation_event=cancel_event
    ):
        print(tick_data.symbol_tick.bid)
        # Now can call cancel_event.set() to stop
```

---

### ❌ Mistake 2: Break Without Cleanup

```python
# ❌ WRONG: Break doesn't cleanup resources
async def bad():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        if some_condition:
            break  # ❌ Stream still running!

    # ❌ No cleanup - resources leak!
```

**Fix:**
```python
# ✅ CORRECT: Proper cleanup in finally
async def good():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            if some_condition:
                cancel_event.set()
                break

    finally:
        await asyncio.sleep(0.5)  # ✅ Cleanup time
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")
```

---

### ❌ Mistake 3: No Channel Close

```python
# ❌ WRONG: Channel never closed
async def bad():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    async for tick_data in account.on_symbol_tick(
        symbols=["EURUSD"],
        cancellation_event=cancel_event
    ):
        # Process...
        pass

    # ❌ Forgot to close channel - connection leak!
```

**Fix:**
```python
# ✅ CORRECT: Always close in finally
async def good():
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            # Process...
            pass

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        await account.channel.close()  # ✅ CRITICAL: Always close
```

---

## Advanced Examples with Enums

### Example 1: Filter Trade Events by Type

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as sub_pb2

async def filter_trade_events():
    """
    Monitor trade events and filter by type using protobuf enums.
    Shows how to work with SUB_ENUM_TRADE_TRANSACTION_TYPE.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    # ✅ Using protobuf enums for filtering
    ORDER_ADD = sub_pb2.SUB_TRADE_TRANSACTION_ORDER_ADD
    ORDER_DELETE = sub_pb2.SUB_TRADE_TRANSACTION_ORDER_DELETE
    DEAL_ADD = sub_pb2.SUB_TRADE_TRANSACTION_DEAL_ADD

    try:
        print("Monitoring trade transactions (filtered by type)...")

        async for tx_data in account.on_trade_transaction(cancellation_event=cancel_event):
            if tx_data.trade_transaction:
                tx = tx_data.trade_transaction

                # ✅ Filter by transaction type using enums
                if tx.type == ORDER_ADD:
                    print(f"[NEW ORDER] Ticket={tx.order_ticket}, Symbol={tx.symbol}, "
                          f"Price={tx.price:.5f}, Volume={tx.volume:.2f}")

                elif tx.type == ORDER_DELETE:
                    print(f"[ORDER DELETED] Ticket={tx.order_ticket}")

                elif tx.type == DEAL_ADD:
                    print(f"[NEW DEAL] Deal={tx.deal_ticket}, Order={tx.order_ticket}, "
                          f"Symbol={tx.symbol}, Price={tx.price:.5f}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(filter_trade_events())
```

---

### Example 2: Sort and Filter Positions by Profit

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def sort_positions_by_profit():
    """
    Monitor position profits and sort by P&L.
    Shows advanced data processing with streaming.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        print("Monitoring positions (sorted by profit)...")
        print("-" * 60)

        async for profit_data in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True,
            cancellation_event=cancel_event
        ):
            # ✅ Collect all updated positions
            positions = list(profit_data.updated_positions)

            if not positions:
                continue

            # ✅ Sort by profit (descending - winners first)
            positions_sorted = sorted(positions, key=lambda p: p.profit, reverse=True)

            print(f"\n[UPDATE] Total positions: {len(positions_sorted)}")
            print(f"{'Symbol':<10} {'Ticket':<10} {'Profit':<12} {'Status':<10}")
            print("-" * 60)

            # ✅ Show top 5 winners and top 5 losers
            for pos in positions_sorted[:5]:  # Top 5 winners
                status = "✅ PROFIT" if pos.profit > 0 else "❌ LOSS"
                print(f"{pos.position_symbol:<10} {pos.ticket:<10} {pos.profit:>10.2f}  {status:<10}")

            if len(positions_sorted) > 10:
                print("   ... middle positions omitted ...")

            for pos in positions_sorted[-5:]:  # Top 5 losers
                status = "✅ PROFIT" if pos.profit > 0 else "❌ LOSS"
                print(f"{pos.position_symbol:<10} {pos.ticket:<10} {pos.profit:>10.2f}  {status:<10}")

            # ✅ Calculate statistics
            total_profit = sum(p.profit for p in positions_sorted)
            winners = sum(1 for p in positions_sorted if p.profit > 0)
            losers = sum(1 for p in positions_sorted if p.profit < 0)

            print("-" * 60)
            print(f"Total P&L: {total_profit:+.2f} | Winners: {winners} | Losers: {losers}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(sort_positions_by_profit())
```

---

### Example 3: Filter Orders by State and Type

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as sub_pb2

async def filter_orders_by_state():
    """
    Monitor trade events and filter orders by state and type.
    Shows complex filtering using multiple enums.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    # ✅ Define enum values for filtering
    ORDER_STATE_PLACED = sub_pb2.SUB_ORDER_STATE_PLACED
    ORDER_STATE_FILLED = sub_pb2.SUB_ORDER_STATE_FILLED
    ORDER_STATE_CANCELED = sub_pb2.SUB_ORDER_STATE_CANCELED

    ORDER_TYPE_BUY_LIMIT = sub_pb2.SUB_ORDER_TYPE_BUY_LIMIT
    ORDER_TYPE_SELL_LIMIT = sub_pb2.SUB_ORDER_TYPE_SELL_LIMIT

    try:
        print("Monitoring pending orders (filtered by state)...")
        print("-" * 70)

        async for trade_data in account.on_trade(cancellation_event=cancel_event):
            event = trade_data.event_data

            # ✅ Process new orders - filter pending limit orders only
            for order in event.new_orders:
                if order.order_type in [ORDER_TYPE_BUY_LIMIT, ORDER_TYPE_SELL_LIMIT]:
                    order_type_str = "BUY LIMIT" if order.order_type == ORDER_TYPE_BUY_LIMIT else "SELL LIMIT"
                    print(f"[NEW PENDING] {order_type_str} #{order.ticket}: "
                          f"{order.symbol} @ {order.price_open:.5f} "
                          f"Vol={order.volume_initial:.2f} SL={order.stop_loss:.5f}")

            # ✅ Process state changed orders - show only filled or cancelled
            for state_change in event.state_changed_orders:
                current = state_change.current_order
                previous = state_change.previous_order

                if current.state == ORDER_STATE_FILLED:
                    print(f"[FILLED] Order #{current.ticket} was filled: "
                          f"{current.symbol} @ {current.price_current:.5f}")

                elif current.state == ORDER_STATE_CANCELED:
                    print(f"[CANCELED] Order #{current.ticket} was cancelled: "
                          f"{current.symbol}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(filter_orders_by_state())
```

---

### Example 4: Multi-Symbol Tick Aggregation with Sorting

```python
import asyncio
from collections import defaultdict
from datetime import datetime
from MetaRpcMT5 import MT5Account

async def aggregate_and_sort_ticks():
    """
    Aggregate ticks from multiple symbols and sort by spread.
    Shows advanced data processing with multiple symbols.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    # ✅ Track latest tick for each symbol
    latest_ticks = {}
    tick_counts = defaultdict(int)

    symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]

    try:
        print(f"Monitoring {len(symbols)} symbols, sorting by spread...")
        print("-" * 80)

        update_interval = 5  # Print sorted results every 5 ticks
        total_ticks = 0

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick

            # ✅ Update latest tick for symbol
            latest_ticks[tick.symbol] = tick
            tick_counts[tick.symbol] += 1
            total_ticks += 1

            # ✅ Every N ticks, show sorted summary
            if total_ticks % update_interval == 0:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Tick Summary (sorted by spread):")
                print("-" * 80)
                print(f"{'Rank':<6} {'Symbol':<10} {'Bid':<12} {'Ask':<12} {'Spread':<10} {'Ticks':<8}")
                print("-" * 80)

                # ✅ Calculate spreads and sort
                symbol_spreads = []
                for symbol, tick in latest_ticks.items():
                    spread = tick.ask - tick.bid
                    symbol_spreads.append((symbol, tick, spread))

                # Sort by spread (ascending - tightest first)
                symbol_spreads.sort(key=lambda x: x[2])

                # ✅ Display sorted results
                for rank, (symbol, tick, spread) in enumerate(symbol_spreads, 1):
                    spread_pips = spread * 10000  # For 4-digit pairs
                    print(f"{rank:<6} {symbol:<10} {tick.bid:<12.5f} {tick.ask:<12.5f} "
                          f"{spread_pips:<10.1f} {tick_counts[symbol]:<8}")

                print("-" * 80)
                print(f"Total ticks received: {total_ticks}")

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(aggregate_and_sort_ticks())
```

---

## Multiple Concurrent Streams

### Example: Run Multiple Streams Simultaneously

```python
import asyncio
from MetaRpcMT5 import MT5Account

async def multiple_concurrent_streams():
    """
    Run multiple streaming methods concurrently.
    Shows proper management of multiple streams.
    """
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    # ✅ Single cancellation event for ALL streams
    cancel_event = asyncio.Event()

    async def stream_ticks():
        """Monitor tick data"""
        try:
            async for tick_data in account.on_symbol_tick(
                symbols=["EURUSD"],
                cancellation_event=cancel_event
            ):
                tick = tick_data.symbol_tick
                print(f"[TICK] {tick.symbol}: {tick.bid:.5f}")
        except Exception as e:
            print(f"[TICK ERROR] {e}")

    async def stream_trades():
        """Monitor trade events"""
        try:
            async for trade_data in account.on_trade(cancellation_event=cancel_event):
                print(f"[TRADE] Event received: {trade_data.type}")
        except Exception as e:
            print(f"[TRADE ERROR] {e}")

    async def stream_profits():
        """Monitor position profits"""
        try:
            async for profit_data in account.on_position_profit(
                interval_ms=2000,
                ignore_empty=True,
                cancellation_event=cancel_event
            ):
                total_positions = len(profit_data.updated_positions)
                print(f"[PROFIT] {total_positions} positions updated")
        except Exception as e:
            print(f"[PROFIT ERROR] {e}")

    async def auto_stop(duration: float):
        """Auto-stop after duration"""
        await asyncio.sleep(duration)
        print(f"\n[STOP] Auto-stopping after {duration} seconds...")
        cancel_event.set()

    try:
        print("Starting multiple concurrent streams...")
        print("-" * 60)

        # ✅ Run all streams concurrently
        await asyncio.gather(
            stream_ticks(),
            stream_trades(),
            stream_profits(),
            auto_stop(30.0)  # Stop all after 30 seconds
        )

    finally:
        # ✅ Ensure cancellation event is set
        cancel_event.set()

        # ✅ Wait for all streams to cleanup
        await asyncio.sleep(0.5)

        # ✅ Close channel
        try:
            await account.channel.close()
            print("[DONE] All streams stopped gracefully")
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

asyncio.run(multiple_concurrent_streams())
```

---

## Architecture Notes

### How Python Streaming Works in MT5Account

**🔑 Critical Understanding:**

**ALL streaming methods** (`on_symbol_tick`, `on_trade`, `on_position_profit`, `on_trade_transaction`, `on_positions_and_pending_orders_tickets`) internally use the **same hidden mechanism**: `execute_stream_with_reconnect`.

This is why:
- The while loop behavior applies to **ALL** streaming operations
- The `cancellation_event` mechanism is required for **ALL** streaming methods
- Resource cleanup rules are **identical** for all streaming operations

**Users don't see this directly** - when you call `account.on_symbol_tick()`, internally it calls `execute_stream_with_reconnect` which contains the infinite reconnection loop.

**Data flow:**

```
User code (async for loop)
    ↓
Async generator (yields data)
    ↓
execute_stream_with_reconnect (background async task)
    ↓
gRPC ClientStream
    ↓
Network (to MT5 terminal)
```

**Cancellation propagation:**
```
User code → cancellation_event → async generator → gRPC call → Network
```

**When you set cancellation_event:**

1. User calls `cancel_event.set()` in their code
2. While loop checks condition on next iteration:
   ```python
   while cancellation_event is None or not cancellation_event.is_set():
   # After .set() → both conditions False → loop STOPS
   ```
3. Current iteration finishes (async for yields last data)
4. `finally` block executes → `stream.cancel()` closes gRPC stream ✅
5. Loop breaks (no new streams created)
6. Network connection closes
7. Resources freed ✅

**Key insight:** The while loop checks `cancellation_event.is_set()` **on each iteration**. Calling `.set()` makes the loop exit after current stream finishes.

### MT5Account Cleanup Mechanism

⚠️ **Important:** This mechanism is **internal to ALL streaming methods**. When you call any streaming method (`on_symbol_tick`, `on_trade`, etc.), you're actually using `execute_stream_with_reconnect` behind the scenes.

The `execute_stream_with_reconnect` method has built-in reconnection logic with automatic stream cleanup:

```python
# In MT5Account (real structure)
async def execute_stream_with_reconnect(..., cancellation_event):
    # ⚠️ CRITICAL: Infinite reconnection loop
    while cancellation_event is None or not cancellation_event.is_set():
        reconnect_required = False
        stream = None

        try:
            stream = stream_invoker(request, headers)
            async for response in stream:
                # Yield data to user
                yield data

        except grpc.aio.AioRpcError as ex:
            if ex.code() == grpc.StatusCode.UNAVAILABLE:
                reconnect_required = True  # Network error → try reconnect
            else:
                raise

        finally:
            if stream:
                stream.cancel()  # ✅ ALWAYS closes current gRPC stream

        # Reconnection logic
        if reconnect_required:
            await asyncio.sleep(0.5)
            await self.reconnect()
            # ⚠️ Loop continues → creates NEW stream
        else:
            break  # Exit only here
```

**What this means:**

✅ **What it DOES do:**
- Closes current gRPC stream automatically (in `finally` block)
- Handles network errors with automatic reconnection
- Cleans up resources for each individual stream

⚠️ **What it DOESN'T do:**
- **Stop the reconnection loop** without `cancellation_event`
- **Prevent new streams** from being created

**Critical understanding:**

```python
# ❌ WITHOUT cancellation_event:
async for tick in account.on_symbol_tick(["EURUSD"]):  # No cancellation_event!
    if count >= 10:
        break  # User breaks → current stream closes ✅
                # BUT while loop continues → creates NEW stream ❌
                # → LEAK: orphaned stream keeps running

# ✅ WITH cancellation_event:
cancel_event = asyncio.Event()
async for tick in account.on_symbol_tick(["EURUSD"], cancellation_event=cancel_event):
    if count >= 10:
        cancel_event.set()  # Stops while loop ✅
        break               # Current stream closes ✅
                            # → CLEAN: no new streams created
```

**Bottom line:**
- ✅ `stream.cancel()` cleans up **current** stream
- ❌ **Only** `cancellation_event.set()` stops the **reconnection while loop**
- 🔑 **How it works**: `while cancellation_event is None or not cancellation_event.is_set()` checks on each iteration
- 🔴 **Without cancellation_event** → while condition is always True → loop runs forever → **LEAK**
- 🔴 **With cancellation_event but no .set()** → while condition stays True → loop runs forever → **LEAK**
- ✅ **With cancellation_event.set()** → while condition becomes False → loop stops → **CLEAN**
- ✅ **You MUST close channel** to free gRPC connection

---

## Recommendations

### ✅ DO:

1. **Always use `cancellation_event`** with streaming methods
2. **Always call `cancel_event.set()`** before exiting
3. **Always use `try/finally` blocks** for cleanup
4. **Always wait 0.5-1.0 seconds** after setting cancellation_event
5. **Always close channel** in finally block: `await account.channel.close()`
6. **Use `asyncio.wait_for()`** for automatic timeouts
7. **Use `asyncio.gather()`** to run multiple streams concurrently

### ❌ DON'T:

1. **Never start streaming without cancellation_event**
2. **Never break from loop without setting cancellation_event**
3. **Never forget finally block** with cleanup code
4. **Never skip waiting period** after cancellation
5. **Never leave channel open** after streaming
6. **Never ignore exceptions** from streams

---

## Troubleshooting and Async Task Leaks

### Checking for Task Leaks

```python
import asyncio

async def check_task_leaks():
    # Before streaming
    before = len(asyncio.all_tasks())
    print(f"Tasks before: {before}")

    # Your streaming code here...
    account = MT5Account(user=12345, password="password", grpc_server="mt5.mrpc.pro:443")
    await account.connect_by_server_name(server_name="YourBroker-Demo", base_chart_symbol="EURUSD")

    cancel_event = asyncio.Event()

    try:
        count = 0
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            count += 1
            if count >= 5:
                break

    finally:
        cancel_event.set()
        await asyncio.sleep(0.5)
        try:
            await account.channel.close()
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")

    # After streaming (wait a bit for cleanup)
    await asyncio.sleep(1.0)
    after = len(asyncio.all_tasks())
    print(f"Tasks after: {after}")
    print(f"Leaked tasks: {after - before}")
    # Should be 0-1 if properly cleaned up

asyncio.run(check_task_leaks())
```

### Debugging Pending Tasks

```python
import asyncio

async def debug_pending_tasks():
    # Get all tasks
    tasks = asyncio.all_tasks()

    print(f"Total pending tasks: {len(tasks)}")
    print("-" * 60)

    for i, task in enumerate(tasks, 1):
        print(f"Task {i}: {task.get_name()}")
        print(f"  Coro: {task.get_coro()}")
        print(f"  Done: {task.done()}")
        if not task.done():
            print(f"  ⚠️  STILL RUNNING!")
        print()
```

### Common Leak Patterns

1. **Not using cancellation_event:**
   ```python
   # ❌ Leak: stream never stops
   async for data in account.on_symbol_tick(symbols=["EURUSD"]):
       # Forgot cancellation_event parameter
       pass
   ```

2. **Not setting cancellation_event:**
   ```python
   # ❌ Leak: stream keeps running after break
   cancel_event = asyncio.Event()
   async for data in account.on_symbol_tick(symbols=["EURUSD"], cancellation_event=cancel_event):
       if condition:
           break  # Forgot cancel_event.set()
   ```

3. **Not closing channel:**
   ```python
   # ❌ Leak: connection stays open
   cancel_event.set()
   await asyncio.sleep(0.5)
   # Forgot await account.channel.close()
   ```

---

## See Also

* **[Streaming Methods Overview](../MT5Account/6.%20Streaming_Methods/Streaming_Methods.Overview.md)** - Complete streaming methods documentation
* **[on_symbol_tick](../MT5Account/6.%20Streaming_Methods/on_symbol_tick.md)** - Tick streaming reference
* **[on_trade](../MT5Account/6.%20Streaming_Methods/on_trade.md)** - Trade events reference
* **[Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)** - Official asyncio guide
* **[gRPC Python](https://grpc.io/docs/languages/python/)** - Official gRPC Python guide

---

**Remember:** Streams are powerful tools for real-time market data, but they require proper lifecycle management. Master cancellation_event, always cleanup in finally blocks, and your streaming code will be robust and leak-free. Happy streaming! 🚀
