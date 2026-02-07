"""
==============================================================================
 FILE: 11_trailing_stop.py - TRAILING STOP ORCHESTRATOR

  ⚠️  DEMONSTRATION ONLY - NOT PRODUCTION READY
      This orchestrator demonstrates trailing stop strategy and API usage.
      Production deployment requires: risk management, error handling, proper position
      sizing, slippage control, logging, monitoring, and extensive testing.

  🎯 PURPOSE:
   Automated trailing stop-loss management with intelligent auto-close.
   Opens test positions, monitors them in real-time, and adjusts SL to
   protect profit. Auto-closes positions that don't perform.

   HOW IT WORKS:
   1. Opens 2 test positions automatically (BUY + SELL, 0.01 lot each)
   2. Monitors positions via stream_position_profits() every second
   3. AUTO-CLOSE CONDITIONS (checked every update):
      • If loss exceeds 50 pips → close immediately
      • If profit doesn't reach 30 pips after 2 minutes → close
   4. TRAILING ACTIVATION (when profit >= 30 pips):
      • Trailing stop activates automatically
      • Moves SL closer to current price at 20 pips distance
      • Only moves SL in favorable direction (locks profit)
   5. Shows detailed status every 30 seconds with countdown timers
   6. Runs for 3 minutes, then prints summary with total P&L

  📚 EXAMPLE SCENARIO:
   BUY EURUSD at 1.2000 (auto-opened):
   - Trail Distance: 20 pips
   - Activation: 30 pips profit
   - Max Loss: 50 pips (auto-close)
   - Max Wait: 2 minutes (auto-close if not activated)

   Scenario A - Profitable (trailing activates):
     Price moves to 1.2040 (+40 pips profit):
      → Trailing activates (>30 pips profit)
      → SL moves to 1.2020 (price - 20 pips)

     Price moves to 1.2060 (+60 pips profit):
      → SL moves to 1.2040 (price - 20 pips)

     Price reverses to 1.2038:
      → SL at 1.2040 triggers = +40 pips profit locked!

   Scenario B - No activation (auto-close):
     Price oscillates between 1.1990-1.2010 (-10 to +10 pips)
     After 2 minutes: Profit = +5 pips (< 30 pips needed)
      → AUTO-CLOSE: +5p ($+0.50) | No activation after 2.0 min

   Scenario C - Big loss (auto-close):
     Price drops to 1.1950 (-50 pips)
      → AUTO-CLOSE: -50.0p ($-5.00) | Loss exceeded 50 pips

    💡 CONFIGURATION PARAMETERS:
   - trail_distance_pips: Distance between current price and SL (default: 20)
   - activation_profit_pips: Min profit to activate trailing (default: 30)
   - max_wait_minutes: Auto-close if not activated (default: 2.0)
   - max_loss_pips: Auto-close if loss exceeds this (default: 50.0)
   - update_interval_ms: How often to check positions (default: 1000ms)
   - duration_minutes: How long to run (default: 3 minutes)
   - managed_tickets: List of positions to manage (set automatically)
   - symbols: List of symbols to monitor (default: all)
   - dry_run: If True, only logs actions without modifying orders

    API METHODS USED:
   From MT5Service:
   - stream_position_profits() - Real-time P&L monitoring (CORE METHOD)
   - get_opened_orders()       - Get current positions at startup
   - modify_order()            - Update SL levels
   - get_symbol_tick()         - Get current prices for calculations

   From MT5Sugar:
   - buy_market()              - Open BUY position
   - sell_market()             - Open SELL position
   - close_position()          - Close position by ticket
   - get_symbol_info()         - Get symbol specifications (point, digits)

    ⚠️ IMPORTANT NOTES:
   - Automatically opens 2 test positions (BUY + SELL) at startup
   - Only manages positions it opened (ignores other account positions)
   - Only moves SL in favorable direction (locks profit)
   - Auto-closes losing positions (> 50 pips loss)
   - Auto-closes stagnant positions (no activation after 2 minutes)
   - Shows detailed status every 30 seconds with countdown timers
   - Prints summary at end: total P&L in pips and dollars
   - Uses streaming for minimal latency (1 second updates)
   - Graceful shutdown via cancellation_event
   - Works with any symbol (Forex, Stocks, Futures)

   🚀 HOW TO RUN:
   cd examples
   python main.py trailing    (or select [11] from menu)

==============================================================================
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

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
from progress_bar import Spinner, TimeProgressBar

# Import APIs
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar

# Import protobuf types
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2


@dataclass
class TrailingState:
    """State tracker for a position being trailed."""
    ticket: int
    symbol: str
    is_buy: bool
    open_price: float
    current_sl: float
    highest_price: float  # For BUY positions
    lowest_price: float   # For SELL positions
    trailing_active: bool
    last_update: datetime
    position_opened_at: datetime  # Track when position was opened
    profit_pips: float = 0.0  # Current profit in pips
    profit_dollars: float = 0.0  # Current profit in dollars


class TrailingStopOrchestrator:
    """
    Automated trailing stop orchestrator.
    Monitors open positions and adjusts stop-loss levels to protect profit.
    """

    def __init__(
        self,
        service: MT5Service,
        sugar: MT5Sugar,
        trail_distance_pips: float = 20.0,
        activation_profit_pips: float = 30.0,
        update_interval_ms: int = 1000,
        symbols: Optional[list] = None,
        dry_run: bool = False,
        max_wait_minutes: float = 2.0,  # Close if not activated after N minutes
        max_loss_pips: float = 50.0,    # Close if loss exceeds N pips
        managed_tickets: Optional[list] = None  # Only manage these tickets
    ):
        """
        Initialize trailing stop orchestrator.

        Args:
            service: MT5Service instance
            sugar: MT5Sugar instance
            trail_distance_pips: Distance to keep SL from current price
            activation_profit_pips: Minimum profit to activate trailing
            update_interval_ms: Update interval in milliseconds
            symbols: List of symbols to monitor (None = all)
            dry_run: If True, only simulate without real modifications
            max_wait_minutes: Auto-close if not activated after N minutes
            max_loss_pips: Auto-close if loss exceeds N pips
            managed_tickets: List of ticket numbers to manage (None = all positions)
        """
        self.service = service
        self.sugar = sugar
        self.trail_distance_pips = trail_distance_pips
        self.activation_profit_pips = activation_profit_pips
        self.update_interval_ms = update_interval_ms
        self.symbols = symbols
        self.dry_run = dry_run
        self.max_wait_minutes = max_wait_minutes
        self.max_loss_pips = max_loss_pips
        self.managed_tickets = managed_tickets  # Only these positions can be auto-closed

        # State tracking
        self.trailing_positions: Dict[int, TrailingState] = {}
        self.is_running = False
        self.total_modifications = 0
        self.auto_closed_count = 0  # Track auto-closed positions
        self.closed_positions_summary = []  # Track closed positions for summary
        self.update_count = 0
        self.last_status_time = 0.0

    async def start(self, duration_minutes: float = 3.0, cancellation_event: Optional[asyncio.Event] = None):
        """
        Start the trailing stop orchestrator.

        Args:
            duration_minutes: How long to run in minutes (default: 3.0)
            cancellation_event: Event to signal shutdown
        """
        print("\n" + "=" * 80)
        print("TRAILING STOP ORCHESTRATOR - STARTING")
        print("=" * 80)
        print(f"  Trail Distance:        {self.trail_distance_pips:.1f} pips")
        print(f"  Activation Profit:     {self.activation_profit_pips:.1f} pips")
        print(f"  Max Wait Time:         {self.max_wait_minutes:.1f} minutes (auto-close if not activated)")
        print(f"  Max Loss:              {self.max_loss_pips:.1f} pips (auto-close on loss)")
        print(f"  Update Interval:       {self.update_interval_ms}ms")
        print(f"  Run Duration:          {duration_minutes:.1f} minutes")
        print(f"  Dry Run Mode:          {self.dry_run}")
        if self.symbols:
            print(f"  Monitored Symbols:     {', '.join(self.symbols)}")
        else:
            print(f"  Monitored Symbols:     ALL")
        print()

        # Create cancellation event if not provided
        if cancellation_event is None:
            cancellation_event = asyncio.Event()

        self.is_running = True
        start_time = time.time()
        duration_seconds = duration_minutes * 60

        try:
            # Step 1: Initialize with spinner
            with Spinner(description="Initializing") as spinner:
                await self._initialize_positions()
                spinner.update()

            if not self.trailing_positions:
                print_warning("No open positions found - waiting for positions to open...")
                print("  Tip: Open a position in MT5 terminal to see trailing stop in action")
                print()

            # Step 2: Main loop - stream position profits with timer
            print_info("Starting real-time position monitoring...")
            print(f"  Will run for {duration_minutes:.1f} minutes")
            print("  Press Ctrl+C to stop early")
            print()
            print("  [STREAMING] Waiting for position profit updates...")
            print(f"  [CONFIG] Update interval: {self.update_interval_ms}ms")
            print(f"  [CONFIG] Trailing distance: {self.trail_distance_pips:.0f} pips")
            print(f"  [CONFIG] Activation profit: {self.activation_profit_pips:.0f} pips")
            print()

            # Create progress bar for monitoring
            progress_bar = TimeProgressBar(
                total_seconds=duration_seconds,
                message="Monitoring positions"
            )

            self.last_status_time = start_time
            last_detail_print = start_time

            print("[DEBUG] Entering stream loop...")
            update_received = False

            async for update in self.service.stream_position_profits(
                interval_ms=self.update_interval_ms,
                ignore_empty=False,  # Changed to False to see all updates
                cancellation_event=cancellation_event
            ):
                if not update_received:
                    print("[DEBUG] First update received!")
                    update_received = True
                # Check if should stop
                current_time = time.time()
                elapsed = current_time - start_time
                if elapsed >= duration_seconds or cancellation_event.is_set():
                    progress_bar.finish()
                    print_info(f"Duration reached ({elapsed:.1f}s) - stopping...")
                    break

                # Process update
                await self._process_profit_update(update)
                self.update_count += 1

                # Update progress bar every 1 second
                if current_time - self.last_status_time >= 1.0:
                    self.last_status_time = current_time
                    progress_bar.update(elapsed)

                    # Print simplified status every 30 seconds (inline, without closing progress bar)
                    if current_time - last_detail_print >= 30.0:
                        last_detail_print = current_time
                        positions_count = len(self.trailing_positions)
                        trailing_count = sum(1 for s in self.trailing_positions.values() if s.trailing_active)
                        print(f"\n  [STATUS] Stream updates: {self.update_count} | "
                              f"Positions tracked: {positions_count} | "
                              f"Trailing active: {trailing_count} | "
                              f"SL modifications: {self.total_modifications} | "
                              f"Auto-closed: {self.auto_closed_count}")
                        # Show detailed breakdown only if positions exist
                        if positions_count > 0:
                            print("  [DETAIL] Position breakdown:")
                            for ticket, state in self.trailing_positions.items():
                                profit_pips = state.profit_pips

                                if state.trailing_active:
                                    status = f"TRAILING (SL active)"
                                else:
                                    # Calculate time until auto-close
                                    position_age = (datetime.now() - state.position_opened_at).total_seconds() / 60.0
                                    time_left = self.max_wait_minutes - position_age
                                    pips_needed = self.activation_profit_pips - profit_pips

                                    if time_left > 0:
                                        status = f"WAITING (need {pips_needed:+.1f}p more, closes in {time_left:.1f}m)"
                                    else:
                                        status = f"WAITING (ready to close)"

                                print(f"    #{ticket}: {state.symbol} {profit_pips:+.1f}p | {status}")

        except asyncio.CancelledError:
            print()
            print_info("Orchestrator stopped by user")
        except Exception as e:
            print()
            print_if_error(e, "Orchestrator error")
        finally:
            # Graceful shutdown
            self.is_running = False
            cancellation_event.set()
            await asyncio.sleep(0.5)  # Give streams time to close

            # Print final detailed status
            try:
                elapsed = time.time() - start_time
                await self._print_detailed_status(elapsed, duration_seconds)
            except Exception:
                pass  # Ignore errors in final status

            # Print summary of closed positions if any
            if self.closed_positions_summary:
                print("\n" + "=" * 80)
                print("AUTO-CLOSED POSITIONS SUMMARY")
                print("=" * 80)

                total_pips = 0.0
                total_dollars = 0.0

                for pos in self.closed_positions_summary:
                    print(f"  #{pos['ticket']} {pos['symbol']} {pos['direction']}: "
                          f"{pos['profit_pips']:+.1f}p (${pos['profit_dollars']:+.2f})")
                    total_pips += pos['profit_pips']
                    total_dollars += pos['profit_dollars']

                print("  " + "-" * 76)
                profit_indicator = "✓" if total_dollars >= 0 else "✗"
                print(f"  {profit_indicator} TOTAL: {total_pips:+.1f}p (${total_dollars:+.2f}) "
                      f"| {len(self.closed_positions_summary)} position(s) closed")
                print()

            print("\n" + "=" * 80)
            print("TRAILING STOP ORCHESTRATOR - STOPPED")
            print("=" * 80)
            print(f"  Total Runtime:          {time.time() - start_time:.1f}s")
            print(f"  Total Updates:          {self.update_count}")
            print(f"  SL Modifications:       {self.total_modifications}")
            print(f"  Auto-Closed Positions:  {self.auto_closed_count}")
            print(f"  Positions Still Open:   {len(self.trailing_positions)}")
            active_count = sum(1 for s in self.trailing_positions.values() if s.trailing_active)
            print(f"  Trailing Active:        {active_count}")
            print()

    async def _initialize_positions(self):
        """Load and initialize tracking for current open positions."""
        print_step(1, "Loading open positions")

        try:
            # Get all open positions
            opened_data = await self.service.get_opened_orders(
                account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
            )

            positions = opened_data.position_infos

            if not positions:
                print("  No open positions found")
                return

            print(f"  Found {len(positions)} open position(s)")

            for pos in positions:
                # Filter by managed_tickets if specified
                if self.managed_tickets is not None and pos.ticket not in self.managed_tickets:
                    continue  # Skip positions not managed by this orchestrator

                # Filter by symbols if specified
                if self.symbols and pos.symbol not in self.symbols:
                    continue

                # Get symbol info for point size
                tick = await self.service.get_symbol_tick(pos.symbol)

                # Initialize tracking state
                is_buy = (pos.type == 0)  # 0=BUY, 1=SELL
                now = datetime.now()

                self.trailing_positions[pos.ticket] = TrailingState(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    is_buy=is_buy,
                    open_price=pos.price_open,
                    current_sl=pos.stop_loss,
                    highest_price=tick.bid if is_buy else tick.ask,
                    lowest_price=tick.bid if is_buy else tick.ask,
                    trailing_active=False,
                    last_update=now,
                    position_opened_at=now,  # Assume position was just opened
                    profit_pips=0.0,
                    profit_dollars=pos.profit
                )

                direction = "BUY" if is_buy else "SELL"
                print(f"    - Position #{pos.ticket}: {pos.symbol} {direction} "
                      f"Vol={pos.volume:.2f} Entry={pos.price_open:.5f} "
                      f"SL={pos.stop_loss:.5f} Profit={pos.profit:.2f}")

            managed_count = len(self.trailing_positions)
            if managed_count == 0:
                print(f"  No managed positions found (managed_tickets filter applied)")
            else:
                print(f"  Managing {managed_count} position(s)")
            print()

        except Exception as e:
            print_if_error(e, "Failed to initialize positions")

    async def _print_detailed_status(self, elapsed: float, duration_seconds: float):
        """
        Print compact status with information about each position.

        Args:
            elapsed: Elapsed time in seconds
            duration_seconds: Total duration in seconds
        """
        active_count = sum(1 for s in self.trailing_positions.values() if s.trailing_active)

        print()
        print(f"  -- Status Update [{elapsed:.0f}s] --")
        print(f"     Updates: {self.update_count} | Positions: {len(self.trailing_positions)} | "
              f"Trailing: {active_count} | Modifications: {self.total_modifications}")

        if not self.trailing_positions:
            print(f"     No positions tracked")
            return

        for ticket, state in self.trailing_positions.items():
            # Get current market price and calculate profit
            try:
                tick = await self.service.get_symbol_tick(state.symbol)
                current_price = tick.bid if state.is_buy else tick.ask

                # Get symbol info for pip calculation
                symbol_info = await self.sugar.get_symbol_info(state.symbol)
                point = symbol_info.point
                pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point

                # Calculate profit in pips
                if state.is_buy:
                    profit_pips = (current_price - state.open_price) / pip
                else:
                    profit_pips = (state.open_price - current_price) / pip

                # Direction and status
                direction = "BUY " if state.is_buy else "SELL"
                status = "TRAILING" if state.trailing_active else "WAITING "

                # Build compact line
                info = f"     [{status}] #{ticket} {state.symbol} {direction} | "
                info += f"Entry: {state.open_price:.5f} | Price: {current_price:.5f} | "
                info += f"SL: {state.current_sl:.5f} | Profit: {profit_pips:+.1f}p"

                # Add specific info based on state
                if not state.trailing_active:
                    distance = self.activation_profit_pips - profit_pips
                    if distance > 0:
                        info += f" (need {distance:.1f}p more)"
                else:
                    # Calculate trail distance only if SL is set
                    if state.current_sl > 0:
                        if state.is_buy:
                            sl_distance_pips = (current_price - state.current_sl) / pip
                        else:
                            sl_distance_pips = (state.current_sl - current_price) / pip
                        info += f" (trail: {sl_distance_pips:.1f}p)"
                    else:
                        info += f" (setting SL...)"

                print(info)

            except Exception as e:
                print(f"     [ERROR] #{ticket} {state.symbol} - {str(e)[:50]}")

    async def _process_profit_update(self, update):
        """
        Process position profit update and apply trailing logic.

        Args:
            update: PositionProfitData from stream
        """
        for pos in update.updated_positions:
            # Skip if we have a managed_tickets list and this ticket is not in it
            if self.managed_tickets is not None and pos.ticket not in self.managed_tickets:
                continue  # Ignore positions not managed by this orchestrator

            # Check if we're tracking this position
            if pos.ticket not in self.trailing_positions:
                # New position appeared - add it
                tick = await self.service.get_symbol_tick(pos.symbol)
                is_buy = (pos.type == 0)

                now = datetime.now()
                self.trailing_positions[pos.ticket] = TrailingState(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    is_buy=is_buy,
                    open_price=pos.price_open,
                    current_sl=pos.stop_loss,
                    highest_price=tick.bid if is_buy else tick.ask,
                    lowest_price=tick.bid if is_buy else tick.ask,
                    trailing_active=False,
                    last_update=now,
                    position_opened_at=now,
                    profit_pips=0.0,
                    profit_dollars=pos.profit
                )
                print_success(f"New managed position: #{pos.ticket} {pos.symbol}")

            state = self.trailing_positions[pos.ticket]

            # Get current market price
            tick = await self.service.get_symbol_tick(state.symbol)
            current_price = tick.bid if state.is_buy else tick.ask

            # Calculate profit in pips
            symbol_info = await self.sugar.get_symbol_info(state.symbol)
            point = symbol_info.point
            pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point

            if state.is_buy:
                profit_pips = (current_price - state.open_price) / pip
            else:
                profit_pips = (state.open_price - current_price) / pip

            state.profit_pips = profit_pips
            state.profit_dollars = pos.profit  # Update profit in dollars from stream

            # === AUTO-CLOSE CONDITIONS ===
            # Condition 1: Max loss exceeded
            if profit_pips < -self.max_loss_pips:
                await self._auto_close_position(
                    state,
                    f"Loss exceeded {self.max_loss_pips:.0f} pips (current: {profit_pips:.1f}p)"
                )
                return  # Position closed, skip further processing

            # Condition 2: Max wait time exceeded without activation
            if not state.trailing_active:
                position_age = (datetime.now() - state.position_opened_at).total_seconds() / 60.0
                if position_age >= self.max_wait_minutes:
                    await self._auto_close_position(
                        state,
                        f"No activation after {self.max_wait_minutes:.1f} min (profit: {profit_pips:.1f}p)"
                    )
                    return  # Position closed, skip further processing

            # Update price extremes
            if state.is_buy:
                state.highest_price = max(state.highest_price, current_price)
            else:
                state.lowest_price = min(state.lowest_price, current_price)

            # Check if trailing should be activated
            if await self._should_activate_trailing(state, pos, current_price):
                if not state.trailing_active:
                    state.trailing_active = True
                    print(f"  <!> Trailing activated for #{pos.ticket} {pos.symbol} "
                          f"(profit: {pos.profit:.2f})")

                # Calculate and apply new SL
                await self._apply_trailing_stop(state, current_price)

            state.last_update = datetime.now()

    async def _should_activate_trailing(self, state: TrailingState, pos, current_price: float) -> bool:
        """
        Check if trailing should be activated for position.

        Args:
            state: Position state
            pos: Position data from stream
            current_price: Current market price

        Returns:
            True if trailing should activate
        """
        # Already active
        if state.trailing_active:
            return True

        # Calculate current profit in pips
        symbol_info = await self.sugar.get_symbol_info(state.symbol)
        point = symbol_info.point
        pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point

        if state.is_buy:
            profit_pips = (current_price - state.open_price) / pip
        else:
            profit_pips = (state.open_price - current_price) / pip

        # Activate if profit exceeds threshold
        return profit_pips >= self.activation_profit_pips

    async def _apply_trailing_stop(self, state: TrailingState, current_price: float):
        """
        Calculate and apply new trailing stop level.

        Args:
            state: Position state
            current_price: Current market price
        """
        # Get symbol info for calculations
        symbol_info = await self.sugar.get_symbol_info(state.symbol)
        point = symbol_info.point
        pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point

        # Calculate new SL level
        trail_distance = self.trail_distance_pips * pip

        if state.is_buy:
            # BUY: SL below current price
            new_sl = current_price - trail_distance
            # Only move SL up (never down)
            if new_sl <= state.current_sl:
                return  # Don't move SL down
        else:
            # SELL: SL above current price
            new_sl = current_price + trail_distance
            # Only move SL down (never up)
            if new_sl >= state.current_sl:
                return  # Don't move SL up

        # Round to proper digits
        new_sl = round(new_sl, symbol_info.digits)

        # Check if change is significant enough (at least 1 pip movement)
        sl_change = abs(new_sl - state.current_sl)
        if sl_change < pip:
            return  # Change too small

        # Update SL
        await self._update_stop_loss(state, new_sl, current_price)

    async def _update_stop_loss(self, state: TrailingState, new_sl: float, current_price: float):
        """
        Update stop-loss level for position.

        Args:
            state: Position state
            new_sl: New SL price
            current_price: Current market price
        """
        direction = "BUY" if state.is_buy else "SELL"

        if self.dry_run:
            print(f"  [DRY RUN] Would modify #{state.ticket} {state.symbol} {direction}: "
                  f"SL {state.current_sl:.5f} -> {new_sl:.5f} (price: {current_price:.5f})")
            state.current_sl = new_sl
            self.total_modifications += 1
            return

        try:
            # Build modify request
            modify_req = trading_helper_pb2.OrderModifyRequest(
                ticket=state.ticket,
                symbol=state.symbol,  # Required field
                stop_loss=new_sl
                # Don't change TP - keep existing
            )

            # Execute modification
            result = await self.service.modify_order(modify_req)

            if result.returned_code == 10009:  # TRADE_RETCODE_DONE
                state.current_sl = new_sl
                self.total_modifications += 1
                print(f"  [OK] Modified #{state.ticket} {state.symbol} {direction}: "
                      f"SL -> {new_sl:.5f} (price: {current_price:.5f})")
            else:
                print(f"  [!] Failed to modify #{state.ticket}: code {result.returned_code}")

        except Exception as e:
            print_if_error(e, f"Error modifying #{state.ticket}")

    async def _auto_close_position(self, state: TrailingState, reason: str):
        """
        Auto-close position based on conditions.

        Args:
            state: Position state
            reason: Reason for closing
        """
        direction = "BUY" if state.is_buy else "SELL"

        profit_pips = state.profit_pips
        profit_dollars = state.profit_dollars

        if self.dry_run:
            print(f"  [DRY RUN] Would auto-close #{state.ticket} {state.symbol} {direction}: "
                  f"{profit_pips:+.1f}p (${profit_dollars:+.2f}) | {reason}")
            # Save to summary
            self.closed_positions_summary.append({
                'ticket': state.ticket,
                'symbol': state.symbol,
                'direction': direction,
                'profit_pips': profit_pips,
                'profit_dollars': profit_dollars,
                'reason': 'auto-close'
            })
            # Remove from tracking
            if state.ticket in self.trailing_positions:
                del self.trailing_positions[state.ticket]
            self.auto_closed_count += 1
            return

        try:
            # Close position using sugar API (returns bool)
            success = await self.sugar.close_position(ticket=state.ticket)

            if success:
                self.auto_closed_count += 1
                print(f"  [CLOSED] #{state.ticket} {state.symbol} {direction}: "
                      f"{profit_pips:+.1f}p (${profit_dollars:+.2f}) | {reason}")
                # Save to summary
                self.closed_positions_summary.append({
                    'ticket': state.ticket,
                    'symbol': state.symbol,
                    'direction': direction,
                    'profit_pips': profit_pips,
                    'profit_dollars': profit_dollars,
                    'reason': 'auto-close'
                })
                # Remove from tracking
                if state.ticket in self.trailing_positions:
                    del self.trailing_positions[state.ticket]
            else:
                print(f"  [!] Failed to auto-close #{state.ticket}: {reason}")

        except Exception as e:
            print_if_error(e, f"Error auto-closing #{state.ticket}")

    def get_status(self) -> dict:
        """Get current orchestrator status."""
        return {
            "is_running": self.is_running,
            "positions_tracked": len(self.trailing_positions),
            "trailing_active": sum(1 for s in self.trailing_positions.values() if s.trailing_active),
            "total_modifications": self.total_modifications,
            "update_count": self.update_count,
        }


async def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print("TRAILING STOP ORCHESTRATOR DEMO")
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
        sugar = MT5Sugar(service, default_symbol=config['test_symbol'])
        print_success("Connected successfully!")
        print()
    except Exception as e:
        fatal(e, "Failed to connect")

    # Create cancellation event
    cancellation_event = asyncio.Event()

    try:
        # Open test positions automatically
        print_step(1, "Opening test positions")
        test_symbol = config['test_symbol']
        test_positions = []

        try:
            # Open BUY position
            print(f"  Opening BUY position on {test_symbol}...")
            buy_ticket = await sugar.buy_market(
                symbol=test_symbol,
                volume=0.01,
                comment="TrailingStop Test BUY"
            )
            test_positions.append(buy_ticket)
            print_success(f"  BUY position opened: #{buy_ticket}")

            # Open SELL position
            print(f"  Opening SELL position on {test_symbol}...")
            sell_ticket = await sugar.sell_market(
                symbol=test_symbol,
                volume=0.01,
                comment="TrailingStop Test SELL"
            )
            test_positions.append(sell_ticket)
            print_success(f"  SELL position opened: #{sell_ticket}")

            print(f"  Total test positions opened: {len(test_positions)}")
            print()

        except Exception as e:
            print_warning(f"Could not open test positions: {e}")
            print("  Orchestrator will monitor any existing positions")
            print()

        # Create orchestrator with configuration
        print_step(2, "Starting orchestrator")
        orchestrator = TrailingStopOrchestrator(
            service=service,
            sugar=sugar,
            trail_distance_pips=20.0,      # 20 pips trailing distance
            activation_profit_pips=30.0,   # Activate after 30 pips profit
            update_interval_ms=1000,       # Check every second
            symbols=None,                  # Monitor all symbols
            dry_run=False,                 # Set True for testing without real modifications
            max_wait_minutes=2.0,          # Auto-close if not activated after 2 minutes
            max_loss_pips=50.0,            # Auto-close if loss exceeds 50 pips
            managed_tickets=test_positions  # Only manage positions we opened
        )

        # Run orchestrator for 3 minutes
        await orchestrator.start(
            duration_minutes=3.0,
            cancellation_event=cancellation_event
        )

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user - shutting down gracefully...")
        cancellation_event.set()
        await asyncio.sleep(0.5)  # Wait for streams to close

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
    print("   - Real-time position monitoring via streaming")
    print("   - Automatic SL adjustment based on profit")
    print("   - Protection against unfavorable SL movements")
    print("   - Graceful handling of new/closed positions")
    print("   - Timed execution with live progress")
    print("   - Dry-run mode for safe testing")
    print()


if __name__ == "__main__":
    asyncio.run(main())
