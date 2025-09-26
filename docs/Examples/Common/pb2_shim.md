# 🧩 `examples/common/pb2_shim.py`

Compatibility shim that keeps the **examples** working across different `MetaRpcMT5` wheel builds.
It exposes commonly used pb2 modules on the package and **re‑exports request classes** so callers can import them from
`MetaRpcMT5.mt5_term_api_account_helper_pb2` even if the real classes live in other pb2s.

---

## 🧭 Plain English

Some wheels ship `Symbol*Request` and friends in `mt5_term_api_market_info_pb2` (MI), while code expects them
under `mt5_term_api_account_helper_pb2` (AH). This shim:

1. **Exposes** pb2 / *_grpc modules as attributes of `MetaRpcMT5` (best‑effort).
2. **Aliases** `AccountHelperServiceStub` → `AccountHelperStub` when only the latter exists.
3. **Re‑exports** request classes from **MarketInfo** and **AccountInformation** pb2s onto **AccountHelper** pb2.

Idempotent and safe: if a class is already present, nothing happens. If a module is missing, it silently skips.

---

## 🔌 Public API

```python
from examples.common.pb2_shim import apply_patch
apply_patch()  # call once, as early as possible
```

> Put it at the very top of your example scripts, before importing enums/messages from `MetaRpcMT5.*`.

---

## 📦 What it exposes / aliases

**Modules exposed on `MetaRpcMT5` (best‑effort):**

* `mt5_term_api_account_helper_pb2` (+ `_grpc`)
* `mt5_term_api_market_info_pb2` (+ `_grpc`)
* `mt5_term_api_account_information_pb2` (+ `_grpc`)

**Service alias (grpc):**

* If `AccountHelperServiceStub` is missing but `AccountHelperStub` exists, create `AccountHelperServiceStub = AccountHelperStub`.

**Request classes re‑exported onto `account_helper_pb2`:**

* From **MarketInfo**:

  * `SymbolsTotalRequest`, `SymbolExistRequest`, `SymbolNameRequest`, `SymbolSelectRequest`
  * `SymbolInfoTickRequest`, `SymbolInfoDoubleRequest`, `SymbolInfoIntegerRequest`, `SymbolInfoStringRequest`
  * `SymbolInfoMarginRateRequest`, `SymbolInfoSessionQuoteRequest`, `SymbolInfoSessionTradeRequest`
  * `SymbolIsSynchronizedRequest`, `MarketBookAddRequest`, `MarketBookGetRequest`, `MarketBookReleaseRequest`
* From **AccountInformation**:

  * `AccountInfoDoubleRequest`, `AccountInfoIntegerRequest`, `AccountInfoStringRequest`

> Result: code can keep importing all these from `MetaRpcMT5.mt5_term_api_account_helper_pb2`, regardless of where they physically live in your wheel.

---

## 🧪 Quick self‑test (optional)

Run in your project root (`PyMT5/`):

```bash
python - <<'PY'
import importlib
from examples.common.pb2_shim import apply_patch; apply_patch()
ah = importlib.import_module('MetaRpcMT5.mt5_term_api_account_helper_pb2')
mi = importlib.import_module('MetaRpcMT5.mt5_term_api_market_info_pb2')
for n in [
  'SymbolSelectRequest','SymbolInfoDoubleRequest','SymbolInfoIntegerRequest','SymbolInfoStringRequest'
]:
    print(f"{n:24} AH:", hasattr(ah,n), '| MI:', hasattr(mi,n))
PY
```

You should see `AH: True` (either native or added by the shim). If not, the class is not present in the wheel at all.

---

## 🧰 Typical usage

```python
from examples.common.pb2_shim import apply_patch
apply_patch()

from MetaRpcMT5 import mt5_term_api_account_helper_pb2 as AH
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI
# Now both AH and MI expose the request classes used by examples.
```

---

## 🧯 Troubleshooting

* **`AttributeError: ... has no attribute 'Symbol...Request'`**
  Call `apply_patch()` **before** any imports from `MetaRpcMT5.*` and re‑run. If it persists, the class likely does not exist in this wheel.
* **`ImportError` for pb2 modules**
  Ensure your Python path includes the project `package/` directory (the examples’ `env.py` already adds it).
* **Service name mismatch**
  If your gRPC stub class is only `AccountHelperStub`, the shim auto‑creates `AccountHelperServiceStub` alias.

---

## 📝 Notes

* The shim is **no‑op** when a symbol already exists on AH (avoids overriding the real thing).
* The module list is conservative; add more `_expose(...)` entries if you introduce new pb2s.
* Silent failures are by design: examples should remain runnable across multiple wheel layouts without blowing up on import.

---

## 🔒 Minimal footprint

This file does **not** touch the package itself and lives entirely under `examples/common/`. Removing it simply removes the compatibility layer — your core SDK remains unchanged.

That’s it. Keep it at the top of your examples and enjoy smoother runs across different MetaRpcMT5 builds.
