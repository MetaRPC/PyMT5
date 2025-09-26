import asyncio
from .common.env import connect, shutdown, SYMBOL
from .common.utils import title, pprint
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI  # enums BID/ASK

async def main():
    acc = await connect()
    try:
        title("Quick Start")

        # Account summary
        summary = await acc.account_summary()
        if isinstance(summary, str):
            print(summary)
        else:
            pprint(summary)

        # Ensure the symbol is in Market Watch
        await acc.symbol_select(SYMBOL, True)

        # BID/ASK via enums (direct calls)
        bid = await acc.symbol_info_double(SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_BID)
        ask = await acc.symbol_info_double(SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_ASK)

        # Show raw values
        print("BID raw:", bid)
        print("ASK raw:", ask)

        # Robust float coercion
        def to_float(x):
            try:
                return float(x)
            except Exception:
                for attr in ("value", "data", "requestedValue", "double", "price", "bid", "ask"):
                    v = getattr(x, attr, None)
                    if v is None:
                        continue
                    try:
                        return float(v)
                    except Exception:
                        pass
                return None

        b = to_float(bid)
        a = to_float(ask)
        if b is not None and a is not None:
            print(f"BID: {b}  ASK: {a}  spread: {a - b}")
        else:
            # Fallback to tick if doubles are not numeric
            tick = await acc.symbol_info_tick(SYMBOL)
            print("tick raw:", tick)
            tb = to_float(getattr(tick, "bid", None))
            ta = to_float(getattr(tick, "ask", None))
            if tb is not None and ta is not None:
                print(f"BID(tick): {tb}  ASK(tick): {ta}  spread: {ta - tb}")
            else:
                print("Could not read BID/ASK from both symbol_info_double and tick.")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.quickstart


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/quickstart.py — minimal quick start (summary + BID/ASK)        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Show a tiny, direct-call example that:                                     ║
║     • prints the account summary,                                            ║
║     • ensures a symbol is in Market Watch,                                   ║
║     • fetches BID/ASK via proper enums,                                      ║
║     • robustly coerces values to floats, with a fallback to tick snapshot.   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (happy path)                                                    ║
║   1) `acc = await connect()` — open async client to the MT5 bridge.          ║
║   2) `title("Quick Start")` — cosmetic section header.                       ║
║   3) `summary = await acc.account_summary()` — fetch account fields;         ║
║      pretty-print if it’s a structured payload (`pprint(summary)`),          ║
║      otherwise print the raw string.                                         ║
║   4) `await acc.symbol_select(SYMBOL, True)` — ensure the symbol is visible. ║
║   5) `symbol_info_double(..., BID/ASK)` using                                ║
║      `MI.SymbolInfoDoubleProperty.SYMBOL_BID/ASK`.                           ║
║   6) Print raw values for diagnostics, then coerce to floats; if coercion    ║
║      fails, fall back to `symbol_info_tick()` and compute spread from tick.  ║
║   7) `await shutdown(acc)` — graceful cleanup even on errors.                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ RPCs used                                                                    ║
║   • `account_summary()`                                                      ║
║   • `symbol_select(symbol, True)`                                            ║
║   • `symbol_info_double(symbol, BID)`                                        ║
║   • `symbol_info_double(symbol, ASK)`                                        ║
║   • `symbol_info_tick(symbol)` (fallback when doubles aren’t numeric)        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers / imports                                                            ║
║   • `connect`, `shutdown`, `SYMBOL` — from `examples/common/env.py`          ║
║   • `title`, `pprint` — from `examples/common/utils.py`                      ║
║   • Enums `MI.SymbolInfoDoubleProperty` (BID/ASK)                            ║
║   • Local `to_float(x)` helper tries common attributes:                      ║
║     `value`, `data`, `requestedValue`, `double`, `price`, `bid`, `ask`.      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                       ║
║   • Pretty account summary (login, equity, leverage, currency, etc.).        ║
║   • `BID raw:` / `ASK raw:` diagnostics.                                     ║
║   • Either: `BID: <b>  ASK: <a>  spread: <a-b>`                              ║
║     or, on fallback: `BID(tick): …  ASK(tick): …  spread: …`.                ║
║   • If both paths fail → prints an explanatory message.                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Robustness notes                                                             ║
║   • Works across pb2 builds where doubles/ticks may arrive as wrapped types. ║
║   • Uses direct calls (no custom wrappers), so the data flow is transparent. ║
║   • If BID and ASK are identical/old, spread may be zero.                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Environment                                                                  ║
║   • Connection settings via `.env` / env vars, e.g.:                         ║
║       `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`, `GRPC_SERVER`               ║
║       `MT5_SYMBOL` (default: EURUSD)                                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   • From project root: `python -m examples.quickstart`                       ║
║   • Or via CLI:   `python -m examples.cli run quickstart`                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""