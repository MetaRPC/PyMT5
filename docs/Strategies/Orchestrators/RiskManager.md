# Risk Manager Orchestrator

> A real-time account guardian: it watches account health and **closes everything** the moment any risk limit is breached — drawdown, daily loss, margin level or position count.

!!! warning "Demonstration only — not production ready"
    This orchestrator shows the strategy idea and the API calls behind it. A real deployment needs comprehensive risk management, error handling, logging, monitoring, and extensive testing. Run it on a **demo account** only.

→ Source: [`examples/4_orchestrators/14_risk_manager.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/14_risk_manager.py)

---

## What it does

Captures the starting balance, then monitors **all** open positions in real time. If any configured threshold is crossed, it closes every position at once to protect the account from runaway drawdown, margin calls and overleveraging. Unlike the other orchestrators, it takes an account-wide view rather than managing one strategy.

## How it works

1. Opens 2 test positions (BUY + SELL, `0.01` lot) for the demo.
2. Records the initial account balance.
3. Streams P&L for all positions via `stream_position_profits()`.
4. Every ~10 seconds prints: current drawdown, daily P&L %, margin level, open-position count, total P&L.
5. **Automatic protection** — closes all positions if any limit is breached:
   - drawdown > `max_drawdown_percent`;
   - daily loss > `max_daily_loss_percent`;
   - margin level < `min_margin_level`;
   - open positions > `max_positions`.
6. Logs every violation and closure, then prints a final risk report. Test positions are cleaned up on exit.

## Parameters

The constructor takes `service` and an optional `RiskLimits`:

```python
RiskManagerOrchestrator(service, limits: RiskLimits | None = None)
```

`RiskLimits` fields:

| Field | Type | Default | Meaning |
| --- | --- | --- | --- |
| `max_drawdown_percent` | `float` | `10.0` | Close all if equity drops this far from the start balance. |
| `max_daily_loss_percent` | `float` | `5.0` | Close all if today's loss exceeds this. |
| `min_margin_level` | `float` | `150.0` | Close all if margin level falls below this (%). |
| `max_positions` | `int` | `10` | Close all if open positions exceed this. |
| `max_risk_per_trade_percent` | `float` | `2.0` | Reserved for future per-trade sizing. |

`await start(duration_minutes=3.0)` runs the monitor. (The menu entry calls the module's `run_risk_manager_example()` wrapper.)

## Example scenarios

- **Drawdown:** start $10,000, cap 10%. Equity → $8,900 (−11%) → close all 3 positions.
- **Daily loss:** cap 5% ($500). Today −$550 (−5.5%) → close all.
- **Margin call prevention:** margin level 140% < 150% → close to free margin.
- **Position limit:** 12 open > 10 → close all.

## Run it

```bash
cd examples
python main.py risk          # or: riskmanager, or menu item [14]
```

## Minimal usage

```python
import asyncio
from pymt5.mt5_service import MT5Service
from demo_helpers import load_settings, create_and_connect_mt5
# RiskLimits lives in the orchestrator module (14_risk_manager.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)

    limits = RiskLimits(
        max_drawdown_percent=15.0,   # more room
        max_daily_loss_percent=3.0,  # stricter daily cap
        min_margin_level=200.0,      # higher margin buffer
        max_positions=5,
    )
    orch = RiskManagerOrchestrator(service, limits=limits)
    await orch.start(duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## API methods used

- **MT5Service:** `stream_position_profits()` (core), `get_opened_orders()`, `get_account_summary()`.
- **MT5Sugar:** `close_position()` (bulk close on breach), `get_account_info()`.

## Notes

- This is account-wide protection — it acts on **every** open position, not just ones it opened (except the demo cleanup of its own test trades).
- Thresholds are checked on every stream update, so a breach triggers a near-immediate close.
- Pair it with any other orchestrator in your own runner to add a safety net.

## See also

- [Strategies — Master Overview](../Strategies.Master.Overview.md)
- [Trailing Stop](TrailingStop.md) · [Position Scaler](PositionScaler.md)
- [MT5Service](../../MT5Service/MT5Service.Overview.md) · [MT5Sugar](../../MT5Sugar/MT5Sugar.Master.Overview.md)
