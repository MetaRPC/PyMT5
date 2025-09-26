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
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/streaming_position_profit.py — live position PnL streaming     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Subscribe to live “position profit” updates from the MT5 bridge and print  ║
║   incoming events for a short demo window. Works with both async-generator   ║
║   and callback-style streaming APIs exposed by different builds.             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                     ║
║   1) Apply pb2 shim (apply_patch), connect to MT5 (connect()).               ║
║   2) Try `acc.on_position_profit(INTERVAL_MS, deadline=None, cancel_evt)`    ║
║      and detect if it returns an **async generator**.                        ║
║      • If yes: consume `async for evt in gen:` until time budget expires.    ║
║   3) If not a generator, fall back to **callback** API:                      ║
║      • Try `await acc.on_position_profit(INTERVAL_MS, on_evt)` → returns     ║
║        `unsub` callable; on TypeError try `(INTERVAL_MS, True, on_evt)`.     ║
║   4) Run for `RUN_SECONDS` seconds, then cancel (event or unsubscribe).      ║
║   5) Print how many profit updates were received; shutdown() gracefully.     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Streams API shapes handled                                                   ║
║   • Async-generator:                                                         ║
║       `gen = acc.on_position_profit(interval_ms, deadline=None, cancel_evt)` ║
║       `async for evt in gen: ...`                                            ║
║   • Callback subscription:                                                   ║
║       `unsub = await acc.on_position_profit(interval_ms, on_evt)` or         ║
║       `unsub = await acc.on_position_profit(interval_ms, True, on_evt)`      ║
║     In both cases, `unsub()` stops updates.                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Cancellation & lifecycle                                                     ║
║   • Async-gen mode: an `asyncio.Event` (`cancel_evt`) is passed into the API;║
║     it’s set after `RUN_SECONDS`, which should terminate the stream.         ║
║   • Callback mode: `unsub()` is called after the sleep window.               ║
║   • All shutdown paths use `contextlib.suppress` to avoid noisy teardown.    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                       ║
║   • Each incoming event is printed as `evt: <payload>`.                      ║
║   • Final line: `profit updates received: <count>`.                          ║
║   • Payload shape is build-specific (position ticket, symbol, profit, etc.). ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Tunables                                                                     ║
║   • `RUN_SECONDS`  — total listening time (default 3.0 s).                   ║
║   • `INTERVAL_MS`  — producer’s update interval request (default 500 ms).    ║
║   (Edit constants at the top of the file.)                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Robustness tactics                                                           ║
║   • Detects generator vs callback API at runtime (TypeError fallback).       ║
║   • Uses `asyncio.create_task` + cooperative cancellation for clean exit.    ║
║   • Shields shutdown steps against spurious exceptions.                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ When “nothing happens”                                                       ║
║   • No open positions or provider doesn’t emit this stream → zero events.    ║
║   • Try increasing `RUN_SECONDS`, ensure trading data exists, or verify the  ║
║     account/build supports `on_position_profit`.                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers / dependencies                                                       ║
║   • `connect`, `shutdown` from `examples/common/env.py`.                     ║
║   • `title` from `examples/common/utils.py`.                                 ║
║   • `apply_patch()` from `examples/common/pb2_shim.py`.                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   • From project root: `python -m examples.cli run streaming_position_profit`║
║     (or run the module file directly).                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
