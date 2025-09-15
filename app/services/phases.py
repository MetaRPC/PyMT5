# comments in English only

from __future__ import annotations
import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING, Iterable, Tuple, Set
from app.compat.mt5_patch import order_calc_profit as calc_profit, order_calc_margin as calc_margin

if TYPE_CHECKING:
    # Adjust import path if your MT5Service lives elsewhere
    from app.core.mt5_service import MT5Service


"""
╔════════════════════════════════════════════════════════════════════════════╗
║ FILE app/services/phases.py — diagnostic phases for MT5Service             ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                    ║
║ • Provide small, safe, and uniform “phases” to exercise a connected        ║
║   MT5Service: connectivity, symbols, opened state, calculations, charts,   ║
║   history, streaming (wrapper), and trading presets.                       ║
║                                                                            ║
║ Key Entry Points                                                           ║
║ • phase_connectivity_and_account(svc)                                      ║
║ • phase_symbols_and_market_info(svc, selected)                             ║
║ • phase_opened_state_snapshot(svc, selected)                               ║
║ • phase_calculations_and_checks(svc, symbol)                               ║
║ • phase_charts_and_dom(svc, selected)                                      ║
║ • phase_history_and_lookups(svc)                                           ║
║ • phase_streams_wrapper(svc)  ← header + delegate to streams_service       ║
║ • phase_trading_ops_preset(svc, plan)  ← dry-run by default                ║
║ • phase_danger_zone_stepwise(svc, symbol)  ← explicit live ops             ║
║ • dump_trading_capabilities(svc)                                           ║
║                                                                            ║
║ Behavior                                                                   ║
║ • Be tolerant to build differences (snake/camel fields, optional stubs).   ║
║ • Never crash on missing APIs; print concise diagnostics instead.          ║
║ • Do not mutate service configuration. Trading presets are dry-run unless  ║
║   explicitly disabled.                                                     ║
║                                                                            ║
║ Safety                                                                      ║
║ • Read-only in all phases except trading presets/stepwise (guarded).       ║
║ • Timeouts and retries are local to callers; no global side effects.       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""


# ────────────────────────────────────────────────────────────────────────────
# UTILS
# ────────────────────────────────────────────────────────────────────────────

def box(title: str) -> None:
    """ASCII box header to visually separate phases in console output."""
    line = "═" * 78
    print("\n" + f"╔{line}╗")
    print(f"║ {title:<76}║")
    print(f"╚{line}╝")


# Run-once helper
_RUN_ONCE: Set[str] = set()

async def run_once(key: str, target):
    """Run a coroutine or zero-arg callable only once during the whole run."""
    if key in _RUN_ONCE:
        return
    _RUN_ONCE.add(key)
    coro = target() if callable(target) else target
    await coro


def _as_float(x) -> float:
    """
    Safely coerce server replies to float:
    • direct float/int
    • common attributes (value/amount/profit/margin/result/res)
    • protobuf → dict via MessageToDict
    """
    try:
        return float(x)
    except Exception:
        pass
    # common attributes
    for k in ("value", "amount", "profit", "margin", "result", "res"):
        try:
            v = getattr(x, k, None)
            if v is not None:
                return float(v)
        except Exception:
            pass
    # protobuf → dict
    try:
        from google.protobuf.json_format import MessageToDict
        d = MessageToDict(x, preserving_proto_field_name=True)
        for k in ("value", "amount", "profit", "margin", "result"):
            if k in d:
                return float(d[k])
    except Exception:
        pass
    return 0.0


async def is_trading_open_now(svc: "MT5Service", symbol: str) -> Tuple[bool | None, str]:
    """
    Check trading availability using order_check_ex when present.
    Returns (True/False/None, reason). None → build lacks order_check_ex.
    """
    try:
        await svc.symbol_select(symbol, True)
    except Exception:
        pass

    order_check_ex = getattr(svc, "order_check_ex", None)
    if callable(order_check_ex):
        try:
            ok = await order_check_ex(action="MARKET", side="BUY", symbol=symbol, volume=0.01)
            if ok is True:
                return True, "order_check_ex: OK"
            return False, "order_check_ex: not OK"
        except Exception as e:
            emsg = str(e)
            if any(x in emsg for x in ("MARKET_CLOSED", "TRADE_RETCODE_MARKET_CLOSED", "10018")):
                return False, "order_check_ex: MARKET_CLOSED (10018)"
            return False, f"order_check_ex error: {emsg.splitlines()[0]}"

    return None, "no order_check_ex in this build"


# ────────────────────────────────────────────────────────────────────────────
# [0] CONNECTIVITY & ACCOUNT
# ────────────────────────────────────────────────────────────────────────────

async def phase_connectivity_and_account(svc: "MT5Service") -> None:
    """Ping core account/time endpoints to validate connectivity quickly."""
    box("0) ▶ Connectivity & Account core")
    try:
        st = await svc.server_time()
        print("server_time:", st)
    except Exception as e:
        print("server_time failed:", e)

    try:
        summ = await svc.account_summary()
        print("account_summary:", summ)
    except Exception as e:
        print("account_summary failed:", e)

    # Probe optional convenience getters when available
    for nm in (
        "account_info", "account_info_balance", "account_info_equity",
        "account_info_margin", "account_info_leverage", "account_currency"
    ):
        try:
            fn = getattr(svc, nm, None)
            if callable(fn):
                res = await fn()
                print(f"{nm}:", res)
        except Exception as e:
            print(f"{nm} failed:", e)


# ────────────────────────────────────────────────────────────────────────────
# [1] SYMBOLS & MARKET INFO
# ────────────────────────────────────────────────────────────────────────────

async def phase_symbols_and_market_info(svc: "MT5Service", selected: str) -> None:
    """Warm-up selection, fetch params/tick/margin/session for target symbols."""
    box("1) 📈 Symbols & Market info")

    # Pre-select symbols for quicker first responses (and potential ALT)
    try:
        await svc.symbol_select(selected, True)
        alt = globals().get("ALT_SYMBOL")
        if alt and alt != selected:
            await svc.symbol_select(alt, True)
    except Exception as e:
        print("symbol_select failed:", e)

    # Params (digits/contract_size)
    try:
        syms: list[str] = [selected]
        alt = globals().get("ALT_SYMBOL")
        if alt and alt not in syms:
            syms.append(alt)

        params = await svc.symbol_params_many(syms)
        for name, p in (params or {}).items():
            if not name:
                continue
            print("symbol_params:", name, {
                "digits": p.get("digits"),
                "contract_size": p.get("contract_size"),
            })
    except Exception as e:
        print("symbol_params_many failed:", e)

    # Last tick
    try:
        tick = await svc.symbol_info_tick(selected)
        print(f"{selected} tick:", tick)
    except Exception as e:
        print("symbol_info_tick failed:", e)

    # Margin rate (initial)
    try:
        mr = await svc.symbol_info_margin_rate(selected)
        imr = getattr(mr, "initial_margin_rate", None) or getattr(mr, "initial", None) or getattr(mr, "rate", None)
        print("symbol_info_margin_rate: initial_margin_rate=", imr)
    except Exception as e:
        print("symbol_info_margin_rate failed:", e)

    # Quote session info — optional per build
    try:
        sq = await svc.symbol_info_session_quote(selected)
        print("symbol_info_session_quote:", "ok" if sq is not None else "n/a")
    except Exception as e:
        print("symbol_info_session_quote failed:", e)


# ────────────────────────────────────────────────────────────────────────────
# [2] OPENED SNAPSHOT
# ────────────────────────────────────────────────────────────────────────────

async def phase_opened_state_snapshot(svc: "MT5Service", selected: str) -> None:
    """Inspect current opened positions/pending orders (tickets + small sample)."""
    box("2) 📂 Opened state snapshot (read-only)")

    # positions_total
    try:
        total = await svc.positions_total()
        print("positions_total:", getattr(total, "total_positions", total))
    except Exception as e:
        print("positions_total failed:", e)

    # tickets
    try:
        tmsg = await svc.opened_orders_tickets()
        pos_tickets = list(getattr(tmsg, "opened_position_tickets", []))
        pend_tickets = list(getattr(tmsg, "opened_pending_tickets",
                                    getattr(tmsg, "opened_order_tickets", [])))
        print("opened_position_tickets:", pos_tickets)
        print("opened_pending_tickets:", pend_tickets)
    except Exception as e:
        print("opened_orders_tickets failed:", e)

    # detailed objects (if build supports opened_orders proto)
    try:
        from google.protobuf.json_format import MessageToDict
        omsg = await svc.opened_orders()
        d = MessageToDict(omsg, preserving_proto_field_name=True)
        pos  = d.get("positions") or d.get("opened_positions") or []
        pend = d.get("orders")    or d.get("opened_orders")    or []
        print(f"opened_orders: pos={len(pos)} pend={len(pend)}")
        if pos:
            first = pos[0]
            small = {k: first.get(k) for k in ("ticket","symbol","volume","price_open","price_current","profit") if k in first}
            print("first_position:", small or first)
        if pend:
            firstp = pend[0]
            smallp = {k: firstp.get(k) for k in ("ticket","symbol","volume","price_open","price_current","type") if k in firstp}
            print("first_pending:", smallp or firstp)
    except AttributeError:
        print("opened_orders: method not found in this build")
    except Exception as e:
        print("opened_orders failed:", repr(e))

    # best-effort JSON snapshot (service-side aggregator)
    try:
        snap = await svc.opened_snapshot()
        print("positions_count:", len(snap["positions"]))
        print("pending_orders_count:", len(snap["pending"]))
        if snap["positions"] and snap["positions"][0]:
            print("first_position:", snap["positions"][0])
    except Exception as e:
        print("opened_snapshot failed:", e)


# ────────────────────────────────────────────────────────────────────────────
# [3] CALCULATIONS
# ────────────────────────────────────────────────────────────────────────────

async def phase_calculations_and_checks(svc: "MT5Service", symbol: str) -> None:
    """Show profit/margin calculators using safe pseudo-prices if needed."""
    box("3) 🧮 Calculations & dry-run checks")
    try:
        tick = await svc.symbol_info_tick(symbol)
        bid = getattr(tick, "bid", None) or getattr(tick, "Bid", None)
        ask = getattr(tick, "ask", None) or getattr(tick, "Ask", None)
        p_open = float(bid or ask or 1.0)
        p_close = p_open + 0.0003
    except Exception as e:
        print("tick read failed:", e)
        p_open, p_close = 1.0, 1.0003

    try:
        profit = await calc_profit(
            svc, symbol, 0.10, "BUY",
            price_open=p_open, price_close=p_close
        )
        print("order_calc_profit:", round(_as_float(profit), 2))
    except Exception as e:
        print("order_calc_profit failed:", e)

    try:
        margin = await calc_margin(svc, symbol, 0.10, "BUY")
        print("order_calc_margin:", round(_as_float(margin), 2))
    except Exception as e:
        print("order_calc_margin failed:", e)


# ────────────────────────────────────────────────────────────────────────────
# [4] CHARTS/COPY & DOM
# ────────────────────────────────────────────────────────────────────────────

async def phase_charts_and_dom(svc: "MT5Service", selected: str) -> None:
    """Copy rates/ticks via best-effort adapters; optional DOM probe."""
    box("4) 🕰 Charts/Copy & 📚 Market Book (DOM)")

    # get server now in seconds (with local fallback)
    async def _server_now_sec() -> int:
        try:
            st = await svc.server_time()
            if hasattr(st, "seconds"):
                return int(st.seconds)
            if isinstance(st, (int, float)):
                return int(st)
        except Exception:
            pass
        return int(time.time())

    now = await _server_now_sec()

    # Safe defaults; can be overridden via global PHASE4_OPTS in main
    PHASE4_OPTS = dict({
        "bars_lookback_days": 7,
        "ticks_lookback_days": 2,
        "rates_timeframes":   ("H1", "M15"),
        "max_rates":          800,
        "max_ticks":          20000,
        "tick_flags":         (3,),
        "do_dom":             True,
    }, **globals().get("PHASE4_OPTS", {}))

    bars_from  = now - PHASE4_OPTS["bars_lookback_days"]  * 24 * 3600
    ticks_from = now - PHASE4_OPTS["ticks_lookback_days"] * 24 * 3600

    async def _copy_rates_range(tf: str):
        try:
            bars = await svc.copy_rates_range_best(
                symbol=selected,
                timeframe=tf,
                ts_from=bars_from,
                ts_to=now,
                count=PHASE4_OPTS["max_rates"],
            )
            print(f"copy_rates_range: tf={tf} -> {len(bars) if bars else 0} items")
        except Exception as e:
            print(f"copy_rates_range failed (tf={tf}): {e!r}")
            print(f"copy_rates_range: tf={tf} -> 0 items")

    async def _copy_rates_from_pos(tf: str):
        try:
            bars = await svc.copy_rates_from_pos_best(
                symbol=selected,
                timeframe=tf,
                start_pos=0,
                count=min(400, PHASE4_OPTS['max_rates']),
            )
            print(f"copy_rates_from_pos: tf={tf} -> {len(bars) if bars else 0} items")
        except Exception as e:
            print(f"copy_rates_from_pos failed (tf={tf}): {e!r}")
            print(f"copy_rates_from_pos: tf={tf} -> 0 items")

    async def _copy_ticks_range():
        for flg in PHASE4_OPTS["tick_flags"]:
            try:
                ticks = await svc.copy_ticks_range_best(
                    symbol=selected,
                    ts_from=ticks_from,
                    ts_to=now,
                    flags=flg,
                    count=PHASE4_OPTS["max_ticks"],
                )
                print(f"copy_ticks_range: flags={flg} -> {len(ticks) if ticks else 0} items")
                return
            except Exception as e:
                print(f"copy_ticks_range failed (flags={flg}): {e!r}")
        print("copy_ticks_range: 0 items")

    for tf in PHASE4_OPTS["rates_timeframes"]:
        await _copy_rates_range(tf)
    for tf in PHASE4_OPTS["rates_timeframes"]:
        await _copy_rates_from_pos(tf)
    await _copy_ticks_range()


# ────────────────────────────────────────────────────────────────────────────
# [5] HISTORY & LOOKUPS
# ────────────────────────────────────────────────────────────────────────────

async def phase_history_and_lookups(svc: "MT5Service") -> None:
    """Pull orders/positions pages and a small deals sample for quick checks."""
    box("5) 🗂 History & ticketed lookups")
    from google.protobuf.json_format import MessageToDict

    HISTORY_DAYS = int(globals().get("HISTORY_DAYS", 7))

    now_ = datetime.now(timezone.utc)
    frm  = now_ - timedelta(days=HISTORY_DAYS)

    # Orders history — flat list (first page)
    try:
        items = await svc.orders_history(from_dt=frm, to_dt=now_, fetch_all=False, size=100)
        print(f"order_history(last {HISTORY_DAYS}d): {len(items)} items (show up to 5)")
        for it in items[:5]:
            ticket = getattr(it, "ticket", None) or getattr(it, "order", None) or getattr(it, "id", None) or "?"
            sym    = getattr(it, "symbol", None) or getattr(it, "symbol_name", None) or ""
            side   = (str(getattr(it, "type", "") or getattr(it, "order_type", "") or
                         getattr(it, "deal_type", "") or getattr(it, "side", ""))).upper()
            print(f"  - {ticket}  {sym}  {side}")
    except Exception as e:
        print("order_history: error:", repr(e))

    # Positions history — single page (if available)
    try:
        ph = await svc.positions_history(open_from=frm, open_to=now_, page=0, size=50)
        if ph is None:
            print("positions_history: n/a in this build")
        else:
            d = MessageToDict(ph, preserving_proto_field_name=True)
            pitems = d.get("items") or d.get("positions") or []
            print(f"positions_history(last {HISTORY_DAYS}d): {len(pitems)} items (show up to 5)")
            for it in pitems[:5]:
                t = it.get("ticket") or it.get("position") or it.get("id") or "?"
                print("  -", t)
    except Exception as e:
        print("positions_history: error:", repr(e))

    # Deals total + small sample
    try:
        if hasattr(svc, "history_deals_total"):
            total = await svc.history_deals_total(frm, now_)
            print(f"deals_total(last {HISTORY_DAYS}d): {total if total is not None else 'n/a'}")
        else:
            print("deals_total: n/a in this build")

        if hasattr(svc, "history_deals_get"):
            sample = await svc.history_deals_get(frm, now_, limit=3, page_size=200)
            if sample:
                print("deals_sample (up to 3):")
                for it in sample[:3]:
                    ticket = getattr(it, "ticket", None) or getattr(it, "order", None) or getattr(it, "id", None) or "?"
                    sym    = getattr(it, "symbol", None) or getattr(it, "symbol_name", None) or ""
                    side   = (str(getattr(it, "type", "") or getattr(it, "order_type", "") or
                                 getattr(it, "deal_type", "") or getattr(it, "side", ""))).upper()
                    price  = getattr(it, "price", None) or getattr(it, "price_open", None) or getattr(it, "price_close", None) or ""
                    print(f"  - {ticket}  {sym}  {side}  {price}")
            else:
                print("deals_sample: 0 items")
        else:
            print("deals_sample: n/a in this build")
    except Exception as e:
        print("deals: error:", repr(e))


# ────────────────────────────────────────────────────────────────────────────
# [6] STREAMING (compact) — thin wrapper for visual symmetry
# ────────────────────────────────────────────────────────────────────────────

async def phase_streams_wrapper(svc: "MT5Service") -> None:
    """
    Print a section header and delegate to app.services.streams_service.phase_streams_compact.
    Pure wrapper for visual consistency; avoids circular imports via lazy import.
    """
    box("6) 📡 Streaming (compact)")
    try:
        # Lazy import to avoid circular deps in some app layouts
        from app.services.streams_service import phase_streams_compact
    except Exception as e:
        print("streaming unavailable:", repr(e))
        return

    # Pick symbols: SELECTED + ALT (if present), keep defaults minimal
    sel = globals().get("SELECTED_SYMBOL") or "EURUSD"
    alt = globals().get("ALT_SYMBOL")
    symbols = [s for s in (sel, alt) if s]

    # Defaults mirror main.py; kwargs remain explicit and conservative
    await phase_streams_compact(
        svc,
        symbols,
        enable_ticks=True,
        enable_opened=True,
        enable_pnl=False,
        duration_ticks=6,
        duration_opened=4,
        throttle=1.0,
        bootstrap_timeout=0.4,
    )


# ────────────────────────────────────────────────────────────────────────────
# [7] TRADING OPS — preset & safe runner
# ────────────────────────────────────────────────────────────────────────────
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradingPlan:
    # Basic
    symbol: str
    volume: float = 0.01
    side: str = "BUY"            # "BUY" | "SELL"
    # Market
    do_market: bool = True
    do_market_modify: bool = True
    do_market_close: bool = True
    # Pending
    do_buy_limit: bool = True    # For SELL side you might use sell_limit symmetrically
    do_pending_modify: bool = True
    do_pending_cancel: bool = True
    # Safety
    dry_run: bool = True         # Default: print only, do not send orders
    max_volume: float = 0.10     # Hard safety cap
    price_offset_points: int = 30  # Offset for limit price (≈3 pips on 5-digit FX)
    # SL/TP/expiration
    sl: Optional[float] = None
    tp: Optional[float] = None
    expiration_ts: Optional[int] = None   # Unix seconds

def _point_for(symbol_tick_price: float) -> float:
    """Coarse point size guess: price < 10 → 0.0001, else 0.01."""
    return 0.0001 if symbol_tick_price and symbol_tick_price < 10 else 0.01

async def phase_trading_ops_preset(svc: "MT5Service", plan: TradingPlan) -> None:
    """
    Safe trading preset runner:
    • Enforces volume cap and dry-run by default.
    • MARKET open → optional MODIFY → CLOSE by symbol.
    • Optional BUY/SELL LIMIT → optional MODIFY → CANCEL.
    """
    box("7) 🚦 Trading preset (safe)")

    # Safety: reject suspicious volumes up-front
    if plan.volume <= 0 or plan.volume > plan.max_volume:
        print(f"abort: volume {plan.volume} exceeds safety limit {plan.max_volume}")
        return

    sym = plan.symbol
    try:
        await svc.symbol_select(sym, True)
    except Exception:
        pass

    # Tick + point estimation
    try:
        tick = await svc.symbol_info_tick(sym)
        bid = float(getattr(tick, "bid", None) or getattr(tick, "Bid", 0.0) or 0.0)
        ask = float(getattr(tick, "ask", None) or getattr(tick, "Ask", 0.0) or 0.0)
        px  = bid or ask or 0.0
    except Exception:
        bid = ask = px = 0.0
    point = _point_for(px)

    # MARKET
    market_ticket = None
    if plan.do_market:
        print(f"MARKET {plan.side} {sym} vol={plan.volume} dry_run={plan.dry_run}")
        if not plan.dry_run:
            try:
                if plan.side.upper() == "BUY":
                    r = await svc.buy_market(sym, plan.volume, sl=plan.sl, tp=plan.tp)
                else:
                    r = await svc.sell_market(sym, plan.volume, sl=plan.sl, tp=plan.tp)
                try:
                    from google.protobuf.json_format import MessageToDict
                    d = MessageToDict(r, preserving_proto_field_name=True) if r else {}
                except Exception:
                    d = r if isinstance(r, dict) else {"repr": repr(r)}
                print("  result:", d or r)
                for k in ("position","ticket","order","deal","id","order_ticket"):
                    if isinstance(d, dict) and d.get(k):
                        market_ticket = str(d[k]); break
            except Exception as e:
                print("  market error:", repr(e))
        else:
            print("  (dry-run) skipped sending")

    # MODIFY (if position ticket could be determined)
    if market_ticket and plan.do_market_modify and hasattr(svc, "position_modify"):
        print(f"MODIFY position {market_ticket}")
        if not plan.dry_run:
            try:
                await svc.position_modify(ticket=int(market_ticket), sl=plan.sl, tp=plan.tp)
                print("  OK")
            except Exception as e:
                print("  error:", repr(e))
        else:
            print("  (dry-run) skipped")

    # CLOSE by symbol (requires keyword arg per some builds)
    if plan.do_market_close:
        print(f"CLOSE position {sym} (by symbol)")
        if not plan.dry_run:
            try:
                await svc.position_close(symbol=sym)  # ← keyword required in several builds
                print("  OK")
            except Exception as e:
                print("  error:", repr(e))
        else:
            print("  (dry-run) skipped")

    # LIMIT pending: place → optional modify → optional cancel
    pend_ticket = None
    do_limit = plan.do_buy_limit if plan.side.upper() == "BUY" else plan.do_buy_limit
    if do_limit:
        if plan.side.upper() == "BUY":
            limit_price = float(f"{max(bid - plan.price_offset_points * point, 0):.5f}") if bid else None
            name = "BUY_LIMIT"
        else:
            limit_price = float(f"{ask + plan.price_offset_points * point:.5f}") if ask else None
            name = "SELL_LIMIT"

        print(f"{name} {sym} vol={plan.volume} at {limit_price} dry_run={plan.dry_run}")
        if not plan.dry_run and limit_price:
            try:
                if plan.side.upper() == "BUY":
                    r = await svc.place_buy_limit(sym, plan.volume, limit_price, sl=plan.sl, tp=plan.tp, expiration=plan.expiration_ts)
                else:
                    r = await svc.place_sell_limit(sym, plan.volume, limit_price, sl=plan.sl, tp=plan.tp, expiration=plan.expiration_ts)
                try:
                    from google.protobuf.json_format import MessageToDict
                    d = MessageToDict(r, preserving_proto_field_name=True) if r else {}
                except Exception:
                    d = r if isinstance(r, dict) else {"repr": repr(r)}
                print("  result:", d or r)
                for k in ("ticket","order","id","order_ticket"):
                    if isinstance(d, dict) and d.get(k):
                        pend_ticket = str(d[k]); break
            except Exception as e:
                print("  pending error:", repr(e))
        elif plan.dry_run:
            print("  (dry-run) skipped sending")

    # Pending modify
    if pend_ticket and plan.do_pending_modify and hasattr(svc, "pending_modify"):
        print(f"PENDING MODIFY ticket={pend_ticket}")
        if not plan.dry_run:
            try:
                await svc.pending_modify(ticket=int(pend_ticket), price=None, sl=plan.sl, tp=plan.tp)
                print("  OK")
            except Exception as e:
                print("  error:", repr(e))
        else:
            print("  (dry-run) skipped")

    # Pending cancel
    if pend_ticket and plan.do_pending_cancel and hasattr(svc, "cancel_order"):
        print(f"PENDING CANCEL ticket={pend_ticket}")
        if not plan.dry_run:
            try:
                await svc.cancel_order(ticket=int(pend_ticket))
                print("  OK")
            except Exception as e:
                print("  error:", repr(e))
        else:
            print("  (dry-run) skipped")


async def show_trading_ops_examples(_: "MT5Service") -> None:
    """Short help: prefer phase_trading_ops_preset for safe, bounded actions."""
    box("7) ⚠ Trading ops — how to run safely")
    print(
        "Use phase_trading_ops_preset(svc, TradingPlan(...)). "
        "By default dry_run=True (no orders sent). "
        "Enable dry_run=False deliberately."
    )


# ────────────────────────────────────────────────────────────────────────────
# [7A] DANGER ZONE — stepwise smoke
# ────────────────────────────────────────────────────────────────────────────

async def phase_danger_zone_stepwise(svc: "MT5Service", symbol: str) -> None:
    """
    Cautious live sequence:
    MARKET BUY → MODIFY → CLOSE, then BUY_LIMIT → MODIFY → CANCEL.
    Uses retries and delta-detection for tickets when bridge is slow.
    """
    box("7A) ⚠ DANGER ZONE — stepwise")

    # --- helpers in scope ---
    def has(name: str) -> bool:
        return callable(getattr(svc, name, None))

    def _err_str(e: Exception) -> str:
        return f"{type(e).__name__}: {e!r}"

    def _is_unavailable_status(raw_dict: dict) -> bool:
        """Detect transient UNAVAILABLE gRPC errors in wrapped result dicts."""
        try:
            err = (raw_dict or {}).get("error", {})
            em = str(err.get("error_message", ""))
            ec = str(err.get("error_code", ""))
            return (
                'StatusCode="Unavailable"' in em
                or "UNAVAILABLE" in em.upper()
                or ec.startswith("GRPC_CLIENT_LIBRARY_METHOD_EXECUTION")
            )
        except Exception:
            return False

    async def _get_open_tickets():
        """Fetch sets of position/pending tickets for delta-detection."""
        try:
            tmsg = await svc.opened_orders_tickets()
            pos  = {str(x) for x in (getattr(tmsg, "opened_position_tickets", []) or [])}
            pend = {str(x) for x in (getattr(tmsg, "opened_pending_tickets",
                                             getattr(tmsg, "opened_order_tickets", [])) or [])}
            return pos, pend
        except Exception:
            return set(), set()

    async def _retry_call(factory, attempts: int = 2, delay: float = 1.2):
        """Simple retry helper for flaky bridges."""
        last = None
        for i in range(1, attempts + 1):
            try:
                return await factory()
            except Exception as e:
                last = e
                print(f"  retry {i}/{attempts} failed with {_err_str(e)}")
                if i < attempts:
                    await asyncio.sleep(delay)
        if last:
            raise last

    # --- choose symbol ---
    candidates: list[str] = []
    if symbol:
        candidates.append(symbol)
    alt = globals().get("ALT_SYMBOL")
    if alt and alt not in candidates:
        candidates.append(alt)
    crypto = globals().get("CRYPTO_SYMBOL")
    if crypto and crypto not in candidates:
        candidates.append(crypto)

    chosen: str | None = None
    for sym in candidates:
        from app.services.phases import is_trading_open_now  # local reuse
        verdict, reason = await is_trading_open_now(svc, sym)
        tag = {True: "OPEN", False: "CLOSED", None: "UNKNOWN"}[verdict]
        print(f"pre-check {sym}: {tag} ({reason})")
        if verdict is True and chosen is None:
            chosen = sym
    if not chosen:
        chosen = candidates[0] if candidates else symbol

    # (optional) log trade permission exposure
    try:
        ai = await svc.account_info()
        may_trade = getattr(ai, "trade_allowed", None) or getattr(ai, "TradeAllowed", None) \
                    or getattr(ai, "trade_expert", None) or getattr(ai, "TradeExpert", None)
        print("preflight: trade_allowed≈", bool(may_trade))
    except Exception:
        pass

    # 1) MARKET BUY 0.01
    buy_ticket = None
    before_pos, before_pend = await _get_open_tickets()
    try:
        if has("buy_market"):
            r = await _retry_call(lambda: svc.buy_market(chosen, 0.01, sl=None, tp=None))
        else:
            async def _send():
                try:
                    return await svc.order_send_ex(action="MARKET", side="BUY", symbol=chosen, volume=0.01)
                except TypeError:
                    return await svc.order_send_ex(action="DEAL", side="BUY", symbol=chosen, volume=0.01)
            r = await _retry_call(_send)

        # extract result
        try:
            from google.protobuf.json_format import MessageToDict
            raw = MessageToDict(r, preserving_proto_field_name=True)
        except Exception:
            raw = r if isinstance(r, dict) else {"repr": repr(r)}
        t = None
        for k in ("ticket","order","id","position","order_ticket","deal"):
            if k in raw and raw[k]:
                t = str(raw[k]); break
        print("BUY raw:", raw)
        buy_ticket = t

        if not buy_ticket and _is_unavailable_status(raw):
            print("BUY detected UNAVAILABLE → warm-up & retry…")
            if has("buy_market"):
                r2 = await _retry_call(lambda: svc.buy_market(chosen, 0.01, sl=None, tp=None), attempts=1)
            else:
                r2 = await _retry_call(_send, attempts=1)
            try:
                from google.protobuf.json_format import MessageToDict
                raw2 = MessageToDict(r2, preserving_proto_field_name=True)
            except Exception:
                raw2 = r2 if isinstance(r2, dict) else {"repr": repr(r2)}
            print("BUY raw#2:", raw2)
            for k in ("ticket","order","id","position","order_ticket","deal"):
                if k in raw2 and raw2[k]:
                    buy_ticket = str(raw2[k]); break
    except Exception as e:
        print("open failed:", _err_str(e))

    if not buy_ticket:
        # Delta-detect new position ticket if bridge hides it in response
        await asyncio.sleep(1.0)
        after_pos, _ = await _get_open_tickets()
        delta = list(after_pos - before_pos)
        if len(delta) == 1:
            buy_ticket = delta[0]
            print("BUY delta-detected ticket:", buy_ticket)
        else:
            print("BUY: no ticket detected (bridge may be read-only or market closed)")

    # 2) MODIFY
    if buy_ticket and has("position_modify"):
        try:
            await svc.position_modify(ticket=buy_ticket, sl=None, tp=None)
            print("position_modify OK:", buy_ticket)
        except Exception as e:
            print("position_modify error:", _err_str(e))

    # 3) CLOSE
    if buy_ticket:
        if has("order_close"):
            try:
                await svc.order_close(buy_ticket)
                print("order_close OK:", buy_ticket)
            except Exception as e:
                print("order_close error:", _err_str(e))
        elif has("position_close"):
            try:
                await svc.position_close(chosen)
                print("position_close OK")
            except Exception as e:
                print("position_close error:", _err_str(e))

    # 4) BUY LIMIT → MODIFY → CANCEL
    pend_ticket = None
    _, before_pend = await _get_open_tickets()

    if has("place_buy_limit"):
        try:
            tick = await svc.symbol_info_tick(chosen)
            bid = float(getattr(tick, "bid", None) or getattr(tick, "Bid", 0.0) or 0.0)

            # Simple point guess (FX): price < 10 → 0.0001, else 0.01
            point = 0.0001 if bid and bid < 10 else 0.01
            # Far enough to avoid instant fill
            price = float(f"{max(bid - 30 * point, 0):.5f}") if bid else None
            print(f"placing BUY_LIMIT at {price} (bid={bid}, point={point})")

            async def _place():
                return await svc.place_buy_limit(chosen, 0.01, price, sl=None, tp=None, expiration=None)

            r = await _retry_call(_place)
            try:
                from google.protobuf.json_format import MessageToDict
                raw = MessageToDict(r, preserving_proto_field_name=True)
            except Exception:
                raw = r if isinstance(r, dict) else {"repr": repr(r)}
            print("BUY_LIMIT raw:", raw)

            for k in ("ticket","order","id","position","order_ticket","deal"):
                if k in raw and raw[k]:
                    pend_ticket = str(raw[k]); break

            if not pend_ticket and _is_unavailable_status(raw):
                print("BUY_LIMIT detected UNAVAILABLE → retry…")
                r2 = await _retry_call(_place, attempts=1)
                try:
                    from google.protobuf.json_format import MessageToDict
                    raw2 = MessageToDict(r2, preserving_proto_field_name=True)
                except Exception:
                    raw2 = r2 if isinstance(r2, dict) else {"repr": repr(r2)}
                print("BUY_LIMIT raw#2:", raw2)
                for k in ("ticket","order","id","position","order_ticket","deal"):
                    if k in raw2 and raw2[k]:
                        pend_ticket = str(raw2[k]); break

        except Exception as e:
            print("place_buy_limit:", _err_str(e))

    if not pend_ticket:
        # Delta-detect pending ticket in slower bridges
        await asyncio.sleep(1.0)
        _, after_pend = await _get_open_tickets()
        delta = list(after_pend - before_pend)
        if len(delta) == 1:
            pend_ticket = delta[0]
            print("BUY_LIMIT delta-detected ticket:", pend_ticket)
        else:
            print("no pending ticket detected")

    if pend_ticket and has("pending_modify"):
        try:
            await svc.pending_modify(ticket=pend_ticket, price=None, sl=None, tp=None)
            print("pending_modify OK:", pend_ticket)
        except Exception as e:
            print("pending_modify error:", _err_str(e))

    if pend_ticket and has("cancel_order"):
        try:
            await svc.cancel_order(ticket=pend_ticket)
            print("cancel_order OK:", pend_ticket)
        except Exception as e:
            print("cancel_order error:", _err_str(e))

    print("LIVE: done")



async def dump_trading_capabilities(svc: "MT5Service") -> None:
    """Enumerate available trading stubs and list their public RPC methods."""
    print("\n🔎 Trading capabilities dump")
    acc = getattr(svc, "acc", None)
    if acc is None:
        print("  acc: <none>")
        return
    client_names = [
        "trade_functions_client","trade_client","trading_client",
        "orders_client","positions_client","deals_client","order_client","dealing_client",
        "account_helper_client",
    ]
    found_any = False
    for nm in client_names:
        stub = getattr(acc, nm, None)
        if not stub:
            continue
        found_any = True
        clsname = getattr(type(stub), "__name__", type(stub))
        print(f"  • {nm}: {clsname}")
        methods = []
        for attr in dir(stub):
            if not attr or attr.startswith("_"):
                continue
            try:
                val = getattr(stub, attr)
                if callable(val) and attr[:1].isupper():
                    methods.append(attr)
            except Exception:
                pass
        for m in sorted(methods):
            print(f"     - {m}")
    if not found_any:
        print("  no trading clients found (build may be read-only)")


__all__ = [
    "box", "run_once", "is_trading_open_now",
    "phase_connectivity_and_account",
    "phase_symbols_and_market_info",
    "phase_opened_state_snapshot",
    "phase_calculations_and_checks",
    "phase_charts_and_dom",
    "phase_history_and_lookups",
    "phase_streams_wrapper",
    "show_trading_ops_examples",
    "phase_danger_zone_stepwise",
    "dump_trading_capabilities",
]
