#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ MT5AccountEx — Adapter with Tiny TTL Cache for Account Summary            ║
# ║---------------------------------------------------------------------------║
# ║ Purpose:                                                                  ║
# ║   - Provide a thin, safe adapter over your SDK's MT5Account.              ║
# ║   - Add a tiny TTL cache for account_summary to prevent 5–7 RPC bursts.   ║
# ║   - Auto-invalidate the cache after state-changing trading calls.         ║
# ║   - Keep a drop-in feel by delegating unknown attributes to the inner     ║
# ║     MT5Account via __getattr__.                                           ║
# ║                                                                           ║
# ║ What you get:                                                             ║
# ║   - Cached convenience getters: balance/equity/leverage/currency/…        ║
# ║   - Graceful async close & context manager support.                       ║
# ║   - Helpers: delete_order(ticket), close_all_positions(...).              ║
# ║                                                                           ║
# ║ Safety:                                                                   ║
# ║   - We never modify the SDK package.                                      ║
# ║   - Dangerous ops are regular SDK calls; cache is invalidated after them. ║
# ║                                                                           ║
# ║ Usage (example):                                                          ║
# ║   inner = MT5Account(user=..., password=..., grpc_server=..., ...)        ║
# ║   await inner.connect()   # if your SDK requires it                       ║
# ║   acc = MT5AccountEx(inner, summary_ttl_sec=0.5)                          ║
# ║   balance = await acc.account_balance()  # uses cached account_summary    ║
# ║   async with acc:                                                         ║
# ║       ...                                                                 ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

from __future__ import annotations
import inspect
from typing import Any
import asyncio
import inspect
import time
from typing import Any, Iterable, Optional

try:
    # Import the SDK class WITHOUT modifying the package. Adjust path if needed.
    from MetaRpcMT5.mt5_account import MT5Account  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "Cannot import MT5Account from your MT5 package. "
        "Check the import path (MetaRpcMT5.mt5_account)."
    ) from e


class MT5AccountEx:
    """
    MT5AccountEx(inner: MT5Account, summary_ttl_sec: float = 0.5)

    A minimal adapter that adds:
      • Tiny TTL cache for `account_summary` to prevent multi-RPC bursts.
      • Automatic cache invalidation after state-changing calls.
      • Convenience getters derived from the cached summary.
      • Graceful shutdown & async context manager support.
      • Small helpers for common tasks (e.g., delete pending order, close all positions).

    Design goals:
      1) Zero modifications to the SDK package.
      2) Drop-in feel: any unknown attribute is delegated to the inner MT5Account.
      3) Keep things explicit and readable.
    """

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ State-changing method names                                           ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    # If your SDK uses different names, extend this set.
    _STATE_CHANGERS: set[str] = {
        # trading (orders)
        "order_send", "order_modify", "order_close", "order_delete",
        "pending_modify", "pending_replace_stop_limit",
        "place_buy_limit", "place_sell_limit", "place_buy_stop", "place_sell_stop",
        "place_stop_limit",
        # positions
        "position_close", "position_modify", "close_all_positions",
        # low-level hooks (if your SDK exposes them)
        "trade_transaction", "raw_order_send",
    }

    def __init__(self, inner: MT5Account, summary_ttl_sec: float = 0.5) -> None:
        # Keep a reference to the original SDK account
        self._inner: MT5Account = inner

        # Tiny TTL cache for account_summary
        self._summary_cache: Optional[Any] = None
        self._summary_cache_ts: float = 0.0
        self._summary_ttl: float = float(summary_ttl_sec)
        self._summary_lock = asyncio.Lock()  # prevent duplicate concurrent fetches

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ Delegation & state-change awareness                                   ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the inner MT5Account.
        For known state-changers, invalidate summary cache AFTER success.
        """
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)

        inner = object.__getattribute__(self, "_inner")
        if inner is None:
            raise RuntimeError("Not connected")

        try:
            attr = getattr(inner, name)
        except AttributeError:
            cls = type(self).__name__
            icls = type(inner).__name__
            raise AttributeError(f"{cls} has no attribute {name!r} and inner {icls} has no {name!r}")

        try:
            state_changers = object.__getattribute__(self, "_STATE_CHANGERS")
        except Exception:
            state_changers = set()
        try:
            invalidate = object.__getattribute__(self, "_invalidate_summary_cache")
        except Exception:
            invalidate = None

        if name in state_changers and callable(attr) and invalidate:
            if inspect.iscoroutinefunction(attr):
                async def _wrapped(*args, **kwargs):
                    res = await attr(*args, **kwargs)
                    try:
                        invalidate()
                    except Exception:
                        pass
                    return res
                return _wrapped
            else:
                def _wrapped(*args, **kwargs):
                    res = attr(*args, **kwargs)
                    try:
                        invalidate()
                    except Exception:
                        pass
                    return res
                return _wrapped

        return attr

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ Summary cache (account_summary)                                        ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    def _invalidate_summary_cache(self) -> None:
        """Drop the cached summary (called after state changes)."""
        self._summary_cache = None
        self._summary_cache_ts = 0.0

    async def _get_summary_cached(
        self,
        *,
        deadline=None,
        cancellation_event=None,
        use_cache: bool = True
    ) -> Any:
        """
        Return account_summary with a tiny TTL.
        Concurrency-safe: first caller fetches; others await the same lock.
        """
        # Fast path: valid cache
        if use_cache and self._summary_cache is not None:
            if (time.time() - self._summary_cache_ts) < self._summary_ttl:
                return self._summary_cache

        async with self._summary_lock:
            # Double-check inside the lock
            if use_cache and self._summary_cache is not None:
                if (time.time() - self._summary_cache_ts) < self._summary_ttl:
                    return self._summary_cache

            if not hasattr(self._inner, "account_summary"):
                raise AttributeError("Inner MT5Account has no 'account_summary' method.")

            summary = await self._inner.account_summary(
                deadline=deadline, cancellation_event=cancellation_event
            )
            self._summary_cache = summary
            self._summary_cache_ts = time.time()
            return summary

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ Convenience getters derived from summary                               ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    async def account_balance(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> float:
        """Return balance (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return float(getattr(s, "balance", 0.0))

    async def account_credit(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> float:
        """Return credit (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return float(getattr(s, "credit", 0.0))

    async def account_equity(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> float:
        """Return equity (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return float(getattr(s, "equity", 0.0))

    async def account_leverage(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> int:
        """Return leverage (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return int(getattr(s, "leverage", 0))

    async def account_login(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> int:
        """Return login/account_login (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return int(getattr(s, "account_login", getattr(s, "login", 0)))

    async def account_name(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> str:
        """Return account holder name (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return str(getattr(s, "name", ""))

    async def account_company(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> str:
        """Return company/broker name (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return str(getattr(s, "company", ""))

    async def account_currency(self, *, use_cache: bool = True, deadline=None, cancellation_event=None) -> str:
        """Return account currency (from cached account_summary)."""
        s = await self._get_summary_cached(use_cache=use_cache, deadline=deadline, cancellation_event=cancellation_event)
        return str(getattr(s, "currency", ""))

    def invalidate(self) -> None:
        """Manual cache invalidation (use if you call inner state-changers directly)."""
        self._invalidate_summary_cache()

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ Context manager & graceful shutdown                                    ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    async def close(self) -> None:
        """
        Best-effort graceful shutdown.
        - Try to stop listeners if present.
        - Try to disconnect/close the inner account.
        - As a last resort, close the underlying channel if accessible.
        - Always invalidate local caches.
        """
        # 1) Stop listeners if the inner exposes them
        for stop_name in ("stop_listeners", "stop", "shutdown"):
            fn = getattr(self._inner, stop_name, None)
            if callable(fn):
                try:
                    res = fn()
                    if inspect.iscoroutine(res):
                        await res
                except Exception:
                    pass  # best-effort

        # 2) Try account-level disconnect/close
        for fn_name in ("disconnect", "close"):
            fn = getattr(self._inner, fn_name, None)
            if callable(fn):
                try:
                    res = fn()
                    if inspect.iscoroutine(res):
                        await res
                    self._invalidate_summary_cache()
                    return
                except Exception:
                    pass

        # 3) Fallback: close underlying gRPC channel if reachable
        chan = getattr(self._inner, "_channel", None) or getattr(self._inner, "channel", None)
        if chan is not None and hasattr(chan, "close"):
            try:
                res = chan.close()
                if inspect.iscoroutine(res):
                    await res
            except Exception:
                pass

        # 4) Invalidate local cache
        self._invalidate_summary_cache()

    async def __aenter__(self) -> "MT5AccountEx":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ Helpers — bulk close & pending delete                                  ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    async def close_all_positions(
        self,
        *,
        symbol: Optional[str] = None,
        magic: Optional[int] = None,
        concurrent: bool = True,
    ) -> dict:
        """
        Close all open positions.
        Filters:
          - symbol: close only positions for this symbol.
          - magic:  close only positions with this magic number (if present).
        If 'concurrent' is True, closes in parallel.
        Returns: {"attempted": N, "closed": K, "errors": [..]}
        """
        positions = await self._list_open_positions()

        # Apply filters
        filtered: list = []
        for p in positions:
            if symbol is not None:
                sym = getattr(p, "symbol", None)
                if (sym or "").upper() != symbol.upper():
                    continue
            if magic is not None:
                mg = getattr(p, "magic", getattr(p, "magic_number", None))
                if mg is None or int(mg) != int(magic):
                    continue
            filtered.append(p)

        errors: list[str] = []
        if concurrent:
            tasks = [asyncio.create_task(self._close_one_position(p)) for p in filtered]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    errors.append(str(r))
        else:
            for p in filtered:
                try:
                    await self._close_one_position(p)
                except Exception as e:
                    errors.append(str(e))

        # Summary cache likely stale after bulk op
        self._invalidate_summary_cache()
        return {"attempted": len(filtered), "closed": len(filtered) - len(errors), "errors": errors}

    async def delete_order(self, ticket: int, *, deadline=None, cancellation_event=None):
        """
        Cancel a pending order by ticket via TradingHelper.OrderClose.
        Returns the full response object from the inner call.

        Notes:
          - We import the protobuf stub at call time to avoid hard dependency
            if your environment defers codegen/imports.
        """
        if ticket is None:
            raise ValueError("ticket is required")

        # Import here to avoid module import-time failures.
        from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2  # type: ignore

        req = th_pb2.OrderCloseRequest(ticket=ticket)

        # Delegate to the inner high-level wrapper (preserves headers/reconnects).
        reply = await self._inner.order_close(
            request=req, deadline=deadline, cancellation_event=cancellation_event
        )

        # Account state may change after cancel → drop cache.
        self._invalidate_summary_cache()
        return reply

    # ╔═══════════════════════════════════════════════════════════════════════╗
    # ║ Internals for helpers                                                  ║
    # ╚═══════════════════════════════════════════════════════════════════════╝
    async def _list_open_positions(self) -> list:
        """
        Enumerate open positions using the best available method from the SDK.
        We probe common method names to stay resilient to SDK differences.
        """
        # 1) Direct "get positions" style
        for name in ("positions_get", "positions", "opened_positions", "positions_open"):
            fn = getattr(self._inner, name, None)
            if callable(fn):
                res = fn()
                return await res if inspect.iscoroutine(res) else res

        # 2) Fallback: total + get-by-index
        total_fn = getattr(self._inner, "positions_total", None)
        if callable(total_fn):
            total_res = total_fn()
            total = await total_res if inspect.iscoroutine(total_res) else total_res
            getter = None
            for gname in ("position_get_by_index", "position_get_index", "position_get"):
                fn = getattr(self._inner, gname, None)
                if callable(fn):
                    getter = fn
                    break
            if getter is not None and isinstance(total, int) and total >= 0:
                out = []
                for i in range(total):
                    item = getter(i)
                    item = await item if inspect.iscoroutine(item) else item
                    if item is not None:
                        out.append(item)
                return out

        raise NotImplementedError(
            "Cannot enumerate open positions: no suitable method found on inner MT5Account."
        )

    async def _close_one_position(self, pos: object) -> None:
        """
        Close a single position using the most appropriate inner method.

        Preference order:
          1) position_close(ticket=? or position=? or object)
          2) order_close(ticket=?), if the backend accepts it for positions
        """
        ticket = self._get_attr_any(pos, ("ticket", "id", "position", "position_id"))
        symbol = self._get_attr_any(pos, ("symbol",))
        volume = self._get_attr_any(pos, ("volume", "lots", "volume_current"))

        # 1) Try position_close first
        fn = getattr(self._inner, "position_close", None)
        if callable(fn):
            sig = inspect.signature(fn)
            kwargs = {}
            if "ticket" in sig.parameters and ticket is not None:
                kwargs["ticket"] = ticket
            elif "position" in sig.parameters and ticket is not None:
                kwargs["position"] = ticket
            elif len(sig.parameters) == 1:
                res = fn(pos)
                await res if inspect.iscoroutine(res) else None
                return
            res = fn(**kwargs) if kwargs else fn()
            res = await res if inspect.iscoroutine(res) else res
            return

        # 2) Fallback: order_close for positions (some backends behave like that)
        fn = getattr(self._inner, "order_close", None)
        if callable(fn) and ticket is not None:
            sig = inspect.signature(fn)
            kwargs = {}
            if "ticket" in sig.parameters:
                kwargs["ticket"] = ticket
            if "symbol" in sig.parameters and symbol is not None:
                kwargs["symbol"] = symbol
            if "volume" in sig.parameters and volume is not None:
                kwargs["volume"] = volume
            res = fn(**kwargs) if kwargs else fn(ticket)
            res = await res if inspect.iscoroutine(res) else res
            return

        raise RuntimeError("No suitable close method (position_close/order_close) found on inner MT5Account.")

    # Small attribute getter used by helpers
    @staticmethod
    def _get_attr_any(obj: object, names: Iterable[str]):
        for n in names:
            if hasattr(obj, n):
                return getattr(obj, n)
        return None
