# ✅ Account Info Double

> **Request:** single numeric account property (double) from MT5.
> Fetch one metric (e.g., Balance, Equity, Margin, MarginLevel, …) by enum.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `account_info_double(...)`
* `MetaRpcMT5/mt5_term_api_account_information_pb2.py` — `AccountInfoDouble*`, `AccountInfoDoublePropertyType`

### RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoDouble(AccountInfoDoubleRequest) → AccountInfoDoubleReply`
* **Low-level client:** `AccountInformationStub.AccountInfoDouble(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.account_info_double(property_id, deadline=None, cancellation_event=None) -> float`

---

### 🔗 Code Example

```python
# Minimal canonical example: get Balance
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

value = await acct.account_info_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
print(f"Balance: {value:.2f}")
```

---

### Method Signature

```python
async def account_info_double(
    self,
    property_id: account_info_pb2.AccountInfoDoublePropertyType,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> float
```

---

## 💬 Just about the main thing

* **What is it.** Returns **one numeric account metric** by enum (balance, equity, margin, margin levels, etc.).
* **Why.** Build dashboards, thresholds/alerts, or quick checks without pulling the full summary.
* **Be careful.**

  * `ACCOUNT_MARGIN_LEVEL' is **a percentage** (usually 0-1000+), not a fraction.
  * Do the rounding yourself (see `account_currency` / `ACCOUNT_CURRENCY_DIGITS` in integer/string methods).
  * Some values (assets/liabilities) are not found in all brokers.
* **When to call.** Dot when you need **one** digit, not the whole `AccountSummary'.
* **Quick check.** Got a number of the `float` type → everything is ok; if None/exception, see connection/errors.

---

## 🔽 Input

| Parameter            | Type                                             | Description                                  |                                                         |
| -------------------- | ------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------- |
| `property_id`        | `AccountInfoDoublePropertyType` (enum, required) | What metric are we requesting?               |                                                         |
| `deadline`           | \`datetime                                       | None\`                                       | The absolute call deadline → is converted to timeout.   |
| `cancellation_event` | \`asyncio.Event                                  | None\`                                       | Cooperative cancellation (graceful stop) for the retry wrapper. |

---

## ⬆️ Output

### Payload: `AccountInfoDoubleData`

| Field            | Proto Type | Description                             |
| ---------------- | ---------- | --------------------------------------- |
| `requestedValue` | `double`   | value of the selected property (`float`). |

### Enum: `AccountInfoDoublePropertyType`

| Value                        | Meaning                            |
| ---------------------------- | ---------------------------------- |
| `ACCOUNT_BALANCE`            | Balance (without floating P/L).      |
| `ACCOUNT_CREDIT`             | Credit.                            |
| `ACCOUNT_PROFIT`             | Floating P/L.                      |
| `ACCOUNT_EQUITY`             | Equity.                            |
| `ACCOUNT_MARGIN`             | Used margin.                       |
| `ACCOUNT_MARGIN_FREE`        | Free margin.                       |
| `ACCOUNT_MARGIN_LEVEL`       | Margin level, **%**.               |
| `ACCOUNT_MARGIN_SO_CALL`     | Stop‑out Call level, **%**.        |
| `ACCOUNT_MARGIN_SO_SO`       | Stop‑out level, **%**.             |
| `ACCOUNT_MARGIN_INITIAL`     | Initial margin.                    |
| `ACCOUNT_MARGIN_MAINTENANCE` | Maintenance margin.                |
| `ACCOUNT_ASSETS`             | Assets (if supported).      |
| `ACCOUNT_LIABILITIES`        | Responsibilities (if supported). |
| `ACCOUNT_COMMISSION_BLOCKED` | Blocked fees.        |

---

### 🎯 Purpose

* Displaying a specific number in the UI/CLI without overloading.
* Simple checks before operations (for example, margin level, equity).
* Easy telemetry/logging based on key metrics.

### 🧩 Notes & Tips

* To format money, use `ACCOUNT_CURRENCY_DIGITS` (via `account_info_integer').
* If you need a set of multiple metrics, see `AccountSummary` — this is one RPC instead of several.
* The method is wrapped by `execute_with_reconnect(...)` — back‑off and retrays on network errors are already inside.

**See also:** `AccountInfoInteger`, `AccountInfoString`, `AccountSummary`.

---

## Usage Examples

### 1) Equity / Margin Level

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

equity = await acct.account_info_double(account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_EQUITY)
level  = await acct.account_info_double(account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_MARGIN_LEVEL)
print(f"Eq={equity:.2f} | ML={level:.1f}%")
```

### 2) Free vs Used Margin

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

free = await acct.account_info_double(account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_MARGIN_FREE)
used = await acct.account_info_double(account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_MARGIN)
print(f"Margin: used={used:.2f} / free={free:.2f}")
```

### 3) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

cancel_event = asyncio.Event()
value = await acct.account_info_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(value)
```
