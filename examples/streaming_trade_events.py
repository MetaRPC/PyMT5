import asyncio, time, contextlib
from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown, SYMBOL
from .common.utils import title

RUN_SECONDS = 10.0
POLL_INTERVAL_S = 0.3

async def main():
    acc = await connect()
    try:
        title("Streaming: up to 1Hz (push preferred)")
        await acc.symbol_select(SYMBOL, True)
        print(f"Symbol {SYMBOL} selected")

        last_print = 0.0
        ticks_total = 0
        push_ticks  = 0
        poll_ticks  = 0
        last_price  = None

        cancel_evt = asyncio.Event()
        got_push   = asyncio.Event()

        async def consume_push():
            nonlocal ticks_total, push_ticks, last_price, last_print
            async for evt in acc.on_symbol_tick(SYMBOL, None, cancel_evt):
                price = getattr(evt, "last", None) or getattr(evt, "bid", None) or getattr(evt, "ask", None)
                if isinstance(price, (float, int)):
                    last_price = float(price)
                push_ticks += 1
                ticks_total += 1
                got_push.set()
                now = time.monotonic()
                if now - last_print >= 1.0:
                    last_print = now
                    print(f"[push] {last_price}")

        async def consume_poll():
            nonlocal ticks_total, poll_ticks, last_price, last_print
            while not cancel_evt.is_set():
                try:
                    ti = await acc.symbol_info_tick(SYMBOL)
                    price = getattr(ti, "last", None) or getattr(ti, "bid", None) or getattr(ti, "ask", None)
                    if isinstance(price, (float, int)):
                        last_price = float(price)
                        poll_ticks += 1
                        ticks_total += 1
                        # print no more frequently than 1 Hz
                        now = time.monotonic()
                        if now - last_print >= 1.0:
                            last_print = now
                            print(f"[poll] {last_price}")
                except Exception:
                    pass
                await asyncio.sleep(POLL_INTERVAL_S)

        push_task = asyncio.create_task(consume_push())
        poll_task = asyncio.create_task(consume_poll())

        # If the push is "woke" - you can disable the poll
        async def stop_poll_on_push():
            await got_push.wait()
            print("Push engaged → stop polling.")
            poll_task.cancel()
            with contextlib.suppress(Exception):
                await poll_task

        guard_task = asyncio.create_task(stop_poll_on_push())

        await asyncio.sleep(RUN_SECONDS)

        cancel_evt.set()
        for t in (guard_task, poll_task, push_task):
            if t and not t.done():
                t.cancel()
        with contextlib.suppress(Exception):
            await asyncio.gather(guard_task, poll_task, push_task)

        print(f"ticks total: {ticks_total} | push: {push_ticks} | polled: {poll_ticks} | last: {last_price}")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


#  python -m examples.streaming_trade_events

"""
    Example: Tick streaming @ ~1 Hz (push preferred, poll as fallback)
    =================================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session; must be closed with `shutdown()`. |
    | Heading | `title("Streaming: up to 1Hz (push preferred)")` | Cosmetic header. |
    | Ensure symbol | `symbol_select(SYMBOL, True)` | Guarantees the symbol is in Market Watch to receive ticks. |
    | Start push | `on_symbol_tick(SYMBOL, None, cancel_evt)` → async generator | Primary source of ticks; lower latency and less load than polling. |
    | Start poll | loop of `symbol_info_tick(SYMBOL)` + `sleep(POLL_INTERVAL_S)` | Fallback path to still show data if push isn’t available yet. |
    | 1 Hz gate | Print no more than once per second (shared throttle) | Keeps console readable; doesn’t flood logs even if ticks are frequent. |
    | Auto switch | Stop polling once the first push tick arrives | Saves resources when streaming is confirmed (`got_push` event). |
    | Counters | Track totals: `ticks_total`, `push_ticks`, `poll_ticks`, `last_price` | Final summary line shows how data arrived. |
    | Cleanup | Set `cancel_evt`, cancel tasks, `await shutdown(acc)` | Graceful teardown even if tasks are mid-await. |

    Tick fields & normalization
    ---------------------------
    - For both push and poll we try `evt.last or evt.bid or evt.ask` (poll: `ti.last|bid|ask`).
    - If a field is present and numeric, it becomes `last_price`.
    - Printed lines are tagged by source: `[push] 1.08457` or `[poll] 1.08457`.

    Concurrency model
    -----------------
    - Three tasks:
      1) `consume_push()` — async-gen over `on_symbol_tick(...)`
      2) `consume_poll()` — while-loop polling every `POLL_INTERVAL_S`
      3) `stop_poll_on_push()` — waits for first push tick, then cancels polling
    - Shared `last_print` throttles output to ~1 Hz across both sources.

    Parameters
    ----------
    - `RUN_SECONDS = 10.0` — total run duration.
    - `POLL_INTERVAL_S = 0.3` — polling cadence (tweak 0.2–1.0 depending on provider limits).

    When you might see zero or only polling
    ---------------------------------------
    - Market closed or no market data → no push ticks; polling may also return stale/none.
    - Provider disables tick streaming for this symbol/account → only polling shows changes.
    - Symbol not selected/allowed → both paths may be silent (ensure `symbol_select` success).
    - Very quiet markets → ticks are rare; increase `RUN_SECONDS`.

    Output (typical)
    ----------------
    Streaming: up to 1Hz (push preferred)
    Symbol EURUSD selected
    [poll] 1.08456
    [push] 1.08457
    Push engaged → stop polling.
    [push] 1.08460
    ...
    ticks total: 23 | push: 19 | polled: 4 | last: 1.08460

    Notes & tips
    ------------
    - If push never engages, the guard keeps polling for the whole window and prints from polling only.
    - If `on_symbol_tick` supports deadlines in your build, prefer **client-side** cancellation (as here) to avoid server-time skew issues.
    - For stress testing, set `RUN_SECONDS=60` and reduce `POLL_INTERVAL_S` cautiously; watch provider throttling.

    How to run
    ----------
    From project root:
      `python -m examples.streaming_tick_push_poll`
    Or via CLI (if present):
      `python -m examples.cli run streaming_tick_push_poll`
    """