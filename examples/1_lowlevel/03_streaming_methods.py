"""══════════════════════════════════════════════════════════════════════════════
FILE: 03_streaming_methods.py - LOW-LEVEL STREAMING METHODS DEMO

PURPOSE:
  Demonstrates MT5 real-time streaming (gRPC server-streaming) for live data.
  Shows how to subscribe to market ticks, trade events, position updates, and more.
  All streams are REAL-TIME and event-driven.

[TARGET] WHO SHOULD USE THIS:

  - Developers building real-time trading applications
  - High-frequency trading (HFT) systems
  - Live monitoring and alerting systems
  - Anyone needing instant market/trade notifications

📚 WHAT THIS DEMO COVERS (5 Streaming Methods):

  PREPARATION: CREATE MT5ACCOUNT & CONNECT
     - MT5Account() - Initialize account
     - connect_by_server_name() - Connect to MT5 cluster

  STEP 1: on_symbol_tick()
     - Real-time Bid/Ask price updates
     - Subscribe to multiple symbols
     - High-frequency tick data

  STEP 2: on_trade()
     - Trade execution events
     - New/disappeared orders and positions
     - History orders and deals

  STEP 3: on_position_profit()
     - Real-time P&L updates for open positions
     - Position profit changes as prices move
     - Position lifecycle (new/updated/deleted)

  STEP 4: on_positions_and_pending_orders_tickets()
     - Track order/position ticket numbers
     - Know what's currently open
     - Minimal data (just ticket IDs)

  STEP 5: on_trade_transaction()
     - Low-level trade transaction events
     - Every single trading operation
     - Order placement, execution, modification, deletion

  FINAL: CLEANUP
     - Close all streams
     - Disconnect from MT5

⚠️ STREAM CHARACTERISTICS:
  - REAL-TIME: Events arrive as they happen (millisecond latency)
  - EVENT-DRIVEN: No polling needed - server pushes data
  - PERSISTENT: Stay open until you close them or error occurs
  - SAFE: Read-only operations (no trades executed)

[!] IMPORTANT NOTES - PROPER STREAM SHUTDOWN:
  - Streams require ACTIVE connection to MT5 terminal
  - Some streams only fire on activity (e.g., on_trade when trading)
  - on_symbol_tick is the most frequent (multiple times per second)
  - Each stream is async generator - handle errors properly

  GRACEFUL SHUTDOWN PATTERN:
  1. Create cancellation_event = asyncio.Event() ONCE at start
  2. Pass cancellation_event to ALL streaming method calls
  3. In finally block:
     a) Call cancellation_event.set() - signals all streams to stop
     b) Wait 0.5s for streams to finish gracefully
     c) Then call disconnect() - closes gRPC channel cleanly
  - This prevents DEADLINE_EXCEEDED errors on disconnect

[i] STREAMING vs POLLING:
  STREAMING (this demo):  Server pushes -> instant updates, efficient
  POLLING (file 01):      Client pulls -> delayed, resource-intensive

🚀 HOW TO RUN THIS DEMO:
  cd examples
  python main.py 3          (or select [3] from interactive menu)

══════════════════════════════════════════════════════════════════════════════"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from MetaRpcMT5 import MT5Account
import package.MetaRpcMT5.mt5_term_api_connection_pb2 as connection_pb2

# Fix Windows console encoding for Unicode characters (only if running standalone)
if sys.platform == 'win32' and __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import common helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_if_error,
    print_success,
    print_info,
    fatal,
)

# Stream limits
MAX_EVENTS = 10
MAX_SECONDS = 5

# ══════════════════════════════════════════════════════════════════════════════
# HELPER: Process stream with timeout and event limit
# ══════════════════════════════════════════════════════════════════════════════
async def process_stream(stream_gen, stream_name: str, handler_func):
    """
    Process async stream with timeout and event limit.

    Args:
        stream_gen: Async generator from streaming method
        stream_name: Name for logging
        handler_func: Function to handle each event (takes event data)
    """
    event_count = 0
    timeout_task = asyncio.create_task(asyncio.sleep(MAX_SECONDS))
    stream_task = None

    try:
        async for event_data in stream_gen:
            event_count += 1

            # Call handler to process event
            handler_func(event_count, event_data)

            if event_count >= MAX_EVENTS:
                print(f"  [+] Received {MAX_EVENTS} events, stopping stream")
                break

        else:
            # Stream ended naturally
            print(f"  [i] Stream closed by server")

    except asyncio.TimeoutError:
        print(f"  [!] Timeout after {MAX_SECONDS}sec (received {event_count} events)")
    except Exception as e:
        print(f"  [X] Stream error: {e}")
    finally:
        if not timeout_task.done():
            timeout_task.cancel()


# MAIN DEMO FUNCTION

async def run_streaming_demo():
    print("═══════════════════════════════════════════════════════════")
    print("MT5 LOWLEVEL DEMO 03: STREAMING METHODS")
    print("═══════════════════════════════════════════════════════════")
    print()

    # LOAD CONFIGURATION
    
    config = load_settings()
    TEST_SYMBOL = config['test_symbol']

    # ═══════════════════════════════════════════════════════════════════════
    # PREPARATION: CREATE MT5ACCOUNT INSTANCE & CONNECT
    # ═══════════════════════════════════════════════════════════════════════
    print("PREPARATION: Creating MT5Account instance and connecting...")
    print("───────────────────────────────────────────────────────────")

    account = await create_and_connect_mt5(config)
    print()

    # Create cancellation event for graceful stream shutdown
    cancellation_event = asyncio.Event()

    try:
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 1: on_symbol_tick() - Real-time tick data stream
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print("STEP 1: [TICK] on_symbol_tick() - Stream tick data")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 1.1. on_symbol_tick()
        #      Subscribe to real-time tick data for specified symbols.
        #      Call: account.on_symbol_tick(symbols, cancellation_event) → gRPC stream → MT5 Server
        #      Returns: Stream of OnSymbolTickResponse (Bid, Ask, Spread, Volume, Time)
        #      HIGH FREQUENCY: Multiple events per second.
        #      Use cases: Price monitoring, tick charts, HFT strategies.
        # ══════════════════════════════════════════════════════════════

        print(f"Streaming {TEST_SYMBOL} (max {MAX_EVENTS} events or {MAX_SECONDS}sec)...")

        def handle_tick(event_num, tick_data):
            """Handle tick event"""
            if tick_data.symbol_tick:
                tick = tick_data.symbol_tick
                spread = tick.ask - tick.bid
                print(f"  #{event_num}: {tick.symbol} | Bid={tick.bid:.5f} Ask={tick.ask:.5f} Spread={spread:.5f}")

        stream_gen = account.on_symbol_tick(symbols=[TEST_SYMBOL], cancellation_event=cancellation_event)

        try:
            await asyncio.wait_for(
                process_stream(stream_gen, "OnSymbolTick", handle_tick),
                timeout=MAX_SECONDS
            )
        except asyncio.TimeoutError:
            print(f"  [!] Timeout after {MAX_SECONDS}sec")

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 2: on_trade() - Trade events stream
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("STEP 2: [TRADE] on_trade() - Stream trade events")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 2.1. on_trade()
        #      Subscribe to trade-related events.
        #      Call: account.on_trade(cancellation_event) → gRPC stream → MT5 Server
        #      Returns: Stream of OnTradeResponse (new/disappeared orders, positions, history)
        #      EVENT-DRIVEN: Fires only when trades occur.
        #      Use cases: Trade monitoring, order tracking, execution alerts.
        # ══════════════════════════════════════════════════════════════

        print(f"Streaming (max {MAX_EVENTS} events or {MAX_SECONDS}sec)...")
        print("  [i] Events fire only when trades occur")

        def handle_trade(event_num, trade_data):
            """Handle trade event"""
            print(f"  Event #{event_num}: Type={trade_data.type}")
            if trade_data.event_data:
                ed = trade_data.event_data
                print(f"    New Orders: {len(ed.new_orders)}, Disappeared Orders: {len(ed.disappeared_orders)}")
                print(f"    New Positions: {len(ed.new_positions)}, Disappeared Positions: {len(ed.disappeared_positions)}")
                print(f"    New History Orders: {len(ed.new_history_orders)}, New History Deals: {len(ed.new_history_deals)}")

        stream_gen = account.on_trade(cancellation_event=cancellation_event)

        try:
            await asyncio.wait_for(
                process_stream(stream_gen, "OnTrade", handle_trade),
                timeout=MAX_SECONDS
            )
        except asyncio.TimeoutError:
            print(f"  [!] Timeout after {MAX_SECONDS}sec")

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: on_position_profit() - Position P&L updates stream
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("STEP 3: [$] on_position_profit() - Stream P&L updates")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 3.1. on_position_profit()
        #      Subscribe to real-time P&L changes for open positions.
        #      Call: account.on_position_profit(interval_ms, ignore_empty, cancellation_event) → gRPC stream → MT5 Server
        #      Returns: Stream of OnPositionProfitResponse (new/updated/deleted positions with P&L)
        #      CONDITIONAL: Fires only when positions exist and prices move.
        #      Use cases: Real-time P&L monitoring, risk management.
        # ══════════════════════════════════════════════════════════════

        print(f"Streaming (max {MAX_EVENTS} events or {MAX_SECONDS}sec)...")
        print("  [i] Events fire only when positions exist and prices change")

        def handle_profit(event_num, profit_data):
            """Handle position profit event"""
            total_positions = (len(profit_data.new_positions) +
                             len(profit_data.updated_positions) +
                             len(profit_data.deleted_positions))
            print(f"  #{event_num}: Total={total_positions} "
                  f"(New={len(profit_data.new_positions)} "
                  f"Upd={len(profit_data.updated_positions)} "
                  f"Del={len(profit_data.deleted_positions)})")

            # Show first 3 updated positions
            max_show = min(3, len(profit_data.updated_positions))
            for i in range(max_show):
                pos = profit_data.updated_positions[i]
                print(f"    #{pos.ticket}: {pos.position_symbol} P&L={pos.profit:+.2f}")

            # Show how many more positions
            if len(profit_data.updated_positions) > max_show:
                remaining = len(profit_data.updated_positions) - max_show
                print(f"    ... and {remaining} more positions")

        stream_gen = account.on_position_profit(interval_ms=1000, ignore_empty=True, cancellation_event=cancellation_event)

        try:
            await asyncio.wait_for(
                process_stream(stream_gen, "OnPositionProfit", handle_profit),
                timeout=MAX_SECONDS
            )
        except asyncio.TimeoutError:
            print(f"  [!] Timeout after {MAX_SECONDS}sec")

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 4: on_positions_and_pending_orders_tickets() - Ticket changes stream
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("STEP 4: [#] on_positions_and_pending_orders_tickets() - Stream ticket changes")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 4.1. on_positions_and_pending_orders_tickets()
        #      Subscribe to order/position ticket number changes.
        #      Call: account.on_positions_and_pending_orders_tickets(interval_ms, cancellation_event) → gRPC stream → MT5 Server
        #      Returns: Stream of OnPositionsAndPendingOrdersTicketsResponse (ticket IDs only)
        #      LIGHTWEIGHT: Only ticket IDs, no detailed info.
        #      Use cases: Quick "what's open?" check, ticket tracking.
        # ══════════════════════════════════════════════════════════════

        print(f"Streaming (max {MAX_EVENTS} events or {MAX_SECONDS}sec)...")
        print("  [i] Events fire when orders/positions open or close")

        def handle_tickets(event_num, tickets_data):
            """Handle tickets event"""
            total_tickets = len(tickets_data.pending_order_tickets) + len(tickets_data.position_tickets)
            print(f"  #{event_num}: Total={total_tickets} "
                  f"(Orders={len(tickets_data.pending_order_tickets)} "
                  f"Pos={len(tickets_data.position_tickets)})")

        stream_gen = account.on_positions_and_pending_orders_tickets(interval_ms=1000, cancellation_event=cancellation_event)

        try:
            await asyncio.wait_for(
                process_stream(stream_gen, "OnTickets", handle_tickets),
                timeout=MAX_SECONDS
            )
        except asyncio.TimeoutError:
            print(f"  [!] Timeout after {MAX_SECONDS}sec")

        # ═══════════════════════════════════════════════════════════════════════
        # STEP 5: on_trade_transaction() - Trade transactions stream
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("STEP 5: [TX] on_trade_transaction() - Stream trade transactions")
        print("───────────────────────────────────────────────────────────")

        # ══════════════════════════════════════════════════════════════
        # 5.1. on_trade_transaction()
        #      Subscribe to ALL trading transaction events.
        #      Call: account.on_trade_transaction(cancellation_event) → gRPC stream → MT5 Server
        #      Returns: Stream of OnTradeTransactionResponse (transaction details: order/deal/type/price)
        #      COMPREHENSIVE: Every order placement, execution, modification, deletion.
        #      Use cases: Audit logs, detailed execution tracking, debugging.
        # ══════════════════════════════════════════════════════════════

        print(f"Streaming (max {MAX_EVENTS} events or {MAX_SECONDS}sec)...")
        print("  [i] Fires on all trade-related transactions")

        def handle_transaction(event_num, transaction_data):
            """Handle trade transaction event"""
            if transaction_data.trade_transaction:
                tx = transaction_data.trade_transaction
                print(f"  #{event_num}: TxType={tx.type} Order={tx.order_ticket} Deal={tx.deal_ticket}")
                if tx.symbol:
                    print(f"    {tx.symbol} | Price={tx.price:.5f} Vol={tx.volume:.2f}")
            else:
                print(f"  #{event_num}: Type={transaction_data.type}")

        stream_gen = account.on_trade_transaction(cancellation_event=cancellation_event)

        try:
            await asyncio.wait_for(
                process_stream(stream_gen, "OnTradeTransaction", handle_transaction),
                timeout=MAX_SECONDS
            )
        except asyncio.TimeoutError:
            print(f"  [!] Timeout after {MAX_SECONDS}sec")

        # ═══════════════════════════════════════════════════════════════════════
        # FINAL: STREAMS COMPLETED
        # ═══════════════════════════════════════════════════════════════════════
        print()
        print()
        print("Final: All streams completed")
        print("───────────────────────────────────────────────────────────")
        print("[+] Streaming demo finished successfully")

        print()
        print("═" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("═" * 80)

        print("\nMETHODS DEMONSTRATED (5 total):")
        print("   STREAMING METHODS (5):    on_symbol_tick, on_trade, on_position_profit,")
        print("                             on_positions_and_pending_orders_tickets,")
        print("                             on_trade_transaction")

        print("\nLowLevel Streaming API Features:")
        print("  • Real-time event-driven streams - server pushes updates instantly")
        print("  • gRPC server-streaming - persistent bidirectional connections")
        print("  • High-frequency data: on_symbol_tick fires multiple times per second")
        print("  • Conditional streams: some fire only on activity (trades, positions)")
        print("  • Graceful shutdown: cancellation_event pattern prevents errors")

        print("\nStream Characteristics:")
        print("  - on_symbol_tick: HIGH FREQUENCY (every price update)")
        print("  - on_trade: EVENT-DRIVEN (only when trades occur)")
        print("  - on_position_profit: CONDITIONAL (requires open positions)")
        print("  - on_positions_and_pending_orders_tickets: LIGHTWEIGHT (ticket IDs only)")
        print("  - on_trade_transaction: COMPREHENSIVE (all trading operations)")

        print("\nWHAT'S NEXT:")
        print("   [4] Service Layer Demo    → python main.py service01")

        print("\n" + "═" * 80)

    except Exception as e:
        print()
        print_if_error(e, "Error during demo execution")
        import traceback
        traceback.print_exc()

    finally:
        # Clean disconnection with proper stream shutdown
        print("\n\nFINAL: Stop streams and disconnect")
        print("─" * 59)

        # Step 1: Signal all active streams to stop
        cancellation_event.set()
        print("  → Sent cancellation signal to all streams")

        # Step 2: Give streams time to finish gracefully
        await asyncio.sleep(0.5)
        print("  → Waiting for streams to finish...")

        # Step 3: Close gRPC channel
        try:
            await account.channel.close()
            print("✓ Channel closed successfully")
        except Exception as e:
            print(f"⚠️  Disconnect warning: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    asyncio.run(run_streaming_demo())
