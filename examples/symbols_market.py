import asyncio
from datetime import datetime, timezone

from .common.pb2_shim import apply_patch
apply_patch() 

from .common.env import connect, shutdown, SYMBOL, VOLUME
from .common.utils import title, safe_async

# pb2 modules/elements
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI

SDouble = MI.SymbolInfoDoubleProperty
SInt    = MI.SymbolInfoIntegerProperty
SStr    = MI.SymbolInfoStringProperty


def _fmt_ts(sec: int | None) -> str:
    if sec is None:
        sec = 0
    sec = int(sec)
    # 86400 seconds = "24:00:00" to avoid confusion with "00:00:00"
    if sec % 86400 == 0 and sec != 0:
        return "24:00:00"
    return datetime.fromtimestamp(sec, tz=timezone.utc).strftime("%H:%M:%S")


def _print_symbol_infos_compact(resp, limit: int = 10) -> None:
    """Compact output of symbol_params_many: maximum number of records and only key fields."""
    infos = getattr(resp, "symbol_infos", None)
    if not infos:
        print("symbol_params_many: empty or the server did not return the list.")
        return
    print(f"symbol_params_many: total={len(infos)} (showing the first {min(limit, len(infos))})")
    for i, info in enumerate(infos[:limit], start=1):
        name            = getattr(info, "name", "")
        digits          = getattr(info, "digits", None)
        currency_base   = getattr(info, "currency_base", "")
        currency_profit = getattr(info, "currency_profit", "")
        trade_mode      = getattr(info, "trade_mode", "")
        sector_name     = getattr(info, "sector_name", "")
        industry_name   = getattr(info, "industry_name", "")
        print(f"  #{i}: {name} | digits={digits} | {currency_base}/{currency_profit} | mode={trade_mode} | {sector_name} / {industry_name}")


async def main():
    acc = await connect()

    # ── Monkey-patch: fixing field names in pb2 queries (snake_case) ──────
    async def _symbol_info_margin_rate(self, symbol, order_type, deadline=None, cancellation_event=None):
        req = AH.SymbolInfoMarginRateRequest(symbol=symbol, order_type=order_type)
        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoMarginRate(
                req, metadata=headers, timeout=max(timeout, 0) if timeout else None
            )
        res = await self.execute_with_reconnect(
            grpc_call=grpc_call, error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline, cancellation_event=cancellation_event
        )
        return res.data

    async def _symbol_info_session_quote(self, symbol, day_of_week, session_index, deadline=None, cancellation_event=None):
        req = AH.SymbolInfoSessionQuoteRequest(symbol=symbol, day_of_week=day_of_week, session_index=session_index)
        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoSessionQuote(
                req, metadata=headers, timeout=max(timeout, 0) if timeout else None
            )
        res = await self.execute_with_reconnect(
            grpc_call=grpc_call, error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline, cancellation_event=cancellation_event
        )
        return res.data

    async def _symbol_info_session_trade(self, symbol, day_of_week, session_index, deadline=None, cancellation_event=None):
        req = AH.SymbolInfoSessionTradeRequest(symbol=symbol, day_of_week=day_of_week, session_index=session_index)
        async def grpc_call(headers):
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            return await self.market_info_client.SymbolInfoSessionTrade(
                req, metadata=headers, timeout=max(timeout, 0) if timeout else None
            )
        res = await self.execute_with_reconnect(
            grpc_call=grpc_call, error_selector=lambda r: getattr(r, "error", None),
            deadline=deadline, cancellation_event=cancellation_event
        )
        return res.data

    acc.symbol_info_margin_rate   = _symbol_info_margin_rate.__get__(acc, type(acc))
    acc.symbol_info_session_quote = _symbol_info_session_quote.__get__(acc, type(acc))
    acc.symbol_info_session_trade = _symbol_info_session_trade.__get__(acc, type(acc))
    # ───────────────────────────────────────────────────────────────────────────

    try:
        title("Symbols & Market")

        # 1) Select a symbol
        await safe_async("symbol_select", acc.symbol_select, SYMBOL, True)

        # 2) BID/ASK
        bid = await safe_async("symbol_info_double(BID)", acc.symbol_info_double, SYMBOL, SDouble.SYMBOL_BID)
        ask = await safe_async("symbol_info_double(ASK)", acc.symbol_info_double, SYMBOL, SDouble.SYMBOL_ASK)
        if isinstance(bid, (float, int)) and isinstance(ask, (float, int)):
            print("spread:", float(ask) - float(bid))

        # 3) Tick-cost per volume
        await safe_async("tick_value_with_size", acc.tick_value_with_size, [SYMBOL])


        # 4) Total characters / name by index
        await safe_async("symbols_total", acc.symbols_total, False)
        await safe_async("symbol_name(0)", acc.symbol_name, 0, False)

        # 5) Tick ​​info/sync
        await safe_async("symbol_info_tick", acc.symbol_info_tick, SYMBOL)
        await safe_async("symbol_is_synchronized", acc.symbol_is_synchronized, SYMBOL)

        # 6) Parameters for multiple characters (compact)
        resp_many = await acc.symbol_params_many([SYMBOL, "XAUUSD"])
        _print_symbol_infos_compact(resp_many, limit=10)

        # 7) Marginal rates (ENUM_ORDER_TYPE → ORDER_TYPE_BUY/SELL/…)
        mr = await safe_async(
            "symbol_info_margin_rate",
            acc.symbol_info_margin_rate,
            SYMBOL, MI.ENUM_ORDER_TYPE.ORDER_TYPE_BUY
        )
        if mr:
            im = getattr(mr, "initial_margin_rate", None)
            mm = getattr(mr, "maintenance_margin_rate", None)
            hm = getattr(mr, "hedged_margin_rate", None)
            print(f"margin_rates: initial={im!r}, maintenance={mm!r}, hedged={hm!r}")

        # 8)Sessions (DayOfWeek + session_index) - human readable text
        sq = await safe_async("symbol_info_session_quote", acc.symbol_info_session_quote, SYMBOL, MI.DayOfWeek.MONDAY, 0)
        if sq:
            start = getattr(getattr(sq, "from_", None), "seconds", None)
            end   = getattr(getattr(sq, "to", None), "seconds", None)
            print(f"quote_session[Mon,#0]: {_fmt_ts(start)} → {_fmt_ts(end)} UTC")

        st = await safe_async("symbol_info_session_trade", acc.symbol_info_session_trade, SYMBOL, MI.DayOfWeek.MONDAY, 0)
        if st:
            start = getattr(getattr(st, "from_", None), "seconds", None)
            end   = getattr(getattr(st, "to", None), "seconds", None)
            print(f"trade_session[Mon,#0]: {_fmt_ts(start)} → {_fmt_ts(end)} UTC")

        # 9) Other: existence, integer/string properties
        await safe_async("symbol_exist", acc.symbol_exist, SYMBOL)
        await safe_async("symbol_info_integer(DIGITS)", acc.symbol_info_integer, SYMBOL, SInt.SYMBOL_DIGITS)
        await safe_async("symbol_info_string(CURRENCY_BASE)", acc.symbol_info_string, SYMBOL, SStr.SYMBOL_CURRENCY_BASE)

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.cli run symbols_market


"""
    Example: Symbols & Market — quotes, params, sessions, margins
    =============================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session to the MT5 bridge; close with `shutdown()`. |
    | Heading | `title("Symbols & Market")` | Cosmetic header. |
    | Monkey-patch | Bind `symbol_info_margin_rate/session_quote/session_trade` | Normalizes pb2 field names (snake/camel) and derives client timeouts from `deadline`. |
    | Select | `symbol_select(SYMBOL, True)` | Ensures the symbol is in Market Watch. |
    | Prices | `symbol_info_double(..., SYMBOL_BID/ASK)` → print spread | Uses **enum** values from `mt5_term_api_market_info_pb2` (not strings). |
    | Tick value | `tick_value_with_size([SYMBOL])` | Quick cost-per-tick probe for the symbol list. |
    | Catalog | `symbols_total(False)` + `symbol_name(0, False)` | Demonstrates total instruments and first symbol name. |
    | Tick/sync | `symbol_info_tick(SYMBOL)` + `symbol_is_synchronized(SYMBOL)` | Health check: last/bid/ask snapshot + feed sync status. |
    | Bulk params | `symbol_params_many([SYMBOL, "XAUUSD"])` → compact print | Shows key fields (digits, currencies, trade mode, sector/industry). |
    | Margin rates | `symbol_info_margin_rate(SYMBOL, ORDER_TYPE_BUY)` | Prints initial/maintenance/hedged rates if provided. |
    | Sessions | `symbol_info_session_quote/trade(..., DayOfWeek.MONDAY, 0)` | Human-readable session window `HH:MM:SS` in UTC. |
    | Misc | `symbol_exist`, `symbol_info_integer(DIGITS)`, `symbol_info_string(CURRENCY_BASE)` | Typical integer/string properties via enums. |

    Imports & enums
    ---------------
    - `from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH`
    - `from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI`
      - Double: `MI.SymbolInfoDoubleProperty.SYMBOL_BID / SYMBOL_ASK`
      - Integer: `MI.SymbolInfoIntegerProperty.SYMBOL_DIGITS`
      - String:  `MI.SymbolInfoStringProperty.SYMBOL_CURRENCY_BASE`
      - Order type: `MI.ENUM_ORDER_TYPE.ORDER_TYPE_BUY`
      - Day of week: `MI.DayOfWeek.MONDAY`

    Patched RPC wrappers (bound to `acc`)
    -------------------------------------
    - `symbol_info_margin_rate(symbol, order_type, *, deadline=None, cancellation_event=None)`
      - Request: `AH.SymbolInfoMarginRateRequest(symbol=..., order_type=...)`
      - Client-side timeout computed from `deadline` (avoids server-time skew).
      - Returns `res.data` with fields like `initial_margin_rate`, `maintenance_margin_rate`, `hedged_margin_rate`.
    - `symbol_info_session_quote(symbol, day_of_week, session_index, *, deadline=None, ...)`
      - Request: `AH.SymbolInfoSessionQuoteRequest(...)`; output has `from_`/`to` timestamps.
    - `symbol_info_session_trade(symbol, day_of_week, session_index, *, deadline=None, ...)`
      - Request: `AH.SymbolInfoSessionTradeRequest(...)`; output has `from_`/`to`.

    Printer helpers
    ---------------
    - `_fmt_ts(sec)` — formats seconds as `HH:MM:SS` (UTC); prints `24:00:00` for exact 24h boundaries.
    - `_print_symbol_infos_compact(resp, limit)` — prints first N entries from `resp.symbol_infos` with selected fields.

    Output (typical)
    ----------------
    > symbol_select('EURUSD', True)
    > symbol_info_double(BID/ASK)
    spread: 0.00012
    symbol_params_many: total=… (first …)
      #1: EURUSD | digits=5 | USD/USD | mode=... | Forex / Majors
    margin_rates: initial=..., maintenance=..., hedged=...
    quote_session[Mon,#0]: 00:00:00 → 24:00:00 UTC
    trade_session[Mon,#0]: 00:00:00 → 24:00:00 UTC

    Notes & edge cases
    ------------------
    - Some providers do not expose margin/session info for all symbols; corresponding calls may return empty `data`.
    - Use **enums** from `MI` for property selectors; builds that accept strings are not guaranteed.
    - If server time is skewed, prefer client-side timeouts (as in patched methods) over server-side deadlines.

    How to run
    ----------
    From project root:
      `python -m examples.symbols_and_market`
    Or via CLI (if present):
      `python -m examples.cli run symbols_and_market`

    Environment
    -----------
    - `SYMBOL` and (optionally) `VOLUME` come from `.common.env`. Ensure `SYMBOL` is tradable and streamed by your provider.
    """



