from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional, Tuple

"""
╔════════════════════════════════════════════════════════════════════════════╗
║ FILE app/services/streams_service.py — streaming helpers & phases          ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                    ║
║ • Provide compact streaming phases with push bootstrap and poll fallback.  ║
║ • De-noise console output via rate limits & tick de-duplication.           ║
║                                                                            ║
║ What it streams                                                            ║
║ • Ticks per symbol list (svc.on_symbol_tick or poll symbol_info_tick).     ║
║ • Opened tickets counts (svc.on_positions_and_pending_orders_tickets).     ║
║ • Optional position PnL snapshots (when the build supports it).            ║
║                                                                            ║
║ Behavior                                                                   ║
║ • Try push first; if no event arrives within bootstrap_timeout, fall back  ║
║   to polling (when a safe poll exists).                                    ║
║ • Silence duplicates: print only meaningful changes at a sane cadence.     ║
║                                                                            ║
║ Safety                                                                     ║
║ • Read-only; auto-selects symbols; tries subscribe_* if available.         ║
║ • Never raises on missing APIs — prints short notes instead.               ║
║                                                                            ║
║ Entrypoints                                                                ║
║ • phase_streams_compact(svc, symbols, ...)  ← default, quiet               ║
║ • phase_streams_quotes_only(svc, symbols, ...)                             ║
║ • phase_streams_verbose(svc, symbols, ...)  ← louder but rate-limited      ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# ────────────────────────────────────────────────────────────────────────────
# helpers
# ────────────────────────────────────────────────────────────────────────────

def _safe_get(obj, *names, default=None):
    """Get first present attribute/key from names; return default on miss."""
    for n in names:
        if isinstance(obj, dict):
            if n in obj:
                return obj[n]
        elif hasattr(obj, n):
            return getattr(obj, n)
    return default

async def _ensure_selected(svc, symbols: Iterable[str]) -> None:
    """Best-effort pre-selection for all symbols (awaits if coroutine)."""
    for s in symbols:
        try:
            r = svc.symbol_select(s, True)
            if asyncio.iscoroutine(r):
                await r
        except Exception:
            pass

async def _subscribe_if_possible(svc, symbols: Iterable[str]) -> Optional[str]:
    """Try known subscribe methods on svc or svc.acc; return the name used."""
    for name in ("subscribe_ticks", "quotes_subscribe", "ticks_subscribe"):
        fn = getattr(svc, name, None) or getattr(getattr(svc, "acc", None), name, None)
        if callable(fn):
            try:
                r = fn(list(symbols))
                if asyncio.iscoroutine(r):
                    await r
                return name
            except Exception:
                pass
    return None

async def _symbol_points_map(svc, symbols: Iterable[str]) -> Dict[str, float]:
    """
    Build symbol→point map using symbol_params_many(digits) when possible.
    Fallback: heuristic (0.0001 for FX-like, else 0.01).
    """
    out: Dict[str, float] = {}
    try:
        names = list(dict.fromkeys(symbols))  # uniq, preserve order
        params = await svc.symbol_params_many(names)
        for nm, p in (params or {}).items():
            digits = None
            if isinstance(p, dict):
                digits = p.get("digits")
            else:
                for k in ("digits", "Digits"):
                    if hasattr(p, k):
                        digits = getattr(p, k); break
            if isinstance(digits, (int, float)):
                out[str(nm)] = 10 ** (-int(digits))
    except Exception:
        pass
    # heuristic defaults per symbol not filled above
    for s in symbols:
        out.setdefault(s, 0.0001 if any(ch.isalpha() for ch in s) else 0.01)
    return out

# generic stream runner with push bootstrap + poll fallback
async def _run_stream_with_poll_fallback(
    agen_factory: Callable[[], Any],
    on_event: Callable[[Any], Awaitable[None]],
    poll_fn: Callable[[], Awaitable[Any]] | None,
    *,
    duration: float,
    throttle: float = 1.0,
    bootstrap_timeout: float = 0.5,
    name: str = "stream",
) -> dict:
    """
    Strategy:
      1) Create async generator (push). Wait <= bootstrap_timeout for first evt.
      2) If no push, use poll_fn at 'throttle' cadence (when provided).
      3) Ensure aclose() on generator when finishing.
    Returns: {"used_stream": bool, "events": int}
    """
    loop = asyncio.get_running_loop()
    end = loop.time() + max(duration, 0.1)
    it = None
    used_stream = False
    cnt = 0

    try:
        # Bootstrap: wait first push event, otherwise fall back
        try:
            it = agen_factory()
            first = await asyncio.wait_for(it.__anext__(), timeout=bootstrap_timeout)
            await on_event(first)
            cnt += 1
            used_stream = True
        except (asyncio.TimeoutError, StopAsyncIteration):
            used_stream = False
        except Exception:
            used_stream = False

        if used_stream:
            # Main push loop (bounded by timeout + throttle)
            while loop.time() < end:
                try:
                    msg = await asyncio.wait_for(
                        it.__anext__(),
                        timeout=max(throttle, 0.1) + 0.5
                    )
                    await on_event(msg)
                    cnt += 1
                except asyncio.TimeoutError:
                    pass
                except StopAsyncIteration:
                    break
                await asyncio.sleep(throttle)
        else:
            # Poll fallback (only if safe polling function exists)
            if poll_fn is None:
                print(f"  {name}: skip (no push & no poll)")
                return {"used_stream": used_stream, "events": cnt}
            while loop.time() < end:
                try:
                    msg = await poll_fn()
                    if msg is None:
                        print(f"  {name}: skip (poll not supported)")
                        break
                    await on_event(msg)
                    cnt += 1
                except Exception:
                    print(f"  {name}: polling failed")
                    break
                await asyncio.sleep(throttle)
    finally:
        if it and hasattr(it, "aclose"):
            try:
                await it.aclose()
            except Exception:
                pass

    return {"used_stream": used_stream, "events": cnt}


# ────────────────────────────────────────────────────────────────────────────
# Anti-noise printers
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class _RateLimiter:
    """Simple per-stream frequency limiter (monotonic-time based)."""
    min_interval: float
    _last_ts: float = field(default=0.0)

    def allow(self) -> bool:
        now = time.monotonic()
        if now - self._last_ts >= self.min_interval:
            self._last_ts = now
            return True
        return False

@dataclass
class _TickDeduper:
    """
    Per-symbol deduper:
    • Prints first tick immediately.
    • Afterwards prints only if |Δbid| or |Δask| ≥ 1 point and rate-limit allows.
    """
    points: Dict[str, float]
    min_interval: float = 0.5
    _last: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # sym -> (bid, ask)
    _rate: Dict[str, _RateLimiter] = field(default_factory=dict)

    def changed(self, sym: str, bid: Optional[float], ask: Optional[float]) -> bool:
        pt = self.points.get(sym, 0.0001)
        last = self._last.get(sym)
        # print first time
        if last is None:
            self._last[sym] = (float(bid or 0.0), float(ask or 0.0))
            self._rate.setdefault(sym, _RateLimiter(self.min_interval))
            return True
        lb, la = last
        db = abs(float(bid or 0.0) - lb)
        da = abs(float(ask or 0.0) - la)
        # ignore micro-moves (< 1 point on both bid/ask)
        if db < pt and da < pt:
            return False
        # frequency guard
        rl = self._rate.setdefault(sym, _RateLimiter(self.min_interval))
        if not rl.allow():
            return False
        self._last[sym] = (float(bid or lb), float(ask or la))
        return True


# ────────────────────────────────────────────────────────────────────────────
# Public phases
# ────────────────────────────────────────────────────────────────────────────

def _banner(title: str) -> None:
    """ASCII section header for a phase."""
    print("\n" + "╔" + "═"*78 + "╗")
    print(("║ " + title).ljust(79, " ") + "║")
    print("╚" + "═"*78 + "╝")


async def phase_streams_compact(
    svc,
    symbols: list[str],
    *,
    enable_ticks: bool = True,
    enable_opened: bool = True,
    enable_pnl: bool = False,  # off by default — not every build supports it
    duration_ticks: float = 6.0,
    duration_opened: float = 4.0,
    duration_pnl: float = 4.0,
    throttle: float = 1.0,
    bootstrap_timeout: float = 0.4,
) -> None:
    """Quiet, de-duplicated streaming overview (ticks + opened + optional PnL)."""
    _banner("6) 📡 Streaming (compact)")

    if enable_ticks:
        print(f"• ticks ({len(symbols)} symbols, duration={int(duration_ticks)}s, throttle={int(throttle)}s)")
    if enable_opened:
        print(f"• opened tickets (duration={int(duration_opened)}s)")
    if enable_pnl:
        print(f"• position PnL (duration={int(duration_pnl)}s)")

    await _ensure_selected(svc, symbols)
    sub = await _subscribe_if_possible(svc, symbols)
    if sub:
        print(f"  (subscribed via {sub})")

    points = await _symbol_points_map(svc, symbols)
    dedup = _TickDeduper(points=points, min_interval=max(throttle, 0.5))

    tasks: list[asyncio.Task] = []

    if enable_ticks:
        async def run_ticks():
            async def on_ev(ev):
                sym = str(_safe_get(ev, "symbol", "Symbol", default=symbols[0]))
                bid = _safe_get(ev, "bid", "Bid", default=None)
                ask = _safe_get(ev, "ask", "Ask", default=None)
                if dedup.changed(sym, bid, ask):
                    print(f"  tick {sym}: {bid} / {ask}")
            res = await _run_stream_with_poll_fallback(
                agen_factory=lambda: svc.on_symbol_tick(symbols),
                on_event=on_ev,
                poll_fn=lambda: svc.symbol_info_tick(symbols[0]),
                duration=duration_ticks,
                throttle=throttle,
                bootstrap_timeout=bootstrap_timeout,
                name="ticks",
            )
            print(f"  ticks total: {res['events']}")
        tasks.append(asyncio.create_task(run_ticks()))

    if enable_opened:
        # print only when counts change; also rate-limit noisy bursts
        last_counts = {"pos": None, "pend": None}
        limiter = _RateLimiter(min_interval=max(throttle, 0.7))

        async def run_opened():
            async def on_ev(ev):
                pos = list(getattr(ev, "opened_position_tickets", []))
                pend = list(getattr(ev, "opened_pending_tickets",
                                    getattr(ev, "opened_order_tickets", [])))
                cp, cd = len(pos), len(pend)
                if (cp, cd) != (last_counts["pos"], last_counts["pend"]) and limiter.allow():
                    last_counts["pos"], last_counts["pend"] = cp, cd
                    print(f"  opened: pos={cp} pend={cd}")
            res = await _run_stream_with_poll_fallback(
                agen_factory=lambda: svc.on_positions_and_pending_orders_tickets(),
                on_event=on_ev,
                poll_fn=lambda: svc.opened_orders_tickets(),
                duration=duration_opened,
                throttle=throttle,
                bootstrap_timeout=bootstrap_timeout,
                name="opened",
            )
            print(f"  opened updates: {res['events']}")
        tasks.append(asyncio.create_task(run_opened()))

    if enable_pnl:
        limiter_pnl = _RateLimiter(min_interval=max(throttle, 1.0))

        async def run_pnl():
            async def on_ev(ev):
                # aggregate + rate-limit
                positions = list(getattr(ev, "positions", []))
                if not limiter_pnl.allow():
                    return
                profit_sum = 0.0
                for p in positions:
                    try:
                        profit_sum += float(getattr(p, "profit", 0.0) or 0.0)
                    except Exception:
                        pass
                print(f"  pnl: positions={len(positions)} profit_sum={round(profit_sum, 2)}")
            res = await _run_stream_with_poll_fallback(
                agen_factory=lambda: svc.on_position_profit(),
                on_event=on_ev,
                poll_fn=None,  # no safe polling analogue — skip if push not available
                duration=duration_pnl,
                throttle=throttle,
                bootstrap_timeout=bootstrap_timeout,
                name="pnl",
            )
            if res["events"] == 0 and not res["used_stream"]:
                print("  pnl: skip")
        tasks.append(asyncio.create_task(run_pnl()))

    if tasks:
        await asyncio.gather(*tasks)


# Narrow profile: quotes only, extra quiet
async def phase_streams_quotes_only(
    svc,
    symbols: list[str],
    *,
    duration: float = 8.0,
    throttle: float = 1.0,
    bootstrap_timeout: float = 0.4,
) -> None:
    """Only ticks for given symbols, with de-duplication and poll fallback."""
    _banner("6) 📡 Streaming — quotes only")

    await _ensure_selected(svc, symbols)
    sub = await _subscribe_if_possible(svc, symbols)
    if sub:
        print(f"  (subscribed via {sub})")

    points = await _symbol_points_map(svc, symbols)
    dedup = _TickDeduper(points=points, min_interval=max(throttle, 0.5))

    async def on_ev(ev):
        sym = str(_safe_get(ev, "symbol", "Symbol", default=symbols[0]))
        bid = _safe_get(ev, "bid", "Bid", default=None)
        ask = _safe_get(ev, "ask", "Ask", default=None)
        if dedup.changed(sym, bid, ask):
            print(f"  {sym}: {bid} / {ask}")

    res = await _run_stream_with_poll_fallback(
        agen_factory=lambda: svc.on_symbol_tick(symbols),
        on_event=on_ev,
        poll_fn=lambda: svc.symbol_info_tick(symbols[0]),
        duration=duration,
        throttle=throttle,
        bootstrap_timeout=bootstrap_timeout,
        name="ticks",
    )
    print(f"  ticks total: {res['events']}")


# Louder profile (debugging) but still rate-limited
async def phase_streams_verbose(
    svc,
    symbols: list[str],
    *,
    duration: float = 10.0,
    throttle: float = 0.5,
    bootstrap_timeout: float = 0.4,
) -> None:
    """Verbose streaming: ticks + opened counters; still protects from spam."""
    _banner("6) 📡 Streaming (verbose)")

    await _ensure_selected(svc, symbols)
    sub = await _subscribe_if_possible(svc, symbols)
    if sub:
        print(f"  (subscribed via {sub})")

    points = await _symbol_points_map(svc, symbols)
    dedup = _TickDeduper(points=points, min_interval=max(throttle, 0.4))

    last_opened = {"pos": None, "pend": None}
    limiter_opened = _RateLimiter(min_interval=max(throttle, 0.6))

    async def run_ticks():
        async def on_ev(ev):
            sym = str(_safe_get(ev, "symbol", "Symbol", default=symbols[0]))
            bid = _safe_get(ev, "bid", "Bid", default=None)
            ask = _safe_get(ev, "ask", "Ask", default=None)
            if dedup.changed(sym, bid, ask):
                print(f"  tick {sym}: {bid} / {ask}")
        await _run_stream_with_poll_fallback(
            agen_factory=lambda: svc.on_symbol_tick(symbols),
            on_event=on_ev,
            poll_fn=lambda: svc.symbol_info_tick(symbols[0]),
            duration=duration,
            throttle=throttle,
            bootstrap_timeout=bootstrap_timeout,
            name="ticks",
        )

    async def run_opened():
        async def on_ev(ev):
            pos = list(getattr(ev, "opened_position_tickets", []))
            pend = list(getattr(ev, "opened_pending_tickets",
                                getattr(ev, "opened_order_tickets", [])))
            cp, cd = len(pos), len(pend)
            if (cp, cd) != (last_opened["pos"], last_opened["pend"]) and limiter_opened.allow():
                last_opened["pos"], last_opened["pend"] = cp, cd
                print(f"  opened: pos={cp} pend={cd}")
        await _run_stream_with_poll_fallback(
            agen_factory=lambda: svc.on_positions_and_pending_orders_tickets(),
            on_event=on_ev,
            poll_fn=lambda: svc.opened_orders_tickets(),
            duration=max(4.0, duration / 2),
            throttle=throttle,
            bootstrap_timeout=bootstrap_timeout,
            name="opened",
        )

    await asyncio.gather(run_ticks(), run_opened())
