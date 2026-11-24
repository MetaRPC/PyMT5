# Async in PyMT5 (and how to go sync yourself)

> **PyMT5 is async-only.** Every method on `MT5Account`, `MT5Service` and `MT5Sugar` is a coroutine you `await` — there are no synchronous variants. This page explains *why*, and shows how to wrap the async API in a synchronous interface yourself if your project needs one.

---

## Why async?

The SDK talks to the terminal over **gRPC**, and the workload is almost entirely waiting on the network. `asyncio` fits that shape:

- **Streaming is continuous.** Ticks, trade events and position-profit updates arrive as a never-ending stream. An async generator (`async for`) lets a single thread handle that stream and stay responsive between events — a blocking call per update would freeze the program.
- **Many calls overlap.** Quotes, orders and account reads across several symbols can be issued concurrently with `asyncio.gather` instead of one-after-another, so their round-trips overlap.
- **No thread-per-connection.** One event loop multiplexes thousands of in-flight calls without a thread pool, which is what you want for a bot or a service.
- **It matches the transport.** `grpc.aio` (async gRPC) is what the SDK is built on, so there is a single, consistent execution model top to bottom.

So the SDK commits to one model — async — rather than shipping two parallel APIs.

```python
summary = await service.get_account_summary()   # ✅ await it
summary = service.get_account_summary()          # ❌ this is a coroutine object, not data
```

### Running async from a normal script

You don't need a framework — wrap your entry coroutine in `asyncio.run(...)`:

```python
import asyncio
from pymt5.mt5_service import MT5Service
from demo_helpers import load_settings, create_and_connect_mt5

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)

    summary = await service.get_account_summary()
    print(f"Balance: {summary.balance}, Equity: {summary.equity}")

    await account.disconnect()

asyncio.run(main())
```

In Jupyter the loop is already running, so you `await` directly in a cell.

---

## Building a synchronous wrapper yourself

Sometimes you *must* call from synchronous code — a legacy codebase, a sync web framework, a simple REPL script, or a library that has to expose a blocking API. You can wrap PyMT5 yourself; the SDK doesn't stop you.

### ⚠️ Why not just `asyncio.run()` per call

`asyncio.run()` creates a **new event loop** every time and closes it afterwards. The SDK's gRPC channel is bound to the loop it was created on, so you **cannot** connect under one `asyncio.run()` and then reuse that `account` under a later `asyncio.run()` — the second call runs on a different loop and the channel breaks.

`asyncio.run()` is therefore fine only for a **single self-contained** coroutine that connects, works and disconnects all in one go:

```python
import asyncio
from pymt5.mt5_service import MT5Service
from demo_helpers import load_settings, create_and_connect_mt5

def get_balance_once() -> float:
    async def _run():
        account = await create_and_connect_mt5(load_settings())
        try:
            return (await MT5Service(account).get_account_summary()).balance
        finally:
            await account.disconnect()
    return asyncio.run(_run())   # connect + read + disconnect, one shot

balance = get_balance_once()
```

### ✅ The reusable pattern: a persistent loop in a background thread

To connect once and then make **many** synchronous calls, run a single event loop in a daemon thread and submit coroutines to it with `run_coroutine_threadsafe`. Everything — including the connect — runs on that one loop, so the channel stays valid:

```python
import asyncio
import threading
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5

class SyncMT5:
    """Drive the async PyMT5 API from synchronous code via one background loop."""

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def run(self, coro):
        """Submit a coroutine to the background loop and block for its result."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result()

    def close(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()


# --- usage: looks synchronous, SDK stays async underneath ---
mt5 = SyncMT5()

config = load_settings()
account = mt5.run(create_and_connect_mt5(config))   # connect ON the background loop
service = MT5Service(account)
sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

summary = mt5.run(service.get_account_summary())     # blocking call
print(f"Balance: {summary.balance}")

ticket = mt5.run(sugar.buy_market("EURUSD", 0.01))   # another blocking call
print(f"Opened #{ticket}")

mt5.run(account.disconnect())
mt5.close()
```

Each `mt5.run(...)` blocks until the coroutine finishes and returns its value (or re-raises its exception), so the rest of your code can be plain synchronous.

### When it's worth it — and when it isn't

- **Worth it:** a one-off script, glue code inside a synchronous app, or exposing a small blocking helper to colleagues who don't use `asyncio`.
- **Skip it for streaming.** Streams are `async for` generators; forcing them through a sync facade means blocking the caller on every event, which defeats the point. Consume streams in async code.
- **Skip it for performance-sensitive concurrency.** The win of async is overlapping calls; a sync wrapper serializes them again. If you need throughput, write async.

---

## Summary

- The SDK is **async-only** — `await` everything; there are no sync methods to call.
- Run it from a script with **`asyncio.run(main())`**; `await` directly inside an async app or Jupyter.
- Need a blocking interface? Build it yourself: `asyncio.run()` for a single self-contained call, or a **persistent background-loop wrapper** (`run_coroutine_threadsafe`) to connect once and make many sync calls.
- Keep **streaming and high-concurrency work in async** — that's what the model is for.

## See also

- [Getting Started](GETTING_STARTED.md) — install and first connection.
- [gRPC Streaming](GRPC_STREAM_MANAGEMENT.md) — subscriptions, cancellation, reconnection.
- [Your First Project](Your_First_Project.md) — a complete runnable script.
