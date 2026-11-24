# Trailing Stop Orchestrator

> Automated trailing stop-loss management with intelligent auto-close. Opens test positions, watches them in real time, and moves the stop-loss closer to price to lock in profit — while cutting positions that stall or lose.

!!! warning "Demonstration only — not production ready"
    This orchestrator shows the strategy idea and the API calls behind it. A real deployment needs proper position sizing, slippage control, logging, monitoring, and extensive testing. Run it on a **demo account** only.

→ Source: [`examples/4_orchestrators/11_trailing_stop.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/11_trailing_stop.py)

---

## What it does

Keeps a protective stop-loss trailing behind a profitable position so that, once price reverses, you keep most of the gain instead of giving it all back. It also enforces two safety exits: a hard loss cap, and a "didn't work out in time" timeout.

It manages **only the positions it opened** (tracked by ticket), so it leaves the rest of your account untouched.

## How it works

1. Opens 2 test positions automatically (BUY + SELL, `0.01` lot each).
2. Streams live P&L for them via `stream_position_profits()` every second.
3. **Auto-close checks** (every update):
   - loss exceeds `max_loss_pips` → close immediately;
   - profit hasn't reached `activation_profit_pips` within `max_wait_minutes` → close.
4. **Trailing activation** (profit ≥ `activation_profit_pips`):
   - the stop starts following price at `trail_distance_pips` behind it;
   - the stop only ever moves in the favorable direction (it never loosens).
5. Prints a detailed status with countdown timers every 30 seconds.
6. Runs for `duration_minutes`, then prints a summary with total P&L.

## Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Typed facade used for streaming, quotes and `modify_order`. |
| `sugar` | `MT5Sugar` | — | High-level helpers (`buy_market`, `close_position`, `get_symbol_info`). |
| `trail_distance_pips` | `float` | `20.0` | Distance kept between price and the stop once trailing is active. |
| `activation_profit_pips` | `float` | `30.0` | Minimum profit before trailing switches on. |
| `update_interval_ms` | `int` | `1000` | How often the position stream reports (ms). |
| `symbols` | `list \| None` | `None` | Restrict to these symbols (`None` = all). |
| `dry_run` | `bool` | `False` | Log intended actions without modifying orders. |
| `max_wait_minutes` | `float` | `2.0` | Auto-close if trailing never activates within this time. |
| `max_loss_pips` | `float` | `50.0` | Auto-close once loss exceeds this. |
| `managed_tickets` | `list \| None` | `None` | Only manage these tickets (`None` = every position). |

`await start(duration_minutes=3.0, cancellation_event=None)` runs the loop.

## Example scenario

BUY EURUSD at 1.2000 — trail 20 pips, activation 30 pips, max loss 50 pips, max wait 2 min.

- **Profitable:** price → 1.2040 (+40p) activates trailing, SL set to 1.2020. Price → 1.2060 (+60p), SL → 1.2040. Price reverses to 1.2038 → SL at 1.2040 triggers = **+40 pips locked**.
- **No activation:** price oscillates ±10p for 2 minutes (never reaches +30p) → auto-close around break-even.
- **Big loss:** price drops to 1.1950 (−50p) → auto-close at the loss cap.

## Run it

```bash
cd examples
python main.py trailing      # or: trailingstop, or menu item [11]
```

## Minimal usage

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    orch = TrailingStopOrchestrator(
        service, sugar,
        trail_distance_pips=20.0,
        activation_profit_pips=30.0,
        max_loss_pips=50.0,
        max_wait_minutes=2.0,
    )
    await orch.start(duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## API methods used

- **MT5Service:** `stream_position_profits()` (core), `get_opened_orders()`, `modify_order()`, `get_symbol_tick()`.
- **MT5Sugar:** `buy_market()`, `sell_market()`, `close_position()`, `get_symbol_info()`.

## Notes

- Moves the stop **only** in the favorable direction — it locks profit, never widens risk.
- Pip size is derived per symbol: on 3/5-digit symbols 1 pip = 10 points.
- Streaming (1 s) keeps latency low; `Ctrl+C` triggers a graceful shutdown via the cancellation event.
- `dry_run=True` logs every intended modify/close without touching the account — use it to watch the logic safely.

## See also

- [Strategies — Master Overview](../Strategies.Master.Overview.md)
- [Position Scaler](PositionScaler.md) · [Risk Manager](RiskManager.md)
- [gRPC Streaming](../../All_Guides/GRPC_STREAM_MANAGEMENT.md) · [MT5Service](../../MT5Service/MT5Service.Overview.md) · [MT5Sugar](../../MT5Sugar/MT5Sugar.Master.Overview.md)
