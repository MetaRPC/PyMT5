# examples/account_info.py
import asyncio
from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title


async def main():
    # Account summary + simple ratios (direct calls, no wrappers)
    acc = await connect()
    try:
        title("Account Information + ratios")

        s = await acc.account_summary()
        if not s:
            print("account_summary() returned no data")
            return

        # Read fields directly from payload (account_*)
        balance = float(getattr(s, "account_balance", 0.0))
        equity  = float(getattr(s, "account_equity",  0.0))
        margin  = float(getattr(s, "account_margin",  0.0))
        free    = float(getattr(s, "account_free_margin", equity - margin))

        login     = getattr(s, "account_login", 0)
        currency  = getattr(s, "account_currency", "")
        leverage  = getattr(s, "account_leverage", 0)
        tz_shift  = getattr(s, "utc_timezone_server_time_shift_minutes", 0)

        # Ratios with zero-division guards
        free_ratio = (free / equity * 100) if equity else 0.0
        drawdown   = ((balance - equity) / balance * 100) if balance else 0.0

        print(f"login={login} | equity={equity:.2f} {currency} | lev=1:{leverage} | tz_shift_min={tz_shift}")
        print(f"free_margin_ratio: {free_ratio:.2f}% | drawdown: {drawdown:.2f}%")

    finally:
        await shutdown(acc)


if __name__ == "__main__":
    asyncio.run(main())


    # python -m examples.account_info
    

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/account_info.py — Account summary & ratios (direct gRPC)       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Fetch a single account_summary over gRPC and print key fields plus two     ║
║   derived metrics (free_margin_ratio, drawdown). No wrappers used.           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Flow (happy path)                                                            ║
║   1) connect()            → create MT5 gRPC session                          ║
║   2) account_summary()    → receive account_* fields                         ║
║   3) compute ratios       → safe math with zero-division guards              ║
║   4) print                → compact, human-readable one-liners               ║
║   5) shutdown()           → always close the session                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Payload fields used                                                          ║
║   account_login : int                                                        ║
║   account_balance : float                                                    ║
║   account_equity  : float                                                    ║
║   account_margin  : float                                                    ║
║   account_free_margin : float   (fallback = equity - margin)                 ║
║   account_currency : str                                                     ║
║   account_leverage : int                                                     ║
║   utc_timezone_server_time_shift_minutes : int                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Derived metrics                                                              ║
║   free_margin_ratio = (free_margin / equity) * 100   if equity  > 0 else 0   ║
║   drawdown          = (balance - equity) / balance * 100  if balance > 0     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers / utilities                                                          ║
║   connect(), shutdown()  — from examples/common/env.py                       ║
║   title()                — console section header                            ║
║   pb2_shim.apply_patch() — early pb2 aliasing for mixed builds               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   From project root:  python -m examples.account_info                        ║
║   Ensure .env / environment has valid connection parameters.                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

