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
╔═══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/streaming_positions_tickets.py — live positions & pending IDs   ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                       ║
║   Subscribe to live updates of **positions and pending orders tickets**       ║
║   (IDs and related payload) and print each event during a short demo window.  ║
║   Works with both async-generator and callback-style APIs across builds.      ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                      ║
║   1) Apply pb2 shim (`apply_patch`), connect to MT5 (`connect()`).            ║
║   2) Try async-generator API:                                                 ║
║        `gen = acc.on_positions_and_pending_orders_tickets(                    ║
║               INTERVAL_MS, deadline=None, cancel_evt)`                        ║
║      • If it is an async generator → `async for evt in gen: ...`              ║
║        for `RUN_SECONDS`, then set `cancel_evt` and await consumer task.      ║
║   3) If not a generator, use callback API (best-effort):                      ║
║        `unsub = await acc.on_positions_and_pending_orders_tickets(            ║
║                 INTERVAL_MS, on_evt)`                                         ║
║      • Sleep `RUN_SECONDS`, then call `unsub()` if provided.                  ║
║   4) Print total event count and shutdown gracefully.                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Streams API shapes handled                                                    ║
║   • **Async-generator**: `on_positions_and_pending_orders_tickets(ms, None,   ║
║     cancel_evt)` returns an async gen → `async for evt in gen`.               ║
║   • **Callback**: `await on_positions_and_pending_orders_tickets(ms, on_evt)` ║
║     → returns `unsub()` callable to stop updates.                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Cancellation & lifecycle                                                      ║
║   • Generator mode: `cancel_evt.set()` after time budget to stop the stream.  ║
║   • Callback mode: call `unsub()` after sleeping `RUN_SECONDS`.               ║
║   • Uses `contextlib.suppress` on teardown to avoid noisy exceptions.         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                        ║
║   • Prints each incoming event as `evt: <payload>` (shape depends on build:   ║
║     tickets/IDs, symbols, counts, etc.).                                      ║
║   • Final line: `tickets updates received: <count>`.                          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Tunables (top of file)                                                        ║
║   • `RUN_SECONDS` — how long to listen (default: 3.0 s).                      ║
║   • `INTERVAL_MS` — requested update interval (default: 1000 ms).             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Robustness tactics                                                            ║
║   • Runtime detection of generator vs callback (TypeError fallbacks).         ║
║   • Cooperative cancellation and shielded teardown for clean exits.           ║
║   • Works across heterogeneous adapters that expose different streaming forms.║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ When “nothing happens”                                                        ║
║   • No open positions or pendings, or provider doesn’t emit this stream →     ║
║     zero events. Increase `RUN_SECONDS` or verify build/server capabilities.  ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ Helpers / dependencies                                                        ║
║   • `connect`, `shutdown` from `examples/common/env.py`.                      ║
║   • `title` from `examples/common/utils.py`.                                  ║
║   • `apply_patch()` from `examples/common/pb2_shim.py`.                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                    ║
║   • `python -m examples.cli run streaming_positions_tickets`                  ║
║     (or run the module directly).                                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""