# ✅ Account Info Double

> **Request:** single numeric account property (double) from MT5. Fetch one metric (e.g., Balance, Equity, Margin, MarginLevel, …) by enum.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `account_info_double(...)`
* `MetaRpcMT5/mt5_term_api_account_information_pb2.py` — `AccountInfoDouble*`, `AccountInfoDoublePropertyType`

## RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoDouble(AccountInfoDoubleRequest) → AccountInfoDoubleReply`
* **Low‑level client:** `AccountInformationStub.AccountInfoDouble(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.account_info_double(property_id, deadline=None, cancellation_event=None) -> float`

---

## 🔗 Code Example

```python
# Minimal canonical example: get Balance
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

value = await acct.account_info_double(
    account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE
)
print(f"Balance: {value:.2f}")
```

---

## Method Signature

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

* **What it is.** Returns **one numeric account metric** by enum (balance, equity, margin, margin level, etc.).
* **Why.** Dashboards, alerts, quick checks without pulling the full summary.
* **Be careful.**

  * `ACCOUNT_MARGIN_LEVEL` is a **percentage** (not a fraction).
  * Do your own formatting/rounding; pair with currency digits from integer/string info if needed.
  * Some metrics (assets/liabilities) may be unsupported by a broker.
* **When to call.** When you need **one** number, not the full `AccountSummary`.
* **Quick check.** Return type is `float`; on transport/proto error you’ll get an exception from the wrapper (or `None` if you wrap with your own `safe_async`).

---

## 🔽 Input

| Parameter            | Type                                             | Description                                          |
| -------------------- | ------------------------------------------------ | ---------------------------------------------------- |
| `property_id`        | `AccountInfoDoublePropertyType` (enum, required) | Which metric to request.                             |
| `deadline`           | `datetime \| None`                               | Absolute deadline; converted to client‑side timeout. |
| `cancellation_event` | `asyncio.Event \| None`                          | Cooperative cancellation for reconnect/retry logic.  |

**Request message:** `AccountInfoDoubleRequest { propertyId }`

---

## ⬆️ Output

* **SDK return:** `float` — the requested numeric value.
* **Underlying proto:** `AccountInfoDoubleReply { data: AccountInfoDoubleData { requestedValue: double } }`

---

## Enum: `AccountInfoDoublePropertyType`

| Value                        | Meaning                    |
| ---------------------------- | -------------------------- |
| `ACCOUNT_BALANCE`            | Balance (closed P/L incl.) |
| `ACCOUNT_CREDIT`             | Credit                     |
| `ACCOUNT_PROFIT`             | Floating P/L               |
| `ACCOUNT_EQUITY`             | Equity                     |
| `ACCOUNT_MARGIN`             | Used margin                |
| `ACCOUNT_MARGIN_FREE`        | Free margin                |
| `ACCOUNT_MARGIN_LEVEL`       | Margin level, **%**        |
| `ACCOUNT_MARGIN_SO_CALL`     | Stop‑out Call level, **%** |
| `ACCOUNT_MARGIN_SO_SO`       | Stop‑out level, **%**      |
| `ACCOUNT_MARGIN_INITIAL`     | Initial margin             |
| `ACCOUNT_MARGIN_MAINTENANCE` | Maintenance margin         |
| `ACCOUNT_ASSETS`             | Assets (if supported)      |
| `ACCOUNT_LIABILITIES`        | Liabilities (if supported) |
| `ACCOUNT_COMMISSION_BLOCKED` | Blocked commissions        |

---

## 🎯 Purpose

* Show a single number in UI/CLI efficiently.
* Pre‑trade checks (e.g., margin level, equity).
* Lightweight telemetry/logging.

## 🧩 Notes & Tips

* For money formatting, pair with currency digits from integer/string account info.
* For multiple metrics at once, prefer `AccountSummary` (one RPC instead of several).
* The SDK path typically wraps calls with reconnect/back‑off logic.

**See also:** [AccountInfoInteger](./account_info_integer.md) · [AccountInfoString](./account_info_string.md) · [AccountSummary](./account_summary.md)


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
