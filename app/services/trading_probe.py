# comments in English only

from __future__ import annotations
import inspect
from typing import Dict, Tuple, Optional

"""
╔════════════════════════════════════════════════════════════════════════════╗
║ FILE app/services/trading_bindings_report.py — wiring checks & prechecks   ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                    ║
║ • Central list of trading method names expected on MT5Service.             ║
║ • One-shot console report showing which endpoints are actually bound.      ║
║ • Lightweight symbol precheck via order_check_ex, when available.          ║
║                                                                            ║
║ Behavior                                                                   ║
║ • Purely introspective: does not invoke any trading action.                ║
║ • Prints real Python signature when introspection works, else hint string. ║
║                                                                            ║
║ Safety                                                                     ║
║ • Read-only; no I/O beyond printing; tolerant to missing methods.          ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

TRADING_METHODS: Dict[str, Tuple[str, str]] = {
    # name: (group, signature_hint)
    "buy_market":              ("market",  "(symbol: str, volume: float, sl=None, tp=None)"),
    "sell_market":             ("market",  "(symbol: str, volume: float, sl=None, tp=None)"),
    "order_send_ex":           ("low",     "(action: 'MARKET'|'DEAL', side: 'BUY'|'SELL', symbol: str, volume: float, price=?, sl=?, tp=?)"),
    "place_buy_limit":         ("pending", "(symbol: str, volume: float, price: float, sl=None, tp=None, expiration: int|None)"),
    "place_sell_limit":        ("pending", "(symbol: str, volume: float, price: float, sl=None, tp=None, expiration: int|None)"),
    "place_buy_stop":          ("pending", "(symbol: str, volume: float, price: float, sl=None, tp=None, expiration: int|None)"),
    "place_sell_stop":         ("pending", "(symbol: str, volume: float, price: float, sl=None, tp=None, expiration: int|None)"),
    "place_stop_limit":        ("pending", "(symbol: str, is_buy: bool, volume: float, stop_price: float, limit_price: float, sl=None, tp=None, expiration: int|None)"),
    "pending_modify":          ("pending", "(ticket: int, price: float|None, sl: float|None, tp: float|None)"),
    "pending_replace_stop_limit": ("pending", "(...)  # optional in some builds"),
    "cancel_order":            ("pending", "(ticket: int)"),
    "position_modify":         ("position","(ticket: int, sl: float|None, tp: float|None)"),
    "position_close":          ("position","(symbol: str)"),
    "close_all_positions":     ("position","()"),
}

def _fmt_sig(fn) -> str:
    """Return inspected signature string or empty string on failure."""
    try:
        return str(inspect.signature(fn))
    except Exception:
        return ""

async def report_trading_bindings(svc, *, show_missing: bool = True) -> None:
    """
    Print which trading methods are bound on MT5Service.
    Does not execute any trading calls.
    """
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print(  "║ Trading methods: wiring check                                ║")
    print(  "╚══════════════════════════════════════════════════════════════╝")

    groups = ("market", "pending", "position", "low")
    for grp in groups:
        print(f"\n[{grp.upper()}]")
        for name, (g, hint) in TRADING_METHODS.items():
            if g != grp:
                continue
            fn = getattr(svc, name, None)
            if callable(fn):
                sig = _fmt_sig(fn) or hint
                print(f"  ✓ {name}{sig}")
            elif show_missing:
                print(f"  · {name}  — missing")

async def first_symbol_precheck(svc, symbol: str) -> None:
    """
    Quick non-blocking precheck: select symbol, attempt order_check_ex if available.
    """
    try:
        await svc.symbol_select(symbol, True)
    except Exception:
        pass
    oce = getattr(svc, "order_check_ex", None)
    if callable(oce):
        try:
            ok = await oce(action="MARKET", side="BUY", symbol=symbol, volume=0.01)
            print(f"precheck(order_check_ex): {symbol} →", "OPEN" if ok else "NOT OK")
        except Exception as e:
            print("precheck(order_check_ex) failed:", str(e).splitlines()[0])
    else:
        print("precheck: order_check_ex not available in this build")
