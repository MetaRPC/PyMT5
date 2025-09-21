# ✅ Account Info String

> **Request:** single string account property from MT5.
> Fetch one label (name, server, currency, company) by enum.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `account_info_string(...)`
* `MetaRpcMT5/mt5_term_api_account_information_pb2.py` — `AccountInfoString*`, `AccountInfoStringPropertyType`

---

### RPC

* **Service:** `mt5_term_api.AccountInformation`
* **Method:** `AccountInfoString(AccountInfoStringRequest) → AccountInfoStringReply`
* **Low-level client:** `AccountInformationStub.AccountInfoString(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.account_info_string(property_id, deadline=None, cancellation_event=None) -> str`

---

### 🔗 Code Example

```python
# Minimal canonical example: get Deposit Currency ("USD"/"EUR"/...)
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

cur = await acct.account_info_string(
    account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY
)
print(f"Currency: {cur}")
```

---

### Method Signature

```python
async def account_info_string(
    self,
    property_id: account_info_pb2.AccountInfoStringPropertyType,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> str
```

---

## 💬 Plain English

* **What it is.** A polite one-question-at-the-counter: *“What’s the account’s **name/server/currency/company**?”* You provide an enum ticket; it hands you one label — a **string**.
* **Why you care.** You need labels for UI, logs, or formatting (e.g., show `USD`, display broker/company, greet by account name).
* **Mind the traps.**

  * Values are **strings**; don’t parse numbers from here — use `AccountInfoInteger/Double` for numerics.
  * Broker naming can vary (`SERVER`/`COMPANY` branding). Treat them as display-only labels.
  * Currency codes are **ISO-like** (e.g., `"USD"`), but formatting still depends on `ACCOUNT_CURRENCY_DIGITS` (see `AccountInfoInteger`).

---

## 🔽 Input

| Parameter            | Type                                             | Description                                        |
| -------------------- | ------------------------------------------------ | -------------------------------------------------- |
| `property_id`        | `AccountInfoStringPropertyType` (enum, required) | Which label to fetch (see enum below).             |
| `deadline`           | `datetime \| None`                               | Absolute per-call deadline → converted to timeout. |
| `cancellation_event` | `asyncio.Event \| None`                          | Cooperative cancel for the retry wrapper.          |

**Request message:** `AccountInfoStringRequest { propertyId }`

---

## ⬆️ Output

### Payload: `AccountInfoStringData`

| Field            | Proto Type | Description                               |
| ---------------- | ---------- | ----------------------------------------- |
| `requestedValue` | `string`   | The label value of the selected property. |

---

### Enum: `AccountInfoStringPropertyType`

| Number | Value              | Meaning                |
| -----: | ------------------ | ---------------------- |
|      0 | `ACCOUNT_NAME`     | Account holder name.   |
|      1 | `ACCOUNT_SERVER`   | Server name.           |
|      2 | `ACCOUNT_CURRENCY` | Deposit currency code. |
|      3 | `ACCOUNT_COMPANY`  | Broker/company name.   |

---

### 🎯 Purpose

* Render precise labels in UI/CLI (currency, server, company, name).
* Build clean status headers and breadcrumbs without extra RPCs.
* Keep business/UI code independent from proto internals.

### 🧩 Notes & Tips

* For money formatting: pair `ACCOUNT_CURRENCY` with `ACCOUNT_CURRENCY_DIGITS` (from `AccountInfoInteger`).
* The SDK wrapper already handles transient gRPC hiccups via `execute_with_reconnect(...)`.

**See also:** [AccountInfoInteger](../Account_Information/account_info_integer.md), [AccountInfoDouble](../Account_Information/account_info_double.md), [AccountSummary](../Account_Information/account_summary.md).

---

## Usage Examples

### 1) Currency + digits → proper amount formatting

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

cur = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY)
# digits comes from AccountInfoInteger
# digits = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_CURRENCY_DIGITS)
print(f"{cur}")
```

### 2) Name & company for headers

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

name = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME)
comp = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_COMPANY)
print(f"{name} — {comp}")
```

### 3) Server label (with deadline & cancellation)

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

cancel_event = asyncio.Event()
server = await acct.account_info_string(
    account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(server)
```

### 4) Compact status line

```python
# Build a readable one-liner for CLI/dashboard
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as account_info_pb2

cur = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY)
name = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_NAME)
server = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_SERVER)
print(f"{name} | {server} | {cur}")
```
