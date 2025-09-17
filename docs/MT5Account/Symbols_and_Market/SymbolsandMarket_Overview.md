# MT5Account · Symbols and Market — Overview

> Quick map of **symbols, sessions, and market‑book** APIs. Use this page to pick the right call fast. Links jump to detailed specs.

## 📁 What lives here

* **[symbols\_total](./symbols_total.md)** — count of **all** symbols vs **Market Watch** only.
* **[symbol\_name](./symbol_name.md)** — resolve **symbol name by index** (all vs selected list).
* **[symbol\_exist](./symbol_exist.md)** — does a symbol exist? Is it **custom**?
* **[symbol\_select](./symbol_select.md)** — add/remove a symbol to/from **Market Watch**.
* **[symbol\_is\_synchronized](./symbol_is_synchronized.md)** — is the symbol **synced** in terminal.
* **[symbol\_info\_tick](./symbol_info_tick.md)** — latest **tick** (Bid/Ask/Last, volumes, time, flags).
* **[symbol\_info\_double](./symbol_info_double.md)** — one **double** prop (enum: `SymbolInfoDoubleProperty`).
* **[symbol\_info\_integer](./symbol_info_integer.md)** — one **integer** prop (enum: `SymbolInfoIntegerProperty`).
* **[symbol\_info\_string](./symbol_info_string.md)** — one **string** prop (enum: `SymbolInfoStringProperty`).
* **[symbol\_info\_margin\_rate](./symbol_info_margin_rate.md)** — **margin rates** by **order type** (enum: `BMT5_ENUM_ORDER_TYPE`).
* **[symbol\_info\_session\_quote](./symbol_info_session_quote.md)** — **quote** session window (enum: `DayOfWeek`).
* **[symbol\_info\_session\_trade](./symbol_info_session_trade.md)** — **trading** session window (enum: `DayOfWeek`).
* **[symbol\_params\_many](./symbol_params_many.md)** — paged **directory of symbol parameters** (enum: `AH_SYMBOL_PARAMS_SORT_TYPE`).
* **[tick\_value\_with\_size](./tick_value_with_size.md)** — batch **tick value/size/contract** per symbol.
* **[market\_book\_add](./market_book_add.md)** — subscribe to **Level II** (DOM) for a symbol.
* **[market\_book\_get](./market_book_get.md)** — fetch **DOM snapshot** (bids/asks ladder).
* **[market\_book\_release](./market_book_release.md)** — unsubscribe from **Level II** (DOM).

---

## 🧭 Plain English

* **symbols\_total** → the **headcount** of symbols (all vs Market Watch).
* **symbol\_name** → walk lists by **index** without fetching everything.
* **symbol\_exist / symbol\_is\_synchronized / symbol\_select** → the **sanity trio**: existence, readiness, and watch‑list toggle.
* **symbol\_info\_* (double/integer/string)*\* → **one property** on demand; cheap and precise.
* **symbol\_info\_tick** → your **now** price snapshot with age/flags.
* **symbol\_info\_session\_quote/trade** → **when quotes/trading are allowed** per weekday & session.
* **symbol\_params\_many** → paged catalog to build tables and validators.
* **tick\_value\_with\_size** → bulk **tick economics** (tick value/size/contract).
* **market\_book\_add/get/release** → **Level II** lifecycle: subscribe → read → release.

> Rule of thumb: need **just one field** → `symbol_info_*`. Need **many rows** → `symbol_params_many` or `tick_value_with_size`. Need **depth** → `market_book_*`.

---

## Quick choose

| If you need…                                | Use                         | Returns                           | Key inputs (enums)                                |
| ------------------------------------------- | --------------------------- | --------------------------------- | ------------------------------------------------- |
| Count symbols                               | `symbols_total`             | `SymbolsTotalData { total }`      | `selected_only: bool`                             |
| Resolve name by index                       | `symbol_name`               | `SymbolNameData { name }`         | `index: int`, `selected: bool`                    |
| Check symbol existence / custom             | `symbol_exist`              | `SymbolExistData`                 | `symbol: str`                                     |
| Ensure Market Watch membership              | `symbol_select`             | `SymbolSelectData`                | `symbol: str`, `select: bool`                     |
| Check sync state                            | `symbol_is_synchronized`    | `SymbolIsSynchronizedData`        | `symbol: str`                                     |
| Latest tick snapshot                        | `symbol_info_tick`          | `SymbolInfoTickData`              | `symbol: str`                                     |
| One **double** property (e.g., BID, POINT)  | `symbol_info_double`        | `SymbolInfoDoubleData { value }`  | `property: SymbolInfoDoubleProperty`              |
| One **integer** property (e.g., DIGITS)     | `symbol_info_integer`       | `SymbolInfoIntegerData { value }` | `property: SymbolInfoIntegerProperty`             |
| One **string** property (e.g., DESCRIPTION) | `symbol_info_string`        | `SymbolInfoStringData { value }`  | `property: SymbolInfoStringProperty`              |
| Margin rates by order type                  | `symbol_info_margin_rate`   | `SymbolInfoMarginRat`             | `order_type: BMT5_ENUM_ORDER_TYPE`                |
| Quote session window                        | `symbol_info_session_quote` | `SymbolInfoSessionQuoteData`      | `day_of_week: DayOfWeek`, `session_index: uint32` |
| Trading session window                      | `symbol_info_session_trade` | `SymbolInfoSessionTradeData`      | `day_of_week: DayOfWeek`, `session_index: uint32` |
| Paged symbol parameters                     | `symbol_params_many`        | `SymbolParamsManyData`            | `sort_type: AH_SYMBOL_PARAMS_SORT_TYPE`, paging   |
| Bulk tick value/size/contract               | `tick_value_with_size`      | `TickValueWithSizeData`           | `symbols: list[str]`                              |
| Subscribe to Level II                       | `market_book_add`           | `MarketBookAddData`               | `symbol: str`                                     |
| Snapshot Level II                           | `market_book_get`           | `MarketBookGetData`               | `symbol: str`                                     |
| Unsubscribe Level II                        | `market_book_release`       | `MarketBookReleaseData`           | `symbol: str`                                     |

---

## ❌ Cross‑refs & gotchas

* **Select & sync** before data: `symbol_select` + `symbol_is_synchronized` help avoid empty ticks/books.
* **UTC timestamps everywhere** (including session windows). Convert once.
* **Server‑side enums** control behavior: always pass the correct enum for `symbol_info_*` and sessions.
* **Market book depth varies** by broker/symbol; arrays may be short or empty.
* **Batch wisely**: `tick_value_with_size` and `symbol_params_many` reduce RPC chatter for tables.

---

## 🟢 Minimal snippets

```python
# Ensure selected & synced, then get a fresh tick
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
s = "EURUSD"
if not (await acct.symbol_is_synchronized(s)).is_synchronized:
    await acct.symbol_select(s, True)
    _ = await acct.symbol_is_synchronized(s)
print((await acct.symbol_info_tick(s)).Bid)
```

```python
# One property (double) — POINT
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as mi_pb2
pt = await acct.symbol_info_double("XAUUSD", mi_pb2.SymbolInfoDoubleProperty.SYMBOL_POINT)
print(pt.value)
```

```python
# DOM: subscribe → get → release
await acct.market_book_add("BTCUSD")
book = await acct.market_book_get("BTCUSD")
await acct.market_book_release("BTCUSD")
```
