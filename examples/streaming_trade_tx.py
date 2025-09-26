import asyncio
from .common.pb2_shim import apply_patch
apply_patch()

from .common.env import connect, shutdown, SYMBOL
from .common.utils import title

RUN_SECONDS     = 10.0      # Here's how long this process will take.
POLL_INTERVAL_S = 0.3       # survey period
RPC_TIMEOUT_S   = 1.0       # timeout for any grpc
JOIN_TIMEOUT_S  = 2.0       # graceful stop

async def main():
    acc = await connect()
    try:
        title("Streaming: ticks for 10 seconds")

        # 0) symbol in Market Watch (signature: symbol_select(symbol, select))
        await acc.symbol_select(SYMBOL, True)
        print(f"Symbol {SYMBOL} selected")

        # 1) easy pumping
        try:
            ok = await asyncio.wait_for(acc.symbol_is_synchronized(SYMBOL), timeout=RPC_TIMEOUT_S)
            if not ok:
                with asyncio.CancelledError:
                    pass
            try:
                await asyncio.wait_for(acc.symbol_info_tick(SYMBOL), timeout=RPC_TIMEOUT_S)
            except Exception:
                pass
        except Exception:
            pass

        total_ticks = 0
        push_ticks  = 0
        poll_ticks  = 0
        last_price  = None

        got_first_push = asyncio.Event()
        cancel_evt     = asyncio.Event()

        async def consume_push():
            nonlocal total_ticks, push_ticks, last_price
            # on_symbol_tick(symbol, deadline=None, cancellation_event=None) -> async generator
            agen = acc.on_symbol_tick(SYMBOL, None, cancel_evt)
            try:
                async for evt in agen:
                    price = getattr(evt, "last", None) or getattr(evt, "bid", None) or getattr(evt, "ask", None)
                    if isinstance(price, (float, int)):
                        last_price = float(price)
                    push_ticks += 1
                    total_ticks += 1
                    if not got_first_push.is_set():
                        got_first_push.set()
            except asyncio.CancelledError:
                # correct exit on cancellation
                raise
            except Exception:
                # We tolerate any network/grpc errors to avoid demo failure.
                pass

        async def consume_polling():
            nonlocal total_ticks, poll_ticks, last_price
            try:
                while not cancel_evt.is_set():
                    try:
                        ti = await asyncio.wait_for(acc.symbol_info_tick(SYMBOL), timeout=RPC_TIMEOUT_S)
                        price = getattr(ti, "last", None) or getattr(ti, "bid", None) or getattr(ti, "ask", None)
                        if isinstance(price, (float, int)):
                            last_price = float(price)
                            poll_ticks += 1
                            total_ticks += 1
                    except asyncio.TimeoutError:
                        # rpc is silent — attempt +
                        pass
                    except Exception:
                        
                        pass
                    await asyncio.sleep(POLL_INTERVAL_S)
            except asyncio.CancelledError:
                raise

        push_task = asyncio.create_task(consume_push(), name="push")
        poll_task = asyncio.create_task(consume_polling(), name="poll")

        # A little helper: as soon as the first signal arrives, we stop the polling.
        async def stop_poll_on_first_push():
            await got_first_push.wait()
            print("Push stream engaged → stopping polling.")
            poll_task.cancel()
            try:
                await asyncio.wait_for(poll_task, timeout=JOIN_TIMEOUT_S)
            except Exception:
                pass

        guard_task = asyncio.create_task(stop_poll_on_first_push(), name="guard")

        # main demo timer
        try:
            await asyncio.sleep(RUN_SECONDS)
        finally:
            # stop everything without freezing
            cancel_evt.set()
            for t in (guard_task, poll_task, push_task):
                if t and not t.done():
                    t.cancel()
            
            try:
                await asyncio.wait_for(asyncio.gather(*[t for t in (guard_task, poll_task, push_task) if t], return_exceptions=True),
                                       timeout=JOIN_TIMEOUT_S)
            except Exception:
                pass

        print(f"ticks total: {total_ticks} | push: {push_ticks} | polled: {poll_ticks} | last price: {last_price}")

    finally:
        await shutdown(acc)

if __name__ == "__main__":
    asyncio.run(main())


# python -m examples.streaming_trade_tx


"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ FILE examples/streaming_ticks.py — 10-second tick stream (push + poll)       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Purpose                                                                      ║
║   Stream symbol ticks for a short window, preferring server **push** events  ║
║   and using periodic **polling** as a fallback. Automatically stops polling  ║
║   once push traffic is detected. Prints basic stats at the end.              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ What it does (main flow)                                                     ║
║   1) Connects and selects `SYMBOL` in Market Watch.                          ║
║   2) “Warm-up”: calls `symbol_is_synchronized` and a single                  ║
║      `symbol_info_tick` to nudge data flow.                                  ║
║   3) Starts two tasks:                                                       ║
║        • **consume_push**: `async for evt in acc.on_symbol_tick(...)`        ║
║          updates `last_price`, increments counters, signals first-push.      ║
║        • **consume_polling**: every `POLL_INTERVAL_S` calls                  ║
║          `symbol_info_tick` and updates counters/price.                      ║
║   4) **Guard** task: when first push arrives, cancels the polling task.      ║
║   5) After `RUN_SECONDS`, cancels everything, joins with a timeout, prints   ║
║      totals (`ticks total | push | polled | last price`) and shuts down.     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Key APIs                                                                     ║
║   • `await acc.symbol_select(SYMBOL, True)`                                  ║
║   • `await acc.symbol_is_synchronized(SYMBOL)`                               ║
║   • **Push stream**: `acc.on_symbol_tick(SYMBOL, None, cancel_evt)` → async  ║
║     generator yielding events (fields like `last`/`bid`/`ask`).              ║
║   • **Polling**: `await acc.symbol_info_tick(SYMBOL)`                        ║
║   • Session lifecycle: `connect()`, `shutdown()`                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Tunables (top of file)                                                       ║
║   • `RUN_SECONDS`     — total demo duration (default **10.0 s**).            ║
║   • `POLL_INTERVAL_S` — polling cadence (default **0.3 s**).                 ║
║   • `RPC_TIMEOUT_S`   — per-RPC timeout for warm-up/poll (default **1.0 s**).║
║   • `JOIN_TIMEOUT_S`  — graceful join timeout when stopping.                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Robustness & cancellation                                                    ║
║   • Uses `asyncio.Event` (`cancel_evt`) to stop the push generator.          ║
║   • Guard cancels polling immediately after first push.                      ║
║   • All cancellations are awaited with a bounded `JOIN_TIMEOUT_S`.           ║
║   • Timeouts/transport errors during polling are tolerated to keep the demo  ║
║     running.                                                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Output                                                                       ║
║   • “Symbol <SYMBOL> selected”                                               ║
║   • Optional “[poll] …” lines (until push shows up).                         ║
║   • Final stats: `ticks total: N | push: A | polled: B | last price: X`.     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Helpers / dependencies                                                       ║
║   • `apply_patch()` from `examples/common/pb2_shim.py` (pb2 compatibility).  ║
║   • `connect`, `shutdown`, `SYMBOL` from `examples/common/env.py`.           ║
║   • `title` from `examples/common/utils.py`.                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ How to run                                                                   ║
║   • `python -m examples.cli run streaming`  (or invoke the module directly). ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""