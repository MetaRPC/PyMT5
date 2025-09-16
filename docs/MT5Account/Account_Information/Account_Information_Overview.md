# MT5Account · Account Information — Overview

> Quick guide to the four primitives that expose **account metadata** via gRPC. Use this page to choose the right call fast. Links below jump to the full specs.

## 📁 What lives here

* **[AccountSummary](./account_summary.md)** — one call, core metrics bundle (balance, equity, leverage, currency, trade mode, server time, credit).
* **[AccountInfoDouble](./account_info_double.md)** — one **numeric** metric by enum (equity, margin, margin level, etc.).
* **[AccountInfoInteger](./account_info_integer.md)** — one **integer** property by enum (login, leverage, flags/modes, currency digits).
* **[AccountInfoString](./account_info_string.md)** — one **label** by enum (name, server, currency, company).

---

## 🧭 Plain English

* **AccountSummary** → the **"full blood panel"** for your account: a compact bundle you can print to see if things look sane.
* **AccountInfoDouble** → one **gauge reading** (a single float).
* **AccountInfoInteger** → **switches & knobs** (integers, often 0/1 flags or mode codes).
* **AccountInfoString** → **labels on the dashboard** (human names/brands/currency codes).

> Rule of thumb: need **many** basics at once → `AccountSummary`. Need **one** specific field → pick one of the `AccountInfo*` calls.

---

## Quick choose

| If you need…                                                    | Use                  | Returns                       | Input params                                                                              |
| --------------------------------------------------------------- | -------------------- | ----------------------------- | ----------------------------------------------------------------------------------------- |
| Core metrics in **one call**                                    | `AccountSummary`     | `AccountSummaryData` (bundle) | *(none)* + optional `deadline`, `cancellation_event`                                      |
| **One float** (equity, margin, profit, margin level, …)         | `AccountInfoDouble`  | `double`                      | `property_id: AccountInfoDoublePropertyType` + optional `deadline`, `cancellation_event`  |
| **One integer** (login, leverage, flags/modes, currency digits) | `AccountInfoInteger` | `int64`                       | `property_id: AccountInfoIntegerPropertyType` + optional `deadline`, `cancellation_event` |
| **One string** (name, server, currency, company)                | `AccountInfoString`  | `string`                      | `property_id: AccountInfoStringPropertyType` + optional `deadline`, `cancellation_event`  |

---

## 🟡 Cross‑refs & gotchas

* **Formatting money?** Combine `AccountInfoString.ACCOUNT_CURRENCY` with `AccountInfoInteger.ACCOUNT_CURRENCY_DIGITS`.
* **Margin level is percent.** `AccountInfoDouble.ACCOUNT_MARGIN_LEVEL` is already **%**, not a fraction.
* **Flags are ints.** Many boolean-like fields are `0/1` integers (e.g., `ACCOUNT_TRADE_ALLOWED`).

---

## Minimal snippets

```python
# Summary (bundle)
sum = await acct.account_summary()
print(sum.account_equity, sum.account_currency)
```

```python
# One float
equity = await acct.account_info_double(account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_EQUITY)
```

```python
# One int (digits)
digits = await acct.account_info_integer(account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_CURRENCY_DIGITS)
```

```python
# One string (currency)
curr = await acct.account_info_string(account_info_pb2.AccountInfoStringPropertyType.ACCOUNT_CURRENCY)
```

---
