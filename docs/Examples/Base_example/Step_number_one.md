# Low-Level Walkthrough — Step number one
**Covers:** Steps **1–6**

 This part focuses on *read-only* and safe operations. No trading actions here.

---

## Helpers used in this part
Paths are **relative** to this page (`docs/Examples/Base_example/Step_number_one.md`).

- **Env & connection diagnostics** — see:  
  - [`env.md`](../Common/env.md)  
  - [`diag_connect.md`](../Common/diag_connect.md)
- **Getting familiar with the base API** — see:  
  - [`Getting_Started.md`](../../MT5Account/Getting_Started.md)  
  - [`BASE.md`](../../MT5Account/BASE.md)  
  - [`Under_the_Hood.md`](../../MT5Account/Under_the_Hood.md)

---

## Prerequisites
- Python **3.13.x** (virtual environment recommended).
- Reachable gRPC endpoint.
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
from examples.common.pb2_shim import apply_patch
apply_patch()

from examples.base_example.lowlevel_walkthrough import main  # entrypoint
asyncio.run(main(only_steps=range(1,9)))  # run steps 1..8 (Step 7 is handled in part two)
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
asyncio.run(main(only_steps=range(1,9)))  # 1..8 (Step 7 is handled in part two)
PY
```

---

# Step 1: one-shot account_summary 📊
**Goal:** Connect via `server_name` (ConnectEx) and print key account metrics: equity, balance, margin, free, free_ratio, drawdown, server_time.  
**Docs:** [`account_summary.md`](../../MT5Account/Account_Information/account_summary.md), [`Getting_Started.md`](../../MT5Account/Getting_Started.md)

**Method signatures:**
```python
ConnectEx(request: ConnectExRequest) -> ConnectExReply
AccountSummary(request: AccountSummaryRequest) -> AccountSummaryReply
```
**Gotchas:** Ensure `MT5_SERVER` is correct; increase `TIMEOUT_SECONDS` if latency is high.

---

# Step 2: account_info_* 🧾
**Goal:** Demonstrate direct pb2 calls `AccountInfo*` and safe field extraction.  
**Docs:** [`account_info_double.md`](../../MT5Account/Account_Information/account_info_double.md), [`account_info_integer.md`](../../MT5Account/Account_Information/account_info_integer.md), [`account_info_string.md`](../../MT5Account/Account_Information/account_info_string.md)

**Method signatures (pb):**
```python
AccountInfoDouble(request: AccountInfoDoubleRequest) -> AccountInfoDoubleReply
AccountInfoInteger(request: AccountInfoIntegerRequest) -> AccountInfoIntegerReply
AccountInfoString(request: AccountInfoStringRequest) -> AccountInfoStringReply
```
**Gotchas:** Some fields may be absent depending on the server — always use safe getters.

---

# Step 3: symbol_* basics 🏷️
**Goal:** Ensure the symbol is available and read key attributes.  
**Docs:** [`SymbolsandMarket_Overview.md`](../../MT5Account/Symbols_and_Market/SymbolsandMarket_Overview.md)

---

# Step 4: symbol_params_many ⚙️
**Goal:** Read a compact set of parameters for one/many symbols: spread, tick size/value, lot step and volume limits, etc.  
**Docs:** [`symbol_params_many.md`](../../MT5Account/Symbols_and_Market/symbol_params_many.md)

**Method signatures (pb):**
```python
SymbolParamsMany(request: SymbolParamsManyRequest) -> SymbolParamsManyReply
```
**Gotchas:** Respect `lot_step`, `min_volume`, `max_volume` when planning trade logic.

---

# Step 5: opened_orders 🗂️
**Goal:** Print active pending orders in compact rows.  
**Docs:** [`opened_orders.md`](../../MT5Account/Orders_Positions_History/opened_orders.md)

**Method signatures:**
```python
OpenedOrders(request: OpenedOrdersRequest) -> OpenedOrdersReply
```
**Gotchas:** Normalize times to UTC and handle empty lists gracefully.

---

# Step 6: opened_orders_tickets 🎟️
**Goal:** Fetch only tickets of current pending orders (useful for targeted operations later).  
**Docs:** [`opened_orders_tickets.md`](../../MT5Account/Orders_Positions_History/opened_orders_tickets.md)

**Method signatures:**
```python
OpenedOrdersTickets(request: OpenedOrdersTicketsRequest) -> OpenedOrdersTicketsReply
```

---

# Step 6f: symbol_info_tick ⏱️
**Goal:** Get last tick for the symbol.  
**Docs:** [`symbol_info_tick.md`](../../MT5Account/Symbols_and_Market/symbol_info_tick.md)

**Method signatures:**
```python
SymbolInfoTick(request: SymbolInfoTickRequest) -> SymbolInfoTickRequestReply
```

---

# Step 6g: symbol_info_session_quote 
**Goal:** Read current **quote** session info for the symbol.  
**Docs:** [`symbol_info_session_quote.md`](../../MT5Account/Symbols_and_Market/symbol_info_session_quote.md)

**Method signatures (pb):**
```python
SymbolInfoSessionQuote(request: SymbolInfoSessionQuoteRequest) -> SymbolInfoSessionQuoteReply
```

---

# Step 6h: symbol_info_session_trade 
**Goal:** Read current **trade** session info for the symbol.  
**Docs:** [`symbol_info_session_trade.md`](../../MT5Account/Symbols_and_Market/symbol_info_session_trade.md)

**Method signatures:**
```python
SymbolInfoSessionTrade(request: SymbolInfoSessionTradeRequest) -> SymbolInfoSessionTradeReply
```

---

# Step 6i: symbol_info_margin_rate 🧮
**Goal:** Read margin rate information for the symbol.  
**Docs:** [`symbol_info_margin_rate.md`](../../MT5Account/Symbols_and_Market/symbol_info_margin_rate.md)

**Method signatures:**
```python
SymbolInfoMarginRate(request: SymbolInfoMarginRateRequest) -> SymbolInfoMarginRateReply
```

---

# Step 6j: symbol_name 🏷️
**Goal:** Read the canonical symbol name.  
**Docs:** [`symbol_name.md`](../../MT5Account/Symbols_and_Market/symbol_name.md)

**Method signatures:**
```python
SymbolName(request: SymbolNameRequest) -> SymbolNameReply
```
---

## Gotchas (quick)
- `MT5_SERVER` must exactly match the broker’s server string.
- If symbol details return empty values — call `symbol_select(SYMBOL, True)` first.
- Normalize time to UTC for history endpoints.
- Increase `TIMEOUT_SECONDS` if you observe high latency.

---

