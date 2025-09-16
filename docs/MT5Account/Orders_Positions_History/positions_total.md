# ✅ Positions Total

> **Request:** total number of **currently open positions** for the connected MT5 account.
> Lightweight integer result — ideal for quick guards and UI badges.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `positions_total(...)`
* `MetaRpcMT5/mt5_term_api_trade_functions_pb2.py` — `PositionsTotal*`

**Menu entry:** `PositionsTotal`

---

### RPC

* **Service:** `mt5_term_api.TradeFunctions`
* **Method:** `PositionsTotal(PositionsTotalRequest) → PositionsTotalReply`
* **Low-level client:** `TradeFunctionsStub.PositionsTotal(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.positions_total(deadline=None, cancellation_event=None) -> int`

---

### 🔗 Code Example

```python
# Minimal canonical example: how many positions are open now?
data = await acct.positions_total()               # PositionsTotalData
print(int(data.total_positions))

```

---

### Method Signature

```python
async def positions_total(
    self,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> trade_functions_pb2.PositionsTotalData
```

---

## 💬 Plain English

* **What it is.** A quick **headcount** for your exposure: “how many positions are alive right now?”
* **Why you care.** Drive red dots and badges in UI, simple pre‑trade rules (e.g., max concurrent positions), and smoke checks.
* **Mind the traps.**

  * This is **positions only** (not pending orders). For orders, see `OpenedOrders`.
  * It returns **one integer**; if you need symbols/volumes/PnL, call richer RPCs (`OpenedOrders`).
  * Consider your netting/hedging mode when interpreting counts.
* **When to call.** On screen open, periodic refresh, before opening new positions.

---

## 🔽 Input

No required input parameters.

| Parameter            | Type            | Description |                                                    |
| -------------------- | --------------- | ----------- | -------------------------------------------------- |
| `deadline`           | \`datetime      | None\`      | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event | None\`      | Cooperative cancel for the retry wrapper.          |

> **Request message:** `PositionsTotalRequest` has **no fields**.

---

## ⬆️ Output

### Payload: `PositionsTotalData`

| Field   | Proto Type | Description                         |
| ------- | ---------- | ----------------------------------- |
| total_positions | int32 | Number of currently open positions. |


---

### 🎯 Purpose

* Show a compact **count badge** in dashboards/CLI.
* Enforce simple **risk/ops rules** (e.g., don’t exceed N concurrent positions).
* Quick sanity checks during workflows.

### 🧩 Notes & Tips

* For details per position (symbol, PnL, volume) use `OpenedOrders` or historical RPCs.
* Wrapper retries transient gRPC errors via `execute_with_reconnect(...)`.

**See also:** `OpenedOrders`, `OpenedOrdersTickets`.

---

## Usage Examples

### 1) Simple print & guard

```python
n = await acct.positions_total()
if int(n) > 10:
    print("Too many open positions — consider reducing exposure.")
else:
    print(f"Open positions: {int(n)}")
```

### 2) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone

cancel_event = asyncio.Event()
count = await acct.positions_total(
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(int(count))
```

### 3) Cross‑check vs OpenedOrders (client‑side sanity)

```python
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

n = int(await acct.positions_total())
od = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
print(n, len(od.position_infos))  # should normally match
```
