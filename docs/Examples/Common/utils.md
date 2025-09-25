# 🛠️ `examples/common/utils.py`

Tiny helpers for **console UX** in examples: section headers, pretty printing, and a safe async wrapper with uniform logs.

---

## 🧭 What’s inside

```python
def title(s: str) -> None: ...
def pprint(obj: Any) -> None: ...
async def safe_async(name: str, fn: Callable[..., Awaitable], *args, **kwargs) -> Optional[Any]: ...
```

* **`title()`** — prints a clear section header: `==================== Name ====================`
* **`pprint()`** — JSON pretty‑prints Python objects (falls back to `str(obj)` if not JSON‑serializable).
* **`safe_async()`** — runs an async call with consistent logging, pretty‑prints the result, catches exceptions, and **returns** the result (or `None` if there was an error or no return value).

---

## 🔌 How to use

### 1) Headers

```python
from examples.common.utils import title

title("Quick Start")
```

### 2) Pretty print

```python
from examples.common.utils import pprint

data = {"symbol": "EURUSD", "bid": 1.09234}
pprint(data)
```

### 3) Safe async calls

```python
from examples.common.utils import safe_async

# simplest form — no args
await safe_async("account_summary", acc.account_summary)

# with positional args
await safe_async("symbol_select", acc.symbol_select, "EURUSD", True)

# with kwargs (will be shown in the call line)
await safe_async("positions_history", acc.positions_history, from_ts=..., to_ts=...)
```

You’ll see a line like:

```
> symbol_select('EURUSD', True)
OK (no return)
```

Or, if it returns a value, a JSON pretty dump of the result.

---

## 🤝 With gRPC stubs (metadata, timeouts)

`safe_async` accepts the target **callable** and its args. For gRPC stubs that require `metadata=` or `timeout=`, use `functools.partial` or pass them as kwargs if your wrapper supports it:

```python
from functools import partial
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as MI

req = MI.SymbolInfoDoubleRequest(symbol="EURUSD", type=MI.SymbolInfoDoubleProperty.SYMBOL_BID)
await safe_async(
    "symbol_info_double(BID)",
    partial(acc.market_info_client.SymbolInfoDouble, req),
    metadata=acc.get_headers(),
    timeout=30.0,
)
```

---

## 📋 Output rules

* **Prelude line:** `> {name}({args_repr})`
* **Success with value:** prints JSON (`ensure_ascii=False`, `indent=2`, `default=str`).
* **Success with no value:** prints `OK (no return)`.
* **Error:** prints `[ERROR] {ExceptionType}: {message}` and returns `None`.

> Note: Non‑JSON objects (e.g., datetime, Decimal, protobuf messages) are rendered via `str(obj)` because of `default=str`.

---

## 🧯 Troubleshooting & tips

* **Nothing printed after the prelude?** Your function likely returned `None` → you’ll see `OK (no return)`.
* **Protobuf objects look too terse?** Convert them yourself before printing, e.g. with `google.protobuf.json_format.MessageToDict`.
* **Need to keep going on errors?** `safe_async` already **catches** and **returns `None`**, so your script won’t crash — just check for `None` if you need branching.

```python
res = await safe_async("symbol_info_double(BID)", ...)
if res is None:
    print("skip spread calc — no data")
```

---

## 🧪 Minimal pattern (all together)

```python
from examples.common.utils import title, safe_async

title("Symbols & Market")
await safe_async("symbol_select", acc.symbol_select, SYMBOL, True)
bid = await safe_async("symbol_info_double(BID)", acc.symbol_info_double, SYMBOL, SDouble.SYMBOL_BID)
ask = await safe_async("symbol_info_double(ASK)", acc.symbol_info_double, SYMBOL, SDouble.SYMBOL_ASK)
if isinstance(bid, (int, float)) and isinstance(ask, (int, float)):
    print("spread:", float(ask) - float(bid))
```

---

## 📝 Design notes

* Output format is stable and greppable, handy for quick logs and CI.

That’s it — small, predictable, and copy‑paste friendly. 🚀
