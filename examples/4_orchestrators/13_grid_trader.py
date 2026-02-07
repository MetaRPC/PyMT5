"""
==============================================================================
 FILE: 13_grid_trader.py - GRID TRADING ORCHESTRATOR

 ⚠️  DEMONSTRATION ONLY - NOT PRODUCTION READY
     This orchestrator demonstrates grid trading strategy and API usage.
     Production deployment requires: risk management, error handling, proper position
     sizing, slippage control, logging, monitoring, and extensive testing.

 PURPOSE:
   Automated grid trading system that places a network of pending orders
   at fixed price levels. When orders are triggered and closed, automatically
   replaces them to maintain the grid structure.

 HOW IT WORKS:
   1. Calculates grid levels around current price (center point)
   2. Places pending orders (BUY_STOP above, SELL_STOP below for HEDGING)
   3. Monitors order/position tickets via stream_opened_tickets() (polling)
   4. When order triggers and closes by TP, places new order at that level
   5. Maintains grid structure automatically for specified duration

 TWO GRID MODES:

   HEDGING (Bi-directional):
   - BUY_STOP orders above center price
   - SELL_STOP orders below center price
   - Profits from price oscillations in both directions
   - Higher activity, manages risk with stop losses

   DIRECTIONAL (One-way):
   - Only BUY_STOP or only SELL_STOP
   - Follows strong trend in one direction
   - Lower risk, requires clear trend

 EXAMPLE GRID SETUP:

   Symbol: EURUSD, Current Price: 1.2000
   Grid Step: 20 pips
   Levels: 3 above, 3 below

   HEDGING GRID:
   1.2060 -> BUY_STOP  (TP: 1.2080)
   1.2040 -> BUY_STOP  (TP: 1.2060)
   1.2020 -> BUY_STOP  (TP: 1.2040)
   1.2000 -> CENTER
   1.1980 -> SELL_STOP (TP: 1.1960)
   1.1960 -> SELL_STOP (TP: 1.1940)
   1.1940 -> SELL_STOP (TP: 1.1920)

   When BUY at 1.2020 triggers and closes at 1.2040 (TP):
   -> Automatically place new BUY_STOP at 1.2020

 CONFIGURATION PARAMETERS:
   - grid_type: HEDGING or DIRECTIONAL
   - grid_step_pips: Distance between levels (default: 20 pips)
   - levels_above: Number of levels above center (default: 3)
   - levels_below: Number of levels below center (default: 3)
   - volume_per_level: Volume for each order (default: 0.01 lots)
   - take_profit_pips: TP distance (default: grid_step_pips)
   - update_interval_ms: Check interval (default: 1000ms)
   - duration_minutes: How long to run (default: 3 minutes)
   - dry_run: If True, simulates without real orders (default: False)

 API METHODS USED:
   From MT5Service:
   - stream_opened_tickets()    - Monitor positions/orders via polling (CORE METHOD)
   - place_order()              - Place pending orders (BUY_STOP/SELL_STOP)
   - close_order()              - Cancel pending orders on shutdown
   - get_symbol_tick()          - Current market prices

   From MT5Sugar:
   - get_symbol_info()          - Symbol specifications (point, digits)

 IMPORTANT NOTES:
   - Automatically maintains grid structure
   - Each level triggers only once at a time
   - TP set to next grid level
   - Graceful shutdown cancels all pending orders
   - Works best in ranging markets
   - Runs for specified duration then stops
   - Uses TMT5_ORDER_TYPE_BUY_STOP / TMT5_ORDER_TYPE_SELL_STOP constants
   - Requires OrderSendRequest (not TradeOrderRequest)
   - Cancel orders via close_order() method
   - Uses polling-based stream_opened_tickets() (not event-based stream_trade_updates())

 HOW TO RUN:
   cd examples
   python main.py grid    (or select [13] from menu)

==============================================================================
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '0_common'))

# Import helpers
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_step,
    print_if_error,
    print_success,
    print_info,
    print_warning,
    fatal,
)

# Import progress bar
from progress_bar import Spinner, ProgressBar, TimeProgressBar

# Import APIs
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar

# Import protobuf types
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2


class GridType(Enum):
    """Grid trading type."""
    HEDGING = "hedging"        # BUY above, SELL below
    DIRECTIONAL = "directional"  # Only BUY or only SELL


@dataclass
class GridLevel:
    """Single level in the grid."""
    level_number: int          # Level index (0 = center)
    price: float              # Price for this level
    is_buy: bool              # True=BUY, False=SELL
    pending_ticket: Optional[int] = None  # Pending order ticket
    position_ticket: Optional[int] = None  # Position ticket if triggered
    triggered: bool = False   # Is order currently triggered
    triggered_logged: bool = False   # Has trigger been logged
    closed_logged: bool = False      # Has close been logged


@dataclass
class GridState:
    """State of the entire grid."""
    symbol: str
    center_price: float
    grid_step_pips: float
    levels: List[GridLevel]
    total_pending: int = 0        # Current pending orders
    total_triggered: int = 0      # Total activations (cumulative)
    active_positions: int = 0     # Current open positions
    total_closed: int = 0         # Total closed positions


class GridTradingOrchestrator:
    """
    Automated grid trading orchestrator.
    Maintains a network of pending orders at fixed price levels.
    """

    def __init__(
        self,
        service: MT5Service,
        sugar: MT5Sugar,
        grid_type: GridType = GridType.HEDGING,
        grid_step_pips: float = 20.0,
        levels_above: int = 3,
        levels_below: int = 3,
        volume_per_level: float = 0.01,
        take_profit_pips: Optional[float] = None,
        update_interval_ms: int = 1000,
        dry_run: bool = False
    ):
        """
        Initialize grid trading orchestrator.

        Args:
            service: MT5Service instance
            sugar: MT5Sugar instance
            grid_type: HEDGING or DIRECTIONAL
            grid_step_pips: Distance between grid levels in pips
            levels_above: Number of levels above center
            levels_below: Number of levels below center
            volume_per_level: Volume for each order
            take_profit_pips: TP distance (None = use grid_step_pips)
            update_interval_ms: Update interval in milliseconds
            dry_run: If True, only simulate without real orders
        """
        self.service = service
        self.sugar = sugar
        self.grid_type = grid_type
        self.grid_step_pips = grid_step_pips
        self.levels_above = levels_above
        self.levels_below = levels_below
        self.volume_per_level = volume_per_level
        self.take_profit_pips = take_profit_pips or grid_step_pips
        self.update_interval_ms = update_interval_ms
        self.dry_run = dry_run

        # State tracking
        self.grid_state: Optional[GridState] = None
        self.is_running = False
        self.update_count = 0
        self.pending_tickets: Set[int] = set()
        self.start_balance: Optional[float] = None
        self.end_balance: Optional[float] = None

    async def start(
        self,
        symbol: str,
        duration_minutes: float = 3.0,
        cancellation_event: Optional[asyncio.Event] = None
    ):
        """
        Start the grid trading orchestrator.

        Args:
            symbol: Symbol to trade
            duration_minutes: How long to run in minutes (default: 3.0)
            cancellation_event: Event to signal shutdown
        """
        print("\n" + "=" * 80)
        print("GRID TRADING ORCHESTRATOR - STARTING")
        print("=" * 80)
        print(f"  Grid Type:             {self.grid_type.value.upper()}")
        print(f"  Grid Step:             {self.grid_step_pips:.1f} pips")
        print(f"  Levels Above:          {self.levels_above}")
        print(f"  Levels Below:          {self.levels_below}")
        print(f"  Volume per Level:      {self.volume_per_level:.2f} lots")
        print(f"  Take Profit:           {self.take_profit_pips:.1f} pips")
        print(f"  Update Interval:       {self.update_interval_ms}ms")
        print(f"  Run Duration:          {duration_minutes:.1f} minutes")
        print(f"  Dry Run Mode:          {self.dry_run}")
        print()

        # Create cancellation event if not provided
        if cancellation_event is None:
            cancellation_event = asyncio.Event()

        self.is_running = True
        start_time = time.time()
        duration_seconds = duration_minutes * 60

        try:
            # Step 1: Initialize grid with spinner
            with Spinner(description="Calculating grid") as spinner:
                await self._initialize_grid(symbol)
                spinner.update()

            # Get starting balance
            if not self.dry_run:
                self.start_balance = await self.sugar.get_balance()
                print_info(f"Starting balance: ${self.start_balance:.2f}")
                print()

            # Step 2: Start stream BEFORE placing orders
            print_info("Starting ticket stream...")
            stream_gen = self.service.stream_opened_tickets(
                interval_ms=self.update_interval_ms,
                cancellation_event=cancellation_event
            )

            # Wait for first update to ensure stream is ready
            with Spinner(description="Waiting for stream connection") as spinner:
                try:
                    first_update = await asyncio.wait_for(stream_gen.__anext__(), timeout=30.0)
                    spinner.update()
                except asyncio.TimeoutError:
                    print_warning("Stream timeout - no data received in 30 seconds!")
                    print("  This indicates a problem with the gRPC stream or MT5 server")
                    return

            # Step 3: Place initial orders with progress bar
            total_orders = len(self.grid_state.levels)
            with ProgressBar(total=total_orders, description="Placing orders") as progress:
                for level in self.grid_state.levels:
                    await self._place_grid_order(level)
                    progress.update(progress.current + 1)
                    await asyncio.sleep(0.1)  # Small delay between orders

            print()
            print_success(f"Grid initialized: {self.grid_state.total_pending} pending orders placed")
            print()

            # Step 4: Main monitoring loop
            print_info("Starting grid monitoring...")
            print(f"  Will run for {duration_minutes:.1f} minutes")
            print("  Press Ctrl+C to stop early")
            print("-" * 80)

            # Process first update we already received
            await self._process_ticket_update(first_update)
            self.update_count += 1
            print()

            # Continue with normal loop with time progress bar
            progress_bar = TimeProgressBar(
                total_seconds=duration_seconds,
                message="Grid monitoring"
            )
            progress_bar.update(0)  # Show initial state

            async for update in stream_gen:
                # Check if should stop
                elapsed = time.time() - start_time
                if elapsed >= duration_seconds or cancellation_event.is_set():
                    progress_bar.finish()
                    print()
                    print_info(f"Duration reached ({elapsed:.1f}s) - stopping...")
                    break

                # Update progress bar
                progress_bar.update(elapsed)

                # Process update
                await self._process_ticket_update(update)
                self.update_count += 1

        except asyncio.CancelledError:
            print()
            print_info("Orchestrator stopped by user")
        except Exception as e:
            print()
            print_if_error(e, "Orchestrator error")
        finally:
            # Graceful shutdown - cancel all pending orders
            await self._cleanup_grid()

            self.is_running = False
            cancellation_event.set()
            await asyncio.sleep(0.5)  # Give streams time to close

            print("\n" + "=" * 80)
            print("GRID TRADING ORCHESTRATOR - STOPPED")
            print("=" * 80)
            print(f"  Total Runtime:          {time.time() - start_time:.1f}s")
            print(f"  Total Updates:          {self.update_count}")
            if self.grid_state:
                print(f"  Grid Levels:            {len(self.grid_state.levels)}")
                print(f"  Orders Triggered:       {self.grid_state.total_triggered}")
                print(f"  Orders Closed:          {self.grid_state.total_closed}")
                print(f"  Still Open:             {self.grid_state.active_positions}")
                print(f"  Still Pending:          {self.grid_state.total_pending}")

                # Calculate efficiency
                if self.grid_state.total_triggered > 0:
                    efficiency = (self.grid_state.total_closed / self.grid_state.total_triggered) * 100
                    print(f"  Close Rate:             {efficiency:.1f}%")

            # Get ending balance and calculate profit/loss
            if not self.dry_run and self.start_balance is not None:
                print()
                print(f"  {'─' * 76}")
                print(f"  PROFIT/LOSS SUMMARY")
                print(f"  {'─' * 76}")

                # Get current balance
                self.end_balance = await self.sugar.get_balance()
                balance_change = self.end_balance - self.start_balance

                print(f"  Starting Balance:       ${self.start_balance:.2f}")
                print(f"  Ending Balance:         ${self.end_balance:.2f}")
                print(f"  Net Profit/Loss:        ${balance_change:+.2f}")

                if self.grid_state and self.grid_state.total_closed > 0:
                    avg_per_trade = balance_change / self.grid_state.total_closed
                    print(f"  Avg P/L per Trade:      ${avg_per_trade:+.2f}")

                # Color-coded result
                if balance_change > 0:
                    print_success(f"Result: PROFIT of ${balance_change:.2f}")
                elif balance_change < 0:
                    print_warning(f"Result: LOSS of ${abs(balance_change):.2f}")
                else:
                    print_info("Result: BREAK EVEN")

            print()

    async def _initialize_grid(self, symbol: str):
        """Calculate and initialize grid levels."""
        print_step(1, f"Calculating grid for {symbol}")

        try:
            # Get current price
            tick = await self.service.get_symbol_tick(symbol)
            center_price = (tick.bid + tick.ask) / 2

            # Get symbol info
            symbol_info = await self.sugar.get_symbol_info(symbol)
            point = symbol_info.point
            pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point

            # Calculate grid step in price
            step_price = self.grid_step_pips * pip

            # Create grid levels
            levels = []

            if self.grid_type == GridType.HEDGING:
                # BUY levels above center
                for i in range(1, self.levels_above + 1):
                    price = center_price + (i * step_price)
                    levels.append(GridLevel(
                        level_number=i,
                        price=round(price, symbol_info.digits),
                        is_buy=True
                    ))

                # SELL levels below center
                for i in range(1, self.levels_below + 1):
                    price = center_price - (i * step_price)
                    levels.append(GridLevel(
                        level_number=-i,
                        price=round(price, symbol_info.digits),
                        is_buy=False
                    ))
            else:  # DIRECTIONAL
                # User chooses direction based on current trend
                # For demo, we'll use BUY direction
                for i in range(1, self.levels_above + self.levels_below + 1):
                    price = center_price + (i * step_price)
                    levels.append(GridLevel(
                        level_number=i,
                        price=round(price, symbol_info.digits),
                        is_buy=True
                    ))

            self.grid_state = GridState(
                symbol=symbol,
                center_price=center_price,
                grid_step_pips=self.grid_step_pips,
                levels=levels
            )

            print(f"  Center Price:    {center_price:.5f}")
            print(f"  Grid Step:       {self.grid_step_pips:.1f} pips ({step_price:.5f})")
            print(f"  Total Levels:    {len(levels)}")
            print()

        except Exception as e:
            print_if_error(e, "Failed to initialize grid")
            raise

    async def _place_grid_order(self, level: GridLevel):
        """Place pending order for a grid level."""
        if self.dry_run:
            level.pending_ticket = 999900 + level.level_number
            self.grid_state.total_pending += 1
            return

        try:
            # Get symbol info for TP calculation
            symbol_info = await self.sugar.get_symbol_info(self.grid_state.symbol)
            point = symbol_info.point
            pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point
            tp_distance = self.take_profit_pips * pip

            # Calculate TP price
            if level.is_buy:
                tp_price = level.price + tp_distance
                order_type = trading_helper_pb2.TMT5_ORDER_TYPE_BUY_STOP
            else:
                tp_price = level.price - tp_distance
                order_type = trading_helper_pb2.TMT5_ORDER_TYPE_SELL_STOP

            tp_price = round(tp_price, symbol_info.digits)

            # Build order request
            order_req = trading_helper_pb2.OrderSendRequest(
                symbol=self.grid_state.symbol,
                operation=order_type,
                volume=self.volume_per_level,
                price=level.price,
                take_profit=tp_price
            )

            # Place order
            result = await self.service.place_order(order_req)

            if result.returned_code == 10009:  # TRADE_RETCODE_DONE
                level.pending_ticket = result.order
                self.pending_tickets.add(result.order)
                self.grid_state.total_pending += 1
            else:
                direction = "BUY" if level.is_buy else "SELL"
                print(f"    [WARN] Failed {direction}_STOP @ {level.price:.5f}: code {result.returned_code}")

        except Exception as e:
            print_if_error(e, f"Error placing order at {level.price:.5f}")

    async def _process_ticket_update(self, update):
        """Process ticket update and maintain grid."""
        if not self.grid_state:
            return

        # Convert to sets for easy comparison
        current_positions = set(update.position_tickets)
        current_pending = set(update.pending_order_tickets)

        # Check each grid level
        for level in self.grid_state.levels:
            if not level.pending_ticket:
                continue

            # Check if pending order was triggered (moved to positions)
            if level.pending_ticket not in current_pending:
                if not level.triggered:
                    # Order triggered - check if it became a position
                    # Note: ticket might change, so we check if any new position appeared
                    level.triggered = True
                    level.position_ticket = level.pending_ticket
                    self.grid_state.total_pending -= 1
                    self.grid_state.total_triggered += 1  # Cumulative count
                    self.grid_state.active_positions += 1  # Current open positions

                    # Log only once
                    if not level.triggered_logged:
                        direction = "BUY" if level.is_buy else "SELL"
                        print(f"  [OK] Grid level triggered: {direction} at {level.price:.5f} (ticket #{level.pending_ticket})")
                        level.triggered_logged = True

            # Check if position was closed (hit TP)
            if level.triggered and level.position_ticket:
                if level.position_ticket not in current_positions:
                    # Position closed - could place new order here
                    self.grid_state.active_positions -= 1  # Decrease current open positions
                    self.grid_state.total_closed += 1

                    # Log only once
                    if not level.closed_logged:
                        direction = "BUY" if level.is_buy else "SELL"
                        print(f"  [OK] Position closed: {direction} at {level.price:.5f} (ticket #{level.position_ticket})")
                        level.closed_logged = True

                    # Reset level for potential re-entry
                    level.triggered = False
                    level.position_ticket = None
                    level.pending_ticket = None
                    level.triggered_logged = False
                    level.closed_logged = False
                    # Restore grid by placing new order at this level
                    await self._place_grid_order(level)

    async def _cleanup_grid(self):
        """Cancel all pending orders on shutdown."""
        if not self.grid_state:
            return

        if self.dry_run:
            print()
            print_info("Dry run mode - no cleanup needed")
            return

        print()
        print_info("Cleaning up grid - canceling pending orders...")

        # Import error handling utilities
        from MetaRpcMT5.helpers.errors import (
            get_retcode_message,
            TRADE_RETCODE_DONE,
            TRADE_RETCODE_POSITION_CLOSED,
            TRADE_RETCODE_NO_CHANGES
        )

        canceled = 0
        failed = 0
        failed_details = []  # Store detailed error messages

        for level in self.grid_state.levels:
            if level.pending_ticket and not level.triggered:
                try:
                    close_req = trading_helper_pb2.OrderCloseRequest(
                        ticket=level.pending_ticket
                    )

                    # Small delay to prevent overwhelming the server
                    await asyncio.sleep(0.1)

                    # FIXED: close_order returns int, not object!
                    result_code = await self.service.close_order(close_req)

                    if result_code == TRADE_RETCODE_DONE:
                        canceled += 1
                        level.pending_ticket = None
                    elif result_code in (TRADE_RETCODE_POSITION_CLOSED, TRADE_RETCODE_NO_CHANGES):
                        # Order already closed/deleted - not an error
                        canceled += 1
                        level.pending_ticket = None
                    else:
                        failed += 1
                        # Store detailed error for reporting
                        direction = "BUY" if level.is_buy else "SELL"
                        failed_details.append(
                            f"    Ticket #{level.pending_ticket} ({direction} @ {level.price:.5f}): "
                            f"{get_retcode_message(result_code)} (code {result_code})"
                        )
                except Exception as e:
                    failed += 1
                    direction = "BUY" if level.is_buy else "SELL"
                    failed_details.append(
                        f"    Ticket #{level.pending_ticket} ({direction} @ {level.price:.5f}): {e}"
                    )

        if canceled > 0:
            print_success(f"Canceled {canceled} pending order(s)")

        if failed > 0:
            print_warning(f"Failed to cancel {failed} order(s):")
            # Print detailed error for each failed order
            for detail in failed_details:
                print(detail)


async def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print("GRID TRADING ORCHESTRATOR DEMO")
    print("=" * 80)
    print()

    # Load configuration
    try:
        config = load_settings()
    except Exception as e:
        fatal(e, "Failed to load settings")

    # Connect to MT5
    print("Connecting to MT5...")
    try:
        account = await create_and_connect_mt5(config)
        service = MT5Service(account)
        test_symbol = config['test_symbol']
        sugar = MT5Sugar(service, default_symbol=test_symbol)
        print_success("Connected successfully!")
        print()
    except Exception as e:
        fatal(e, "Failed to connect")

    # Create cancellation event
    cancellation_event = asyncio.Event()

    try:
        # Auto-detect grid type based on market analysis
        print("[AUTO-DETECT] Analyzing market conditions...")

        # Get recent price data to detect trend
        try:
            tick = await sugar.get_price_info(test_symbol)
            current_price = (tick.bid + tick.ask) / 2

            # Simple trend detection: compare current price with recent average
            # In production, you'd use more sophisticated indicators
            await asyncio.sleep(0.1)  # Small delay
            tick2 = await sugar.get_price_info(test_symbol)
            price2 = (tick2.bid + tick2.ask) / 2

            price_change_pct = abs(price2 - current_price) / current_price * 100

            # Decision logic:
            # - Low volatility / ranging → HEDGING (safer, both directions)
            # - High volatility / trending → DIRECTIONAL (trend following)
            if price_change_pct < 0.01:  # Very stable market
                grid_type = GridType.HEDGING
                print_info("Market: RANGING → Using HEDGING mode (BUY + SELL)")
            else:
                grid_type = GridType.DIRECTIONAL
                print_info("Market: TRENDING → Using DIRECTIONAL mode (trend following)")

        except Exception as e:
            # Fallback to safe default
            print_warning(f"Market analysis failed: {e}")
            grid_type = GridType.HEDGING
            print_info("Defaulting to HEDGING mode (safer)")

        print()

        # Create orchestrator
        orchestrator = GridTradingOrchestrator(
            service=service,
            sugar=sugar,
            grid_type=grid_type,
            grid_step_pips=20.0,       # 20 pips between levels
            levels_above=3,            # 3 levels above center
            levels_below=3,            # 3 levels below center
            volume_per_level=0.10,     # 0.10 lots per order (increased from 0.01)
            take_profit_pips=20.0,     # TP = grid step
            update_interval_ms=1000,   # Check every second
            dry_run=False              # Set True for testing
        )

        # Run orchestrator for 3 minutes
        await orchestrator.start(
            symbol=config['test_symbol'],
            duration_minutes=3.0,
            cancellation_event=cancellation_event
        )

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user - shutting down gracefully...")
        cancellation_event.set()
        await asyncio.sleep(0.5)

    finally:
        # Disconnect
        print("\nDisconnecting from MT5...")
        try:
            await account.channel.close()
            print_success("Disconnected successfully")
        except Exception as e:
            print_if_error(e, "Disconnect failed")

    print("\n" + "=" * 80)
    print("[OK] DEMO COMPLETED")
    print("=" * 80)
    print()
    print("[!] KEY FEATURES DEMONSTRATED:")
    print("   - Two grid modes: HEDGING (bi-directional) and DIRECTIONAL (one-way)")
    print("   - Automatic grid level calculation")
    print("   - Pending order placement with TP")
    print("   - Real-time order monitoring")
    print("   - Automatic grid maintenance")
    print("   - Graceful cleanup on shutdown")
    print("   - Timed execution with live progress")
    print()


if __name__ == "__main__":
    asyncio.run(main())
