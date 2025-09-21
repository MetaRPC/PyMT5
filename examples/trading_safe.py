import asyncio
from datetime import datetime, timezone

# --- pb2 shim ---
from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown, SYMBOL, VOLUME, ENABLE_TRADING
from .common.utils import title, safe_async

# precise pb2 modules
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as TF
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI

# ──────────────────────────────
# Verified TF enums
# ──────────────────────────────
ORDER_BUY_TF  = TF.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY
ORDER_SELL_TF = TF.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_SELL

FILLING_FOK_TF = TF.MRPC_ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK
TIME_GTC_TF    = TF.MRPC_ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC

# ──────────────────────────────
# Utilities
# ──────────────────────────────
def _num(x):
    v = getattr(x, "value", x)
    return float(v)

def _set_if_supported(msg, field, value) -> bool:
    try:
        setattr(msg, field, value)
        return True
    except Exception:
        return False

def _short(s: str, n: int = 220) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n] + "…"

def _try_headers(acc):
    """
    Returns metadata with guaranteed ('id', <connection_id>) if we can.
    """
    mk = getattr(acc, "_create_headers", None)
    headers = []
    if callable(mk):
        try:
            headers = list(mk() or [])
        except Exception:
            headers = []
    else:
        headers = list(getattr(acc, "metadata", None) or getattr(acc, "_metadata", None) or [])

    def has_id(hs):
        try:
            return any(str(k).lower() == "id" and v for (k, v) in hs)
        except Exception:
            return False

    if not has_id(headers):
        for name in ("id_", "id", "connection_id", "session_id", "terminal_id", "context_id", "client_id"):
            val = getattr(acc, name, None)
            if val:
                headers.append(("id", str(val)))
                break
    return headers or None

def _print_check_result(label: str, res):
    """
    We support different response forms: res.data.mql_trade_check_result or raw error.
    """
    data = getattr(res, "data", res)
    chk  = getattr(data, "mql_trade_check_result", data)
    ret = getattr(chk, "retcode", None) or getattr(chk, "ret_code", None) or getattr(chk, "result_code", None)
    com = getattr(chk, "comment", None) or getattr(chk, "message", None)

    if ret is None and com is None:
        # Perhaps this is an error wrapper with error/error_code/error_message fields.
        err = getattr(data, "error", None) or getattr(res, "error", None)
        if err:
            ec = getattr(err, "error_code", "") or getattr(err, "code", "")
            em = getattr(err, "error_message", "") or getattr(err, "message", "")
            print(f"[{label}] check: ERROR code={ec!r} msg={_short(em)!r}")
            return
        print(f"[{label}] check: (No retcode/comment) raw={_short(str(res).strip())}")
    else:
        print(f"[{label}] check: ret={ret!r} msg={com!r}")

def _print_exc(label: str, e: Exception):
    etype = type(e).__name__
    estr  = _short(str(e))
    details = getattr(e, "details", None)
    code    = getattr(e, "code", None)
    d_text  = _short(details() if callable(details) else (details or ""))
    c_text  = str(code()) if callable(code) else str(code or "")
    print(f"[{label}] TF check ERROR: type={etype} code={c_text} details={d_text}")

def _extract_wrapped_error(obj):
    """
    If the server returned an error field within a successful response → we get a short description.
    """
    data = getattr(obj, "data", None) or obj
    err  = getattr(data, "error", None) or getattr(obj, "error", None)
    if err:
        code = getattr(err, "error_code", "") or getattr(err, "code", "")
        msg  = getattr(err, "error_message", "") or getattr(err, "message", "")
        if code or msg:
            return code, msg

    s = str(obj)
    if "UNEXPECTED_COMMAND_EXECUTION_ERROR_IN_INTERNAL_GRPC_SERVICE" in s \
       or "Object reference not set to an instance of an object" in s:
        return ("UNEXPECTED_COMMAND_EXECUTION_ERROR_IN_INTERNAL_GRPC_SERVICE",
                "Object reference not set to an instance of an object.")
    return None, None

# ── OrderCheck (TF only, no TH/real shipping) ────────────────────────
async def order_check_tf(acc, *, symbol: str, volume: float, price: float, buy: bool):
    headers = _try_headers(acc)

    # We design strictly according to the prototype
    mql = TF.MrpcMqlTradeRequest(
        order_type=(ORDER_BUY_TF if buy else ORDER_SELL_TF),
        symbol=symbol,
        volume=volume,
        deviation=50,
        type_filling=FILLING_FOK_TF,
        type_time=TIME_GTC_TF,
    )
    # price - in one of the possible fields
    if not (_set_if_supported(mql, "price", price)
            or _set_if_supported(mql, "open_price", price)
            or _set_if_supported(mql, "order_price", price)):
        raise RuntimeError("Failed to set price (price/open_price/order_price).")

    req = TF.OrderCheckRequest(mql_trade_request=mql)
    res = await acc.trade_functions_client.OrderCheck(req, metadata=headers, timeout=6.0)

    # If an error wrapper is received inside the response, we'll simply return it as is.
    code, msg = _extract_wrapped_error(res)
    if code or msg:
        print(f"[CHECK] TF returned error payload: code={code!r} msg={_short(msg)!r}")
    return res

# ──────────────────────────────
# main
# ──────────────────────────────
async def main():
    acc = await connect()
    try:
        title("Trading (safe): margin + order_check (no live orders)")

        # 1) Symbol and quotes
        await safe_async("symbol_select", acc.symbol_select, SYMBOL, True)
        ask = await safe_async("symbol_info_double(ASK)", acc.symbol_info_double, SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_ASK)
        bid = await safe_async("symbol_info_double(BID)", acc.symbol_info_double, SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_BID)
        p_ask, p_bid = _num(ask), _num(bid)

        # 2) Margin calculation (the field in TF is called open_price)
        req_m_buy  = TF.OrderCalcMarginRequest(symbol=SYMBOL, order_type=ORDER_BUY_TF,  volume=float(VOLUME), open_price=p_ask)
        req_m_sell = TF.OrderCalcMarginRequest(symbol=SYMBOL, order_type=ORDER_SELL_TF, volume=float(VOLUME), open_price=p_bid)
        m_buy  = await safe_async("order_calc_margin(BUY)",  acc.order_calc_margin, req_m_buy)
        m_sell = await safe_async("order_calc_margin(SELL)", acc.order_calc_margin, req_m_sell)

        # 3) TF.OrderCheck only (without TradingHelper)
        try:
            res_buy  = await order_check_tf(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_ask, buy=True)
            _print_check_result("BUY",  res_buy)
        except Exception as e:
            _print_exc("BUY", e)

        try:
            res_sell = await order_check_tf(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_bid, buy=False)
            _print_check_result("SELL", res_sell)
        except Exception as e:
            _print_exc("SELL", e)

        # 4) Total margin
        def _margin_val(x):
            return getattr(x, "margin", None) or getattr(x, "required_margin", None) or getattr(x, "data", None) or x
        if m_buy:  print(f"[BUY]  required_margin: {_margin_val(m_buy)!r}")
        if m_sell: print(f"[SELL] required_margin: {_margin_val(m_sell)!r}")

        # 5) There are no live orders on purpose
        if ENABLE_TRADING:
            print("ENABLE_TRADING=1 → We deliberately DO NOT send an order in this example.")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.cli run trading_safe

    """
    Example: Trading (safe) — TF margin + TF OrderCheck (no live orders)
    ====================================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session; close with `shutdown()`. |
    | Heading | `title(...)` | Cosmetic header. |
    | Select & quotes | `symbol_select(SYMBOL, True)`; read `ASK`/`BID` via `symbol_info_double` | Ensures symbol in Market Watch; extracts numeric prices (`_num()` unwraps `.value`). |
    | Margin (TF) | Build **TF.OrderCalcMarginRequest** (open_price = ask/bid) → `acc.order_calc_margin(req)` | Pure TF path: one request per side (BUY/SELL). |
    | OrderCheck (TF) | `order_check_tf(...)` → **TF.OrderCheckRequest** with **MrpcMqlTradeRequest** | No TradingHelper; uses known TF enums and tries common price field names. |
    | Print results | `_print_check_result("BUY"/"SELL", res)` + margin summary | Renders retcode/comment or short wrapped error if server embeds it. |
    | Safety | No live orders even if `ENABLE_TRADING=1` | This example intentionally **does not** send/close orders. |
    | Cleanup | `await shutdown(acc)` | Graceful disconnect. |

    Exact modules & enums (TF / MI)
    --------------------------------
    - `from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as TF`
      - Side: `TF.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY / ORDER_TYPE_TF_SELL`
      - Filling: `TF.MRPC_ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK`
      - Time-in-force: `TF.MRPC_ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC`
      - Requests used: `TF.OrderCalcMarginRequest`, `TF.OrderCheckRequest`, `TF.MrpcMqlTradeRequest`
    - `from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI`
      - Quotes: `MI.SymbolInfoDoubleProperty.SYMBOL_ASK / SYMBOL_BID`

    Request construction details
    ----------------------------
    - **OrderCalcMargin (TF)**:
        - BUY:  `open_price = ASK`,   SELL: `open_price = BID`
        - Other fields: `symbol`, `order_type`, `volume`
    - **OrderCheck (TF)**:
        - `MrpcMqlTradeRequest` fields set:
          - `order_type` (BUY/SELL via TF enums)
          - `symbol`, `volume`, `deviation=50`, `type_filling=FOK`, `type_time=GTC`
          - price field: best-effort (`price` | `open_price` | `order_price`) via `_set_if_supported(...)`
        - Metadata: `_try_headers(acc)` injects `('id', <connection_id>)` if possible
        - RPC: `acc.trade_functions_client.OrderCheck(req, metadata=headers, timeout=6.0)`

    Error/response handling
    -----------------------
    - `_extract_wrapped_error(obj)` detects server-side `error{code,message}` embedded in a success payload or common internal errors (e.g. `"Object reference not set..."`).
    - `_print_check_result(label, res)` prints:
      - `retcode` / `comment` (or `ret_code` / `result_code`, `message`)
      - or a compact error line if response carries an error envelope
    - `_print_exc(label, e)` prints gRPC exception type/code/details when OrderCheck throws.

    Output (typical)
    ----------------
    Trading (safe): margin + order_check (no live orders)
    [BUY]  check: ret='TRADE_RETCODE_DONE' msg='done'
    [SELL] check: ret='TRADE_RETCODE_DONE' msg='done'
    [BUY]  required_margin: 123.45
    [SELL] required_margin: 123.10

    Notes & edge cases
    ------------------
    - Some servers require specific price field naming; `_set_if_supported` tries multiple common aliases.
    - If OrderCheck returns a success envelope with an internal error object, we report its short code/message.
    - Margin values can differ from helper APIs due to TF vs. TH calculation paths or symbol margin specifics.
    - Time is UTC-based when needed (imports available if you extend with deadlines).

    How to run
    ----------
    From project root:
      `python -m examples.trading_tf_check`
    Or via CLI (if present):
      `python -m examples.cli run trading_tf_check`

    Environment
    -----------
    - `SYMBOL`, `VOLUME`, `ENABLE_TRADING` are taken from `.common.env`.
    - This example **does not** place or close live orders, regardless of `ENABLE_TRADING`.
    """