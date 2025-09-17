# 🚗 Under the Hood — a friendly RPC guide

## TL;DR

1. Protocol method → `Service.Method(Request) → Reply`
2. Low‑level stub → `ServiceStub.Method(request, metadata, timeout)`
3. **SDK wrapper** → `await MT5Account.method_name(..., deadline=None, cancellation_event=None)` and it **returns the `*.Data` payload** (already unwrapped).
4. **UTC timestamps everywhere.** Convert once at the UI boundary.
5. **Streams** are infinite → always pass a `cancellation_event` and keep handlers non‑blocking.

Full map: see **BASE**.
Overviews:  [Account Info](./Account_Information/Account_Information_Overview.md) · [Orders/Positions/History](./Orders_Positions_History/OrdersPositionsHistory_Overview.md) · [Symbols & Market](./Symbols_and_Market/SymbolsandMarket_Overview.md) · [Trading Ops](./Trading_Operations/TradingOperations_Overview.md) · [Subscriptions](./Subscriptions_Streaming/SubscriptionsStreaming_Overview.md)

---

## Anatomy of a call

```python
# Unary call pattern
from datetime import datetime, timedelta, timezone
value = await acct.account_info_double(
    property_id=...,  # enum
    deadline=datetime.now(timezone.utc) + timedelta(seconds=3),
)
# value is already the float from *.Data
```

**Deadline?** Becomes gRPC `timeout`.
**Cancellation?** Graceful stop for retries/streams.

The wrappers use `execute_with_reconnect(...)` for **retries** on transient errors and **terminal reconnects**. Practical upshot:

* You don’t need try/except around every call — only where you act differently by error type.
* Focus on **business logic** (what to do on timeout/retcode), not plumbing.

---

## Unary vs. Streaming

**Unary** — most `*Info*`, `*History*`, `order_*`.
**Streaming** — [on\_symbol\_tick](./Subscriptions_Streaming/on_symbol_tick.md), [on\_trade](./Subscriptions_Streaming/on_trade.md), [on\_trade\_transaction](./Subscriptions_Streaming/on_trade_transaction.md), [on\_position\_profit](./Subscriptions_Streaming/on_position_profit.md), [on\_positions\_and\_pending\_orders\_tickets](./Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md).

Streaming pattern:

```python
import asyncio
stop = asyncio.Event()
async for ev in acct.on_trade(cancellation_event=stop):
    queue.put_nowait(ev)  # heavy lifting goes to workers
    if should_stop(ev):
        stop.set()
```

**Back‑pressure 101:** keep the per‑event handler light → fan‑out to queues/workers → aggregate in your store → render.

---

## Enums, types & the “magic numbers” ban

* Don’t hardcode integers. Use the **enums** from the relevant `pb2`.
* Common sets:
  – Order types / filling / time → Trading Ops docs and [order\_send](./Trading_Operations/order_send.md), [order\_check](./Trading_Operations/order_check.md).
  – Order/Position states → [OpenedOrders](./Orders_Positions_History/opened_orders.md).

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as ai_pb2
level = await acct.account_info_double(ai_pb2.AccountInfoDoublePropertyType.ACCOUNT_MARGIN_LEVEL)
print(f"Margin Level: {level:.1f}%")
```

---

## Time handling

* Everything is **UTC** (`google.protobuf.Timestamp` or `time_msc`).
* Convert to local time **once** at the UI edge.
* For history, use closed‑open ranges (`from <= x < to`) and let the server **sort via enum**.

---

## Live + History: best friends

**Cold start:** take one snapshot (e.g., [OpenedOrders](./Orders_Positions_History/opened_orders.md)), then keep it fresh via a stream — [on\_trade](./Subscriptions_Streaming/on_trade.md) or [on\_trade\_transaction](./Subscriptions_Streaming/on_trade_transaction.md).
**Cheap monitoring:** use the IDs‑only stream [on\_positions\_and\_pending\_orders\_tickets](./Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md) and pull details **only on change**.

---

## Trade lifecycle: send → check → modify → close

* **Pre‑flight:** [order\_check](./Trading_Operations/order_check.md) and/or [order\_calc\_margin](./Trading_Operations/order_calc_margin.md).
* **Send:** [order\_send](./Trading_Operations/order_send.md) (always set filling/time explicitly).
* **Modify / Close:** [order\_modify](./Trading_Operations/order_modify.md), [order\_close](./Trading_Operations/order_close.md).
* **Diagnostics:** [on\_trade\_transaction](./Subscriptions_Streaming/on_trade_transaction.md) — pairs `request + result` with retcodes.

```python
from MetaRpcMT5 import mt5_term_api_trade_functions_pb2 as tf_pb2
rq = tf_pb2.MqlTradeRequest(
    order_type_filling=tf_pb2.SUB_ENUM_ORDER_TYPE_FILLING.ORDER_FILLING_FOK,
    type_time=tf_pb2.SUB_ENUM_ORDER_TYPE_TIME.ORDER_TIME_GTC,
)
```

---

## 🟢 Market Book (DOM)

The trio: [market\_book\_add](./Symbols_and_Market/market_book_add.md) → [market\_book\_get](./Symbols_and_Market/market_book_get.md) → [market\_book\_release](./Symbols_and_Market/market_book_release.md).

Subscribe → read → **always** release when leaving the page. DOM subscriptions are not houseplants; don’t forget to water them… with a `release()`.

---

## Errors & retcodes

* gRPC/network issues — wrappers retry.
* Trading **retcodes** — see `mrpc_mt5_error_pb2.py` and the `order_*`/`on_trade_transaction` pages.
* For UX/logging, keep both **numeric code** and **human string**.

Normalization sketch:

```python
def normalize_trade_result(r):
    return {
        "retcode": r.trade_return_int_code,
        "code": int(r.trade_return_code),
        "desc": getattr(r, "retcode_code_description", ""),
        "price": r.deal_price or r.price,
    }
```

---

## Performance notes

* **Sort server‑side** via enums; symbol filters are often cheaper **client‑side**.
* Batch/aggregate inside workers for streaming P/L rather than re‑rendering every tick.
* For big tables: combine RPC pagination (history) with a local cache.

---

## Mini‑recipes

**1) Stable snapshot of live objects**

```python
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2
od = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
```

**2) Set‑diff via IDs stream**

```python
prev = (set(), set())
async for ev in acct.on_positions_and_pending_orders_tickets(750):
    pos, ords = set(ev.opened_position_tickets), set(ev.opened_orders_tickets)
    if (pos, ords) != prev:
        # fetch heavy details only on change
        prev = (pos, ords)
```

**3) De‑noise P/L streaming**

```python
async for ev in acct.on_position_profit(1000, True):
    if not (ev.new_positions or ev.updated_positions or ev.deleted_positions):
        continue
    process(ev)
```

---

## 🟡 FAQ

* **Why enums over strings?** — Fewer typos, clearer intent, linters help.
* **Can I skip `deadline`?** — You can, but deterministic timeouts make ops happier.
* **Why IDs‑only streams?** — They’re **cheap** and perfect for change detection; pull details on demand.

