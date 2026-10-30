# 🗺️ PyMT5 Project Map

> The whole project as one annotated tree, with links. **Links point to section *overviews*, never to individual method pages** — open an overview to drill down into its methods.

---

## 🧱 The three layers

PyMT5 is built in three decoupled layers. Your code can enter at any level.

| Layer | Source | What it does | Overview |
| ----- | ------ | ------------ | -------- |
| **3 · MT5Sugar** | `src/pymt5/mt5_sugar.py` | Convenience on top of Service: risk-based sizing, price/volume normalization, point-offset helpers, batch close/cancel. | [MT5Sugar overview](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/) |
| **2 · MT5Service** | `src/pymt5/mt5_service.py` | Typed facade: clean signatures that return ready Python data (no raw proto). What most code uses. | [MT5Service overview](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/) |
| **1 · MT5Account** | `package/MetaRpcMT5/mt5_account.py` | Low-level gRPC: proto request/reply, connect/session, auto-reconnect, streaming. Everything else builds on it. | [MT5Account overview](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/) |

```
Your code  →  MT5Sugar  →  MT5Service  →  MT5Account  →  gRPC  →  MetaRPC gateway → MT5 terminal
```

---

## 🌳 Repository tree

- **`PyMT5/`** — repo root (examples/demo project; the SDK itself is the importable `pymt5` package)
  - **`src/pymt5/`** — the package you `import`
    - `mt5_service.py` — **Layer 2** source → [MT5Service overview](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/)
    - `mt5_sugar.py` — **Layer 3** source → [MT5Sugar overview](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/)
  - **`package/MetaRpcMT5/`** — low-level gRPC layer
    - `mt5_account.py` — **Layer 1** source → [MT5Account overview](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/)
    - **`helpers/`** — `errors.py`, connection & retry helpers
    - `*_pb2.py` / `*_pb2_grpc.py` — generated gRPC / protobuf stubs (the raw contract)
  - **`examples/`** — runnable demos (the numbered menu), launched from `main.py`
    - `main.py` — interactive menu / CLI runner → [Getting Started](GETTING_STARTED.md)
    - **`0_common/`** — shared helpers (`demo_helpers.py`, `progress_bar.py`) + `settings.json` (your MT5 credentials) · protobuf inspector (16) → [Protobuf Inspector](PROTOBUF_INSPECTOR_GUIDE.md)
    - **`1_lowlevel/`** — `01`–`03` → [MT5Account overview](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/)
    - **`2_service/`** — `04`–`05` → [MT5Service overview](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/)
    - **`3_sugar/`** — `06`–`10` → [MT5Sugar overview](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/)
    - **`4_orchestrators/`** — `11`–`15` → [Strategies overview](https://metarpc.github.io/PyMT5/Strategies/Strategies.Master.Overview/)
    - **`5_usercode/`** — `17` → [UserCode Sandbox](USERCODE_SANDBOX_GUIDE.md)
  - **`docs/`** — this documentation site (see the map below)
  - **`tests/`** — unit tests
  - `mkdocs.yml` — docs site config · `.github/workflows/` — CI

---

## 📚 Documentation tree

- **`docs/`**
  - [Home](../index.md) — landing page
  - **`All_Guides/`** — the guides (Getting Started, Your First Project, Glossary, Sync vs Async, gRPC Streaming, ENUMs, Return Codes, …); browse them in the left nav or on the [docs site](https://metarpc.github.io/PyMT5/)
  - **`MT5Account/`** — low-level gRPC docs → [overview](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/) *(per-method pages inside)*
  - **`MT5Service/`** — typed facade docs → [overview](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/) *(per-method pages inside)*
  - **`MT5Sugar/`** — convenience API docs → [overview](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/) *(per-method pages inside)*
  - **`Strategies/`** — the five orchestrators → [overview](https://metarpc.github.io/PyMT5/Strategies/Strategies.Master.Overview/) *(per-strategy pages inside)*
  - `Guide_Images/` · `styles/` · `javascripts/` · `includes/` — assets & theme

> The `MT5Account/`, `MT5Service/`, `MT5Sugar/` and `Strategies/` folders hold per-method / per-strategy pages. By design this map links only their **overviews** — each overview is the index into its own detail pages.

---

## 🎯 Which layer should you use?

- **Most trading apps → [MT5Sugar](https://metarpc.github.io/PyMT5/MT5Sugar/MT5Sugar.Master.Overview/).** Risk sizing and auto-normalization protect you from off-quote and invalid-volume rejections.
- **Custom execution → [MT5Service](https://metarpc.github.io/PyMT5/MT5Service/MT5Service.Overview/).** Typed calls when you manage your own sizing/normalization.
- **Protocol-level control → [MT5Account](https://metarpc.github.io/PyMT5/MT5Account/MT5Account.Master.Overview/).** Raw proto structures and streams.
