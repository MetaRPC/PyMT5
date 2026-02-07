## symbol_select — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `symbol_select()` to **manage Market Watch content** — add and remove symbols.

The example implements a practical task: cleaning Market Watch of all symbols except a predefined list.

---

## Method Signature

```python
async def symbol_select(
    symbol: str,
    select: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `symbol` — trading symbol name
* `select=True` adds the symbol to Market Watch
* `select=False` removes the symbol from Market Watch
* The method returns the operation result

---

## 🧩 Code Example — Market Watch Cleanup

```python
async def cleanup_market_watch(account: MT5Account, keep_symbols: list[str]):
    total_data = await account.symbols_total(selected_only=True)
    total = total_data.total

    removed = []
    for i in range(total):
        name_data = await account.symbol_name(index=i, selected=True)
        symbol = name_data.name

        if symbol not in keep_symbols:
            data = await account.symbol_select(symbol=symbol, select=False)
            if data.success:
                removed.append(symbol)
                print(f"Removed: {symbol}")

    print(f"Removed {len(removed)} symbols from Market Watch")
    return removed
```

This example demonstrates practical use of `symbol_select()` for managing the displayed symbols list.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting Selected Symbols Count

```python
total_data = await account.symbols_total(selected_only=True)
total = total_data.total
```

At this step:

* the number of symbols in Market Watch is requested
* this value is used as the iteration boundary

---

### 2️⃣ Iterating Through Symbols by Index

```python
for i in range(total):
```

The code sequentially iterates through all symbols currently added to Market Watch.

---

### 3️⃣ Getting Symbol Name

```python
name_data = await account.symbol_name(index=i, selected=True)
symbol = name_data.name
```

At this step:

* the symbol name is obtained by index
* the name is used to decide on removal

---

### 4️⃣ Removing Symbol from Market Watch

```python
data = await account.symbol_select(symbol=symbol, select=False)
```

If the symbol is not in the `keep_symbols` list:

* `symbol_select()` is called with `select=False`
* a command is sent to the terminal to remove the symbol from Market Watch

---

### 5️⃣ Checking Operation Result

```python
if data.success:
```

The method returns an object with a `success` flag:

* `True` — operation completed successfully
* `False` — operation was not completed

User code decides how to interpret the result.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`symbol_select()`**:

* adds or removes a symbol from Market Watch
* performs one specific operation
* returns the operation result

**`cleanup_market_watch()`**:

* determines which symbols to keep
* manages list iteration
* decides on removal
* aggregates the result

---

## Summary

This example illustrates the state management pattern through low-level API:

> **get current state → make decision → change state → check result**

The `symbol_select()` method performs an atomic operation of adding or removing a symbol, while all Market Watch management logic is implemented on the user code side.
