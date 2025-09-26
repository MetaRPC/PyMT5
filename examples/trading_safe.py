# examples/trading_safe.py
import os
import asyncio

from .common.env import connect, shutdown, SYMBOL, VOLUME, ENABLE_TRADING
from .common.utils import title
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as TF
from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as TH 

# ───────── config ─────────
ORDERCHECK_MODE = os.getenv("ORDERCHECK_MODE", "auto").lower()  # auto | soft | tf

# ───────── enums / constants ─────────
ORDER_BUY_TF  = TF.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_BUY
ORDER_SELL_TF = TF.ENUM_ORDER_TYPE_TF.ORDER_TYPE_TF_SELL
FILLING_FOK_TF = TF.MRPC_ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK
TIME_GTC_TF    = TF.MRPC_ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC
TIME_SPEC_TF   = getattr(TF.MRPC_ENUM_ORDER_TYPE_TIME, "ORDER_TIME_SPECIFIED", TIME_GTC_TF)

HAS_TH_CHECK = hasattr(TH, "OrderCheckRequest")

# ───────── utils ─────────
def _num(x):
    v = getattr(x, "value", x)
    return float(v)

def _short(s: str, n: int = 220) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n] + "…"

def _set_if_supported(msg, field, value) -> bool:
    try:
        if value is None:
            return False
        setattr(msg, field, value)
        return True
    except Exception:
        return False

def _has_any(obj, names):
    return any(hasattr(obj, n) for n in names)

_RETC_FIELDS = ("retcode", "ret_code", "result_code", "retcode_value", "code", "ret") 
_COMM_FIELDS = ("comment", "message", "msg", "description")

def _safe_comment_to_text(val: object) -> str:
    """We type 'comment' normally: if it's binary, we show the hex."""
    try:
        if val is None:
            return ""
        s = str(val)
        # If there are "garbage" non-printable characters, print hex
        bad = sum(ch < " " or ch > "~" for ch in s)
        if bad > 0:
            try:
                b = s.encode("latin-1", "ignore")
                return f"hex:{b.hex()}"
            except Exception:
                return repr(s)
        return s
    except Exception:
        try:
            b = bytes(val)
            return f"hex:{b.hex()}"
        except Exception:
            return repr(val)

def _deep_find_check_node(obj, _depth=0):
    """We search for a node with retcode/comment in depth (up to 8 levels)."""
    if obj is None or _depth > 8:
        return None
    if _has_any(obj, _RETC_FIELDS) or _has_any(obj, _COMM_FIELDS):
        return obj
    for attr in ("data", "mql_trade_check_result", "check_result", "result", "payload"):
        child = getattr(obj, attr, None)
        if child is not None:
            found = _deep_find_check_node(child, _depth + 1)
            if found is not None:
                return found
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            child = getattr(obj, name)
        except Exception:
            continue
        if callable(child):
            continue
        found = _deep_find_check_node(child, _depth + 1)
        if found is not None:
            return found
    return None

def _print_check_result(label: str, res) -> bool:
    """
    We print the result and return True if the retcode is found (even if it is an error), otherwise False.
    """
    node = _deep_find_check_node(res) or _deep_find_check_node(getattr(res, "data", None)) or res

    ret = None
    for f in _RETC_FIELDS:
        val = getattr(node, f, None)
        if val not in (None, ""):
            ret = val
            break

    com = ""
    for f in _COMM_FIELDS:
        val = getattr(node, f, None)
        if val not in (None, ""):
            com = _safe_comment_to_text(val)
            break

    if ret is None and not com:
        raw = str(res)
        if len(raw) > 400:
            raw = raw[:400] + " …"
        print(f"[{label}] check: <shape unknown> raw={raw!r}")
        return False
    else:
        print(f"[{label}] check: ret={ret!r} msg={com!r}")
        return ret is not None

def _maybe_dump_resp(label: str, res):
    if os.getenv("ORDERCHECK_DUMP", "0") != "1":
        return
    print(f"[{label}] dump: type={type(res).__name__}")
    try:
        if hasattr(res, "ListFields"):
            fields = ", ".join(fd.name for (fd, _) in res.ListFields())
            print(f"[{label}] fields: {fields}")
    except Exception:
        pass
    s = str(res)
    print(f"[{label}] raw: {s[:800]}{' …' if len(s) > 800 else ''}")

def _extract_wrapped_error(obj):
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

def _fmt(val):
    try:
        return float(getattr(val, "value", val))
    except Exception:
        return None

def _try_headers(acc):
    """Returns metadata with a guaranteed ('id', <connection_id>) - so that TF doesn't complain."""
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

def _headers(acc):
    """Preferably acc.get_headers() (as in your service), otherwise _try_headers()."""
    if hasattr(acc, "get_headers"):
        try:
            hs = acc.get_headers() or []
            return hs
        except Exception:
            pass
    return _try_headers(acc)

def _set_trade_action_deal(mql) -> bool:
    """Sets the DEAL action to one of the available fields (action/trade_action/request_action/type_action)."""
    candidates = (
        ("MRPC_ENUM_TRADE_REQUEST_ACTION", "TRADE_ACTION_DEAL"),
        ("ENUM_TRADE_REQUEST_ACTION_TF", "TRADE_ACTION_DEAL"),
        ("TRADE_REQUEST_ACTION_TF", "TRADE_ACTION_DEAL"),
    )
    deal_val = None
    for enum_cls, name in candidates:
        enum = getattr(TF, enum_cls, None)
        if enum and hasattr(enum, name):
            deal_val = getattr(enum, name)
            break
    deal_val = deal_val if deal_val is not None else 1 

    for fld in ("action", "trade_action", "request_action", "type_action"):
        if _set_if_supported(mql, fld, deal_val):
            return True
    return False

def _set_expiration_copyfrom(mql, seconds: int = 86400) -> int:
    """Writes Timestamp(+seconds) to the first matching field: expiration/time_expiration/expiration_time/time_specified/specified_time."""
    try:
        from datetime import datetime, timedelta, timezone as _tz
        from google.protobuf.timestamp_pb2 import Timestamp
        ts = Timestamp(); ts.FromDatetime(datetime.now(_tz.utc) + timedelta(seconds=seconds))
    except Exception:
        return 0
    for name in ("expiration", "time_expiration", "expiration_time", "time_specified", "specified_time"):
        if hasattr(mql, name):
            try:
                getattr(mql, name).CopyFrom(ts)
                return int(ts.seconds)
            except Exception:
                pass
    return 0

# ───────── TF.OrderCheck ─────────
async def order_check_tf(acc, *, symbol: str, volume: float, price: float | None, buy: bool):
    hdrs = _headers(acc)

    # Option 1
    try:
        req = TF.OrderCheckRequest(
            volume=float(volume),
            operation=(ORDER_BUY_TF if buy else ORDER_SELL_TF),
        )
        _set_if_supported(req, "symbol", symbol)
        _set_if_supported(req, "price", float(price) if price is not None else None)
        res = await acc.trade_functions_client.OrderCheck(req, metadata=hdrs, timeout=6.0)
        code, msg = _extract_wrapped_error(res)
        if code:
            raise RuntimeError(f"TF internal error: {code}: {msg}")
        return res
    except Exception:
        # Option 2 - as in lowlevel_walkthrough: MrpcMqlTradeRequest + ACTION=DEAL + expiration + type_time=SPECIFIED
        mql = TF.MrpcMqlTradeRequest(
            order_type=(ORDER_BUY_TF if buy else ORDER_SELL_TF),
            symbol=symbol,
            volume=float(volume),
            deviation=50,
            type_filling=FILLING_FOK_TF,
            type_time=TIME_SPEC_TF,  
        )
        _set_if_supported(mql, "type", getattr(mql, "order_type", None)) 
        # price in any supported field
        if not (_set_if_supported(mql, "price", price)
                or _set_if_supported(mql, "open_price", price)
                or _set_if_supported(mql, "order_price", price)):
            raise RuntimeError("Failed to set price (price/open_price/order_price)")
        _set_trade_action_deal(mql)
        _set_expiration_copyfrom(mql, 86400)  # +1 day

        req2 = TF.OrderCheckRequest(mql_trade_request=mql)
        res = await acc.trade_functions_client.OrderCheck(req2, metadata=hdrs, timeout=6.0)
        code, msg = _extract_wrapped_error(res)
        if code:
            raise RuntimeError(f"TF internal error: {code}: {msg}")
        return res

# ───────── TH.OrderCheck ─────────
async def order_check_th(acc, *, symbol: str, volume: float, price: float, buy: bool):
    if not HAS_TH_CHECK:
        raise RuntimeError("TradingHelper.OrderCheckRequest not available in this build.")
    req = TH.OrderCheckRequest(
        symbol=symbol,
        order_type=TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_BUY if buy else TH.TMT5_ENUM_ORDER_TYPE.ORDER_TYPE_SELL,
        volume=float(volume),
        price=float(price),
    )
    res = await acc.order_check(req)
    code, msg = _extract_wrapped_error(res)
    if code:
        raise RuntimeError(f"TH error: {code}: {msg}")
    return res

# ───────── "soft" check without RPC ─────────
async def soft_order_check(acc, *, symbol: str, volume: float, price: float, buy: bool):
    reasons = []
    ok = True

    vol_min  = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MIN)
    vol_max  = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_VOLUME_MAX)
    vol_step = await acc.symbol_info_double(symbol, MI.SymbolInfoDoubleProperty.SYMBOL_VOLUME_STEP)
    vmn, vmx, vst = _fmt(vol_min) or 0.0, _fmt(vol_max) or 0.0, _fmt(vol_step) or 0.01

    if volume < vmn: ok = False; reasons.append(f"volume<{vmn}")
    if vmx and volume > vmx: ok = False; reasons.append(f"volume>{vmx}")
    if vst > 0:
        k = round((volume - vmn) / vst)
        if abs(vmn + k * vst - volume) > 1e-8:
            ok = False; reasons.append(f"volume not multiple of step {vst}")

    trade_mode = await acc.symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.SYMBOL_TRADE_MODE)
    tm = int(_fmt(trade_mode) or 0)
    if tm == 0: ok = False; reasons.append("trade_mode=disabled")

    req = TF.OrderCalcMarginRequest(symbol=symbol,
                                    order_type=(ORDER_BUY_TF if buy else ORDER_SELL_TF),
                                    volume=float(volume),
                                    open_price=float(price))
    m = await acc.order_calc_margin(req)
    required_margin = (_fmt(getattr(m, "margin", None))
                       or _fmt(getattr(m, "required_margin", None))
                       or _fmt(getattr(m, "data", None))
                       or 0.0)

    free_margin = 0.0
    try:
        s = await acc.account_summary()
        free_margin = float(getattr(s, "account_free_margin", None)
                            or getattr(s, "free_margin", None)
                            or (getattr(s, "account_equity", 0.0) - getattr(s, "account_margin", 0.0))
                            or 0.0)
    except Exception:
        pass

    if required_margin and free_margin and free_margin < required_margin:
        ok = False; reasons.append(f"free_margin<{required_margin:.2f}")

    return {
        "ok": ok,
        "reasons": reasons,
        "volume_min": vmn, "volume_max": vmx, "volume_step": vst,
        "stops_level": _fmt(await acc.symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.SYMBOL_TRADE_STOPS_LEVEL)),
        "freeze_level": _fmt(await acc.symbol_info_integer(symbol, MI.SymbolInfoIntegerProperty.SYMBOL_TRADE_FREEZE_LEVEL)),
        "required_margin": required_margin, "free_margin": free_margin,
        "trade_mode": tm,
    }

# ───────── main ─────────
async def main():
    acc = await connect()
    try:
        title("Trading (safe): margin + order_check (no live orders)")

        await acc.symbol_select(SYMBOL, True)
        ask = await acc.symbol_info_double(SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_ASK)
        bid = await acc.symbol_info_double(SYMBOL, MI.SymbolInfoDoubleProperty.SYMBOL_BID)
        p_ask, p_bid = _num(ask), _num(bid)
        print(f"Prices: BID={p_bid} | ASK={p_ask} | spread={p_ask - p_bid}")

        req_m_buy  = TF.OrderCalcMarginRequest(symbol=SYMBOL, order_type=ORDER_BUY_TF,  volume=float(VOLUME), open_price=p_ask)
        req_m_sell = TF.OrderCalcMarginRequest(symbol=SYMBOL, order_type=ORDER_SELL_TF, volume=float(VOLUME), open_price=p_bid)
        m_buy  = await acc.order_calc_margin(req_m_buy)
        m_sell = await acc.order_calc_margin(req_m_sell)

        any_ok = False
        tf_failed = False

        # TH
        if ORDERCHECK_MODE != "soft" and HAS_TH_CHECK:
            try:
                r = await order_check_th(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_ask, buy=True)
                _maybe_dump_resp("BUY/TH", r)
                any_ok = _print_check_result("BUY/TH", r) or any_ok
            except Exception as e:
                print(f"[BUY/TH] error: {_short(str(e))}")
            try:
                r = await order_check_th(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_bid, buy=False)
                _maybe_dump_resp("SELL/TH", r)
                any_ok = _print_check_result("SELL/TH", r) or any_ok
            except Exception as e:
                print(f"[SELL/TH] error: {_short(str(e))}")
        elif not HAS_TH_CHECK:
            print("TradingHelper.OrderCheckRequest not available in this build — skipping TH path.")

        # TF
        ok_buy = ok_sell = False
        if ORDERCHECK_MODE != "soft":
            try:
                r = await order_check_tf(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_ask, buy=True)
                _maybe_dump_resp("BUY/TF", r)
                ok_buy = _print_check_result("BUY/TF", r)
                any_ok = any_ok or ok_buy
            except Exception as e:
                tf_failed = True
                print(f"[BUY/TF] error: {_short(str(e))}")
            try:
                r = await order_check_tf(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_bid, buy=False)
                _maybe_dump_resp("SELL/TF", r)
                ok_sell = _print_check_result("SELL/TF", r)
                any_ok = any_ok or ok_sell
            except Exception as e:
                tf_failed = True
                print(f"[SELL/TF] error: {_short(str(e))}")

        # Soft fallback - if the mode is soft, either the TF did not give a retcode in both directions, or the TF fell
        if ORDERCHECK_MODE == "soft" or (not ok_buy and not ok_sell) or tf_failed:
            print("\nSoft check (no RPC):")
            r_buy  = await soft_order_check(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_ask, buy=True)
            r_sell = await soft_order_check(acc, symbol=SYMBOL, volume=float(VOLUME), price=p_bid, buy=False)
            print("  BUY :", r_buy)
            print("  SELL:", r_sell)
            any_ok = True

        if not any_ok:
            print("\nOrderCheck is not available on this server/build (helper & TF failed).")

        def _margin_val(x):
            return getattr(x, "margin", None) or getattr(x, "required_margin", None) or getattr(x, "data", None) or x
        if m_buy:  print(f"[BUY]  required_margin: {_margin_val(m_buy)!r}")
        if m_sell: print(f"[SELL] required_margin: {_margin_val(m_sell)!r}")

        if ENABLE_TRADING:
            print("ENABLE_TRADING=1 → This example still does NOT send orders (safe mode).")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# $env:MT5_ENABLE_TRADING=0
# python -m examples.trading_safe

# or via CLI:
# python -m examples.cli run trading_safe


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/trading_safe.py — safe trading checks with robust fallbacks    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Validate a prospective trade safely on heterogeneous MT5 pb2 builds:       ║
║   fetch prices, compute required margin, attempt OrderCheck via multiple     ║
║   RPC shapes (TF first, TH if present), and gracefully fall back to a        ║
║   “soft” local check when the server/build doesn’t support OrderCheck.       ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ High-level flow                                                              ║
║  1) connect()                                                                ║
║  2) Ensure SYMBOL is in Market Watch.                                        ║
║  3) Read BID/ASK via MI enums → print spread.                                ║
║  4) Compute margin via TF.OrderCalcMarginRequest (buy/sell).                 ║
║  5) OrderCheck attempts (governed by ORDERCHECK_MODE):                       ║
║     • TH path (if build exposes TH.OrderCheckRequest) → acc.order_check().   ║
║     • TF path (preferred):                                                   ║
║         – Variant A: TF.OrderCheckRequest(symbol/price/operation…).          ║
║         – Variant B: TF.MrpcMqlTradeRequest with DEAL action + expiration,   ║
║           wrapped into TF.OrderCheckRequest (matches low-level walkthrough). ║
║     • If TF/TH fail or return no retcode → “soft” local check (no RPC).      ║
║  6) Print margins, checks, diagnostics; shutdown().                          ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Configuration / environment                                                  ║
║  • ORDERCHECK_MODE = auto | soft | tf                                        ║
║      auto: try TH (if available) + TF; fallback to soft if needed.           ║
║      soft: skip RPC checks, run only local validation.                       ║
║      tf  : force TF path (skip TH).                                          ║
║  • SYMBOL, VOLUME, ENABLE_TRADING — from .common.env                         ║
║  • ORDERCHECK_DUMP=1 — print proto fields/raw payloads for debugging.        ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Key RPCs / enums                                                             ║
║  • Market info (MI): SYMBOL_BID, SYMBOL_ASK, SYMBOL_VOLUME_{MIN/MAX/STEP},   ║
║    SYMBOL_TRADE_MODE, SYMBOL_TRADE_{STOPS/ FREEZE}_LEVEL.                    ║
║  • Trade Functions (TF):                                                     ║
║      - OrderCalcMarginRequest (open_price)                                   ║
║      - OrderCheckRequest (+ MrpcMqlTradeRequest fallback)                    ║
║      - ENUM_ORDER_TYPE_TF: ORDER_TYPE_TF_{BUY,SELL}                          ║
║      - MRPC_ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK                        ║
║      - MRPC_ENUM_ORDER_TYPE_TIME.{ORDER_TIME_GTC, ORDER_TIME_SPECIFIED}      ║
║  • Trading Helper (TH) (optional build): OrderCheckRequest                   ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ What the soft check validates (no RPC)                                       ║
║  • Volume within [VOLUME_MIN, VOLUME_MAX] and on VOLUME_STEP grid.           ║
║  • TRADE_MODE enabled.                                                       ║
║  • Required margin (TF.OrderCalcMargin) vs account free margin.              ║
║  • Also returns stops_level, freeze_level for transparency.                  ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Internal helpers provided in this file                                       ║
║  • _num(x): tolerant float extraction from proto fields.                     ║
║  • _fmt(x): numeric coercion helper for proto value/data.                    ║
║  • _safe_comment_to_text(): prints text or hex if comment is binary/garbled. ║
║  • _deep_find_check_node(): walks nested fields to find {retcode,comment}.   ║
║  • _print_check_result(): unified log output; returns True if retcode found. ║
║  • _maybe_dump_resp(): optional structured dump (ORDERCHECK_DUMP=1).         ║
║  • _extract_wrapped_error(): unwraps embedded error {code,message}.          ║
║  • _headers() / _try_headers(): ensure ('id', <connection_id>) metadata for  ║
║    TF calls to avoid “TERMINAL_IDENTIFIER_REQUEST_HEADER_NOT_FOUND”.         ║
║  • _set_trade_action_deal(): sets DEAL action across differing field names.  ║
║  • _set_expiration_copyfrom(): stamps expiration Timestamp (+1 day) to work  ║
║    around servers that require time_specified in TF requests.                ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Compatibility / resilience features                                          ║
║  • TH path is optional (HAS_TH_CHECK); skipped if pb2 lacks it.              ║
║  • TF path tries both the “flat” request and the MrpcMqlTradeRequest form.   ║
║  • Tolerates odd retcode/comment placements and binary comment payloads.     ║
║  • Prints hex codes like `hex:7617aa0e` when comments are non-printable.     ║
║  • Falls back to soft validation if TF returns internal errors or no retcode.║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Output                                                                       ║
║  • “Prices: BID=… | ASK=… | spread=…”                                        ║
║  • Check results per path (TH/TF), including retcode & message/hex.          ║
║  • Soft-check details when RPC is unavailable/unreliable.                    ║
║  • Required margin for BUY/SELL (from TF.OrderCalcMargin).                   ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ Error handling                                                               ║
║  • Catches/prints RPC exceptions per path; preserves overall script success. ║
║  • Forces ID header into TF metadata to avoid header-missing errors.         ║
║  • Uses expiration/time_specified to bypass server bugs requiring it.        ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ How to run                                                                   ║
║  • From project root:                                                        ║
║      python -m examples.cli run trading_safe                                 ║
║    Environment knobs: ORDERCHECK_MODE, ORDERCHECK_DUMP, SYMBOL, VOLUME.      ║
╟──────────────────────────────────────────────────────────────────────────────╢
║ When to use                                                                  ║
║  • You need a safe, read-only pre-trade validation that works across various ║
║    broker servers/builds without placing real orders.                        ║
║  • You are diagnosing TF/TH OrderCheck compatibility or server quirks.       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
