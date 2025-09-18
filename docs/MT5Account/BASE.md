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

## 🧭 How to pick an API

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

# 📚 Full Index · All Method Specs

---

## 📄 Account Information

* **Overview:** [Account\_Information\_Overview.md](./Account_Information/Account_Information_Overview.md)
* **Single‑value getters**
  – [account\_info\_double.md](./Account_Information/account_info_double.md)
  – [account\_info\_integer.md](./Account_Information/account_info_integer.md)
  – [account\_info\_string.md](./Account_Information/account_info_string.md)
* **Summary**
  – [account\_summary.md](./Account_Information/account_summary.md)

---

## 📦 Orders · Positions · History

* **Overview:** [OrdersPositionsHistory\_Overview.md](./Orders_Positions_History/OrdersPositionsHistory_Overview.md)
* **Live now**
  – [opened\_orders.md](./Orders_Positions_History/opened_orders.md)
  – [opened\_orders\_tickets.md](./Orders_Positions_History/opened_orders_tickets.md)
  – [positions\_total.md](./Orders_Positions_History/positions_total.md)
* **History**
  – [order\_history.md](./Orders_Positions_History/order_history.md)
  – [positions\_history.md](./Orders_Positions_History/positions_history.md)

---

## 🏷️ Symbols and Market

* **Overview:** [SymbolsandMarket\_Overview.md](./Symbols_and_Market/SymbolsandMarket_Overview.md)

### Inventory

* [symbols\_total.md](./Symbols_and_Market/symbols_total.md)
* [symbol\_exist.md](./Symbols_and_Market/symbol_exist.md)
* [symbol\_name.md](./Symbols_and_Market/symbol_name.md)
* [symbol\_select.md](./Symbols_and_Market/symbol_select.md)
* [symbol\_is\_synchronized.md](./Symbols_and_Market/symbol_is_synchronized.md)

### Properties & Quotes

* [symbol\_params\_many.md](./Symbols_and_Market/symbol_params_many.md)
* [symbol\_info\_double.md](./Symbols_and_Market/symbol_info_double.md)
* [symbol\_info\_integer.md](./Symbols_and_Market/symbol_info_integer.md)
* [symbol\_info\_string.md](./Symbols_and_Market/symbol_info_string.md)
* [symbol\_info\_tick.md](./Symbols_and_Market/symbol_info_tick.md)

### Sessions & Margin

* [symbol\_info\_session\_quote.md](./Symbols_and_Market/symbol_info_session_quote.md)
* [symbol\_info\_session\_trade.md](./Symbols_and_Market/symbol_info_session_trade.md)
* [symbol\_info\_margin\_rate.md](./Symbols_and_Market/symbol_info_margin_rate.md)
* **Pricing utils:** [tick\_value\_with\_size.md](./Symbols_and_Market/tick_value_with_size.md)

### Market Book (DOM)

* [market\_book\_add.md](./Symbols_and_Market/market_book_add.md)
* [market\_book\_get.md](./Symbols_and_Market/market_book_get.md)
* [market\_book\_release.md](./Symbols_and_Market/market_book_release.md)

---

## 🛠 Trading Operations

* **Overview:** [TradingOperations\_Overview.md](./Trading_Operations/TradingOperations_Overview.md)
* **Placement & lifecycle**
  – [order\_send.md](./Trading_Operations/order_send.md)
  – [order\_modify.md](./Trading_Operations/order_modify.md)
  – [order\_close.md](./Trading_Operations/order_close.md)
* **Feasibility & costs**
  – [order\_check.md](./Trading_Operations/order_check.md)
  – [order\_calc\_margin.md](./Trading_Operations/order_calc_margin.md)

---

## 📡 Subscriptions · Streaming

* **Overview:** [SubscriptionsStreaming\_Overview.md](./Subscriptions_Streaming/SubscriptionsStreaming_Overview.md)
* **Prices & symbols**
  – [on\_symbol\_tick.md](./Subscriptions_Streaming/on_symbol_tick.md)
* **Trading events**
  – [on\_trade.md](./Subscriptions_Streaming/on_trade.md)
  – [on\_trade\_transaction.md](./Subscriptions_Streaming/on_trade_transaction.md)
* **P/L & IDs snapshots**
  – [on\_position\_profit.md](./Subscriptions_Streaming/on_position_profit.md)
  – [on\_positions\_and\_pending\_orders\_tickets.md](./Subscriptions_Streaming/on_positions_and_pending_orders_tickets.md)

“May your risk stay capped and your curiosity uncapped.”


