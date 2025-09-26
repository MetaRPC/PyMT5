# Low‑Level Walkthrough — Step number three

**Covers:** Steps **11–16** (trading and event streaming).

> ⚠️ This is where account state changes begin. Use a **demo** account or minimal volumes. Always double‑check parameters before sending.

---

## Helpers & utilities

Paths are relative to this page (`docs/Examples/Base_example/Step_number_three.md`).

* **pb2 shim (enum/field compatibility):** [`pb2_shim.md`](../Common/pb2_shim.md)
* **Common utils (price/volume normalization, printers, safe‑get):** [`utils.md`](../Common/utils.md)
* **Env & diagnostics (if needed):** [`env.md`](../Common/env.md), [`diag_connect.md`](../Common/diag_connect.md)

## How to run

PowerShell (Windows):

```powershell
$env:RUN_TRADING=1
$env:STREAM_RUN_SECONDS=15

@'
import asyncio
from examples.common.pb2_shim import apply_patch
apply_patch()

from examples.base_example.lowlevel_walkthrough import main
# Execute trading steps and streaming
asyncio.run(main(only_steps=[11,12,13,14,15,16]))
'@ | python -
```

Bash:

```bash
export RUN_TRADING=1
export STREAM_RUN_SECONDS=15
python - <<'PY'
import asyncio
from examples.common.pb2_shim import apply_patch
apply_patch()

from examples.base_example.lowlevel_walkthrough import main
asyncio.run(main(only_steps=[11,12,13,14,15,16]))
PY
```

---

# Step 11: Trading — order_calc_margin (safe) 🧮

**Goal:** dry‑run margin calculation for the selected parameters (symbol/side/volume).

**Docs:** [`order_calc_margin.md`](../../MT5Account/Trading_Operations/order_calc_margin.md)

**Signatures (pb):**

```python
OrderCalcMargin(OrderCalcMarginRequest) -> OrderCalcMarginReply
```

**Tips:** use values from `SymbolParamsMany` (tick_size, lot_step, min/max volume) to keep inputs valid.

---

# Step 12: TF OrderCheck — MARKET + mandatory expiration ✅

**Goal:** validate placing a MARKET order with a mandatory `expiration`.

**Docs:** [`order_check.md`](../../MT5Account/Trading_Operations/order_check.md)

**Signatures:**

```python
OrderCheck(OrderCheckRequest) -> OrderCheckReply
```

**Notes:** validate SL/TP against `tick_size` and minimum stop distances; set `expiration` per broker policy.

---

# Step 12b: OrderCheck DIAG — print payload with expiration = +1 day 🔍

**Goal:** repeat the check with `expiration = now + 1 day`, and **print the full response** (diagnostic field/reason breakdown).

**Docs:** [`order_check.md`](../../MT5Account/Trading_Operations/order_check.md)

**Signatures (pb):**

```python
OrderCheck(OrderCheckRequest) -> OrderCheckReply
```

---

# Step 13: order_send (market — TradingHelper) 🚀

**Goal:** send a market order using env parameters (`TRADE_SIDE`, `TRADE_VOLUME`, `SL/TP`, `DEVIATION`, `TIME`, `FILLING`).

**Docs:** [`order_send.md`](../../MT5Account/Trading_Operations/order_send.md)

**Signatures:**

```python
OrderSend(OrderSendRequest) -> OrderSendReply
```

**Precautions:** check `lot_step` / `min_volume` / `max_volume`; ensure SL/TP align to tick size and do not violate minimum distances.

---

# Step 13a: discover POSITION_TICKET via one‑shot stream 🎯

**Goal:** if a position ticket is not provided, obtain it from the tickets stream (short‑lived subscription).

**Docs:** [`on_positions_and_pending_orders_tickets.md`](../../MT5Account/Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md)

**Signatures (pb):**

```python
OnPositionsAndPendingOrdersTickets(OnPositionsAndPendingOrdersTicketsRequest) -> stream OnPositionsAndPendingOrdersTicketsReply
```

---

# Step 14: order_modify_sltp — TradingHelper ✏️

**Goal:** modify SL/TP for an existing position.

**Docs:** [`order_modify.md`](../../MT5Account/Trading_Operations/order_modify.md)

**Signatures:**

```python
OrderModify(OrderModifyRequest) -> OrderModifyReply
```

**Notes:** respect tick size and minimum distances; the ticket is taken from `POSITION_TICKET` or Step 13a.

---

# Step 15: order_close — TradingHelper 🧹

**Goal:** close a position fully or partially (`CLOSE_VOLUME`).

**Docs:** [`order_close.md`](../../MT5Account/Trading_Operations/order_close.md)

**Signatures:**

```python
OrderClose(OrderCloseRequest) -> OrderCloseReply
```

---

# Step 16a: on_symbol_tick ⏱️

**Goal:** subscribe to symbol ticks and handle several events; terminate cleanly via `STREAM_RUN_SECONDS`.

**Docs:** [`on_symbol_tick.md`](../../MT5Account/Subscriptions_Streaming/on_symbol_tick.md)

**Signatures:**

```python
OnSymbolTick(OnSymbolTickRequest) -> stream OnSymbolTickReply
```

---

# Step 16b: on_trade 💹

**Goal:** listen to trade (deal) events and print key fields.

**Docs:** [`on_trade.md`](../../MT5Account/Subscriptions_Streaming/on_trade.md)

**Signatures (pb):**

```python
OnTrade(OnTradeRequest) -> stream OnTradeReply
```

---

# Step 16c: on_position_profit 💰

**Goal:** subscribe to profit updates for open positions.

**Docs:** [`on_position_profit.md`](../../MT5Account/Subscriptions_Streaming/on_position_profit.md)

**Signatures:**

```python
OnPositionProfit(OnPositionProfitRequest) -> stream OnPositionProfitReply
```

---

# Step 16d: on_positions_and_pending_orders_tickets 🎟️

**Goal:** receive tickets for positions and pending orders (also used in Step 13a).

**Docs:** [`on_positions_and_pending_orders_tickets.md`](../../MT5Account/Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md)

**Signatures:**

```python
OnPositionsAndPendingOrdersTickets(OnPositionsAndPendingOrdersTicketsRequest) -> stream OnPositionsAndPendingOrdersTicketsReply
```

---

# Step 16e: on_trade_transaction 🔄

**Goal:** subscribe to trade‑transaction events (low‑level changes of orders/positions).

**Docs:** [`on_trade_transaction.md`](../../MT5Account/Subscriptions_Streaming/on_trade_transaction.md)

**Signatures:**

```python
OnTradeTransaction(OnTradeTransactionRequest) -> stream OnTradeTransactionReply
```

---

## Quick tips

* For OrderCheck/Send/Modify/Close, always validate parameters using symbol data (tick_size, lot_step, min/max volume, stop levels).
* Don’t forget `TRADE_DEVIATION`, `TRADE_TIME` (GTC/DAY/…), `TRADE_FILLING` (FOK/IOC/…).
* For streams, set `STREAM_RUN_SECONDS` and always unsubscribe/close cleanly.
