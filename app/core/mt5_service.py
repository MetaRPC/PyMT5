from __future__ import annotations

# ── Stdlib ───────────────────────────────────────────────────────────────────
import asyncio
import inspect
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Dict, Iterable, List, Optional, TYPE_CHECKING

# ── 3rd-party ────────────────────────────────────────────────────────────────
from google.protobuf.timestamp_pb2 import Timestamp

# ── MT5 / Protobuf API ───────────────────────────────────────────────────────
from MetaRpcMT5 import ApiExceptionMT5, ConnectExceptionMT5
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as ah_pb2  

# ── Local app ────────────────────────────────────────────────────────────────
from .config import MT5Config


# ── Account class  ──────────────────────────────────
try:
    from MetaRpcMT5Ex import MT5AccountEx as MT5Account
except ImportError:
    try:
        from examples.mt5_account_ex import MT5AccountEx as MT5Account
    except ImportError:
        from MetaRpcMT5 import MT5Account  # type: ignore

if TYPE_CHECKING:
    from MetaRpcMT5.mt5_account import MT5Account as MT5Account 

# ── helpers ──────────────────────────────────────────────────────────────────

class MT5Service:

    # ╔════════════════════════════════════════╗
    # ║ Class-level attributes / inner members ║
    # ╚════════════════════════════════════════╝
    acc: Optional["MT5Account"]

    # ╔═══════════════════════════╗
    # ║ 0) Connectivity & Account ║
    # ╚═══════════════════════════╝
    async def connect(self) -> bool:
        from app.core.mt5_connect_helper import connect_via_helper
        return await connect_via_helper(self)

    async def disconnect(self) -> bool:
        from app.core.mt5_connect_helper import disconnect_via_helper
        return await disconnect_via_helper(self)

    async def ensure_connected(self) -> bool:
        from app.core.mt5_connect_helper import ensure_connected
        return await ensure_connected(self)

    # ╔═════════════════════╗
    # ║ 7) Internal Helpers ║
    # ╚═════════════════════╝
    def __init__(self, cfg: "MT5Config"):
        self.cfg = cfg
        self.acc = None
        self.logger = None
        self._timeout = int(getattr(cfg, "timeout_seconds", 90))
        self._base_chart_symbol = getattr(cfg, "base_chart_symbol", "EURUSD")

    def __getattr__(self, name: str):
        """
Delegating unknown attributes/methods to self.acc.
        Asynchronous — we wrap them to call them directly.
        """
        acc = object.__getattribute__(self, "acc")
        if acc is None:
            raise RuntimeError("Not connected")
        target = getattr(acc, name, None)
        if target is None:
            raise AttributeError(f"'MT5Service' has no attribute '{name}' and MT5Account has no '{name}'")
        import inspect
        if inspect.iscoroutinefunction(target):
            async def _wrapped(*args, **kwargs):
                if self.acc is None:
                    raise RuntimeError("Not connected")
                return await target(*args, **kwargs)
            return _wrapped
        return target

    async def ensure_symbol_visible(self, symbol: str, *, wait_for_tick: bool = True,
                                    timeout_ms: int = 1500, poll_ms: int = 100) -> bool:
        
        
        import time as _time
        if not self.acc:
            raise RuntimeError("Not connected")
        try:
            sel = getattr(self, "symbol_select", None)
            if callable(sel):
                try:
                    await sel(symbol, True)
                except TypeError:
                    await sel(symbol, enable=True)
        except Exception:
            pass

        if not wait_for_tick:
            return True

        deadline = _time.monotonic() + timeout_ms / 1000.0
        while _time.monotonic() < deadline:
            try:
                
                for nm in ("symbol_exist", "symbol_visible", "is_symbol_visible"):
                    fn = getattr(self, nm, None)
                    if callable(fn):
                        res = await fn(symbol)
                        ok = bool(getattr(res, "exists", getattr(res, "visible", res)))
                        if ok:
                            break
                
                tick = await self.acc.symbol_info_tick(symbol=symbol)
                if tick is not None:
                    return True
            except Exception:
                pass
            await asyncio.sleep(poll_ms / 1000.0)
        return False

    # ╔══════════╗
    # ║ 8) Other ║
    # ╚══════════╝
    async def opened_snapshot(self) -> dict:
       
        from google.protobuf.json_format import MessageToDict
        opened_msg = await self.opened_orders()
        d = MessageToDict(opened_msg, preserving_proto_field_name=True)

        raw_positions = d.get("position_infos") or d.get("positions") or []
        raw_pending   = d.get("pending_orders") or d.get("orders") or []

        keys = ("ticket", "symbol", "volume", "price_open", "price_current", "sl", "tp", "profit")
        def to_summary(item: dict) -> dict:
            return {k: item.get(k) for k in keys}

        return {
            "positions": [to_summary(it) for it in raw_positions],
            "pending":   [to_summary(it) for it in raw_pending],
        }

# ╔══════════════════════════════════════╗
# ║ MODULE HELPERS (Top-level functions) ║
# ╚══════════════════════════════════════╝
# --- 0) Connectivity & Account ---
async def disconnect(self) -> None:
        """
        Best‑effort graceful shutdown
        ┌───────────────┬───────────────────────────────────────────────────┐
        │ Step          │ What happens                                      │
        ├───────────────┼───────────────────────────────────────────────────┤
        │ stop_*        │ acc.stop_listeners/stop/shutdown if present       │
        │ disconnect    │ acc.disconnect() if present                       │
        │ channel.close │ close gRPC channel if exposed                     │
        └───────────────┴───────────────────────────────────────────────────┘
        """
        acc = self.acc
        self.acc = None
        if not acc:
            return
        for stop_name in ('stop_listeners', 'stop', 'shutdown'):
            fn = getattr(acc, stop_name, None)
            if callable(fn):
                try:
                    res = fn()
                    if inspect.isawaitable(res):
                        await res
                except Exception:
                    pass
        maybe_disc = getattr(acc, 'disconnect', None)
        if callable(maybe_disc):
            try:
                res = maybe_disc()
                if inspect.isawaitable(res):
                    await res
            except Exception:
                pass
        ch = getattr(acc, 'channel', None)
        if ch and hasattr(ch, 'close'):
            try:
                res = ch.close()
                if inspect.isawaitable(res):
                    await res
            except Exception:
                pass

def is_connected(self) -> bool:
        """Lightweight check that the account object exists (and channel if exposed)."""
        if self.acc is None:
            return False
        ch = getattr(self.acc, 'channel', None)
        if ch is None:
            return True
        return True

async def server_time(self):
    if not self.acc:
        raise RuntimeError('Not connected')
    summ = await self.acc.account_summary()
    return getattr(summ, 'server_time', None)

async def account_summary(self) -> Any:
        """Return account summary from backend (adapter may cache this internally)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.account_summary()

async def account_info_double(self, prop: int) -> Any:
        """Get account double property by id."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.account_info_double(prop=prop)

async def account_info_integer(self, prop: int) -> Any:
        """Get account integer property by id."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.account_info_integer(prop=prop)

async def account_info_string(self, prop: int) -> Any:
        """Get account string property by id."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.account_info_string(prop=prop)

# --- 1) Symbols & Market Info ---
async def quote(self, symbol: str) -> Any:
        """Return last tick/quote for symbol (wrapper over symbol_info_tick)."""
        return await self.symbol_info_tick(symbol)

async def symbol_info_tick(self, symbol: str) -> Any:
        if not self.acc:
            raise RuntimeError('Not connected')
        try:
            return await self.acc.symbol_info_tick(symbol=symbol)
        except (AttributeError, TypeError):
            pass
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
        from MetaRpcMT5 import mt5_term_api_market_info_pb2_grpc as _
        client = getattr(self.acc, 'market_info_client', None)
        if client is None:
            raise NotImplementedError('market_info_client not available in this package')
        req = mi_pb2.SymbolInfoTickRequest(symbol=symbol)
        exec_fn = getattr(self.acc, 'execute_with_reconnect', None)
        if callable(exec_fn):

            async def grpc_call(headers):
                return await client.SymbolInfoTick(req, metadata=headers, timeout=None)
            res = await exec_fn(grpc_call, lambda r: getattr(r, 'error', None))
        else:
            headers = self.acc.get_headers() if hasattr(self.acc, 'get_headers') else []
            res = await client.SymbolInfoTick(req, metadata=headers, timeout=None)
        return getattr(res, 'data', res)

async def symbol_params(self, symbol: str) -> Optional[Any]:
        """
        Return parameters for a single symbol. Internally calls symbol_params_many()
        and selects the matching symbol (case-insensitive) or the first item.
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        arr = await self.symbol_params_many([symbol])
        sym_u = symbol.upper()
        if isinstance(arr, (list, tuple)):
            for it in arr:
                s = (getattr(it, 'symbol', '') or getattr(it, 'symbol_name', '')).upper()
                if s == sym_u:
                    return it
            return arr[0] if arr else None
        for name in ('items', 'params', 'symbols', 'list', 'data'):
            bag = getattr(arr, name, None)
            if isinstance(bag, (list, tuple)):
                for it in bag:
                    s = (getattr(it, 'symbol', '') or getattr(it, 'symbol_name', '')).upper()
                    if s == sym_u:
                        return it
                return bag[0] if bag else None
        return None

async def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        """Ensure symbol is (de)selected in Market Watch. Try gRPC first, fallback to SDK."""
        acc = getattr(self, 'acc', None)
        if acc is None:
            raise RuntimeError('Not connected')

        client = getattr(acc, 'market_info_client', None)
        if client is not None:
            try:
                from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2  # type: ignore
                headers = acc.get_headers() if hasattr(acc, 'get_headers') else []
                try:
                    req = mi_pb2.SymbolSelectRequest(symbol=symbol, enable=bool(enable))
                except Exception:
                    req = mi_pb2.SymbolSelectRequest(symbol=symbol, select=bool(enable))
                await client.SymbolSelect(req, metadata=headers, timeout=2.0)
                return True
            except Exception:
                pass

        import inspect as _inspect
        fn = getattr(acc, 'symbol_select', None)
        if callable(fn):
            res = fn(symbol, bool(enable))
            res = (await res) if _inspect.iscoroutine(res) else res
            return bool(res if isinstance(res, bool) else getattr(res, 'ok', True))

        return False

async def symbols_visible(self) -> List[str]:
        """List of visible symbols (best-effort)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        for name in ('symbols_visible', 'symbols_visible_names'):
            fn = getattr(self.acc, name, None)
            if callable(fn):
                res = await fn()
                if isinstance(res, (list, tuple)):
                    return [str(x) for x in res]
                for fld in ('items', 'names', 'symbols'):
                    v = getattr(res, fld, None)
                    if isinstance(v, (list, tuple)):
                        return [str(x) for x in v]
        return []

async def symbols_search(self, pattern: str) -> List[str]:
        """Search symbols by substring/pattern if backend supports it; otherwise filter all_symbols()."""
        if not self.acc:
            raise RuntimeError('Not connected')
        fn = getattr(self.acc, 'symbols_search', None)
        if callable(fn):
            res = await fn(pattern)
            if isinstance(res, (list, tuple)):
                return [str(x) for x in res]
        names = await self.all_symbols()
        p = (pattern or '').upper()
        return [n for n in names if p in n.upper()]

async def symbol_info_session_trade(self, symbol: str, day_of_week: int=0, session_index: int=0):
    if not self.acc:
        raise RuntimeError('Not connected')
    return await self.acc.symbol_info_session_trade(symbol, day_of_week, session_index)

async def symbol_info_session_quote(self, symbol: str, day_of_week: int=0, session_index: int=0):
    if not self.acc:
        raise RuntimeError('Not connected')
    return await self.acc.symbol_info_session_quote(symbol, day_of_week, session_index)

async def quotes_many(self, symbols: Iterable[str]) -> Dict[str, Any]:
        """
        Fetch last quotes for many symbols concurrently.
        Returns dict {symbol -> tick|None}.
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        syms = [str(s) for s in symbols]

        async def _one(s: str):
            try:
                return await self.symbol_info_tick(symbol=s)
            except Exception:
                return None
        results = await asyncio.gather(*[_one(s) for s in syms])
        return {s: r for s, r in zip(syms, results)}

async def symbol_info_double(self, symbol: str, prop: int) -> Any:
        """Get symbol double property by id."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.symbol_info_double(symbol=symbol, prop=prop)

async def symbol_info_integer(self, symbol: str, prop: int) -> Any:
        """Get symbol integer property by id."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.symbol_info_integer(symbol=symbol, prop=prop)

async def symbol_info_string(self, symbol: str, prop: int) -> Any:
        """Get symbol string property by id."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.symbol_info_string(symbol=symbol, prop=prop)

async def symbol_info_margin_rate(self, symbol: str, order_type: Optional[int]=None) -> Any:
        """
        Correct implementation: call MarketInfo.SymbolInfoMarginRate (NOT account_helper).
        If order_type is None, default to BUY.
        """
        if not getattr(self, 'acc', None):
            raise RuntimeError('Not connected')
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
        from MetaRpcMT5 import mt5_term_api_market_info_pb2_grpc as _
        client = getattr(self.acc, 'market_info_client', None)
        if client is None:
            raise NotImplementedError('market_info_client not available in this package')
        if order_type is None:
            order_type = getattr(mi_pb2, 'ORDER_TYPE_BUY', 0)
        req = mi_pb2.SymbolInfoMarginRateRequest(symbol=symbol, order_type=order_type)
        exec_fn = getattr(self.acc, 'execute_with_reconnect', None)
        if callable(exec_fn):

            async def grpc_call(headers):
                return await client.SymbolInfoMarginRate(req, metadata=headers, timeout=None)
            res = await exec_fn(grpc_call, lambda r: getattr(r, 'error', None))
        else:
            headers = self.acc.get_headers() if hasattr(self.acc, 'get_headers') else []
            res = await client.SymbolInfoMarginRate(req, metadata=headers, timeout=None)
        return getattr(res, 'data', res)

async def symbol_info_session_quote(self, symbol: str, day_of_week: Optional[int]=None, session_index: Optional[int]=None) -> Any:
    
    if not self.acc:
        raise RuntimeError('Not connected')
    from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
    from MetaRpcMT5 import mt5_term_api_market_info_pb2_grpc as _
    if day_of_week is None:
        wd = datetime.now(timezone.utc).weekday()
        map_py_to_mi = {0: mi_pb2.DayOfWeek.MONDAY, 1: mi_pb2.DayOfWeek.TUESDAY, 2: mi_pb2.DayOfWeek.WEDNESDAY, 3: mi_pb2.DayOfWeek.THURSDAY, 4: mi_pb2.DayOfWeek.FRIDAY, 5: mi_pb2.DayOfWeek.SATURDAY, 6: mi_pb2.DayOfWeek.SUNDAY}
        day_of_week = map_py_to_mi.get(wd, mi_pb2.DayOfWeek.MONDAY)
    if session_index is None:
        session_index = 0
    req = mi_pb2.SymbolInfoSessionQuoteRequest(symbol=symbol, day_of_week=day_of_week, session_index=session_index)
    client = getattr(self.acc, 'market_info_client', None)
    if client is None:
        raise NotImplementedError('market_info_client not available in this package')
    exec_fn = getattr(self.acc, 'execute_with_reconnect', None)
    if callable(exec_fn):

        async def grpc_call(headers):
            return await client.SymbolInfoSessionQuote(req, metadata=headers, timeout=None)
        res = await exec_fn(grpc_call, lambda r: getattr(r, 'error', None))
    else:
        headers = self.acc.get_headers() if hasattr(self.acc, 'get_headers') else []
        res = await client.SymbolInfoSessionQuote(req, metadata=headers, timeout=None)
    return getattr(res, 'data', res)

async def symbol_info_session_trade(self, symbol: str) -> Any:
        """Get session trade info for symbol."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.symbol_info_session_trade(symbol=symbol)

async def symbol_name(self, pos: int) -> Any:
        """Get symbol name by index (in Market Watch)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.symbol_name(pos=pos)

async def symbol_is_synchronized(self, symbol: str) -> Any:
        """Check if symbol is synchronized in terminal."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.symbol_is_synchronized(symbol=symbol)

async def market_book_add(self, symbol: str) -> Any:
    if not self.acc:
        raise RuntimeError('Not connected')
    from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
    from MetaRpcMT5 import mt5_term_api_market_info_pb2_grpc as _
    client = getattr(self.acc, 'market_info_client', None)
    if client is None:
        raise NotImplementedError('market_info_client not available in this package')
    req = mi_pb2.MarketBookAddRequest(symbol=symbol)
    exec_fn = getattr(self.acc, 'execute_with_reconnect', None)
    if callable(exec_fn):

        async def grpc_call(headers):
            return await client.MarketBookAdd(req, metadata=headers, timeout=None)
        res = await exec_fn(grpc_call, lambda r: getattr(r, 'error', None))
    else:
        headers = self.acc.get_headers() if hasattr(self.acc, 'get_headers') else []
        res = await client.MarketBookAdd(req, metadata=headers, timeout=None)
    return getattr(res, 'data', res)

async def market_book_release(self, symbol: str) -> Any:
    if not self.acc:
        raise RuntimeError('Not connected')
    from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
    from MetaRpcMT5 import mt5_term_api_market_info_pb2_grpc as _
    client = getattr(self.acc, 'market_info_client', None)
    if client is None:
        raise NotImplementedError('market_info_client not available in this package')
    req = mi_pb2.MarketBookReleaseRequest(symbol=symbol)
    exec_fn = getattr(self.acc, 'execute_with_reconnect', None)
    if callable(exec_fn):

        async def grpc_call(headers):
            return await client.MarketBookRelease(req, metadata=headers, timeout=None)
        res = await exec_fn(grpc_call, lambda r: getattr(r, 'error', None))
    else:
        headers = self.acc.get_headers() if hasattr(self.acc, 'get_headers') else []
        res = await client.MarketBookRelease(req, metadata=headers, timeout=None)
    return getattr(res, 'data', res)

async def symbol_info_session_trade(self, symbol: str, day_of_week: int=0, session_index: int=0):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    try:
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as _mi
        req = _mi.SymbolInfoSessionTradeRequest(symbol=symbol, day_of_week=day_of_week, session_index=session_index)
        headers = acc.get_headers()
        return await acc.market_info_client.SymbolInfoSessionTrade(req, metadata=headers, timeout=None)
    except Exception:
        return await acc.symbol_info_session_trade(symbol, day_of_week, session_index)

async def symbol_info_session_quote(self, symbol: str, day_of_week: int=0, session_index: int=0):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    try:
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as _mi
        req = _mi.SymbolInfoSessionQuoteRequest(symbol=symbol, day_of_week=day_of_week, session_index=session_index)
        headers = acc.get_headers()
        return await acc.market_info_client.SymbolInfoSessionQuote(req, metadata=headers, timeout=None)
    except Exception:
        return await acc.symbol_info_session_quote(symbol, day_of_week, session_index)

async def market_book_get(self, symbol: str, tries: int = 6, delay: float = 0.25, timeout: float = 1.5):
    acc = getattr(self, "acc", None)
    if acc is None:
        raise RuntimeError("Not connected")

    # ensure symbol visible
    for nm in ("ensure_symbol_visible", "symbol_select"):
        f = getattr(self, nm, None)
        if callable(f):
            try:
                r = f(symbol) if nm == "symbol_select" else f(symbol, True)
                if hasattr(r, "__await__"):
                    await r
            except Exception:
                pass

    # choose client/protos
    mic = getattr(acc, "market_info_client", None)
    mbc = getattr(acc, "market_book_client", None) or getattr(acc, "depth_client", None)
    headers = acc.get_headers() if hasattr(acc, "get_headers") else []

    try:
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2  # type: ignore
    except Exception:
        mi_pb2 = None
    try:
        from MetaRpcMT5 import mt5_term_api_market_book_pb2 as mb_pb2  # type: ignore
    except Exception:
        mb_pb2 = None

    def _extract_ba(res):
        data = getattr(res, "data", res)
        bids = getattr(data, "bids", None) or getattr(data, "Bids", None) or []
        asks = getattr(data, "asks", None) or getattr(data, "Asks", None) or []
        return list(bids), list(asks)

    # helper to call Get with retries on a given client/api
    async def _get_via_market_info() -> dict | None:
        if not mic or not mi_pb2:
            return None
        added = False
        try:
            # Add
            try:
                req_add = mi_pb2.MarketBookAddRequest(symbol=symbol)
                await mic.MarketBookAdd(req_add, metadata=headers, timeout=timeout)
                added = True
            except Exception:
                pass

            last = {"bids": [], "asks": []}
            for _ in range(tries):
                try:
                    req_get = mi_pb2.MarketBookGetRequest(symbol=symbol)
                    res = await mic.MarketBookGet(req_get, metadata=headers, timeout=timeout)
                    bids, asks = _extract_ba(res)
                    if bids or asks:
                        return {"bids": bids, "asks": asks}
                    last = {"bids": bids, "asks": asks}
                except Exception:
                    
                    pass
                await asyncio.sleep(delay)
            return last
        finally:
            if added:
                try:
                    req_rel = mi_pb2.MarketBookReleaseRequest(symbol=symbol)
                    res = mic.MarketBookRelease(req_rel, metadata=headers, timeout=timeout)
                    if hasattr(res, "__await__"):
                        await res
                except Exception:
                    pass

    async def _get_via_market_book() -> dict | None:
        if not mbc or not mb_pb2:
            return None
       
        last = {"bids": [], "asks": []}
        for _ in range(tries):
            try:
                req = mb_pb2.MarketBookGetRequest()
                if hasattr(req, "symbol"):
                    req.symbol = symbol
                elif hasattr(req, "Symbol"):
                    req.Symbol = symbol
                res = await mbc.Get(req, metadata=headers, timeout=timeout)
                bids, asks = _extract_ba(res)
                if bids or asks:
                    return {"bids": bids, "asks": asks}
                last = {"bids": bids, "asks": asks}
            except Exception:
                pass
            await asyncio.sleep(delay)
        return last

    # try MarketInfo API first, then fallback to MarketBook API
    data = await _get_via_market_info()
    if data is None or (not data["bids"] and not data["asks"]):
        fb = await _get_via_market_book()
        if fb is not None:
            data = fb

    return data or {"bids": [], "asks": []}

async def symbol_info_margin_rate(self, symbol: str, order_type: int=0):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    return await acc.symbol_info_margin_rate(symbol, order_type)

async def symbol_info_margin_rate(self, symbol: str, order_type: int=0):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    try:
        from MetaRpcMT5 import mt5_term_api_market_info_pb2 as _mi
        req = _mi.SymbolInfoMarginRateRequest(symbol=symbol, order_type=order_type)
        headers = acc.get_headers()
        return await acc.market_info_client.SymbolInfoMarginRate(req, metadata=headers, timeout=None)
    except Exception:
        return await acc.symbol_info_margin_rate(symbol, order_type)

# --- 2) Copy & Charts ---
async def copy_rates_from_pos(self, symbol: str, timeframe: str = 'H1',
                                  start_pos: int = 0, count: int = 1000) -> list[dict]:
        acc = getattr(self, 'acc', None)
        if acc is None:
            raise RuntimeError('Not connected')
        # gRPC
        try:
            from MetaRpcMT5 import mt5_term_api_charts_pb2 as ch  # type: ignore
            minutes = _tf_minutes(timeframe)
            headers = acc.get_headers() if hasattr(acc, 'get_headers') else []
            try:
                req = ch.CopyRatesFromPosRequest(symbol=symbol, timeframe_minutes=minutes,
                                                 start_pos=start_pos, count=count)
            except Exception:
                req = ch.CopyRatesFromPosRequest(symbol=symbol, timeframe=minutes,
                                                 startPos=start_pos, count=count)
            res = await acc.charts_client.CopyRatesFromPos(req, metadata=headers, timeout=2.5)
            rows = getattr(res, 'rates', None) or getattr(res, 'items', None) or []
            return [_ohlc_row(c) for c in rows]
        except Exception:
            pass
        # SDK
        try:
            data = await acc.copy_rates_from_pos(symbol, timeframe, start_pos, count)  # type: ignore
            rows = data if isinstance(data, (list, tuple)) else getattr(data, 'items', None) or []
            return [_ohlc_row(c) for c in rows]
        except Exception:
            return []

async def copy_rates_range(self, symbol: str, timeframe: str = 'H1',
                               ts_from: int | None = None, ts_to: int | None = None,
                               count_max: int = 3000) -> list[dict]:
        acc = getattr(self, 'acc', None)
        if acc is None:
            raise RuntimeError('Not connected')
        # gRPC
        try:
            from MetaRpcMT5 import mt5_term_api_charts_pb2 as ch  # type: ignore
            minutes = _tf_minutes(timeframe)
            headers = acc.get_headers() if hasattr(acc, 'get_headers') else []
            try:
                req = ch.CopyRatesRangeRequest(symbol=symbol, timeframe_minutes=minutes,
                                               time_from=_as_int_ts(ts_from), time_to=_as_int_ts(ts_to),
                                               count_max=count_max)
            except Exception:
                req = ch.CopyRatesRangeRequest(symbol=symbol, timeframe=minutes,
                                               timeFrom=_as_int_ts(ts_from), timeTo=_as_int_ts(ts_to),
                                               countMax=count_max)
            res = await acc.charts_client.CopyRatesRange(req, metadata=headers, timeout=2.5)
            rows = getattr(res, 'rates', None) or getattr(res, 'items', None) or []
            return [_ohlc_row(c) for c in rows]
        except Exception:
            pass
        # SDK
        try:
            data = await acc.copy_rates_range(symbol, timeframe, ts_from, ts_to, count_max)  # type: ignore
            rows = data if isinstance(data, (list, tuple)) else getattr(data, 'items', None) or []
            return [_ohlc_row(c) for c in rows]
        except Exception:
            return []

async def copy_ticks_range(self, symbol: str, ts_from: int | None = None, ts_to: int | None = None,
                               flags: int = 0, count_max: int = 5000) -> list[dict]:
        acc = getattr(self, 'acc', None)
        if acc is None:
            raise RuntimeError('Not connected')
        # gRPC
        try:
            from MetaRpcMT5 import mt5_term_api_charts_pb2 as ch  # type: ignore
            headers = acc.get_headers() if hasattr(acc, 'get_headers') else []
            try:
                req = ch.CopyTicksRangeRequest(symbol=symbol, time_from=_as_int_ts(ts_from),
                                               time_to=_as_int_ts(ts_to), flags=flags, count_max=count_max)
            except Exception:
                req = ch.CopyTicksRangeRequest(symbol=symbol, timeFrom=_as_int_ts(ts_from),
                                               timeTo=_as_int_ts(ts_to), flags=flags, countMax=count_max)
            res = await acc.charts_client.CopyTicksRange(req, metadata=headers, timeout=2.5)
            rows = getattr(res, 'ticks', None) or getattr(res, 'items', None) or []
            return [_tick_row(t) for t in rows]
        except Exception:
            pass
        # SDK
        try:
            data = await acc.copy_ticks_range(symbol, ts_from, ts_to, flags, count_max)  # type: ignore
            rows = data if isinstance(data, (list, tuple)) else getattr(data, 'items', None) or []
            return [_tick_row(t) for t in rows]
        except Exception:
            return []

# --- 3) Calculations ---
async def opened_orders_profit(self) -> Dict[str, Any]:
        """
        Return PnL snapshot for all open positions.
        ┌────────────┬───────────────────────────────────────────────────────┐
        │ Strategy   │ 1) try order_calc_profit per position                 │
        │            │ 2) else manual calc via tick_value & point            │
        ├────────────┼───────────────────────────────────────────────────────┤
        │ Output     │ {"total": float, "items":[{ticket,symbol,profit,...}]}│
        └────────────┴───────────────────────────────────────────────────────┘
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        snap = await self.opened_orders(sort_mode=0)
        positions = getattr(snap, 'positions', None) or getattr(snap, 'opened_positions', None) or []
        if not positions:
            return {'total': 0.0, 'items': []}
        symbols = sorted({(getattr(p, 'symbol', '') or getattr(p, 'symbol_name', '')).upper() for p in positions})
        ticks: Dict[str, Any] = {}
        for s in symbols:
            try:
                ticks[s] = await self.symbol_info_tick(symbol=s)
            except Exception:
                ticks[s] = None
        params_map: Dict[str, Any] = {}
        try:
            par = await self.symbol_params_many(symbols)
            for name in dir(par):
                val = getattr(par, name, None)
                if isinstance(val, (list, tuple)):
                    for item in val:
                        sym = (getattr(item, 'symbol', '') or getattr(item, 'symbol_name', '')).upper()
                        if sym:
                            params_map[sym] = item
        except Exception:
            pass

        def _side_from(pos: Any) -> Optional[str]:
            v = getattr(pos, 'type', getattr(pos, 'position_type', None))
            if isinstance(v, int):
                return 'BUY' if v == 0 else 'SELL' if v == 1 else None
            if isinstance(v, str):
                s = v.upper()
                if 'BUY' in s:
                    return 'BUY'
                if 'SELL' in s:
                    return 'SELL'
            return None

        def _point_for(sym: str) -> Optional[float]:
            p = params_map.get(sym)
            if p is not None:
                pt = getattr(p, 'point', None)
                if isinstance(pt, (int, float)) and pt > 0:
                    return float(pt)
                dg = getattr(p, 'digits', None)
                try:
                    if dg is not None:
                        d = int(dg)
                        return 10.0 ** (-d)
                except Exception:
                    pass
            return None
        total = 0.0
        items: List[Dict[str, Any]] = []
        for pos in positions:
            sym = (getattr(pos, 'symbol', '') or getattr(pos, 'symbol_name', '')).upper()
            vol = float(getattr(pos, 'volume', getattr(pos, 'lots', getattr(pos, 'volume_current', 0.0))) or 0.0)
            side = _side_from(pos) or 'BUY'
            open_price = float(getattr(pos, 'price_open', getattr(pos, 'open_price', getattr(pos, 'price', 0.0))) or 0.0)
            tick = ticks.get(sym)
            bid = float(getattr(tick, 'bid', 0.0)) if tick else None
            ask = float(getattr(tick, 'ask', 0.0)) if tick else None
            close_price = (bid if side == 'BUY' else ask) or (ask if side == 'BUY' else bid)
            profit_val: Optional[float] = None
            calc_fn = getattr(self.acc, 'order_calc_profit', None)
            if callable(calc_fn) and close_price:
                try:
                    order_type = 0 if side == 'BUY' else 1
                    res = await calc_fn(sym, order_type, vol, open_price, close_price)
                    for fld in ('calc_profit', 'profit', 'value', 'amount'):
                        v = getattr(res, fld, None)
                        if isinstance(v, (int, float)):
                            profit_val = float(v)
                            break
                    if profit_val is None and isinstance(res, (int, float)):
                        profit_val = float(res)
                except Exception:
                    profit_val = None
            if profit_val is None and close_price and open_price:
                try:
                    tv = await self.tick_value_with_size(sym, vol)
                    tick_value = float(getattr(tv, 'tick_value', tv))
                    point = _point_for(sym)
                    if point and tick_value:
                        delta = close_price - open_price if side == 'BUY' else open_price - close_price
                        points = delta / point
                        profit_val = points * tick_value
                except Exception:
                    profit_val = None
            profit_val = float(profit_val or 0.0)
            total += profit_val
            items.append({'ticket': int(getattr(pos, 'ticket', getattr(pos, 'id', 0)) or 0), 'symbol': sym, 'volume': vol, 'side': side, 'open_price': open_price, 'last_bid': bid, 'last_ask': ask, 'profit': profit_val})
        return {'total': total, 'items': items}

async def on_position_profit(self) -> AsyncIterator[Any]:
        """Yield position profit updates (if supported by backend)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        h = getattr(self.acc, 'on_position_profit', None)
        if not h:
            raise NotImplementedError('on_position_profit not available')
        async for e in h():
            yield e

# --- 4) Trading & Orders ---
async def orders_total(self, pool: str='PENDING', *, unique_by_ticket: bool=True) -> int:
        """
        Count opened items.

        ┌────────┬───────────────────────────────────────────────────────────┐
        │ pool   │ Meaning                                                  │
        ├────────┼───────────────────────────────────────────────────────────┤
        │PENDING │ only pending orders                                      │
        │TRADES  │ only opened positions                                    │
        │OPENED  │ alias for positions                                      │
        │ALL     │ positions + pending (dedup by ticket by default)         │
        └────────┴───────────────────────────────────────────────────────────┘
        """
        snap = await self.opened_orders(0)
        positions = getattr(snap, 'positions', None) or getattr(snap, 'opened_positions', None) or []
        pending = getattr(snap, 'pending', None) or getattr(snap, 'orders', None) or getattr(snap, 'opened_orders', None) or []

        def _count(arr: Iterable[object]) -> int:
            if not unique_by_ticket:
                try:
                    return len(arr)
                except Exception:
                    pass
            seen = set()
            for it in arr:
                if isinstance(it, int):
                    seen.add(int(it))
                    continue
                val: Optional[int] = None
                for fld in ('ticket', 'order', 'order_ticket', 'id', 'position', 'position_id'):
                    v = getattr(it, fld, None)
                    if v is not None:
                        try:
                            val = int(v)
                            break
                        except Exception:
                            pass
                if val is None:
                    val = id(it)
                seen.add(val)
            return len(seen)
        pool_u = (pool or 'PENDING').upper()
        if pool_u == 'PENDING':
            return _count(pending)
        if pool_u in ('TRADES', 'OPENED', 'POSITIONS'):
            return _count(positions)
        if pool_u == 'ALL':
            return _count(positions) + _count(pending)
        raise ValueError(f'Unknown pool: {pool!r}')

async def positions_get(self) -> List[Any]:
        """Return list of current open positions (no pending)."""
        snap = await self.opened_orders(0)
        for field in ('positions', 'opened_positions', 'position_infos'):
            arr = getattr(snap, field, None)
            if arr:
                return list(arr)
        return []

async def position_get(self, *, ticket: Optional[int]=None, symbol: Optional[str]=None) -> Optional[Any]:
        """Return a single position by ticket or by symbol (case-insensitive)."""
        if (ticket is None) == (symbol is None):
            raise ValueError('Provide exactly one of: ticket or symbol')
        for p in await self.positions_get():
            if ticket is not None:
                try:
                    if int(getattr(p, 'ticket', getattr(p, 'id', 0)) or 0) == int(ticket):
                        return p
                except Exception:
                    continue
            else:
                s = (getattr(p, 'symbol', '') or getattr(p, 'symbol_name', '')).upper()
                if s == (symbol or '').upper():
                    return p
        return None

async def has_open_position(self, symbol: str | None=None, *, magic: int | None=None, direction: str | None=None, min_volume: float | None=None) -> bool:
        """Return True if there is at least one open position matching filters (symbol/magic/side/min_volume)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        want_dir = direction.upper() if direction else None
        want_sym = symbol.upper() if symbol else None
        if want_sym is None and magic is None and (want_dir is None) and (min_volume is None):
            total = await self.acc.positions_total()
            try:
                return int(total) > 0
            except Exception:
                return int(getattr(total, 'value', 0)) > 0
        data = await self.opened_orders(sort_mode=0)
        positions = getattr(data, 'positions', None) or getattr(data, 'opened_positions', None) or []

        def _side_from(pos: Any) -> Optional[str]:
            v = getattr(pos, 'type', getattr(pos, 'position_type', None))
            if isinstance(v, int):
                return 'BUY' if v == 0 else 'SELL' if v == 1 else None
            if isinstance(v, str):
                s = v.upper()
                if 'BUY' in s:
                    return 'BUY'
                if 'SELL' in s:
                    return 'SELL'
            return None
        for p in positions:
            if want_sym is not None:
                ps = (getattr(p, 'symbol', '') or getattr(p, 'symbol_name', '')).upper()
                if ps != want_sym:
                    continue
            if magic is not None:
                pm = getattr(p, 'magic', getattr(p, 'magic_number', None))
                if pm is None or int(pm) != int(magic):
                    continue
            if want_dir is not None:
                side = _side_from(p)
                if side != want_dir:
                    continue
            if min_volume is not None:
                vol = getattr(p, 'volume', getattr(p, 'lots', getattr(p, 'volume_current', 0.0)))
                try:
                    if float(vol) < float(min_volume):
                        continue
                except Exception:
                    continue
            return True
        return False

async def position_modify(self, ticket: int, *, sl: Optional[float]=None, tp: Optional[float]=None, deviation: Optional[int]=None, magic: Optional[int]=None, comment: Optional[str]=None, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """Modify SL/TP of an existing position; prefers native position_modify, falls back to order_modify."""
        if not self.acc:
            raise RuntimeError('Not connected')
        fn = getattr(self.acc, 'position_modify', None)
        if callable(fn):
            return await fn(ticket=int(ticket), sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, deadline=deadline, cancellation_event=cancellation_event)
        try:
            from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
        except Exception as e:
            raise NotImplementedError('position_modify is not supported by this package') from e
        req = th_pb2.OrderModifyRequest(ticket=int(ticket))
        if sl is not None:
            self._set_first_present(req, float(sl), 'stop_loss', 'sl')
        if tp is not None:
            self._set_first_present(req, float(tp), 'take_profit', 'tp')
        if deviation is not None:
            self._set_first_present(req, int(deviation), 'slippage', 'deviation')
        if magic is not None:
            self._set_if_has(req, 'magic', int(magic))
        if comment:
            self._set_if_has(req, 'comment', str(comment))
        modify = getattr(self.acc, 'order_modify', None)
        if not callable(modify):
            raise NotImplementedError('Neither position_modify nor order_modify is available')
        rep = await modify(request=req, deadline=deadline, cancellation_event=cancellation_event)
        return getattr(rep, 'data', rep)

async def position_close(self, ticket: int, *, volume: Optional[float]=None, price: Optional[float]=None, deviation: Optional[int]=None, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """Close position by ticket; tries multiple backends (position_close or order_close)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        fn = getattr(self.acc, 'position_close', None)
        if callable(fn):
            return await fn(ticket=int(ticket), volume=volume, price=price, deviation=deviation, deadline=deadline, cancellation_event=cancellation_event)
        from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
        if hasattr(th_pb2, 'PositionCloseRequest') and hasattr(self.acc, 'position_close'):
            req = th_pb2.PositionCloseRequest(ticket=int(ticket))
            if volume is not None:
                self._set_if_has(req, 'volume', float(volume))
            if price is not None:
                self._set_if_has(req, 'price', float(price))
            if deviation is not None:
                self._set_first_present(req, int(deviation), 'slippage', 'deviation')
            rep = await self.acc.position_close(request=req, deadline=deadline, cancellation_event=cancellation_event)
            return getattr(rep, 'data', rep)
        if hasattr(th_pb2, 'OrderCloseRequest') and hasattr(self.acc, 'order_close'):
            req = th_pb2.OrderCloseRequest(ticket=int(ticket))
            rep = await self.acc.order_close(request=req, deadline=deadline, cancellation_event=cancellation_event)
            return getattr(rep, 'data', rep)
        raise NotImplementedError('No supported close method found for this backend')

async def order_check(self, req: ah_pb2.OrderCheckRequest) -> Any:
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.order_check(req)

async def order_select(self, *, ticket: Optional[int]=None, index: Optional[int]=None, pool: str='TRADES', include_pending: bool=True, days_back: int=30, items_per_page: int=800) -> Optional[Any]:
        """Return order/position-like entry by ticket or by index from chosen pool."""
        if not self.acc:
            raise RuntimeError('Not connected')
        if (ticket is None) == (index is None):
            raise ValueError("Provide exactly one of 'ticket' or 'index'")
        pool_u = (pool or 'TRADES').upper()
        if pool_u in ('TRADES', 'OPENED'):
            snap = await self.opened_orders(sort_mode=0)
            positions = self._get_list_any(snap, ('positions', 'opened_positions', 'positions_list'))
            pending = self._get_list_any(snap, ('pending', 'orders', 'opened_orders', 'pending_orders'))
            search_list = list(positions) + (list(pending) if include_pending else [])
            if ticket is not None:
                t = int(ticket)
                for it in search_list:
                    if self._match_ticket(it, t):
                        return it
                return None
            idx = int(index)
            return search_list[idx] if 0 <= idx < len(search_list) else None
        if pool_u == 'PENDING':
            snap = await self.opened_orders(sort_mode=0)
            pending = self._get_list_any(snap, ('pending', 'orders', 'opened_orders', 'pending_orders'))
            if ticket is not None:
                t = int(ticket)
                for it in pending:
                    if self._match_ticket(it, t):
                        return it
                return None
            idx = int(index)
            return pending[idx] if 0 <= idx < len(pending) else None
        if pool_u == 'HISTORY':
            to_dt = datetime.now(tz=timezone.utc)
            from_dt = to_dt - timedelta(days=days_back)
            data = await self.order_history(from_dt=from_dt, to_dt=to_dt, page_number=0, items_per_page=items_per_page)
            candidates = self._extract_history_items(data)
            if ticket is not None:
                t = int(ticket)
                for it in candidates:
                    if self._match_ticket(it, t):
                        return it
                return None
            idx = int(index)
            return candidates[idx] if 0 <= idx < len(candidates) else None
        raise ValueError(f'Unknown pool: {pool!r}')

async def order_send_ex(self, symbol: str, *, side: str, kind: str='MARKET', volume: float, price: float=0.0, stop_price: Optional[float]=None, sl: Optional[float]=None, tp: Optional[float]=None, deviation: int=0, magic: Optional[int]=None, comment: Optional[str]=None, expiration: Optional[datetime | float | int]=None, type_time: Optional[int]=None, type_filling: Optional[int]=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """
        Build and send TradingHelper.OrderSend with friendly arguments.

        ┌───────────────┬────────────────────────────────────────────────────┐
        │ Param         │ Meaning                                            │
        ├───────────────┼────────────────────────────────────────────────────┤
        │ side          │ "BUY"/"SELL"                                       │
        │ kind          │ MARKET/LIMIT/STOP/STOP_LIMIT                        │
        │ price         │ main price (limit or market 0.0)                   │
        │ stop_price    │ trigger price (for STOP/STOP_LIMIT)                 │
        │ sl/tp         │ stop-loss / take-profit                             │
        │ deviation     │ slippage/deviation (proto‑specific)                 │
        │ expiration    │ datetime or epoch seconds                           │
        │ ensure_visible│ make symbol visible & optionally wait first tick    │
        └───────────────┴────────────────────────────────────────────────────┘
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        if ensure_visible:
            await self.ensure_symbol_visible(symbol, wait_for_tick=wait_for_tick)
        from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
        try:
            from google.protobuf.timestamp_pb2 import Timestamp
        except Exception:
            Timestamp = None
        op = self._resolve_operation_enum(th_pb2, side, kind)
        req = th_pb2.OrderSendRequest(symbol=symbol, operation=op, volume=float(volume), price=float(price or 0.0))
        if stop_price is not None:
            self._set_first_present(req, float(stop_price), 'stop_limit_price', 'stop_price', 'price_stop')
        if sl is not None:
            self._set_first_present(req, float(sl), 'stop_loss', 'sl')
        if tp is not None:
            self._set_first_present(req, float(tp), 'take_profit', 'tp')
        if deviation is not None:
            self._set_first_present(req, int(deviation), 'slippage', 'deviation')
        if magic is not None:
            self._set_if_has(req, 'magic', int(magic))
        if comment:
            self._set_if_has(req, 'comment', str(comment))
        if type_time is not None:
            self._set_first_present(req, int(type_time), 'type_time', 'time_type', 'time_in_force')
        if type_filling is not None:
            self._set_first_present(req, int(type_filling), 'type_filling', 'filling_type')
        if expiration is not None and Timestamp is not None:
            ts = Timestamp()
            if isinstance(expiration, datetime):
                dt = expiration if expiration.tzinfo else expiration.replace(tzinfo=timezone.utc)
                ts.FromDatetime(dt.astimezone(timezone.utc))
            else:
                ts.FromSeconds(int(float(expiration)))
            self._set_if_has(req, 'expiration', ts)
        reply = await self.acc.order_send(request=req, deadline=deadline, cancellation_event=cancellation_event)
        return getattr(reply, 'data', reply)

async def order_send_stop_limit(self, symbol: str, is_buy: bool, volume: float, stop_price: float, limit_price: float, *, sl: Optional[float]=None, tp: Optional[float]=None, deviation: int=0, magic: Optional[int]=None, comment: Optional[str]=None, expiration: Optional[datetime | float | int]=None, type_time: Optional[int]=None, type_filling: Optional[int]=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """Convenience: place STOP‑LIMIT using order_send_ex under the hood."""
        side = 'BUY' if is_buy else 'SELL'
        return await self.order_send_ex(symbol, side=side, kind='STOP_LIMIT', volume=volume, price=float(limit_price), stop_price=float(stop_price), sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, expiration=expiration, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def pending_modify(self, ticket: int, *, price: Optional[float]=None, stop_price: Optional[float]=None, sl: Optional[float]=None, tp: Optional[float]=None, deviation: Optional[int]=None, expiration: Optional[datetime | float | int]=None, type_time: Optional[int]=None, type_filling: Optional[int]=None, volume: Optional[float]=None, magic: Optional[int]=None, comment: Optional[str]=None, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """
        Modify a pending order by ticket via TradingHelper.OrderModify.

        Tip: Provide only the fields you want to change; others stay intact.
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        if all((v is None for v in (price, stop_price, sl, tp, deviation, expiration, type_time, type_filling, volume, magic, comment))):
            raise ValueError('Nothing to modify: provide at least one field')
        from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
        try:
            from google.protobuf.timestamp_pb2 import Timestamp
        except Exception:
            Timestamp = None
        req = th_pb2.OrderModifyRequest(ticket=int(ticket))
        if price is not None:
            self._set_first_present(req, float(price), 'price', 'limit_price')
        if stop_price is not None:
            self._set_first_present(req, float(stop_price), 'stop_limit_price', 'stop_price', 'price_stop')
        if sl is not None:
            self._set_first_present(req, float(sl), 'stop_loss', 'sl')
        if tp is not None:
            self._set_first_present(req, float(tp), 'take_profit', 'tp')
        if deviation is not None:
            self._set_first_present(req, int(deviation), 'slippage', 'deviation')
        if type_time is not None:
            self._set_first_present(req, int(type_time), 'type_time', 'time_type', 'time_in_force')
        if type_filling is not None:
            self._set_first_present(req, int(type_filling), 'type_filling', 'filling_type')
        if expiration is not None and Timestamp is not None:
            ts = Timestamp()
            if isinstance(expiration, datetime):
                dt = expiration if expiration.tzinfo else expiration.replace(tzinfo=timezone.utc)
                ts.FromDatetime(dt.astimezone(timezone.utc))
            else:
                ts.FromSeconds(int(float(expiration)))
            self._set_if_has(req, 'expiration', ts)
        if volume is not None:
            self._set_if_has(req, 'volume', float(volume))
        if magic is not None:
            self._set_if_has(req, 'magic', int(magic))
        if comment:
            self._set_if_has(req, 'comment', str(comment))
        modify = getattr(self.acc, 'order_modify', None)
        if not callable(modify):
            raise NotImplementedError('order_modify is not available in this package')
        rep = await modify(request=req, deadline=deadline, cancellation_event=cancellation_event)
        return getattr(rep, 'data', rep)

async def pending_replace_stop_limit(self, ticket: int, *, stop_price: float, limit_price: float, is_buy: Optional[bool]=None, volume: Optional[float]=None, sl: Optional[float]=None, tp: Optional[float]=None, deviation: int=0, magic: Optional[int]=None, comment: Optional[str]=None, expiration: Optional[datetime | float | int]=None, prefer_modify: bool=True, ensure_visible: bool=True, wait_for_tick: bool=True, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """
        Replace an existing pending order with a STOP‑LIMIT order.

        ┌──────────────┬─────────────────────────────────────────────────────┐
        │ prefer_modify│ try modify in-place; if not OK → delete + recreate  │
        │ is_buy       │ deduced from order.type if None                      │
        │ carry-over   │ sl/tp/magic/comment/expiration are preserved by def. │
        └──────────────┴─────────────────────────────────────────────────────┘
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        if stop_price <= 0 or limit_price <= 0:
            raise ValueError('stop_price and limit_price must be > 0')
        cur = await self.order_select(ticket=ticket, pool='PENDING')
        if cur is None:
            raise ValueError(f'Pending order ticket={ticket} not found')
        sym = (getattr(cur, 'symbol', '') or getattr(cur, 'symbol_name', '')).upper()
        cur_vol = float(getattr(cur, 'volume', getattr(cur, 'lots', 0.0)) or 0.0)
        cur_sl = self._get_first(cur, 'stop_loss', 'sl')
        cur_tp = self._get_first(cur, 'take_profit', 'tp')
        cur_mag = self._get_first(cur, 'magic', 'magic_number')
        cur_cmt = self._get_first(cur, 'comment', 'order_comment')
        cur_exp = self._get_first(cur, 'expiration', 'expiry', 'time_expiration')
        if is_buy is None:
            t = getattr(cur, 'type', getattr(cur, 'order_type', None))
            if isinstance(t, int):
                is_buy = t == 0
            elif isinstance(t, str):
                is_buy = 'BUY' in t.upper()
            else:
                is_buy = True
        side = 'BUY' if is_buy else 'SELL'
        vol = float(volume if volume is not None else cur_vol)
        if vol <= 0:
            raise ValueError('volume must be > 0')
        if prefer_modify:
            try:
                rep = await self.pending_modify(ticket=ticket, price=float(limit_price), stop_price=float(stop_price), sl=float(sl) if sl is not None else None, tp=float(tp) if tp is not None else None, deviation=int(deviation), expiration=self._normalize_exp(expiration))
                if self._is_reply_ok(rep):
                    return rep
            except Exception:
                pass
        from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
        if hasattr(th_pb2, 'OrderCloseRequest') and hasattr(self.acc, 'order_close'):
            close_req = th_pb2.OrderCloseRequest(ticket=int(ticket))
            _ = await self.acc.order_close(request=close_req, deadline=deadline, cancellation_event=cancellation_event)
        else:
            raise RuntimeError('Backend does not support pending delete (order_close not available)')
        if ensure_visible:
            await self.ensure_symbol_visible(sym, wait_for_tick=wait_for_tick)
        rep2 = await self.order_send_ex(sym, side=side, kind='STOP_LIMIT', volume=vol, price=float(limit_price), stop_price=float(stop_price), sl=float(sl if sl is not None else cur_sl) if sl is not None or cur_sl is not None else None, tp=float(tp if tp is not None else cur_tp) if tp is not None or cur_tp is not None else None, deviation=int(deviation), magic=int(magic if magic is not None else cur_mag) if magic is not None or cur_mag is not None else None, comment=str(comment if comment is not None else cur_cmt) if comment is not None or cur_cmt is not None else None, expiration=self._normalize_exp(expiration if expiration is not None else cur_exp), deadline=deadline, cancellation_event=cancellation_event)
        return rep2

async def orders_history(self, *, from_dt: datetime | int | None=None, to_dt: datetime | int | None=None, days_back: int=7, page: int=0, size: int=800, sort_mode: Optional[int]=None, fetch_all: bool=False, return_raw: bool=False) -> Any:
        """
        Get order history; return flat list (default) or raw pages.

        ┌────────────┬───────────────────────────────────────────────────────┐
        │ fetch_all  │ paginate until last page, concatenate items           │
        │ return_raw │ return page objects instead of a flat list            │
        └────────────┴───────────────────────────────────────────────────────┘
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        if to_dt is None:
            to_dt = datetime.now(tz=timezone.utc)
        if from_dt is None:
            from_dt = self._to_dt(to_dt) - timedelta(days=days_back)
        if sort_mode is None:
            sort_mode = ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_ASC
        raw_pages: List[Any] = []
        flat_items: List[Any] = []
        p = int(page)
        while True:
            reply = await self.order_history(from_dt=from_dt, to_dt=to_dt, sort_mode=sort_mode, page_number=p, items_per_page=size)
            if reply is None:
                break
            if return_raw:
                raw_pages.append(reply)
            else:
                flat_items.extend(self._extract_history_items(reply))
            if not fetch_all:
                break
            n = len(self._extract_history_items(reply))
            if n < size or n == 0:
                break
            p += 1
        if return_raw:
            return raw_pages[0] if not fetch_all else raw_pages
        return flat_items

async def history_order_by_ticket(self, ticket: int, *, days_back: int=30, items_per_page: int=800) -> Optional[Any]:
        """Find historical order by ticket (quick scan of one page after checking opened)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        try:
            snap = await self.opened_orders(sort_mode=0)
            for name in ('orders', 'pending', 'opened_orders', 'positions'):
                arr = getattr(snap, name, None)
                if isinstance(arr, (list, tuple)):
                    for item in arr:
                        for fld in ('ticket', 'order', 'order_ticket', 'id'):
                            v = getattr(item, fld, None)
                            if v is not None and int(v) == int(ticket):
                                return item
        except Exception:
            pass
        to_dt = datetime.now(tz=timezone.utc)
        from_dt = to_dt - timedelta(days=days_back)
        data = await self.order_history(from_dt=from_dt, to_dt=to_dt, page_number=0, items_per_page=items_per_page)
        for it in self._extract_history_items(data):
            for fld in ('ticket', 'order', 'order_ticket', 'id'):
                v = getattr(it, fld, None)
                if v is not None and int(v) == int(ticket):
                    return it
        return None

async def history_deal_by_ticket(self, ticket: int, *, days_back: int=30, page_size: int=500, max_pages: int=40) -> Optional[Any]:
        """Find historical 'deal-like' entry by ticket scanning history pages."""
        if not self.acc:
            raise RuntimeError('Not connected')
        to_dt = datetime.now(datetime.UTC).replace(tzinfo=timezone.utc)
        from_dt = to_dt - timedelta(days=days_back)
        sort_mode = ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_ASC
        for page in range(max_pages):
            data = await self.acc.order_history(from_dt=from_dt, to_dt=to_dt, sort_mode=sort_mode, page_number=page, items_per_page=page_size)
            if data is None:
                break
            found = self._find_any_by_ticket(data, ticket)
            if found is not None:
                return found
            n = self._first_container_len(data)
            if n is None or n < page_size:
                break
        return None

async def history_deals_get(self, from_dt: datetime | int, to_dt: datetime | int, *, symbol: str | None=None, direction: str | None=None, magic: int | None=None, limit: int | None=None, page_size: int=500, max_pages: int=100) -> List[Any]:
        """Return list of deal-like records within interval via OrderHistory + filtering."""
        if not self.acc:
            raise RuntimeError('Not connected')
        f = self._to_dt(from_dt)
        t = self._to_dt(to_dt)
        want_sym = symbol.upper() if symbol else None
        want_dir = direction.upper() if direction else None
        sort_mode = ah_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE.BMT5_SORT_BY_CLOSE_TIME_ASC
        out: List[Any] = []
        for page in range(max_pages):
            data = await self.acc.order_history(from_dt=f, to_dt=t, sort_mode=sort_mode, page_number=page, items_per_page=page_size)
            if data is None:
                break
            for item in self._iter_history_items(data):
                if not self._is_deal_like(item):
                    continue
                if want_sym:
                    sym = (getattr(item, 'symbol', '') or getattr(item, 'symbol_name', '')).upper()
                    if sym != want_sym:
                        continue
                if magic is not None:
                    mg = getattr(item, 'magic', getattr(item, 'magic_number', None))
                    if mg is None or int(mg) != int(magic):
                        continue
                if want_dir:
                    side = self._dir_from(item)
                    if side and side != want_dir:
                        continue
                out.append(item)
                if limit is not None and len(out) >= limit:
                    return out
            n = self._first_container_len(data)
            if n is None or n < page_size:
                break
        return out

async def history_deals_total(self, from_dt: datetime | int, to_dt: datetime | int) -> Optional[int]:
        """Best‑effort total: try 'total' fields on page 0, else number of items in first container."""
        if not self.acc:
            raise RuntimeError('Not connected')
        data = await self.order_history(from_dt=from_dt, to_dt=to_dt, page_number=0, items_per_page=1)
        for name in ('total_items', 'total', 'items_total', 'records', 'count'):
            val = getattr(data, name, None)
            if isinstance(val, int):
                return val
            try:
                if val is not None and isinstance(int(val), int):
                    return int(val)
            except Exception:
                pass
        page_info = getattr(data, 'page_info', None)
        if page_info is not None:
            for name in ('total_items', 'total', 'items_total', 'records', 'count'):
                val = getattr(page_info, name, None)
                if isinstance(val, int):
                    return val
                try:
                    if val is not None and isinstance(int(val), int):
                        return int(val)
                except Exception:
                    pass
        return self._first_container_len(data)

async def on_trade(self) -> AsyncIterator[Any]:
        if not self.acc:
            raise RuntimeError('Not connected')
        h = getattr(self.acc, 'on_trade', None)
        if not h:
            raise NotImplementedError('on_trade not available')
        async for tr in h():
            yield tr

async def on_positions_and_pending_orders_tickets(self) -> AsyncIterator[Any]:
        if not self.acc:
            raise RuntimeError('Not connected')
        h = getattr(self.acc, 'on_positions_and_pending_orders_tickets', None)
        if not h:
            raise NotImplementedError('on_positions_and_pending_orders_tickets not available')
        async for item in h():
            yield item

async def on_opened_orders_tickets(self, *, include_pending: bool=True, emit_on_change_only: bool=True, poll_ms: int=500, total_ms: Optional[int]=None) -> AsyncIterator[Dict[str, List[int]]]:
        """
        Yield snapshots of opened order tickets.

        Preference order:
          • Use package stream 'on_positions_and_pending_orders_tickets' if present.
          • Else poll 'opened_orders_tickets' periodically.

        Output: {"positions":[...], "pending":[...], "all":[...]}
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        stream = getattr(self.acc, 'on_positions_and_pending_orders_tickets', None)
        if callable(stream):
            prev_all: Optional[List[int]] = None
            async for item in stream():
                pos = self._extract_ticket_list(item, prefer=('positions_tickets', 'position_tickets', 'positions'))
                pend = self._extract_ticket_list(item, prefer=('pending_orders_tickets', 'pending_tickets', 'pending'))
                if not include_pending:
                    pend = []
                all_t = self._uniq_ints(pos + pend)
                if emit_on_change_only and prev_all == all_t:
                    continue
                prev_all = all_t
                yield {'positions': pos, 'pending': pend, 'all': all_t}
            return
        get_snap = getattr(self.acc, 'opened_orders_tickets', None)
        if not callable(get_snap):
            raise NotImplementedError('Neither stream nor snapshot method is available in this package version.')
        t0 = time.monotonic()
        prev_all: Optional[List[int]] = None
        while True:
            snap = await get_snap()
            pos = self._extract_ticket_list(snap, prefer=('positions', 'positions_tickets', 'position_tickets'))
            pend = self._extract_ticket_list(snap, prefer=('pending', 'pending_orders_tickets', 'pending_tickets'))
            if not include_pending:
                pend = []
            all_t = self._uniq_ints(pos + pend)
            if not emit_on_change_only or prev_all != all_t:
                prev_all = all_t
                yield {'positions': pos, 'pending': pend, 'all': all_t}
            if total_ms is not None and (time.monotonic() - t0) * 1000.0 >= total_ms:
                break
            await asyncio.sleep(poll_ms / 1000.0)

@staticmethod
def _is_deal_like(obj: Any) -> bool:
        for f in ('deal', 'deal_ticket'):
            if getattr(obj, f, None) is not None:
                return True
        et = getattr(obj, 'entry_type', getattr(obj, 'entry_kind', None))
        if isinstance(et, str) and 'DEAL' in et.upper():
            return True
        if isinstance(et, int):
            pass
        has_ticket = getattr(obj, 'ticket', None) is not None
        has_qty = any((getattr(obj, f, None) is not None for f in ('volume', 'lots', 'volume_current')))
        has_price = any((getattr(obj, f, None) is not None for f in ('price', 'price_open', 'price_close')))
        return bool(has_ticket and has_qty and has_price)

async def cancel_all_pendings(self, *, symbol: str | None=None, direction: str | None=None, deviation: int | None=None, deadline=None, cancellation_event=None, on_error: str='continue') -> dict:
        """
        Cancel all pending orders (optionally filtered by symbol and side).
        Returns {"canceled":[tickets...], "errors":[{"ticket":..., "error":"..."}]}.
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        sym_u = symbol.upper() if symbol else None
        dir_u = direction.upper() if direction else None
        snap = await self.opened_orders(0)
        pending = getattr(snap, 'pending', None) or getattr(snap, 'orders', None) or getattr(snap, 'opened_orders', None) or []
        targets: list[int] = []
        for it in pending:
            t = int(getattr(it, 'ticket', getattr(it, 'order', getattr(it, 'id', 0))) or 0)
            if not t:
                continue
            if sym_u:
                ps = (getattr(it, 'symbol', '') or getattr(it, 'symbol_name', '')).upper()
                if ps != sym_u:
                    continue
            if dir_u:
                v = getattr(it, 'type', getattr(it, 'order_type', None))
                side = None
                if isinstance(v, int):
                    side = 'BUY' if v == 0 else 'SELL' if v == 1 else None
                elif isinstance(v, str):
                    s = v.upper()
                    side = 'BUY' if 'BUY' in s else 'SELL' if 'SELL' in s else None
                if side != dir_u:
                    continue
            targets.append(t)
        canceled: list[int] = []
        errors: list[dict] = []
        for t in targets:
            try:
                _ = await self.cancel_order(ticket=t, deviation=deviation, deadline=deadline, cancellation_event=cancellation_event)
                canceled.append(t)
            except Exception as e:
                errors.append({'ticket': t, 'error': str(e)})
                if on_error == 'raise':
                    raise
        return {'canceled': canceled, 'errors': errors}

async def close_symbol_positions(self, symbol: str, *, direction: str | None=None, deviation: int | None=None, deadline=None, cancellation_event=None) -> dict:
        """Close all positions for a given symbol (optionally only BUY or SELL)."""
        return await self.close_all_positions(symbol=symbol, direction=direction, deviation=deviation, deadline=deadline, cancellation_event=cancellation_event)

async def cancel_order(self, ticket: int, *, deviation: Optional[int]=None, deadline: Any=None, cancellation_event: Any=None) -> Any:
        """
        Cancel/delete a pending order by ticket (a.k.a. DeleteOrder).
        Under the hood uses TradingHelper.OrderClose(ticket=...).
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        from MetaRpcMT5 import mt5_term_api_trading_helper_pb2 as th_pb2
        req = th_pb2.OrderCloseRequest(ticket=int(ticket))
        if deviation is not None and hasattr(req, 'deviation'):
            req.deviation = int(deviation)
        rep = await self.acc.order_close(request=req, deadline=deadline, cancellation_event=cancellation_event)
        return getattr(rep, 'data', rep)

async def close_all_positions(self, *, symbol: Optional[str]=None, direction: Optional[str]=None, deviation: Optional[int]=None, deadline: Any=None, cancellation_event: Any=None, on_error: str='continue') -> Dict[str, Any]:
        """
        Close all open positions (optionally filter by symbol and/or direction).
        Returns {"closed": [tickets...], "errors": [{"ticket": ..., "error": "..."}]}.
        """
        if not self.acc:
            raise RuntimeError('Not connected')
        sym_u = symbol.upper() if symbol else None
        dir_u = direction.upper() if direction else None
        positions = await self.positions_get()

        def _side_from(pos: Any) -> Optional[str]:
            v = getattr(pos, 'type', getattr(pos, 'position_type', None))
            if isinstance(v, int):
                return 'BUY' if v == 0 else 'SELL' if v == 1 else None
            if isinstance(v, str):
                s = v.upper()
                if 'BUY' in s:
                    return 'BUY'
                if 'SELL' in s:
                    return 'SELL'
            return None
        targets = []
        for p in positions:
            psym = (getattr(p, 'symbol', '') or getattr(p, 'symbol_name', '')).upper()
            if sym_u and psym != sym_u:
                continue
            if dir_u:
                if _side_from(p) != dir_u:
                    continue
            t = int(getattr(p, 'ticket', getattr(p, 'id', 0)) or 0)
            if t:
                targets.append(t)
        closed: List[int] = []
        errors: List[Dict[str, Any]] = []
        for t in targets:
            try:
                _ = await self.position_close(ticket=t, deviation=deviation, deadline=deadline, cancellation_event=cancellation_event)
                closed.append(t)
            except Exception as e:
                errors.append({'ticket': t, 'error': str(e)})
                if on_error == 'raise':
                    raise
        return {'closed': closed, 'errors': errors}

async def buy_market(self, symbol: str, volume: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_ex(symbol, side='BUY', kind='MARKET', volume=volume, price=0.0, sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def sell_market(self, symbol: str, volume: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_ex(symbol, side='SELL', kind='MARKET', volume=volume, price=0.0, sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def place_buy_limit(self, symbol: str, volume: float, price: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_ex(symbol, side='BUY', kind='LIMIT', volume=volume, price=float(price), sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def place_sell_limit(self, symbol: str, volume: float, price: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_ex(symbol, side='SELL', kind='LIMIT', volume=volume, price=float(price), sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def place_buy_stop(self, symbol: str, volume: float, price: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_ex(symbol, side='BUY', kind='STOP', volume=volume, price=float(price), sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def place_sell_stop(self, symbol: str, volume: float, price: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_ex(symbol, side='SELL', kind='STOP', volume=volume, price=float(price), sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def place_buy_stop_limit(self, symbol: str, volume: float, stop_price: float, limit_price: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, expiration=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_stop_limit(symbol, True, volume, stop_price, limit_price, sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, expiration=expiration, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def place_sell_stop_limit(self, symbol: str, volume: float, stop_price: float, limit_price: float, *, sl: float | None=None, tp: float | None=None, deviation: int=0, magic: int | None=None, comment: str | None=None, expiration=None, type_time: int | None=None, type_filling: int | None=None, ensure_visible: bool=True, wait_for_tick: bool=True, deadline=None, cancellation_event=None) -> Any:
        return await self.order_send_stop_limit(symbol, False, volume, stop_price, limit_price, sl=sl, tp=tp, deviation=deviation, magic=magic, comment=comment, expiration=expiration, type_time=type_time, type_filling=type_filling, ensure_visible=ensure_visible, wait_for_tick=wait_for_tick, deadline=deadline, cancellation_event=cancellation_event)

async def deals_count(self, from_dt, to_dt, *, symbol: str | None=None, direction: str | None=None, magic: int | None=None) -> int:
        items = await self.history_deals_get(from_dt, to_dt, symbol=symbol, direction=direction, magic=magic)
        return len(items)

async def order_send(self, request: Any) -> Any:
        """Low-level order send. Pass the pb2 request from MetaRpcMT5.trade_functions_pb2.OrderSendRequest."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.order_send(request=request)

async def order_modify(self, request: Any) -> Any:
        """Low-level order modify. Pass pb2 request."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.order_modify(request=request)

async def order_close(self, request: Any) -> Any:
        """Low-level order/position close. Pass pb2 request."""
        if not self.acc:
            raise RuntimeError('Not connected')
        return await self.acc.order_close(request=request)

async def on_trade_transaction(self) -> AsyncIterator[Any]:
        """Yield trade transaction events from terminal."""
        if not self.acc:
            raise RuntimeError('Not connected')
        h = getattr(self.acc, 'on_trade_transaction', None)
        if not h:
            raise NotImplementedError('on_trade_transaction not available')
        async for e in h():
            yield e

async def positions_by_symbol(self, symbol: str) -> List[Any]:
        if not self.acc:
            raise RuntimeError('Not connected')
        want = (symbol or '').upper()
        out: List[Any] = []
        for p in await self.positions_get():
            psym = (getattr(p, 'symbol', '') or getattr(p, 'symbol_name', '')).upper()
            if psym == want:
                out.append(p)
        return out

async def pending_orders_total(self) -> int:
        if not self.acc:
            raise RuntimeError('Not connected')
        snap = await self.opened_orders(0)
        for field in ('pending', 'orders', 'opened_orders', 'pending_orders', 'order_infos'):
            arr = getattr(snap, field, None)
            if arr:
                try:
                    return int(getattr(arr, 'Count', len(arr)))
                except Exception:
                    return len(list(arr))
        return 0

async def positions_by_symbol(self, symbol: str) -> List[Any]:
    if not self.acc:
        raise RuntimeError('Not connected')
    want = (symbol or '').upper()
    out: List[Any] = []
    for p in await self.positions_get():
        psym = (getattr(p, 'symbol', '') or getattr(p, 'symbol_name', '')).upper()
        if psym == want:
            out.append(p)
    return out

async def pending_orders_total(self) -> int:
    if not self.acc:
        raise RuntimeError('Not connected')
    snap = await self.opened_orders(0)
    for field in ('pending', 'orders', 'opened_orders', 'pending_orders', 'order_infos'):
        arr = getattr(snap, field, None)
        if arr:
            try:
                return int(getattr(arr, 'Count', len(arr)))
            except Exception:
                try:
                    return len(list(arr))
                except Exception:
                    pass
    return 0

async def opened_orders_tickets(self):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    return await acc.opened_orders_tickets()

async def positions_total(self):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    return await acc.positions_total()

async def opened_orders_tickets(self, *args, **kwargs):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise RuntimeError('Not connected')
    return await acc.opened_orders_tickets(*args, **kwargs)

def normalize_opened_orders(opened_msg):
    """Return dict with 'positions' and 'pending' as plain Python lists of dicts."""
    from google.protobuf.json_format import MessageToDict
    d = MessageToDict(opened_msg, preserving_proto_field_name=True)
    raw_positions = d.get('position_infos') or d.get('positions') or []
    raw_pending = d.get('pending_orders') or d.get('orders') or []
    keys = ['ticket', 'symbol', 'volume', 'price_open', 'price_current', 'sl', 'tp', 'profit']

    def to_summary(item):
        if isinstance(item, dict):
            return {k: item.get(k) for k in keys}
        return {k: getattr(item, k, None) for k in keys}
    return {'positions': [to_summary(it) for it in raw_positions], 'pending': [to_summary(it) for it in raw_pending]}

# --- 5) History & Lookups ---
@staticmethod
def _extract_history_items(data: Any) -> list:
        for name in ('orders', 'deals', 'entries', 'history', 'items', 'records'):
            arr = getattr(data, name, None)
            if isinstance(arr, (list, tuple)):
                return list(arr)
        for name in dir(data):
            if name.startswith('_'):
                continue
            arr = getattr(data, name, None)
            if isinstance(arr, (list, tuple)):
                return list(arr)
        return []

@staticmethod
def _iter_history_items(root: Any):
        for name in dir(root):
            if name.startswith('_'):
                continue
            val = getattr(root, name, None)
            if isinstance(val, (list, tuple)):
                for x in val:
                    yield x

# --- 7) Internal Helpers ---
def _get(obj, *names):
    for n in names:
        try:
            v = getattr(obj, n)
        except Exception:
            v = None
        if v is not None:
            return v
    return None

def _as_int_ts(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, datetime):
        if x.tzinfo is None:
            x = x.replace(tzinfo=timezone.utc)
        return int(x.timestamp())
    try:
        return int(float(x))
    except Exception:
        return None

def _tf_code(tf):
    if isinstance(tf, int):
        return tf
    return _TF_CODE.get(str(tf).upper().strip(), 16385)

def _tf_minutes(tf):
    s = (str(tf).upper().strip()) if not isinstance(tf, int) else str(tf)
    if s.startswith('M'):
        try:
            return int(s[1:])
        except Exception:
            return 1
    return 60 

def _get(o, *names):
    for n in names:
        if hasattr(o, n):
            return getattr(o, n)
        if isinstance(o, dict) and n in o:
            return o[n]
    return None

def _ohlc_row(c):
    def unbox(v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        return float(_get(v, 'value', 'Value'))
    return {
        'time': _as_int_ts(_get(c, 'time', 'Time')),
        'open': unbox(_get(c, 'open', 'Open')),
        'high': unbox(_get(c, 'high', 'High')),
        'low':  unbox(_get(c, 'low',  'Low')),
        'close':unbox(_get(c, 'close','Close')),
        'tick_volume': int(_get(c, 'tick_volume', 'TickVolume') or 0),
        'spread': int(_get(c, 'spread', 'Spread') or 0),
        'real_volume': int(_get(c, 'real_volume', 'RealVolume') or 0),
    }

def _tick_row(t):
    def unbox(v):
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        return float(_get(v, 'value', 'Value'))
    return {
        'time': _as_int_ts(_get(t, 'time', 'Time')),
        'bid': unbox(_get(t, 'bid', 'Bid')),
        'ask': unbox(_get(t, 'ask', 'Ask')),
        'last':unbox(_get(t, 'last','Last')),
        'volume': unbox(_get(t, 'volume', 'Volume')),
        'flags': int(_get(t, 'flags', 'Flags') or 0),
    }

def __init__(self, cfg: MT5Config):
    self.cfg = cfg
    self.acc = None
    self.logger = None
    self._timeout = int(getattr(cfg, "timeout_seconds", 90))
    self._base_chart_symbol = getattr(cfg, "base_chart_symbol", "EURUSD")

@staticmethod
def _ts(dt: datetime | int | float) -> "Timestamp":
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(float(dt), tz=timezone.utc)
    elif isinstance(dt, datetime) and dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    ts = Timestamp()
    ts.FromDatetime(dt)  # UTC-aware
    return ts

@staticmethod
def _set_if_has(obj: object, name: str, value) -> None:
        if hasattr(obj, name):
            setattr(obj, name, value)

@staticmethod
def _set_first_present(obj: object, value, *names: str) -> None:
        for n in names:
            if hasattr(obj, n):
                setattr(obj, n, value)
                return

@staticmethod
def _resolve_operation_enum(th_pb2, side: str, kind: str) -> int:
        """
        Map (side, kind) to protobuf enum constant in a tolerant way.

        ┌──────────┬───────────────┬─────────────────────────────────────────┐
        │ side     │ kind          │ enum names tried (in this order)        │
        ├──────────┼───────────────┼─────────────────────────────────────────┤
        │ BUY      │ MARKET        │ TF_ORDER_TYPE_TF_BUY, ORDER_TYPE_BUY    │
        │ SELL     │ MARKET        │ TF_ORDER_TYPE_TF_SELL, ORDER_TYPE_SELL  │
        │ BUY      │ LIMIT         │ TF_ORDER_TYPE_TF_BUY_LIMIT, ...         │
        │ SELL     │ LIMIT         │ TF_ORDER_TYPE_TF_SELL_LIMIT, ...        │
        │ BUY      │ STOP          │ TF_ORDER_TYPE_TF_BUY_STOP, ...          │
        │ SELL     │ STOP          │ TF_ORDER_TYPE_TF_SELL_STOP, ...         │
        │ BUY      │ STOP_LIMIT    │ TF_ORDER_TYPE_TF_BUY_STOP_LIMIT, ...    │
        │ SELL     │ STOP_LIMIT    │ TF_ORDER_TYPE_TF_SELL_STOP_LIMIT, ...   │
        └──────────┴───────────────┴─────────────────────────────────────────┘
        """
        side_u = (side or '').upper()
        kind_u = (kind or 'MARKET').upper()
        wanted = {('BUY', 'MARKET'): ('TF_ORDER_TYPE_TF_BUY', 'ORDER_TYPE_BUY'), ('SELL', 'MARKET'): ('TF_ORDER_TYPE_TF_SELL', 'ORDER_TYPE_SELL'), ('BUY', 'LIMIT'): ('TF_ORDER_TYPE_TF_BUY_LIMIT', 'ORDER_TYPE_BUY_LIMIT'), ('SELL', 'LIMIT'): ('TF_ORDER_TYPE_TF_SELL_LIMIT', 'ORDER_TYPE_SELL_LIMIT'), ('BUY', 'STOP'): ('TF_ORDER_TYPE_TF_BUY_STOP', 'ORDER_TYPE_BUY_STOP'), ('SELL', 'STOP'): ('TF_ORDER_TYPE_TF_SELL_STOP', 'ORDER_TYPE_SELL_STOP'), ('BUY', 'STOP_LIMIT'): ('TF_ORDER_TYPE_TF_BUY_STOP_LIMIT', 'ORDER_TYPE_BUY_STOP_LIMIT'), ('SELL', 'STOP_LIMIT'): ('TF_ORDER_TYPE_TF_SELL_STOP_LIMIT', 'ORDER_TYPE_SELL_STOP_LIMIT')}[side_u, kind_u]
        pool = {name: getattr(th_pb2, name) for name in dir(th_pb2) if name.isupper() and isinstance(getattr(th_pb2, name), int)}
        for name in wanted:
            if name in pool:
                return int(pool[name])
        for k, v in pool.items():
            if k.endswith(wanted[-1]):
                return int(v)
        raise ValueError(f'Unsupported operation for side={side_u}, kind={kind_u}')

@staticmethod
def _get_list_any(root: object, names: Iterable[str]) -> list:
        for name in names:
            arr = getattr(root, name, None)
            if isinstance(arr, (list, tuple)):
                return list(arr)
        return []

@staticmethod
def _scan_first_list(root: object) -> list:
        for name in dir(root):
            if name.startswith('_'):
                continue
            arr = getattr(root, name, None)
            if isinstance(arr, (list, tuple)):
                return list(arr)
        return []

@staticmethod
def _match_ticket(obj: object, ticket: int) -> bool:
        for fld in ('ticket', 'order', 'order_ticket', 'id', 'position', 'position_id'):
            try:
                v = getattr(obj, fld, None)
                if v is not None and int(v) == int(ticket):
                    return True
            except Exception:
                continue
        return False

@staticmethod
def _dir_from(obj: Any) -> Optional[str]:
        v = getattr(obj, 'type', getattr(obj, 'order_type', getattr(obj, 'position_type', None)))
        if isinstance(v, str):
            s = v.upper()
            if 'BUY' in s:
                return 'BUY'
            if 'SELL' in s:
                return 'SELL'
            return None
        if isinstance(v, int):
            return 'BUY' if v == 0 else 'SELL' if v == 1 else None
        return None

@staticmethod
def _first_container_len(root: Any) -> Optional[int]:
        for name in dir(root):
            if name.startswith('_'):
                continue
            val = getattr(root, name, None)
            if isinstance(val, (list, tuple)):
                try:
                    return len(val)
                except Exception:
                    return None
        return None

@staticmethod
def _get_first(obj: object, *names: str):
        for n in names:
            try:
                v = getattr(obj, n)
            except Exception:
                v = None
            if v is not None:
                return v
        return None

@staticmethod
def _is_reply_ok(reply: object) -> bool:
        objs = [reply, getattr(reply, 'data', None)]
        for o in objs:
            if o is None:
                continue
            for nm in ('returned_code', 'retcode', 'code'):
                try:
                    v = getattr(o, nm, None)
                    if v is not None and int(v) == 0:
                        return True
                except Exception:
                    pass
            s = getattr(o, 'returned_string_code', None)
            if isinstance(s, str) and s.upper() in ('OK', 'TRADE_RETCODE_DONE', 'DONE', 'ACCEPTED', 'REQUEST_ACCEPTED'):
                return True
        return False

@staticmethod
def _normalize_exp(exp):
        if exp is None:
            return None
        if isinstance(exp, datetime):
            return exp if exp.tzinfo else exp.replace(tzinfo=timezone.utc)
        try:
            return datetime.fromtimestamp(float(exp), tz=timezone.utc)
        except Exception:
            return None

def _as_int_list(x):
    out = []
    try:
        for v in x or []:
            try:
                out.append(int(v))
            except Exception:
                pass
    except Exception:
        pass
    return out

def _extract_ticket_list(root, prefer=()):
    for name in prefer:
        xs = getattr(root, name, None)
        if isinstance(xs, (list, tuple)):
            return _as_int_list(xs)
    for nm in dir(root):
        if nm.startswith('_'):
            continue
        xs = getattr(root, nm, None)
        if isinstance(xs, (list, tuple)):
            return _as_int_list(xs)
    return []

def _uniq_ints(xs):
    try:
        return sorted(set((int(v) for v in xs)))
    except Exception:
        return list(xs)

def _svc_getattr(self, name: str):
    acc = getattr(self, 'acc', None)
    if acc is None:
        raise AttributeError(name)
    import inspect as _inspect
    attr = getattr(acc, name)
    if _inspect.iscoroutinefunction(attr):

        async def _proxy(*a, **kw):
            return await attr(*a, **kw)
        return _proxy
    if callable(attr):

        def _proxy(*a, **kw):
            return attr(*a, **kw)
        return _proxy
    return attr

def _tf_minutes(tf: str | int):
    if isinstance(tf, int):
        return tf
    tf = str(tf).upper().strip()
    table = {'M1': 1, 'M2': 2, 'M3': 3, 'M4': 4, 'M5': 5, 'M6': 6, 'M10': 10, 'M12': 12, 'M15': 15, 'M20': 20, 'M30': 30, 'H1': 60, 'H2': 120, 'H3': 180, 'H4': 240, 'H6': 360, 'H8': 480, 'H12': 720, 'D1': 1440, 'W1': 10080, 'MN1': 43200}
    return table.get(tf, 60)

def _safe_ts(x):
    try:
        if isinstance(x, datetime):
            return int(x.timestamp())
        if hasattr(x, 'seconds'):
            return int(x.seconds)
        if isinstance(x, (int, float)):
            return int(x)
    except Exception:
        pass
    return None

def _ohlc_row(c):

    def g(o, name, alt=None):
        if hasattr(o, name):
            return getattr(o, name)
        if alt and hasattr(o, alt):
            return getattr(o, alt)
        if isinstance(o, dict):
            return o.get(name, o.get(alt))
        return None
    return {'time': _safe_ts(g(c, 'time')), 'open': g(c, 'open'), 'high': g(c, 'high'), 'low': g(c, 'low'), 'close': g(c, 'close'), 'tick_volume': g(c, 'tick_volume', 'tickVolume'), 'spread': g(c, 'spread'), 'real_volume': g(c, 'real_volume', 'realVolume')}

def _tick_row(t):

    def g(o, name, alt=None):
        if hasattr(o, name):
            return getattr(o, name)
        if alt and hasattr(o, alt):
            return getattr(o, alt)
        if isinstance(o, dict):
            return o.get(name, o.get(alt))
        return None
    return {'time': _safe_ts(g(t, 'time')), 'bid': g(t, 'bid'), 'ask': g(t, 'ask'), 'last': g(t, 'last'), 'volume': g(t, 'volume'), 'flags': g(t, 'flags')}

def _ts(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, datetime):
        return int(x.timestamp())
    if hasattr(x, 'seconds'):
        return int(x.seconds)
    return None

def _row_ohlc(c):

    def g(o, *names):
        for n in names:
            if hasattr(o, n):
                return getattr(o, n)
            if isinstance(o, dict) and n in o:
                return o[n]
        return None

    def unbox(v):
        return float(getattr(v, 'value', v)) if v is not None else None
    return {'time': _ts(g(c, 'time')), 'open': unbox(g(c, 'open')), 'high': unbox(g(c, 'high')), 'low': unbox(g(c, 'low')), 'close': unbox(g(c, 'close')), 'tick_volume': g(c, 'tick_volume', 'tickVolume'), 'spread': g(c, 'spread'), 'real_volume': g(c, 'real_volume', 'realVolume')}

def _row_tick(t):

    def g(o, *names):
        for n in names:
            if hasattr(o, n):
                return getattr(o, n)
            if isinstance(o, dict) and n in o:
                return o[n]
        return None

    def unbox(v):
        return float(getattr(v, 'value', v)) if v is not None else None
    return {'time': _ts(g(t, 'time')), 'bid': unbox(g(t, 'bid')), 'ask': unbox(g(t, 'ask')), 'last': unbox(g(t, 'last')), 'volume': g(t, 'volume'), 'flags': g(t, 'flags')}

def _ts_int(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, datetime):
        return int(x.replace(tzinfo=timezone.utc).timestamp())
    if hasattr(x, 'seconds'):
        
        return int(getattr(x, 'seconds'))
    return None

def _tf_minutes(tf: str | int) -> int:
    if isinstance(tf, int):
        return tf
    tf = str(tf).upper().strip()
    table = {
        'M1':1,'M2':2,'M3':3,'M4':4,'M5':5,'M6':6,'M10':10,'M12':12,'M15':15,'M20':20,'M30':30,
        'H1':60,'H2':120,'H3':180,'H4':240,'H6':360,'H8':480,'H12':720,'D1':1440,'W1':10080,'MN1':43200
    }
    return table.get(tf, 60)

# --- 8) Other ---
async def is_symbol_visible(self, symbol: str) -> bool:
        """Best-effort check: true if symbol is visible/known (explicit methods or tick fetch)."""
        if not self.acc:
            raise RuntimeError('Not connected')
        for name in ('symbol_exist', 'symbol_visible', 'is_symbol_visible'):
            fn = getattr(self.acc, name, None)
            if callable(fn):
                try:
                    res = await fn(symbol)
                    return bool(getattr(res, 'exists', getattr(res, 'visible', res)))
                except Exception:
                    break
        try:
            tick = await self.acc.symbol_info_tick(symbol=symbol)
            return tick is not None
        except Exception:
            return False

async def all_symbols(self) -> List[str]:
        """Try to return full list of symbol names, if backend exposes it."""
        if not self.acc:
            raise RuntimeError('Not connected')
        for name in ('symbols_all_names', 'symbols_names', 'symbols', 'all_symbols', 'symbols_get_all'):
            fn = getattr(self.acc, name, None)
            if callable(fn):
                res = await fn()
                if isinstance(res, (list, tuple)):
                    return [str(x) for x in res]
                for fld in ('items', 'names', 'symbols'):
                    v = getattr(res, fld, None)
                    if isinstance(v, (list, tuple)):
                        return [str(x) for x in v]
        return []

async def on_symbol_tick(self, symbols: Iterable[str]) -> AsyncIterator[Any]:
        """Yield ticks using backend stream if available."""
        if not self.acc:
            raise RuntimeError('Not connected')
        h = getattr(self.acc, 'on_symbol_tick', None)
        if not h:
            raise NotImplementedError('on_symbol_tick not available in this package version')
        async for tick in h(list(symbols)):
            yield tick

# --- Module trailing content (kept as-is) ---




from datetime import datetime, timezone


_TF_CODE = {
    'M1': 1, 'M2': 2, 'M3': 3, 'M4': 4, 'M5': 5, 'M6': 6, 'M10': 10, 'M12': 12, 'M15': 15, 'M20': 20, 'M30': 30,
    'H1': 16385, 'H2': 16386, 'H3': 16387, 'H4': 16388, 'H6': 16390, 'H8': 16392, 'H12': 16396,
    'D1': 16408, 'W1': 32769, 'MN1': 49153,
}






  
























































































from datetime import datetime, timezone





















MT5Service._extract_ticket_list = staticmethod(_extract_ticket_list)
MT5Service._uniq_ints = staticmethod(_uniq_ints)
MT5Service._find_any_by_ticket = staticmethod(lambda data, t: next((x for x in MT5Service._iter_history_items(data) if MT5Service._match_ticket(x, t)), None))
try:
    _BIND_NAMES = ['symbols_total', 'symbol_info_session_trade', 'symbol_info_session_quote', 'tick_value_with_size', 'market_book_get', 'server_time', 'opened_orders', 'opened_orders_tickets', 'positions_total']
    for _name in _BIND_NAMES:
        _fn = globals().get(_name)
        if _fn:
            setattr(MT5Service, _name, _fn)
except Exception as _e:
    pass


















from datetime import datetime
import math


















if __name__ == '__main__':
    import asyncio
    import os
    import getpass
    import traceback
    from dotenv import load_dotenv
    from app.core.config import MT5Config
    load_dotenv()
    DEFAULT_LOGIN = int(os.getenv('MT5_LOGIN', '5036292718'))
    DEFAULT_SERVER = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')
    ENV_PASSWORD = os.getenv('MT5_PASSWORD', '')

    def prompt_int(prompt: str, default: int | None=None) -> int:
        while True:
            s = input(f'{prompt} [{default}]: ').strip()
            if not s and default is not None:
                return default
            try:
                return int(s)
            except ValueError:
                print('Please enter a valid integer.')
    print('>> __main__ starting', flush=True)
    login = prompt_int('MT5 login', DEFAULT_LOGIN)
    if ENV_PASSWORD:
        password = ENV_PASSWORD
        print('>> using password from .env', flush=True)
    else:
        password = getpass.getpass('MT5 password: ').strip()
    server_name = input(f'MT5 server_name [{DEFAULT_SERVER}]: ').strip() or DEFAULT_SERVER
    print(f'>> creds collected (login={login}, server={server_name})', flush=True)
    svc = MT5Service(MT5Config(user=login, password=password, server_name=server_name, timeout_seconds=90))
    print('>> grpc_server:', svc.cfg.grpc_server, 'timeout_seconds:', svc.cfg.timeout_seconds, flush=True)
    print('>> MT5Service constructed', flush=True)
