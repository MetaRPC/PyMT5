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
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/streaming.py — hybrid tick streaming (push-preferred, 1 Hz IO) ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Demonstrate a resilient tick stream: subscribe to server “push” ticks and  ║
║   simultaneously poll as a fallback, then automatically stop polling once    ║
║   push activity is detected. Prints at most ~1 line per second.              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                     ║
║   1) Connects (connect()), selects SYMBOL, shows a header (title).           ║
║   2) Starts two tasks in parallel:                                           ║
║        • consume_push(): async-iterates `acc.on_symbol_tick(...)`.           ║
║        • consume_poll(): periodically calls `acc.symbol_info_tick(...)`.     ║
║   3) A guard task waits for first push event, then cancels the poll task.    ║
║   4) Runs for RUN_SECONDS, cancels tasks, prints counters, and shuts down.   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Concurrency & cancellation                                                   ║
║   • `cancel_evt` stops the push generator.                                   ║
║   • `got_push` is set on the first push event → cancels the poll task.       ║
║   • All tasks are awaited with suppression to ensure clean teardown.         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Data selection & printing                                                    ║
║   • From events/ticks, the code prefers `last`, then `bid`, then `ask`.      ║
║   • Prints no more than once per second (monotonic time throttle).           ║
║   • Final line reports totals:                                               ║
║       `ticks total | push | polled | last price`.                            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Tunables (top of file)                                                       ║
║   • `RUN_SECONDS`      — total demo duration (default: 10.0 s).              ║
║   • `POLL_INTERVAL_S`  — polling cadence (default: 0.3 s).                   ║
║   • Push cadence is driven by the server; poll is used only until push hits. ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Key APIs used                                                                ║
║   • `await acc.symbol_select(SYMBOL, True)`                                  ║
║   • Push: `async for evt in acc.on_symbol_tick(SYMBOL, None, cancel_evt)`    ║
║   • Poll: `await acc.symbol_info_tick(SYMBOL)`                               ║
║   • Session lifecycle: `connect()`, `shutdown()`                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Robustness notes                                                             ║
║   • Works even if push never arrives (keeps polling).                        ║
║   • Stops polling as soon as push is confirmed (“Push engaged → stop…”).     ║
║   • Exception-safe teardown via `contextlib.suppress` and task cancellation. ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Output example                                                               ║
║   Symbol EURUSD selected                                                     ║
║   [poll] 1.12345                                                             ║
║   [push] 1.12347                                                             ║
║   Push engaged → stop polling.                                               ║
║   ...                                                                        ║
║   ticks total: 57 | push: 44 | polled: 13 | last: 1.12389                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Dependencies / helpers                                                       ║
║   • Env/setup: `examples/common/env.py` (connect, shutdown, SYMBOL).         ║
║   • Console helpers: `examples/common/utils.py` (title).                     ║
║   • pb2 compatibility layer: `examples/common/pb2_shim.py` (apply_patch).    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   • `python -m examples.cli run streaming`                                   ║
║     (or run this module directly).                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""