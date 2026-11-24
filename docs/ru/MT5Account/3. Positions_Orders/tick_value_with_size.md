# Получение стоимости тика и размера контракта для символов

> **Запрос:** информация о стоимости тика и размере контракта для нескольких символов.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.tick_value_with_size(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.AccountHelper`
* **Определение в proto:** `TickValueWithSize` (определено в `mt5-term-api-account-helper.proto`)
* **Enum в этом методе:** 0 enum (простая структура данных)

### RPC

* **Сервис:** `mt5_term_api.AccountHelper`
* **Метод:** `TickValueWithSize(TickValueWithSizeRequest) -> TickValueWithSizeReply`
* **Низкоуровневый клиент (сгенерированный):** `AccountHelperStub.TickValueWithSize(request, metadata, timeout)`

## 💬 Только самое важное

* **Что это.** Получить стоимость тика и размеры контрактов для нескольких символов за один вызов.
* **Зачем это нужно.** Рассчитать стоимость позиции, требования по марже и прибыль/убыток в валюте счёта.
* **Когда использовать.** Используйте перед торговлей, чтобы понять стоимость тика и размер контракта для расчёта рисков.

---

## 🎯 Назначение

Используйте для получения ключевых торговых параметров:

* Получить стоимость тика (стоимость движения на один тик)
* Получить размер тика (минимальное изменение цены)
* Получить размер контракта (размер лота)
* Рассчитать прибыль/убыток на тик
* Понять требования по марже
* Эффективно запросить несколько символов пакетом

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [tick_value_with_size - How it works](../HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW.md)**

---

## Сигнатура метода

```python
async def tick_value_with_size(
    self,
    symbols: list[str],
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.TickValueWithSizeData
```

**Сообщение запроса:**

```protobuf
message TickValueWithSizeRequest {
  repeated string symbol_names = 1;
}
```

**Сообщение ответа:**

```protobuf
message TickValueWithSizeReply {
  TickValueWithSizeData data = 1;
  Error error = 2;
}

message TickValueWithSizeData {
  repeated TickSizeSymbol symbol_tick_size_infos = 1;
}
```

---

## 🔽 Вход

| Параметр      | Тип                     | Описание                                                |
| ------------- | ----------------------- | ------------------------------------------------------- |
| `symbols`     | `list[str]` (обязательно)  | Список имён символов для запроса                      |
| `deadline`    | `datetime` (опционально)   | Крайний срок для вызова gRPC (UTC datetime)          |
| `cancellation_event` | `asyncio.Event` (опционально) | Событие для отмены операции                   |

**Использование:**

```python
from datetime import datetime, timedelta, timezone

# Запрос нескольких символов
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

deadline = datetime.now(timezone.utc) + timedelta(seconds=5)
data = await account.tick_value_with_size(
    symbols=symbols,
    deadline=deadline
)
```

---

## ⬆️ Выход - `TickValueWithSizeData`

| Поле                     | Тип                       | Тип Python             | Описание                                 |
| ------------------------ | ------------------------- | ---------------------- | ---------------------------------------- |
| `symbol_tick_size_infos` | `repeated TickSizeSymbol` | `list[TickSizeSymbol]` | Список информации о стоимости/размере тика по каждому символу |

**Каждый TickSizeSymbol содержит:**

| Поле                   | Тип      | Тип Python  | Описание                                             |
| ---------------------- | -------- | ----------- | ---------------------------------------------------- |
| `Index`                | `int32`  | `int`       | Индекс в наборе результатов                          |
| `Name`                 | `string` | `str`       | Имя символа                                          |
| `TradeTickValue`       | `double` | `float`     | Стоимость тика (и для прибыли, и для убытка)          |
| `TradeTickValueProfit` | `double` | `float`     | Стоимость тика для расчёта прибыли                    |
| `TradeTickValueLoss`   | `double` | `float`     | Стоимость тика для расчёта убытка                     |
| `TradeTickSize`        | `double` | `float`     | Минимальное изменение цены (размер тика)              |
| `TradeContractSize`    | `double` | `float`     | Размер контракта (размер лота, например 100000 для EURUSD) |

---

## 🧩 Примечания и советы

* **Пакетный запрос:** Запрашивайте несколько символов за один вызов для эффективности.
* **Стоимость тика:** Стоимость в валюте счёта движения на один тик.
* **Размер контракта:** Размер одного стандартного лота (например, 100000 единиц для EURUSD).
* **Расчёт прибыли/убытка:** Используйте стоимость тика и размер тика для расчёта P/L на пункт/тик.
* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC.
* **Требуется подключение:** Сначала вызовите `connect_by_host_port()` или `connect_by_server_name()`.
* **Потокобезопасность:** Безопасно вызывать одновременно из нескольких asyncio-задач.

---

## 🔗 Примеры использования

### 1) Получить стоимость тика для нескольких символов

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account

async def main():
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

        data = await account.tick_value_with_size(
            symbols=symbols,
            deadline=deadline
        )

        for info in data.symbol_tick_size_infos:
            print(f"\n{info.Name}:")
            print(f"  Tick Value: ${info.TradeTickValue:.2f}")
            print(f"  Tick Size: {info.TradeTickSize}")
            print(f"  Contract Size: {info.TradeContractSize:.0f}")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### 2) Рассчитать прибыль на пункт

```python
async def calculate_profit_per_pip(
    account: MT5Account,
    symbol: str,
    lots: float
) -> float:
    """Calculate profit per pip for given symbol and volume"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Рассчитать прибыль на пункт (предполагая 10 тиков на пункт для большинства пар)
    profit_per_pip = info.TradeTickValue * 10 * lots

    print(f"{symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Profit per pip: ${profit_per_pip:.2f}")

    return profit_per_pip

# Использование:
profit_per_pip = await calculate_profit_per_pip(account, "EURUSD", 1.0)
```

### 3) Рассчитать требование по марже

```python
async def calculate_margin(
    account: MT5Account,
    symbol: str,
    lots: float,
    price: float,
    leverage: int
) -> float:
    """Calculate margin requirement for position"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Маржа = (Размер контракта * Лоты * Цена) / Кредитное плечо
    contract_value = info.TradeContractSize * lots * price
    margin = contract_value / leverage

    print(f"Margin calculation for {symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Price: {price}")
    print(f"  Leverage: 1:{leverage}")
    print(f"  Contract Size: {info.TradeContractSize:.0f}")
    print(f"  Required Margin: ${margin:.2f}")

    return margin

# Использование:
margin = await calculate_margin(account, "EURUSD", 1.0, 1.10000, 100)
```

### 4) Получить информацию о тиках для всех основных пар

```python
async def get_major_pairs_info(account: MT5Account):
    """Get tick value info for major currency pairs"""
    major_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "USDCAD", "NZDUSD"
    ]

    data = await account.tick_value_with_size(symbols=major_pairs)

    print("\nMajor Pairs Tick Information:")
    print(f"{'Symbol':<10} {'Tick Value':<12} {'Tick Size':<12} {'Contract Size':<15}")
    print("-" * 60)

    for info in data.symbol_tick_size_infos:
        print(f"{info.Name:<10} ${info.TradeTickValue:<11.2f} "
              f"{info.TradeTickSize:<12} {info.TradeContractSize:<15.0f}")

    return data

# Использование:
await get_major_pairs_info(account)
```

### 5) Рассчитать стоимость позиции

```python
async def calculate_position_value(
    account: MT5Account,
    symbol: str,
    lots: float,
    price: float
) -> dict:
    """Calculate total position value"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Стоимость позиции = Размер контракта * Лоты * Цена
    position_value = info.TradeContractSize * lots * price

    result = {
        "symbol": symbol,
        "lots": lots,
        "price": price,
        "contract_size": info.TradeContractSize,
        "position_value": position_value,
        "tick_value": info.TradeTickValue,
        "tick_size": info.TradeTickSize
    }

    print(f"\nPosition Value Calculation:")
    print(f"  Symbol: {symbol}")
    print(f"  Volume: {lots} lots")
    print(f"  Price: {price}")
    print(f"  Contract Size: {info.TradeContractSize:.0f}")
    print(f"  Position Value: ${position_value:,.2f}")

    return result

# Использование:
value = await calculate_position_value(account, "EURUSD", 1.0, 1.10000)
```

### 6) Сравнить стоимость тика между символами

```python
async def compare_tick_values(account: MT5Account, symbols: list[str]):
    """Compare tick values across multiple symbols"""
    data = await account.tick_value_with_size(symbols=symbols)

    # Сортировка по стоимости тика
    sorted_infos = sorted(
        data.symbol_tick_size_infos,
        key=lambda x: x.TradeTickValue,
        reverse=True
    )

    print("\nSymbols sorted by tick value:")
    for i, info in enumerate(sorted_infos, 1):
        print(f"{i}. {info.Name}: ${info.TradeTickValue:.2f} per tick")

    return sorted_infos

# Использование:
symbols = ["EURUSD", "GBPUSD", "USDJPY", "GOLD", "OIL"]
await compare_tick_values(account, symbols)
```

### 7) Рассчитать расстояние стоп-лосса

```python
async def calculate_sl_distance(
    account: MT5Account,
    symbol: str,
    lots: float,
    max_loss: float
) -> float:
    """Calculate maximum SL distance for given max loss"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Symbol {symbol} not found")

    info = data.symbol_tick_size_infos[0]

    # Рассчитать допустимое количество пунктов
    profit_per_pip = info.TradeTickValue * 10 * lots
    max_pips = max_loss / profit_per_pip if profit_per_pip > 0 else 0

    print(f"\nStop Loss Calculation for {symbol}:")
    print(f"  Volume: {lots} lots")
    print(f"  Max Loss: ${max_loss:.2f}")
    print(f"  Profit per pip: ${profit_per_pip:.2f}")
    print(f"  Max SL distance: {max_pips:.1f} pips")

    return max_pips

# Использование:
max_pips = await calculate_sl_distance(account, "EURUSD", 1.0, 100.0)
```

### 8) Проверить существование символов

```python
async def validate_symbols(
    account: MT5Account,
    symbols: list[str]
) -> dict:
    """Check which symbols are valid and available"""
    data = await account.tick_value_with_size(symbols=symbols)

    returned_symbols = {info.Name for info in data.symbol_tick_size_infos}
    requested_symbols = set(symbols)

    valid = list(returned_symbols)
    invalid = list(requested_symbols - returned_symbols)

    result = {
        "valid": valid,
        "invalid": invalid,
        "valid_count": len(valid),
        "invalid_count": len(invalid)
    }

    print(f"\nSymbol Validation:")
    print(f"  Valid symbols: {valid}")
    if invalid:
        print(f"  Invalid symbols: {invalid}")

    return result

# Использование:
symbols = ["EURUSD", "INVALID_SYMBOL", "GBPUSD"]
validation = await validate_symbols(account, symbols)
```

---

## Типовые шаблоны

### Получить стоимость тика для одного символа

```python
async def get_symbol_tick_value(account: MT5Account, symbol: str) -> float:
    """Get tick value for single symbol"""
    data = await account.tick_value_with_size(symbols=[symbol])
    if data.symbol_tick_size_infos:
        return data.symbol_tick_size_infos[0].TradeTickValue
    return 0.0
```

### Рассчитать риск на позицию

```python
async def calculate_risk(
    account: MT5Account,
    symbol: str,
    lots: float,
    sl_pips: float
) -> float:
    """Calculate risk amount for position with SL"""
    data = await account.tick_value_with_size(symbols=[symbol])
    if not data.symbol_tick_size_infos:
        return 0.0

    info = data.symbol_tick_size_infos[0]
    profit_per_pip = info.TradeTickValue * 10 * lots
    risk = profit_per_pip * sl_pips

    return risk
```

---

## 📚 См. также

* [opened_orders](./opened_orders.md) - Получить текущие открытые позиции
* [positions_total](./positions_total.md) - Получить количество открытых позиций
