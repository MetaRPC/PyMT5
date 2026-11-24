# The MetaRPC SDK family

> Where PyMT5 sits — and how it pairs with the **Trade Copier** ([PyCopier](https://github.com/MetaRPC/PyCopier)) to mirror a strategy across accounts.

MetaRPC ships two families of SDKs. They share the **same owner API key**, the **same gRPC-over-TLS transport** to `*.mrpc.pro`, the same [mrpc.pro](https://mrpc.pro/explorer/mt5-client) portal and the same demo onboarding — but they do different jobs.

| Family | Job | Endpoint | SDKs |
| ------ | --- | -------- | ---- |
| **Terminal SDKs** | operate **one** trading account — connect, read, trade, stream | `mt5.mrpc.pro:443` (MT5) | **PyMT5**, GoMT5, CSharpMT5, CppMT5, NodeMT5, RubyMT5, RustMT5 (+ MT4 variants) |
| **Copier SDKs** | mirror trades **between** accounts (master → followers) | `copy.mrpc.pro:443` | [PyCopier](https://github.com/MetaRPC/PyCopier), RubyCopier, NodeCopier, GoCopier, CSharpCopier, … |

**PyMT5 is a Terminal SDK.** When you want to *replicate* what happens on one account to others, reach for the **Copier** SDK — in Python that's **[PyCopier](https://github.com/MetaRPC/PyCopier)** (`pycopier`).

---

## How PyMT5 and PyCopier relate

|  | **PyMT5** (this SDK) | **PyCopier** |
| --- | --- | --- |
| Scope | one account | a master → follower **pair** |
| Does | `quick_connect`, quotes, `buy_market_with_sltp`, streams | `start` · `list` · `pause` · `remove` a copier |
| Endpoint | `mt5.mrpc.pro:443` | `copy.mrpc.pro:443` |
| Thinks in | ticks, positions, orders | risk sizing, pause/resume, copy logs |
| Style | **async** (`await`) | **async** (`await`) |

**One sentence:** PyMT5 is where trades are *produced and observed* on an account; PyCopier is how they're *distributed* to followers.

Both are `asyncio`-native, so they slot into the same event loop — you can drive the master with PyMT5 and open a copier with PyCopier from the same `async def main()`.

---

## How the copier connects accounts

A copier enrolls **two** accounts — a `master` and a `slave` — each described by a `pycopier.Account`:

```python
Account(type="MT5", user=12345, password="...", server="Broker-Server", name="", id="")
```

| Field | Meaning |
| ----- | ------- |
| `type` | account route — `"MT5"`, `"MT4"`, `"CT"` (cTrader), `"TL"` (TradeLocker), plus `*_MTAPI` / `*_MRPC` variants. The deployment must enable the route. |
| `user` | login (int) |
| `password` | account password |
| `server` | broker server / cluster |
| `id` | connected terminal/session id — **required only for `CT` / `TL`**; for MT5 leave it empty and the copier connects by credentials. Preserve its exact format if you do pass one. |

> There is **no GUID-bridge helper** in PyCopier (unlike some sibling SDKs). For MT4/MT5 the copier connects the master and the slave itself from `user` / `password` / `server` — you do **not** hand it a PyMT5 session handle.

---

## Install PyCopier

PyCopier is a **source install** (no separate runtime download), Python **3.10+**:

```bash
git clone https://github.com/MetaRPC/PyCopier.git
cd PyCopier
python -m pip install -e .
```

Then:

```python
from pycopier import CopierService, StartRequest, Account
```

### The owner key (`user_key`)

The copier authenticates with your **owner API key**, passed as `user_key` (sent as the `apikey` gRPC metadata header):

```python
svc = CopierService("copy.mrpc.pro:443", user_key=os.environ["MRPC_API_KEY"])
```

- `manager_key` is optional and defaults to `user_key`.
- **`TRIAL` is not accepted** by the copier — it needs a real owner key (printable ASCII, no whitespace). `CopierService.start` on a TRIAL/empty key raises a `ValueError`, not an `ok=False` reply.

---

## End-to-end: run a strategy on the master, replicate to a follower

```python
import asyncio, os
from pymt5 import MT5Sugar, MT5Service, MT5Account
from pycopier import CopierService, StartRequest, Account

KEY = os.environ["MRPC_API_KEY"]   # owner key — TRIAL is NOT accepted by the copier

async def main():
    # 1 · Operate the MASTER account with PyMT5 (Terminal SDK, mt5.mrpc.pro)
    account = MT5Account.create(
        user=int(os.environ["MASTER_LOGIN"]),
        password=os.environ["MASTER_PASSWORD"],
        grpc_server="mt5.mrpc.pro:443",
    )
    master = MT5Sugar(MT5Service(account))
    await master.quick_connect("FxPro-MT5 Demo")

    # ... produce/observe trades on the master as usual, e.g.:
    # await master.buy_market_with_sltp("EURUSD", volume=0.1, sl_pips=50, tp_pips=100)

    # 2 · Start a copier: MASTER -> FOLLOWER (PyCopier, on copy.mrpc.pro)
    svc = CopierService("copy.mrpc.pro:443", user_key=KEY)
    req = StartRequest(
        risk_type="LotMultiplier",     # or "FixedLot" / "FixedBalanceMultiplier"
        risk_value="1.0",              # decimal STRING — lots or multiplier
        copy_sl=True,
        copy_tp=True,
        master=Account(type="MT5", user=int(os.environ["MASTER_LOGIN"]),
                       password=os.environ["MASTER_PASSWORD"], server="FxPro-MT5 Demo"),
        slave=Account(type="MT5", user=int(os.environ["SLAVE_LOGIN"]),
                      password=os.environ["SLAVE_PASSWORD"], server="FxPro-MT5 Demo"),
    )
    rep = await svc.start(req)
    if not rep.ok:
        raise SystemExit(f"copier start failed: {rep.error}")
    print(f"copier #{rep.copier_id} running")

    # 3 · Manage it
    await svc.pause(rep.copier_id, True)    # pause
    await svc.pause(rep.copier_id, False)   # resume (there is no separate resume() — pause(id, False))
    # await svc.remove(rep.copier_id)       # tear down
    await svc.close()

asyncio.run(main())
```

### Same thing with the fluent builder (`CopierSugar`)

```python
from pycopier import CopierSugar

rep = await (
    CopierSugar.create()
    .with_credentials(os.environ["MRPC_API_KEY"])
    .from_master(type="MT5", user=int(os.environ["MASTER_LOGIN"]),
                 password=os.environ["MASTER_PASSWORD"], server="FxPro-MT5 Demo")
    .to_slave(type="MT5", user=int(os.environ["SLAVE_LOGIN"]),
              password=os.environ["SLAVE_PASSWORD"], server="FxPro-MT5 Demo")
    .with_lot_multiplier(1.0)   # or .with_fixed_lot(0.10)
    .copy_sl().copy_tp()
    .start()
)
```

---

## The copier's core operations

All methods are **async** and return simple reply objects:

| Call | Returns | Notes |
| ---- | ------- | ----- |
| `await svc.start(request)` | `StartReply(ok, copier_id, error)` | starts master → slave copying; ~180 s timeout |
| `await svc.list()` | `ListReply(ok, copiers, error)` | each `CopierSummary` has `id`, master/slave `type`/`user`/`server`, `risk_type`, `risk_value`, `paused`, `pause_reason` |
| `await svc.pause(copier_id, paused)` | `SimpleReply` | `paused=True` pauses, `paused=False` resumes |
| `await svc.remove(copier_id)` | `SimpleReply` | removes the copier |
| `async for log in svc.stream_trade_logs(copier_id)` | `TradeLog` stream | live copy events |
| `await svc.close()` | — | closes the client channel |

### Risk sizing (`risk_type`)

| `risk_type` | `risk_value` means |
| ----------- | ------------------ |
| `LotMultiplier` (default) | multiply the master's lot by this factor |
| `FixedLot` | always open this many lots on the follower |
| `FixedBalanceMultiplier` | scale by balance ratio (set `fixed_master_balance` as the denominator) |

(Two further sizing policies exist but are not documented here.)

---

## Gotchas

- **`start` / `list` / `pause` / `remove` turn gRPC errors into `ok=False` replies**; *configuration* errors (bad/empty/TRIAL key) raise exceptions instead — handle both.
- **Disposing the client does not stop a server-side copier.** Call `remove()` to actually tear one down; `close()` only closes your local channel.
- **Billing can block a resume** — a `pause(id, False)` may come back with `ok=False` and a `pause_reason`.
- The wrapper exposes the **core** routes (`start` / `list` / `pause` / `remove` + trade-log stream), not every REST route the service has.

---

### See also

- **[PyCopier on GitHub](https://github.com/MetaRPC/PyCopier)** — source, examples (`examples/list.py`, `examples/sizing_preview.py`), and reference.
- [Getting Started](./GETTING_STARTED.md) · [Your First Project](./Your_First_Project.md) — the PyMT5 (Terminal SDK) side.
- [MT5 Client API Explorer](https://mrpc.pro/explorer/mt5-client) — your owner key and the raw protos.
