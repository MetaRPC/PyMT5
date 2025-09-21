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
    Example: Tick streaming for 10s — push first, polling as backup
    ===============================================================

    | Section | What happens | Why / Notes |
    |---|---|---|
    | Connect | `acc = await connect()` | Opens async session; must be closed with `shutdown()`. |
    | Heading | `title("Streaming: ticks for 10 seconds")` | Cosmetic header. |
    | Ensure symbol | `symbol_select(SYMBOL, True)` | Puts symbol into Market Watch to receive data. |
    | Warm-up | `symbol_is_synchronized(SYMBOL)` + `symbol_info_tick(SYMBOL)` | Gentle probe to wake feeds; all calls are timeout-guarded. |
    | Start push | `on_symbol_tick(SYMBOL, None, cancel_evt)` → async generator | Primary, low-latency tick source; sets `got_first_push` on the first event. |
    | Start polling | Loop of `symbol_info_tick(SYMBOL)` + `sleep(POLL_INTERVAL_S)` | Fallback while push is not yet delivering. |
    | Auto-switch | `stop_poll_on_first_push()` cancels polling when push starts | Saves bandwidth/CPU once streaming is confirmed. |
    | Timed run | Sleep `RUN_SECONDS` then cancel tasks with join timeout | Ensures graceful stop without hanging forever. |
    | Summary | Print totals and the last seen price | `ticks total`, `push`, `polled`, `last price`. |

    RPCs used
    ---------
    - `symbol_select(symbol: str, select: bool)` → ensure symbol readiness
    - `symbol_is_synchronized(symbol: str) -> bool` → quick health/sync check
    - `symbol_info_tick(symbol: str)` → snapshot tick (poll)
    - `on_symbol_tick(symbol: str, deadline=None, cancellation_event=None)` → async generator (push)

    Concurrency & cancellation
    --------------------------
    - Tasks:
      1) `consume_push()` — iterates async-gen, counts ticks, updates `last_price`, signals `got_first_push`.
      2) `consume_polling()` — polls with `POLL_INTERVAL_S`, guarded by `RPC_TIMEOUT_S`.
      3) `stop_poll_on_first_push()` — waits `got_first_push`, cancels polling, waits up to `JOIN_TIMEOUT_S`.
    - Global `cancel_evt` requests a cooperative stop for the push generator.
    - Final teardown cancels all tasks and `gather`s them with a join timeout so the demo never hangs.

    Parameters (tuning knobs)
    -------------------------
    - `RUN_SECONDS = 10.0` — total demo duration.
    - `POLL_INTERVAL_S = 0.3` — polling cadence (e.g., 0.2–1.0 s).
    - `RPC_TIMEOUT_S = 1.0` — per-RPC client-side timeout for warm-up/poll calls.
    - `JOIN_TIMEOUT_S = 2.0` — how long we wait for tasks to finish during shutdown.

    Price extraction
    ----------------
    - For both push events and poll snapshots we take first available of:
      `last` → `bid` → `ask`. If numeric, it becomes `last_price`.

    Typical output
    --------------
    Streaming: ticks for 10 seconds
    Symbol EURUSD selected
    Push stream engaged → stopping polling.
    ticks total: 42 | push: 37 | polled: 5 | last price: 1.08460

    Notes & edge cases
    ------------------
    - If you see only polling (or zero ticks): market closed, symbol not streamed, or provider throttling.
    - Increase `RUN_SECONDS` for quiet markets. Lower `POLL_INTERVAL_S` carefully (provider limits may apply).
    - Prefer client-side timeouts/cancellation (as in this example) if server time can be skewed.

    How to run
    ----------
    From project root:
      `python -m examples.streaming_ticks_10s`
    Or via CLI (if present):
      `python -m examples.cli run streaming_ticks_10s`
    """