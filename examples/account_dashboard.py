"""Bounded, read-only terminal dashboard. No web server or order submission.

Uses the same four private environment variables as read_account.py.
Run: python examples/account_dashboard.py --samples 6 --interval 5
"""
import argparse
import asyncio
import os
from datetime import datetime, timezone

from read_account import create_account


async def dashboard(samples=6, interval=5, account_factory=None):
    if not 1 <= samples <= 60 or not 1 <= interval <= 60:
        raise ValueError("Use 1–60 samples and a 1–60 second interval")
    account = create_account(account_factory)
    try:
        await account.connect_by_server_name(os.environ["MT5_SERVER"], timeout_seconds=30)
        print("UTC time                  Balance         Equity    Free margin (account currency)")
        for index in range(samples):
            summary = await asyncio.wait_for(account.account_summary(), timeout=15)
            print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} "
                  f"{summary.account_balance:14.2f} {summary.account_equity:14.2f} "
                  f"{summary.account_margin_free:14.2f}")
            if index + 1 < samples:
                await asyncio.sleep(interval)
    finally:
        await asyncio.wait_for(account.disconnect(), timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=6)
    parser.add_argument("--interval", type=int, default=5)
    args = parser.parse_args()
    try:
        asyncio.run(dashboard(args.samples, args.interval))
    except (Exception, KeyboardInterrupt) as exc:
        print(f"Dashboard stopped ({type(exc).__name__}). Check terminal cleanup in the portal.")
        raise SystemExit(1) from None
