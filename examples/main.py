"""══════════════════════════════════════════════════════════════════════════════
FILE: main.py - MAIN ENTRY POINT FOR ALL EXAMPLES

╔═══════════════════════════════════════════════════════════════════════════╗
║                    PyMT5 - MetaTrader 5 gRPC Client                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

This is the ENTRY POINT for ALL demonstration examples.
Provides an interactive menu to showcase the MT5 gRPC API at all abstraction
levels: low-level (protobuf), mid-level (service), high-level (sugar), and
automated strategies (orchestrators).

╔═══════════════════════════════════════════════════════════════════════════╗
║                        LEARNING PROGRESSION                               ║
╚═══════════════════════════════════════════════════════════════════════════╝

Follow this order to understand the architecture from ground up:

TIER 1: LOW-LEVEL (MT5Account)
   Location: examples/1_lowlevel/
   Features: Direct gRPC/protobuf calls, raw data structures
   Use case: Understanding the foundation, custom integrations

TIER 2: MID-LEVEL (MT5Service) - RECOMMENDED
   Location: src/pymt5/mt5_service.py
   Features: Wrapper facade over MT5Account, cleaner API with Python types
   Use case: Organized method groups, dataclasses instead of protobuf

TIER 3: HIGH-LEVEL (MT5Sugar)
   Location: src/pymt5/mt5_sugar.py
   Features: One-liner operations, risk-based calculations, auto-normalization
   Use case: Rapid development, smart defaults, ready-made patterns

TIER 4: ORCHESTRATORS
   Location: examples/4_orchestrators/
   Features: Automated trading strategies (trailing stop, grid, risk manager)
   Use case: Production-ready patterns, complete strategy examples

╔═══════════════════════════════════════════════════════════════════════════╗
║                              USAGE                                        ║
╚═══════════════════════════════════════════════════════════════════════════╝

Interactive Menu:
  cd examples
  python main.py                → Shows menu with all 17 examples

Direct Launch (skip menu):
  python main.py 1              → Low-level general operations
  python main.py lowlevel01     → Same as above (alias)
  python main.py service        → Mid-level service examples
  python main.py sugar06        → High-level sugar basics
  python main.py trailing       → Trailing stop orchestrator
  python main.py inspect        → Protobuf inspector tool
  python main.py usercode       → User code sandbox

Available Categories:
  Low-level:      1-3   (lowlevel01, lowlevel02, lowlevel03)
  Service:        4-5   (service, service05)
  Sugar:          6-10  (sugar06, sugar07, sugar08, sugar09, sugar10)
  Orchestrators:  11-15 (trailing, scaler, grid, risk, rebalancer)
  Tools:          16    (inspect)
  Usercode:       17    (usercode)

╔═══════════════════════════════════════════════════════════════════════════╗
║                         PROJECT STRUCTURE                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

examples/
├── main.py                           <- THIS FILE (entry point)
├── 0_common/
│   ├── settings.json                 <- Connection settings
│   ├── demo_helpers.py               <- Connection & error handling utilities
│   ├── progress_bar.py               <- Progress bar utilities
│   └── 16_protobuf_inspector.py      <- Interactive protobuf explorer
│
├── 1_lowlevel/                       <- Low-level (MT5Account) demonstrations
│   ├── 01_general_operations.py      <- Account, symbols, positions, DOM
│   ├── 02_trading_operations.py      <- Order send/modify/close, calculations
│   └── 03_streaming_methods.py       <- Ticks, trades, profits, transactions
│
├── 2_service/                        <- Mid-level (MT5Service) demonstrations
│   ├── 04_service_demo.py            <- Service wrapper examples
│   └── 05_service_streaming.py       <- Service streaming examples
│
├── 3_sugar/                          <- High-level (MT5Sugar) demonstrations
│   ├── 06_sugar_basics.py            <- Connection, account info, symbols
│   ├── 07_sugar_trading.py           <- Trading operations
│   ├── 08_sugar_positions.py         <- Position management
│   ├── 09_sugar_history.py           <- History & profits
│   └── 10_sugar_advanced.py          <- Advanced features
│
├── 4_orchestrators/                  <- Automated strategy demonstrations
│   ├── 11_trailing_stop.py           <- Trailing stop strategy
│   ├── 12_position_scaler.py         <- Position scaling strategy
│   ├── 13_grid_trader.py             <- Grid trading strategy
│   ├── 14_risk_manager.py            <- Risk management system
│   └── 15_portfolio_rebalancer.py    <- Portfolio rebalancing
│
└── 5_usercode/                       <- User code sandbox
    └── 17_usercode.py                <- Custom user code template

══════════════════════════════════════════════════════════════════════════════"""

import asyncio
import sys
import os
import traceback

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add examples directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import demo modules dynamically (files start with numbers)
import importlib.util

def import_demo_module(folder, filename):
    """Import module from file that starts with number"""
    module_path = os.path.join(os.path.dirname(__file__), folder, filename)
    spec = importlib.util.spec_from_file_location(filename.replace('.py', ''), module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None

# Import demo modules from lowlevel/
demo_01 = import_demo_module('1_lowlevel', '01_general_operations.py')
demo_02 = import_demo_module('1_lowlevel', '02_trading_operations.py')
demo_03 = import_demo_module('1_lowlevel', '03_streaming_methods.py')

# Import demo modules from 2_service/
demo_04 = import_demo_module('2_service', '04_service_demo.py')
demo_05 = import_demo_module('2_service', '05_service_streaming.py')

# Import tools from 0_common/
inspector_tool = import_demo_module('0_common', '16_protobuf_inspector.py')

# Import orchestrators from 4_orchestrators/
orchestrator_11 = import_demo_module('4_orchestrators', '11_trailing_stop.py')
orchestrator_12 = import_demo_module('4_orchestrators', '12_position_scaler.py')
orchestrator_13 = import_demo_module('4_orchestrators', '13_grid_trader.py')
orchestrator_14 = import_demo_module('4_orchestrators', '14_risk_manager.py')
orchestrator_15 = import_demo_module('4_orchestrators', '15_portfolio_rebalancer.py')

# Import usercode from 5_usercode/
usercode_demo = import_demo_module('5_usercode', '17_usercode.py')


def print_banner():
    """Print application banner"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║              PyMT5 - MetaTrader 5 gRPC Client                    ║")
    print("║                    LOW-LEVEL DEMONSTRATIONS                      ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()


def show_menu() -> str:
    """
    Display interactive menu and get user choice.

    Returns:
        User's menu choice as string
    """
    print("┌──────────────────────────────────────────────────────────────────┐")
    print("│  LOW-LEVEL EXAMPLES (Direct gRPC)                                │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [1]  General Operations   → python main.py lowlevel01           │")
    print("│  [2]  Trading Operations   → python main.py lowlevel02           │")
    print("│  [3]  Streaming Methods    → python main.py lowlevel03           │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  MID-LEVEL (MT5Service Wrapper) - RECOMMENDED                    │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [4]  Service Examples     → python main.py service              │")
    print("│  [5]  Streaming Methods    → python main.py service05            │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  HIGH-LEVEL (Sugar API - Simplest)                               │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [6]  Basics (Connection)  → python main.py sugar06              │")
    print("│  [7]  Trading Operations   → python main.py sugar07              │")
    print("│  [8]  Position Management  → python main.py sugar08              │")
    print("│  [9]  History & Profits    → python main.py sugar09              │")
    print("│  [10] Advanced Features    → python main.py sugar10              │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  ORCHESTRATORS (Automated Strategies)                            │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [11] Trailing Stop        → python main.py trailing             │")
    print("│  [12] Position Scaler      → python main.py scaler               │")
    print("│  [13] Grid Trading         → python main.py grid                 │")
    print("│  [14] Risk Manager         → python main.py risk                 │")
    print("│  [15] Portfolio Rebalancer → python main.py rebalancer           │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  PRESETS & TOOLS                                                 │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [16] Protobuf Inspector   → python main.py inspect              │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  USER CODE SANDBOX                                               │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [17] User Code Sandbox    → python main.py usercode             │")
    print("├──────────────────────────────────────────────────────────────────┤")
    print("│  [0]  EXIT                                                       │")
    print("└──────────────────────────────────────────────────────────────────┘")
    print()

    choice = input("Enter your choice: ").strip()
    print()
    return choice


async def execute_command(command: str) -> tuple[bool, Exception | None]:
    """
    Execute demo based on command.

    Parameters:
        command: Command string from menu or CLI

    Returns:
        Tuple of (exit_requested, error)
    """
    command = command.lower().strip()

    # ═════════════════════════════════════════════════════════════
    # LOW-LEVEL EXAMPLES
    # ═════════════════════════════════════════════════════════════
    if command in ["1", "lowlevel01", "general"]:
        if demo_01:
            try:
                await demo_01.run_general_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    elif command in ["2", "lowlevel02", "trading"]:
        if demo_02:
            try:
                await demo_02.run_trading_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    elif command in ["3", "lowlevel03", "streaming", "stream"]:
        if demo_03:
            try:
                await demo_03.run_streaming_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    # ═════════════════════════════════════════════════════════════
    # MID-LEVEL (SERVICE)
    # ═════════════════════════════════════════════════════════════
    elif command in ["4", "service", "mid"]:
        if demo_04:
            try:
                await demo_04.main()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    elif command in ["5", "service05", "servicestreaming"]:
        if demo_05:
            try:
                await demo_05.main()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    # ═════════════════════════════════════════════════════════════
    # HIGH-LEVEL (SUGAR)
    # ═════════════════════════════════════════════════════════════
    elif command in ["6", "sugar06", "sugarbasics", "basics"]:
        demo_06 = import_demo_module('3_sugar', '06_sugar_basics.py')
        if demo_06:
            try:
                await demo_06.run_sugar_basics_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    elif command in ["7", "sugar07", "sugartrading"]:
        demo_07 = import_demo_module('3_sugar', '07_sugar_trading.py')
        if demo_07:
            try:
                await demo_07.run_sugar_trading_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Demo module not found")
            return False, None

    elif command in ["8", "sugar08", "sugarpositions", "positions"]:
        demo_08 = import_demo_module('3_sugar', '08_sugar_positions.py')
        if demo_08:
            try:
                await demo_08.run_sugar_positions_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Demo module not found")
            return False, None

    elif command in ["9", "sugar09", "sugarhistory", "history"]:
        demo_09 = import_demo_module('3_sugar', '09_sugar_history.py')
        if demo_09:
            try:
                await demo_09.run_sugar_history_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Demo module not found")
            return False, None

    elif command in ["10", "sugar10", "sugaradvanced", "advanced"]:
        demo_10 = import_demo_module('3_sugar', '10_sugar_advanced.py')
        if demo_10:
            try:
                await demo_10.run_sugar_advanced_demo()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Demo module not found")
            return False, None

    # ═════════════════════════════════════════════════════════════
    # ORCHESTRATORS
    # ═════════════════════════════════════════════════════════════
    elif command in ["11", "trailing", "trailingstop"]:
        if orchestrator_11:
            try:
                await orchestrator_11.main()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Trailing Stop orchestrator module not found")
            return False, None

    elif command in ["12", "scaler", "positionscaler"]:
        if orchestrator_12:
            try:
                await orchestrator_12.main()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("❌ Position Scaler orchestrator module not found")
            return False, None

    elif command in ["13", "grid", "gridtrading"]:
        if orchestrator_13:
            try:
                await orchestrator_13.main()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Grid Trading orchestrator module not found")
            return False, None

    elif command in ["14", "risk", "riskmanager"]:
        if orchestrator_14:
            try:
                await orchestrator_14.run_risk_manager_example()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Risk Manager orchestrator module not found")
            return False, None

    elif command in ["15", "rebalancer", "portfolio"]:
        if orchestrator_15:
            try:
                await orchestrator_15.main()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Portfolio Rebalancer orchestrator module not found")
            return False, None

    # ═════════════════════════════════════════════════════════════
    # PRESETS & TOOLS
    # ═════════════════════════════════════════════════════════════
    elif command in ["16", "inspect", "inspector", "proto"]:
        if inspector_tool:
            try:
                inspector_tool.run_protobuf_inspector()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Protobuf Inspector module not found")
            return False, None

    elif command in ["17", "usercode", "user", "sandbox", "custom"]:
        if usercode_demo:
            try:
                await usercode_demo.run_user_code()
                return False, None
            except Exception as e:
                return False, e
        else:
            print("[X] Usercode module not found")
            return False, None

    # ═════════════════════════════════════════════════════════════
    # EXIT
    # ═════════════════════════════════════════════════════════════
    elif command in ["0", "x", "exit", "quit"]:
        return True, None

    # ═════════════════════════════════════════════════════════════
    # INVALID COMMAND
    # ═════════════════════════════════════════════════════════════
    else:
        print(f"\n❌ Invalid command: {command}")
        print("Valid commands: 1-17, 0 (exit)")
        print("Or use keywords:")
        print("  Low-level:      lowlevel01, lowlevel02, lowlevel03")
        print("  Service:        service, service05")
        print("  Sugar:          sugar06, sugar07, sugar08, sugar09, sugar10")
        print("  Orchestrators:  trailing, scaler, grid, risk, rebalancer")
        print("  Tools:          inspect")
        print("  Usercode:       usercode, sandbox")
        return False, None


async def main_loop():
    """Main application loop"""
    while True:
        # Get command from CLI args or interactive menu
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
        else:
            print_banner()
            command = show_menu()

        # Execute command
        exit_requested, error = await execute_command(command)

        # Handle errors
        if error:
            print("\n╔════════════════════════════════════════════════════════════╗")
            print("║                    ERROR OCCURRED                          ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print(f"\nError: {error}")
            print(f"Error type: {type(error).__name__}")
            if hasattr(error, '__traceback__'):
                print("\nTraceback:")
                traceback.print_exception(type(error), error, error.__traceback__)

            if len(sys.argv) > 1:
                sys.exit(1)

            input("\nPress Enter to return to menu...")
            continue

        # Handle exit
        if exit_requested:
            print("\nExiting...")
            return

        # If CLI mode, exit after completion
        if len(sys.argv) > 1:
            print("\n\nPress Enter to exit...")
            input()
            return

        # Interactive menu - ask for next action
        print()
        print("┌──────────────────────────────────────────────────────────────┐")
        print("│  [M] Return to Main Menu  |  [0] Exit                        │")
        print("└──────────────────────────────────────────────────────────────┘")
        next_action = input("\nYour choice: ").strip().lower()
        print()

        if next_action in ["0", "exit", "quit"]:
            print("Exiting...")
            return


def main():
    """Entry point"""
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
