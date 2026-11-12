# Three small read-only examples

Start with a disposable demo account. These examples connect to a hosted MT5 terminal but never submit orders. Hosted usage is billed, including for broker demo accounts.

## Install and configure

```bash
git clone https://github.com/MetaRPC/PyMT5.git
cd PyMT5
python -m pip install ./package
```

Set `MRPC_API_KEY`, `MT5_LOGIN`, `MT5_PASSWORD` and `MT5_SERVER` in your private process environment. Get the API key from [your portal](https://mrpc.pro/my). Do not put credentials in command arguments, committed files or shared screenshots.

## Read one account snapshot

```bash
python examples/read_account.py
```

Reads balance, equity and free margin, then attempts to disconnect in `finally`. Amounts are in the account's deposit currency. [Source](https://github.com/MetaRPC/PyMT5/blob/main/examples/read_account.py).

## Watch a small account dashboard

```bash
python examples/account_dashboard.py --samples 6 --interval 5
```

Prints six timestamped rows, waiting five seconds between reads. It has no web server, open port, order controls or background process. Each account read has a 15-second timeout. [Source](https://github.com/MetaRPC/PyMT5/blob/main/examples/account_dashboard.py).

## Stream quotes with an explicit end

```bash
python examples/stream_quotes.py --symbol EURUSD --seconds 30 --events 20
```

Use your broker's exact symbol, including any suffix. The example stops when it receives 20 events or reaches 30 seconds, whichever comes first. A quiet market still reaches the time limit. It closes its stream before disconnecting. [Source](https://github.com/MetaRPC/PyMT5/blob/main/examples/stream_quotes.py).

This is **gRPC server streaming**. For the separate REST service's WebSocket workflow, use [the existing WebSocket tutorial](https://mrpc.pro/tutorials/console/websocket?lang=en).

## Check cleanup and test limits

On failure, shared console output shows only the exception type. Inspect sensitive details locally and redact them before sharing. The SDK suppresses some disconnect errors: returning from cleanup does not prove the remote terminal stopped. Check your portal after a network failure and stop unused terminals.

```bash
python -m unittest discover -s tests -p 'test_*example*.py'
```

Offline tests cover bounded reads, event limits, quiet-stream cancellation, failure cleanup, input checks and credential-free output. They do not establish live broker connectivity or execution. For copying, use the separate [PyCopier sizing worksheet](https://metarpc.github.io/PyCopier/sizing/).
