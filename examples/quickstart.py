import asyncio
from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown, SYMBOL
from .common.utils import title, safe_async
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI  # ← enums BID/ASK

async def main():
    acc = await connect()
    try:
        title("Quick Start")

        # Brief account summary
        await safe_async("account_summary", acc.account_summary)

        # Make sure the symbol is in Market Watch
        await safe_async("symbol_select", acc.symbol_select, SYMBOL, True)

        # BID/ASK via correct enums
        bid = await safe_async("symbol_info_double(BID)", acc.symbol_info_double, SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_BID)
        ask = await safe_async("symbol_info_double(ASK)", acc.symbol_info_double, SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_ASK)

        # Small spread withdrawal (if prices are received)
        try:
            if isinstance(bid, (int, float)) and isinstance(ask, (int, float)):
                print("spread:", float(ask) - float(bid))
        except Exception:
            pass

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.quickstart

"""
    Example: Quick Start (account snapshot + BID/ASK + spread)
    ==========================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session to the MT5 bridge; must be closed with `shutdown()`. |
    | Heading | `title("Quick Start")` | Cosmetic section header in console/log. |
    | Account summary | `safe_async("account_summary", acc.account_summary)` | Quick health-check: login, equity, currency, etc. Helps verify connectivity/auth. |
    | Ensure symbol | `symbol_select(SYMBOL, True)` | Puts the symbol into Market Watch so price properties become available. |
    | Prices | `symbol_info_double(SYMBOL, SYMBOL_BID/ASK)` | Reads BID/ASK using **enum** values from `mt5_term_api_market_info_pb2`. |
    | Spread | `print(float(ask) - float(bid))` | Simple spread calculation if both numbers are available. |
    | Cleanup | `await shutdown(acc)` | Always close the session, even on errors. |

    RPCs used (with params)
    -----------------------
    - `account_summary()` → aggregated account info (login, balance/equity, currency, leverage, etc.)
    - `symbol_select(symbol: str, enable: bool)` → ensure symbol is visible/selected
    - `symbol_info_double(symbol: str, property: SymbolInfoDoubleProperty)` →
        * `MI.SymbolInfoDoubleProperty.SYMBOL_BID`
        * `MI.SymbolInfoDoubleProperty.SYMBOL_ASK`

    Enums / modules
    ---------------
    - `from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI`
      Use `MI.SymbolInfoDoubleProperty.*` constants (not strings) when requesting BID/ASK.

    Notes on return types
    ---------------------
    - `safe_async(...)` returns whatever the wrapped method returns in your build.
      In most builds `symbol_info_double(...)` returns a **float** directly; in some it may return a message with a `.value` field.
      The example prints the spread only if both `bid` and `ask` are numeric.
      (If your build returns messages, read `bid.value` / `ask.value` before computing the spread.)

    Environment
    -----------
    - `SYMBOL` is imported from your env/helper (`.common.env`); set it to a tradable instrument (e.g., `EURUSD`, `XAUUSD`).
    - Make sure the account has market data for the symbol; otherwise BID/ASK may be unavailable.

    Typical output
    --------------
    > account_summary()
    "account_login: ... account_equity: ... account_currency: \"USD\" ..."
    > symbol_select('EURUSD', True)
    "success: true"
    > symbol_info_double(BID/ASK)
    spread: 0.00012

    Edge cases
    ----------
    - If `symbol_select` fails or the symbol is not streamed by your provider, BID/ASK may be missing.
    - If your server time is skewed and you use server-side deadlines elsewhere, prefer client-side timeouts (not used here).

    How to run
    ----------
    From project root:
      `python -m examples.quick_start`
    Or via your CLI (if present):
      `python -m examples.cli run quick_start`
    """