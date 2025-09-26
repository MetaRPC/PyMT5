# Low-Level Walkthrough — Step number two
**Covers:** Steps **7–10** (positions total, order/positions history, Market Book DOM, DOM scan).  

> This part remains *read-only* (no order placement). DOM subscriptions are opened and released safely.

---

## Helpers used in this part
Paths are **relative** to this page (`docs/Examples/Base_example/Step_number_two.md`).

- **pb2 shim (compatibility layer)** — apply before any pb2 usage:  
  - [`pb2_shim.md`](../Common/pb2_shim.md)
- **Common utilities (pretty printers, UTC/time helpers, safe getters)**:  
  - [`utils.md`](../Common/utils.md)
- **Environment & diagnostics (optional, if connection/env needs checks)**:  
  - [`env.md`](../Common/env.md), [`diag_connect.md`](../Common/diag_connect.md)

---

## How to run this part
PowerShell (Windows):
```powershell
# Optional toggles for DOM steps
$env:RUN_DOM=1        # enables Step 10
$env:RUN_DOM_SCAN=1   # enables Step 10a

python - <<'PY'
import asyncio
from examples.common.pb2_shim import apply_patch
apply_patch()

from examples.base_example.lowlevel_walkthrough import main
# Run steps 7..10; Step 10a is gated by RUN_DOM_SCAN=1
asyncio.run(main(only_steps=[7,8,9,10]))
PY
```

Bash:
```bash
export RUN_DOM=1        # enables Step 10
export RUN_DOM_SCAN=1   # enables Step 10a
python - <<'PY'
import asyncio
from examples.common.pb2_shim import apply_patch
apply_patch()

from examples.base_example.lowlevel_walkthrough import main
asyncio.run(main(only_steps=[7,8,9,10]))
PY
```

---

# Step 7: positions_total 📊
**Goal:** Return the count of open positions (with a hard fallback to the direct stub if helper path fails).  
**Docs:** [`positions_total.md`](../../MT5Account/Orders_Positions_History/positions_total.md)

**Method signatures:**
```python
PositionsTotal(request: Empty) -> PositionsTotalReply
```

---

# Step 8: order_history (last 7 days) 🕰️
**Goal:** Fetch order history within a time window using pb2 `Timestamp` (UTC).  
**Docs:** [`order_history.md`](../../MT5Account/Orders_Positions_History/order_history.md)

**Method signatures:**
```python
OrderHistory(request: OrderHistoryRequest) -> OrderHistoryReply
```

---

# Step 9: positions_history (last 7 days) 📜
**Goal:** Fetch positions history within a time window; prints compact rows with key PnL/time fields.  
**Docs:** [`positions_history.md`](../../MT5Account/Orders_Positions_History/positions_history.md)

**Method signatures (pb):**
```python
PositionsHistory(request: PositionsHistoryRequest) -> PositionsHistoryReply
```

---

# Step 10: Market Book (DOM) 📈
**Goal:** Probe DOM carefully — check depth, subscribe, read a few snapshots, then release.  
**Docs:** [`market_book_add.md`](../../MT5Account/Symbols_and_Market/market_book_add.md),  
[`market_book_get.md`](../../MT5Account/Symbols_and_Market/market_book_get.md),  
[`market_book_release.md`](../../MT5Account/Symbols_and_Market/market_book_release.md)

**Method signatures:**
```python
MarketBookAdd(request: MarketBookAddRequest) -> MarketBookAddReply
MarketBookGet(request: MarketBookGetRequest) -> MarketBookGetReply
MarketBookRelease(request: MarketBookReleaseRequest) -> MarketBookReleaseReply
```
**Gotchas:** Not every server or symbol exposes DOM. If unavailable, log a clear warning and continue — that’s expected.

---

# Step 10a: scan symbols that have DOM 🔎
**Goal:** Iterate symbols and print those with available DOM by attempting a lightweight subscribe/release.  
**Docs:** [`symbols_total.md`](../../MT5Account/Symbols_and_Market/symbols_total.md),  
[`market_book_add.md`](../../MT5Account/Symbols_and_Market/market_book_add.md),  
[`market_book_release.md`](../../MT5Account/Symbols_and_Market/market_book_release.md)

**Method signatures:**
```python
SymbolsTotal(SymbolsTotalRequest) -> SymbolsTotalReply
MarketBookAdd(MarketBookAddRequest) -> MarketBookAddReply
MarketBookRelease(MarketBookReleaseRequest) -> MarketBookReleaseReply
```
