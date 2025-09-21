# ✅ Positions History

> **Request:** paginated **positions history** for a time range.
> Server‑side sorted pages of historical **positions** (open→close lifecycle, PnL, fees).

**Source files:**

* `MetaRpcMT5/mt5_account.py` — method `positions_history(...)`
* `MetaRpcMT5/mt5_term_api_account_helper_pb2.py` — `PositionsHistory*`, `PositionsHistoryData`, `PositionHistoryData`, `BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE`

---

### RPC

* **Service:** `mt5_term_api.AccountHelper`
* **Method:** `PositionsHistory(PositionsHistoryRequest) → PositionsHistoryReply`
* **Low-level client:** `AccountHelperStub.PositionsHistory(request, metadata, timeout)`
* **SDK wrapper:** `MT5Account.positions_history(sort_type, open_from, open_to, page=1, size=100, deadline=None, cancellation_event=None)`

---

### 🔗 Code Example

```python
# Minimal canonical example: last 30 days, sort by CLOSE_TIME desc
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
res = await acct.positions_history(
    sort_type=ah_pb2.BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE.BMT5_POSHIST_SORT_BY_CLOSE_TIME_DESC,
    open_from=now - timedelta(days=30),
    open_to=now,
    page=1,
    size=100,
)

print(res.array_total, len(res.positions_data))  # total items, items on this page
```

---

### Method Signature

```python
async def positions_history(
    self,
    sort_type: account_helper_pb2.BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE,
    open_from: datetime,
    open_to: datetime,
    page: int = 1,
    size: int = 100,
    deadline: datetime | None = None,
    cancellation_event: asyncio.Event | None = None,
) -> account_helper_pb2.PositionsHistoryData
```

---

## 💬 Plain English

* **What it is.** A **closed positions ledger**: each row is a position’s life story — opened at X, closed at Y, with PnL/fees and reasons.
* **Why you care.** PnL reporting, compliance/audit, and troubleshooting sequences (“when/why did this position close?”).
* **Mind the traps.**

  * It’s **paginated**; read `array_total/page_number/items_per_page` to loop properly.
  * All times are UTC `Timestamp`s; convert once before rendering.
  * Positions history ≠ order/deal history; fields are position‑level (aggregated), not individual deal lines.

---

## 🔽 Input

| Parameter            | Type                                                         | Description                                 |                                           |
| -------------------- | ------------------------------------------------------------ | ------------------------------------------- | ----------------------------------------- |
| `sort_type`          | `BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE` (enum, **required**) | Server‑side sort (see enum below).          |                                           |
| `open_from`          | `datetime` (UTC)                                             | Start of the time window for **open time**. |                                           |
| `open_to`            | `datetime` (UTC)                                             | End of the time window for **open time**.   |                                           |
| `page`               | `int`                                                        | 1‑based page number.                        |                                           |
| `size`               | `int`                                                        | Items per page (e.g., 50/100/500).          |                                           |
| `deadline`           | \`datetime                                                   | None\`                                      | Absolute per‑call deadline → timeout.     |
| `cancellation_event` | \`asyncio.Event                                              | None\`                                      | Cooperative cancel for the retry wrapper. |

> **Request message:** `PositionsHistoryRequest { position_open_time_from, position_open_time_to, sort_type, page_number, items_per_page }`

---

## ⬆️ Output

### Payload: `PositionsHistoryData`

| Field            | Proto Type                     | Description                         |
| ---------------- | ------------------------------ | ----------------------------------- |
| `array_total`    | `int32`                        | Total number of items across pages. |
| `page_number`    | `int32`                        | Page number of this reply.          |
| `items_per_page` | `int32`                        | Items per page of this reply.       |
| `positions_data` | `repeated PositionHistoryData` | Page of closed/opened positions.    |

#### Message: `PositionHistoryData`

| Field                 | Type                        | Notes                                 |
| --------------------- | --------------------------- | ------------------------------------- |
| `index`               | `uint32`                    | Internal ordering index.              |
| `ticket`              | `uint64`                    | Position ticket ID.                   |
| `identifier`          | `int64`                     | Position identifier.                  |
| `symbol`              | `string`                    | Symbol.                               |
| `type`                | `BMT5_ENUM_POSITION_TYPE`   | BUY/SELL.                             |
| `reason`              | `BMT5_ENUM_POSITION_REASON` | CLIENT/EXPERT/SL/TP/SO/…              |
| `open_time`           | `Timestamp`                 | When opened.                          |
| `close_time`          | `Timestamp`                 | When closed.                          |
| `volume_initial`      | `double`                    | Initial volume.                       |
| `volume`              | `double`                    | Final volume (at close).              |
| `price_open`          | `double`                    | Open price.                           |
| `price_close`         | `double`                    | Close price.                          |
| `stop_loss`           | `double`                    | SL.                                   |
| `take_profit`         | `double`                    | TP.                                   |
| `swap`                | `double`                    | Swap accrued.                         |
| `profit`              | `double`                    | Position PnL.                         |
| `commission`          | `double`                    | Commission.                           |
| `position_commission` | `double`                    | Per‑position commission (if present). |
| `magic_number`        | `int64`                     | EA/strategy tag.                      |
| `account_login`       | `int64`                     | Account login.                        |

---

### Enum: `BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE`

| Number | Value                                          | Meaning                |
| -----: | ---------------------------------------------- | ---------------------- |
|      0 | `BMT5_POSHIST_SORT_BY_OPEN_TIME_ASC`           | Open time ascending.   |
|      1 | `BMT5_POSHIST_SORT_BY_OPEN_TIME_DESC`          | Open time descending.  |
|      2 | `BMT5_POSHIST_SORT_BY_CLOSE_TIME_ASC`          | Close time ascending.  |
|      3 | `BMT5_POSHIST_SORT_BY_CLOSE_TIME_DESC`         | Close time descending. |
|      4 | `BMT5_POSHIST_SORT_BY_POSITION_TICKET_ID_ASC`  | Ticket ascending.      |
|      5 | `BMT5_POSHIST_SORT_BY_POSITION_TICKET_ID_DESC` | Ticket descending.     |

> Related enums used above: `BMT5_ENUM_POSITION_TYPE`, `BMT5_ENUM_POSITION_REASON`.

---

## Usage Examples

### 1) Last month PnL by symbol

```python
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
from_dt = (now.replace(day=1) - timedelta(days=1)).replace(day=1)

page, size = 1, 200
pnl_by_symbol = {}
while True:
    res = await acct.positions_history(
        ah_pb2.BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE.BMT5_POSHIST_SORT_BY_CLOSE_TIME_DESC,
        open_from=from_dt,
        open_to=now,
        page=page,
        size=size,
    )
    for ph in res.positions_data:
        sym = ph.symbol
        pnl_by_symbol[sym] = pnl_by_symbol.get(sym, 0.0) + float(ph.profit)
    if len(res.positions_data) < size:
        break
    page += 1

for sym, pnl in sorted(pnl_by_symbol.items()):
    print(sym, round(pnl, 2))
```

### 2) Only SELL positions, last 7 days

```python
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

now = datetime.now(timezone.utc)
res = await acct.positions_history(
    ah_pb2.BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE.BMT5_POSHIST_SORT_BY_OPEN_TIME_ASC,
    now - timedelta(days=7), now,
    1, 100
)
only_sell = [p for p in res.positions_data if int(p.type) == 1]  # assuming 0=BUY,1=SELL
print(len(only_sell))
```

### 3) With deadline & cancellation

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

cancel_event = asyncio.Event()
res = await acct.positions_history(
    ah_pb2.BMT5_ENUM_POSITIONS_HISTORY_SORT_TYPE.BMT5_POSHIST_SORT_BY_POSITION_TICKET_ID_ASC,
    datetime.now(timezone.utc) - timedelta(days=1),
    datetime.now(timezone.utc),
    1, 100,
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
    cancellation_event=cancel_event,
)
print(res.size)
```
