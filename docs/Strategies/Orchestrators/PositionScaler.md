# Position Scaler Orchestrator

> Adds volume to an existing position at predefined price levels — either **pyramiding** into a winner or **averaging** into a loser — while respecting a hard total-volume cap.

!!! warning "Demonstration only — not production ready"
    This orchestrator shows the strategy idea and the API calls behind it. A real deployment needs proper position sizing, slippage control, logging, monitoring, and extensive testing. Run it on a **demo account** only.

→ Source: [`examples/4_orchestrators/12_position_scaler.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/12_position_scaler.py)

---

## What it does

Scales a single base position in steps. Each time price reaches the next configured level, it adds a slice of volume and records that the level has fired (so it never doubles up on the same level). Total exposure is always clamped to `max_total_volume`.

## How it works

1. Picks a base position (opens test positions if none is passed) and streams its P&L via `stream_position_profits()`.
2. On each update, measures profit/loss in pips against the configured `scale_levels_pips`.
3. When a level is reached, adds `scale_volume_percent` of the base volume — as long as the new total stays under `max_total_volume` and margin allows.
4. Each level triggers **once**. A live progress bar and periodic status show total volume and scale count.

### Two modes

- **Pyramiding** (trend-following): adds to **profitable** positions at `+30/+60/+90` pips. Lower risk, needs a real trend.
- **Averaging** (mean-reversion): adds to **losing** positions at `−30/−60/−90` pips. Higher risk — use strict limits.

## Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Streaming, quotes, account summary. |
| `sugar` | `MT5Sugar` | — | `buy_market`/`sell_market`, margin & symbol helpers, `close_position`. |
| `scale_type` | `ScaleType` | `PYRAMIDING` | `PYRAMIDING` or `AVERAGING`. |
| `scale_levels_pips` | `list[float]` | `[30, 60, 90]` | Pip levels at which to add volume. |
| `scale_volume_percent` | `float` | `50.0` | Percent of base volume added per level. |
| `max_total_volume` | `float` | `0.50` | Hard cap on combined volume (lots). |
| `update_interval_ms` | `int` | `1000` | Position stream interval (ms). |
| `dry_run` | `bool` | `False` | Simulate adds without executing. |

`await start(symbol, base_ticket=None, duration_minutes=3.0, cancellation_event=None)` runs the loop. If `base_ticket` is omitted the demo opens its own test positions.

## Example scenario (pyramiding)

BUY EURUSD at 1.2000, base volume `0.10`, levels `+30/+60/+90`, add 50% (`0.05`) per level, cap `0.30`:

- price → 1.2030 (+30p) → add 0.05 → total 0.15
- price → 1.2060 (+60p) → add 0.05 → total 0.20
- price → 1.2090 (+90p) → add 0.05 → total 0.25

## Run it

```bash
cd examples
python main.py scaler        # or: positionscaler, or menu item [12]
```

## Minimal usage

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5
# ScaleType lives in the orchestrator module (12_position_scaler.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    orch = PositionScalerOrchestrator(
        service, sugar,
        scale_type=ScaleType.PYRAMIDING,
        scale_levels_pips=[30.0, 60.0, 90.0],
        scale_volume_percent=50.0,
        max_total_volume=0.30,
    )
    await orch.start(symbol=config["test_symbol"], duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## API methods used

- **MT5Service:** `stream_position_profits()` (core), `get_opened_orders()`, `get_symbol_tick()`, `get_account_summary()`.
- **MT5Sugar:** `buy_market()` / `sell_market()`, `calculate_required_margin()`, `get_account_info()`, `get_symbol_info()`, `close_position()`.

## Notes

- Always respects `max_total_volume`, and checks free margin before adding.
- **Averaging** adds to losers — it is the higher-risk mode; keep `max_total_volume` tight.
- The demo opens 2 small test positions, uses the first as base and the second as backup, and closes **only** its own test positions on exit.

## See also

- [Strategies — Master Overview](../Strategies.Master.Overview.md)
- [Trailing Stop](TrailingStop.md) · [Risk Manager](RiskManager.md)
- [MT5Service](../../MT5Service/MT5Service.Overview.md) · [MT5Sugar](../../MT5Sugar/MT5Sugar.Master.Overview.md)
