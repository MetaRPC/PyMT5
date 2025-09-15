"""
╔════════════════════════════════════════════════════════════════╗
║ FILE app/charts_copy_patch.py                                  ║
╠════════════════════════════════════════════════════════════════╣
║ Purpose: Add tolerant copy_* helpers to MT5Service that try    ║
║          multiple API names/arg-variants across different pb2.  ║
║ Adds:   MT5Service.copy_rates_range_best                       ║
║         MT5Service.copy_rates_from_pos_best                    ║
║         MT5Service.copy_ticks_range_best                       ║
║ Style:  Best-effort → iterate fn names & kw aliases → first OK.║
╚════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

# Best-effort wrapper over copy_rates_range-style methods:
# tries several function names + kw aliases (ts_from/from_ts/...).
async def _copy_rates_range_best(
    self, *,
    symbol: str,
    timeframe,
    ts_from: int,
    ts_to: int,
    count: int | None = None,
    count_max: int | None = None,
):
    variants = []
    # Some builds accept count, others count_max; some ignore both.
    for cnt_key in ("count", "count_max", None):
        base = dict(symbol=symbol, timeframe=timeframe)
        if cnt_key == "count":       base["count"] = count or count_max
        elif cnt_key == "count_max": base["count_max"] = count_max or count
        # Alternate arg names for range:
        variants += [
            dict(base, ts_from=ts_from, ts_to=ts_to),
            dict(base, from_ts=ts_from, to_ts=ts_to),
            dict(base, from_time=ts_from, to_time=ts_to),
            dict(base, start_ts=ts_from, end_ts=ts_to),
        ]

    for fn_name in ("copy_rates_range", "copy_rates", "rates_range", "copy_rates_range_ex"):
        fn = getattr(self, fn_name, None)
        if not callable(fn):
            continue
        for kw in variants:
            try:
                return await fn(**kw)
            except TypeError:
                # wrong signature for this variant — try next
                continue
            except Exception:
                # runtime/server error — try next variant anyway
                continue
    return []  # uniform “empty” fallback


# Best-effort wrapper for positional copy of bars by start index.
async def _copy_rates_from_pos_best(self, *, symbol: str, timeframe, start_pos: int, count: int):
    variants = [
        dict(symbol=symbol, timeframe=timeframe, start_pos=start_pos,      count=count),
        dict(symbol=symbol, timeframe=timeframe, start_position=start_pos, count=count),
        dict(symbol=symbol, timeframe=timeframe, position=start_pos,       count=count),
    ]
    for fn_name in ("copy_rates_from_pos", "copy_rates_from_position", "rates_from_pos"):
        fn = getattr(self, fn_name, None)
        if not callable(fn):
            continue
        for kw in variants:
            try:
                return await fn(**kw)
            except TypeError:
                continue
            except Exception:
                continue
    return []


# Best-effort wrapper over copy_ticks_range-style methods.
async def _copy_ticks_range_best(
    self, *,
    symbol: str,
    ts_from: int,
    ts_to: int,
    flags: int,
    count: int | None = None,
    count_max: int | None = None,
):
    variants = []
    for cnt_key in ("count", "count_max", None):
        base = dict(symbol=symbol, flags=flags)
        if cnt_key == "count":       base["count"] = count or count_max
        elif cnt_key == "count_max": base["count_max"] = count_max or count
        variants += [
            dict(base, ts_from=ts_from, ts_to=ts_to),
            dict(base, from_ts=ts_from, to_ts=ts_to),
            dict(base, from_time=ts_from, to_time=ts_to),
            dict(base, start_ts=ts_from, end_ts=ts_to),
        ]

    for fn_name in ("copy_ticks_range", "copy_ticks", "ticks_range"):
        fn = getattr(self, fn_name, None)
        if not callable(fn):
            continue
        for kw in variants:
            try:
                return await fn(**kw)
            except TypeError:
                continue
            except Exception:
                continue
    return []


# Patch the helpers onto MT5Service (no hard fail if service is absent).
try:
    from app.core.mt5_service import MT5Service  # type: ignore
    setattr(MT5Service, "copy_rates_range_best", _copy_rates_range_best)
    setattr(MT5Service, "copy_rates_from_pos_best", _copy_rates_from_pos_best)
    setattr(MT5Service, "copy_ticks_range_best", _copy_ticks_range_best)
except Exception:
    pass
