# ✅ Getting an Account Summary

> **Request:** full account summary (`AccountSummaryData`) from MT5.
> Fetch all core account metrics in a single call.

**Source files (SDK):**

* `MetaRpcMT5/mt5_account.py` — method `account_summary(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `AccountSummary*`, `MrpcEnumAccountTradeMode`

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `AccountSummary(AccountSummaryRequest) → AccountSummaryReply`
* **Low-level client:** `AccountHelperStub.AccountSummary(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.account_summary(deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# High-level (prints formatted summary):
async def show_account_summary(acct):
    s = await acct.account_summary()
    print(
        f"Account Summary: Balance={s.account_balance:.2f}, "
        f"Equity={s.account_equity:.2f}, Currency={s.account_currency}, "
        f"Login={s.account_login}, Leverage={s.account_leverage}, "
        f"Mode={s.account_trade_mode}"
    )

# Low-level (returns the proto message):
summary = await acct.account_summary()
# summary: AccountSummaryData
```

---

### Method Signature

```python
async def account_summary(
    self,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.AccountSummaryData
```

---

## 💬 Just about the main thing

* **What is it.** One RPC that returns the account status: balance, equity, currency, leverage, account type, and server time.
* **Why.** Quick status for UI/CLI; compare currency/login/leverage with expectations; understand the status of the balance/equity bundle; make sure that the terminal responds (by `server_time').
* **Quick receipt.** There is `account_login`, `account_currency`, `account_leverage`, `account_equity` → the connection is alive, the data is coming.

---

## 🔽 Input

No required input parameters.

| Parameter            | Type            | Description |                                                    |
| -------------------- | --------------- | ----------- | -------------------------------------------------- |
| `deadline`           | \`datetime      | None\`      | Absolute per-call deadline → converted to timeout. |
| `cancellation_event` | \`asyncio.Event | None\`      | Cooperative cancel for retry loop.                 |

---

## ⬆️ Output

### Payload: `AccountSummaryData`

| Field                                    | Proto Type                      | Description                                |
| ---------------------------------------- | ------------------------------- | ------------------------------------------ |
| `account_login`                          | `int64`                         | Trading account login (ID).                |
| `account_balance`                        | `double`                        | Balance excluding floating P/L.            |
| `account_equity`                         | `double`                        | Equity = balance + floating P/L.           |
| `account_user_name`                      | `string`                        | Account holder display name.               |
| `account_leverage`                       | `int64`                         | Leverage (e.g., 100 for 1:100).            |
| `account_trade_mode`                     | `enum MrpcEnumAccountTradeMode` | Trade mode of the account.                 |
| `account_company_name`                   | `string`                        | Broker/company display name.               |
| `account_currency`                       | `string`                        | Deposit currency code (e.g., `USD`).       |
| `server_time`                            | `google.protobuf.Timestamp`     | Server time at response.                   |
| `utc_timezone_server_time_shift_minutes` | `int64`                         | Server timezone offset (minutes from UTC). |
| `account_credit`                         | `double`                        | Credit amount.                             |


---

### 🎯 Purpose

Use to display real-time account state and sanity‑check connectivity:

* Dashboard/CLI status
* Verify free margin & equity before trading

### 🧩 Notes & Tips

* Wrapper uses `execute_with_reconnect(...)` to retry on transient gRPC errors.
* Consider a short per‑call timeout (3–5s) and retry if the terminal is syncing symbols.

### «Notes & Tips»: (Доделать)

See also: AccountInfoDouble, AccountInfoInteger, AccountInfoString, PositionsTotal, OpenedOrders.  

## Usage Examples

### 1) Per‑call deadline

```python
 Enforce a short absolute deadline to avoid hanging calls
from datetime import datetime, timedelta, timezone


summary = await acct.account_summary(
deadline=datetime.now(timezone.utc) + timedelta(seconds=3)
)
print(f"[deadline] Equity={summary.account_equity:.2f}")
```

### 2) Cooperative cancellation (with asyncio.Event)
```python
 Pass a cancellation_event to allow graceful stop from another task
import asyncio
from datetime import datetime, timedelta, timezone


cancel_event = asyncio.Event()


 somewhere else: cancel_event.set() to request cancellation
summary = await acct.account_summary(
deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
cancellation_event=cancel_event,
)
print(f"[cancel] Currency={summary.account_currency}")

```
### 3) Compact status line for UI/CLI

```python
 Produce a short, readable one‑liner for dashboards/CLI
s = await acct.account_summary()
status = (
f"Acc {s.account_login} | {s.account_currency} | "
f"Bal {s.account_balance:.2f} | Eq {s.account_equity:.2f} | "
f"Lev {s.account_leverage} | Mode {s.account_trade_mode}"
)
print(status)
```

### 4) Human‑readable server time with timezone shift
```python
Convert server_time (UTC Timestamp) + shift (minutes) to a local server time string
from datetime import timezone, timedelta


s = await acct.account_summary()
server_dt_utc = s.server_time.ToDatetime().replace(tzinfo=timezone.utc)
shift = timedelta(minutes=int(s.utc_timezone_server_time_shift_minutes))
server_local = server_dt_utc + shift
print(f"Server time: {server_local.isoformat()} (shift {shift})")
```

### 5) Map proto → your dataclass (thin view‑model)

```python
 Keep only the fields you actually use; fast and test‑friendly
from dataclasses import dataclass


@dataclass
class AccountSummaryView:
login: int
currency: str
balance: float
equity: float
leverage: int
mode: int # enum value; map to label if needed


@staticmethod
def from_proto(p):
return AccountSummaryView(
login=int(p.account_login),
currency=str(p.account_currency),
balance=float(p.account_balance),
equity=float(p.account_equity),
leverage=int(p.account_leverage),
mode=int(p.account_trade_mode),
)


s = await acct.account_summary()
view = AccountSummaryView.from_proto(s)
print(view)
```
### What this teaches

 * How to call account_summary() safely with deadline and cancellation.

 * How to format results for UX/CLI without dragging proto types everywhere.

 * How to interpret server time correctly with the server‑provided UTC shift.

 * How to decouple UI/business code from the raw proto via a small view‑model.
