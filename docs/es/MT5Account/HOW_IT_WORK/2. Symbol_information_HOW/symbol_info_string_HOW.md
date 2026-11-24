## symbol_info_string — How it works (SYMBOL_PATH)

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `symbol_info_string()` to retrieve a string property of a symbol and parse it at the application code level.

The example uses the `SYMBOL_PATH` property, which describes the symbol's location in the MetaTrader terminal's Market Watch hierarchy.

---

## Method Signature

```python
async def symbol_info_string(
    symbol: str,
    property: SymbolInfoStringProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* `symbol` — trading symbol name
* `property` specifies which string property of the symbol to retrieve
* The method returns an object containing the string property value

---

## 🧩 Code Example — Retrieving and parsing symbol path

```python
result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_PATH
)

path = result.value
folders = path.split("\\")

print(f"Symbol Path: {path}")
print(f"Hierarchy: {' > '.join(folders)}")
```

In this example, the `symbol_info_string()` method is used to retrieve the symbol path, after which the string is parsed into separate levels.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Requesting Symbol String Property

```python
result = await account.symbol_info_string(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_PATH
)
```

At this step:

* one asynchronous call is performed
* the symbol name and string property type are passed to the terminal
* a response object is returned

The method itself does not interpret the value — it only returns the string associated with the symbol.

---

### 2️⃣ Extracting Value

```python
path = result.value
```

Here:

* `result.value` — regular Python string
* example value:

```
Forex\\Majors\\EURUSD
```

After this line, the API work is complete, only the local value is used further.

---

### 3️⃣ Parsing String into Levels

```python
folders = path.split("\\")
```

The level separator is the `\\` character.

The result is a list of strings:

```python
["Forex", "Majors", "EURUSD"]
```

String parsing is performed entirely on the user code side.

---

### 4️⃣ Human-Readable Representation

```python
print(f"Hierarchy: {' > '.join(folders)}")
```

This step is not related to the API.

It is only needed for:

* visual display of hierarchy
* debugging
* interface output

---

## What SYMBOL_PATH Means

`SYMBOL_PATH` is a string description of **where the symbol is located in the Market Watch tree** of the MetaTrader terminal.

The last element of the path always corresponds to the symbol itself, while all previous elements are the groups in which it is displayed.

For example:

```
Forex\\Majors\\EURUSD
```

means:

> the symbol `EURUSD` is located in the `Majors` group, which is in the `Forex` group

---

## Important Note

The `SYMBOL_PATH` structure:

* is not standardized
* may differ between brokers
* may have different depth

Therefore, the path should be considered as **descriptive metadata**, not as a strict format.

---

## Summary

In this example, `symbol_info_string()` is used to retrieve a string property of a symbol and parse it in application code.

The method returns the string without interpretation, while all logic for analyzing and using the value is entirely on the user side.
