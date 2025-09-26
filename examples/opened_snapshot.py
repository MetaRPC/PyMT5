# examples/opened_snapshot.py
import asyncio
import logging

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title

try:
    from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH 
except Exception:
    AH = None 

# ───────────────────────── logging ─────────────────────────
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ───────────────────────── helpers ─────────────────────────
def _get_first(obj, *names):
    """Return the first field/key found from names."""
    if obj is None:
        return None
    for n in names:
        try:
            if isinstance(obj, dict) and n in obj:
                return obj[n]
            if hasattr(obj, n):
                return getattr(obj, n)
        except Exception:
            pass
    return None

def _len(x):
    try:
        return len(x)
    except Exception:
        return 0

def _take_first(seq, n=10):
    """It is safe to take the first n elements from an arbitrary collection/repeatable field pb2."""
    try:
        if hasattr(seq, "__getitem__") and hasattr(seq, "__len__"):
            return [seq[i] for i in range(min(n, len(seq)))]
        return list(seq)[:n]
    except Exception:
        return []

def _resolve_containers(reply):
    """
    We support different container names in the response:
- positions / position_infos / opened_positions
- pending / orders / opened_orders / pending_orders
Returns a list of tuples [(label, iterable), ...], all non-empty.
    """
    if reply is None:
        return []

    # Sometimes it's useful to remove .data
    reply0 = _get_first(reply, "data") or reply

    positions = (
        _get_first(reply0, "positions")
        or _get_first(reply0, "position_infos")
        or _get_first(reply0, "opened_positions")
    )

    pendings = (
        _get_first(reply0, "pending")
        or _get_first(reply0, "orders")
        or _get_first(reply0, "opened_orders")
        or _get_first(reply0, "pending_orders")
    )

    out = []
    if positions:
        out.append(("positions", positions))
    if pendings:
        out.append(("pending_orders", pendings))
    return out

def _print_item(i, it):
    """Printing a single order/position record with the most user-friendly set of fields."""
    ticket = _get_first(it, "ticket", "order", "id")
    symbol = _get_first(it, "symbol", "symbol_name")
    volume = _get_first(it, "volume", "volume_initial", "volume_current")
    price_open = _get_first(it, "price_open", "price")
    price_cur  = _get_first(it, "price_current", "price_cur", "price_current_bid")
    profit = _get_first(it, "profit")
    swap   = _get_first(it, "swap")

    parts = [
        f"#{i}",
        f"ticket={ticket}" if ticket is not None else None,
        f"{symbol}" if symbol else None,
        f"vol={volume}" if volume is not None else None,
        f"open={price_open}" if price_open is not None else None,
        f"cur={price_cur}" if price_cur is not None else None,
        f"P/L={profit}" if profit is not None else None,
        f"swap={swap}" if swap is not None else None,
    ]
    line = " | ".join(p for p in parts if p)
    log.info("   %s", line)

def _print_snapshot(reply) -> None:
    """We beautifully print a “snapshot” of open positions/applications."""
    if reply is None:
        log.warning("The server returned an empty response..")
        return

    blocks = _resolve_containers(reply)
    if not blocks:
        log.info("Opened snapshot: arrays of requests/positions were not found in the response.")
        return

    for label, arr in blocks:
        cnt = _len(arr)
        log.info("▶ %s: %s piece (first %s)", label, cnt, min(cnt, 10))
        for idx, it in enumerate(_take_first(arr, 10), 1):
            _print_item(idx, it)


async def main():
    acc = await connect()
    try:
        title("Opened snapshot")

        reply = None

        # 1)Low-level call via wrapper (without safe_async → without "sheet")
        if hasattr(acc, "opened_orders"):
            try:
                reply = await acc.opened_orders()
            except TypeError:
                
                try:
                    reply = await acc.opened_orders(0)
                except Exception as e:
                    log.debug("opened_orders(sort=0) failed: %r", e)
                    reply = None
            except Exception as e:
                log.debug("opened_orders() failed: %r", e)
                reply = None

        # 2) Direct gRPC bypassing the wrapper
        if reply is None and AH is not None and getattr(acc, "account_helper_client", None):
            try:
                req = AH.OpenedOrdersRequest()
                
                try:
                    setattr(req, "inputSortMode", 0)
                except Exception:
                    try:
                        setattr(req, "sortMode", 0)
                    except Exception:
                        pass

                meta = acc.get_headers() if hasattr(acc, "get_headers") else []
                r = await acc.account_helper_client.OpenedOrders(req, metadata=meta, timeout=5.0)
                reply = _get_first(r, "data") or r
            except Exception as e:
                log.warning("Direct OpenedOrders RPC failed: %r", e)

        if reply is None:
            log.error("Unable to get a snapshot of open tickets in this client build.")
            return

        _print_snapshot(reply)

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.opened_snapshot


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/opened_snapshot.py — snapshot of open positions and orders     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Retrieve and neatly print a “snapshot” of open positions and/or pending    ║
║   orders. Works across heterogeneous builds: first tries the high-level      ║
║   client method, and if unavailable falls back to a direct AccountHelper RPC.║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                     ║
║   1) Applies the pb2 shim (module/alias compatibility).                      ║
║   2) Connects to MT5 (connect()), prints a title header.                     ║
║   3) Attempts acc.opened_orders():                                           ║
║        • call without args; on TypeError retry with 0 (sort=0).              ║
║   4) If that fails and AH + account_helper_client exist:                     ║
║        • build AH.OpenedOrdersRequest(),                                     ║
║        • set sorting (inputSortMode or sortMode) = 0,                        ║
║        • call AccountHelper.OpenedOrders(..., timeout=5s) with metadata      ║
║          (acc.get_headers() if present),                                     ║
║        • take payload from r.data when available.                            ║
║   5) If no reply — log an error and exit.                                    ║
║   6) If reply present — detect containers (positions / opened_positions,     ║
║      pending / orders / opened_orders / pending_orders) and print top 10.    ║
║   7) Gracefully shuts down the connection (shutdown()).                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Formats & robustness                                                         ║
║   • Supports varying field names and nesting (e.g., reply.data).             ║
║   • Prints user-friendly fields for each item: ticket/order/id, symbol,      ║
║     volume*(initial/current), price_open/price, price_current, P/L, swap.    ║
║   • Logging configured at INFO level (basicConfig(level=INFO)).              ║
║   • Direct calls only; no safe_async wrapper.                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Direct API calls                                                             ║
║   High-level:  acc.opened_orders([sort=0])                                   ║
║   Low-level :  AccountHelper.OpenedOrders(AH.OpenedOrdersRequest, metadata)  ║
║   Utilities :  connect(), shutdown(), title()                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers in this file                                                         ║
║   _get_first(obj, *names)  — first existing attr/key among names.            ║
║   _len(x)                  — safe length.                                    ║
║   _take_first(seq, n=10)   — top n items from list/repeated pb2 field.       ║
║   _resolve_containers(r)   — find arrays of positions and/or orders.         ║
║   _print_item(i, it)       — one human-readable line per position/order.     ║
║   _print_snapshot(reply)   — assemble and print compact snapshot.            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Dependencies                                                                 ║
║   pb2_shim.apply_patch() — pb2 module/class aliases.                         ║
║   MetaRpcMT5.mt5_term_api_account_helper_pb2 as AH — RPC types (optional).   ║
║   acc.account_helper_client — low-level gRPC client (if present).            ║
║   examples/common/env: connect(), shutdown()                                 ║
║   examples/common/utils: title()                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Error handling                                                               ║
║   • TypeError on opened_orders() → retry with argument 0.                    ║
║   • Low-level RPC exceptions → warning log and fallback/exit.                ║
║   • Empty reply or missing arrays → clear, informative log messages.         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   python -m examples.cli run opened_snapshot                                 ║
║   (connection parameters via .env/environment).                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Notes                                                                        ║
║   • AH is imported “softly”: if not present in the build, only the           ║
║     high-level acc.opened_orders() path is used.                             ║
║   • Metadata comes from acc.get_headers() when available.                    ║
║   • Prints at most the first 10 items per container.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""