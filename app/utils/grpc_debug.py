"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE app/grpc_debug.py — gRPC aio debug interceptor and attach helpers       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose: Log outgoing gRPC calls (aio) with safe redaction and optional file ║
║          dump; supports all 4 RPC kinds; easy attach to existing channels.   ║
║ Key:     AioDebugInterceptor; attach_grpc_debug_interceptor(); channel utils ║
║ Notes:   Redacts keys: password/pwd/pass/authorization; truncates long text. ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import asyncio
import datetime as dt
import functools
import inspect
import io
import sys
from typing import Any, Iterable, Optional, Sequence, Tuple

import grpc

# ————————————————————————————————————————————————————————————————
# Helpers
# ————————————————————————————————————————————————————————————————
def _now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def _safe_open_append(path: Optional[str]):
    if not path:
        return None
    try:
        return open(path, "a", encoding="utf-8", buffering=1)
    except Exception:
        return None

def _short(s: str, limit: int = 2000) -> str:
    if len(s) <= limit:
        return s
    return s[:limit] + f"... ({len(s)-limit} more)"

def _msg_to_dict(msg: Any) -> Any:
    # Pretty-print protobuf via json_format; fallback to str(msg)
    try:
        from google.protobuf.json_format import MessageToDict  # type: ignore
        return MessageToDict(msg, preserving_proto_field_name=True)
    except Exception:
        try:
            return str(msg)
        except Exception:
            return "<unprintable>"

def _redact_obj(obj: Any, redact_keys: Iterable[str]) -> Any:
    keys = {k.lower() for k in redact_keys}
    try:
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if str(k).lower() in keys:
                    out[k] = "***"
                else:
                    out[k] = _redact_obj(v, keys)
            return out
        if isinstance(obj, (list, tuple)):
            return type(obj)(_redact_obj(v, keys) for v in obj)
        # primitives
        return obj
    except Exception:
        return obj

def _redact_metadata(md: Optional[Sequence[Tuple[str, str]]], redact_keys: Iterable[str]):
    if not md:
        return md
    keys = {k.lower() for k in redact_keys}
    out = []
    for k, v in md:
        if k.lower() in keys:
            out.append((k, "***"))
        else:
            out.append((k, v))
    return out

# ————————————————————————————————————————————————————————————————
# AIO Debug Interceptor
# ————————————————————————————————————————————————————————————————
class AioDebugInterceptor(grpc.aio.ClientInterceptor):
    def __init__(
        self,
        *,
        log_to_file: Optional[str] = None,
        also_print: bool = True,
        dump_payload: bool = True,
        max_text: int = 4000,
        redact_keys: Iterable[str] = ("password", "pwd", "pass", "authorization"),
    ) -> None:
        self.dump_payload = dump_payload
        self.max_text = max_text
        self.redact_keys = tuple(redact_keys)
        self._fp = _safe_open_append(log_to_file)
        self._also_print = also_print

    def _log(self, text: str) -> None:
        line = f"[{_now()}] {text}"
        if self._also_print:
            print(line)
        if self._fp:
            try:
                self._fp.write(line + "\n")
            except Exception:
                pass

    # ——— common path
    async def _intercept_common(self, kind: str, continuation, call_details, request_or_iterator):
        method = getattr(call_details, "method", "?")
        deadline = getattr(call_details, "timeout", None) or getattr(call_details, "deadline", None)
        metadata = getattr(call_details, "metadata", None)

        red_md = _redact_metadata(metadata, self.redact_keys)

        self._log(f"→ RPC {kind} {method} | deadline={deadline} | metadata={red_md}")

        # Request dump (safe)
        if self.dump_payload:
            try:
                if inspect.isasyncgen(request_or_iterator) or inspect.isgenerator(request_or_iterator):
                    self._log("  request: <stream>")
                else:
                    d = _msg_to_dict(request_or_iterator)
                    d = _redact_obj(d, self.redact_keys)
                    self._log("  request: " + _short(str(d), self.max_text))
            except Exception as e:
                self._log(f"  request: <unprintable> ({e!r})")

        # Call
        try:
            resp = await continuation(call_details, request_or_iterator)
        except grpc.aio.AioRpcError as rpc_err:
            code = rpc_err.code()
            details = rpc_err.details()
            debug = getattr(rpc_err, "debug_error_string", None)
            self._log(f"✖ RPC ERROR {method} | code={code} details={details} debug={debug}")
            raise
        except Exception as e:
            self._log(f"✖ RPC EXC {method}: {e!r}")
            raise

        # Response dump (object for unary, iterator for stream)
        if self.dump_payload:
            try:
                d = _msg_to_dict(resp)
                d = _redact_obj(d, self.redact_keys)
                self._log("  response: " + _short(str(d), self.max_text))
            except TypeError:
                self._log(f"  response: <{type(resp).__name__}>")
            except Exception as e:
                self._log(f"  response: <unprintable> ({e!r})")

        self._log(f"✓ RPC OK {method}")
        return resp

    # ——— intercept interfaces
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        return await self._intercept_common("unary_unary", continuation, client_call_details, request)

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        return await self._intercept_common("unary_stream", continuation, client_call_details, request)

    async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return await self._intercept_common("stream_unary", continuation, client_call_details, request_iterator)

    async def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        return await self._intercept_common("stream_stream", continuation, client_call_details, request_iterator)


# ————————————————————————————————————————————————————————————————
# Helpers to attach interceptor to an existing aio channel
# ————————————————————————————————————————————————————————————————
_POSSIBLE_CH_NAMES = (
    "channel", "_channel", "grpc_channel", "mt5_channel",
    "aio_channel", "channel_aio", "grpc_aio_channel", "_grpc_aio_channel",
    "conn_channel", "connection_channel",
)

def _get_any_channel(obj) -> Optional[grpc.aio.Channel]:
    for nm in _POSSIBLE_CH_NAMES:
        ch = getattr(obj, nm, None)
        if ch is not None:
            return ch
    # clients.*
    clients = getattr(obj, "clients", None)
    if clients is not None:
        for nm in _POSSIBLE_CH_NAMES:
            ch = getattr(clients, nm, None)
            if ch is not None:
                return ch
    return None

def _set_channel_everywhere(obj, new_ch: grpc.aio.Channel) -> None:
    for nm in _POSSIBLE_CH_NAMES:
        try:
            if hasattr(obj, nm):
                setattr(obj, nm, new_ch)
        except Exception:
            pass
    clients = getattr(obj, "clients", None)
    if clients is not None:
        for nm in _POSSIBLE_CH_NAMES:
            try:
                if hasattr(clients, nm):
                    setattr(clients, nm, new_ch)
            except Exception:
                pass

def attach_grpc_debug_interceptor(
    acc: Any,
    *,
    log_to_file: Optional[str] = "mt5_rpc_debug.log",
    also_print: bool = True,
    dump_payload: bool = True,
    redact_keys: Iterable[str] = ("password", "pwd", "pass", "authorization"),
    rebuild_stubs: bool = True,
    rebuild_fn = None,
) -> bool:
    """
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ║ FUNCTION attach_grpc_debug_interceptor                                      ║
    ╠═════════════════════════════════════════════════════════════════════════════╣
    ║ Attaches AioDebugInterceptor to acc's grpc.aio.Channel; optionally          ║
    ║ rebuilds stubs via rebuild_fn(acc, new_channel). Returns True on success.   ║
    ║ Sensitive keys are redacted; payload dump is optional.                      ║
    ║ Usage (example):                                                            ║
    ║   attach_grpc_debug_interceptor(acc, log_to_file="mt5_rpc_debug.log",       ║
    ║                                  rebuild_fn=_build_all_clients_from_channel)║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """
    ch = _get_any_channel(acc)
    if ch is None or not isinstance(ch, grpc.aio.Channel):
        return False

    interceptor = AioDebugInterceptor(
        log_to_file=log_to_file,
        also_print=also_print,
        dump_payload=dump_payload,
        redact_keys=redact_keys,
    )
    try:
        new_ch = grpc.aio.intercept_channel(ch, interceptor)
    except Exception:
        return False

    _set_channel_everywhere(acc, new_ch)

    # If provided, rebuild service stubs against the new channel
    if rebuild_stubs:
        try:
            if rebuild_fn is not None:
                rebuild_fn(acc, new_ch)
        except Exception:
            pass

    return True

