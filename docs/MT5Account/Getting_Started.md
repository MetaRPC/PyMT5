# PyMT5 — Getting Started 🚀


## 1) Requirements 🧰

* **Windows** with **PowerShell**.
* **Python 3.13.x** (project verified with 3.13.7).
* **MetaTrader 5** terminal and valid account (Demo or Live).
* Network access to a gRPC gateway (default `mt5.mrpc.pro:443`).

---

## 2) Project checkout 📦

```powershell
cd C:\Users\<YOU>\
# Download/unzip the project into C:\Users\<YOU>\PyMT5
cd C:\Users\<YOU>\PyMT5
```

`main.py` is your entry point (a phase-based PLAYBOOK).

---

## 3) Virtual environment 🧪

```powershell
# Create venv (one time)
python -m venv .venv

# Activate (every session)
.\.venv\Scripts\Activate.ps1

# Check version
python --version   # expecting Python 3.13.x
```

---

## 4) Credentials & configuration (ENV) 🔐

This project **does not** hardcode credentials. They are read from **environment variables** (see `main.py`):

* `MT5_LOGIN` (int)
* `MT5_PASSWORD` (string)
* `MT5_SERVER` (e.g., `MetaQuotes-Demo`)
* `GRPC_SERVER` (e.g., `mt5.mrpc.pro:443`)
* Optional: `TIMEOUT_SECONDS`, `MT5_VERBOSE`

### A) Set ENV in PowerShell (session-only)

```powershell
$env:MT5_LOGIN    = "<YOUR_LOGIN>"
$env:MT5_PASSWORD = "<YOUR_PASSWORD>"
$env:MT5_SERVER   = "<YOUR_MT5_SERVER>"   # e.g., MetaQuotes-Demo
$env:GRPC_SERVER  = "mt5.mrpc.pro:443"
$env:TIMEOUT_SECONDS = "120"
$env:MT5_VERBOSE  = "1"

echo "login=$($env:MT5_LOGIN) server=$($env:MT5_SERVER) grpc=$($env:GRPC_SERVER) t=$($env:TIMEOUT_SECONDS)"
```

### B) Use a `.env` file (recommended) 📄

Create `.env` in the project root:

```
MT5_LOGIN=YOUR_LOGIN
MT5_PASSWORD=YOUR_PASSWORD
MT5_SERVER=MetaQuotes-Demo
GRPC_SERVER=mt5.mrpc.pro:443
TIMEOUT_SECONDS=120
MT5_VERBOSE=1
```

> `.env` is loaded via `python-dotenv` in `main.py`. Add `.env` to `.gitignore`.

---

## 5) Run the project ▶️

```powershell
python .\main.py
```

You should see `[connect] ...` logs and phase sections (0–7). A healthy run shows `server_time`, `account_summary`, symbol ticks, etc.

---

## 6) Phases (fine-grained control) 🧭

`main.py` executes demo **phases**. You can turn them on/off via ENV without changing code:

* **PHASE0 — Connectivity & Account**: connection check, `server_time`, `account_summary`.
* **PHASE1 — Symbols & Market info**: symbol params, ticks, margin/session data.
* **PHASE2 — Opened state snapshot**: positions/orders quick snapshot.
* **PHASE3 — Calculations & dry‑run**: `order_calc_*` sanity checks.
* **PHASE4 — Charts/Copy & DOM**: optional/placeholder in current build.
* **PHASE5 — History & lookups**: history for `HISTORY_DAYS`, ticket lookups.
* **PHASE6 — Streaming (compact)**: short live stream (ticks + open tickets) with throttle.
* **TRADE\_PRESET — Safe trading preset**: demo market/close/pending; can be dry‑run.
* **LIVE\_TEST — Developer mini‑test**: see `app/playground/live_test.py`.

### Toggle phases via ENV

```powershell
# Minimal run (PHASE0 only)
$env:RUN_PHASE0 = "1"
$env:RUN_PHASE1 = "0"
$env:RUN_PHASE2 = "0"
$env:RUN_PHASE3 = "0"
$env:RUN_PHASE4 = "0"
$env:RUN_PHASE5 = "0"
$env:RUN_PHASE6 = "0"

# Make sure trading preset is off during learning
$env:RUN_TRADE_PRESET = "0"   # or keep TRADE_PRESET=0 in .env
```

> Internally `main.py` maps ENV flags to a `RUN[...]` dictionary; defaults are applied if ENV not set.

---


## 7) Helpful ENV knobs ⚙️

* `SELECTED_SYMBOL` (default `EURUSD`) — primary example symbol.
* `ALT_SYMBOL` (default `GBPUSD`).
* `CRYPTO_SYMBOL` (default `BTCUSD`).
* `HISTORY_DAYS` (default `7`).
* `STREAM_TIMEOUT_SECONDS` (default `45`).
* `BASE_CHART_SYMBOL` — fallback symbol for pings/tick requests if your broker uses suffixes (e.g., `.m`).

---

## 8) Typical signals & what they mean 🔎

* `AttributeError('terminalInstanceGuid')` during `connect_by_host_port` → expected for some builds; code auto‑falls back to `ConnectEx/Connect` and may enter **LITE mode**.
* `LITE mode: skip session/terminal handshake (pb2 missing)` → your protobuf set lacks some methods (Ping/handshake). The project handles this and still works.
* Post‑connect ping fails on `symbols_total(False)` → temporarily skip that call in `_try_post_connect_ping` in `app/core/mt5_connect_helper.py`.
* Final `KeyboardInterrupt` after cancel → cosmetic on Python 3.13; catch `CancelledError/KeyboardInterrupt` in the lowest `try/except` in `main.py` if you want clean logs.

---

## 9) Quick start checklist ✅

1. Activate venv → verify `python --version`.
2. Provide ENV (login/password/server/GRPC) → increase `TIMEOUT_SECONDS` if needed.
3. First run with **PHASE0** only.
4. If okay → enable **PHASE1–PHASE6**.
5. Only then try trading: `TRADE_PRESET=1` and `TRADE_DRY_RUN=0` — on demo only.

---

## 10) Example `.env` for development 🧾

```
MT5_LOGIN=12345678
MT5_PASSWORD=***
MT5_SERVER=MetaQuotes-Demo
GRPC_SERVER=mt5.mrpc.pro:443

TIMEOUT_SECONDS=120
MT5_VERBOSE=1
HISTORY_DAYS=7
STREAM_TIMEOUT_SECONDS=45

SELECTED_SYMBOL=EURUSD
ALT_SYMBOL=GBPUSD
CRYPTO_SYMBOL=BTCUSD
BASE_CHART_SYMBOL=EURUSD

# Phases
RUN_PHASE0=1
RUN_PHASE1=1
RUN_PHASE2=1
RUN_PHASE3=1
RUN_PHASE4=0
RUN_PHASE5=1
RUN_PHASE6=1

# Trading preset
TRADE_PRESET=0
TRADE_DRY_RUN=1
```
---

## 13) Run after setting `.env` ▶️

```powershell
.\.venv\Scripts\Activate.ps1
python .\main.py
```

You should see phase sections like **“0) ▶ Connectivity & Account”**, **“1) 📈 Symbols & Market info”**, etc. If logs are clean — you’re ready to go.
