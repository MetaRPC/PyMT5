"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/cli.py — CLI for listing and running examples                   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                      ║
║   Command-line interface (CLI) to list available examples and run one by name.║
║                                                                               ║
║ Exposes:                                                                      ║
║   1) list — prints all available example names.                               ║
║   2) run  — runs a selected example (async) by name.                          ║
║   3) run_entry(entry) — dynamically imports the target and RETURNS its main   ║
║      coroutine/function (execution happens in main()).                        ║
║                                                                               ║
║ Strategy:                                                                     ║
║   1) Parse CLI args: `list` or `run <name>`.                                  ║
║   2) For `list`: print keys from EXAMPLES.                                    ║
║   3) For `run`: import the target via `run_entry`, then `asyncio.run(coro())`.║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
import argparse, asyncio
from .common.pb2_shim import apply_patch   
apply_patch()



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
  mod = __import__(mod_name, fromlist=[func_name])
  return getattr(mod, func_name) 

def main():
  p = argparse.ArgumentParser(prog="examples", description="MT5Account examples runner")
  sub = p.add_subparsers(dest="cmd")
  sub.add_parser("list", help="List available examples")
  run_p = sub.add_parser("run", help="Run one example")
  run_p.add_argument("name", choices=EXAMPLES.keys())
  args = p.parse_args()

  if args.cmd == "list" or args.cmd is None:
    print("Available examples:")
    for k in EXAMPLES.keys():
      print(" -", k)
    return

  if args.cmd == "run":
    coro = run_entry(EXAMPLES[args.name])
    asyncio.run(coro())

if __name__ == "__main__":
  main()


