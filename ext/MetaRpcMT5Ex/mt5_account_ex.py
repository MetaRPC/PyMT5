# ╔════════════════════════════════════════════════════════════════════════════╗
# ║ MT5AccountEx — server-name connect shim (framed edition)                   ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║ What & Why                                                                 ║
# ║ ───────────                                                                ║
# ║ Some versions of the MetaRpcMT5 package expose `connect_by_server_name`,   ║
# ║ others only expose a low-level `Connection.ConnectEx` RPC.                 ║
# ║ This adapter keeps your code stable:                                       ║
# ║   • If the base class has `connect_by_server_name` → we delegate to it.    ║
# ║   • Otherwise we build and call `ConnectEx` directly.                      ║
# ║                                                                            ║
# ║ Quick Reference                                                            ║
# ║ ───────────────                                                            ║
# ║   connect_by_server_name(                                                  ║
# ║       server_name: str,                                                    ║
# ║       base_chart_symbol: str = "EURUSD",                                   ║
# ║       wait_for_terminal_is_alive: bool = True,  # kept for API symmetry    ║
# ║       timeout_seconds: int = 30,                                           ║
# ║       deadline: Optional[datetime] = None                                  ║
# ║   ) → None                                                                 ║
# ║                                                                            ║
# ║ Return value                                                               ║
# ║ ─────────────                                                              ║
# ║ Mirrors the underlying implementation: most clients treat this as          ║
# ║ a side‑effecting call (connects or raises). We return whatever the         ║
# ║ underlying method returns (often `None`).                                  ║
# ╚════════════════════════════════════════════════════════════════════════════╝
from __future__ import annotations

from typing import Optional
from datetime import datetime
from MetaRpcMT5 import MT5Account, ApiExceptionMT5
import MetaRpcMT5.mt5_term_api_connection_pb2 as connection_pb2


# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Small helper: extract a human-readable message from various error shapes  │
# └───────────────────────────────────────────────────────────────────────────┘
def safe_error_message(err) -> str:
    return (getattr(err, "message", "")
            or getattr(err, "errorMessage", "")
            or getattr(err, "error_message", ""))


class MT5AccountEx(MT5Account):
    """
    Thin, non-invasive adapter over `MetaRpcMT5.MT5Account`.

    Goals
    -----
    1) Keep public API stable across package versions.
    2) Prefer the high-level connect path if it exists.
    3) Gracefully fall back to the low-level `ConnectEx` RPC.

    Notes
    -----
    - We DO NOT change any behavior of the base class; we only extend it.
    - We DO propagate server-side errors by raising `ApiExceptionMT5` with
      the message extracted from the RPC reply (when available).
    """

    # ╔══════════════════════════════════════════════════════════════════════╗
    # ║ Public API: connect by server (cluster) name                         ║
    # ╚══════════════════════════════════════════════════════════════════════╝
    async def connect_by_server_name(
        self,
        server_name: str,
        base_chart_symbol: str = "EURUSD",
        wait_for_terminal_is_alive: bool = True,
        timeout_seconds: int = 30,
        deadline: Optional[datetime] = None,
    ):
        """
        Connect to MT5 by named server/cluster.

        Strategy
        --------
        1) Preferred path: call `super().connect_by_server_name(...)`.
           • Works on newer package versions.
        2) Fallback path: construct `ConnectExRequest` and call
           `connection_client.ConnectEx(...)` directly.
           • Works on older package versions where the helper is missing.

        Parameters
        ----------
        server_name : str
            Broker server/cluster name (e.g., "MetaQuotes-Demo").
        base_chart_symbol : str
            Symbol used for readiness/sync checks on connect.
        wait_for_terminal_is_alive : bool
            Kept for API symmetry; the fallback relies on server-side defaults.
        timeout_seconds : int
            How long to wait for terminal readiness on the server side.
        deadline : Optional[datetime]
            Absolute client-side deadline used to compute gRPC timeout.

        Raises
        ------
        ApiExceptionMT5
            If backend returns an error object with a message in the reply.
        AttributeError
            Only for the *preferred* path if the base class is too old;
            in that case we switch to the fallback path automatically.
        """
        # ┌───────────────────────────────────────────────────────────────────┐
        # │ 1) Preferred path: delegate to the base implementation            │
        # └───────────────────────────────────────────────────────────────────┘
        try:
            return await super().connect_by_server_name(
                server_name=server_name,
                base_chart_symbol=base_chart_symbol,
                wait_for_terminal_is_alive=wait_for_terminal_is_alive,
                timeout_seconds=timeout_seconds,
                deadline=deadline,
            )

        # ┌───────────────────────────────────────────────────────────────────┐
        # │ 2) Fallback path: build and call Connection.ConnectEx directly    │
        # └───────────────────────────────────────────────────────────────────┘
        except AttributeError:
            # Build the request the same way the helper would do.
            req = connection_pb2.ConnectExRequest(
                user=self.user,
                password=self.password,
                mt_cluster_name=server_name,
                base_chart_symbol=base_chart_symbol,
                terminal_readiness_waiting_timeout_seconds=timeout_seconds,
            )

            # Compute per-RPC timeout from an absolute deadline, if given.
            timeout = (deadline - datetime.utcnow()).total_seconds() if deadline else None
            # gRPC expects timeout >= 0 or None
            timeout = max(timeout, 0) if timeout is not None else None

            # Perform the RPC using the same channel/auth headers as the base class.
            res = await self.connection_client.ConnectEx(
                req,
                metadata=self.get_headers(),
                timeout=timeout,
            )

            # If backend attached an error object with a message, bubble it up.
            err = getattr(res, "error", None)
            if err and safe_error_message(err):
                raise ApiExceptionMT5(err)

            # Keep parity with base helper: usually returns None on success.
            return None
