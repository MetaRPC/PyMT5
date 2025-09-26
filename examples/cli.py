# examples/cli.py
import argparse
import asyncio
import importlib

# Ensure env side-effects: sys.path + pb2 shim + MT5Account imports
from .common import env as _env 

EXAMPLES = {
    "quickstart": "examples.quickstart:main",
    "account_info": "examples.account_info:main",
    "symbols_market": "examples.symbols_market:main",
    "market_book": "examples.market_book:main",
    "orders_history": "examples.orders_history:main",
    "trading_safe": "examples.trading_safe:main",
    "streaming": "examples.streaming:main",
    "streaming_trade_events": "examples.streaming_trade_events:main",
    "streaming_trade_tx": "examples.streaming_trade_tx:main",
    "streaming_position_profit": "examples.streaming_position_profit:main",
    "streaming_positions_tickets": "examples.streaming_positions_tickets:main",
    "positions_history": "examples.positions_history:main",
    "trading_basics": "examples.trading_basics:main",
    "opened_snapshot": "examples.opened_snapshot:main",
}

def run_entry(entry: str):
    mod_name, func_name = entry.split(":")
    mod = importlib.import_module(mod_name)
    return getattr(mod, func_name)

def main():
    p = argparse.ArgumentParser(prog="examples", description="MT5Account examples runner")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List available examples")
    run_p = sub.add_parser("run", help="Run one example")
    run_p.add_argument("name", choices=EXAMPLES.keys())

    args = p.parse_args()

    if args.cmd in (None, "list"):
        print("Available examples:")
        for k in sorted(EXAMPLES.keys()):
            print(" ", k)
        return

    if args.cmd == "run":
        coro = run_entry(EXAMPLES[args.name])
        asyncio.run(coro())
        return

    p.print_help()

if __name__ == "__main__":
    main()
    """
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/cli.py — unified runner for example modules                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Provide a single command-line entry point to discover and run any example  ║
║   in the repo. Ensures environment side-effects (sys.path, pb2 shim, MT5     ║
║   adapter imports) before executing the selected example.                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (flow)                                                          ║
║   1) `from .common import env as _env` — import for side-effects only:       ║
║      • extends PYTHONPATH (root, package/, ext/)                             ║
║      • applies pb2 shim/aliases                                              ║
║      • selects MT5AccountEx or base MT5Account                               ║
║   2) Declares `EXAMPLES` mapping: name → "module_path:callable".             ║
║   3) Parses CLI:                                                             ║
║      • `list` — prints available example names                               ║
║      • `run <name>` — dynamically imports module and calls `main()`          ║
║   4) Resolves entry via `importlib`, calls it with `asyncio.run(...)`.       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Public CLI                                                                   ║
║   • List:  `python -m examples.cli list`                                     ║
║   • Run :  `python -m examples.cli run quickstart`                           ║
║            (names come from the `EXAMPLES` mapping)                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Contract for examples                                                        ║
║   • Target referenced by `"module:func"` must be an **async** callable:      ║
║       `async def main(): ...`                                                ║
║   • The module must be importable from the project root (env has set paths). ║
║   • Any required env variables/.env are the example’s responsibility.        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Extending                                                                    ║
║   1) Create a new example module exporting `async def main()`.               ║
║   2) Add an entry to `EXAMPLES`, e.g.:                                       ║
║        "my_demo": "examples.my_demo:main",                                   ║
║   3) Run it: `python -m examples.cli run my_demo`.                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Error handling & UX                                                          ║
║   • Unknown example names are rejected by argparse `choices`.                ║
║   • Exceptions inside examples propagate to the console (useful for debug).  ║
║   • Import-time side-effects ensure pb2 shims are applied before use.        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Dependencies                                                                 ║
║   • stdlib: argparse, asyncio, importlib                                     ║
║   • local: examples/common/env (side-effects only)                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Notes                                                                        ║
║   • If an example isn’t async, wrap it: `asyncio.to_thread(sync_main)` or    ║
║     refactor to `async def main()`.                                          ║
║   • Keep names in `EXAMPLES` human-friendly; they appear in `list`.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""