# examples/opened_snapshot.py
import asyncio
import logging

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title

try:
    from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH  # type: ignore
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
    Example: Opened Orders/Positions snapshot with graceful fallbacks
    =================================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Open async session to the MT5 bridge; must be closed with `shutdown()`. |
    | Heading | `title("Opened snapshot")` | Cosmetic section header in console/log. |
    | Primary path | Try low-level wrapper: `acc.opened_orders()` | Uses the client wrapper if present in this build. Handles optional sort mode param when required. |
    | Fallback path | Direct gRPC to `AccountHelper.OpenedOrders` via pb2 (if available) | Bypasses wrapper differences across builds; sets optional sort field if it exists. |
    | Normalize | `_resolve_containers(reply)` | Supports variant container names: positions vs. position_infos vs. opened_positions; pending vs. orders vs. opened_orders vs. pending_orders. |
    | Print | `_print_snapshot(reply)` | Logs counts per container and prints up to 10 friendly rows per block (ticket, symbol, volume, open/cur prices, P/L, swap). |
    | Cleanup | `await shutdown(acc)` | Always close the session even if earlier steps failed. |

    RPCs used (may vary by build)
    ------------------------------
    - Wrapper (if exposed):
        * `opened_orders([sort_mode])`  → returns a structure with pending/orders and/or positions
    - Direct gRPC (fallback; requires pb2 & stub in this build):
        * `AccountHelper.OpenedOrders(OpenedOrdersRequest{...})`
          - Optional sort field names that may exist in different builds: `inputSortMode`, `sortMode`
          - Metadata headers are obtained via `acc.get_headers()` if available

    Helper behavior
    ---------------
    - `_get_first(obj, *names)`: fetch first existing attribute/key among candidates; tolerates dicts and pb2.
    - `_len(x)`: safe length getter.
    - `_take_first(seq, n=10)`: safely slices pb2 repeated fields/lists/iterables.
    - `_resolve_containers(reply)`: accepts `reply` or `reply.data`, returns non-empty containers as
      `[("positions", positions_iterable), ("pending_orders", pendings_iterable)]`.
    - `_print_item(i, it)`: prints one entry using common fields if present:
        ticket/order/id, symbol/symbol_name, volume/volume_initial/volume_current,
        price_open/price, price_current/price_cur/price_current_bid, profit, swap.
      Missing fields are silently skipped to stay robust across schema variants.

    Logging & errors
    ----------------
    - Module-level `logging.basicConfig(level=logging.INFO)`.
    - The primary wrapper path catches `TypeError` to auto-retry with `sort=0` for builds that require it.
    - Both wrapper and gRPC calls are guarded; failures are logged at DEBUG/WARNING and the flow proceeds to fallbacks.
    - If no snapshot could be retrieved, prints a single clear error and exits gracefully.

    Output format (typical)
    -----------------------
    ▶ positions: 2 pcs (first 2)
       #1 | ticket=123456 | EURUSD | vol=0.1 | open=1.08450 | cur=1.08510 | P/L=6.00 | swap=0.00
       #2 | ticket=123457 | XAUUSD | vol=0.02 | open=2350.00 | cur=2351.10 | P/L=2.20
    ▶ pending_orders: 1 pcs (first 1)
       #1 | ticket=987654 | EURUSD | vol=0.1 | open=1.08300

    Environment / requirements
    --------------------------
    - A configured connection (see your `.env` / `connect()` implementation).
    - This example tolerates schema differences across builds; pb2 for AccountHelper is optional.
    - If the client build lacks both the wrapper and AccountHelper stub, the example will report that the snapshot is unavailable.

    Edge cases & portability
    ------------------------
    - Different servers/builds expose different field names and container shapes; this example normalizes them.
    - If the API returns an envelope with `data`, it will be unwrapped automatically.
    - Large datasets are trimmed in log output (first 10 items per container) to keep logs readable.

    How to run
    ----------
    From the project root:
      `python -m examples.opened_snapshot`

    If you use the CLI runner:
      `python -m examples.cli run opened_snapshot`
    """