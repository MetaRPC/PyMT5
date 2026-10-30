# Grid Trading Orchestrator

> Places a network of pending stop orders at fixed price steps around the current price, then re-seeds a level whenever its order triggers and closes — keeping the grid intact for the whole run.

!!! warning "Demonstration only — not production ready"
    This orchestrator shows the strategy idea and the API calls behind it. A real deployment needs proper position sizing, slippage control, logging, monitoring, and extensive testing. Run it on a **demo account** only.

→ Source: [`examples/4_orchestrators/13_grid_trader.py`](https://github.com/MetaRPC/PyMT5/blob/main/examples/4_orchestrators/13_grid_trader.py)

---

## What it does

Builds a grid of pending orders at a fixed pip step above and below a center price, each with a take-profit set to the next level. As triggered orders close at their TP, it places a fresh order back at that level so the grid keeps working — ideal for ranging, oscillating markets.

## How it works

1. Reads the current price and computes grid levels around it (the center).
2. Places pending orders — `BUY_STOP` above and `SELL_STOP` below for a hedging grid.
3. Polls order/position tickets via `stream_opened_tickets()`.
4. When a level's order triggers and closes by TP, places a new order back at that level.
5. Maintains the structure for `duration_minutes`, then cancels all pending orders on shutdown.

### Two modes

- **Hedging** (bi-directional): `BUY_STOP` above + `SELL_STOP` below — profits from oscillations either way.
- **Directional** (one-way): only `BUY_STOP` or only `SELL_STOP` — follows a clear trend, lower activity.

## Parameters

| Parameter | Type | Default | Meaning |
| --- | --- | --- | --- |
| `service` | `MT5Service` | — | Order placement, ticket stream, quotes. |
| `sugar` | `MT5Sugar` | — | `get_symbol_info()` for point/digits. |
| `grid_type` | `GridType` | `HEDGING` | `HEDGING` or `DIRECTIONAL`. |
| `grid_step_pips` | `float` | `20.0` | Distance between levels. |
| `levels_above` | `int` | `3` | Number of levels above center. |
| `levels_below` | `int` | `3` | Number of levels below center. |
| `volume_per_level` | `float` | `0.01` | Volume for each order. |
| `take_profit_pips` | `float \| None` | `None` | TP distance (`None` → use `grid_step_pips`). |
| `update_interval_ms` | `int` | `1000` | Polling interval (ms). |
| `dry_run` | `bool` | `False` | Simulate without placing real orders. |

`await start(symbol, duration_minutes=3.0, cancellation_event=None)` runs the loop.

## Example grid

EURUSD, center 1.2000, step 20 pips, 3 above / 3 below (hedging):

```
1.2060 → BUY_STOP  (TP 1.2080)
1.2040 → BUY_STOP  (TP 1.2060)
1.2020 → BUY_STOP  (TP 1.2040)
1.2000 → CENTER
1.1980 → SELL_STOP (TP 1.1960)
1.1960 → SELL_STOP (TP 1.1940)
1.1940 → SELL_STOP (TP 1.1920)
```

When the BUY at 1.2020 triggers and closes at its TP (1.2040), a new `BUY_STOP` is placed back at 1.2020.

## Run it

```bash
cd examples
python main.py grid          # or: gridtrading, or menu item [13]
```

## Minimal usage

```python
import asyncio
from pymt5.mt5_service import MT5Service
from pymt5.mt5_sugar import MT5Sugar
from demo_helpers import load_settings, create_and_connect_mt5
# GridType lives in the orchestrator module (13_grid_trader.py)

async def main():
    config = load_settings()
    account = await create_and_connect_mt5(config)
    service = MT5Service(account)
    sugar = MT5Sugar(service, default_symbol=config["test_symbol"])

    orch = GridTradingOrchestrator(
        service, sugar,
        grid_type=GridType.HEDGING,
        grid_step_pips=20.0,
        levels_above=3,
        levels_below=3,
        volume_per_level=0.01,
    )
    await orch.start(symbol=config["test_symbol"], duration_minutes=3.0)

    await account.disconnect()

asyncio.run(main())
```

## API methods used

- **MT5Service:** `stream_opened_tickets()` (core, polling), `place_order()`, `close_order()`, `get_symbol_tick()`.
- **MT5Sugar:** `get_symbol_info()`.

## Notes

- Works best in **ranging** markets; a strong one-way trend will keep hitting stops on the wrong side (use `DIRECTIONAL` then).
- Uses `TMT5_ORDER_TYPE_BUY_STOP` / `TMT5_ORDER_TYPE_SELL_STOP` with `OrderSendRequest`; pending orders are cancelled via `close_order()`.
- Ticket tracking is **polling-based** (`stream_opened_tickets()`), not the event-based `stream_trade_updates()`.
- Graceful shutdown cancels every pending order the grid created.

## See also

- [Strategies — Master Overview](../Strategies.Master.Overview.md)
- [Trailing Stop](TrailingStop.md) · [Portfolio Rebalancer](PortfolioRebalancer.md)
- [gRPC Streaming](../../All_Guides/GRPC_STREAM_MANAGEMENT.md) · [MT5Service](../../MT5Service/MT5Service.Overview.md)
