# Low‑Level Walkthrough — Step_number_(one)
**Covers:** Steps **1–8** (connect, account summary/info, symbols basics & params, opened orders, positions, order history).  
**Audience:** Beginners who want to understand raw MT5 gRPC calls without wrappers.

> This part focuses on *read-only* and safe operations. No trading actions here.

---

## Helpers used in this part
These helpers are referenced by the steps below. Keep them local to the example for copy‑paste, or later move to `examples/common`.

- **Env and connection diagnostics** — see:  
  - [`docs/Examples/Common/env.md`](docs/Examples/Common/env.md)  
  - [`docs/Examples/Common/diag_connect.md`](docs/Examples/Common/diag_connect.md)
- **Getting started & base API layout** — see:  
  - [`docs/MT5Account/Getting_Started.md`](docs/MT5Account/Getting_Started.md)  
  - [`docs/MT5Account/BASE.md`](docs/MT5Account/BASE.md)  
  - [`docs/MT5Account/Under_the_Hood.md`](docs/MT5Account/Under_the_Hood.md)

---

## Prerequisites
- Python **3.13.x** in a virtual environment.
- gRPC endpoint reachable from your network.
- Valid MT5 credentials.

### Environment variables used here
| Name | Default | Purpose |
|---|---:|---|
| `GRPC_SERVER` | `mt5.mrpc.pro:443` | gRPC backend endpoint |
| `MT5_LOGIN` | `0` | MT5 login |
| `MT5_PASSWORD` | `""` | MT5 password |
| `MT5_SERVER` | `""` | MT5 server name (for ConnectEx) |
| `MT5_SYMBOL` | `EURUSD` | Base symbol for examples |
| `TIMEOUT_SECONDS` | `90` | Deadline for most RPC calls |

> No trading flags required in this part (`RUN_TRADING` not used).

---

## How to run this part
PowerShell (Windows):
```powershell
$env:MT5_LOGIN=1234567
$env:MT5_PASSWORD='pass'
$env:MT5_SERVER='MetaQuotes-Demo'
$env:GRPC_SERVER='mt5.mrpc.pro:443'
python - <<'PY'
import asyncio
# Ensure the shim is applied before any pb2 usage
from examples.common.pb2_shim import apply_patch  # comments in English only
apply_patch()

from examples.base_example.lowlevel_walkthrough import main  # entrypoint for the whole walkthrough
asyncio.run(main(only_steps=range(1,9)))  # run steps 1..8
PY
```

Bash:
```bash
export MT5_LOGIN=1234567
export MT5_PASSWORD='pass'
export MT5_SERVER="MetaQuotes-Demo"
export GRPC_SERVER="mt5.mrpc.pro:443"
python - <<'PY'
import asyncio
from examples.common.pb2_shim import apply_patch  # comments in English only
apply_patch()

from examples.base_example.lowlevel_walkthrough import main
asyncio.run(main(only_steps=range(1,9)))  # 1..8
PY
```

---

## Steps in detail (with docs)

### Step 1 — Account Summary
**Goal:** connect using `server_name` (ConnectEx) and print account metrics (equity, balance, margin, free, free_ratio, drawdown, server_time).  
**Docs:** [`Account Summary`](docs/MT5Account/Account_Information/account_summary.md),  
[`Getting Started`](docs/MT5Account/Getting_Started.md)

---

### Step 2 — Account Info (pb2)
**Goal:** demonstrate direct `AccountInfo*Request` calls and safe field extraction.  
**Docs:** [`Account Info (double)`](docs/MT5Account/Account_Information/account_info_double.md),  
[`Account Info (integer)`](docs/MT5Account/Account_Information/account_info_integer.md),  
[`Account Info (string)`](docs/MT5Account/Account_Information/account_info_string.md),  
[`Account Information Overview`](docs/MT5Account/Account_Information/Account_Information_Overview.md)

---

### Step 3 — Symbols: basics
**Goal:** ensure symbol availability and read key attributes.  
**Calls used:** `symbol_exist`, `symbol_select`, `symbols_total`, `symbol_info_*`, `symbol_info_tick`, `tick_value_with_size`, `symbol_is_synchronized`.  
**Docs:** [`symbol_exist`](docs/MT5Account/Symbols_and_Market/symbol_exist.md),  
[`symbol_select`](docs/MT5Account/Symbols_and_Market/symbol_select.md),  
[`symbols_total`](docs/MT5Account/Symbols_and_Market/symbols_total.md),  
[`symbol_info_double`](docs/MT5Account/Symbols_and_Market/symbol_info_double.md),  
[`symbol_info_integer`](docs/MT5Account/Symbols_and_Market/symbol_info_integer.md),  
[`symbol_info_string`](docs/MT5Account/Symbols_and_Market/symbol_info_string.md),  
[`symbol_info_tick`](docs/MT5Account/Symbols_and_Market/symbol_info_tick.md),  
[`tick_value_with_size`](docs/MT5Account/Symbols_and_Market/tick_value_with_size.md),  
[`symbol_is_synchronized`](docs/MT5Account/Symbols_and_Market/symbol_is_synchronized.md)

> Extras used later: [`symbol_info_session_quote`](docs/MT5Account/Symbols_and_Market/symbol_info_session_quote.md), [`symbol_info_session_trade`](docs/MT5Account/Symbols_and_Market/symbol_info_session_trade.md), [`symbol_info_margin_rate`](docs/MT5Account/Symbols_and_Market/symbol_info_margin_rate.md), [`symbol_name`](docs/MT5Account/Symbols_and_Market/symbol_name.md).

---

### Step 4 — SymbolParamsMany (batch)
**Goal:** read a compact set of parameters for one/many symbols via `SymbolParamsManyRequest` → `SymbolParameters` (spread, tick size/value, lot step, volume limits, etc.).  
**Docs:** [`symbol_params_many`](docs/MT5Account/Symbols_and_Market/symbol_params_many.md)

---

### Step 5 — Opened Orders (snapshot)
**Goal:** print active pending orders in compact rows.  
**Docs:** [`opened_orders`](docs/MT5Account/Orders_Positions_History/opened_orders.md)

---

### Step 6 — Opened Orders Tickets
**Goal:** fetch only tickets of current pending orders (useful for targeted operations later).  
**Docs:** [`opened_orders_tickets`](docs/MT5Account/Orders_Positions_History/opened_orders_tickets.md)

---

### Step 7 — Positions Total
**Goal:** show the count of open positions (with fallback to direct stub if helper path fails).  
**Docs:** [`positions_total`](docs/MT5Account/Orders_Positions_History/positions_total.md)

---

### Step 8 — Orders History (last 7 days)
**Goal:** fetch order history in a bounded window using pb2 `Timestamp` (UTC).  
**Docs:** [`order_history`](docs/MT5Account/Orders_Positions_History/order_history.md),  
[`Orders & Positions History Overview`](docs/MT5Account/Orders_Positions_History/OrdersPositionsHistory_Overview.md)

---

## Gotchas (quick)
- `MT5_SERVER` must match the broker server string.
- If symbol info is empty — call `symbol_select(SYMBOL, true)` first.
- Normalize time to UTC for history endpoints.
- Increase `TIMEOUT_SECONDS` if latency is high.

---

## Next
Continue with **Step_number_(two).md** for DOM and pre‑trade checks (Steps 9–12).
