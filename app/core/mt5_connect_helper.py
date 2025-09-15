
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/compat/mt5_connect_helper.py — resilient MT5 gRPC connection helper ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose:                                                                     ║
║   Make a best-effort connection to an MT5 terminal over gRPC across many     ║
║   different pb2 builds/layouts. Handles GUID/headers, multiple connect paths,║
║   stub discovery, optional low-level login, and graceful disconnect.         ║
║                                                                              ║
║ What it does (happy path):                                                   ║
║   1) Build MT5Account(**kwargs) from cfg, derive host/port from grpc_server. ║
║   2) Ensure terminal GUID + default headers are present immediately.         ║
║   3) Try several connect variants (reconnect/connect/… + by server/host:port)║
║   4) Optionally run ConnectEx/Connect requests (manual handshake).           ║
║   5) Detect LITE mode (session/terminal pb2 missing) and adapt.              ║
║   6) Discover a gRPC channel, attach all known stubs from that channel.      ║
║   7) Fallback discover an “account-like” stub, attempt low-level Login.      ║
║   8) Post-login factories, then wait-ready with soft ping logic.             ║
║                                                                              ║
║ Public API:                                                                  ║
║   - connect_via_helper(svc) -> bool                                          ║
║   - disconnect_via_helper(svc) -> bool                                       ║
║   - ensure_connected(svc) -> bool                                            ║
║                                                                              ║                                                                   
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import asyncio
import inspect
import pkgutil
from typing import TYPE_CHECKING, Optional, Tuple, Iterable

# IMPORTANT: keep these imports at the very top (expected by some builds)
from MetaRpcMT5.mt5_account import MT5Account  # type: ignore
from MetaRpcMT5 import ConnectExceptionMT5     # type: ignore

if TYPE_CHECKING:
    from app.core.mt5_service import MT5Service


async def connect_via_helper(svc: "MT5Service") -> bool:
    """
    Universal connect routine:
    MT5Account → connect (server_name / host:port / ConnectEx / Connect)
    → build stubs from channel → (opt) low-level Login → post-factories → final ping.
    """
    # Optional pb2 alias patch (no-op if not present)
    try:
        from app.patches.patch_mt5_pb2_aliases import apply_patch
        apply_patch()
    except Exception:
        pass

    # local, consistent logging wrapper
    def _log(msg: str) -> None:
        try:
            lg = svc.__dict__.get("logger", None)
            lg.debug(msg) if lg else print(msg)
        except Exception:
            print(msg)

    cfg = svc.cfg
    _log(
        f"[connect] cfg: user={'***' if getattr(cfg,'user',None) else None} "
        f"server_name={getattr(cfg,'server_name',None)!r} "
        f"grpc_server={getattr(cfg,'grpc_server',None)!r} "
        f"host={getattr(cfg,'host',None)!r} port={getattr(cfg,'port',None)!r}"
    )

    # 0) Build MT5Account kwargs that match real __init__ signature
    try:
        sig = inspect.signature(MT5Account.__init__)
        params_map = sig.parameters
        params = set(params_map.keys())
        supports_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params_map.values())
    except Exception:
        params, supports_kwargs = set(), True

    def _set(dst: dict, k: str, v):
        if v is None:
            return
        if supports_kwargs or (not params) or (k in params):
            dst[k] = v

    kwargs: dict = {}
    _set(kwargs, "user", getattr(cfg, "user", None))
    _set(kwargs, "password", getattr(cfg, "password", None))
    _set(kwargs, "grpc_server", getattr(cfg, "grpc_server", None))
    server_pref = getattr(cfg, "server_name", getattr(cfg, "server", None))
    if "server_name" in params or supports_kwargs:
        _set(kwargs, "server_name", server_pref)
    elif "server" in params:
        _set(kwargs, "server", server_pref)
    tmo = getattr(cfg, "timeout_seconds", None)
    if "timeout_seconds" in params or supports_kwargs:
        _set(kwargs, "timeout_seconds", tmo)
    elif "timeout" in params:
        _set(kwargs, "timeout", tmo)
    _set(kwargs, "base_chart_symbol", getattr(cfg, "base_chart_symbol", None))

    # Derive host/port from grpc_server if host is missing
    host = getattr(cfg, "host", None)
    port = getattr(cfg, "port", None)
    if not host:
        gs = getattr(cfg, "grpc_server", None)
        if isinstance(gs, str) and ":" in gs:
            host_part, pstr = gs.rsplit(":", 1)
            host = host_part
            try:
                port = int(pstr)
            except Exception:
                port = 443

    # 1) Create account holder (attach early so factories can see it)
    acc = MT5Account(**kwargs)
    svc.acc = acc

    # Ensure terminal GUID + default headers are present immediately
    import uuid as _uuid
    guid = (
        getattr(acc, "terminal_instance_guid", None)
        or getattr(acc, "terminalInstanceGuid", None)
        or getattr(acc, "id", None)
        or getattr(acc, "Id", None)
    )
    if not guid:
        guid = str(_uuid.uuid4())
    for attr_name in ("terminal_instance_guid", "terminalInstanceGuid", "id", "Id"):
        try:
            setattr(acc, attr_name, guid)
        except Exception:
            pass

    user = getattr(cfg, "user", None)
    pwd  = getattr(cfg, "password", None)

    try:
        headers = acc.get_headers()  # type: ignore[attr-defined]
    except Exception:
        headers = []

    if not headers:
        # fallback header provider if account object has none
        def _fallback_headers():
            base = [
                ("terminalInstanceGuid", guid),
                ("id", guid),
                ("client-id", guid),
            ]
            if user is not None:
                base.append(("user", str(user)))
            if server_pref is not None:
                base.append(("server", str(server_pref)))
            return base
        try:
            setattr(acc, "get_headers", _fallback_headers)  # type: ignore[attr-defined]
            headers = acc.get_headers()  # type: ignore[attr-defined]
        except Exception:
            headers = _fallback_headers()
    # cache headers for builds that read `_headers` directly
    try:
        setattr(acc, "_headers", headers)
    except Exception:
        pass

    # 2) Primary connect attempts (before any pings)
    for name in ("reconnect", "connect", "connect_async", "start", "initialize", "open"):
        fn = getattr(acc, name, None)
        if not callable(fn):
            continue
        try:
            _log(f"[connect] try acc.{name}()")
            r = fn()
            if inspect.iscoroutine(r):
                await r
            break
        except Exception as e:
            _log(f"[connect] {name} failed: {e!r}")

    # Explicit bridges: by server_name and by host:port
    try:
        if getattr(cfg, "server_name", None) and hasattr(acc, "connect_by_server_name"):
            _log(f"[connect] connect_by_server_name({cfg.server_name!r})")
            try:
                await acc.connect_by_server_name(
                    server_name=cfg.server_name,
                    base_chart_symbol=getattr(cfg, "base_chart_symbol", "EURUSD"),
                    wait_for_terminal_is_alive=False,
                    timeout_seconds=int(getattr(cfg, "timeout_seconds", 90)),
                )
            except Exception as e:
                _log(f"[connect] connect_by_server_name failed: {e!r}")

        if host and hasattr(acc, "connect_by_host_port"):
            _log(f"[connect] connect_by_host_port({host!r}, {int(port or 443)})")
            try:
                await acc.connect_by_host_port(
                    host=host,
                    port=int(port or 443),
                    base_chart_symbol=getattr(cfg, "base_chart_symbol", "EURUSD"),
                    wait_for_terminal_is_alive=False,
                    timeout_seconds=int(getattr(cfg, "timeout_seconds", 90)),
                )
            except Exception as e:
                _log(f"[connect] connect_by_host_port failed: {e!r}")
    except Exception as e:
        _log(f"[connect] explicit connect fallback wrapper: {e!r}")

    # Manual ConnectEx / Connect handshakes if available
    try:
        conn_client = (
            getattr(acc, "connection_client", None)
            or getattr(acc, "connect_client", None)
            or getattr(acc, "connection_stub", None)
        )
        try:
            from MetaRpcMT5 import mt5_term_api_connection_pb2 as conn_pb2  # type: ignore
        except Exception:
            conn_pb2 = None

        if conn_client and conn_pb2:
            # ConnectEx
            if hasattr(conn_pb2, "ConnectExRequest") and hasattr(conn_client, "ConnectEx"):
                try:
                    req = conn_pb2.ConnectExRequest()
                    if hasattr(req, "terminalInstanceGuid"):
                        setattr(req, "terminalInstanceGuid", guid)
                    elif hasattr(req, "id"):
                        setattr(req, "id", guid)
                    if hasattr(req, "server_name") and server_pref:
                        req.server_name = server_pref
                    if hasattr(req, "host") and host:
                        req.host = host
                    if hasattr(req, "port"):
                        req.port = int(port or 443)

                    resp = conn_client.ConnectEx(
                        req, metadata=headers, timeout=float(getattr(cfg, "timeout_seconds", 90))
                    )
                    if hasattr(resp, "__await__"):
                        await resp
                    _log("[connect] ConnectExRequest ok")
                except Exception as e:
                    _log(f"[connect] ConnectExRequest failed: {e!r}")

            # Connect
            if hasattr(conn_pb2, "ConnectRequest") and hasattr(conn_client, "Connect"):
                try:
                    req2 = conn_pb2.ConnectRequest()
                    if hasattr(req2, "host") and host:
                        req2.host = host
                    if hasattr(req2, "port"):
                        req2.port = int(port or 443)
                    resp2 = conn_client.Connect(
                        req2, metadata=headers, timeout=float(getattr(cfg, "timeout_seconds", 90))
                    )
                    if hasattr(resp2, "__await__"):
                        await resp2
                    _log("[connect] ConnectRequest ok")
                except Exception as e:
                    _log(f"[connect] ConnectRequest failed: {e!r}")

        # LITE mode detection: if session/terminal pb2 missing — skip those handshakes
        try:
            import MetaRpcMT5.mt5_term_api_session_pb2 as _s  # type: ignore
            import MetaRpcMT5.mt5_term_api_terminal_pb2 as _t  # type: ignore
            acc._lite_mode = False  # type: ignore[attr-defined]
        except Exception:
            acc._lite_mode = True   # type: ignore[attr-defined]
            _log("[connect] LITE mode: skip session/terminal handshake (pb2 missing)")
            if not hasattr(acc, "get_headers") or acc.get_headers is None:
                acc.get_headers = lambda: getattr(acc, "_headers", [])  # type: ignore[attr-defined]

        # Session/Terminal handshake if NOT LITE
        if not getattr(acc, "_lite_mode", False):
            await _try_session_or_terminal_handshake(acc, headers, server_pref, user, pwd, guid, _log)
        else:
            _log("[connect] session/terminal handshake skipped (LITE)")
            # In LITE: try a gentle AccountHelper.Ping to wake things up
            try:
                ch = None
                for ch_, _ in _iter_possible_channels(acc):
                    ch = ch_ or ch
                    if ch:
                        break
                if ch:
                    from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2  # type: ignore
                    from MetaRpcMT5 import mt5_term_api_account_helper_pb2_grpc as ah_grpc  # type: ignore
                    stub = getattr(acc, "account_helper_client", None) or ah_grpc.AccountHelperServiceStub(ch)
                    resp = stub.Ping(ah_pb2.PingRequest(), metadata=headers or [], timeout=5.0)
                    if hasattr(resp, "__await__"):
                        await resp
                    _log("[connect] AccountHelper.Ping OK (LITE)")
                else:
                    _log("[connect] no channel for AccountHelper.Ping (LITE)")
            except Exception as e:
                _log(f"[connect] AccountHelper.Ping failed (LITE): {e!r}")

        # Nudge internal connected state after handshakes
        for nm in ("reconnect", "connect", "start", "initialize", "open"):
            fn = getattr(acc, nm, None)
            if not callable(fn):
                continue
            try:
                _log(f"[connect] post-handshake acc.{nm}()")
                r = fn()
                if inspect.iscoroutine(r):
                    await r
                break
            except Exception as e:
                _log(f"[connect] post-handshake {nm} failed: {e!r}")

        try:
            await asyncio.sleep(0.5)  # give terminal a moment to settle
        except Exception:
            pass

    except Exception as e:
        _log(f"[connect] direct Connect wrapper failed: {e!r}")

    # 3) Build stubs from any discovered channel
    try:
        found = None
        for ch, origin in _iter_possible_channels(acc):
            if ch is not None:
                _build_all_clients_from_channel(acc, ch, _log)
                found = origin
                _log(f"[connect] stubs built from channel @ {origin}")
                break

        if found is None:
            _log("[connect] no channel attribute found yet → Let's try factories")
            for factory in ("ensure_clients", "connect_clients", "connect_all_clients"):
                fn = getattr(acc, factory, None)
                if callable(fn):
                    try:
                        _log(f"[connect] calling factory {factory}()")
                        r = fn()
                        if inspect.iscoroutine(r):
                            await r
                    except Exception as e:
                        _log(f"[connect] factory {factory} failed: {e!r}")

            for ch, origin in _iter_possible_channels(acc):
                if ch is not None:
                    _build_all_clients_from_channel(acc, ch, _log)
                    _log(f"[connect] stubs built from channel @ {origin} (retry)")
                    break
    except Exception as e:
        _log(f"[connect] build stubs from channel failed: {e!r}")

    # If no account_client, try to auto-attach “account-like” stub
    if getattr(acc, "account_client", None) is None:
        try:
            attached = _find_and_attach_account_like_client(acc, _log)
            if attached:
                _log(f"[connect] attached account-like client: {attached}")
        except Exception as e:
            _log(f"[connect] dynamic account-like client discovery failed: {e!r}")

    # 4) Optional low-level Login on any suitable stub
    try:
        ok = await _try_low_level_login(acc, user, pwd, server_pref, _log)
        if ok:
            _log("[connect] low-level login: OK")
        else:
            _log("[connect] skip low-level Login (no suitable client/method)")
    except Exception as e:
        _log(f"[connect] low-level Login block failed: {e!r}")

    # 5) Post-login factories
    for factory in ("ensure_clients", "connect_clients", "connect_all_clients"):
        fn = getattr(acc, factory, None)
        if callable(fn):
            try:
                _log(f"[connect] post-login factory {factory}()")
                r = fn()
                if hasattr(r, "__await__"):
                    await r
            except Exception as e:
                _log(f"[connect] post-login factory {factory} failed: {e!r}")

    # 6) Final wait-ready loop (soft in LITE mode)
    await _post_connect_wait_ready(svc, tries=12, delay=0.5)
    return True


async def disconnect_via_helper(svc: "MT5Service") -> bool:
    """
    Graceful disconnect: unsubscribe/Logout/close all stubs/channels and clear svc.acc.
    """
    def _log(msg: str):
        try:
            logger = svc.__dict__.get("logger", None)
            logger.debug(msg) if logger else print(msg)
        except Exception:
            pass

    acc = getattr(svc, "acc", None)
    if acc is None:
        return True

    # Try to stop any streams/subscriptions
    for nm in ("unsubscribe_all", "stop_streams", "close_streams"):
        fn = getattr(acc, nm, None)
        if callable(fn):
            try:
                _log(f"[disconnect] {nm}()")
                r = fn()
                if inspect.iscoroutine(r):
                    await r
            except Exception:
                pass

    # Optional Logout via account_client (if present)
    try:
        acc_client = getattr(acc, "account_client", None)
        if acc_client is not None and hasattr(acc_client, "Logout"):
            try:
                from MetaRpcMT5 import mt5_term_api_account_pb2 as acc_pb2  # type: ignore
            except Exception:
                acc_pb2 = None
            if acc_pb2 is not None:
                try:
                    _log("[disconnect] account_client.Logout()")
                    req = acc_pb2.LogoutRequest()
                    resp = acc_client.Logout(req, timeout=3.0)
                    if inspect.iscoroutine(resp):
                        await resp
                except Exception:
                    pass
    except Exception:
        pass

    # Common close/dispose methods
    for nm in ("logout", "close", "disconnect", "stop", "shutdown", "dispose", "release"):
        fn = getattr(acc, nm, None)
        if callable(fn):
            try:
                _log(f"[disconnect] {nm}()")
                r = fn()
                if inspect.iscoroutine(r):
                    await r
            except Exception:
                pass

    # Close gRPC channel if available
    for ch_name in ("channel", "_channel", "grpc_channel", "mt5_channel"):
        ch = getattr(acc, ch_name, None)
        if ch is None:
            continue
        try:
            close = getattr(ch, "close", None)
            if callable(close):
                _log(f"[disconnect] {ch_name}.close()")
                res = close()
                if inspect.iscoroutine(res):
                    await res
        except Exception:
            pass

    svc.acc = None
    _log("[disconnect] done")
    return True


async def ensure_connected(svc: "MT5Service") -> bool:
    """
    Ensure the service is connected; reconnect if the local ping fails.
    """
    acc = getattr(svc, "acc", None)
    if acc is None:
        return await connect_via_helper(svc)

    # Local “ping”: try several cheap calls; success if any completes
    async def _ping() -> bool:
        for nm in ("server_time", "symbols_total", "symbols_total_noarg", "account_summary"):
            try:
                if nm == "server_time":
                    f = getattr(acc, "server_time", None)
                    if callable(f):
                        r = f()
                        if inspect.iscoroutine(r):
                            await r
                        return True
                elif nm == "symbols_total":
                    f = getattr(acc, "symbols_total", None)
                    if callable(f):
                        r = f(False)  # builds that require selected_only param
                        if inspect.iscoroutine(r):
                            await r
                        return True
                elif nm == "symbols_total_noarg":
                    f = getattr(acc, "symbols_total", None)
                    if callable(f):
                        try:
                            r = f()  # builds with no params
                            if inspect.iscoroutine(r):
                                await r
                            return True
                        except TypeError:
                            pass
                else:  # account_summary
                    f = getattr(acc, "account_summary", None)
                    if callable(f):
                        r = f()
                        if inspect.iscoroutine(r):
                            await r
                        return True
            except Exception:
                continue
        return False

    if await _ping():
        return True

    await disconnect_via_helper(svc)
    return await connect_via_helper(svc)


async def _try_post_connect_ping(svc) -> bool:
    """
    Soft readiness check on acc; if any of these succeed, we consider the terminal alive.
    """
    acc = getattr(svc, "acc", None)
    if acc is None:
        return False

    base_sym = getattr(getattr(svc, "cfg", None), "base_chart_symbol", "EURUSD")

    attempts = [
        ("server_time", ()),                     # safest on most builds
        ("symbols_total", (False,)),             # builds requiring `selected_only`
        ("opened_orders_tickets", ()),           # light RPC if present
        ("symbol_info_tick", ({"symbol": base_sym},)),  # kwargs variant
    ]

    for fn_name, args in attempts:
        fn = getattr(acc, fn_name, None)
        if not callable(fn):
            continue
        try:
            if args and isinstance(args[0], dict):
                res = fn(**args[0])
            else:
                res = fn(*args)
            if inspect.iscoroutine(res):
                await res
            return True
        except TypeError:
            continue
        except Exception as e:
            print(f"[connect] ping {fn_name}{args} failed:", e)
    return False


async def _post_connect_wait_ready(svc, *, tries: int = 12, delay: float = 0.5) -> None:
    """
    Wait for terminal readiness after ConnectRequest.
    In LITE mode the logic is softer: if key stubs are attached, we proceed.
    """
    acc = getattr(svc, "acc", None)
    lite = bool(getattr(acc, "_lite_mode", False)) if acc else False

    for i in range(tries):
        if await _try_post_connect_ping(svc):
            print("[connect] success")
            return
        await asyncio.sleep(delay)

        if lite and i >= max(1, tries // 2):
            if any(getattr(acc, nm, None) for nm in (
                "account_helper_client", "market_info_client", "symbols_client", "account_client"
            )):
                print("[connect] success (LITE mode — stubs attached, skipping final ping)")
                return

    if lite:
        print("[connect] final ping failed (LITE) — continue without hard fail")
        return

    print("[connect] final ping failed → raising ConnectExceptionMT5")
    raise ConnectExceptionMT5("Please call connect method first")


# === deep getattr & channel discovery =========================================

def _deep_getattr(obj, path: str):
    """Safe getattr by dotted path (e.g. '_transport._channel')."""
    cur = obj
    for part in path.split("."):
        if cur is None:
            return None
        try:
            cur = getattr(cur, part)
        except Exception:
            return None
    return cur


def _iter_possible_channels(acc):
    """
    Yield all likely places where a gRPC channel might be stored.
    Returns generator of (channel, origin_label).
    """
    # 1) direct attributes
    direct_names = [
        "channel", "_channel", "grpc_channel", "mt5_channel",
        "aio_channel", "channel_aio", "grpc_aio_channel", "_grpc_aio_channel",
        "conn_channel", "connection_channel",
    ]
    for nm in direct_names:
        ch = getattr(acc, nm, None)
        if ch:
            yield ch, nm

    # 2) methods returning a channel
    method_names = ["get_channel", "channel", "grpc_channel", "get_grpc_channel"]
    for m in method_names:
        fn = getattr(acc, m, None)
        if callable(fn):
            try:
                ch = fn()
                if ch:
                    yield ch, f"{m}()"
            except Exception:
                pass

    # 3) nested `clients` object
    clients_obj = getattr(acc, "clients", None)
    if clients_obj is not None:
        for nm in ("channel", "grpc_channel", "_channel", "_grpc_aio_channel"):
            ch = getattr(clients_obj, nm, None)
            if ch:
                yield ch, f"clients.{nm}"

    # 4) extract channel from known client stubs
    client_names = [
        "account_client", "market_info_client", "symbols_client",
        "charts_client", "book_client", "account_helper_client",
    ]
    nested_paths = [
        "_channel", "channel", "_transport._channel", "_stub._channel",
    ]
    for cname in client_names:
        cl = getattr(acc, cname, None)
        if cl is None:
            continue
        for path in nested_paths:
            ch = _deep_getattr(cl, path)
            if ch:
                yield ch, f"{cname}.{path}"


def _build_all_clients_from_channel(acc, channel, log):
    """
    Given a channel, attach all known stubs to `acc` if missing.
    Silently skip those not present in current build.
    """
    # Account
    if getattr(acc, "account_client", None) is None:
        try:
            from MetaRpcMT5 import mt5_term_api_account_pb2_grpc as acc_grpc  # type: ignore
            acc.account_client = acc_grpc.AccountServiceStub(channel)
            log("[connect] account_client stub attached")
        except Exception:
            pass

    # AccountHelper (various stub names across builds)
    if getattr(acc, "account_helper_client", None) is None:
        try:
            from MetaRpcMT5 import mt5_term_api_account_helper_pb2_grpc as ah_grpc  # type: ignore
            stub_cls = (
                getattr(ah_grpc, "AccountHelperServiceStub", None) or
                getattr(ah_grpc, "AccountHelperStub", None) or
                getattr(ah_grpc, "AccountHelperClientStub", None)
            )
            if stub_cls:
                acc.account_helper_client = stub_cls(channel)
                log("[connect] account_helper_client stub attached")
        except Exception:
            pass

    # MarketInfo
    if getattr(acc, "market_info_client", None) is None:
        try:
            from MetaRpcMT5 import mt5_term_api_market_info_pb2_grpc as mi_grpc  # type: ignore
            stub_cls = getattr(mi_grpc, "MarketInfoServiceStub", None) or getattr(mi_grpc, "MarketSymbolsServiceStub", None)
            if stub_cls:
                acc.market_info_client = stub_cls(channel)
                log("[connect] market_info_client stub attached")
        except Exception:
            pass

    # Symbols
    if getattr(acc, "symbols_client", None) is None:
        try:
            from MetaRpcMT5 import mt5_term_api_symbols_pb2_grpc as sym_grpc  # type: ignore
            stub_cls = getattr(sym_grpc, "SymbolsServiceStub", None)
            if stub_cls:
                acc.symbols_client = stub_cls(channel)
                log("[connect] symbols_client stub attached")
        except Exception:
            pass

    # Charts
    if getattr(acc, "charts_client", None) is None:
        try:
            from MetaRpcMT5 import mt5_term_api_charts_pb2_grpc as ch_grpc  # type: ignore
            stub_cls = getattr(ch_grpc, "ChartsServiceStub", None)
            if stub_cls:
                acc.charts_client = stub_cls(channel)
                log("[connect] charts_client stub attached")
        except Exception:
            pass

    # Book / DOM (service name differs across builds)
    if getattr(acc, "book_client", None) is None:
        for modname in ("mt5_term_api_book_pb2_grpc", "mt5_term_api_market_book_pb2_grpc"):
            try:
                mod = __import__(f"MetaRpcMT5.{modname}", fromlist=["*"])  # type: ignore
                stub_cls = (
                    getattr(mod, "BookServiceStub", None)
                    or getattr(mod, "MarketBookServiceStub", None)
                )
                if stub_cls:
                    acc.book_client = stub_cls(channel)
                    log("[connect] book_client stub attached")
                    break
            except Exception:
                pass

    # TradeFunctions
    if getattr(acc, "trade_functions_client", None) is None:
        try:
            from MetaRpcMT5 import mt5_term_api_trade_functions_pb2_grpc as tf_grpc  # type: ignore
            stub_cls = (
                getattr(tf_grpc, "TradeFunctionsServiceStub", None)
                or getattr(tf_grpc, "TradeServiceStub", None)
            )
            if stub_cls:
                acc.trade_functions_client = stub_cls(channel)
                log("[connect] trade_functions_client stub attached")
        except Exception:
            pass


# === dynamic account-like client discovery & login ============================

def _iter_meta_rpc_modules() -> Iterable[str]:
    """Yield candidate MetaRpcMT5.*_pb2_grpc module names for stub scanning."""
    base = "MetaRpcMT5"
    try:
        import MetaRpcMT5  # type: ignore
        for m in pkgutil.iter_modules(MetaRpcMT5.__path__):  # type: ignore
            name = m.name
            if name.endswith("_pb2_grpc"):
                yield f"{base}.{name}"
    except Exception:
        # fallback list of known names
        for name in (
            "MetaRpcMT5.mt5_term_api_account_pb2_grpc",
            "MetaRpcMT5.mt5_term_api_auth_pb2_grpc",
            "MetaRpcMT5.mt5_term_api_session_pb2_grpc",
            "MetaRpcMT5.mt5_term_api_terminal_pb2_grpc",
            "MetaRpcMT5.mt5_term_api_connection_pb2_grpc",
        ):
            yield name


def _find_and_attach_account_like_client(acc, log) -> Optional[str]:
    """
    Scan *_pb2_grpc modules and attach any stub that exposes a login-like method
    as acc.account_client. Returns a descriptor string if something was attached.
    """
    login_methods = ("Login", "AccountLogin", "UserLogin", "OpenSession", "SessionOpen", "TerminalLogin")

    channel = None
    for ch, _origin in _iter_possible_channels(acc):
        channel = ch
        if channel:
            break
    if channel is None:
        return None

    for modname in _iter_meta_rpc_modules():
        try:
            mod = __import__(modname, fromlist=["*"])
        except Exception:
            continue

        for attr in dir(mod):
            if not attr.endswith("Stub"):
                continue
            Stub = getattr(mod, attr, None)
            if Stub is None:
                continue
            try:
                stub = Stub(channel)
            except Exception:
                continue

            for meth in login_methods:
                if hasattr(stub, meth) and callable(getattr(stub, meth)):
                    acc.account_client = stub
                    return f"{modname}.{attr}::{meth}"

    return None


async def _try_low_level_login(acc, user, pwd, server_pref, log) -> bool:
    """
    Attempt a low-level login on any discovered “account-like” client.
    Tries multiple request classes and field layouts.
    """
    candidates: list[Tuple[object, str]] = []
    acc_client = getattr(acc, "account_client", None)
    if acc_client is not None:
        candidates.append((acc_client, "account_client"))

    for nm in ("account_helper_client", "auth_client", "session_client", "terminal_client"):
        c = getattr(acc, nm, None)
        if c is not None:
            candidates.append((c, nm))

    if not candidates:
        return False

    req_modules = (
        "MetaRpcMT5.mt5_term_api_account_pb2",
        "MetaRpcMT5.mt5_term_api_auth_pb2",
        "MetaRpcMT5.mt5_term_api_session_pb2",
        "MetaRpcMT5.mt5_term_api_terminal_pb2",
    )
    req_names = (
        "LoginRequest",
        "AccountLoginRequest",
        "UserLoginRequest",
        "OpenSessionRequest",
        "SessionOpenRequest",
        "TerminalLoginRequest",
    )
    method_names = ("Login", "AccountLogin", "UserLogin", "OpenSession", "SessionOpen", "TerminalLogin")

    headers = []
    if hasattr(acc, "get_headers"):
        try:
            headers = acc.get_headers()
        except Exception:
            headers = []

    for stub, stub_label in candidates:
        callables = [mn for mn in method_names if hasattr(stub, mn) and callable(getattr(stub, mn))]
        if not callables:
            continue

        req_cls = None
        for modname in req_modules:
            try:
                req_mod = __import__(modname, fromlist=["*"])
            except Exception:
                continue
            for rn in req_names:
                cls = getattr(req_mod, rn, None)
                if cls is not None:
                    req_cls = cls
                    break
            if req_cls:
                break

        if req_cls is None:
            class _Empty:
                pass
            req_cls = _Empty  # type: ignore

        try:
            req = req_cls()  # type: ignore
        except Exception:
            req = None

        def _set_if_has(obj, name: str, value):
            if obj is None:
                return
            try:
                if hasattr(obj, name):
                    setattr(obj, name, value)
            except Exception:
                pass

        if req is not None:
            for login_field in ("login", "user", "account", "login_id"):
                _set_if_has(req, login_field, user)
            for pass_field in ("password", "pwd", "pass"):
                _set_if_has(req, pass_field, pwd)
            for serv_field in ("server", "server_name"):
                _set_if_has(req, serv_field, server_pref)

        for m in callables:
            try:
                fn = getattr(stub, m)
                if req is None:
                    resp = fn(timeout=5.0, metadata=headers)
                else:
                    resp = fn(req, timeout=5.0, metadata=headers)
                if hasattr(resp, "__await__"):
                    await resp
                log(f"[connect] login via {stub_label}.{m} -> OK")
                return True
            except Exception as e:
                log(f"[connect] {stub_label}.{m} failed: {e!r}")

    return False


async def _try_session_or_terminal_handshake(acc, headers, server_pref, user, pwd, guid, log) -> bool:
    """Perform soft Session/Terminal handshake or a Ping before market RPCs."""
    def _set_if_has(obj, name, value):
        try:
            if hasattr(obj, name) and value is not None:
                setattr(obj, name, value)
        except Exception:
            pass

    # Find any usable channel
    channel = None
    try:
        for ch, _origin in _iter_possible_channels(acc):
            channel = ch
            if channel:
                break
    except Exception:
        channel = None
    if channel is None:
        return False

    # 1) Session.OpenSession / Session.SessionOpen
    try:
        from MetaRpcMT5 import mt5_term_api_session_pb2 as s_pb2        # type: ignore
        from MetaRpcMT5 import mt5_term_api_session_pb2_grpc as s_grpc  # type: ignore
        stub = getattr(acc, "session_client", None) or s_grpc.SessionServiceStub(channel)

        req_cls = getattr(s_pb2, "OpenSessionRequest", None) or getattr(s_pb2, "SessionOpenRequest", None)
        call = getattr(stub, "OpenSession", None) or getattr(stub, "SessionOpen", None)
        if req_cls and callable(call):
            req = req_cls()
            for f in ("terminalInstanceGuid", "id", "guid"):
                _set_if_has(req, f, guid)
            for f in ("server", "server_name"):
                _set_if_has(req, f, server_pref)
            for f in ("login", "user", "account", "login_id"):
                _set_if_has(req, f, user)
            for f in ("password", "pwd", "pass"):
                _set_if_has(req, f, pwd)

            resp = call(req, metadata=headers or [], timeout=10.0)
            if hasattr(resp, "__await__"):
                await resp
            log("[connect] Session.OpenSession OK")
            return True
    except Exception as e:
        log(f"[connect] session handshake failed: {e!r}")

    # 2) Terminal.TerminalLogin / Terminal.IsAlive
    try:
        from MetaRpcMT5 import mt5_term_api_terminal_pb2 as t_pb2        # type: ignore
        from MetaRpcMT5 import mt5_term_api_terminal_pb2_grpc as t_grpc  # type: ignore
        stub = getattr(acc, "terminal_client", None) or t_grpc.TerminalServiceStub(channel)

        login_cls = getattr(t_pb2, "TerminalLoginRequest", None)
        login_fn  = getattr(stub, "TerminalLogin", None)
        if login_cls and callable(login_fn):
            req = login_cls()
            for f in ("terminalInstanceGuid", "id", "guid"):
                _set_if_has(req, f, guid)
            for f in ("server", "server_name"):
                _set_if_has(req, f, server_pref)
            resp = login_fn(req, metadata=headers or [], timeout=10.0)
            if hasattr(resp, "__await__"):
                await resp
            log("[connect] TerminalLogin OK")
            return True

        # fallback: IsAlive / TerminalIsAlive
        alive_cls = getattr(t_pb2, "IsAliveRequest", None) or getattr(t_pb2, "TerminalIsAliveRequest", None)
        alive_fn  = getattr(stub, "IsAlive", None) or getattr(stub, "TerminalIsAlive", None)
        if alive_cls and callable(alive_fn):
            req = alive_cls()
            for f in ("terminalInstanceGuid", "id", "guid"):
                _set_if_has(req, f, guid)
            resp = alive_fn(req, metadata=headers or [], timeout=5.0)
            if hasattr(resp, "__await__"):
                await resp
            log("[connect] Terminal.IsAlive OK")
            return True
    except Exception as e:
        log(f"[connect] terminal handshake failed: {e!r}")

    # 3) AccountHelper.Ping as the lightest keepalive
    try:
        from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2        # type: ignore
        from MetaRpcMT5 import mt5_term_api_account_helper_pb2_grpc as ah_grpc  # type: ignore
        stub = getattr(acc, "account_helper_client", None) or ah_grpc.AccountHelperServiceStub(channel)

        if hasattr(ah_pb2, "PingRequest") and hasattr(stub, "Ping"):
            resp = stub.Ping(ah_pb2.PingRequest(), metadata=headers or [], timeout=5.0)
            if hasattr(resp, "__await__"):
                await resp
            log("[connect] AccountHelper.Ping OK")
            return True
    except Exception as e:
        log(f"[connect] account_helper ping failed: {e!r}")

    return False
