"""
══════════════════════════════════════════════════════════════════════════════
 FILE: 05_service_streaming.py - MID-LEVEL SERVICE API STREAMING DEMO

 📚 WHAT THIS DEMO COVERS (5 Streaming Methods):
   PREPARATION: CREATE MT5SERVICE & CONNECT
   STEP 1: STREAM TICKS - Real-time price updates
   STEP 2: STREAM TRADE UPDATES - Trade events (positions/orders)
   STEP 3: STREAM POSITION PROFITS - P&L updates
   STEP 4: STREAM OPENED TICKETS - Lightweight ticket monitoring
   STEP 5: STREAM TRANSACTIONS - Detailed transaction log

 🎯 PURPOSE:
   Demonstrate ALL 5 streaming methods in MT5Service.
   Each stream runs for limited events/time with 2-second delays between.

 📊 LAYERS:
   LOW  → MT5Account (protobuf/gRPC) - NOT USED here
   MID  → MT5Service (clean Python)  - USED HERE ✓
   HIGH → MT5Sugar (ultra-simple)    - NOT USED here

 💡 KEY CONCEPTS:
   - AsyncIterator pattern for all streams
   - Automatic type conversion (Timestamp → datetime)
   - Clean Python dataclasses (SymbolTick, etc.)
   - MAX_EVENTS and MAX_DURATION limits
   - 2-second delays between streams
   - cancellation_event for graceful stream shutdown

 ⚠️  IMPORTANT - PROPER STREAM SHUTDOWN:
   1. Create cancellation_event = asyncio.Event() ONCE at start
   2. Pass cancellation_event to ALL stream methods
   3. In finally block:
      a) Call cancellation_event.set() - signals all streams to stop
      b) Wait 0.5s for streams to finish gracefully
      c) Then call disconnect() - closes gRPC channel cleanly
   - This prevents DEADLINE_EXCEEDED errors on disconnect

 🚀 HOW TO RUN THIS DEMO:
   cd examples
   python main.py 5          (or select [5] from interactive menu)

══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))

from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_step,
    print_if_error,
    print_success,
    print_info,
    fatal,
)
from pymt5.mt5_service import MT5Service


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS - Stream Control
# ═══════════════════════════════════════════════════════════════════════════

MAX_EVENTS = 5      # Maximum events to receive per stream
MAX_DURATION = 10   # Maximum duration in seconds for some streams


async def main():
    print("=" * 80)
    print("MT5 SERVICE STREAMING DEMO - ALL 5 STREAMING METHODS")
    print("=" * 80)
    print()

    # Load settings with error handling
    try:
        config = load_settings()
    except Exception as e:
        fatal(e, "Failed to load settings")

    # ══════════════════════════════════════════════════════════════════════════
    # PREPARATION: CREATE MT5SERVICE & CONNECT
    # ══════════════════════════════════════════════════════════════════════════
    print()
    print("=" * 80)
    print("PREPARATION: CREATE MT5SERVICE & CONNECT")
    print("=" * 80)
    try:
        account = await create_and_connect_mt5(config)
        service = MT5Service(account)
        print_success("MT5Service created and connected")
        print()
    except Exception as e:
        fatal(e, "Failed to connect to MT5")

    # Create cancellation event for graceful stream shutdown
    cancellation_event = asyncio.Event()

    try:
        # ══════════════════════════════════════════════════════════════════════
        # STEP 1: STREAM TICKS
        #         Monitor real-time price updates for symbols.
        #
        #         Method: stream_ticks(symbols: List[str])
        #         Returns: AsyncIterator[SymbolTick]
        #
        #         SymbolTick dataclass contains:
        #         - time: datetime
        #         - bid, ask, last: float
        #         - volume: int
        #         - flags: int
        # ══════════════════════════════════════════════════════════════════════
        print_step(1, "STREAM TICKS - Real-time Price Updates")
        print(f"  Method: stream_ticks()")
        print(f"  Symbol: {config['test_symbol']}")
        print(f"  📊 Max events: {MAX_EVENTS}, Max duration: {MAX_DURATION}s")
        print()

        count = 0
        try:
            async def process_ticks():
                nonlocal count
                async for tick in service.stream_ticks([config['test_symbol']], cancellation_event):
                    count += 1
                    spread = tick.ask - tick.bid
                    time_str = tick.time.strftime('%H:%M:%S')
                    print(f"  Tick #{count:2d}: Bid={tick.bid:8.5f} Ask={tick.ask:8.5f} "
                          f"Spread={spread:.5f} Time={time_str}")

                    if count >= MAX_EVENTS:
                        print()
                        print_success(f"Received {count} tick events")
                        break

            await asyncio.wait_for(process_ticks(), timeout=MAX_DURATION)
        except asyncio.TimeoutError:
            print_info(f"Timeout after {MAX_DURATION}s (received {count} events)")
        except Exception as e:
            print_if_error(e, "Stream ticks error")

        print()
        await asyncio.sleep(2)  # 2-second delay between streams

        # ══════════════════════════════════════════════════════════════════════
        # STEP 2: STREAM TRADE UPDATES
        #         Monitor trade events (positions and orders changes).
        #
        #         Method: stream_trade_updates()
        #         Returns: AsyncIterator[Any] with fields:
        #         - opened_positions: List
        #         - opened_orders: List
        #
        #         NOTE: May have no events if no trading activity.
        # ══════════════════════════════════════════════════════════════════════
        print_step(2, "STREAM TRADE UPDATES - Trade Events")
        print(f"  Method: stream_trade_updates()")
        print(f"  Purpose: Monitor positions/orders changes")
        print(f"  📊 Max events: {MAX_EVENTS}, Max duration: {MAX_DURATION}s")
        print()

        count = 0
        try:
            async def process_trade_updates():
                nonlocal count
                async for data in service.stream_trade_updates(cancellation_event):
                    count += 1
                    pos_count = len(data.opened_positions)
                    ord_count = len(data.opened_orders)
                    print(f"  Event #{count:2d}: Positions={pos_count} Orders={ord_count}")

                    if count >= MAX_EVENTS:
                        print()
                        print_success(f"Received {count} trade events")
                        break

            await asyncio.wait_for(process_trade_updates(), timeout=MAX_DURATION)
            if count == 0:
                print_info("No events (normal if no trading activity)")
        except asyncio.TimeoutError:
            if count == 0:
                print_info(f"Timeout after {MAX_DURATION}s - no events (normal if no trading)")
            else:
                print_info(f"Timeout after {MAX_DURATION}s (received {count} events)")
        except Exception as e:
            print_if_error(e, "Stream trade updates error")

        print()
        await asyncio.sleep(2)  # 2-second delay between streams

        # ══════════════════════════════════════════════════════════════════════
        # STEP 3: STREAM POSITION PROFITS
        #         Monitor P&L updates for open positions.
        #
        #         Method: stream_position_profits(interval_ms, ignore_empty)
        #         Returns: AsyncIterator[Any] with fields:
        #         - updated_positions: List with profit field
        #
        #         Parameters:
        #         - interval_ms: Update interval in milliseconds (1000 = 1s)
        #         - ignore_empty: Skip updates with no data
        #
        #         NOTE: No updates if no open positions.
        # ══════════════════════════════════════════════════════════════════════
        print_step(3, "STREAM POSITION PROFITS - P&L Updates")
        print(f"  Method: stream_position_profits()")
        print(f"  Purpose: Monitor profit/loss changes")
        print(f"  📊 Interval: 1000ms, Max events: {MAX_EVENTS}")
        print()

        count = 0
        try:
            async def process_position_profits():
                nonlocal count
                async for data in service.stream_position_profits(1000, True, cancellation_event):
                    count += 1
                    total_pnl = sum(pos.profit for pos in data.updated_positions)
                    pos_count = len(data.updated_positions)
                    print(f"  Update #{count:2d}: Positions={pos_count} Total P&L={total_pnl:8.2f}")

                    if count >= MAX_EVENTS:
                        print()
                        print_success(f"Received {count} profit updates")
                        break

            await asyncio.wait_for(process_position_profits(), timeout=MAX_DURATION)
            if count == 0:
                print_info("No updates (no open positions)")
        except asyncio.TimeoutError:
            if count == 0:
                print_info(f"Timeout after {MAX_DURATION}s - no updates (no open positions)")
            else:
                print_info(f"Timeout after {MAX_DURATION}s (received {count} events)")
        except Exception as e:
            print_if_error(e, "Stream position profits error")

        print()
        await asyncio.sleep(2)  # 2-second delay between streams

        # ══════════════════════════════════════════════════════════════════════
        # STEP 4: STREAM OPENED TICKETS
        #         Lightweight monitoring of position/order ticket numbers.
        #
        #         Method: stream_opened_tickets(interval_ms)
        #         Returns: AsyncIterator[Any] with fields:
        #         - opened_position_tickets: List[int]
        #         - opened_orders_tickets: List[int]
        #
        #         Parameters:
        #         - interval_ms: Update interval in milliseconds (1000 = 1s)
        #
        #         USE CASE: Detect new positions/orders without full data.
        # ══════════════════════════════════════════════════════════════════════
        print_step(4, "STREAM OPENED TICKETS - Lightweight Monitoring")
        print(f"  Method: stream_opened_tickets()")
        print(f"  Purpose: Monitor ticket number changes")
        print(f"  📊 Interval: 1000ms, Max events: {MAX_EVENTS}")
        print()

        count = 0
        try:
            async def process_opened_tickets():
                nonlocal count
                async for data in service.stream_opened_tickets(1000, cancellation_event):
                    count += 1
                    pos_tickets = list(data.position_tickets)
                    ord_tickets = list(data.pending_order_tickets)
                    print(f"  Update #{count:2d}: Position tickets={pos_tickets} Pending order tickets={ord_tickets}")

                    if count >= MAX_EVENTS:
                        print()
                        print_success(f"Received {count} ticket updates")
                        break

            await asyncio.wait_for(process_opened_tickets(), timeout=MAX_DURATION)
        except asyncio.TimeoutError:
            print_info(f"Timeout after {MAX_DURATION}s (received {count} events)")
        except Exception as e:
            print_if_error(e, "Stream opened tickets error")

        print()
        await asyncio.sleep(2)  # 2-second delay between streams

        # ══════════════════════════════════════════════════════════════════════
        # STEP 5: STREAM TRANSACTIONS
        #         Detailed transaction log for all trade operations.
        #
        #         Method: stream_transactions()
        #         Returns: AsyncIterator[Any] with fields:
        #         - trade_transaction: Object with type, order, deal, etc.
        #
        #         USE CASE: Audit trail, monitoring all trading activity.
        #
        #         NOTE: May have no transactions if no trading.
        # ══════════════════════════════════════════════════════════════════════
        print_step(5, "STREAM TRANSACTIONS - Detailed Transaction Log")
        print(f"  Method: stream_transactions()")
        print(f"  Purpose: Monitor all trading operations")
        print(f"  📊 Max events: {MAX_EVENTS}, Max duration: {MAX_DURATION}s")
        print()

        count = 0
        try:
            async def process_transactions():
                nonlocal count
                async for data in service.stream_transactions(cancellation_event):
                    count += 1
                    tx_type = data.trade_transaction.type
                    print(f"  Transaction #{count:2d}: Type={tx_type}")

                    if count >= MAX_EVENTS:
                        print()
                        print_success(f"Received {count} transactions")
                        break

            await asyncio.wait_for(process_transactions(), timeout=MAX_DURATION)
            if count == 0:
                print_info("No transactions (no trading activity)")
        except asyncio.TimeoutError:
            if count == 0:
                print_info(f"Timeout after {MAX_DURATION}s - no transactions (no trading activity)")
            else:
                print_info(f"Timeout after {MAX_DURATION}s (received {count} events)")
        except Exception as e:
            print_if_error(e, "Stream transactions error")

        print()

    finally:
        # ══════════════════════════════════════════════════════════════════════
        # FINAL: STOP STREAMS & DISCONNECT
        # ══════════════════════════════════════════════════════════════════════
        print()
        print("─" * 80)
        print("FINAL: Stop streams and disconnect from MT5")
        print("─" * 80)

        # Step 1: Signal all active streams to stop
        cancellation_event.set()
        print("  → Sent cancellation signal to all streams")

        # Step 2: Give streams time to finish gracefully
        await asyncio.sleep(0.5)
        print("  → Waiting for streams to finish...")

        # Step 3: Disconnect from MT5 and close channel
        try:
            await account.channel.close()
            print_success("Disconnected successfully")
        except Exception as e:
            print_if_error(e, "Disconnect failed")

    # ═══════════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════════════
    print()
    print("=" * 80)
    print("✓ STREAMING DEMO COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print()
    print("📋 SUMMARY - 5 Streaming Methods Demonstrated:")
    print("   1. stream_ticks()             - Real-time price updates")
    print("   2. stream_trade_updates()     - Trade events (positions/orders)")
    print("   3. stream_position_profits()  - P&L updates")
    print("   4. stream_opened_tickets()    - Lightweight ticket monitoring")
    print("   5. stream_transactions()      - Detailed transaction log")
    print()
    print("🎯 KEY TAKEAWAYS:")
    print("   • All streams use AsyncIterator pattern")
    print("   • Clean Python types (datetime, dataclasses)")
    print("   • 30-80% less code than low-level API")
    print("   • Automatic type conversion")
    print("   • Graceful error handling")
    print("   • cancellation_event prevents disconnect errors")
    print()
    print("🚀 NEXT STEPS:")
    print("   1. Combine multiple streams for comprehensive monitoring")
    print("   2. Build real-time trading dashboards")
    print("   3. Create automated trading strategies")
    print("   4. Explore MT5Sugar (HIGH-level) for even simpler API")
    print()


if __name__ == "__main__":
    asyncio.run(main())