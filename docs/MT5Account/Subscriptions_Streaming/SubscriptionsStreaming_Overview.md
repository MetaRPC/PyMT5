# MT5Account · Subscriptions\_Streaming — Overview

> Quick map of the **live streaming** APIs: ticks, trade deltas, transactions, position P/L, and IDs-only snapshots. Use this to pick the right stream fast.

## 📁 What lives here

* **[on\_symbol\_tick](./on_symbol_tick.md)** — live **tick** stream per symbol (Bid/Ask/Last, volumes, flags, time).
* **[on\_trade](./on_trade.md)** — high‑level **order/position/deal** deltas + **account P/L snapshot** per event.
* **[on\_trade\_transaction](./on_trade_transaction.md)** — low‑level **transaction** feed: *transaction + request + result*.
* **[on\_position\_profit](./on_position_profit.md)** — periodic **P/L snapshots** for positions (new/updated/deleted) + account info.
* **[on\_positions\_and\_pending\_orders\_tickets](./on_positions_and_pending_orders_tickets.md)** — periodic **IDs‑only** snapshot of **position** and **pending order** tickets.

---

## 🧭 Plain English

* **on\_symbol\_tick** → your **price heartbeat** (per‑symbol ticks for UI/algos).
* **on\_trade** → **state deltas** (orders/positions/deals) bundled for easy UI sync.
* **on\_trade\_transaction** → **audit‑level** stream with request/result pairing.
* **on\_position\_profit** → **P/L ticker** for positions on a timer.
* **on\_positions\_and\_pending\_orders\_tickets** → **cheap set‑diff** source (IDs only).

> Rule of thumb: need **prices** → `on_symbol_tick`; need **deltas** → `on_trade`; need **audit** → `on_trade_transaction`; need **P/L** → `on_position_profit`; need **change detection** → IDs‑only stream.

---

## Quick choose

| If you need…                               | Use                                       | Returns                                             | Key inputs                                        |
| ------------------------------------------ | ----------------------------------------- | --------------------------------------------------- | ------------------------------------------------- |
| Live ticks (Bid/Ask/Last/flags/time)       | `on_symbol_tick`                          | **stream** `OnSymbolTickData`                       | `symbols: list[str]`, `cancellation_event?`       |
| Deltas of orders/positions/deals + account | `on_trade`                                | **stream** `OnTradeData`                            | `cancellation_event?`                             |
| Raw transactions with request+result       | `on_trade_transaction`                    | **stream** `OnTradeTransactionData`                 | `cancellation_event?`                             |
| Timed position P/L snapshots               | `on_position_profit`                      | **stream** `OnPositionProfitData`                   | `interval_ms:int`, `ignore_empty:bool`, `cancel?` |
| IDs‑only snapshot (positions & pendings)   | `on_positions_and_pending_orders_tickets` | **stream** `OnPositionsAndPendingOrdersTicketsData` | `interval_ms:int`, `cancellation_event?`          |

---

## ❌ Cross‑refs & gotchas

* **Long‑lived streams** — always support a `cancellation_event` and stop cleanly on page change/shutdown.
* **UTC times** — `Timestamp`/`time_msc` are UTC; convert once for UI.
* **Back‑pressure** — keep per‑event handlers light; push to queues if you do heavy work.
* **Cold start** — use `OpenedOrders` (or other snapshot RPCs) once, then rely on streams.
* **IDs vs full objects** — tickets stream is for **set‑diff**; fetch details only on change.

---

## 🟢 Minimal snippets

```python
# on_symbol_tick — print Bid/Ask
async for ev in acct.on_symbol_tick(["EURUSD", "XAUUSD"]):
    t = ev.symbol_tick
    print(t.symbol, t.bid, t.ask)
```

```python
# on_trade — count changed objects per event
async for ev in acct.on_trade():
    d = ev.event_data
    print(len(d.new_orders), len(d.updated_positions), len(d.new_history_deals))
```

```python
# on_trade_transaction — show type and ids
async for ev in acct.on_trade_transaction():
    tr = ev.trade_transaction
    print(tr.type, tr.order_ticket, tr.deal_ticket)
```

```python
# on_position_profit — sum current P/L in the batch
async for ev in acct.on_position_profit(1000, True):
    print(sum(p.profit for p in (ev.updated_positions or [])))
```

```python
# on_positions_and_pending_orders_tickets — diff detector
prev_pos, prev_ord = set(), set()
async for ev in acct.on_positions_and_pending_orders_tickets(750):
    pos, ords = set(ev.opened_position_tickets), set(ev.opened_orders_tickets)
    if (pos != prev_pos) or (ords != prev_ord):
        print("changed")
        prev_pos, prev_ord = pos, ords
```
