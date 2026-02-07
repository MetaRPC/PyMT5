"""
==============================================================================
 FILE: 14_risk_manager.py - RISK MANAGER ORCHESTRATOR

  ⚠️  DEMONSTRATION ONLY - NOT PRODUCTION READY
      This orchestrator demonstrates risk management strategy and API usage.
      Production deployment requires: comprehensive risk management, error handling,
      proper position sizing, slippage control, logging, monitoring, and extensive testing.

  🎯 PURPOSE:
   Real-time account protection system that monitors account health and
   automatically enforces risk limits. Protects your account from excessive
   drawdown, margin calls, and overleveraging by closing positions when
   thresholds are breached.

   HOW IT WORKS:
   1. Opens 2 test positions (BUY & SELL 0.01 lot) for demonstration
   2. Captures initial account balance at startup
   3. Monitors ALL existing positions via stream_position_profits() in real-time
   4. Shows progress bar and updates every 10 seconds with:
      - Current drawdown from initial balance
      - Daily profit/loss percentage
      - Margin level (used vs available)
      - Number of open positions
      - Total profit/loss
   5. AUTOMATIC PROTECTION - Closes all positions if ANY limit breached:
      - Drawdown exceeds max % (default: 10%)
      - Daily loss exceeds max % (default: 5%)
      - Margin level drops below minimum (default: 150%)
      - Position count exceeds maximum (default: 10)
   6. Logs all violations and closures for audit trail
   7. Automatically closes test positions on exit (cleanup)
   8. Provides final risk report with statistics

  📚 EXAMPLE SCENARIOS:

   Scenario A - Drawdown Protection:
     Initial Balance: $10,000
     Max Drawdown: 10% ($1,000)

     Current: Equity drops to $8,900 (-11% drawdown)
      → TRIGGERED: Drawdown 11.00% > 10.00%
      → ACTION: Close all 3 open positions
      → RESULT: Account protected from further losses

   Scenario B - Daily Loss Limit:
     Initial Balance: $10,000
     Max Daily Loss: 5% ($500)

     Today's P/L: -$550 (-5.5%)
      → TRIGGERED: Daily loss 5.50% > 5.00%
      → ACTION: Close all positions
      → RESULT: Prevents catastrophic daily loss

   Scenario C - Margin Call Prevention:
     Margin Level: 140%
     Min Margin Level: 150%

     → TRIGGERED: Margin level 140% < 150%
     → ACTION: Close positions to free margin
     → RESULT: Prevents broker margin call at 100%

   Scenario D - Position Limit:
     Open Positions: 12
     Max Positions: 10

     → TRIGGERED: Positions 12 > 10
     → ACTION: Close all positions
     → RESULT: Prevents overleveraging

  💡 CONFIGURATION PARAMETERS:

   RiskLimits dataclass controls protection levels:
     - max_drawdown_percent: 10.0        # Close all if equity drops 10%
     - max_daily_loss_percent: 5.0       # Close all if daily loss > 5%
     - min_margin_level: 150.0           # Close if margin < 150%
     - max_positions: 10                 # Maximum simultaneous positions
     - max_risk_per_trade_percent: 2.0   # Future: per-trade risk limit

   Customize in code (lines 585-590):
     limits = RiskLimits(
         max_drawdown_percent=15.0,      # More aggressive (15%)
         max_daily_loss_percent=3.0,     # Stricter daily limit (3%)
         min_margin_level=200.0,         # Higher margin buffer (200%)
         max_positions=5                 # Fewer positions allowed
     )

  📊 TYPICAL OUTPUT:

   [*] Opening 2 test positions on EURUSD...
     [OK] Opened BUY position #12345678
     [OK] Opened SELL position #12345679
   [OK] Opened 2/2 test positions

   --- Risk Manager Configuration ---
   Initial Balance: $10000.00
   Max Drawdown: 10.0%
   Max Daily Loss: 5.0%
   Min Margin Level: 150%
   Max Positions: 10
   ----------------------------------

   [OK] Risk Manager active - monitoring account health
   [*] Will run for 180 seconds

   [=========>          ] Risk monitoring (30s/180s)

   [10s/180s] [OK] Equity: $10025.50 | Drawdown: 0.00% | Margin: 350% |
              Positions: 2 | P/L: +$25.50 | Violations: 0

   [20s/180s] [OK] Equity: $10018.20 | Drawdown: 0.00% | Margin: 340% |
              Positions: 2 | P/L: +$18.20 | Violations: 0

   [!] RISK LIMIT BREACHED:
       -> Margin level 140% < 150%
   [!] Closing 3 positions for protection...
       [OK] Closed position #12345678
       [OK] Closed position #12345679
       [OK] Closed position #12345680
   [OK] Protection complete: 3/3 closed

   --- Final Risk Report ---
   Updates Processed: 36
   Violations Detected: 1
   Final Balance: $9875.00
   Final Equity: $9875.00
   Total Drawdown: 1.25%
   Open Positions: 0
   Total P/L: $-125.00
   ------------------------

   [*] Closing all test positions...
   [*] Found 2 position(s) to close
     [OK] Closed position #12345678
     [OK] Closed position #12345679
   [OK] Closed 2/2 positions

  🚀 HOW TO RUN:
   cd examples
   python main.py risk                (or select [14] from menu)

   OR run directly from examples folder:
   python 4_orchestrators/14_risk_manager.py

  ⚙️ REQUIREMENTS:
   - Active MT5 terminal connection
   - Settings file with account credentials (settings.json)
   - Demo or live account with sufficient balance ($10+ recommended)

  ⚠️ IMPORTANT NOTES:
   - This orchestrator WILL close positions automatically!
   - Opens 2 test positions (BUY & SELL 0.01 lot) at start
   - Test with DEMO account first to understand behavior
   - Adjust limits according to your risk tolerance
   - Monitor first run closely to ensure correct operation
   - Automatically closes all positions at the end (cleanup)
   - Compatible with demo accounts (no order_check needed)

  🔧 CUSTOMIZATION IDEAS:
   - Add email/SMS alerts when limits breached
   - Implement partial closure instead of closing all
   - Add time-based rules (e.g., close all at market close)
   - Log violations to database for analysis
   - Add profit targets (close when daily profit > X%)
   - Implement trailing drawdown protection

DEMO COMPATIBLE: Avoids order_check() and DOM methods
ASCII ONLY: No Unicode symbols for maximum compatibility
==============================================================================
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "0_common"))

from progress_bar import Spinner, TimeProgressBar
from demo_helpers import (
    load_settings,
    create_and_connect_mt5,
    print_step,
    print_success,
    print_if_error,
    print_info,
    fatal,
)

# Import protobuf types
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2

# Import trade return codes
from MetaRpcMT5.helpers.errors import TRADE_RETCODE_DONE


@dataclass
class RiskMetrics:
    """Current account risk metrics"""
    initial_balance: float
    current_balance: float
    current_equity: float
    current_margin: float
    free_margin: float
    margin_level: float
    open_positions: int
    total_profit: float
    daily_profit: float

    @property
    def drawdown_percent(self) -> float:
        """Calculate current drawdown from initial balance"""
        if self.initial_balance <= 0:
            return 0.0
        return ((self.initial_balance - self.current_equity) / self.initial_balance) * 100

    @property
    def daily_loss_percent(self) -> float:
        """Calculate daily loss percentage"""
        if self.initial_balance <= 0:
            return 0.0
        return (self.daily_profit / self.initial_balance) * 100


@dataclass
class RiskLimits:
    """Risk management limits"""
    max_drawdown_percent: float = 10.0      # Close all if equity drops 10%
    max_daily_loss_percent: float = 5.0     # Close all if daily loss exceeds 5%
    min_margin_level: float = 150.0         # Close positions if margin level < 150%
    max_positions: int = 10                  # Maximum simultaneous positions
    max_risk_per_trade_percent: float = 2.0  # Maximum risk per position


class RiskManagerOrchestrator:
    """
    Real-time risk management orchestrator

    Continuously monitors account health and enforces risk limits.
    Automatically closes positions when thresholds are breached.
    """

    def __init__(self, service, limits: Optional[RiskLimits] = None):
        """
        Initialize Risk Manager

        Args:
            service: MT5Service or MT5Sugar instance
            limits: Risk limits configuration (uses defaults if None)
        """
        self.service = service
        self.limits = limits or RiskLimits()
        self.initial_balance: Optional[float] = None
        self.update_count = 0
        self.violations_count = 0
        self.last_check_time = 0.0

    async def _get_current_metrics(self) -> RiskMetrics:
        """Gather current account metrics"""
        # Get account info
        account_info = await self.service.get_account_summary()

        balance = account_info.balance
        equity = account_info.equity
        margin = account_info.margin
        free_margin = account_info.free_margin
        margin_level = account_info.margin_level

        # Get positions
        opened_data = await self.service.get_opened_orders(sort_mode=0)
        positions = opened_data.position_infos
        open_positions = len(positions)
        total_profit = sum(p.profit for p in positions)

        # Get daily stats (if available)
        daily_profit = 0.0
        try:
            # Calculate daily profit from positions opened today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            for pos in positions:
                open_time = pos.time
                if open_time >= today_start.timestamp():
                    daily_profit += pos.profit
        except Exception:
            # Fallback: use total profit as daily profit
            daily_profit = total_profit

        return RiskMetrics(
            initial_balance=self.initial_balance or balance,
            current_balance=balance,
            current_equity=equity,
            current_margin=margin,
            free_margin=free_margin,
            margin_level=margin_level,
            open_positions=open_positions,
            total_profit=total_profit,
            daily_profit=daily_profit
        )

    async def _check_and_enforce_limits(self, metrics: RiskMetrics) -> bool:
        """
        Check risk limits and enforce if breached

        Returns:
            True if limits breached and positions closed
        """
        violations = []

        # Check 1: Maximum Drawdown
        if metrics.drawdown_percent > self.limits.max_drawdown_percent:
            violations.append(f"Drawdown {metrics.drawdown_percent:.2f}% > {self.limits.max_drawdown_percent:.2f}%")

        # Check 2: Daily Loss Limit
        if metrics.daily_loss_percent < -self.limits.max_daily_loss_percent:
            violations.append(f"Daily loss {abs(metrics.daily_loss_percent):.2f}% > {self.limits.max_daily_loss_percent:.2f}%")

        # Check 3: Margin Level
        if metrics.margin_level > 0 and metrics.margin_level < self.limits.min_margin_level:
            violations.append(f"Margin level {metrics.margin_level:.0f}% < {self.limits.min_margin_level:.0f}%")

        # Check 4: Position Count
        if metrics.open_positions > self.limits.max_positions:
            violations.append(f"Positions {metrics.open_positions} > {self.limits.max_positions}")

        # If violations found, close all positions
        if violations:
            self.violations_count += 1
            print(f"\n[!] RISK LIMIT BREACHED:")
            for v in violations:
                print(f"    -> {v}")

            # Close all positions
            opened_data = await self.service.get_opened_orders(sort_mode=0)
            positions = opened_data.position_infos
            if positions:
                print(f"[!] Closing {len(positions)} positions for protection...")
                closed_count = 0

                for pos in positions:
                    try:
                        ticket = pos.ticket
                        if ticket > 0:
                            # Use close_order with OrderCloseRequest
                            close_req = trading_helper_pb2.OrderCloseRequest(
                                ticket=ticket
                            )
                            result_code = await self.service.close_order(close_req)

                            if result_code == TRADE_RETCODE_DONE:
                                closed_count += 1
                                print(f"    [OK] Closed position #{ticket}")
                            else:
                                print(f"    [!] Failed to close #{ticket}: code {result_code}")
                    except Exception as e:
                        print(f"    [!] Failed to close #{ticket}: {e}")

                print(f"[OK] Protection complete: {closed_count}/{len(positions)} closed")
                return True

        return False

    async def _initialize(self):
        """Initialize risk manager - capture initial balance"""
        account_info = await self.service.get_account_summary()
        self.initial_balance = account_info.balance

        print(f"\n--- Risk Manager Configuration ---")
        print(f"Initial Balance: ${self.initial_balance:.2f}")
        print(f"Max Drawdown: {self.limits.max_drawdown_percent:.1f}%")
        print(f"Max Daily Loss: {self.limits.max_daily_loss_percent:.1f}%")
        print(f"Min Margin Level: {self.limits.min_margin_level:.0f}%")
        print(f"Max Positions: {self.limits.max_positions}")
        print(f"----------------------------------\n")

    async def start(
        self,
        duration_minutes: float = 3.0,
        cancellation_event: Optional[asyncio.Event] = None
    ):
        """
        Start risk monitoring

        Args:
            duration_minutes: How long to run (default: 3 minutes)
            cancellation_event: Event to signal early shutdown
        """
        if cancellation_event is None:
            cancellation_event = asyncio.Event()

        start_time = time.time()
        duration_seconds = duration_minutes * 60

        print(f"[*] Starting Risk Manager for {duration_minutes:.1f} minutes...")

        # Initialize
        with Spinner(description="Initializing risk manager") as spinner:
            await self._initialize()
            await asyncio.sleep(0.5)
            spinner.update()

        print("[OK] Risk Manager active - monitoring account health")
        print(f"[*] Will run for {duration_seconds:.0f} seconds\n")

        # Create progress bar
        progress_bar = TimeProgressBar(
            total_seconds=duration_seconds,
            message="Risk monitoring"
        )
        progress_bar.update(0)

        try:
            # Monitor via position profit stream
            async for update in self.service.stream_position_profits(
                interval_ms=1000,      # Check every second
                ignore_empty=False,    # Show all updates for visibility
                cancellation_event=cancellation_event
            ):
                self.update_count += 1
                current_time = time.time()
                elapsed = current_time - start_time

                # Update progress bar
                progress_bar.update(elapsed)

                # Check if time expired
                if elapsed >= duration_seconds or cancellation_event.is_set():
                    progress_bar.finish()
                    print(f"\n[*] Duration complete ({elapsed:.0f}s)")
                    break

                # Rate limit checks (every 10 seconds minimum)
                if current_time - self.last_check_time < 10.0:
                    continue

                self.last_check_time = current_time

                # Get current metrics
                metrics = await self._get_current_metrics()

                # Check and enforce limits
                limit_breached = await self._check_and_enforce_limits(metrics)

                # Print detailed status
                status = "[PROTECTED]" if limit_breached else "[OK]"

                print(f"\n[{elapsed:.0f}s/{duration_seconds:.0f}s] {status} "
                      f"Equity: ${metrics.current_equity:.2f} | "
                      f"Drawdown: {metrics.drawdown_percent:.2f}% | "
                      f"Margin: {metrics.margin_level:.0f}% | "
                      f"Positions: {metrics.open_positions} | "
                      f"P/L: ${metrics.total_profit:+.2f} | "
                      f"Violations: {self.violations_count}")

        except Exception as e:
            print(f"\n[!] Error in risk manager: {e}")
            raise

        finally:
            # Graceful shutdown
            print(f"\n[*] Stopping risk manager...")
            cancellation_event.set()
            await asyncio.sleep(0.5)

            # Final status
            try:
                final_metrics = await self._get_current_metrics()
                print(f"\n--- Final Risk Report ---")
                print(f"Updates Processed: {self.update_count}")
                print(f"Violations Detected: {self.violations_count}")
                print(f"Final Balance: ${final_metrics.current_balance:.2f}")
                print(f"Final Equity: ${final_metrics.current_equity:.2f}")
                print(f"Total Drawdown: {final_metrics.drawdown_percent:.2f}%")
                print(f"Open Positions: {final_metrics.open_positions}")
                print(f"Total P/L: ${final_metrics.total_profit:.2f}")
                print(f"------------------------\n")
            except Exception as e:
                print(f"[!] Could not generate final report: {e}")

            print("[OK] Risk Manager stopped")


async def _open_test_positions(sugar, symbol: str, count: int = 2):
    """Open test positions for risk manager demonstration"""
    print(f"\n[*] Opening {count} test positions on {symbol}...")

    opened = 0
    for i in range(count):
        try:
            # Alternate BUY and SELL
            is_buy = (i % 2 == 0)
            direction = "BUY" if is_buy else "SELL"

            # Use correct MT5Sugar methods
            if is_buy:
                ticket = await sugar.buy_market(
                    symbol=symbol,
                    volume=0.01,  # Micro lot
                    comment=f"Risk Manager Test {i+1}"
                )
            else:
                ticket = await sugar.sell_market(
                    symbol=symbol,
                    volume=0.01,  # Micro lot
                    comment=f"Risk Manager Test {i+1}"
                )

            if ticket and ticket > 0:
                opened += 1
                print(f"  [OK] Opened {direction} position #{ticket}")
            else:
                print(f"  [!] Failed to open {direction} position")

            # Small delay between orders
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"  [!] Error opening position: {e}")

    print(f"[OK] Opened {opened}/{count} test positions\n")
    return opened


async def _close_all_test_positions(service):
    """Close all open positions (cleanup after test)"""
    print("\n[*] Closing all test positions...")

    try:
        opened_data = await service.get_opened_orders(sort_mode=0)
        positions = opened_data.position_infos

        if not positions:
            print("[OK] No positions to close")
            return

        print(f"[*] Found {len(positions)} position(s) to close")
        closed = 0

        for pos in positions:
            try:
                ticket = pos.ticket
                close_req = trading_helper_pb2.OrderCloseRequest(ticket=ticket)
                result = await service.close_order(close_req)

                if result == TRADE_RETCODE_DONE:
                    closed += 1
                    print(f"  [OK] Closed position #{ticket}")
                else:
                    print(f"  [!] Failed to close #{ticket}: code {result}")

                await asyncio.sleep(0.3)

            except Exception as e:
                print(f"  [!] Error closing #{ticket}: {e}")

        print(f"[OK] Closed {closed}/{len(positions)} positions\n")

    except Exception as e:
        print(f"[!] Error during cleanup: {e}")


async def run_risk_manager_example():
    """Example: Run risk manager with custom limits"""
    from pymt5.mt5_service import MT5Service
    from pymt5.mt5_sugar import MT5Sugar

    # Load configuration
    try:
        config = load_settings()
    except Exception as e:
        fatal(e, "Failed to load settings")

    # Connect to MT5
    print_step(1, "Connecting to MT5")
    try:
        account = await create_and_connect_mt5(config)
        service = MT5Service(account)
        sugar = MT5Sugar(service, default_symbol=config.get('test_symbol', 'EURUSD'))
        print_success("Connected successfully!")
        print()
    except Exception as e:
        fatal(e, "Failed to connect")

    # Open test positions for demonstration
    test_symbol = config.get('test_symbol', 'EURUSD')
    await _open_test_positions(sugar, test_symbol, count=2)

    # Custom risk limits
    limits = RiskLimits(
        max_drawdown_percent=10.0,
        max_daily_loss_percent=5.0,
        min_margin_level=150.0,
        max_positions=10
    )

    try:
        # Create and start risk manager
        manager = RiskManagerOrchestrator(service, limits)
        await manager.start(duration_minutes=3.0)

    finally:
        # Cleanup: close all test positions
        await _close_all_test_positions(service)

        print("\nDisconnecting from MT5...")
        try:
            await account.channel.close()
            print_success("Disconnected successfully")
        except Exception as e:
            print_if_error(e, "Disconnect failed")


if __name__ == "__main__":
    asyncio.run(run_risk_manager_example())
