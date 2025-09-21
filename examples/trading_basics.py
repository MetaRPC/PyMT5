# examples/trading_basics.py
import os
import re
import asyncio
import logging
from typing import Any, Tuple

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown, SYMBOL, VOLUME
from .common.utils import title, safe_async
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI

# ───────────────────────── logging ─────────────────────────
log = logging.getLogger(__name__)

logging.basicConfig(level=logging.WARNING)

ENABLE_TRADING = os.getenv("MT5_ENABLE_TRADING", "0") == "1"
DEBUG_RPC = os.getenv("MT5_DEBUG", "0") == "1"

# ───────────────────────── helpers ─────────────────────────
def _fval(x: Any, default: float = 0.0) -> float:
    """We are trying to call float from different response forms (number/proto/string)."""
    try:
        if x is None:
            return float(default)
        if isinstance(x, (int, float)):
            return float(x)

        # proto.value
        v = getattr(x, "value", None)
        if isinstance(v, (int, float, str)):
            try:
                return float(v)
            except Exception:
                pass

        # proto.data.value
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
    return float(default)

def _set(obj: Any, names, value) -> bool:
    """We try to set the field by any of the name options."""
    for n in names:
        try:
            setattr(obj, n, value)
            return True
        except Exception:
            continue
    return False

async def _get_bid_ask(acc, symbol: str) -> Tuple[float, float]:
    bid = await safe_async(
        "symbol_info_double(BID)",
        acc.symbol_info_double, symbol, MI.SymbolInfoDoubleProperty.SYMBOL_BID
    )
    ask = await safe_async(
        "symbol_info_double(ASK)",
        acc.symbol_info_double, symbol, MI.SymbolInfoDoubleProperty.SYMBOL_ASK
    )
    return _fval(bid), _fval(ask)

# ─────────── dynamic search for RPC modules/methods ───────────
_CANDIDATE_TF_MODULES = [
    "MetaRpcMT5.mt5_term_api_trade_functions_pb2",
    "MetaRpcMT5.mt5_term_api_trading_pb2",
    "MetaRpcMT5.mt5_trade_functions_pb2",
]
_CANDIDATE_CLIENT_ATTRS = ["trade_functions_client", "trade_client", "trading_client"]
_CANDIDATE_MARGIN_METHODS = ["OrderCalcMargin", "CalcMargin", "OrderCalcMargin2"]
_CANDIDATE_CHECK_METHODS  = ["OrderCheck", "CheckOrder", "OrderCheckNew"]

def _import_first(mod_names):
    for name in mod_names:
        try:
            mod = __import__(name, fromlist=["*"])
            return mod, name
        except Exception:
            continue
    return None, None

def _get_first_attr(obj, names):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n), n
    return None, None

def _find_req_class(mod, prefer_suffix="Request", must_have=("Order","")):
    if not mod:
        return None, None
    for nm in dir(mod):
        if not nm.endswith(prefer_suffix):
            continue
        up = nm.upper()
        if all(w.upper() in up for w in must_have if w):
            return getattr(mod, nm), nm
    return None, None

def _enum_side(side) -> int:
    try:
        s = str(side).upper()
        return 0 if s in ("BUY","B","LONG","0") else 1
    except Exception:
        try:
            return int(side)
        except Exception:
            return 0

async def _rpc_call_generic(acc, method_candidates, req_words, fill_fields):
    """Single binding: find client → module → Request → method and call RPC."""
    client, client_name = _get_first_attr(acc, _CANDIDATE_CLIENT_ATTRS)
    if client is None:
        raise RuntimeError("No trade_* client found in this build")

    mod, mod_name = _import_first(_CANDIDATE_TF_MODULES)
    if not mod:
        raise RuntimeError("No suitable pb2 module trade_functions found")

    ReqCls, req_cls_name = _find_req_class(mod, "Request", req_words)
    if ReqCls is None:
        raise RuntimeError(f"Request with keys not found in module {mod_name} {req_words}")

    req = ReqCls()
    fill_fields(req)

    method = None
    picked_method = None
    for mn in method_candidates:
        if hasattr(client, mn):
            method = getattr(client, mn)
            picked_method = mn
            break
    if method is None:
        raise RuntimeError(f"There are no methods in client {client_name} {method_candidates}")

    async def grpc_call(headers):
        return await method(req, metadata=headers, timeout=5.0)

    if DEBUG_RPC:
        log.warning(
            "RPC try: client=%s | module=%s | request=%s | method=%s | req_dump=%r",
            client_name, mod_name, req_cls_name, picked_method, req
        )

    res = await acc.execute_with_reconnect(
        grpc_call=grpc_call,
        error_selector=lambda r: getattr(r, "error", None),
        deadline=None,
        cancellation_event=None,
    )
    return getattr(res, "data", res)

# ───────────────────────── calculations ─────────────────────────
async def _order_calc_margin(acc, symbol: str, volume: float, side: int | str = "BUY", price: float | None = None):
    # 1) RPC
    try:
        if price is None:
            t = await acc.symbol_info_tick(symbol)
            b = float(getattr(t, "bid", 0.0) or getattr(t, "Bid", 0.0) or 0.0)
            a = float(getattr(t, "ask", 0.0) or getattr(t, "Ask", 0.0) or 0.0)
            price = a or b or 1.0

        side_code = _enum_side(side)

        def _fill(req):
            _set(req, ["symbol"], symbol)
            _set(req, ["order_type","type","cmd"], int(side_code))
            _set(req, ["volume","volume_lots"], float(volume))
            _set(req, ["price"], float(price))

        data = await _rpc_call_generic(acc, _CANDIDATE_MARGIN_METHODS, ("Order","Margin"), _fill)
        val = _fval(data, None)
        return val if val is not None else data
    except Exception as e:
        if DEBUG_RPC:
            log.warning("order_calc_margin (RPC) unavailable: %s", e)

    # 2) Local fallback
    try:
        info = None
        for nm in ("symbol_info", "get_symbol_info", "symbol_info_get"):
            f = getattr(acc, nm, None)
            if callable(f):
                try:
                    info = await f(symbol)
                    break
                except Exception:
                    pass

        # leverage (from account, otherwise 100)
        lev = 100.0
        try:
            acc_sum = await acc.account_summary()
            lev = float(getattr(acc_sum, "account_leverage", None) or 100.0)
        except Exception:
            pass
        lev = max(float(lev or 1.0), 1.0)

        # contract
        contract_size = float(
            getattr(info, "trade_contract_size", None)
            or getattr(info, "TradeContractSize", None)
            or getattr(info, "contract_size", None)
            or getattr(info, "ContractSize", None)
            or 100000.0
        )

        if price is None:
            bid, ask = await _get_bid_ask(acc, symbol)
            price = float(ask or bid or 1.0)

        # Basic formula: (contract_size * volume / leverage) in base currency
        margin = (contract_size * float(volume)) / lev

        # If the account currency ≠ the base currency, multiply by the price
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

async def _order_check(acc, symbol: str, volume: float, price: float, side: int | str = "BUY"):
    # 1) RPC
    try:
        side_code = _enum_side(side)

        def _fill(req):
            _set(req, ["symbol"], symbol)
            _set(req, ["order_type","type","cmd"], int(side_code))
            _set(req, ["volume","volume_lots"], float(volume))
            _set(req, ["price"], float(price))

        data = await _rpc_call_generic(acc, _CANDIDATE_CHECK_METHODS, ("Order","Check"), _fill)
        return data
    except Exception as e:
        if DEBUG_RPC:
            log.warning("order_check (RPC) unavailable: %s", e)

    # 2) Demo validation
    return {"ok": True, "symbol": symbol, "side": str(side), "volume": float(volume), "price": float(price)}

# ───────────────────────── sending/closing ─────────────────────────
async def _order_send(acc, symbol, volume, price):
    if not ENABLE_TRADING:
        print("MT5_ENABLE_TRADING != 1 → Real sending is disabled.")
        return None
    # Minimum output; trying two options
    try:
        return await safe_async("order_send(symbol,'BUY',volume,price)", acc.order_send, symbol, "BUY", float(volume), float(price))
    except Exception:
        pass
    try:
        req = {
            "symbol": symbol,
            "action": "BUY",
            "type": "ORDER_TYPE_BUY",
            "volume": float(volume),
            "price": float(price),
            "time": "ORDER_TIME_GTC",
            "deviation": 20,
        }
        return await safe_async("order_send(dict)", acc.order_send, req)
    except Exception:
        return None

async def _order_close(acc, symbol, ticket=None):
    if not ENABLE_TRADING:
        return
    try:
        if ticket is not None:
            return await safe_async("order_close(ticket)", acc.order_close, int(ticket))
    except Exception:
        pass
    try:
        return await safe_async("order_close(symbol)", acc.order_close, symbol)
    except Exception:
        return None

# ───────────────────────── main ─────────────────────────
async def main():
    acc = await connect()
    try:
        title("Trading basics (safe)")

        # 0) symbol available
        await safe_async("symbol_select", acc.symbol_select, SYMBOL, True)

        # 1) prices
        bid, ask = await _get_bid_ask(acc, SYMBOL)
        print(f"Prices: BID={bid} | ASK={ask} | spread={ask - bid}")

        # 2) margin + validation (RPC → fallback)
        m = await _order_calc_margin(acc, SYMBOL, VOLUME, side="BUY", price=ask)
        print(f"order_calc_margin: { _fval(m, m) }")

        chk = await _order_check(acc, SYMBOL, VOLUME, ask, side="BUY")
        print(f"order_check: {chk}")

        # 3) real sending (if enabled by environment variable)
        send_res = await _order_send(acc, SYMBOL, VOLUME, ask)

        # 4) closing (if sent)
        if send_res is not None:
            ticket = None
            for k in ("order", "ticket", "position", "deal"):
                ticket = ticket or getattr(send_res, k, None)
                if ticket:
                    break
            await _order_close(acc, SYMBOL, ticket=ticket)

        print("Done.")
    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.trading_basics


    """
    Example: Trading basics (safe) — quotes → margin/check → (optional) send/close
    =============================================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Open async session to the MT5 bridge; close with `shutdown()`. |
    | Heading | `title("Trading basics (safe)")` | Cosmetic header in console/log. |
    | Ensure symbol | `symbol_select(SYMBOL, True)` | Guarantees the symbol is available in Market Watch. |
    | Quotes | `_get_bid_ask(SYMBOL)` via `symbol_info_double(BID/ASK)` | Unified extraction with `_fval(...)` so both raw floats and message wrappers work. |
    | Margin | `_order_calc_margin(symbol, volume, side="BUY", price=ask)` | Tries RPC (`OrderCalcMargin*`) and falls back to a local estimation formula. |
    | Check | `_order_check(symbol, volume, price, side)` | Tries `OrderCheck*` RPC; otherwise returns a minimal “ok” demo result. |
    | Send (opt) | `_order_send(acc, SYMBOL, VOLUME, ask)` | **Only** if `MT5_ENABLE_TRADING=1` — prevents accidental live trading. Two request shapes are supported. |
    | Close (opt) | `_order_close(acc, SYMBOL, ticket)` | Closes by ticket (preferred) or by symbol as a fallback. |
    | Cleanup | `await shutdown(acc)` | Always disconnect cleanly. |

    Safety switches (env)
    ---------------------
    - `MT5_ENABLE_TRADING=1` → allows real `order_send` / `order_close`. Default is **off** (safe dry-run).
    - `MT5_DEBUG=1` → verbose RPC discovery logs (client/module/method/req dump).
    - `SYMBOL`, `VOLUME` come from `.common.env`.

    RPC discovery (portable across builds)
    --------------------------------------
    - Candidate pb2 modules for trading:
        * `MetaRpcMT5.mt5_term_api_trade_functions_pb2`
        * `MetaRpcMT5.mt5_term_api_trading_pb2`
        * `MetaRpcMT5.mt5_trade_functions_pb2`
    - Candidate clients on `acc`:
        * `trade_functions_client`, `trade_client`, `trading_client`
    - Candidate margin methods:
        * `OrderCalcMargin`, `CalcMargin`, `OrderCalcMargin2`
    - Candidate check methods:
        * `OrderCheck`, `CheckOrder`, `OrderCheckNew`
    - `_rpc_call_generic(...)` locates client → module → `*Request` class (by name fragments) → method, fills fields, invokes gRPC with a 5s timeout, and returns `.data` if present.

    Field/enum normalization helpers
    --------------------------------
    - `_fval(x)` — extracts a float from:
        * raw number, `.value`, `.data.value`, or string dumps like `"value: 1.2345"`.
    - `_set(obj, ["field", "altField", ...], value)` — assigns to the first available field name.
    - `_enum_side(side)` — maps `"BUY"/"SELL"/"B"/"LONG"/"0/1"` (case-insensitive) to integer side codes 0/1.

    Margin calculation fallback (when RPC is unavailable)
    ----------------------------------------------------
    - Contract size: from symbol info (`trade_contract_size|contract_size`, fallback `100000.0`).
    - Leverage: from `account_summary().account_leverage` (fallback `100.0`, min `1.0`).
    - Price: `ask` (or `bid`) if not supplied.
    - Formula:
        ```
        margin_base = contract_size * volume / leverage
        margin = margin_base if account_currency == symbol_base
                 else margin_base * price
        ```
      This is a **rough estimate** for demo purposes and may differ from server `OrderCalcMargin` due to:
      - margin mode (Forex/CFD), hedged margin settings,
      - symbol-specific coefficients, conversion chains, or tiered margin.

    Order check fallback
    --------------------
    - If no `OrderCheck*` RPC is available, returns a minimal dict:
      `{"ok": True, "symbol": ..., "side": ..., "volume": ..., "price": ...}`.

    Order send/close behavior
    -------------------------
    - `_order_send` tries:
        1) Positional form: `order_send(symbol, "BUY", volume, price)`
        2) Dict form compatible with some builds:
           `{"symbol": ..., "action": "BUY", "type": "ORDER_TYPE_BUY", "volume": ..., "price": ..., "time": "ORDER_TIME_GTC", "deviation": 20}`
      Returns the provider's response (often contains `order | ticket | position | deal`).
    - `_order_close` prioritizes closing by explicit ticket; falls back to `order_close(symbol)` if needed.

    Typical output
    --------------
    Prices: BID=1.08456 | ASK=1.08468 | spread=0.00012
    order_calc_margin: 123.45
    order_check: {'ok': True, 'symbol': 'EURUSD', 'side': 'BUY', 'volume': 0.10, 'price': 1.08468}
    MT5_ENABLE_TRADING != 1 → Real sending is disabled.
    Done.

    Notes & edge cases
    ------------------
    - If quotes are missing, ensure the symbol is tradable/visible and market data is available.
    - Different builds may rename fields in trading requests; `_set(...)` keeps the code tolerant.
    - Live orders require permissions/margin; providers may reject for many reasons (market closed, trade mode, min volume step).
    - For strict server-time issues, prefer client-side timeouts in your helpers (this script uses fixed 5s on trading RPCs).

    How to run
    ----------
    From project root:
      `python -m examples.trading_basics`
    Or via CLI (if present):
      `python -m examples.cli run trading_basics`
    """