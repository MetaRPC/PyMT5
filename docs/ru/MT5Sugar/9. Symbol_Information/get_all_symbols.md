# Получить все символы (`get_all_symbols`)

> **Sugar-метод:** Возвращает полный список всех доступных торговых символов.

**Информация об API:**

* **Метод:** `sugar.get_all_symbols()`
* **Возвращает:** Список имён символов (строки)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_all_symbols(self) -> List[str]
```

---

## 🔽 Входные параметры

Параметры не требуются.

---

## Возвращаемое значение

| Тип | Описание |
|------|-------------|
| `List[str]` | Список всех доступных имён символов (например, ["EURUSD", "GBPUSD", ...]) |

---

## 🏛️ Основное

**Что делает:**

- Получает полный список всех символов, доступных у брокера
- Использует оптимизированное пакетное получение с пагинацией
- Возвращает по 100 символов на страницу
- Эффективнее, чем индивидуальные запросы символов

**Ключевое поведение:**

- Автоматически обрабатывает пагинацию
- Возвращает ВСЕ символы (не только видимые)
- Получает по 100 символов за запрос
- Может вернуть сотни символов
- Возвращает только имена символов (не полную информацию)

---

## ⚡ Под капотом

```
MT5Sugar.get_all_symbols()
    ↓ выполняет цикл с пагинацией (по 100 на страницу)
    ↓ вызывает
MT5Service.get_symbol_params_many(name_filter=None)
    ↓ вызывает
MT5Account.symbol_params_many()
    ↓ gRPC protobuf
MarketInfoService.SymbolParamsMany()
    ↓ терминал MT5
    ↓ извлекает имена символов из SymbolParams
```

**Цепочка вызовов:**

1. Sugar запускает цикл пагинации (page=1, size=100)
2. Sugar вызывает Service.get_symbol_params_many() без фильтра
3. Service перенаправляет в Account.symbol_params_many()
4. Account отправляет gRPC-запрос в терминал
5. Sugar извлекает name из каждого SymbolParams
6. Продолжает пагинацию, пока не будут получены все символы
7. Возвращает полный список имён символов

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:1642`
- Service: `src/pymt5/mt5_service.py:658`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1221`

---

## Когда использовать

**Используйте `get_all_symbols()`, когда:**

- Строите интерфейс выбора символов
- Сканируете все символы в поисках возможностей
- Проверяете списки символов
- Обнаруживаете доступные инструменты
- Функции автодополнения символов

**Не используйте, когда:**

- Нужны только конкретные символы (задайте их напрямую)
- Нужны только валютные пары (используйте подход с фильтрацией)
- Нужна полная информация о символе (используйте `get_symbol_info()`)
- Проверяете существование одного символа (используйте `is_symbol_available()`)

---

## 🔗 Примеры

### Пример 1: Список всех доступных символов

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def list_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить все символы
    symbols = await sugar.get_all_symbols()

    print(f"Total symbols available: {len(symbols)}")
    print(f"First 10 symbols: {symbols[:10]}")

# Вывод:
# Total symbols available: 358
# First 10 symbols: ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURAUD', 'EURCAD']
```

### Пример 2: Найти только валютные пары

```python
async def find_forex_pairs():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить все символы
    all_symbols = await sugar.get_all_symbols()

    # Распространённые коды валют форекс
    currencies = ['EUR', 'USD', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']

    # Отфильтровать валютные пары (обе валюты в общем списке)
    forex_pairs = [
        s for s in all_symbols
        if len(s) == 6 and s[:3] in currencies and s[3:] in currencies
    ]

    print(f"Forex pairs: {len(forex_pairs)}")
    print(forex_pairs)

# Вывод:
# Forex pairs: 28
# ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', ...]
```

### Пример 3: Поиск конкретных символов

```python
async def search_symbols():
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    await sugar.quick_connect("FxPro-MT5 Demo")

    # Получить все символы
    all_symbols = await sugar.get_all_symbols()

    # Найти символы золота
    gold_symbols = [s for s in all_symbols if 'XAU' in s or 'GOLD' in s]
    print(f"Gold symbols: {gold_symbols}")

    # Найти пары EUR
    eur_pairs = [s for s in all_symbols if s.startswith('EUR')]
    print(f"EUR pairs ({len(eur_pairs)}): {eur_pairs}")

    # Найти криптовалюты
    crypto = [s for s in all_symbols if 'BTC' in s or 'ETH' in s]
    print(f"Crypto: {crypto}")
```

---

## Типичные ошибки

**Ошибка 1: Ожидание отсортированного результата**
```python
# Символы могут быть не в алфавитном порядке
symbols = await sugar.get_all_symbols()
# Порядок зависит от ответа брокера
```

**Решение:** Сортируйте вручную при необходимости
```python
symbols = await sugar.get_all_symbols()
symbols_sorted = sorted(symbols)
```

**Ошибка 2: Отсутствие кэширования результатов**
```python
# Повторное получение всех символов медленно
for i in range(10):
    symbols = await sugar.get_all_symbols()  # Медленно!
    # Что-то делать с символами
```

**Решение:** Кэшируйте список
```python
# Получить один раз
symbols_cache = await sugar.get_all_symbols()

# Использовать кэшированный список
for i in range(10):
    # Использовать symbols_cache
    pass
```

**Ошибка 3: Предположение, что все символы торгуемы**
```python
# Не все символы могут быть торгуемы в данный момент
symbols = await sugar.get_all_symbols()

# Некоторые могут быть отключены или ограничены
for symbol in symbols:
    await sugar.buy_market(symbol, volume=0.01)  # Может не сработать!
```

**Решение:** Сначала проверяйте, торгуем ли символ
```python
symbols = await sugar.get_all_symbols()

for symbol in symbols:
    # Проверить доступность
    is_available = await sugar.is_symbol_available(symbol)

    if is_available:
        # Теперь безопасно торговать
        pass
```

---

## Полезные советы

**Совет 1: Кэширование символов с TTL**
```python
from datetime import datetime, timedelta

class SymbolCache:
    def __init__(self, ttl_minutes=60):
        self.symbols = None
        self.last_fetch = None
        self.ttl = timedelta(minutes=ttl_minutes)

    async def get_symbols(self, sugar):
        """Получить символы с кэшем на 1 час."""
        now = datetime.now()

        if self.symbols is None or (now - self.last_fetch) > self.ttl:
            self.symbols = await sugar.get_all_symbols()
            self.last_fetch = now

        return self.symbols

# Использование
cache = SymbolCache(ttl_minutes=60)
symbols = await cache.get_symbols(sugar)
```

**Совет 2: Группировка символов по типу**
```python
from collections import defaultdict

async def group_symbols_by_type():
    """Сгруппировать символы по категориям."""
    symbols = await sugar.get_all_symbols()

    groups = defaultdict(list)

    for symbol in symbols:
        if 'XAU' in symbol or 'GOLD' in symbol:
            groups['Metals'].append(symbol)
        elif 'BTC' in symbol or 'ETH' in symbol:
            groups['Crypto'].append(symbol)
        elif len(symbol) == 6:  # Вероятно, форекс
            groups['Forex'].append(symbol)
        else:
            groups['Other'].append(symbol)

    for category, syms in groups.items():
        print(f"{category}: {len(syms)} symbols")
```

**Совет 3: Создание автодополнения символов**
```python
async def autocomplete_symbol(prefix: str):
    """Автодополнение имён символов."""
    all_symbols = await sugar.get_all_symbols()

    # Найти совпадения
    matches = [s for s in all_symbols if s.startswith(prefix.upper())]

    return matches[:10]  # Вернуть топ-10 совпадений

# Использование
matches = await autocomplete_symbol("EUR")
print(matches)  # ['EURAUD', 'EURCAD', 'EURCHF', ...]
```

---

## 📚 См. также

- [get_symbol_info](get_symbol_info.md) - Получить полные параметры символа
- [is_symbol_available](is_symbol_available.md) - Проверить существование символа
- [get_symbol_digits](get_symbol_digits.md) - Получить число десятичных знаков символа
