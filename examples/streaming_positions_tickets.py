import asyncio
import contextlib
import inspect

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title

RUN_SECONDS     = 3.0     # This is how many seconds we listened to updates for.
INTERVAL_MS     = 1000    # frequency/interval of requested updates

async def main():
    acc = await connect()
    try:
        title(f"Streaming: on_positions_and_pending_orders_tickets ({int(RUN_SECONDS)}s, {INTERVAL_MS} ms)")

        count = 0
        cancel_evt = asyncio.Event()

        # Trying to get an async generator:
        gen = None
        try:
            gen = acc.on_positions_and_pending_orders_tickets(INTERVAL_MS, None, cancel_evt)
        except TypeError:
            
            gen = acc.on_positions_and_pending_orders_tickets(INTERVAL_MS)

        if gen and inspect.isasyncgen(gen):
            async def consume():
                nonlocal count
                async for evt in gen:
                    
                    count += 1
                    print("evt:", evt)  # ← we display the event

            task = asyncio.create_task(consume())
            # We wait for RUN_SECONDS, then carefully turn off the generator
            try:
                await asyncio.sleep(RUN_SECONDS)
            finally:
                cancel_evt.set()
                with contextlib.suppress(Exception):
                    await task

        else:
            # Rare case: if there is an adapter with a callback, we will support it too (best-effort)
            def on_evt(_evt):
                nonlocal count
                count += 1
                print("evt:", _evt)  # ← we display the event

            # we're trying to get a reply
            unsub = await acc.on_positions_and_pending_orders_tickets(INTERVAL_MS, on_evt)
            await asyncio.sleep(RUN_SECONDS)
            if callable(unsub):
                with contextlib.suppress(Exception):
                    unsub()

        print("tickets updates received:", count)

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())



# python -m examples.streaming_positions_tickets

"""
    Example: Streaming — positions & pending order tickets
    ======================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session to the MT5 bridge; must be closed with `shutdown()`. |
    | Heading | `title(...)` | Shows stream name and timing parameters. |
    | Params | `RUN_SECONDS`, `INTERVAL_MS` | Run duration and requested update interval (ms). |
    | Primary path | `gen = acc.on_positions_and_pending_orders_tickets(INTERVAL_MS, None, cancel_evt)` | Newer builds return an **async generator**; we pass a `cancellation_event` for graceful stop. |
    | Consume | `async for evt in gen: ...` | Each `evt` typically contains current **tickets** of positions and pending orders. We print raw events for portability. |
    | Fallback path | Callback-style API | For legacy adapters: subscribe with Python callback and optional `unsub` handle; sleep for `RUN_SECONDS`, then unsubscribe. |
    | Cleanup | `cancel_evt.set()` or `unsub()`; `await shutdown(acc)` | Cooperative cancellation, then guaranteed disconnect. |

    API variants handled
    --------------------
    1) **Async generator** (preferred in recent builds)
       - Common signature:
         `on_positions_and_pending_orders_tickets(interval_ms: int, deadline: Optional[datetime]=None, cancellation_event: Optional[asyncio.Event]=None) -> AsyncGenerator[Event, None]`
       - We detect the generator with `inspect.isasyncgen(gen)` and iterate it.

    2) **Callback-based** (legacy)
       - Possible signature:
         `(interval_ms, on_callback) -> unsub_callable`
       - We increment a counter and print each incoming event; call `unsub()` if provided.

    Event payload
    -------------
    - The structure depends on your build/provider. Typical fields refer to **position tickets** and **pending order tickets**,
      sometimes accompanied by lightweight metadata (symbol, side, etc.). This example prints the **raw object**.

    Timing & cancellation
    ---------------------
    - The stream runs for `RUN_SECONDS` (default 3s). After that:
      - async-gen path: `cancel_evt.set()` requests a cooperative stop; we await the consumer task.
      - callback path: we call `unsub()` if a callable was returned.
    - `INTERVAL_MS` is the target cadence (e.g., 1000 ms). Actual push rate may be throttled by the provider.

    Error handling
    --------------
    - We optimistically try the 3-arg async-gen signature; on `TypeError` retry without `deadline/cancel_evt`.
    - Callback path is wrapped best-effort; unsubscription is suppressed on errors.

    Typical output
    --------------
    ==================== Streaming: on_positions_and_pending_orders_tickets (3s, 1000 ms) ====================
    evt: <TicketsEvent positions=[12345678, 12345679] pending=[987654, 987655] ts=...>
    evt: <TicketsEvent ...>
    ...
    tickets updates received: N

    Notes & tips
    ------------
    - If you see **zero** updates:
      - No open positions and no pending orders → nothing to report.
      - Market closed → tickets list may not change.
      - Some providers emit only **on change**; without state changes the stream may be quiet.
    - For debugging, increase `RUN_SECONDS` (e.g., 30) and ensure there are open positions or active pendings.

    How to run
    ----------
    From project root:
      `python -m examples.streaming_position_and_pending_tickets`
    Or via your CLI (if present):
      `python -m examples.cli run streaming_position_and_pending_tickets`

    Tuning
    ------
    - Adjust `INTERVAL_MS` (e.g., 500–2000 ms) to balance load vs. responsiveness.
    - Keep `RUN_SECONDS` long enough to observe changes during quiet markets.
    """