# Проверить существование символа

> **Запрос:** проверить, существует ли символ с указанным именем на торговой платформе.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_exist(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolExist` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolExist(SymbolExistRequest) -> SymbolExistReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolExist(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Проверить, существует ли символ и является ли он стандартным или пользовательским.
* **Зачем это нужно.** Проверить имена символов перед торговлей или запросом данных.
* **Когда использовать.** Используйте перед торговлей или подпиской на данные символа.

---

## 🎯 Назначение

Используйте для проверки символов:

* Проверить существование символа на платформе
* Определить стандартный символ или пользовательский
* Проверить пользовательский ввод
* Предотвратить ошибки при запросе несуществующих символов
* Предторговая проверка

---

## 📚 Руководство

Для подробного построчного объяснения с примерами смотрите:
**-> [symbol_exist - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_exist(
    self,
    symbol: str,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Сообщение запроса:**

```protobuf
message SymbolExistRequest {
  string name = 1;
}
```

**Сообщение ответа:**

```protobuf
message SymbolExistReply {
  oneof response {
    SymbolExistData data = 1;
    Error error = 2;
  }
}

message SymbolExistData {
  bool exists = 1;
  bool is_custom = 2;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbol`      | `str` (обязательный)    | Имя символа для проверки                                |
| `deadline`    | `datetime` (необязательно) | Крайний срок для gRPC-вызова (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции                  |

---

## ⬆️ Выход - `SymbolExistData`

| Поле        | Тип    | Python-тип  | Описание                                         |
| ----------- | ------ | ----------- | ------------------------------------------------ |
| `exists`    | `bool` | `bool`      | True, если символ существует                      |
| `is_custom` | `bool` | `bool`      | True, если символ пользовательский (не стандартный) |

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC.
* **Чувствительность к регистру:** Имена символов чувствительны к регистру.

---

## 🔗 Примеры использования

### 1) Проверить существование символа

```python
async def main():
    account = MT5Account(...)
    await account.connect_by_server_name("MetaQuotes-Demo")

    data = await account.symbol_exist(symbol="EURUSD")

    if data.exists:
        symbol_type = "custom" if data.is_custom else "standard"
        print(f"[OK] EURUSD exists ({symbol_type})")
    else:
        print("[ERROR] EURUSD does not exist")
```

### 2) Проверить символ перед торговлей

```python
async def validate_symbol(account: MT5Account, symbol: str) -> bool:
    """Validate symbol exists before trading"""
    data = await account.symbol_exist(symbol=symbol)

    if not data.exists:
        print(f"[ERROR] Symbol {symbol} does not exist")
        return False

    print(f"[OK] Symbol {symbol} validated")
    return True

# Использование:
if await validate_symbol(account, "EURUSD"):
    # Разместить сделку
    pass
```

### 3) Проверить несколько символов

```python
async def check_symbols(account: MT5Account, symbols: list[str]):
    """Check which symbols exist"""
    results = {}

    for symbol in symbols:
        data = await account.symbol_exist(symbol=symbol)
        results[symbol] = data.exists

    # Вывести результаты
    for symbol, exists in results.items():
        status = "[OK]" if exists else "[ERROR]"
        print(f"{status} {symbol}: {'exists' if exists else 'not found'}")

    return results

# Использование:
symbols = ["EURUSD", "GBPUSD", "INVALID"]
await check_symbols(account, symbols)
```

### 4) Отфильтровать действительные символы

```python
async def filter_valid_symbols(
    account: MT5Account,
    symbols: list[str]
) -> list[str]:
    """Filter out non-existent symbols"""
    valid_symbols = []

    for symbol in symbols:
        data = await account.symbol_exist(symbol=symbol)
        if data.exists:
            valid_symbols.append(symbol)

    print(f"[OK] {len(valid_symbols)} of {len(symbols)} symbols are valid")
    return valid_symbols

# Использование:
symbols = ["EURUSD", "GBPUSD", "INVALID_SYMBOL"]
valid = await filter_valid_symbols(account, symbols)
```

### 5) Определить пользовательские символы

```python
async def get_symbol_type(account: MT5Account, symbol: str) -> str:
    """Get symbol type (standard/custom/not found)"""
    data = await account.symbol_exist(symbol=symbol)

    if not data.exists:
        return "not_found"
    return "custom" if data.is_custom else "standard"

# Использование:
symbol_type = await get_symbol_type(account, "EURUSD")
print(f"EURUSD type: {symbol_type}")
```

---

## Распространённые паттерны

### Быстрая проверка существования

```python
async def symbol_exists(account: MT5Account, symbol: str) -> bool:
    """Quick check if symbol exists"""
    data = await account.symbol_exist(symbol=symbol)
    return data.exists
```

---

## 📚 См. также

* [symbols_total](./symbols_total.md) - Получить общее количество символов
* [symbol_name](./symbol_name.md) - Получить имя символа по индексу
* [symbol_select](./symbol_select.md) - Добавить/удалить символ из Market Watch
