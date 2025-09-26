# PyMT5 — Project Map & Layers

## 0) TL;DR

* **You edit** (green): `app/`, `examples/`, `ext/`, `docs/`, `main.py`, `settings.json`.
* **Don’t edit** (lock): `package/MetaRpcMT5/*_pb2*.py` (generated gRPC stubs), build artifacts.
* **Start here**: `examples/quickstart.py` → verify connection → затем переносите логику в `app/services/*`.
* **Danger zone**: всё, что может ставить/менять/закрывать ордера — см. `app/services/trading_service.py`. ☢️

Legend: 🟢 = safe to edit, 🔒 = generated/infra, 🧩 = extension/adapters, 📚 = docs, 🧪 = tests, 🧠 = core logic, 🔌 = integration, 🧭 = examples.

---

## 1) High-Level Project Map

```
PyMT5/
├── app/                    🟢 🧠 Project application code (services, patches, utils)
├── docs/                   🟢 📚 MkDocs content (guides, API, site)
├── examples/               🟢 🧭 Minimal runnable scripts & how-tos
├── ext/                    🟢 🧩 Local adapters/shims that wrap the base package
├── package/                🔒 Published package sources (incl. generated pb2)
├── main.py                 🟢 Entry point (optional)
├── settings.json           🟢 Local/dev settings
├── README.md               🟢 Project overview
└── mkdocs.yml              🟢 Docs site config
```

### 1.1 `app/` (you will work here 80% of the time)

```
🟢 app/
├── calc/                    Helpers for trading/math (e.g., P&L, margin)
├── compat/                  Patches for pb2/terminal compatibility
├── core/                    Core service & connection glue
├── patches/                 Small, focused monkey-patches
├── playground/              Local sandboxes (don’t ship to prod)
├── services/                High-level APIs (history, streams, trading)
├── utils/                   Debug and helper utilities
└── __init__.py
```

Key files:

* `core/mt5_service.py` — central async client/service wrapper. 🔌
* `core/mt5_connect_helper.py` — resilient connect/disconnect/ensure logic. 🧠
* `services/trading_service.py` — high-level trading ops (market/pending, mgmt). ☢️
* `services/streams_service.py` — subscriptions/streaming helpers. 🔌
* `services/history_service.py` — historical queries. 🔌
* `services/phases.py` — reusable step sequences (“phases”) for scenarios. 🧠
* `compat/mt5_patch.py` & `patches/*` — targeted fallbacks/aliases for shaky pb2s. 🧩
* `utils/grpc_debug.py` — introspection/log helpers for gRPC calls. 🛠️

### 1.2 `examples/` (actual runnable scripts)

```
🧭examples/
├── base_example/
│   └── lowlevel_walkthrough           Driver for Steps 1–16 (select steps via env/CLI)
├── common/
│   ├── env.py                         Env helpers (creds, defaults)
│   ├── pb2_shim.py                    Patch/aliases for pb2 quirks
│   ├── diag_connect.py                Connectivity diagnostics
│   └── utils.py                       Print/normalize helpers
├── legacy_examples/
│   └── quick_start_connect.py         Old minimal connect (kept for reference)
├── account_info.py                    AccountInfo* demo
├── list_account_methods.py            Introspect callable methods
├── opened_snapshot.py                 Pending orders snapshot
├── orders_history.py                  Orders history
├── positions_history.py               Positions history
├── market_book.py                     DOM (book) demo
├── symbols_market.py                  Symbol info & params
├── streaming_position_profit.py       Stream: position profit
├── streaming_positions_tickets.py     Stream: positions & pending tickets
├── streaming_trade_events.py          Stream: trade deals
├── streaming_trade_tx.py              Stream: trade transactions
├── trading_basics.py                  Pre-trade checks
├── trading_safe.py                    Safe trading flow (checks → send/modify/close)
├── quickstart.py                      Quick start (connect & ping)
├── cli.py                             CLI runner (wraps scenarios)
└── __main__.py
```

### 1.3 `ext/` (local adapters)

```
ext/
└── MetaRpcMT5Ex/
    ├── mt5_account_ex.py   🟢 Server-name connect shim; auto-fallback to ConnectEx
    └── __init__.py
```

### 1.4 `package/MetaRpcMT5` (generated stubs & vendor code — don’t touch)

```
MetaRpcMT5/
├── __init__.py
├── mrpc_mt5_error_pb2(.py|_grpc.py)          🔒
├── mt5_term_api_*_pb2(.py|_grpc.py)          🔒 Generated request/response messages & service stubs
├── mt5_account.py                             🟡 Thin convenience wrapper (read-only edits recommended)
└── ...
```

---

## 2) Who edits what (policy)

* 🟢 **Edit freely**: `app/*`, `examples/*`, `ext/*`, `main.py`, `settings.json`.
* 🛑 **Don’t edit**: `package/MetaRpcMT5/*_pb2*.py` (regenerate from proto instead).
* 🧪 **Tests**: put local tests in `package/tests` or add `tests/` at repo root.

---

## 3) Project Trees

### 3.1 Top-level (depth 2)

```
PyMT5/
├── app/
├── docs/
├── examples/
├── ext/
├── package/
├── main.py
├── mkdocs.yml
├── README.md
└── settings.json
```

### 3.2 `app/` (depth 3)

```
app/
├── calc/mt5_calc.py
├── compat/{mt5_patch.py, __init__.py}
├── core/{config.py, constants.py, mt5_connect_helper.py, mt5_service.py}
├── patches/{charts_copy_patch.py, market_info_patch.py, mt5_bind_patch.py,
│           patch_mt5_pb2_aliases.py, quiet_connect_patch.py, symbol_params_patch.py}
├── playground/live_test.py
├── services/{history_service.py, phases.py, streams_service.py, trading_probe.py, trading_service.py}
├── utils/grpc_debug.py
└── __init__.py
```

### 3.3 `examples/` (selected)

```
examples/
├── base_example/lowlevel_walkthrough
├── common/{env.py, pb2_shim.py, diag_connect.py, utils.py}
├── legacy_examples/quick_start_connect.py
├── {quickstart.py, account_info.py, opened_snapshot.py, orders_history.py,
│    positions_history.py, market_book.py, symbols_market.py,
│    streaming_position_profit.py, streaming_positions_tickets.py,
│    streaming_trade_events.py, streaming_trade_tx.py,
│    trading_basics.py, trading_safe.py, list_account_methods.py, cli.py}
└── __main__.py
```

### 3.4 `package/MetaRpcMT5` (excerpt)

```
MetaRpcMT5/
├── mt5_account.py
├── mt5_term_api_..._pb2.py
├── mt5_term_api_..._pb2_grpc.py
└── ...
```

---

## 4) How to build a scenario (step-by-step)

1. **Start** in `examples/` — sketch a minimal script that calls one or two `MT5Service` methods.
2. **Promote** it into `app/services/` as a function (`async def your_scenario(...)`).
3. **Compose phases** using `app/services/phases.py` if the scenario has multiple steps.
4. **Patch carefully** — if you hit pb2 differences, look at `app/compat/mt5_patch.py` and `app/patches/*`.
5. **Stream or poll** — for ticks/transactions use `streams_service.py`; for history use `history_service.py`.
6. **Wire up config** via `core/config.py` (env, defaults) and reuse `core/mt5_connect_helper.py`.

---

“Wishing you green candles, quiet terminals, and reproducible wins. 🟢”
