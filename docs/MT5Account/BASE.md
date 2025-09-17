# MT5Account — Master Overview

> One page to **orient fast**: what lives where, how to choose the right API, and jump links to every **overview** and **method spec** in this docs set.

---

## 🚦 Start here — Section Overviews

* **[Account\_Information — Overview](./Account_Information/Account_Information_Overview.md)**
  Account balance/equity/margins, single‑value getters & summary.

* **[Orders.Positions.History — Overview](./Orders_Positions_History/OrdersPositionsHistory_Overview.md)**
  What’s open now, tickets, orders/deals history, positions history.

* **[Symbols\_and\_Market — Overview](./Symbols_and_Market/SymbolsandMarket_Overview.md)**
  Symbols inventory, properties, sessions, margin rates, market book (DOM).

* **[Trading\_Operations — Overview](./Trading_Operations/TradingOperations_Overview.md)**
  Place/modify/close orders, preflight checks, margin calculations.

* **[Subscriptions\_Streaming — Overview](./Subscriptions_Streaming/SubscriptionsStreaming_Overview.md)**
  Live streams: ticks, trade deltas, transactions, P/L snapshots, IDs‑only.

---

## 🧭 How to pick an API (very short)

| If you need…                   | Go to…                   | Typical calls                                                                                                         |
| ------------------------------ | ------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| A single account metric        | Account\_Information     | `account_info_double/integer/string`, `account_summary`                                                               |
| Live objects or history        | Orders.Positions.History | `opened_orders`, `opened_orders_tickets`, `order_history`, `positions_history`, `positions_total`                     |
| Symbol specs & market plumbing | Symbols\_and\_Market     | `symbol_info_*`, `symbols_total`, `market_book_*`                                                                     |
| Trading actions / feasibility  | Trading\_Operations      | `order_send/modify/close`, `order_check`, `order_calc_margin`                                                         |
| Realtime updates               | Subscriptions\_Streaming | `on_symbol_tick`, `on_trade`, `on_trade_transaction`, `on_position_profit`, `on_positions_and_pending_orders_tickets` |

---

## 🔌 Usage pattern (SDK wrappers)

Every method follows the same shape:

* **Service/Method (gRPC):** `Service.Method(Request) → Reply`
* **Low-level stub:** `ServiceStub.Method(request, metadata, timeout)`
* **SDK wrapper (what you call):** `await MT5Account.method_name(..., deadline=None, cancellation_event=None)`
* **Reply:** SDK returns **`.data`** payload (already unwrapped) unless otherwise noted.

Timestamps = **UTC** (`google.protobuf.Timestamp`). For long‑lived streams, pass a **`cancellation_event`**.

---

## 📚 Full Index · All Method Specs

### Account\_Information

* [account\_info\_double.md](./Account_Information/account_info_double.md)
* [account\_info\_integer.md](./Account_Information/account_info_integer.md)
* [account\_info\_string.md](./Account_Information/account_info_string.md)
* [account\_summary.md](./Account_Information/account_summary.md)

---

### Orders\_Positions\_History

* [opened\_orders.md](./Orders_Positions_History/opened_orders.md)
* [opened\_orders\_tickets.md](./Orders_Positions_History/opened_orders_tickets.md)
* [order\_history.md](./Orders_Positions_History/order_history.md)
* [positions\_history.md](./Orders_Positions_History/positions_history.md)
* [positions\_total.md](./Orders_Positions_History/positions_total.md)

---

### Symbols\_and\_Market

* [symbols\_total.md](./Symbols_and_Market/symbols_total.md)
* [symbol\_exist.md](./Symbols_and_Market/symbol_exist.md)
* [symbol\_name.md](./Symbols_and_Market/symbol_name.md)
* [symbol\_select.md](./Symbols_and_Market/symbol_select.md)
* [symbol\_is\_synchronized.md](./Symbols_and_Market/symbol_is_synchronized.md)
* [symbol\_params\_many.md](./Symbols_and_Market/symbol_params_many.md)
* [symbol\_info\_double.md](./Symbols_and_Market/symbol_info_double.md)
* [symbol\_info\_integer.md](./Symbols_and_Market/symbol_info_integer.md)
* [symbol\_info\_string.md](./Symbols_and_Market/symbol_info_string.md)
* [symbol\_info\_tick.md](./Symbols_and_Market/symbol_info_tick.md)
* [symbol\_info\_margin\_rate.md](./Symbols_and_Market/symbol_info_margin_rate.md)
* [symbol\_info\_session\_quote.md](./Symbols_and_Market/symbol_info_session_quote.md)
* [symbol\_info\_session\_trade.md](./Symbols_and_Market/symbol_info_session_trade.md)
* Market Book (DOM): [market\_book\_add.md](./Symbols_and_Market/market_book_add.md), [market\_book\_get.md](./Symbols_and_Market/market_book_get.md), [market\_book\_release.md](./Symbols_and_Market/market_book_release.md)
* Pricing utils: [tick\_value\_with\_size.md](./Symbols_and_Market/tick_value_with_size.md)

---

### Trading\_Operations

* [order\_send.md](./Trading_Operations/order_send.md)
* [order\_modify.md](./Trading_Operations/order_modify.md)
* [order\_close.md](./Trading_Operations/order_close.md)
* [order\_check.md](./Trading_Operations/order_check.md)
* [order\_calc\_margin.md](./Trading_Operations/order_calc_margin.md)

---

### Subscriptions\_Streaming

* [on\_symbol\_tick.md](./Subscriptions_Streaming/on_symbol_tick.md)
* [on\_trade.md](./Subscriptions_Streaming/on_trade.md)
* [on\_trade\_transaction.md](./Subscriptions_Streaming/on_trade_transaction.md)
* [on\_position\_profit.md](./Subscriptions_Streaming/on_position_profit.md)
* [on\_positions\_and\_pending\_orders\_tickets.md](./Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md)

---

## 🪪 Common enums (where to find)

* **Order/Position enums** — in the method pages; proto sources: `mt5_term_api_trading_helper_pb2.py`, `mt5_term_api_market_info_pb2.py`.
* **Trading request/transaction enums** — see Trading\_Operations & Subscriptions; proto sources: `mt5_term_api_trade_functions_pb2.py`, `mt5_term_api_subscriptions_pb2.py`, and error codes in `mrpc_mt5_error_pb2.py` (`MqlErrorTradeCode`).

---

## 🧩 Cross‑cutting notes & tips

* **Timezones:** all times are **UTC**. Convert once for UI.
* **Money formatting:** use account currency digits from `account_info_integer` (`ACCOUNT_CURRENCY_DIGITS`).
* **Filling & time policies:** set explicitly (`*_FOK/IOC/RETURN/BOC`, `*_GTC/DAY/SPECIFIED/SPECIFIED_DAY`).
* **Streams:** always wire a `cancellation_event` and keep handlers lightweight (fan‑out to queues if needed).
* **Retries:** SDK wrappers use `execute_with_reconnect(...)` to handle transient gRPC issues.

---

## 🔗 Also useful

* Top‑level docs:

  * [`docs/index.md`](../index.md) — portal page
  * [`docs/api.md`](../api.md) — project API notes (if present)
* Examples:

  * `examples/quick_start_connect.py` — minimal connect
  * `examples/mt5_account_ex.py` — end‑to‑end usage

> If you add a new method doc, place it in the right folder and add the link here **and** to the folder’s own Overview page.

