import asyncio
from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title, safe_async


async def main():
    """
    Example: Account Information + Ratios (summary-only)
    ====================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async client to the MT5 bridge. Must be closed with `shutdown()`. |
    | Heading | `title("Account Information + ratios")` | Cosmetic section header in console/log. |
    | Summary | `safe_async("account_summary", acc.account_summary)` | One RPC returns account fields (login, balance, equity, currency, leverage, etc.). Wrapped to avoid hard fails. |
    | Parse   | Read `account_*` fields from the summary | Use payload names you actually receive (e.g., `account_equity`), with `getattr(..., default)` for safety. |
    | Ratios  | Compute `free_margin_ratio`, `drawdown` | Guarded against division by zero; falls back to `equity - margin` if `account_free_margin` is missing. |
    | Print   | Pretty-print essentials | Shows login, equity with currency, leverage, UTC offset (minutes), then ratios line. |
    | Cleanup | `await shutdown(acc)` | Ensures session is closed even on exceptions. |

    Fields used from `account_summary` (exact payload names)
    --------------------------------------------------------
    - `account_login: int`
    - `account_balance: float`
    - `account_equity: float`
    - `account_margin: float` (may be 0 or missing on some servers)
    - `account_free_margin: float` (optional; fallback = equity - margin)
    - `account_currency: str`
    - `account_leverage: int`
    - `server_time.seconds: int` (unix epoch)
    - `utc_timezone_server_time_shift_minutes: int` (server_time - UTC, minutes; can be negative)

    Computed metrics (this example)
    -------------------------------
    - `free_margin_ratio = (free_margin / equity) * 100`  if `equity > 0` else `0`
    - `drawdown          = ((balance - equity) / balance) * 100`  if `balance > 0` else `0`

    RPCs used
    ---------
    - `account_summary()` only.  
      (We deliberately avoid `account_info_*` calls here to stay compatible with the current package build.)

    Error handling
    --------------
    - `safe_async(label, func, *args)` catches/logs exceptions and returns `None` on failure.
    - Division-by-zero is prevented by checks on `equity` and `balance`.
    - Missing fields fall back via `getattr(..., default)`.

    Typical output
    --------------
    > account_summary()
    login=95591860 | equity=99969.86 USD | lev=1:100 | tz_shift_min=-2436
    free_margin_ratio: 72.35% | drawdown: 0.02%

    How to run
    ----------
    From the project root:
    `python -m examples.account_info`

    Requirements
    ------------
    - Valid connection settings in environment (see `.env` / your `connect()` impl).
    - Active session on the target server with permissions to query account info.
    """

    acc = await connect()
    try:
        title("Account Information + ratios")

        # One-shot snapshot of account figures (safe wrapper logs errors and returns None on failure)
        s = await safe_async("account_summary", acc.account_summary)

        if s:
            # Field names follow the payload you receive (account_*)
            balance = float(getattr(s, "account_balance", 0.0))
            equity  = float(getattr(s, "account_equity",  0.0))
            margin  = float(getattr(s, "account_margin",  0.0))
            free    = float(getattr(s, "account_free_margin", equity - margin))

            login     = getattr(s, "account_login", 0)
            currency  = getattr(s, "account_currency", "")
            leverage  = getattr(s, "account_leverage", 0)
            tz_shift  = getattr(s, "utc_timezone_server_time_shift_minutes", 0)

            # Ratios with divide-by-zero guards
            free_ratio = (free / equity * 100) if equity else 0.0
            drawdown   = ((balance - equity) / balance * 100) if balance else 0.0

            print(f"login={login} | equity={equity:.2f} {currency} | lev=1:{leverage} | tz_shift_min={tz_shift}")
            print(f"free_margin_ratio: {free_ratio:.2f}% | drawdown: {drawdown:.2f}%")
        else:
            print("account_summary() returned no data")

    finally:
        # Always close the connection, even if a prior step failed
        await shutdown(acc)


if __name__ == "__main__":
    asyncio.run(main())

# python -m examples.account_info
