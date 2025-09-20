# Project Map & Layers

## 0) TL;DR

* **You edit** (green): `app/`, `examples/`, `ext/`, `docs/`, `main.py`, `settings.json`.
* **Don’t edit** (lock): `package/MetaRpcMT5/*_pb2*.py` (generated gRPC stubs), build artifacts.
* **Start here**: `examples/quick_start_connect.py` → verify connection → move to `app/services/*` for real work.
* **Danger zone**: anything that can place/cancel orders — see `app/services/trading_service.py`. ☢️

Legend: 🟢 = safe to edit, 🔒 = generated/infra, 🧩 = extension/adapters, 📚 = docs, 🧪 = tests, 🧠 = core logic, 🔌 = integration, 🧭 = examples.

---

## 1) High‑Level Project Map

```
PyMT5/
├── app/                    🟢 🧠 Project application code (services, patches, utils)
├── docs/                   🟢 📚 MkDocs content (guides, API, this page)
├── examples/               🟢 🧭 Minimal runnable scripts & how‑tos
├── ext/                    🟢 🧩 Local adapters/shims that wrap the base package
├── package/                🔒 Published package sources (incl. generated pb2)
├── main.py                 🟢 Entry point (optional)
├── settings.json           🟢 Local/dev settings
├── README.md               🟢 Project overview
└── mkdocs.yml              🟢 Docs site config
```

### 1.1 `app/` (you will work here 80% of the time)

```
app/
├── calc/                   🟢 Helpers for trading/math (e.g., P&L, margin)
├── compat/                 🟢 Patches for pb2/terminal compatibility
├── core/                   🟢 Core service & connection glue
├── patches/                🟢 Small, focused monkey‑patches
├── playground/             🟢 Local sandboxes (don’t ship to prod)
├── services/               🟢 High‑level APIs (history, streams, trading)
├── utils/                  🟢 Debug and helper utilities
└── __init__.py
```

Key files:

* `core/mt5_service.py` — central async client/service wrapper. 🔌
* `core/mt5_connect_helper.py` — resilient connect/disconnect/ensure logic. 🧠
* `services/trading_service.py` — high‑level trading ops (market/pending, mgmt). ☢️
* `services/streams_service.py` — subscriptions/streaming helpers. 🔌
* `services/history_service.py` — historical queries. 🔌
* `services/phases.py` — reusable step sequences (“phases”) for scenarios. 🧠
* `compat/mt5_patch.py` & `patches/*` — targeted fallbacks/aliases for shaky pb2s. 🧩
* `utils/grpc_debug.py` — introspection/log helpers for gRPC calls. 🛠️

### 1.2 `examples/`

```
examples/
├── quick_start_connect.py  🟢 Minimal connection check (edit creds/server)
├── list_account_methods.py 🟢 Discover callable methods at runtime
└── mt5_account_ex.py       🟢 Example using the extended adapter from `ext/`

```

Use these to validate your environment, then migrate code into `app/services/*`.

### 1.3 `ext/` (local adapters)

```
ext/
└── MetaRpcMT5Ex/
    ├── mt5_account_ex.py   🟢 Server‑name connect shim; auto‑fallback to ConnectEx
    └── __init__.py
```


### 1.4 `package/MetaRpcMT5` (generated stubs & vendor code — don’t touch)

```
MetaRpcMT5/
├── __init__.py
├── mrpc_mt5_error_pb2.py                🔒
├── mrpc_mt5_error_pb2_grpc.py           🔒
├── mt5_account.py                        🟡 Thin convenience wrapper (usually safe to read, avoid heavy edits)
├── mt5_term_api_*_pb2.py                🔒 Generated request/response messages
└── mt5_term_api_*_pb2_grpc.py           🔒 Generated service stubs
```

---

## 2) Who edits what (policy)

* 🟢 **Edit freely**: `app/*`, `examples/*`, `ext/*`, `main.py`, `settings.json`.
* 🛑 **Don’t edit**: `package/MetaRpcMT5/*_pb2*.py` (regenerate from proto instead).
* 🧪 **Tests**: put local tests in `package/tests` or add `tests/` at repo root.

---

## 3) Project Trees (for quick orientation)

### 3.1 Top‑level (depth 2)

```
PyMT5/
├── app/
│   ├── calc/
│   ├── compat/
│   ├── core/
│   ├── patches/
│   ├── playground/
│   ├── services/
│   ├── utils/
│   └── __init__.py
├── docs/
│   ├── I_want_to_add/
│   ├── MT5Account/
│   ├── api.md
│   └── index.md
├── examples/
│   ├── __init__.py
│   ├── list_account_methods.py
│   ├── mt5_account_ex.py
│   ├── PyMT5.py
│   ├── PyMT5.pyproj
│   ├── PyMT5.sln
│   ├── quick_start_connect.py
│   └── requirements.txt
├── ext/
│   ├── MetaRpcMT5Ex/
│   └── setup.py
├── package/
│   ├── MetaRpcMT5/
│   ├── tests/
│   ├── mt5_term_api.pyproj
│   ├── mt5_term_api.pyproj.user
│   ├── mt5_term_api.sln
│   ├── pyproject.toml
│   └── python.pyproj.user
├── .gitignore
├── main.py
├── mkdocs.yml
├── README.md
├── settings.json
└── tree.txt
```

### 3.2 `app/` (depth 3)

```
app/
├── calc/
│   └── mt5_calc.py
├── compat/
│   ├── __init__.py
│   └── mt5_patch.py
├── core/
│   ├── config.py
│   ├── constants.py
│   ├── mt5_connect_helper.py
│   └── mt5_service.py
├── patches/
│   ├── charts_copy_patch.py
│   ├── market_info_patch.py
│   ├── mt5_bind_patch.py
│   ├── patch_mt5_pb2_aliases.py
│   ├── quiet_connect_patch.py
│   └── symbol_params_patch.py
├── playground/
│   └── live_test.py
├── services/
│   ├── history_service.py
│   ├── phases.py
│   ├── streams_service.py
│   ├── trading_probe.py
│   └── trading_service.py
├── utils/
│   └── grpc_debug.py
└── __init__.py
```

### 3.3 `examples/`

```
examples/
├── __init__.py
├── list_account_methods.py
├── mt5_account_ex.py
├── PyMT5.py
├── PyMT5.pyproj
├── PyMT5.sln
├── quick_start_connect.py
└── requirements.txt
```

### 3.4 `package/MetaRpcMT5`

```
MetaRpcMT5/
├── __init__.py
├── mrpc_mt5_error_pb2.py
├── mrpc_mt5_error_pb2_grpc.py
├── mt5_account.py
├── mt5_term_api_account_helper_pb2.py
├── mt5_term_api_account_helper_pb2_grpc.py
├── mt5_term_api_account_information_pb2.py
├── mt5_term_api_account_information_pb2_grpc.py
├── mt5_term_api_charts_pb2.py
├── mt5_term_api_charts_pb2_grpc.py
├── mt5_term_api_connection_pb2.py
├── mt5_term_api_connection_pb2_grpc.py
├── mt5_term_api_health_check_pb2.py
├── mt5_term_api_health_check_pb2_grpc.py
├── mt5_term_api_internal_charts_pb2.py
├── mt5_term_api_internal_charts_pb2_grpc.py
├── mt5_term_api_market_info_pb2.py
├── mt5_term_api_market_info_pb2_grpc.py
├── mt5_term_api_subscriptions_pb2.py
├── mt5_term_api_subscriptions_pb2_grpc.py
├── mt5_term_api_trade_functions_pb2.py
├── mt5_term_api_trade_functions_pb2_grpc.py
├── mt5_term_api_trading_helper_pb2.py
└── mt5_term_api_trading_helper_pb2_grpc.py
```

### 3.5 `ext/`

```
ext/
├── MetaRpcMT5Ex/
│   ├── __init__.py
│   └── mt5_account_ex.py
└── setup.py
```

### 3.6 `docs/`

```
docs/
├── I_want_to_add/
│   ├── Architecture_DataFlow.md
│   └── Glossary.md
├── MT5Account/
│   ├── Account_Information/
│   ├── Orders_Positions_History/
│   ├── Subscriptions_Streaming/
│   ├── Symbols_and_Market/
│   ├── Trading_Operations/
│   ├── BASE.md
│   └── Under_the_Hood.md
├── api.md
└── index.md
```

---

## 4) How to build a scenario (step‑by‑step)

1. **Start** in `examples/` — sketch a minimal script that calls one or two `MT5Service` methods.
2. **Promote** it into `app/services/` as a function (`async def your_scenario(...)`).
3. **Compose phases** using `app/services/phases.py` if the scenario has multiple steps.
4. **Patch carefully** — if you hit pb2 differences, look at `app/compat/mt5_patch.py` and `app/patches/*`.
5. **Stream or poll** — for ticks/transactions use `streams_service.py`; for history use `history_service.py`.
6. **Wire up config** via `core/config.py` (env, defaults) and reuse `core/mt5_connect_helper.py`.
---

“Wishing you green candles, quiet terminals, and reproducible wins. 🟢”
