# 🔌 `examples/common/diag_connect.py`

Tiny network sanity check for your `GRPC_SERVER` — from DNS all the way to **gRPC TLS channel readiness**. Perfect for answering: *“Is the network broken or is it my code?”* 

---

## 🧭 Plain English

Runs four checks in order and stops at the first failure:

1. **DNS** → resolve host.
2. **TCP** → open a raw TCP socket to `host:port`.
3. **TLS** → perform the handshake (SNI = `HOST`).
4. **gRPC** → create a secure aio channel and await `channel_ready()`.

Prints `OK` / `FAIL …` for each step.

> ℹ️ The script does not set a process exit code. Read the text output.

---

## 📁 Source

`PyMT5/examples/common/diag_connect.py`

**Deps:** stdlib + `grpc` (aio channel).

---

## ⚙️ Environment

Single env var (with default):

```ini
GRPC_SERVER=mt5.mrpc.pro:443
```

### Quick ways to set `GRPC_SERVER`

**PowerShell (Windows):**

```powershell
$env:GRPC_SERVER = "your.host.com:443"
```

**CMD (Windows):**

```bat
set GRPC_SERVER=your.host.com:443
```

**Bash (Linux/macOS):**

```bash
export GRPC_SERVER=your.host.com:443
```

---

## ▶️ How to run

Pick the command that matches where you run it from.

**A. From the *parent* of the `PyMT5/` package folder:**

```bash
python -m PyMT5.examples.common.diag_connect
```

**B. From inside the `PyMT5/` package folder:**

```bash
python -m examples.common.diag_connect
```

**C. Directly by path:**

```bash
python PyMT5/examples/common/diag_connect.py
# or, if your CWD is PyMT5/:
python examples/common/diag_connect.py
```

> If you use a virtual env, replace `python` with `.venv/Scripts/python` (Windows) or `.venv/bin/python` (Unix).

---

## 🖨️ Sample output

```
[1] DNS resolve myhost…
    OK: ['203.0.113.10', '203.0.113.12']
[2] TCP connect myhost:443…
    OK
[3] TLS handshake myhost:443…
    OK
[4] gRPC channel_ready (TLS) myhost:443…
    OK (channel ready)
```

---

## 🧯 Troubleshooting (by step)

**[1] FAIL DNS** — host typo, DNS override (hosts/VPN/adbocker), DNS server down.

> ✅ Check: `nslookup your.host.com` / `dig your.host.com`.

**[2] FAIL TCP** — port closed by server/firewall, corporate proxy/DPI, routing issue.

> ✅ Check: `telnet host 443` / `Test-NetConnection -Port 443`.

**[3] FAIL TLS** — wrong SNI/cert, MITM proxy without trusted root, bad system clock.

> ✅ Check: `openssl s_client -connect host:443 -servername host`.

**[4] FAIL gRPC TLS** — service is HTTP(S) but not gRPC/HTTP2, ALPN quirks, requires special creds/mTLS.

> ✅ Ensure it is a gRPC endpoint and intermediates are valid.

---

## 💡 Notes

* `channel_ready()` waits 10s. In high‑latency nets you may bump the timeout in code if needed.
* `CERTIFICATE_VERIFY_FAILED` often means a corporate TLS proxy. Install the proxy CA certificate into your OS store (no code change required).
* Some proxies/firewalls break ALPN/TLS → step [3] OK, step [4] fails.

---

## ➜ Next

If all four steps are **OK**, infra is fine. Jump to root `examples/` (market/history/streaming/trading). If a step fails, use the Troubleshooting hints to fix the corresponding network layer first.

🧱 Slow and steady: DNS → TCP → TLS → gRPC. 😉
