## symbol_name — How it works

---

## 📌 Overview

This example shows how to retrieve **trading symbol names by index** using the low-level asynchronous method `symbol_name()` and how to safely build a list of symbols with error handling based on it.

The `symbol_name()` method itself is very simple — it returns the symbol name by a given index. However, in practice, it is almost always used **in pair with `symbols_total()`** and inside a loop.

---

## Method Signature

```python
async def symbol_name(
    index: int,
    selected: bool,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `index` — symbol index (numbering starts from `0`)
* `selected` determines where the symbol list is taken from:

  * `True` — only symbols from Market Watch
  * `False` — all available symbols
* The method returns an object with the symbol name

---

## 🧩 Code Example — Safe retrieval of symbol list

```python
async def get_symbols_safe(account, selected_only: bool = True) -> list[str]:
    symbols = []

    try:
        count_data = await account.symbols_total(selected_only=selected_only)
        total = count_data.total

        for i in range(total):
            try:
                symbol_data = await account.symbol_name(index=i, selected=selected_only)
                symbols.append(symbol_data.name)
            except Exception as e:
                print(f"Error getting symbol at index {i}: {e}")
                continue

        print(f"Successfully retrieved {len(symbols)} out of {total} symbols")

    except Exception as e:
        print(f"Error getting symbol count: {e}")

    return symbols
```

This example demonstrates an error-resistant way to iterate through the symbol list.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Getting Symbol Count

```python
count_data = await account.symbols_total(selected_only=selected_only)
total = count_data.total
```

At this step:

* a separate low-level call is performed
* the server returns the total number of symbols
* this value is used as the loop boundary

Without this step, it is impossible to correctly use `symbol_name()`.

---

### 2️⃣ Iterating Through Indices

```python
for i in range(total):
```

The code iterates through all possible indices:

* each index corresponds to one symbol
* the order is determined by the server

Indices are not stable identifiers for symbols.

---

### 3️⃣ Getting Symbol Name by Index

```python
symbol_data = await account.symbol_name(index=i, selected=selected_only)
```

At this step:

* one asynchronous call is performed
* the server returns the symbol name for the given index
* the name is available in the `symbol_data.name` field

The method does not return any additional information about the symbol.

---

### 4️⃣ Local Error Handling

```python
except Exception as e:
    print(f"Error getting symbol at index {i}: {e}")
    continue
```

Here, important protective logic is implemented:

* an error retrieving one symbol does not interrupt the entire process
* the problematic index is simply skipped
* the loop continues

This is especially important when working with large symbol lists.

---

### 5️⃣ Handling Symbol Count Error

```python
except Exception as e:
    print(f"Error getting symbol count: {e}")
```

If the total number of symbols could not be retrieved:

* further iteration is impossible
* the function returns an empty list

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`symbol_name()`**:

* returns the symbol name by index
* does not know the total number of symbols
* does not manage list iteration
* does not handle iteration errors

**`get_symbols_safe()`**:

* retrieves the number of symbols
* manages the loop
* handles errors
* forms the final list

---

## Summary

This example illustrates the standard pattern of working with index-based low-level methods:

> **get size → iterate → handle errors → collect result**

The `symbol_name()` method provides minimal data access, while all iteration and resilience logic is implemented on the user code side.
