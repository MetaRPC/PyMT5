"""Read-only gRPC quote stream, bounded even when the market is quiet.

Run: python examples/stream_quotes.py --symbol EURUSD --seconds 30 --events 20
Use your broker's exact symbol; hosted connection usage is billed.
"""
import argparse
import asyncio
import os

from read_account import create_account


async def stream_quotes(symbol="EURUSD", seconds=30, events=20, account_factory=None):
    if not symbol.strip() or not 0 < seconds <= 300 or not 1 <= events <= 1000:
        raise ValueError("Supply a symbol, up to 300 seconds and 1–1000 events")
    account = create_account(account_factory)
    stop = asyncio.Event()
    stream = None
    count = 0
    try:
        await account.connect_by_server_name(os.environ["MT5_SERVER"], timeout_seconds=30)
        stream = account.on_symbol_tick(symbols=[symbol], cancellation_event=stop)

        async def consume():
            nonlocal count
            async for data in stream:
                tick = data.symbol_tick
                print(f"{tick.symbol}: bid={tick.bid} ask={tick.ask}")
                count += 1
                if count >= events:
                    break

        try:
            await asyncio.wait_for(consume(), timeout=seconds)
        except asyncio.TimeoutError:
            print(f"Time limit reached; received {count} events. A quiet stream is not proof of failure.")
        return count
    finally:
        stop.set()
        try:
            if stream is not None:
                await asyncio.wait_for(stream.aclose(), timeout=5)
        finally:
            await asyncio.wait_for(account.disconnect(), timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--events", type=int, default=20)
    args = parser.parse_args()
    try:
        asyncio.run(stream_quotes(args.symbol, args.seconds, args.events))
    except (Exception, KeyboardInterrupt) as exc:
        print(f"Stream stopped ({type(exc).__name__}). Check terminal cleanup in the portal.")
        raise SystemExit(1) from None
