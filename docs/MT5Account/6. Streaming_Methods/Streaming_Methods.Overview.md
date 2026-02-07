# MT5Account - Streaming Methods - Overview

> Real-time streams: ticks, trades, profit updates, transaction log. Use this page to choose the right API for real-time subscriptions.

## 📁 What lives here

### Real-Time Price Updates

* **[on_symbol_tick](./on_symbol_tick.md)** - real-time tick stream for symbols.

### Trading Events

* **[on_trade](./on_trade.md)** - position/order changes (opened, closed, modified).
* **[on_trade_transaction](./on_trade_transaction.md)** - detailed transaction log (complete audit trail).

### Position Monitoring

* **[on_position_profit](./on_position_profit.md)** - periodic profit/loss updates.
* **[on_positions_and_pending_orders_tickets](./on_positions_and_pending_orders_tickets.md)** - periodic ticket lists (lightweight).

---

## 📚 Step-by-step tutorials

**Note:** Streaming methods are async generator-based APIs. Check individual method pages for detailed examples of asyncio patterns and event handling.

* **[on_symbol_tick](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_symbol_tick_HOW.md)** - Detailed tick streaming examples
* **[on_trade](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW.md)** - Trade event monitoring patterns
* **[on_trade_transaction](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW.md)** - Transaction logging examples
* **[on_position_profit](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW.md)** - P/L monitoring patterns
* **[on_positions_and_pending_orders_tickets](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW.md)** - Ticket tracking examples

---

## 🧭 Plain English

* **on_symbol_tick** -> **stream live prices** for symbols (bid, ask, volume updates).
* **on_trade** -> **monitor trade events** (position opened/closed/modified).
* **on_trade_transaction** -> **detailed audit log** of all trading operations.
* **on_position_profit** -> **periodic P/L updates** for open positions.
* **on_positions_and_pending_orders_tickets** -> **periodic ticket lists** (lightweight monitoring).

> Rule of thumb: need **live prices** -> `on_symbol_tick`; need **trade notifications** -> `on_trade`; need **detailed audit** -> `on_trade_transaction`; need **P/L monitoring** -> `on_position_profit`.

---

## Quick choose

| If you need...                                   | Use                                         | Returns (async stream)             | Key inputs                          |
| ------------------------------------------------ | ------------------------------------------- | ---------------------------------- | ----------------------------------- |
| Real-time price ticks                            | `on_symbol_tick`                            | OnSymbolTickData                   | List of symbol names                |
| Trade event notifications                        | `on_trade`                                  | OnTradeData                        | *(none)*                            |
| Detailed transaction audit log                   | `on_trade_transaction`                      | OnTradeTransactionData             | *(none)*                            |
| Real-time profit/loss updates                    | `on_position_profit`                        | OnPositionProfitData               | Interval (ms), ignore_empty flag    |
| Real-time ticket list changes                    | `on_positions_and_pending_orders_tickets`   | OnPositionsAndPendingOrdersTicketsData | Interval (ms)                   |

---

## ℹ️ Cross-refs & gotchas

* **Streaming = async generators** - Methods return async generators, use `async for` to consume data.
* **Cancellation** - Use `asyncio.Event` and call `event.set()` to stop streams gracefully.
* **Async/await required** - All streaming methods must be called with `await` in async functions.
* **on_symbol_tick** - High frequency, can generate many updates per second.
* **on_trade** - Triggered on every trade event (open, close, modify, delete).
* **on_trade_transaction** - Most detailed, includes all transaction types and states.
* **on_position_profit** - Periodic updates at specified intervals (e.g., every 500ms).
* **Resource management** - Always cancel streams when done to close connections and free resources.
* **Error handling** - Errors are raised as exceptions - wrap in try/except for error handling.
* **Automatic reconnection** - All streams have built-in reconnection via `execute_stream_with_reconnect`.

---

## 🟢 Minimal snippets

```python
import asyncio
from MetaRpcMT5 import MT5Account

# Stream live ticks for EURUSD
async def stream_ticks():
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
        async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
            tick = tick_data.symbol_tick
            print(f"EURUSD: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        await account.channel.close()

asyncio.run(stream_ticks())
```

```python
# Monitor trade events
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

            if event.new_positions:
                print(f"New positions: {len(event.new_positions)}")
            if event.disappeared_positions:
                print(f"Closed positions: {len(event.disappeared_positions)}")

    finally:
        await account.channel.close()

asyncio.run(monitor_trades())
```

```python
# Monitor position profit/loss
async def monitor_pnl():
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
            for pos in update.updated_positions:
                print(f"#{pos.ticket} ({pos.position_symbol}): ${pos.profit:.2f}")

    finally:
        await account.channel.close()

asyncio.run(monitor_pnl())
```

```python
# Monitor position tickets
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

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            print(f"Open positions: {len(update.position_tickets)}")
            print(f"Pending orders: {len(update.pending_order_tickets)}")

    finally:
        await account.channel.close()

asyncio.run(monitor_tickets())
```

```python
# Detailed transaction log
async def transaction_log():
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
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction
            print(f"Transaction: Order #{tx.order_ticket}, "
                  f"Deal #{tx.deal_ticket}, State: {tx.order_state}")

    finally:
        await account.channel.close()

asyncio.run(transaction_log())
```

```python
# Multiple streams with cancellation
async def multiple_streams():
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

    async def stop_after(seconds):
        await asyncio.sleep(seconds)
        cancel_event.set()

    async def stream_ticks():
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"[TICK] {tick.bid:.5f}")

    async def stream_trades():
        async for trade_data in account.on_trade(
            cancellation_event=cancel_event
        ):
            print(f"[TRADE] Event received")

    try:
        # Run multiple streams concurrently
        await asyncio.gather(
            stream_ticks(),
            stream_trades(),
            stop_after(30)  # Stop all after 30 seconds
        )
    finally:
        await account.channel.close()

asyncio.run(multiple_streams())
```

```python
# Using cancellation event for graceful shutdown
async def stream_with_cancellation():
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

    async def handle_keyboard_interrupt():
        """Wait for Ctrl+C and trigger cancellation"""
        try:
            await asyncio.Event().wait()  # Wait forever
        except asyncio.CancelledError:
            cancel_event.set()

    try:
        # Create task for keyboard interrupt handling
        interrupt_task = asyncio.create_task(handle_keyboard_interrupt())

        # Stream with cancellation support
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD", "GBPUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"{tick.symbol}: {tick.bid:.5f}")

        interrupt_task.cancel()

    except KeyboardInterrupt:
        cancel_event.set()
        print("\nGracefully stopping stream...")

    finally:
        await account.channel.close()

asyncio.run(stream_with_cancellation())
```

---

## 📚 See also

* **Account info:** [account_summary](../1.%20Account_Information/account_summary.md) - get current account state
* **Positions:** [opened_orders](../3.%20Positions_Orders/opened_orders.md) - get current positions snapshot
* **Symbol info:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - get current price snapshot
