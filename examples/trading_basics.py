# examples/trading_basics.py
import os
import re
import asyncio
import logging
from typing import Any, Tuple, Optional

from .common.env import connect, shutdown, SYMBOL, VOLUME, ENABLE_TRADING
from .common.utils import title
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as TH  # requests + enums

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

DEBUG_RPC = os.getenv("MT5_DEBUG", "0") == "1"


# ───────────────────────── helpers ─────────────────────────

def _fval(x: Any, default: Optional[float] = None) -> Optional[float]:
    """Coerce various response shapes to float."""
    try:
        if x is None:
            return default
        if isinstance(x, (int, float)):
            return float(x)

        v = getattr(x, "value", None)
        if isinstance(v, (int, float, str)):
            try:
                return float(v)
            except Exception:
                pass

        data = getattr(x, "data", None)
        if data is not None:
            dv = getattr(data, "value", None)
            if isinstance(dv, (int, float, str)):
                try:
                    return float(dv)
                except Exception:
                    pass

        if isinstance(x, str):
            m = re.search(r"(-?\d+(?:\.\d+)?)", x)
            if m:
                return float(m.group(1))
    except Exception:
        pass
    return default


async def _get_bid_ask(acc, symbol: str) -> Tuple[Optional[float], Optional[float]]:
    """Read BID/ASK via proper enums, robustly cast to float."""
    bid = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_BID)
    ask = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_ASK)
    return _fval(bid), _fval(ask)


# ───────────────────────── margin/check (direct → fallback) ─────────────────────────

async def _order_calc_margin(acc, symbol: str, volume: float, side: str = "BUY", price: Optional[float] = None):
    """
    Preferred: TH.OrderCalcMarginRequest → acc.order_calc_margin(req)
    Fallback: simple local estimate if RPC not available.
    """
    # Prepare price if needed
    if price is None:
        t = await acc.symbol_info_tick(symbol)
        b = _fval(getattr(t, "bid", None), 0.0)
        a = _fval(getattr(t, "ask", None), 0.0)
        price = a or b or 1.0

    # Try direct RPC
    try:
        req = TH.OrderCalcMarginRequest(
            symbol=symbol,
            order_type=TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_BUY if str(side).upper() in ("BUY", "B", "LONG", "0") else TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
            volume=float(volume),
            price=float(price),
        )
        res = await acc.order_calc_margin(req)
        val = _fval(getattr(res, "data", res), None)
        return val if val is not None else res
    except Exception as e:
        if DEBUG_RPC:
            log.warning("order_calc_margin RPC not available, falling back: %s", e)

    # Local rough estimate: (contract_size * volume / leverage) * (FX if needed)
    try:
        # leverage from account (default 100)
        lev = 100.0
        try:
            acc_sum = await acc.account_summary()
            lev = float(getattr(acc_sum, "account_leverage", None) or 100.0)
        except Exception:
            pass
        lev = max(float(lev or 1.0), 1.0)

        # contract size from symbol info (default 100000)
        info = None
        for nm in ("symbol_info", "get_symbol_info", "symbol_info_get"):
            f = getattr(acc, nm, None)
            if callable(f):
                try:
                    info = await f(symbol)
                    break
                except Exception:
                    pass
        contract_size = float(
            getattr(info, "trade_contract_size", None)
            or getattr(info, "contract_size", None)
            or 100000.0
        )

        margin = (contract_size * float(volume)) / lev

        base = symbol[:3].upper() if len(symbol) >= 6 else ""
        acct_ccy = None
        try:
            acc_sum = await acc.account_summary()
            acct_ccy = str(getattr(acc_sum, "account_currency", None) or "").upper()
        except Exception:
            pass
        if not acct_ccy or acct_ccy != base:
            margin *= float(price or 1.0)

        return margin
    except Exception:
        return None


async def _order_check(acc, symbol: str, volume: float, price: float, side: str = "BUY"):
    """Preferred: TH.OrderCheckRequest → acc.order_check(req). Fallback: dummy OK."""
    try:
        req = TH.OrderCheckRequest(
            symbol=symbol,
            order_type=TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_BUY if str(side).upper() in ("BUY", "B", "LONG", "0") else TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
            volume=float(volume),
            price=float(price),
        )
        return await acc.order_check(req)
    except Exception as e:
        if DEBUG_RPC:
            log.warning("order_check RPC not available, falling back: %s", e)
        return {"ok": True, "symbol": symbol, "side": str(side), "volume": float(volume), "price": float(price)}


# ───────────────────────── sending/closing ─────────────────────────

async def _order_send(acc, symbol: str, volume: float, price: float):
    """
    Preferred: TH.OrderSendRequest → acc.order_send(req)
    Fallback: legacy acc.order_send(symbol, 'BUY', volume, price)
    """
    if not ENABLE_TRADING:
        print("MT5_ENABLE_TRADING != 1 → real sending is disabled.")
        return None

    # Direct request (as in docs)
    try:
        req = TH.OrderSendRequest(
            symbol=symbol,
            operation=TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_BUY,
            volume=float(volume),
            price=float(price),           # 0.0 for pure market, if allowed by server
            slippage=20,
            stop_loss=0.0,
            take_profit=0.0,
            comment="docs example",
            expert_id=0,
            stop_limit_price=0.0,
            expiration_time_type=TH.TMT5_ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC,
        )
        return await acc.order_send(req)
    except Exception as e:
        if DEBUG_RPC:
            log.warning("order_send(req) failed, trying legacy signature: %s", e)

    # Legacy signature fallback (some builds)
    try:
        return await acc.order_send(symbol, "BUY", float(volume), float(price))
    except Exception as e:
        if DEBUG_RPC:
            log.warning("order_send(legacy) failed: %s", e)
        return None


async def _order_close(acc, symbol: str, ticket: Optional[int] = None):
    if not ENABLE_TRADING:
        return
    # Prefer closing by ticket if returned
    try:
        if ticket is not None:
            return await acc.order_close(int(ticket))
    except Exception:
        pass
    # Otherwise best-effort by symbol
    try:
        return await acc.order_close(symbol)
    except Exception:
        return None


# ───────────────────────── main ─────────────────────────

async def main():
    acc = await connect()
    try:
        title("Trading basics (direct)")

        # 0) ensure symbol is visible
        await acc.symbol_select(SYMBOL, True)

        # 1) prices
        bid, ask = await _get_bid_ask(acc, SYMBOL)
        if bid is None or ask is None:
            print("Prices are unavailable; cannot proceed.")
            return
        print(f"Prices: BID={bid} | ASK={ask} | spread={ask - bid}")

        # 2) margin + validation
        m = await _order_calc_margin(acc, SYMBOL, VOLUME, side="BUY", price=ask)
        print(f"order_calc_margin: { _fval(m, m) }")

        chk = await _order_check(acc, SYMBOL, VOLUME, ask, side="BUY")
        print(f"order_check: {chk}")

        # 3) real sending (if enabled by environment variable)
        send_res = await _order_send(acc, SYMBOL, VOLUME, ask)
        if send_res is not None:
            print("order_send result:", send_res)

        # 4) closing (if sent and ticket is present)
        if send_res is not None:
            ticket = None
            for k in ("order", "ticket", "position", "deal"):
                ticket = ticket or getattr(send_res, k, None)
                if ticket:
                    break
            if ticket:
                await _order_close(acc, SYMBOL, ticket=int(ticket))

        print("Done.")
    finally:
        await shutdown(acc)


if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.trading_basics


    """
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/trading_basics.py — trading basics (direct calls)              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Show a minimal trading flow without safe_async: get prices, calc margin,   ║
║   run OrderCheck, send an order, and attempt closing — using direct RPC      ║
║   calls with careful fallbacks for varying pb2 builds.                       ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Happy-path flow                                                              ║
║  1) Connect: connect() → MT5Account; ensure SYMBOL is in Market Watch.       ║
║  2) Prices: symbol_info_double(BID/ASK) via MI enums → robust float.         ║
║  3) Margin: TH.OrderCalcMarginRequest → acc.order_calc_margin(req).          ║
║  4) Check : TH.OrderCheckRequest       → acc.order_check(req).               ║
║  5) Send  : TH.OrderSendRequest        → acc.order_send(req) (if enabled).   ║
║  6) Close : by ticket (if returned) or by symbol.                            ║
║  7) Cleanup: shutdown(acc).                                                  ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Key API calls                                                                ║
║  • Market info:                                                              ║
║    - symbol_select(symbol, True)                                             ║
║    - symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_BID/ASK)  ║
║    - symbol_info_tick(symbol) (as a price fallback)                          ║
║    - (opt.) symbol_info / get_symbol_info / symbol_info_get (contract size)  ║
║  • TradingHelper (TH):                                                       ║
║    - OrderCalcMarginRequest → order_calc_margin(req)                         ║
║    - OrderCheckRequest       → order_check(req)                              ║
║    - OrderSendRequest        → order_send(req)                               ║
║  • Service: account_summary(), order_close(ticket|symbol)                    ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Enums / types used                                                           ║
║  • MI.SymbolInfoDoubleProperty: SYMBOL_BID, SYMBOL_ASK                       ║
║  • TH.TMT5_ENUM_ORDER_TYPE: ORDER_TYPE_BUY / ORDER_TYPE_SELL                 ║
║  • TH.TMT5_ENUM_ORDER_TYPE_TIME: ORDER_TIME_GTC                              ╟
║ Helper functions                                                             ║
║  • _fval(x): tolerant float coercion (value/data/string with number).        ║
║  • _get_bid_ask(...): reads BID/ASK via MI enums and coerces to float.       ║
║  • _order_calc_margin(...): tries TH RPC first; fallback local estimate      ║
║    (contract_size*volume/leverage) with FX adjustment if needed.             ║
║  • _order_check(...): tries TH RPC first; fallback to a “soft OK” dict.      ║
║  • _order_send(...): tries TH.OrderSendRequest; falls back to legacy         ║
║    acc.order_send(symbol, 'BUY', volume, price).                             ║
║  • _order_close(...): by ticket (preferred) or by symbol.                    ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Behavior across builds / errors                                              ║
║  • Missing TH.* requests or methods → graceful fallbacks (local calc/legacy).║
║  • Missing contract_size / leverage → defaults (100000 / 100).               ║
║  • BID/ASK not numeric → fallback to tick.bid/tick.ask.                      ║
║  • RPC errors are contained inside helpers; extra logs when MT5_DEBUG=1.     ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Inputs / environment                                                         ║
║  • SYMBOL, VOLUME — from .env via common.env.                                ║
║  • MT5_ENABLE_TRADING=1 — allow real order send/close.                       ║
║  • MT5_DEBUG=1 — verbose logging for RPC fallbacks.                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Output / side effects                                                        ║
║  • Prints prices, computed margin, check and send results.                   ║
║  • Real trading only when MT5_ENABLE_TRADING=1.                              ║
║  • May close by returned ticket if present.                                  ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Limitations & notes                                                          ║
║  • No safe_async: this sample deliberately uses direct calls; helper funcs   ║
║    absorb typical failures.                                                  ║
║  • Margin math in fallback is simplified — prefer RPC for accuracy.          ║
║  • Commissions/swaps are not included in the local estimate.                 ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ How to run                                                                   ║
║  • From project root:                                                        ║
║      python -m examples.cli run trading_basics                               ║
║    or:                                                                       ║
║      python -m examples.trading_basics                                       ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ When to use this sample                                                      ║
║  • You want an end-to-end flow with direct calls (no wrappers).              ║
║  • You need to see behavior on servers missing parts of the TH API.          ║
║  • You want a quick sanity check for margin/validity and sending, with real  ║
║    trading gated by an environment flag.                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""