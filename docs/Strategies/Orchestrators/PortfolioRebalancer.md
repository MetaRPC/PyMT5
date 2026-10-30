# Portfolio Rebalancer Orchestrator

> Keeps a multi-symbol portfolio at its target weights. It sizes positions from account equity, watches each symbol's share, and trades to pull allocations back whenever they drift past a threshold.

!!! warning "Demonstration only — not production ready"
    This orchestrator shows the strategy idea and the API calls behind it. A real deployment needs proper position sizing, slippage control, logging, monitoring, and extensive testing. Run it on a **demo account** only.

→ Source: [`examples/4_orchestrators/15_portfolio_rebalancer.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/15_portfolio_rebalancer.py)

---

## What it does

Maintains a target allocation across several symbols (e.g. EURUSD 40% / GBPUSD 30% / USDJPY 30%). It computes the right volume for each target from current equity, opens the positions, then monitors each symbol's share of equity. When a symbol drifts beyond `rebalance_threshold`, it trades to restore the targets.

## How it works

1. Reads account equity and computes per-symbol volumes from the target percentages.
   *(e.g. equity $9,600 → EURUSD 40% ≈ 0.64 lot, GBPUSD 30% ≈ 0.48 lot)*
2. Opens the portfolio positions (one per target).
3. Streams P&L via `stream_position_profits()` and recomputes each symbol's current share.
4. When any symbol's deviation exceeds `rebalance_threshold`, triggers a rebalance — reduce the overweight symbols, add to the underweight ones.
5. Runs for `duration_minutes`, then closes all portfolio positions on exit.

## Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Streaming and quotes. |
| `sugar` | `MT5Sugar` | — | Account info, positions, symbol info, open/close. |
| `targets` | `list[PortfolioTarget]` | — | Target allocation (see below). |
| `rebalance_threshold` | `float` | `5.0` | Minimum deviation % that triggers a rebalance. |
| `check_interval_ms` | `int` | `5000` | How often to re-check allocation (ms). |
| `dry_run` | `bool` | `False` | Log rebalances without executing. |

`PortfolioTarget` fields: `symbol: str`, `target_percent: float` (0–100), `direction: str` (`"BUY"` or `"SELL"`).

`await start(duration_minutes=3.0, cancellation_event=None)` runs the loop.

## Example scenario

Target EURUSD 40% / GBPUSD 30% / USDJPY 30%. After price moves: EURUSD drifts to 50% (+10%), GBPUSD and USDJPY to 25% each (−5%). Rebalance → reduce EURUSD, add to GBPUSD and USDJPY → back to 40/30/30.

## Run it

```bash
cd examples
python main.py rebalancer    # or: portfolio, or menu item [15]
```

## Minimal usage

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5
# PortfolioTarget lives in the orchestrator module (15_portfolio_rebalancer.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    targets = [
        PortfolioTarget("EURUSD", 40.0, "BUY"),
        PortfolioTarget("GBPUSD", 30.0, "BUY"),
        PortfolioTarget("USDJPY", 30.0, "BUY"),
    ]
    orch = PortfolioRebalancerOrchestrator(
        service, sugar,
        targets=targets,
        rebalance_threshold=5.0,
    )
    await orch.start(duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## API methods used

- **MT5Service:** `stream_position_profits()`, `get_symbol_tick()`.
- **MT5Sugar:** `get_account_info()`, `get_open_positions()`, `get_symbol_info()`, `buy_market()` / `sell_market()`, `close_position()`.

## Notes

- Volumes are computed from equity and the target percentages, so demo positions can be fairly large (often 0.5–1.0 lot each); a safety cap of 5.0 lots applies.
- The demo is **DEMO-compatible**: it uses a simple margin estimate (≈ $6,000 per lot) and skips `order_check()` / `order_calc_margin()`.
- All portfolio positions are closed automatically when the run ends.

## See also

- [Strategies — Master Overview](../Strategies.Master.Overview.md)
- [Grid Trader](GridTrader.md) · [Risk Manager](RiskManager.md)
- [MT5Service](../../MT5Service/MT5Service.Overview.md) · [MT5Sugar](../../MT5Sugar/MT5Sugar.Master.Overview.md)
