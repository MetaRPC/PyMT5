## symbol_params_many — How it works

---

## 📌 Overview

This example shows how to use the low-level asynchronous method `symbol_params_many()` to retrieve **parameters for all symbols** using pagination loading.

The `symbol_params_many()` method is designed for batch retrieval of information for multiple symbols at once. Since the number of symbols can be large, the API uses **pagination**.

---

## Method Signature

```python
async def symbol_params_many(
    request: SymbolParamsManyRequest,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
):
```

Key points:

* The method is asynchronous and called with `await`
* Request parameters are passed through a `SymbolParamsManyRequest` object
* Pagination settings are specified in the request
* The method returns one page of data per call

---

## 🧩 Code Example — Iterating through all pages

```python
async def get_all_symbols(account):
    all_symbols = []
    page_number = 0
    items_per_page = 100

    while True:
        request = account_helper_pb2.SymbolParamsManyRequest()
        request.page_number = page_number
        request.items_per_page = items_per_page

        data = await account.symbol_params_many(request)

        all_symbols.extend(data.symbol_infos)
        print(f"Page {page_number}: Retrieved {len(data.symbol_infos)} symbols")

        if len(all_symbols) >= data.symbols_total:
            break

        if len(data.symbol_infos) == 0:
            break

        page_number += 1

    print(f"Total symbols retrieved: {len(all_symbols)}")
    return all_symbols
```

In this example, the `symbol_params_many()` method is used inside a loop to sequentially retrieve all pages.

---

## 🟢 Detailed Explanation

---

### 1️⃣ Initializing Pagination Parameters

```python
page_number = 0
items_per_page = 100
```

* `page_number` specifies the page number (numbering starts from `0`)
* `items_per_page` determines the maximum number of symbols per page

The page size is chosen by the user based on the balance between speed and data volume.

---

### 2️⃣ Forming the Request

```python
request = account_helper_pb2.SymbolParamsManyRequest()
request.page_number = page_number
request.items_per_page = items_per_page
```

At each step of the loop:

* a new request object is created
* current page parameters are set in it

The method does not store pagination state — all page management is on the user code side.

---

### 3️⃣ Retrieving One Page of Data

```python
data = await account.symbol_params_many(request)
```

At this step:

* one asynchronous call is performed
* the server returns one page of symbols
* the response contains:

  * list of symbol parameters for the current page
  * total number of symbols (`symbols_total`)

---

### 4️⃣ Accumulating Results

```python
all_symbols.extend(data.symbol_infos)
```

The retrieved data is added to the overall list.

The API does not aggregate pages automatically — this is done manually in user code.

---

### 5️⃣ Loop Exit Conditions

```python
if len(all_symbols) >= data.symbols_total:
    break
```

The loop terminates when:

* the number of collected symbols reaches the total count

---

```python
if len(data.symbol_infos) == 0:
    break
```

Additional safety check:

* if the server returned an empty page
* further requests make no sense

---

### 6️⃣ Moving to Next Page

```python
page_number += 1
```

After processing the current page, the number is incremented and the loop continues.

---

## The Role of Low-Level Method

Clear boundary of responsibility:

**`symbol_params_many()`**:

* returns one page of symbol parameters
* reports the total number of symbols
* does not manage pagination
* does not aggregate data

**`get_all_symbols()`**:

* manages page numbers
* accumulates results
* determines termination conditions
* forms the final list

---

## Summary

This example demonstrates the standard pattern of working with paginated low-level methods:

> **request page → process data → check conditions → request next page**

The `symbol_params_many()` method provides access to data by pages, while all iteration and aggregation logic is implemented on the user code side.
