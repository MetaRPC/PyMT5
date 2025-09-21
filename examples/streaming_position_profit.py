import asyncio
import contextlib
import inspect

from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown
from .common.utils import title

RUN_SECONDS  = 3.0    # listen for 3 seconds
INTERVAL_MS  = 500    # update interval, as in the source (500 ms)

async def main():
    acc = await connect()
    try:
        title(f"Streaming: on_position_profit ({int(RUN_SECONDS)} seconds, {INTERVAL_MS} ms interval)")

        count = 0
        cancel_evt = asyncio.Event()

        # Trying to get an async generator (typical case for your build):
        gen = None
        try:
            # Common signature: on_position_profit(interval_ms, deadline=None, cancellation_event=None) -> async generator
            gen = acc.on_position_profit(INTERVAL_MS, None, cancel_evt)
        except TypeError:
            # If the adapter is different, let's try without deadline/cancel_evt
            gen = acc.on_position_profit(INTERVAL_MS)

        if gen and inspect.isasyncgen(gen):
            async def consume():
                nonlocal count
                async for evt in gen:
                    count += 1
                
                    print("evt:", evt)

            task = asyncio.create_task(consume())
            try:
                await asyncio.sleep(RUN_SECONDS)
            finally:
                cancel_evt.set()
                with contextlib.suppress(Exception):
                    await task

        else:
            
            def on_evt(_evt):
                nonlocal count
                count += 1
                print("evt:", _evt)

            unsub = None
            
            try:
                
                unsub = await acc.on_position_profit(INTERVAL_MS, on_evt)
            except TypeError:
                try:
                    
                    unsub = await acc.on_position_profit(INTERVAL_MS, True, on_evt)
                except TypeError:
                    
                    pass

            await asyncio.sleep(RUN_SECONDS)
            if callable(unsub):
                with contextlib.suppress(Exception):
                    unsub()

        print("profit updates received:", count)

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.streaming_position_profit

"""
    Example: Streaming PnL — `on_position_profit` (async generator or callback)
    =========================================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session to the MT5 bridge; must be closed with `shutdown()`. |
    | Heading | `title(...)` | Shows stream name and timing parameters. |
    | Params | `RUN_SECONDS`, `INTERVAL_MS` | Run duration and update interval (ms) to match adapter defaults. |
    | Primary path | Create async generator: `acc.on_position_profit(INTERVAL_MS, None, cancel_evt)` | Typical modern builds return an **async generator**; we pass `cancellation_event` for graceful stop. |
    | Consume | `async for evt in gen: ...` | Count and print raw events (`evt` usually carries current positions PnL snapshot/changes). |
    | Fallback path | Legacy callback API | For older adapters: subscribe with a Python callback and optional `unsub` handle. |
    | Stop | `cancel_evt.set()` or `unsub()` | Cooperative cancellation to end the stream after `RUN_SECONDS`. |
    | Cleanup | `await shutdown(acc)` | Always close the session even on errors. |

    Stream API variants handled
    ---------------------------
    1) **Async generator** (preferred in newer builds)
       - Signature commonly seen:
         `on_position_profit(interval_ms: int, deadline: Optional[datetime]=None, cancellation_event: Optional[asyncio.Event]=None) -> AsyncGenerator[Event, None]`
       - We detect by `inspect.isasyncgen(gen)` and iterate asynchronously.

    2) **Callback-based** (legacy)
       - Possible signatures:
         - `(interval_ms, on_callback)` → returns `unsub` callable
         - `(interval_ms, include_closed: bool, on_callback)` → returns `unsub`
         - `(interval_ms, include_closed, on_callback, *extra)` → exotic; tolerated
       - We print each event in the callback and call `unsub()` at the end if provided.

    Event payloads
    --------------
    - `evt` content depends on your build/provider; typical fields relate to positions and their current **profit/loss**.
    - This example intentionally prints the **raw object** (`evt`) to stay portable across schema variants.

    Timing & cancellation
    ---------------------
    - The stream runs for `RUN_SECONDS` (default 3s), then:
      - async-gen path: set `cancel_evt` to request a cooperative stop and await the consumer task.
      - callback path: call `unsub()` if available.
    - `INTERVAL_MS` controls server push cadence (e.g., 500 ms). Real cadence may vary with provider throttling.

    Error handling
    --------------
    - We try the async-generator signature first; if it raises `TypeError`, we fall back to callback variants.
    - All teardown paths are wrapped with `contextlib.suppress` to avoid noisy exceptions on shutdown.

    Output (typical)
    ----------------
    ==================== Streaming: on_position_profit (3 seconds, 500 ms interval) ====================
    evt: <PnLEvent positions=... total_profit=... timestamp=...>
    evt: <PnLEvent ...>
    ...
    profit updates received: N

    Edge cases & tips
    -----------------
    - If you receive **no events**, ensure there are open positions and the account has live market data.
    - Some providers only emit on **changes**; if PnL is static, event rate may be low.
    - If your environment has skewed server time, avoid passing server-side `deadline`; use **client-side** cancellation (as in this example).

    How to run
    ----------
    From project root:
      `python -m examples.on_position_profit`
    Or via CLI (if present):
      `python -m examples.cli run on_position_profit`

    Tuning
    ------
    - Increase `RUN_SECONDS` for longer observation windows (e.g., 30s).
    - Adjust `INTERVAL_MS` to reduce/raise event frequency (provider limits may apply).
    """
