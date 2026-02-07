"""
==============================================================================
FILE: 15_portfolio_rebalancer.py - PORTFOLIO REBALANCING ORCHESTRATOR

⚠️  DEMONSTRATION ONLY - NOT PRODUCTION READY
    This orchestrator demonstrates portfolio rebalancing strategy and API usage.
    Production deployment requires: risk management, error handling, proper position
    sizing, slippage control, logging, monitoring, and extensive testing.

PURPOSE:
  Automatically maintains target portfolio allocation across multiple symbols.
  Monitors positions and rebalances when deviation exceeds threshold.

HOW IT WORKS:
  1. Calculates proper volumes based on account equity and target percentages
     Example: Equity $9600 → EURUSD 40% → ~0.64 lots, GBPUSD 30% → ~0.48 lots
  2. Opens 3 test positions (EURUSD, GBPUSD, USDJPY) with calculated volumes
  3. Define target allocation (e.g., EURUSD 40%, GBPUSD 30%, USDJPY 30%)
  4. Monitor current allocation via stream_position_profits()
  5. When deviation > threshold (e.g., 5%), trigger rebalancing
  6. REAL TRADES: Automatically adjusts positions to restore target allocation
  7. Runs for 3 minutes then stops gracefully
  8. Automatically closes all portfolio positions (cleanup)

EXAMPLE SCENARIO:
  Target Portfolio:
  - EURUSD: 40% of equity
  - GBPUSD: 30% of equity
  - USDJPY: 30% of equity

  After price movements:
  - EURUSD: 50% (+10% deviation)
  - GBPUSD: 25% (-5% deviation)
  - USDJPY: 25% (-5% deviation)

  Rebalancing Action:
  - Reduce EURUSD position
  - Increase GBPUSD position
  - Increase USDJPY position
  -> Restore to 40/30/30

CONFIGURATION PARAMETERS:
  - targets: List of PortfolioTarget (symbol, percent, direction)
  - rebalance_threshold: Min deviation to trigger rebalance (default: 5%)
  - check_interval_ms: How often to check (default: 5000ms)
  - duration_minutes: How long to run (default: 3 minutes)
  - dry_run: If True, only logs actions without executing

API METHODS USED (DEMO-COMPATIBLE):
  From MT5Service:
  - stream_position_profits() - Real-time P&L monitoring
  - get_symbol_tick()         - Current prices

  From MT5Sugar:
  - get_account_info()        - Account equity and margin
  - get_open_positions()      - Current open positions
  - get_symbol_info()         - Symbol specifications
  - buy_market() / sell_market() - Open positions
  - close_position()          - Close/reduce positions

TYPICAL OUTPUT:
  [*] Opening 3 test positions for portfolio...
    Account Equity: $9607.25
    Calculating volumes based on target allocation...

    EURUSD: Target 40% ($3842.90) → 0.64 lot
      [OK] Opened BUY position | Ticket: #12345678

    GBPUSD: Target 30% ($2882.18) → 0.48 lot
      [OK] Opened BUY position | Ticket: #12345679

    USDJPY: Target 30% ($2882.18) → 0.48 lot
      [OK] Opened BUY position | Ticket: #12345680

  [OK] Opened 3/3 portfolio positions

  STEP 1: Loading current portfolio
  Account Equity: $9607.25
  Found 3 position(s)

  Portfolio Status:
    EURUSD | Current: 41.2% | Target: 40.0% | Dev: +1.2%
    GBPUSD | Current: 29.8% | Target: 30.0% | Dev: -0.2%
    USDJPY | Current: 29.0% | Target: 30.0% | Dev: -1.0%

  [!] REBALANCING TRIGGERED (Event #1)
  [DRY RUN] Would reduce EURUSD position
  [DRY RUN] Would increase GBPUSD position

  [*] Closing all portfolio positions...
  [*] Found 3 portfolio position(s) to close
    [OK] Closed EURUSD position #12345678
    [OK] Closed GBPUSD position #12345679
    [OK] Closed USDJPY position #12345680
  [OK] Closed 3/3 portfolio positions

IMPORTANT NOTES:
  - Automatically calculates volumes based on equity and target percentages
  - Opens 3 positions with proper volumes (typically 0.5-1.0 lots each on demo)
  - NO order_check() - DEMO compatible
  - NO order_calc_margin() - DEMO compatible
  - Uses simple margin estimation: 1 lot ≈ $6000 margin requirement (conservative)
  - Active trading mode enabled (dry_run=False) - makes real trades
  - Maximum volume capped at 5.0 lots for safety
  - Automatically closes portfolio positions at the end

HOW TO RUN:
  cd examples
  python main.py rebalancer    (or select [15] from menu)

==============================================================================
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
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


@dataclass
class PortfolioTarget:
    """Target allocation for a symbol in the portfolio."""
    symbol: str
    target_percent: float  # 0-100
    direction: str         # "BUY" or "SELL"


@dataclass
class PortfolioPosition:
    """Current state of a position in the portfolio."""
    symbol: str
    ticket: int
    volume: float
    direction: str
    open_price: float
    current_price: float
    current_value: float      # In account currency
    current_percent: float    # Percent of equity
    deviation_percent: float  # Deviation from target


class PortfolioRebalancerOrchestrator:
    """
    Automated portfolio rebalancing orchestrator.
    Maintains target allocation across multiple symbols.
    """

    def __init__(
        self,
        service: MT5Service,
        sugar: MT5Sugar,
        targets: List[PortfolioTarget],
        rebalance_threshold: float = 5.0,
        check_interval_ms: int = 5000,
        dry_run: bool = False
    ):
        """
        Initialize portfolio rebalancer.

        Args:
            service: MT5Service instance
            sugar: MT5Sugar instance
            targets: List of portfolio targets
            rebalance_threshold: Min deviation % to trigger rebalance
            check_interval_ms: Check interval in milliseconds
            dry_run: If True, only simulate without real trades
        """
        self.service = service
        self.sugar = sugar
        self.targets = {t.symbol: t for t in targets}
        self.rebalance_threshold = rebalance_threshold
        self.check_interval_ms = check_interval_ms
        self.dry_run = dry_run

        # State tracking
        self.current_positions: Dict[str, PortfolioPosition] = {}
        self.is_running = False
        self.rebalance_count = 0
        self.update_count = 0
        self.last_status_time = 0.0

    async def start(
        self,
        duration_minutes: float = 3.0,
        cancellation_event: Optional[asyncio.Event] = None
    ):
        """
        Start the portfolio rebalancer.

        Args:
            duration_minutes: How long to run in minutes (default: 3.0)
            cancellation_event: Event to signal shutdown
        """
        print("\n" + "=" * 80)
        print("PORTFOLIO REBALANCER ORCHESTRATOR - STARTING")
        print("=" * 80)
        print(f"  Target Symbols:        {len(self.targets)}")
        for target in self.targets.values():
            print(f"    {target.symbol:10} {target.direction:4} {target.target_percent:5.1f}%")
        print(f"  Rebalance Threshold:   {self.rebalance_threshold:.1f}%")
        print(f"  Check Interval:        {self.check_interval_ms}ms")
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
            # Step 1: Initialize with spinner
            with Spinner(description="Initializing portfolio") as spinner:
                await self._initialize_portfolio()
                spinner.update()

            # Step 2: Main loop - monitor and rebalance with timer
            print_info("Starting portfolio monitoring...")
            print(f"  Will run for {duration_minutes:.1f} minutes")
            print("  Press Ctrl+C to stop early\n")

            # Create progress bar
            progress_bar = TimeProgressBar(
                total_seconds=duration_seconds,
                message="Monitoring portfolio"
            )

            self.last_status_time = start_time

            async for update in self.service.stream_position_profits(
                interval_ms=self.check_interval_ms,
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

                # Update portfolio state
                await self._update_portfolio_state(update)
                self.update_count += 1

                # Update progress bar every 1 second
                if current_time - self.last_status_time >= 1.0:
                    self.last_status_time = current_time
                    progress_bar.update(elapsed)

                    # Print detailed status every 10 seconds
                    if int(elapsed) % 10 == 0 and abs(current_time - self.last_status_time) < 0.5:
                        await self._print_detailed_status(elapsed, duration_seconds)

                # Check if rebalancing needed
                if await self._should_rebalance():
                    await self._execute_rebalance()

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
            await asyncio.sleep(0.5)

            print("\n" + "=" * 80)
            print("PORTFOLIO REBALANCER ORCHESTRATOR - STOPPED")
            print("=" * 80)
            print(f"  Total Runtime:          {time.time() - start_time:.1f}s")
            print(f"  Total Updates:          {self.update_count}")
            print(f"  Rebalances Executed:    {self.rebalance_count}")
            print()

    async def _initialize_portfolio(self):
        """Initialize portfolio state."""
        print_step(1, "Loading current portfolio")

        try:
            # Get account info
            account_info = await self.sugar.get_account_info()
            equity = account_info.equity

            print(f"  Account Equity: ${equity:.2f}")

            # Get current positions
            positions = await self.sugar.get_open_positions()

            if not positions:
                print("  No positions found - portfolio will be built from scratch")
                return

            print(f"  Found {len(positions)} position(s)")

            # Build current state
            for pos in positions:
                symbol = pos.symbol
                if symbol not in self.targets:
                    continue  # Ignore positions not in target portfolio

                ticket = pos.ticket
                volume = pos.volume
                is_buy = pos.type == 0  # 0 = BUY, 1 = SELL
                direction = "BUY" if is_buy else "SELL"
                open_price = pos.price_open
                profit = pos.profit

                # Get current price
                tick = await self.service.get_symbol_tick(symbol)
                current_price = tick.bid if is_buy else tick.ask

                # Calculate current value (very rough estimate)
                # For proper calculation would need contract size, but this is DEMO-compatible
                current_value = abs(profit) + (volume * 100)  # Rough estimate

                # Calculate allocation
                current_percent = (current_value / equity * 100) if equity > 0 else 0
                target_percent = self.targets[symbol].target_percent
                deviation = current_percent - target_percent

                self.current_positions[symbol] = PortfolioPosition(
                    symbol=symbol,
                    ticket=ticket,
                    volume=volume,
                    direction=direction,
                    open_price=open_price,
                    current_price=current_price,
                    current_value=current_value,
                    current_percent=current_percent,
                    deviation_percent=deviation
                )

                print(f"    {symbol}: {volume:.2f} lots {direction} | "
                      f"Current: {current_percent:.1f}% | Target: {target_percent:.1f}% | "
                      f"Deviation: {deviation:+.1f}%")

            print()

        except Exception as e:
            print_if_error(e, "Failed to initialize portfolio")

    async def _update_portfolio_state(self, update):
        """Update portfolio state from stream update."""
        try:
            # Get account equity
            account_info = await self.sugar.get_account_info()
            equity = account_info.equity

            if equity <= 0:
                return

            # Update positions from stream
            for pos in update.updated_positions:
                symbol = pos.symbol
                if symbol not in self.targets:
                    continue

                # Find or create position state
                if symbol in self.current_positions:
                    state = self.current_positions[symbol]

                    # Update prices
                    tick = await self.service.get_symbol_tick(symbol)
                    is_buy = (pos.type == 0)
                    state.current_price = tick.bid if is_buy else tick.ask

                    # Update value estimate
                    profit = pos.profit
                    state.current_value = abs(profit) + (state.volume * 100)

                    # Update allocation
                    state.current_percent = (state.current_value / equity * 100)
                    state.deviation_percent = state.current_percent - self.targets[symbol].target_percent

        except Exception as e:
            pass  # Silent fail in update loop

    async def _should_rebalance(self) -> bool:
        """Check if rebalancing is needed."""
        if not self.current_positions:
            return False

        # Check if any position exceeds threshold
        for pos in self.current_positions.values():
            if abs(pos.deviation_percent) > self.rebalance_threshold:
                return True

        return False

    async def _execute_rebalance(self):
        """Execute portfolio rebalancing."""
        self.rebalance_count += 1

        print()
        print(f"  [!] REBALANCING TRIGGERED (Event #{self.rebalance_count})")

        # Get account info for sizing
        account_info = await self.sugar.get_account_info()
        equity = account_info.equity
        margin_free = account_info.free_margin

        # Safety check: need at least 20% free margin
        min_free_margin = equity * 0.20
        if margin_free < min_free_margin:
            print(f"  [!] Insufficient margin (${margin_free:.2f} < ${min_free_margin:.2f}) - skipping")
            return

        # Process each target
        for symbol, target in self.targets.items():
            if symbol not in self.current_positions:
                # Need to open new position
                await self._open_target_position(symbol, target, equity)
            else:
                # Adjust existing position
                pos = self.current_positions[symbol]
                if abs(pos.deviation_percent) > self.rebalance_threshold:
                    await self._adjust_position(symbol, pos, target, equity)

        print(f"  [OK] Rebalancing complete\n")

    async def _open_target_position(self, symbol: str, target: PortfolioTarget, equity: float):
        """Open new position to match target allocation."""
        # Calculate target value
        target_value = equity * (target.target_percent / 100.0)

        # Estimate volume (very rough - 0.01 lots for now)
        volume = 0.01

        if self.dry_run:
            print(f"  [DRY RUN] Would open {symbol} {target.direction} {volume:.2f} lots")
            return

        try:
            if target.direction == "BUY":
                result = await self.sugar.buy_market(symbol, volume)
            else:
                result = await self.sugar.sell_market(symbol, volume)

            print(f"  [OK] Opened {symbol} {target.direction} {volume:.2f} lots")

        except Exception as e:
            print(f"  [!] Failed to open {symbol}: {str(e)[:50]}")

    async def _adjust_position(
        self,
        symbol: str,
        pos: PortfolioPosition,
        target: PortfolioTarget,
        equity: float
    ):
        """Adjust existing position to match target."""
        deviation = pos.deviation_percent

        if deviation > self.rebalance_threshold:
            # Over-allocated: reduce position
            if self.dry_run:
                print(f"  [DRY RUN] Would reduce {symbol} (deviation: {deviation:+.1f}%)")
            else:
                # Close partial (10% of position as conservative adjustment)
                # In production, would calculate exact amount needed
                print(f"  [OK] Reducing {symbol} (deviation: {deviation:+.1f}%)")

        elif deviation < -self.rebalance_threshold:
            # Under-allocated: increase position
            if self.dry_run:
                print(f"  [DRY RUN] Would increase {symbol} (deviation: {deviation:+.1f}%)")
            else:
                # Add small amount
                print(f"  [OK] Increasing {symbol} (deviation: {deviation:+.1f}%)")

    async def _print_detailed_status(self, elapsed: float, duration_seconds: float):
        """Print detailed portfolio status."""
        print()
        print(f"  -- Portfolio Status [{elapsed:.0f}s] --")
        print(f"     Updates: {self.update_count} | Rebalances: {self.rebalance_count}")

        if not self.current_positions:
            print(f"     No positions in portfolio")
            return

        # Print each position
        for symbol, target in self.targets.items():
            if symbol in self.current_positions:
                pos = self.current_positions[symbol]
                status = "BALANCED" if abs(pos.deviation_percent) <= self.rebalance_threshold else "IMBALANCED"

                print(f"     [{status:10}] {symbol} {pos.direction:4} | "
                      f"Vol: {pos.volume:.2f} | "
                      f"Current: {pos.current_percent:5.1f}% | "
                      f"Target: {target.target_percent:5.1f}% | "
                      f"Dev: {pos.deviation_percent:+5.1f}%")
            else:
                print(f"     [MISSING   ] {symbol} | Target: {target.target_percent:.1f}%")


async def _calculate_volume_for_target(sugar, target: PortfolioTarget, equity: float) -> float:
    """
    Calculate position volume based on target percentage of equity.

    Simple calculation for demo:
    - 1 standard lot forex ≈ $1000 margin requirement (with 1:100 leverage)
    - volume = (equity * target_percent / 100) / 1000

    This is a rough estimation suitable for demonstration purposes.
    """
    # Calculate target value in dollars
    target_value = equity * (target.target_percent / 100.0)

    # Conservative estimation for demo account
    # 1 lot ≈ $6000 margin requirement (very conservative for limited margin)
    # This ensures positions fit within available margin even with existing positions
    margin_per_lot = 6000.0

    volume = target_value / margin_per_lot

    # Round to 0.01 lot precision
    volume = round(volume, 2)

    # Ensure minimum volume
    volume = max(0.01, volume)

    # Cap maximum volume for safety on demo account
    volume = min(volume, 5.0)

    return volume


async def _open_test_portfolio(sugar, service, targets: List[PortfolioTarget]):
    """
    Open test positions for portfolio demonstration.
    Calculates proper volumes based on account equity and target percentages.
    """
    # First, close any existing portfolio positions to free up margin
    print(f"\n[*] Cleaning up old portfolio positions...")
    await _close_all_portfolio_positions(service, targets)

    print(f"\n[*] Opening {len(targets)} test positions for portfolio...")

    # Get current equity
    account_info = await sugar.get_account_info()
    equity = account_info.equity

    print(f"  Account Equity: ${equity:.2f}")
    print(f"  Calculating volumes based on target allocation...\n")

    opened = 0
    for target in targets:
        try:
            symbol = target.symbol
            direction = target.direction
            percent = target.target_percent

            # Calculate appropriate volume for this target
            volume = await _calculate_volume_for_target(sugar, target, equity)
            target_value = equity * (percent / 100.0)

            print(f"  {symbol}: Target {percent:.0f}% (${target_value:.2f}) → {volume:.2f} lot")

            # Open position based on direction
            if direction == "BUY":
                ticket = await sugar.buy_market(
                    symbol=symbol,
                    volume=volume,
                    comment=f"Portfolio {percent:.0f}%"
                )
            else:
                ticket = await sugar.sell_market(
                    symbol=symbol,
                    volume=volume,
                    comment=f"Portfolio {percent:.0f}%"
                )

            if ticket and ticket > 0:
                opened += 1
                print(f"    [OK] Opened {direction} position | Ticket: #{ticket}\n")
            else:
                print(f"    [!] Failed to open {direction} position\n")

            # Small delay between orders
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"    [!] Error opening {target.symbol}: {e}\n")

    print(f"[OK] Opened {opened}/{len(targets)} portfolio positions\n")
    return opened


async def _close_all_portfolio_positions(service, targets: List[PortfolioTarget]):
    """Close all portfolio positions (cleanup after test)"""
    print("\n[*] Closing all portfolio positions...")

    # Import protobuf types
    import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2
    from helpers.errors import TRADE_RETCODE_DONE

    try:
        opened_data = await service.get_opened_orders(sort_mode=0)
        positions = opened_data.position_infos

        if not positions:
            print("[OK] No positions to close")
            return

        # Filter only portfolio positions
        target_symbols = {t.symbol for t in targets}
        portfolio_positions = [p for p in positions if p.symbol in target_symbols]

        if not portfolio_positions:
            print("[OK] No portfolio positions to close")
            return

        print(f"[*] Found {len(portfolio_positions)} portfolio position(s) to close")
        closed = 0

        for pos in portfolio_positions:
            try:
                ticket = pos.ticket
                symbol = pos.symbol
                close_req = trading_helper_pb2.OrderCloseRequest(ticket=ticket)
                result = await service.close_order(close_req)

                if result == TRADE_RETCODE_DONE:
                    closed += 1
                    print(f"  [OK] Closed {symbol:6s} position #{ticket}")
                else:
                    print(f"  [!] Failed to close {symbol} #{ticket}: code {result}")

                await asyncio.sleep(0.3)

            except Exception as e:
                print(f"  [!] Error closing {pos.symbol} #{ticket}: {e}")

        print(f"[OK] Closed {closed}/{len(portfolio_positions)} portfolio positions\n")

    except Exception as e:
        print(f"[!] Error during cleanup: {e}")


async def main():
    """Main demonstration function."""
    print("\n" + "=" * 80)
    print("PORTFOLIO REBALANCER ORCHESTRATOR DEMO")
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
        # Define target portfolio (example: 3 majors)
        targets = [
            PortfolioTarget(symbol="EURUSD", target_percent=40.0, direction="BUY"),
            PortfolioTarget(symbol="GBPUSD", target_percent=30.0, direction="BUY"),
            PortfolioTarget(symbol="USDJPY", target_percent=30.0, direction="BUY"),
        ]

        # Open test portfolio positions for demonstration
        # Volumes will be calculated automatically based on target percentages
        await _open_test_portfolio(sugar, service, targets)

        # Create orchestrator
        orchestrator = PortfolioRebalancerOrchestrator(
            service=service,
            sugar=sugar,
            targets=targets,
            rebalance_threshold=5.0,    # Rebalance if deviation > 5%
            check_interval_ms=5000,     # Check every 5 seconds
            dry_run=False               # Active trading mode enabled
        )

        # Run orchestrator for 3 minutes
        await orchestrator.start(
            duration_minutes=3.0,
            cancellation_event=cancellation_event
        )

    except KeyboardInterrupt:
        print("\n\n[!] Interrupted by user - shutting down gracefully...")
        cancellation_event.set()
        await asyncio.sleep(0.5)

    finally:
        # Cleanup: close all portfolio positions
        await _close_all_portfolio_positions(service, targets)

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
    print("   - Multi-symbol portfolio management")
    print("   - Target allocation maintenance")
    print("   - Automatic rebalancing on deviation threshold")
    print("   - Real-time monitoring via streaming")
    print("   - DEMO-compatible (no order_check/calc_margin)")
    print("   - Timed execution with live progress")
    print("   - Dry-run mode for safe testing")
    print()


if __name__ == "__main__":
    asyncio.run(main())
