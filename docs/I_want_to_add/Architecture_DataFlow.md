# 🏗️ Architecture & Data Flow (PyMT5 + MT5)

*A practical map of how our Python SDK, gRPC services, and the MT5 terminal talk to each other — with just enough humor to keep the margin level above 100%.*

---

## 🗺️ Big Picture

```
             ┌───────────────────────────────┐
             │        🖥️ MT5 Terminal        │
             │ (broker login, quotes, trades)│
             └───────────────┬───────────────┘
                             │ local/IPC
                             ▼
             ┌────────────────────────────────┐
             │  mt5_term_api.*  (gRPC server) │
             │  Services: MarketInfo, Trade.. │
             └───────────────┬────────────────┘
                             │ gRPC
                             ▼
     ┌───────────────────────────────────────────────────┐
     │  📦 Python SDK (MetaRpcMT5)                        │
     │  MT5Account (package/MetaRpcMT5/mt5_account.py)   │
     │  + generated pb2/pb2_grpc stubs                   │
     └───────────────┬───────────────────────────────────┘
                     │ async await
                     ▼
        ┌───────────────────────────────┐
        │  👩‍💻 Your App / Examples      │
        │  (docs, examples, services)   │
        └───────────────────────────────┘
```

**You write**: high‑level `await acct.method(...)` calls.
**SDK does**: request building, metadata, deadlines, retries, unwraps `.reply.data`.
**Server does**: talks to the real MT5 terminal and executes.

---

## ⚙️ Main Components (by folders)

### 🔩 SDK & gRPC contracts (client side)

* `package/MetaRpcMT5/mt5_account.py` — **MT5Account** wrappers (public API).
* `package/MetaRpcMT5/mt5_term_api_*.py` — **pb2** messages (requests/replies/enums).
* `package/MetaRpcMT5/mt5_term_api_*_pb2_grpc.py` — **stubs** (client bindings).
* `package/MetaRpcMT5/mrpc_mt5_error_pb2.py` — errors/retcodes mapping.

### 🧠 App layer & helpers (optional services)

* `app/core/mt5_connect_helper.py` — connection bootstrap, metadata.
* `app/core/mt5_service.py` — higher‑level service orchestration.
* `app/services/streams_service.py` — stream fan‑out (ticks/trade events).
* `app/services/trading_service.py` — trading flows (send/modify/close).
* `app/services/history_service.py` — history pagination & caching.
* `app/patches/*.py` — compatibility tweaks (symbol params, market info, etc.).

### 📚 Docs & Examples

* `docs/MT5Account/**` — method specs & overviews (what you read now).
* `examples/quick_start_connect.py` — minimal bootstrap.
* `examples/mt5_account_ex.py` — end‑to‑end usage playground.

---

## 🔀 Data Flow (Unary)

1. **Your call** → \`await acct.symbol\_info\_double(...)
2. **Wrapper** builds `Request`, sets `metadata`, computes `timeout` from `deadline`.
3. **Stub** → `ServiceStub.Method(request, metadata, timeout)`.
4. **Server** performs the operation via MT5 terminal.
5. **Reply** → SDK unwraps `reply.data` → you get clean `*.Data` (or a primitive like `float`).

```python
from MetaRpcMT5 import mt5_term_api_account_information_pb2 as ai_pb2
value = await acct.account_info_double(ai_pb2.AccountInfoDoublePropertyType.ACCOUNT_EQUITY)
print(f"Equity: {value:.2f}")
```

---

## 🔄 Data Flow (Streaming)

Streams keep a channel open and push events. Use **cancellation\_event** and keep handlers **non‑blocking**.

```python
import asyncio
stop = asyncio.Event()
async for ev in acct.on_trade(cancellation_event=stop):
    queue.put_nowait(ev)  # heavy work elsewhere
    if should_stop(ev):
        stop.set()
```

Common streams:

* `on_symbol_tick` — live ticks per symbol.
* `on_trade` — high‑level deltas (orders/positions/deals) + account snapshot.
* `on_trade_transaction` — low‑level transaction + request + result.
* `on_position_profit` — timed P/L frames for positions.
* `on_positions_and_pending_orders_tickets` — IDs‑only snapshots for set‑diff.

Links: [Subscriptions Overview](./Subscriptions_Streaming/SubscriptionsStreaming_Overview.md)

---

## 🧩 RPC Domains & Where to Look

* **Account Info** → balance/equity/margins:
  [Overview](./Account_Information/Account_Information_Overview.md)
* **Orders · Positions · History** → live & past trading objects:
  [Overview](./Orders_Positions_History/OrdersPositionsHistory_Overview.md)
* **Symbols & Market** → symbol catalog, properties, sessions, DOM:
  [Overview](./Symbols_and_Market/SymbolsandMarket_Overview.md)
* **Trading Ops** → send/modify/close, checks, margin calc:
  [Overview](./Trading_Operations/TradingOperations_Overview.md)

---

## ✨ Highlights

* **Wrappers return payloads** (`*.Data`) already unwrapped from replies.
* **Deadlines** become stub timeouts; pass them for predictable latency.
* **Retries & reconnects** handled in wrappers (`execute_with_reconnect(...)`).
* **UTC timestamps** everywhere; convert once near UI.
* **Server‑side sorting** via enums; client‑side filtering for symbol lists is often cheaper.

---

## 🛠️ Developer Notes

* Prefer enums from pb2 (no “magic numbers”).
* For Market Book use the trio:
  [market\_book\_add](./Symbols_and_Market/market_book_add.md) → [market\_book\_get](./Symbols_and_Market/market_book_get.md) → [market\_book\_release](./Symbols_and_Market/market_book_release.md).
* Cold‑start: get a full snapshot once ([OpenedOrders](./Orders_Positions_History/opened_orders.md)), then maintain via streams.
* Cheap change detection: IDs‑only stream → fetch details **only** on change.

---

## 📦 Minimal Bootstrap (Example)

```python
from MetaRpcMT5.mt5_account import MT5Account
from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as ah_pb2

acct = MT5Account(...)
od = await acct.opened_orders(
    ah_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
print(len(od.opened_orders), len(od.position_infos))
```

---

## 🧪 Debug & Troubleshooting

* Log transport issues with `app/utils/grpc_debug.py`.
* Keep both **retcode int** and **string** (see `mrpc_mt5_error_pb2.py`).
* If a stream "goes quiet", check that your handler isn’t blocking and the **release** was not called prematurely (DOM).

---

## ❓FAQ

**Can I skip `deadline`?** You can, but stable timeouts make ops happy.
**Why IDs‑only streams?** They’re cheap and perfect for set‑diff; pull details on demand.
**Where are enums?** In the relevant `mt5_term_api_*_pb2.py` files next to each method’s doc.
