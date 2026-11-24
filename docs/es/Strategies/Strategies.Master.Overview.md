# Strategies — Master Overview

> One page to orient fast: which orchestrators ship with the PyMT5 SDK, how to choose one, how to run it, and links to every strategy spec.

---

!!! warning "Educational & demonstration purpose only"
    Every orchestrator here is a **demonstration example** that showcases the PyMT5 API and serves as a template for building your own strategies. They are **not** production-ready trading systems: market analysis is simplified, risk controls are minimal, and execution logic is basic (no slippage handling, no adverse-condition detection).

    **Use demo accounts only.** Before anything live: understand every line, backtest, forward-test on demo for a long time, add real risk management, and add monitoring/alerting. Trading involves substantial risk of loss; you are responsible for your own decisions.

---

## The orchestrators

All five live in [`examples/4_orchestrators/`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators) and run from the interactive menu (`examples/main.py`).

| # | Strategy | What it does | Best for | Run |
| --- | --- | --- | --- | --- |
| 11 | **[Trailing Stop](Orchestrators/TrailingStop.md)** | Trails the stop-loss behind a winner; auto-closes stalled/losing trades. | Letting profit run safely | `python main.py trailing` |
| 12 | **[Position Scaler](Orchestrators/PositionScaler.md)** | Adds volume at levels — pyramiding or averaging — under a volume cap. | Scaling into a move | `python main.py scaler` |
| 13 | **[Grid Trader](Orchestrators/GridTrader.md)** | Pending-order grid that re-seeds levels as they fill. | Ranging / oscillating markets | `python main.py grid` |
| 14 | **[Risk Manager](Orchestrators/RiskManager.md)** | Account-wide guardian; closes everything when a limit is breached. | Protecting the account | `python main.py risk` |
| 15 | **[Portfolio Rebalancer](Orchestrators/PortfolioRebalancer.md)** | Keeps multi-symbol allocations at target weights. | Multi-symbol portfolios | `python main.py rebalancer` |

## Pick one by goal

- **Protect an open winner** → [Trailing Stop](Orchestrators/TrailingStop.md)
- **Build a bigger position step by step** → [Position Scaler](Orchestrators/PositionScaler.md)
- **Trade a sideways range automatically** → [Grid Trader](Orchestrators/GridTrader.md)
- **Enforce account-level risk limits** → [Risk Manager](Orchestrators/RiskManager.md)
- **Hold several symbols at fixed weights** → [Portfolio Rebalancer](Orchestrators/PortfolioRebalancer.md)

---

## How an orchestrator fits the SDK

Orchestrators sit on top of the three-layer API — they are plain Python classes that drive `MT5Service` and `MT5Sugar`:

```
ORCHESTRATORS  (examples/4_orchestrators/)
  Trailing Stop · Position Scaler · Grid Trader · Risk Manager · Portfolio Rebalancer
        │  async loop, streams position P&L, decides, trades
        ▼
MT5Sugar      high-level helpers  (buy_market, close_position, get_symbol_info, …)
        ▼
MT5Service    typed facade        (stream_position_profits, modify_order, place_order, …)
        ▼
MT5Account    low-level gRPC
```

Each orchestrator is **async**, monitors positions through a streaming method (mostly `stream_position_profits()`), and shuts down gracefully on `Ctrl+C` via a cancellation event. See [gRPC Streaming](../All_Guides/GRPC_STREAM_MANAGEMENT.md) for the streaming model.

## Common run pattern

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5

async def main():
    # 1) connect
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    # 2) configure + run an orchestrator
    orch = TrailingStopOrchestrator(service, sugar, trail_distance_pips=20.0)
    await orch.start(duration_minutes=3.0)

    # 3) disconnect
    await account.disconnect()

asyncio.run(main())
```

The quickest way to try any of them is the menu:

```bash
cd examples
python main.py              # interactive menu
python main.py trailing     # or run one directly: trailing / scaler / grid / risk / rebalancer
```

## Shared behavior

- **Demo-safe:** each demo opens its own small test positions and closes **only those** on exit.
- **Pips vs points:** pip size is derived per symbol (on 3/5-digit symbols 1 pip = 10 points).
- **Dry run:** most orchestrators accept `dry_run=True` to log intended trades without touching the account.
- **Graceful stop:** `Ctrl+C` cancels the stream and cleans up pending orders/positions.

---

## Related documentation

- [MT5Account — Master Overview](../MT5Account/MT5Account.Master.Overview.md) — low-level gRPC API.
- [MT5Service](../MT5Service/MT5Service.Overview.md) — typed wrapper methods.
- [MT5Sugar — Master Overview](../MT5Sugar/MT5Sugar.Master.Overview.md) — high-level helpers.
- [gRPC Streaming](../All_Guides/GRPC_STREAM_MANAGEMENT.md) — subscriptions and cancellation.
- [Sync vs Async](../All_Guides/SYNC_VS_ASYNC.md) — async patterns.
- [UserCode Sandbox](../All_Guides/USERCODE_SANDBOX_GUIDE.md) — write your own strategy.

## Quick jump

- [Trailing Stop](Orchestrators/TrailingStop.md)
- [Position Scaler](Orchestrators/PositionScaler.md)
- [Grid Trader](Orchestrators/GridTrader.md)
- [Risk Manager](Orchestrators/RiskManager.md)
- [Portfolio Rebalancer](Orchestrators/PortfolioRebalancer.md)
