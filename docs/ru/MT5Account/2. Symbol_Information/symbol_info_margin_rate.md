# Get Symbol Margin Rates

> **Запрос:** получить ставки маржи для символа и типа ордера.

**Информация об API:**

* **Низкоуровневый API:** `MT5Account.symbol_info_margin_rate(...)` (определён в `package/MetaRpcMT5/mt5_account.py`)
* **gRPC-сервис:** `mt5_term_api.MarketInfo`
* **Proto-определение:** `SymbolInfoMarginRate` (определено в `mt5-term-api-market-info.proto`)

### RPC

* **Сервис:** `mt5_term_api.MarketInfo`
* **Метод:** `SymbolInfoMarginRate(SymbolInfoMarginRateRequest) -> SymbolInfoMarginRateReply`
* **Низкоуровневый клиент (сгенерированный):** `MarketInfoStub.SymbolInfoMarginRate(request, metadata, timeout)`

## 💬 Только самое главное

* **Что это.** Получить начальную и поддерживающую ставки маржи для конкретного символа и типа ордера.
* **Зачем это нужно.** Рассчитать требования к марже перед размещением ордеров, понять условия кредитного плеча.
* **Когда использовать.** Используйте перед торговлей для оценки потребности в марже, особенно для разных типов ордеров (BUY/SELL).

---

## 🎯 Назначение

Используйте его для запроса требований к марже:

* Рассчитать требуемую маржу перед открытием позиций
* Понять различия маржи между ордерами BUY и SELL
* Оценить влияние кредитного плеча на маржу
* Проверить доступную маржу перед торговлей
* Сравнить требования к марже по символам
* Планировать размер позиции на основе доступной маржи

---

## 📚 Руководство

Подробное построчное объяснение с примерами смотрите здесь:
**-> [symbol_info_margin_rate - Как это работает](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW.md)**

---

## Сигнатура метода

```python
async def symbol_info_margin_rate(
    self,
    symbol: str,
    order_type: market_info_pb2.ENUM_ORDER_TYPE,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoMarginRateData
```

**Сообщение запроса:**

```protobuf
message SymbolInfoMarginRateRequest {
  string symbol = 1;
  ENUM_ORDER_TYPE order_type = 2;
}
```

**Сообщение ответа:**

```protobuf
message SymbolInfoMarginRateReply {
  oneof response {
    SymbolInfoMarginRateData data = 1;
    Error error = 2;
  }
}

message SymbolInfoMarginRateData {
  double maintenance_margin_rate = 1;
  double initial_margin_rate = 2;
}
```

---

## 🔽 Вход

| Параметр    | Тип                     | Описание                           |
| ------------ | ------------------------ | ------------------------------------- |
| `symbol`     | `str` (обязательно)         | Имя символа                           |
| `order_type` | `ENUM_ORDER_TYPE` (enum) | Тип ордера (BUY, SELL и т. д.)          |
| `deadline`    | `datetime` (необязательно)   | Крайний срок для gRPC-вызова (UTC datetime) |
| `cancellation_event` | `asyncio.Event` (необязательно) | Событие для отмены операции |

---

## ⬆️ Выход

| Поле                     | Тип     | Python-тип | Описание                     |
| ------------------------- | -------- | ----------- | ------------------------------- |
| `initial_margin_rate`     | `double` | `float`     | Начальная ставка маржи             |
| `maintenance_margin_rate` | `double` | `float`     | Поддерживающая ставка маржи         |

**Возвращаемое значение:** Метод возвращает объект `SymbolInfoMarginRateData` с полями ставок маржи.

---

## 🧱 Связанные enum (из proto)

> **Примечание:** В Python-коде используйте полный путь enum из модуля market_info.

### `ENUM_ORDER_TYPE`

Определено в `mt5-term-api-market-info.proto`.

| Константа | Значение | Описание |
|----------|-------|-------------|
| `ORDER_TYPE_BUY` | 0 | Рыночный ордер на покупку |
| `ORDER_TYPE_SELL` | 1 | Рыночный ордер на продажу |
| `ORDER_TYPE_BUY_LIMIT` | 2 | Отложенный ордер Buy Limit |
| `ORDER_TYPE_SELL_LIMIT` | 3 | Отложенный ордер Sell Limit |
| `ORDER_TYPE_BUY_STOP` | 4 | Отложенный ордер Buy Stop |
| `ORDER_TYPE_SELL_STOP` | 5 | Отложенный ордер Sell Stop |
| `ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Отложенный ордер Buy Stop Limit |
| `ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Отложенный ордер Sell Stop Limit |
| `ORDER_TYPE_CLOSE_BY` | 8 | Закрытие встречным ордером |

**Использование в Python:**
```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить ставки маржи для ордеров BUY
rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)
print(f"Initial margin rate: {rates.initial_margin_rate}")
print(f"Maintenance margin rate: {rates.maintenance_margin_rate}")
```

---

## 🧩 Примечания и советы

* **Автоматическое переподключение:** Встроенная защита от временных ошибок gRPC с автоматическим переподключением через `execute_with_reconnect`.
* **Таймаут по умолчанию:** Если `deadline` равен `None`, метод будет ждать бесконечно (или до таймаута сервера).
* **Значение ставок маржи:**
  - **Начальная ставка маржи:** Ставка, используемая при открытии позиции (умножается на стоимость контракта)
  - **Поддерживающая ставка маржи:** Ставка, используемая для поддержания открытой позиции
* **Различия ставок:** Ордера BUY и SELL могут иметь разные ставки маржи для одного символа.
* **Хеджевые счета:** На хеджевых счетах ставки маржи обычно одинаковы для BUY и SELL.
* **Неттинговые счета:** На неттинговых счетах расчёты маржи могут отличаться в зависимости от направления позиции.
* **Расчёт:** Требуемая маржа = (Размер контракта × Объём × Цена) × Ставка маржи
* **Обработка UUID:** UUID экземпляра терминала автоматически генерируется сервером, если не указан.
  Для явного контроля (например, в сценариях стриминга) передайте `id_=uuid4()` в конструктор.
  
---

## 🔗 Примеры использования

### 1) Получить ставки маржи для ордера BUY

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить ставки маржи для ордера BUY
rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"BUY Order Margin Rates:")
print(f"  Initial: {rates.initial_margin_rate}")
print(f"  Maintenance: {rates.maintenance_margin_rate}")
```

### 2) Сравнить ставки маржи BUY и SELL

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Получить ставки маржи BUY
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

# Получить ставки маржи SELL
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)

print(f"XAUUSD Margin Rates:")
print(f"  BUY  - Initial: {buy_rates.initial_margin_rate}, Maintenance: {buy_rates.maintenance_margin_rate}")
print(f"  SELL - Initial: {sell_rates.initial_margin_rate}, Maintenance: {sell_rates.maintenance_margin_rate}")

if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
    print("  Same margin rates for both directions (hedge account)")
else:
    print("  Different margin rates (check account type)")
```

### 3) Рассчитать требуемую маржу перед торговлей

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def calculate_required_margin(
    account,
    symbol: str,
    volume: float,
    order_type: int = market_info_pb2.ORDER_TYPE_BUY
) -> float:
    """Рассчитать требуемую маржу для открытия позиции"""

    # Получить ставки маржи
    rates = await account.symbol_info_margin_rate(
        symbol=symbol,
        order_type=order_type
    )

    # Получить размер контракта
    contract_size_data = await account.symbol_info_double(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_TRADE_CONTRACT_SIZE
    )

    # Получить текущую цену (ASK для BUY, BID для SELL)
    if order_type in [market_info_pb2.ORDER_TYPE_BUY, market_info_pb2.ORDER_TYPE_BUY_LIMIT, market_info_pb2.ORDER_TYPE_BUY_STOP]:
        price_data = await account.symbol_info_double(symbol=symbol, property=market_info_pb2.SYMBOL_ASK)
    else:
        price_data = await account.symbol_info_double(symbol=symbol, property=market_info_pb2.SYMBOL_BID)

    # Рассчитать маржу
    contract_value = contract_size_data.value * volume * price_data.value
    required_margin = contract_value * rates.initial_margin_rate

    return required_margin

# Использование
margin = await calculate_required_margin(
    account=account,
    symbol="EURUSD",
    volume=1.0,
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Required margin for 1.0 lot EURUSD BUY: ${margin:.2f}")
```

### 4) Проверить, достаточно ли доступной маржи

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

async def can_open_position(
    account,
    symbol: str,
    volume: float,
    order_type: int = market_info_pb2.ORDER_TYPE_BUY
) -> bool:
    """Проверить, достаточно ли на счёте маржи для открытия позиции"""

    # Рассчитать требуемую маржу (из предыдущего примера)
    required_margin = await calculate_required_margin(account, symbol, volume, order_type)

    # Получить свободную маржу
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    # Проверить достаточность
    if free_margin >= required_margin:
        print(f"[OK] Sufficient margin:")
        print(f"  Required: ${required_margin:.2f}")
        print(f"  Available: ${free_margin:.2f}")
        return True
    else:
        print(f"[ERROR] Insufficient margin:")
        print(f"  Required: ${required_margin:.2f}")
        print(f"  Available: ${free_margin:.2f}")
        print(f"  Deficit: ${required_margin - free_margin:.2f}")
        return False

# Использование
if await can_open_position(account, "EURUSD", 2.0):
    print("The account has enough free margin to open the 2.0 lot position (per this estimate)")
```

### 5) Получить ставки маржи с таймаутом

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

# Установить крайний срок
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    rates = await account.symbol_info_margin_rate(
        symbol="GBPUSD",
        order_type=market_info_pb2.ORDER_TYPE_BUY,
        deadline=deadline
    )
    print(f"Margin rates retrieved: {rates.initial_margin_rate}")
except Exception as e:
    print(f"Timeout or error: {e}")
```

### 6) Сравнить требования к марже по символам

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def compare_symbol_margins(account, symbols: list[str]):
    """Сравнить требования к марже для нескольких символов"""

    print(f"{'Symbol':<10} {'Initial Rate':<15} {'Maintenance Rate':<20}")
    print("=" * 45)

    for symbol in symbols:
        try:
            rates = await account.symbol_info_margin_rate(
                symbol=symbol,
                order_type=market_info_pb2.ORDER_TYPE_BUY
            )
            print(f"{symbol:<10} {rates.initial_margin_rate:<15.4f} {rates.maintenance_margin_rate:<20.4f}")
        except Exception as e:
            print(f"{symbol:<10} ERROR: {e}")

# Использование
await compare_symbol_margins(account, ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"])
```

---

## 📚 См. также

* [symbol_info_double](./symbol_info_double.md) - Получить свойства символа типа double (размер контракта, цены)
* [order_calc_margin](../5. Trading_Operations/order_calc_margin.md) - Рассчитать маржу для конкретных параметров ордера
* [account_info_double](../1. Account_Information/account_info_double.md) - Получить информацию о марже счёта
