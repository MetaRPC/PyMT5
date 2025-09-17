# ✅ Symbol Exist

> **Request:** check whether a **symbol** exists on the server (either standard or custom) and whether it’s a **custom** one.

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `symbol_exist(...)`
* `MetaRpcMT5/mt5_term_api_market_info_pb2.py` — `SymbolExist*` messages (`SymbolExistRequest`, `SymbolExistReply`, `SymbolExistData`)
* `MetaRpcMT5/mt5_term_api_market_info_pb2_grpc.py` — service stub `MarketInfoStub`

---

### RPC

* **Service:** `mt5_term_api.MarketInfo`
* **Method:** `SymbolExist(SymbolExistRequest) → SymbolExistReply`
* **Low-level client:** `MarketInfoStub.SymbolExist(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.symbol_exist(symbol, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Check if symbol exists and whether it is custom
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2

info = await acct.symbol_exist("EURUSD")
print(info.exists, info.is_custom)  # e.g., True False
```

---

### Method Signature

```python
async def symbol_exist(
    self,
    symbol: str,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> market_info_pb2.SymbolExistData
```

---

## 💬 Plain English

* **What it is.** Returns a tiny struct telling you if the **symbol exists** and whether it’s a **custom** symbol.
* **Why you care.** Gate user input, avoid 404‑style flows before heavier RPCs (quotes, specs, orders).
* **Mind the traps.**

  * Request field is `name` (string) → pass the exact **symbol name**.
  * The reply’s `.data` is unwrapped by the SDK wrapper; you receive `SymbolExistData` directly.

---

## 🔽 Input

| Parameter            | Type                 | Description                                       |                                                    |   |
| -------------------- | -------------------- | ------------------------------------------------- | -------------------------------------------------- | - |
| `symbol`             | `str` (**required**) | Symbol name to check (maps to `name` in request). |                                                    |   |
| `deadline`           | \`datetime           | None\`                                            | Absolute per‑call deadline → converted to timeout. |   |
| `cancellation_event` | \`asyncio.Event      | None\`                                            | Cooperative cancel for the retry wrapper.          |   |

> **Request message (verified):** `SymbolExistRequest { name: string }`

---

## ⬆️ Output

### Payload: `SymbolExistData`

| Field       | Proto Type | Description                                  |
| ----------- | ---------- | -------------------------------------------- |
| `exists`    | `bool`     | `True` if the symbol exists.                 |
| `is_custom` | `bool`     | `True` if the symbol is a **custom** symbol. |

> **Wire reply:** `SymbolExistReply { data: SymbolExistData, error: Error? }`
> SDK returns `reply.data`.

---

### 🎯 Purpose

* Validate user input before deeper calls (quotes/specs/orders).
* Drive UI hints (e.g., badge custom symbols).
* Health checks in batch symbol import pipelines.

### 🧩 Notes & Tips

* Combine with `symbols_total(...)` and `symbol_name(...)` to page through and validate symbol lists.
* If `exists=False`, skip any downstream price/spec requests to avoid server noise.
