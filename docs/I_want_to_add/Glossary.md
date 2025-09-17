# 📖 Glossary

---

## Quick Cheat Sheet

| Term             | Example                              | Meaning                                                  |
| ---------------- | ------------------------------------ | -------------------------------------------------------- |
| **Symbol**       | `EURUSD`, `XAUUSD`                   | Trading instrument identifier.                           |
| **Lot**          | `1.00` → usually 100,000 units       | Standard trade size.                                     |
| **Volume**       | `0.10`, `2.50`                       | Lots to trade (can be fractional).                       |
| **SL**           | `1.09500`                            | Stop Loss — protective exit level.                       |
| **TP**           | `1.10500`                            | Take Profit — target exit level.                         |
| **Ticket**       | `12345678`                           | Unique order/position/deal ID (uint64 in most RPCs).     |
| **Digits**       | `5`                                  | Quote precision; e.g., 1.23456 for 5 digits.             |
| **Point**        | `0.00001` (EURUSD)                   | Smallest price step for the symbol.                      |
| **Pip**          | `0.0001` (most FX majors)            | Conventional 1 «pip» (may differ from `point`).          |
| **Margin**       | `100.00`                             | Funds locked for open exposure.                          |
| **Equity**       | `1000.00`                            | Balance ± floating P/L.                                  |
| **Free Margin**  | `900.00`                             | Equity − Margin.                                         |
| **Leverage**     | `1:500`                              | Borrowed funds ratio.                                    |
| **Market Watch** | **selected symbols** in the terminal | The watchlist used by `selected_only=True` in some RPCs. |
| **DOM/Book**     | Market Depth                         | Level‑2 price ladder; see *Market Book* methods.         |
| **Enum**         | `BMT5_ENUM_*`, `MRPC_ENUM_*`         | Strongly‑typed constants — no «magic numbers».           |
| **Retcode**      | `10009`, `TRADE_RETCODE_DONE`        | Trade server return code (see error mapping).            |
| **Deadline**     | `now() + 3s`                         | Per‑call absolute deadline → turned into gRPC timeout.   |
| **Cancellation** | `asyncio.Event()`                    | Cooperative stop for retry/stream wrappers.              |
| **Stream**       | `on_trade()`, `on_symbol_tick()`     | Long‑lived server push (events until cancelled).         |

---

## 📊 Order & Position Lifecycle (MT5)

```text
   ┌─────────────┐
   │  New Order  │  (market or pending)
   └──────┬──────┘
          │
          │ executed → DEAL_ADD (may create/affect POSITION)
          ▼
   ┌─────────────┐
   │   Opened    │  (POSITION with floating P/L)
   └───┬─────┬───┘
      SL     TP
      │      │
      ▼      ▼
   ┌─────────────┐      pending order can be
   │   Closed    │ ◄─── deleted/cancelled before fill
   └─────────────┘
```

*MT5 note:* in **hedging** mode multiple positions per symbol can coexist; in **netting** — one net position per symbol.

---

## 🧑‍💻 Account Terms

* **Login / Server** — broker account ID and server name.
* **Balance / Equity / Margin / Free** — see cheat sheet; numbers come from [Account Info methods](./Account_Information/Account_Information_Overview.md).
* **Currency Digits** — use `ACCOUNT_CURRENCY_DIGITS` (integer) to format money correctly.

---

## 📈 Market Info Terms

* **Symbol Inventory** — size & presence checks:
  – [symbols\_total.md](./Symbols_and_Market/symbols_total.md), [symbol\_exist.md](./Symbols_and_Market/symbol_exist.md), [symbol\_name.md](./Symbols_and_Market/symbol_name.md), [symbol\_select.md](./Symbols_and_Market/symbol_select.md)
* **Properties** — double/int/string getters & bulk params:
  – [symbol\_info\_double.md](./Symbols_and_Market/symbol_info_double.md), [symbol\_info\_integer.md](./Symbols_and_Market/symbol_info_integer.md), [symbol\_info\_string.md](./Symbols_and_Market/symbol_info_string.md), [symbol\_params\_many.md](./Symbols_and_Market/symbol_params_many.md)
* **Quotes & Sessions** — tick snapshot and trading/quote sessions:
  – [symbol\_info\_tick.md](./Symbols_and_Market/symbol_info_tick.md), [symbol\_info\_session\_quote.md](./Symbols_and_Market/symbol_info_session_quote.md), [symbol\_info\_session\_trade.md](./Symbols_and_Market/symbol_info_session_trade.md)
* **Margin model** — per‑order type margin rate & calc helpers:
  – [symbol\_info\_margin\_rate.md](./Symbols_and_Market/symbol_info_margin_rate.md), [order\_calc\_margin.md](./Trading_Operations/order_calc_margin.md), [tick\_value\_with\_size.md](./Symbols_and_Market/tick_value_with_size.md)
* **Market Book (DOM)** — subscribe/read/release:
  – [market\_book\_add.md](./Symbols_and_Market/market_book_add.md) → [market\_book\_get.md](./Symbols_and_Market/market_book_get.md) → [market\_book\_release.md](./Symbols_and_Market/market_book_release.md)

---

## 📦 Orders & History Terms

* **Live snapshot** — [opened\_orders.md](./Orders_Positions_History/opened_orders.md) (orders + positions) and IDs‑only [opened\_orders\_tickets.md](./Orders_Positions_History/opened_orders_tickets.md).
* **History** — [order\_history.md](./Orders_Positions_History/order_history.md) (orders+deals), [positions\_history.md](./Orders_Positions_History/positions_history.md).
* **Count** — [positions\_total.md](./Orders_Positions_History/positions_total.md).

---

## 🔌 RPC & Streaming Terms

* **Unary RPC** — one request → one reply; returns `*.Data` payload already unwrapped.
* **Streaming RPC** — server pushes events until you cancel:
  – [on\_symbol\_tick.md](./Subscriptions_Streaming/on_symbol_tick.md),
  – [on\_trade.md](./Subscriptions_Streaming/on_trade.md),
  – [on\_trade\_transaction.md](./Subscriptions_Streaming/on_trade_transaction.md),
  – [on\_position\_profit.md](./Subscriptions_Streaming/on_position_profit.md),
  – [on\_positions\_and\_pending\_orders\_tickets.md](./Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md)
* **Deadline & Cancellation** — pass `deadline` (to set timeout) and `cancellation_event` (to stop cleanly).

---

## 🛡️ Errors & Codes

* **gRPC transport** — timeouts, unavailables; wrappers auto‑retry via `execute_with_reconnect(...)`.
* **Trade retcodes** — see numeric+string mapping in `package/MetaRpcMT5/mrpc_mt5_error_pb2.py` and docs for `order_*` / `on_trade_transaction`.
* **Validation** — prefer enums over raw ints/strings to avoid typos.

---

## ✅ One‑page Summary

* **Account** — who you are & your limits.
* **Market Info** — what you can trade and how it’s specified.
* **Orders/History** — what’s live & what happened before.
* **RPC** — unary vs streaming, with deadlines & cancellation.
* **Errors** — retcodes & transport issues, surfaced cleanly by the SDK.

