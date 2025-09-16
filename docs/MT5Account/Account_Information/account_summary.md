# Getting an Account Summary

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

### Code Example

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

## 🧩 Notes & Tips

* Wrapper uses `execute_with_reconnect(...)` to retry on transient gRPC errors.
* Consider a short per‑call timeout (3–5s) and retry if the terminal is syncing symbols.

