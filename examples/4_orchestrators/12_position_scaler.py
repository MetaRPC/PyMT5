"""
==============================================================================
 FILE: 12_position_scaler.py - POSITION SCALER ORCHESTRATOR

 ⚠️  DEMONSTRATION ONLY - NOT PRODUCTION READY
     This orchestrator demonstrates position scaling strategy and API usage.
     Production deployment requires: risk management, error handling, proper position
     sizing, slippage control, logging, monitoring, and extensive testing.

 PURPOSE:
   Automated position scaling (pyramiding or averaging) orchestrator.
   Adds volume to existing positions at predefined profit/loss levels.

 HOW IT WORKS:
   1. Monitors base position via stream_position_profits()
   2. When position reaches scale level (profit or loss), adds volume
   3. Tracks total volume and ensures risk limits are respected
   4. Can work in two modes: PYRAMIDING or AVERAGING
   5. Shows live progress bar with time tracking and detailed status updates

 TWO SCALING MODES:

   PYRAMIDING (Trend Following):
   - Adds to PROFITABLE positions
   - Levels: +30, +60, +90 pips profit
   - Logic: "Trend is working -> increase exposure"
   - Lower risk, requires strong trend

   AVERAGING (Mean Reversion):
   - Adds to LOSING positions
   - Levels: -30, -60, -90 pips loss
   - Logic: "Price will reverse -> average entry"
   - Higher risk, requires strict limits

 EXAMPLE SCENARIO (PYRAMIDING):
   BUY EURUSD at 1.2000, volume 0.10:
   - Scale Levels: +30, +60, +90 pips
   - Scale Volume: 50% of base = 0.05 lots
   - Max Total: 0.30 lots

   Price reaches 1.2030 (+30 pips):
   -> Add 0.05 lots at 1.2030
   -> Total: 0.15 lots

   Price reaches 1.2060 (+60 pips):
   -> Add 0.05 lots at 1.2060
   -> Total: 0.20 lots

   Price reaches 1.2090 (+90 pips):
   -> Add 0.05 lots at 1.2090
   -> Total: 0.25 lots

 CONFIGURATION PARAMETERS:
   - scale_type: "pyramiding" or "averaging"
   - scale_levels: List of levels in pips [30, 60, 90]
   - scale_volume_percent: % of base volume to add (default: 50%)
   - max_total_volume: Maximum total volume (default: 0.50 lots)
   - update_interval_ms: Check interval (default: 1000ms)
   - dry_run: If True, simulates trades without execution (default: False)

 API METHODS USED:
   From MT5Service:
   - stream_position_profits() - Real-time P&L monitoring (CORE METHOD)
   - get_opened_orders()       - Get current positions and orders
   - get_symbol_tick()         - Current market prices
   - get_account_summary()     - Account balance and equity info

   From MT5Sugar:
   - buy_market() / sell_market() - Add volume to positions
   - calculate_required_margin()  - Check required margin before scaling
   - get_account_info()           - Account balance and free margin
   - get_symbol_info()            - Symbol specifications (digits, point)
   - close_position()             - Close positions in cleanup

 IMPORTANT NOTES:
   - PYRAMIDING: Lower risk, requires trend
   - AVERAGING: High risk, use with caution
   - Always respects max_total_volume limit
   - Checks available margin before adding
   - Each scale level triggered only once
   - Demo automatically opens 2 test positions (0.01 lots each)
   - Uses first position as base, second as backup
   - Auto-switches to second position if first closes
   - Closes ONLY test positions (not other account positions)

 HOW TO RUN:
   cd examples
   python main.py scaler    (or select [12] from menu)

   The demo will:
   1. Connect to MT5
   2. Auto-detect scaling mode (always PYRAMIDING for safety)
   3. Open 2 small test positions automatically (first = base)
   4. Monitor and scale the base position for 3 minutes
   5. Auto-switch to second position if first closes
   6. Close ONLY test positions at the end (leaves other positions alone)

==============================================================================
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
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
from progress_bar import Spinner, TimeProgressBar

# Import APIs
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar

# Import protobuf types
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2


class ScaleType(Enum):
    """Scaling strategy type."""
    PYRAMIDING = "pyramiding"  # Add to profitable positions
    AVERAGING = "averaging"    # Add to losing positions


@dataclass
class ScaleLevel:
    """Definition of a scale level."""
    pips: float           # Level in pips from entry
    triggered: bool       # Has this level been triggered
    ticket: Optional[int] # Ticket of order placed at this level


@dataclass
class ScalerState:
    """State tracker for position being scaled."""
    base_ticket: int
    symbol: str
    is_buy: bool
    entry_price: float
    base_volume: float
    current_total_volume: float
    scale_levels: List[ScaleLevel]
    last_update: datetime


class PositionScalerOrchestrator:
    """
    Automated position scaler orchestrator.
    Adds volume to positions at predefined levels.
    """

    def __init__(
        self,
        service: MT5Service,
        sugar: MT5Sugar,
        scale_type: ScaleType = ScaleType.PYRAMIDING,
        scale_levels_pips: List[float] = None,
        scale_volume_percent: float = 50.0,
        max_total_volume: float = 0.50,
        update_interval_ms: int = 1000,
        dry_run: bool = False
    ):
        """
        Initialize position scaler orchestrator.

        Args:
            service: MT5Service instance
            sugar: MT5Sugar instance
            scale_type: PYRAMIDING or AVERAGING
            scale_levels_pips: Levels in pips [30, 60, 90]
            scale_volume_percent: % of base volume to add each level
            max_total_volume: Maximum total volume
            update_interval_ms: Update interval in milliseconds
            dry_run: If True, only simulate without real trades
        """
        self.service = service
        self.sugar = sugar
        self.scale_type = scale_type
        self.scale_levels_pips = scale_levels_pips or [30.0, 60.0, 90.0]
        self.scale_volume_percent = scale_volume_percent
        self.max_total_volume = max_total_volume
        self.update_interval_ms = update_interval_ms
        self.dry_run = dry_run

        # State tracking
        self.scaler_state: Optional[ScalerState] = None
        self.is_running = False
        self.total_scales = 0
        self.update_count = 0
        self.last_status_time = 0.0

    async def start(
        self,
        symbol: str,
        base_ticket: Optional[int] = None,
        duration_minutes: float = 3.0,
        cancellation_event: Optional[asyncio.Event] = None
    ):
        """
        Start the position scaler orchestrator.

        Args:
            symbol: Symbol to monitor
            base_ticket: Specific ticket to scale (None = find automatically)
            duration_minutes: How long to run in minutes (default: 3.0)
            cancellation_event: Event to signal shutdown
        """
        print("\n" + "=" * 80)
        print("POSITION SCALER ORCHESTRATOR - STARTING")
        print("=" * 80)
        print(f"  Scale Type:            {self.scale_type.value.upper()}")
        print(f"  Scale Levels:          {self.scale_levels_pips} pips")
        print(f"  Scale Volume:          {self.scale_volume_percent}% of base")
        print(f"  Max Total Volume:      {self.max_total_volume} lots")
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
            # Step 1: Find base position with spinner
            with Spinner(description="Initializing") as spinner:
                await self._initialize_base_position(symbol, base_ticket)
                spinner.update()

            if not self.scaler_state:
                print_warning(f"No base position found for {symbol}")
                print(f"  Tip: Open a position on {symbol} to start scaling")
                return

            # Step 2: Main loop - monitor and scale with timer
            print_info("Starting position monitoring...")
            print(f"  Will run for {duration_minutes:.1f} minutes")
            print("  Press Ctrl+C to stop early\n")

            # Create progress bar for monitoring
            progress_bar = TimeProgressBar(
                total_seconds=duration_seconds,
                message="Monitoring positions"
            )

            self.last_status_time = start_time
            last_detail_print = start_time

            async for update in self.service.stream_position_profits(
                interval_ms=self.update_interval_ms,
                ignore_empty=True,
                cancellation_event=cancellation_event
            ):
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

                    # Print detailed status every 30 seconds
                    if current_time - last_detail_print >= 30.0:
                        last_detail_print = current_time
                        progress_bar.finish()
                        await self._print_detailed_status(elapsed, duration_seconds)
                        # Recreate progress bar
                        progress_bar = TimeProgressBar(
                            total_seconds=duration_seconds,
                            message="Monitoring positions"
                        )

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

            print("\n" + "=" * 80)
            print("POSITION SCALER ORCHESTRATOR - STOPPED")
            print("=" * 80)
            print(f"  Total Runtime:          {time.time() - start_time:.1f}s")
            print(f"  Total Updates:          {self.update_count}")
            print(f"  Scale Orders:           {self.total_scales}")
            if self.scaler_state:
                print(f"  Final Total Volume:     {self.scaler_state.current_total_volume:.2f} lots")
                triggered = sum(1 for l in self.scaler_state.scale_levels if l.triggered)
                print(f"  Levels Triggered:       {triggered}/{len(self.scaler_state.scale_levels)}")
            print()

    async def _print_detailed_status(self, elapsed: float, duration_seconds: float):
        """
        Print compact status with information about scaling progress.

        Args:
            elapsed: Elapsed time in seconds
            duration_seconds: Total duration in seconds
        """
        if not self.scaler_state:
            print()
            print(f"  -- Status Update [{elapsed:.0f}s] --")
            print(f"     No position being tracked")
            return

        triggered = sum(1 for l in self.scaler_state.scale_levels if l.triggered)

        print()
        print(f"  -- Status Update [{elapsed:.0f}s] --")
        print(f"     Updates: {self.update_count} | Levels: {triggered}/{len(self.scaler_state.scale_levels)} | "
              f"Scales: {self.total_scales} | Volume: {self.scaler_state.current_total_volume:.2f}/{self.max_total_volume}")

        try:
            # Get current market price
            tick = await self.service.get_symbol_tick(self.scaler_state.symbol)
            current_price = tick.bid if self.scaler_state.is_buy else tick.ask

            # Calculate profit in pips
            profit_pips = await self._calculate_profit_pips(current_price)

            # Direction and status
            direction = "BUY " if self.scaler_state.is_buy else "SELL"

            # Build status line
            info = f"     Base Position #{self.scaler_state.base_ticket}: {self.scaler_state.symbol} {direction} | "
            info += f"Entry: {self.scaler_state.entry_price:.5f} | Price: {current_price:.5f} | "
            info += f"Profit: {profit_pips:+.1f}p"
            print(info)

            # Show scale levels status
            print(f"     Scale Levels:")
            for i, level in enumerate(self.scaler_state.scale_levels, 1):
                scale_volume = self.scaler_state.base_volume * (self.scale_volume_percent / 100.0)
                sign = "+" if self.scale_type == ScaleType.PYRAMIDING else "-"

                if level.triggered:
                    status = "✓ DONE"
                    print(f"       [{status}] Level {i}: {sign}{level.pips:.0f}p -> Added {scale_volume:.2f} lots (Ticket #{level.ticket})")
                else:
                    # Calculate distance to trigger
                    if self.scale_type == ScaleType.PYRAMIDING:
                        distance = level.pips - profit_pips
                        if distance > 0:
                            status = f"WAITING (need {distance:+.1f}p more)"
                        else:
                            status = "READY"
                    else:  # AVERAGING
                        distance = -level.pips - profit_pips
                        if distance < 0:
                            status = f"WAITING (need {-distance:.1f}p more loss)"
                        else:
                            status = "READY"

                    print(f"       [ WAIT ] Level {i}: {sign}{level.pips:.0f}p -> {status}")

        except Exception as e:
            print(f"     [ERROR] Failed to get status: {str(e)[:50]}")

    async def _initialize_base_position(self, symbol: str, ticket: Optional[int]):
        """Find and initialize base position for scaling."""
        print_step(1, f"Finding base position for {symbol}")

        try:
            # Get all positions for symbol
            opened_data = await self.service.get_opened_orders(
                account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
            )

            # Filter by symbol
            positions = [p for p in opened_data.position_infos if p.symbol == symbol]

            if not positions:
                print(f"  No positions found for {symbol}")
                return

            # Find base position
            if ticket:
                base_pos = next((p for p in positions if p.ticket == ticket), None)
                if not base_pos:
                    print(f"  Position #{ticket} not found")
                    return
            else:
                # Use oldest position as base
                base_pos = positions[0]

            # Initialize scaler state
            is_buy = (base_pos.type == 0)
            direction = "BUY" if is_buy else "SELL"

            # Create scale levels
            scale_levels = [
                ScaleLevel(pips=level, triggered=False, ticket=None)
                for level in self.scale_levels_pips
            ]

            self.scaler_state = ScalerState(
                base_ticket=base_pos.ticket,
                symbol=base_pos.symbol,
                is_buy=is_buy,
                entry_price=base_pos.price_open,
                base_volume=base_pos.volume,
                current_total_volume=base_pos.volume,
                scale_levels=scale_levels,
                last_update=datetime.now()
            )

            print_success(f"Base position initialized")
            print(f"    - Position #{base_pos.ticket}: {base_pos.symbol} {direction}")
            print(f"      Volume:      {base_pos.volume:.2f} lots")
            print(f"      Entry:       {base_pos.price_open:.5f}")
            print(f"      SL:          {base_pos.stop_loss:.5f}")
            print(f"      TP:          {base_pos.take_profit:.5f}")
            print(f"      Profit:      {base_pos.profit:.2f}")
            print()

            # Show scale plan
            print_info("Scale Plan:")
            for i, level in enumerate(self.scaler_state.scale_levels, 1):
                scale_volume = self.scaler_state.base_volume * (self.scale_volume_percent / 100.0)
                target_price = self._calculate_target_price(level.pips)

                sign = "+" if self.scale_type == ScaleType.PYRAMIDING else "-"
                print(f"    Level {i}: {sign}{level.pips:.0f} pips "
                      f"(price ~{target_price:.5f}) -> Add {scale_volume:.2f} lots")
            print()

        except Exception as e:
            print_if_error(e, "Failed to initialize base position")

    async def _process_profit_update(self, update):
        """Process position profit update and check for scale triggers."""
        if not self.scaler_state:
            return

        # Find our base position in update
        base_pos = next(
            (p for p in update.updated_positions if p.ticket == self.scaler_state.base_ticket),
            None
        )

        if not base_pos:
            # Base position closed - try to find another position of same symbol
            closed_ticket = self.scaler_state.base_ticket
            closed_symbol = self.scaler_state.symbol
            print_warning(f"Base position #{closed_ticket} closed")

            # Try to switch to another position with same symbol
            found_replacement = False
            for p in update.updated_positions:
                if p.symbol == closed_symbol and p.ticket != closed_ticket:
                    print_info(f"Switching to position #{p.ticket} as new base")
                    # Re-initialize with new base position
                    try:
                        tick = await self.service.get_symbol_tick(p.symbol)
                        is_buy = (p.type == 0)

                        self.scaler_state = ScalerState(
                            base_ticket=p.ticket,
                            symbol=p.symbol,
                            is_buy=is_buy,
                            entry_price=p.price_open,
                            base_volume=p.volume,
                            current_total_volume=p.volume,
                            scale_levels=[
                                ScaleLevel(pips=level, triggered=False, ticket=None)
                                for level in self.scale_levels_pips
                            ],
                            last_update=datetime.now()
                        )
                        found_replacement = True
                        break  # Exit loop after finding replacement
                    except Exception as e:
                        print_if_error(e, f"Failed to switch to position #{p.ticket}")
                        continue

            if found_replacement:
                return  # Continue monitoring new base
            else:
                # No alternative position found
                print_warning("No alternative position found - stopping monitoring")
                self.scaler_state = None
                return

        # Get current price
        tick = await self.service.get_symbol_tick(self.scaler_state.symbol)
        current_price = tick.bid if self.scaler_state.is_buy else tick.ask

        # Calculate current profit in pips
        profit_pips = await self._calculate_profit_pips(current_price)

        # Check each scale level
        for level in self.scaler_state.scale_levels:
            if level.triggered:
                continue  # Already triggered

            should_trigger = False

            if self.scale_type == ScaleType.PYRAMIDING:
                # Trigger on profit levels
                should_trigger = profit_pips >= level.pips
            else:  # AVERAGING
                # Trigger on loss levels
                should_trigger = profit_pips <= -level.pips

            if should_trigger:
                await self._trigger_scale_level(level, current_price)

        self.scaler_state.last_update = datetime.now()

    async def _trigger_scale_level(self, level: ScaleLevel, current_price: float):
        """Trigger a scale level - add volume."""
        if not self.scaler_state:
            return

        # Calculate scale volume
        scale_volume = self.scaler_state.base_volume * (self.scale_volume_percent / 100.0)

        # Check if would exceed max total volume
        new_total = self.scaler_state.current_total_volume + scale_volume
        if new_total > self.max_total_volume:
            remaining = self.max_total_volume - self.scaler_state.current_total_volume
            if remaining <= 0:
                print_warning(f"Max volume {self.max_total_volume} reached - skipping level")
                level.triggered = True
                return

            scale_volume = remaining
            print_warning(f"Adjusting volume to {scale_volume:.2f} to respect max limit")

        # Check available margin
        try:
            required_margin = await self.sugar.calculate_required_margin(
                self.scaler_state.symbol,
                scale_volume
            )
            account_info = await self.sugar.get_account_info()

            if required_margin > account_info.free_margin:
                print_warning(f"Insufficient margin: need {required_margin:.2f}, "
                            f"have {account_info.free_margin:.2f}")
                level.triggered = True
                return
        except Exception as e:
            print_if_error(e, "Failed to check margin")
            return

        # Execute scale order
        direction = "BUY" if self.scaler_state.is_buy else "SELL"
        sign = "+" if self.scale_type == ScaleType.PYRAMIDING else "-"

        print(f"\n  <!> SCALE TRIGGERED: {sign}{level.pips:.0f} pips "
              f"(price: {current_price:.5f})")
        print(f"     Adding {scale_volume:.2f} lots to {direction} position")

        if self.dry_run:
            print(f"  [DRY RUN] Would open {direction} {self.scaler_state.symbol} "
                  f"{scale_volume:.2f} lots at {current_price:.5f}")
            level.triggered = True
            level.ticket = 999999  # Dummy ticket
            self.scaler_state.current_total_volume += scale_volume
            self.total_scales += 1
            print_success(f"Scale order simulated (Total volume: "
                        f"{self.scaler_state.current_total_volume:.2f} lots)")
            return

        try:
            # Place order
            if self.scaler_state.is_buy:
                ticket = await self.sugar.buy_market(
                    self.scaler_state.symbol,
                    scale_volume
                )
            else:
                ticket = await self.sugar.sell_market(
                    self.scaler_state.symbol,
                    scale_volume
                )

            if ticket > 0:
                level.triggered = True
                level.ticket = ticket
                self.scaler_state.current_total_volume += scale_volume
                self.total_scales += 1

                print_success(f"Scale order placed: Ticket #{ticket}")
                print(f"     Total volume now: {self.scaler_state.current_total_volume:.2f} lots")
            else:
                print_warning(f"Failed to place scale order (ticket={ticket})")

        except Exception as e:
            print_if_error(e, "Failed to place scale order")

    async def _calculate_profit_pips(self, current_price: float) -> float:
        """Calculate current profit in pips."""
        if not self.scaler_state:
            return 0.0

        symbol_info = await self.sugar.get_symbol_info(self.scaler_state.symbol)
        point = symbol_info.point
        pip = point * 10 if symbol_info.digits == 5 or symbol_info.digits == 3 else point

        if self.scaler_state.is_buy:
            return (current_price - self.scaler_state.entry_price) / pip
        else:
            return (self.scaler_state.entry_price - current_price) / pip

    def _calculate_target_price(self, pips: float) -> float:
        """Calculate target price for given pips."""
        if not self.scaler_state:
            return 0.0

        # Note: This is approximate - actual calculation needs symbol info
        pip_value = 0.0001 if self.scaler_state.symbol.startswith("JPY") else 0.00001

        if self.scale_type == ScaleType.PYRAMIDING:
            # Profit direction
            if self.scaler_state.is_buy:
                return self.scaler_state.entry_price + (pips * pip_value)
            else:
                return self.scaler_state.entry_price - (pips * pip_value)
        else:
            # Loss direction
            if self.scaler_state.is_buy:
                return self.scaler_state.entry_price - (pips * pip_value)
            else:
                return self.scaler_state.entry_price + (pips * pip_value)


async def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print("POSITION SCALER ORCHESTRATOR DEMO")
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

    # Initialize test positions list (needed for finally block)
    test_positions = []
    base_ticket = None

    try:
        # Auto-detect scale type based on account balance and risk tolerance
        print("[AUTO-DETECT] Analyzing account risk profile...")

        try:
            account_info = await service.get_account_summary()
            balance = account_info.balance
            equity = account_info.equity

            # Decision logic:
            # - High account health (equity >= 90% of balance) → PYRAMIDING (safer)
            # - Low account health (equity < 90% of balance) → PYRAMIDING (avoid more risk)
            # - Default: Always PYRAMIDING (safer option)

            equity_ratio = (equity / balance) * 100 if balance > 0 else 100

            if equity_ratio >= 90:
                scale_type = ScaleType.PYRAMIDING
                print_info(f"Account Health: {equity_ratio:.1f}% → Using PYRAMIDING (add to winners)")
            else:
                scale_type = ScaleType.PYRAMIDING  # Still safer even when losing
                print_info(f"Account Health: {equity_ratio:.1f}% → Using PYRAMIDING (safer approach)")

        except Exception as e:
            # Fallback to safe default
            print_warning(f"Account analysis failed: {e}")
            scale_type = ScaleType.PYRAMIDING
            print_info("Defaulting to PYRAMIDING mode (safer)")

        print()

        # Open 2 test positions for demonstration
        # NOTE: This is for demo purposes - in production, positions should already exist
        print_info("Opening test positions for demonstration...")
        print("  This demo will open 2 small positions to showcase the scaler\n")

        try:
            # Open first position (base position)
            print("  Opening position #1 (base)...")
            ticket1 = await sugar.buy_market(test_symbol, 0.01)
            if ticket1 > 0:
                test_positions.append(ticket1)
                base_ticket = ticket1  # Use first position as base
                print_success(f"    Position #1 opened: Ticket #{ticket1} (0.01 lots)")
            else:
                print_warning(f"    Failed to open position #1")

            # Small delay to ensure positions are registered
            await asyncio.sleep(0.5)

            # Open second position (will also be tracked)
            print("  Opening position #2 (additional)...")
            ticket2 = await sugar.buy_market(test_symbol, 0.01)
            if ticket2 > 0:
                test_positions.append(ticket2)
                print_success(f"    Position #2 opened: Ticket #{ticket2} (0.01 lots)")
            else:
                print_warning(f"    Failed to open position #2")

            print()
            if test_positions:
                print_info("Test positions opened successfully!")
                print(f"  Base position for scaling: #{base_ticket}")
                print(f"  Total positions opened: {len(test_positions)}\n")
            else:
                print_warning("No test positions were opened!")
                print()

            # Wait a moment for positions to settle
            await asyncio.sleep(1.0)

        except Exception as e:
            print_if_error(e, "Failed to open test positions")
            print_warning("Continuing without test positions - make sure you have positions open!")
            print()

        # Create orchestrator
        orchestrator = PositionScalerOrchestrator(
            service=service,
            sugar=sugar,
            scale_type=scale_type,
            scale_levels_pips=[30.0, 60.0, 90.0],  # Scale at +/-30, 60, 90 pips
            scale_volume_percent=50.0,              # Add 50% of base volume
            max_total_volume=0.50,                  # Max 0.50 lots total
            update_interval_ms=1000,                # Check every second
            dry_run=False                           # Set True for testing
        )

        # Run orchestrator for 3 minutes
        await orchestrator.start(
            symbol=test_symbol,
            base_ticket=base_ticket,  # Use the first opened position
            duration_minutes=3.0,
            cancellation_event=cancellation_event
        )

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user - shutting down gracefully...")
        cancellation_event.set()
        await asyncio.sleep(0.5)

    finally:
        # Close ONLY test positions that we opened
        print("\nClosing test positions...")
        try:
            if not test_positions:
                print("  No test positions to close")
            else:
                # Get current positions to check which are still open
                opened_data = await service.get_opened_orders(
                    account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
                )

                # Create a set of currently open tickets
                open_tickets = {p.ticket for p in opened_data.position_infos}

                # Close only our test positions that are still open
                closed_count = 0
                for ticket in test_positions:
                    if ticket not in open_tickets:
                        print(f"    Position #{ticket} already closed")
                        continue

                    try:
                        # Find position info
                        pos = next((p for p in opened_data.position_infos if p.ticket == ticket), None)

                        # Close position
                        close_result = await sugar.close_position(ticket)
                        if close_result > 0:
                            profit = pos.profit if pos else 0.0
                            print_success(f"    Closed position #{ticket} (profit: {profit:.2f})")
                            closed_count += 1
                        else:
                            print_warning(f"    Failed to close position #{ticket}")
                    except Exception as e:
                        print_if_error(e, f"Error closing position #{ticket}")

                print(f"  Closed {closed_count}/{len(test_positions)} test position(s)")

        except Exception as e:
            print_if_error(e, "Failed to close test positions")

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
    print("   - Auto-detect scaling mode (PYRAMIDING for safety)")
    print("   - Automatic opening of 2 test positions (first = base, second = backup)")
    print("   - Automatic volume addition at profit/loss levels")
    print("   - Auto-switch to backup position if base closes")
    print("   - Total volume limit enforcement")
    print("   - Margin checking before each scale")
    print("   - Each level triggers only once")
    print("   - Timed execution with live progress")
    print("   - Smart cleanup: closes ONLY test positions (leaves others alone)")
    print()
    print("[!] NOTE: In production, positions should already exist before running the scaler")
    print()


if __name__ == "__main__":
    asyncio.run(main())
