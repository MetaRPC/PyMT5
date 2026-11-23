## symbol_exist — How it works

---

## 📌 Overview

This example demonstrates how to check **whether a trading symbol exists in the terminal** using the low-level asynchronous method `symbol_exist()`.

The method is used for basic input data validation: before subscribing, before trading, or before loading symbol parameters.

It answers only one question:

> *Is a symbol with this name known to the terminal?*

---

## Method Signature

```python
async def symbol_exist(
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and must be called with `await`
* `symbol` — symbol name as a string (e.g., `"EURUSD"`)
* `deadline` and `cancellation_event` control execution time
* The method returns an object with information about symbol existence

---

## 🧩 Code Example — Checking Multiple Symbols

```python
async def check_symbols(account: MT5Account, symbols: list[str]):
    results = {}

    for symbol in symbols:
        data = await account.symbol_exist(symbol=symbol)
        results[symbol] = data.exists

    for symbol, exists in results.items():
        status = "[OK]" if exists else "[ERROR]"
        print(f"{status} {symbol}: {'exists' if exists else 'not found'}")

    return results
```

In this example, `symbol_exist()` is used to sequentially check a list of symbols.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Iterating Through Symbol List

```python
for symbol in symbols:
```

The function iterates through a list of strings, where each string is a trading symbol name.

Checks are performed **sequentially**, for each symbol separately.

---

### 2️⃣ Checking Symbol Existence

```python
data = await account.symbol_exist(symbol=symbol)
```

At this step, one asynchronous call is executed.

* The symbol name is passed to the method
* The terminal checks whether such a symbol is known
* The result is returned as a response object

The method does not throw an error if the symbol is not found — this information is returned in the response data.

---

### 3️⃣ Extracting Check Result

```python
results[symbol] = data.exists
```

The response object contains the `exists` field.

* `True` — symbol exists
* `False` — symbol not found

Only this fact is saved to the dictionary, without additional symbol information.

---

### 4️⃣ Processing Results

```python
for symbol, exists in results.items():
```

After all checks are completed, results are processed separately.

This allows:

* First collecting data
* Then making decisions or displaying information

---

### 5️⃣ Displaying Information

```python
status = "[OK]" if exists else "[ERROR]"
print(f"{status} {symbol}: {'exists' if exists else 'not found'}")
```

Regular application logic is used here:

* A human-readable status is formed
* Symbol name and check result are displayed

This code does not affect the check itself — it's only for convenience.

---

## Summary

In this example, `symbol_exist()` is used as a simple way to verify the correctness of symbol names.

The method is called for each symbol separately, returns information about its existence, and all result processing logic remains on the calling code side.
