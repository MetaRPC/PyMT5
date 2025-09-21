# ✅ Account Info Integer

> **Request:** single integer account property from MT5.
> Fetch one integer metric (login, leverage, flags/modes, currency digits) by enum.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `account_info_integer(...)`
* `MetaRpcMT5/mt5_term_api_account_information_pb2.py` — `AccountInfoInteger*`, `AccountInfoIntegerPropertyType`

---

### RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoInteger(AccountInfoIntegerRequest) → AccountInfoIntegerReply`
* **Low-level client:** `AccountInformationStub.AccountInfoInteger(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.account_info_integer(property_id, deadline=None, cancellation_event=None) -> int`

---

### 🔗 Code Example

```python
# Minimal canonical example: get Leverage
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

lev = await acct.account_info_integer(
    account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE
)
print(f"Leverage: {lev}")
```

---

### Method Signature

```python
async def account_info_integer(
    self,
    property_id: account_info_pb2.AccountInfoIntegerPropertyType,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> int
```

---

## 💬 Plain English

* **What it is.** A vending machine for **single integer facts** about your account —
  you insert the right enum, it drops one number: login, leverage, flags, modes, currency digits.
* **Why you care.** You often need *one* integer fast (e.g., `LEVERAGE` or `CURRENCY_DIGITS`) without pulling the whole summary.
* **Mind the traps.**

  * Booleans are usually returned as **0/1 integers** (e.g., `ACCOUNT_TRADE_ALLOWED`).
  * Modes (e.g., stop‑out mode) are numeric codes — map them to labels in your UI.
  * `CURRENCY_DIGITS` is crucial for money formatting; use it with doubles from `AccountInfoDouble`.
* **When to call.** Targeted checks, formatting decisions, guards for UI/flows.
* **Quick check.** You get a Python `int`. If it explodes/None → check connectivity and the error doc.

---

## 🔽 Input

No required input besides the enum.

| Parameter            | Type                                              | Description                                        |
| -------------------- | ------------------------------------------------- | -------------------------------------------------- |
| `property_id`        | `AccountInfoIntegerPropertyType` (enum, required) | Which integer metric to fetch (see list below).    |
| `deadline`           | `datetime \| None`                                | Absolute per‑call deadline → converted to timeout. |
| `cancellation_event` | `asyncio.Event \| None`                           | Cooperative cancel for the retry wrapper.          |

> **Request message:** `AccountInfoIntegerRequest { propertyId }`

---

## ⬆️ Output

### Payload: `AccountInfoIntegerData`

| Field   | Proto Type | Description                         |
| ------- | ---------- | ----------------------------------- |
| `value` | `int64`    | The value of the selected property. |

---

### Enum: `AccountInfoIntegerPropertyType`

| Number | Value                     | Meaning                                    |
| -----: | ------------------------- | ------------------------------------------ |
|      0 | `ACCOUNT_LOGIN`           | Account login (ID).                        |
|      1 | `ACCOUNT_TRADE_MODE`      | Trade mode code (map to label if needed).  |
|      2 | `ACCOUNT_LEVERAGE`        | Leverage (e.g., 100 for 1:100).            |
|      3 | `ACCOUNT_LIMIT_ORDERS`    | Current limit for pending orders (if set). |
|      4 | `ACCOUNT_MARGIN_SO_MODE`  | Stop-out mode code (percent/money).        |
|      5 | `ACCOUNT_TRADE_ALLOWED`   | Trading allowed flag (0/1).                |
|      6 | `ACCOUNT_TRADE_EXPERT`    | Expert Advisors allowed flag (0/1).        |
|      7 | `ACCOUNT_MARGIN_MODE`     | Margin mode code (netting/hedging).        |
|      8 | `ACCOUNT_CURRENCY_DIGITS` | Number of digits for money formatting.     |
|      9 | `ACCOUNT_FIFO_CLOSE`      | FIFO close flag (0/1), if supported.       |
|     10 | `ACCOUNT_HEDGE_ALLOWED`   | Hedging allowed flag (0/1).                |

---

### 🎯 Purpose

* Fetch one integer property fast for UI formatting and guards.
* Build conditions/alerts based on leverage, modes, or flags.
* Keep code decoupled: business/UI depend on enums, not on pb internals.

### 🧩 Notes & Tips

* Combine with `AccountInfoDouble` (for values) and `AccountInfoString` (for currency) to format amounts correctly.
* Map mode/flag integers to human labels near the UI (don’t leak raw codes to users).
* The wrapper handles transient gRPC errors via `execute_with_reconnect(...)`.

**See also:** [AccountInfoDouble](../Account_Information/account_info_double.md), [AccountInfoString](../Account_Information/account_info_string.md), [AccountSummary](../Account_Information/account_summary.md).

---

## Usage Examples

### 1) Leverage & Currency Digits

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

lev = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE)
digits = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_CURRENCY_DIGITS)
print(f"Lev={lev} | Digits={digits}")
```

### 2) Trading allowed / expert allowed

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

trade_ok = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED)
expert_ok = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_EXPERT)
print(f"TradeAllowed={bool(trade_ok)} | ExpertAllowed={bool(expert_ok)}")
```

### 3) Stop‑out mode code → label

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

mode = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_MARGIN_SO_MODE)
mode_label = {0: "PERCENT", 1: "MONEY"}.get(int(mode), f"UNKNOWN({mode})")
print(f"StopOutMode={mode_label}")
```

### 4) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

cancel_event = asyncio.Event()
value = await acct.account_info_integer(
    account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LOGIN,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(value)
```
