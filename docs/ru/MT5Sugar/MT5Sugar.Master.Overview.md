# MT5Sugar - Общий обзор

> Высокоуровневые удобные методы для автоматизации торговли в MetaTrader 5 на Python

**MT5Sugar** оборачивает экземпляр `MT5Service` (композиция, а не наследование) и добавляет удобные методы для:

- Расчёта размера позиции на основе риска (процент риска, SL/TP в пунктах)
- Автоматической нормализации объёма и цены
- Массовых операций (закрытие всех позиций, управление несколькими сделками)
- Исторического анализа и статистики
- Предторговой проверки и контроля маржи
- Мониторинга P/L в реальном времени и отслеживания позиций
- Упрощённого управления подключением

---

## Навигация по категориям

### 🔌 [01] ПОДКЛЮЧЕНИЕ

**Подключение к терминалу MT5 и проверка состояния соединения**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `quick_connect()` | Подключение по имени кластера (РЕКОМЕНДУЕТСЯ) | [Docs](1.%20Connection/quick_connect.md) |
| `is_connected()` | Проверить, установлено ли подключение к MT5 | [Docs](1.%20Connection/is_connected.md) |
| `ping()` | Проверить, что соединение активно | [Docs](1.%20Connection/ping.md) |

---

### 💰 [02] СВОЙСТВА СЧЁТА

**Быстрый доступ к балансу счёта и показателям маржи**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `get_balance()` | Баланс счёта (только реализованная прибыль) | [Docs](2.%20Account_Properties/get_balance.md) |
| `get_equity()` | Текущие средства (equity) (баланс + плавающий P/L) | [Docs](2.%20Account_Properties/get_equity.md) |
| `get_margin()` | Используемая в данный момент маржа | [Docs](2.%20Account_Properties/get_margin.md) |
| `get_free_margin()` | Доступная маржа для новых позиций | [Docs](2.%20Account_Properties/get_free_margin.md) |
| `get_margin_level()` | Уровень маржи в процентах (Equity / Margin x 100) | [Docs](2.%20Account_Properties/get_margin_level.md) |
| `get_floating_profit()` | Суммарная плавающая прибыль/убыток по всем открытым позициям | [Docs](2.%20Account_Properties/get_floating_profit.md) |
| `get_account_info()` | Полный снимок счёта за один вызов | [Docs](2.%20Account_Properties/get_account_info.md) |

**Синтаксис свойства:**

- `balance` -- async-свойство, эквивалентно `get_balance()` | [Docs](2.%20Account_Properties/balance_property.md)

**Структуры данных:**

- `AccountInfo` -- login, balance, equity, profit, margin, free_margin, margin_level, leverage, currency, company, trade_allowed, trade_expert, server_name, server_time

---

### 💹 [03] ЦЕНЫ И КОТИРОВКИ

**Работа с текущими рыночными ценами**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `get_bid()` | Текущая цена BID для символа | [Docs](3.%20Prices_Quotes/get_bid.md) |
| `get_ask()` | Текущая цена ASK для символа | [Docs](3.%20Prices_Quotes/get_ask.md) |
| `get_spread()` | Текущий спред (ASK - BID) в ценовых единицах | [Docs](3.%20Prices_Quotes/get_spread.md) |
| `get_price_info()` | Полный снимок цены (bid, ask, спред, время) | [Docs](3.%20Prices_Quotes/get_price_info.md) |
| `wait_for_price()` | Ожидание корректной цены с тайм-аутом | [Docs](3.%20Prices_Quotes/wait_for_price.md) |

**Структуры данных:**

- `PriceInfo` -- symbol, bid, ask, spread, time

---

### 📦 [04] ПРОСТАЯ ТОРГОВЛЯ

**Размещение рыночных и отложенных ордеров без SL/TP**

#### Рыночные ордера

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `buy_market()` | BUY по текущей цене ASK | [Docs](4.%20Simple_Trading/buy_market.md) |
| `sell_market()` | SELL по текущей цене BID | [Docs](4.%20Simple_Trading/sell_market.md) |

#### Отложенные ордера

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `buy_limit()` | Buy Limit -- покупка ниже текущей цены | [Docs](4.%20Simple_Trading/buy_limit.md) |
| `sell_limit()` | Sell Limit -- продажа выше текущей цены | [Docs](4.%20Simple_Trading/sell_limit.md) |
| `buy_stop()` | Buy Stop -- покупка выше текущей цены (пробой) | [Docs](4.%20Simple_Trading/buy_stop.md) |
| `sell_stop()` | Sell Stop -- продажа ниже текущей цены (пробой вниз) | [Docs](4.%20Simple_Trading/sell_stop.md) |

---

### 🎯 [05] ТОРГОВЛЯ С SL/TP

**Размещение ордеров со стоп-лоссом и тейк-профитом за один вызов**

Поддерживает как абсолютные значения цен, так и запись в пунктах через параметры `sl_pips` / `tp_pips`.

#### Рыночные ордера с SL/TP

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `buy_market_with_sltp()` | BUY с SL/TP (цены или пункты) | [Docs](5.%20Trading_With_SLTP/buy_market_with_sltp.md) |
| `sell_market_with_sltp()` | SELL с SL/TP (цены или пункты) | [Docs](5.%20Trading_With_SLTP/sell_market_with_sltp.md) |

#### Отложенные ордера с SL/TP

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `buy_limit_with_sltp()` | Buy Limit с SL/TP | [Docs](5.%20Trading_With_SLTP/buy_limit_with_sltp.md) |
| `sell_limit_with_sltp()` | Sell Limit с SL/TP | [Docs](5.%20Trading_With_SLTP/sell_limit_with_sltp.md) |

**Пример:**
```python
# BUY EURUSD: SL 50 пунктов, TP 100 пунктов (соотношение 1:2 R:R)
ticket = await sugar.buy_market_with_sltp("EURUSD", volume=0.1, sl_pips=50, tp_pips=100)
```

---

### ⚙️ [06] УПРАВЛЕНИЕ ПОЗИЦИЯМИ

**Изменение и закрытие существующих позиций**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `close_position()` | Закрыть позицию целиком по тикету | [Docs](6.%20Position_Management/close_position.md) |
| `close_position_partial()` | Частичное закрытие на заданный объём | [Docs](6.%20Position_Management/close_position_partial.md) |
| `close_all_positions()` | Закрыть все открытые позиции (опционально по символу) | [Docs](6.%20Position_Management/close_all_positions.md) |
| `modify_position_sltp()` | Изменить SL и/или TP (передайте None, чтобы оставить без изменений) | [Docs](6.%20Position_Management/modify_position_sltp.md) |
| `modify_position_sl()` | Изменить только стоп-лосс | [Docs](6.%20Position_Management/modify_position_sl.md) |
| `modify_position_tp()` | Изменить только тейк-профит | [Docs](6.%20Position_Management/modify_position_tp.md) |

---

### 📋 [07] ИНФОРМАЦИЯ О ПОЗИЦИЯХ

**Запрос и анализ открытых позиций**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `get_open_positions()` | Получить все открытые позиции | [Docs](7.%20Position_Information/get_open_positions.md) |
| `get_position_by_ticket()` | Получить конкретную позицию по тикету (None, если не найдена) | [Docs](7.%20Position_Information/get_position_by_ticket.md) |
| `get_positions_by_symbol()` | Получить все позиции по конкретному символу | [Docs](7.%20Position_Information/get_positions_by_symbol.md) |
| `has_open_position()` | Проверить наличие позиций (опционально по символу) | [Docs](7.%20Position_Information/has_open_position.md) |
| `count_open_positions()` | Общее количество открытых позиций | [Docs](7.%20Position_Information/count_open_positions.md) |
| `get_total_profit()` | Суммарный плавающий P/L по всем позициям | [Docs](7.%20Position_Information/get_total_profit.md) |
| `get_profit_by_symbol()` | Плавающий P/L по конкретному символу | [Docs](7.%20Position_Information/get_profit_by_symbol.md) |

**Структуры данных:**

- `PositionInfo` -- ticket, symbol, volume, type, profit, sl, tp, open_price, open_time

---

### 📊 [08] ИСТОРИЯ И СТАТИСТИКА

**Получение истории торговли и аналитики эффективности**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `get_deals()` | Закрытые позиции за указанный период | [Docs](8.%20History_Statistics/get_deals.md) |
| `get_profit()` | Суммарный реализованный P/L за указанный период | [Docs](8.%20History_Statistics/get_profit.md) |
| `get_daily_stats()` | Подробная дневная статистика | [Docs](8.%20History_Statistics/get_daily_stats.md) |

**Удобные обёртки для `get_deals()`:**

- `get_deals_today()` -- Period.TODAY
- `get_deals_yesterday()` -- Period.YESTERDAY
- `get_deals_this_week()` -- Period.THIS_WEEK (с понедельника по текущий момент)
- `get_deals_this_month()` -- Period.THIS_MONTH
- `get_deals_date_range(from_date, to_date)` -- Period.CUSTOM

**Удобные обёртки для `get_profit()`:**

- `get_profit_today()` -- Period.TODAY
- `get_profit_this_week()` -- Period.THIS_WEEK
- `get_profit_this_month()` -- Period.THIS_MONTH

**Структуры данных:**

- `DailyStats` -- date, deals_count, profit, commission, swap, volume

---

### 🏷️ [09] ИНФОРМАЦИЯ О СИМВОЛАХ

**Свойства символа и торговые условия**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `get_symbol_info()` | Полные параметры символа за один вызов | [Docs](9.%20Symbol_Information/get_symbol_info.md) |
| `get_all_symbols()` | Список всех доступных символов у брокера | [Docs](9.%20Symbol_Information/get_all_symbols.md) |
| `is_symbol_available()` | Проверить, существует ли символ и доступен ли он | [Docs](9.%20Symbol_Information/is_symbol_available.md) |
| `get_min_stop_level()` | Минимальная дистанция SL/TP в пунктах (points) | [Docs](9.%20Symbol_Information/get_min_stop_level.md) |
| `get_symbol_digits()` | Точность цены символа в знаках после запятой | [Docs](9.%20Symbol_Information/get_symbol_digits.md) |

**Структуры данных:**

- `SymbolInfo` -- name, bid, ask, spread, digits, point, volume_min, volume_max, volume_step, contract_size

---

### 🛡️ [10] УПРАВЛЕНИЕ РИСКАМИ

**Расчёт размера позиции, вычисление маржи и предторговая проверка**

| Метод | Описание | Документация |
|--------|-------------|---------------|
| `calculate_position_size()` | Автоматический расчёт размера лота по проценту риска | [Docs](10.%20Risk_Management/calculate_position_size.md) |
| `calculate_required_margin()` | Маржа, необходимая для конкретной позиции | [Docs](10.%20Risk_Management/calculate_required_margin.md) |
| `can_open_position()` | Полная предторговая проверка через MT5 order_check | [Docs](10.%20Risk_Management/can_open_position.md) |
| `get_max_lot_size()` | Максимально допустимый к торговле объём для символа | [Docs](10.%20Risk_Management/get_max_lot_size.md) |

**Пример:**
```python
# Автоматический расчёт размера лота с риском 2% при SL в 50 пунктов
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)
```

---

## Типичные сценарии использования

### 1. Простой рыночный ордер
```python
ticket = await sugar.buy_market("EURUSD", volume=0.10)
print(f"Position opened: #{ticket}")
```

### 2. Рыночный ордер с SL/TP в пунктах
```python
ticket = await sugar.buy_market_with_sltp(
    "EURUSD", volume=0.10,
    sl_pips=50, tp_pips=100
)
print(f"BUY #{ticket} opened (1:2 R:R)")
```

### 3. Расчёт размера позиции на основе риска
```python
symbol = "EURUSD"
risk_percent = 2.0      # Риск 2% от баланса
sl_pips = 50            # Стоп-лосс 50 пунктов

# Автоматически рассчитать размер лота
volume = await sugar.calculate_position_size(symbol, risk_percent, sl_pips)

# Проверить перед торговлей
can_open, reason = await sugar.can_open_position(symbol, volume)
if not can_open:
    print(f"Cannot trade: {reason}")
else:
    ticket = await sugar.buy_market_with_sltp(symbol, volume, sl_pips=50, tp_pips=100)
    print(f"Position #{ticket} opened (risking {risk_percent}%)")
```

### 4. Полный торговый процесс
```python
# Шаг 1: Подключение
await sugar.quick_connect("FxPro-MT5 Demo")

# Шаг 2: Проверка символа
if not await sugar.is_symbol_available("EURUSD"):
    raise ValueError("Symbol not available")

# Шаг 3: Расчёт размера позиции (риск 2%)
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

# Шаг 4: Проверка
can_open, reason = await sugar.can_open_position("EURUSD", volume)
if not can_open:
    raise RuntimeError(f"Cannot trade: {reason}")

# Шаг 5: Торговля
ticket = await sugar.buy_market_with_sltp("EURUSD", volume, sl_pips=50, tp_pips=100)
print(f"Position #{ticket} opened")
```

### 5. Мониторинг позиций и закрытие при просадке
```python
total_profit = await sugar.get_total_profit()
print(f"Floating P/L: ${total_profit:.2f}")

if total_profit < -500:
    print("Drawdown $500 -- closing all positions")
    closed_count = await sugar.close_all_positions()
    print(f"Closed {closed_count} positions")
```

### 6. Дневной отчёт об эффективности
```python
info = await sugar.get_account_info()
print(f"Account: #{info.login}, Balance: ${info.balance:.2f}, Equity: ${info.equity:.2f}")

stats = await sugar.get_daily_stats()
print(f"Today -- Deals: {stats.deals_count}, Profit: ${stats.profit:.2f}")
```

### 7. Анализ по конкретному символу
```python
symbol = "EURUSD"

has_pos = await sugar.has_open_position(symbol)
print(f"{symbol} has open position: {has_pos}")

if has_pos:
    profit = await sugar.get_profit_by_symbol(symbol)
    print(f"{symbol} floating P/L: ${profit:.2f}")

    if profit < -100:
        closed = await sugar.close_all_positions(symbol)
        print(f"Closed {closed} positions for {symbol}")
```

### 8. Отложенный ордер с проверкой
```python
symbol = "EURUSD"
volume = 0.1
limit_price = 1.08500

# Получить текущую цену
price_info = await sugar.get_price_info(symbol)
print(f"Current bid: {price_info.bid}, ask: {price_info.ask}")

# Проверить маржу
margin_needed = await sugar.calculate_required_margin(symbol, volume)
free_margin = await sugar.get_free_margin()

if margin_needed > free_margin:
    raise RuntimeError("Insufficient margin")

# Разместить Buy Limit ниже текущей цены
if limit_price < price_info.ask:
    ticket = await sugar.buy_limit_with_sltp(
        symbol, volume, price=limit_price,
        sl=1.08000, tp=1.09000
    )
    print(f"Buy Limit placed: #{ticket}")
```

### 9. Отслеживание недельной эффективности
```python
deals = await sugar.get_deals_this_week()
print(f"Trades this week: {len(deals)}")

if deals:
    total_profit = sum(d.profit for d in deals)
    winners = sum(1 for d in deals if d.profit > 0)
    win_rate = (winners / len(deals)) * 100

    print(f"Win rate: {win_rate:.1f}%")
    print(f"Total profit: ${total_profit:.2f}")
```

### 10. Портфель из нескольких символов
```python
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

print("PORTFOLIO STATUS")
print("=" * 40)

total_floating = 0.0

for symbol in symbols:
    positions = await sugar.get_positions_by_symbol(symbol)
    count = len(positions)
    profit = 0.0

    if count > 0:
        profit = await sugar.get_profit_by_symbol(symbol)
        total_floating += profit

    print(f"{symbol}: {count} positions, P/L: ${profit:.2f}")

print(f"\nTotal floating P/L: ${total_floating:.2f}")
```

---

## Связанная документация

- **MT5Account** -- Низкоуровневые методы gRPC/Proto | [Обзор MT5Account](../MT5Account/MT5Account.Master.Overview.md)
- **MT5Service** -- Промежуточный сервисный слой | [Обзор MT5Service](../MT5Service/MT5Service.Overview.md)
- **MT5Sugar** (этот документ) -- Высокоуровневые удобные методы

---

## Архитектура

```
MT5Sugar (High-level)  <-- Вы здесь
    |  Упрощённая торговля, управление рисками, аналитика
    v
MT5Service (Mid-level)
    |  Преобразование типов, управление тайм-аутами
    v
MT5Account (Low-level)
    |  Прямые вызовы gRPC/Protobuf
    v
MetaTrader 5 Terminal
```

**Сравнение слоёв:**

| Характеристика | MT5Account | MT5Service | MT5Sugar |
|---------|------------|------------|----------|
| Сложность | Низкоуровневый Proto | Промежуточный типизированный | Высокоуровневый удобный |
| Кривая обучения | Крутая | Умеренная | Пологая |
| Многословность | Высокая | Средняя | Низкая |
| Управление рисками | Вручную | Вручную | Встроенное |
| Расчёт размера позиции | Вручную | Вручную | Автоматический |
| SL/TP | Только цены | Только цены | Пункты или цены |
| Сценарий применения | Собственные обёртки | Стандартные приложения | Торговые боты |

---

## Соглашения

- Все методы асинхронные -- всегда используйте `await`
- Цены всегда абсолютные (например, 1.08500), а не относительные
- Объёмы всегда в лотах (например, 0.1), а не в единицах валюты
- **Пункты (Points)** -- минимальный шаг цены (для 5 знаков: 0.00001)
- **Пипсы (Pips)** -- стандартная единица трейдера (для 5 знаков: 1 пипс = 10 пунктов = 0.0001)
- Параметры `sl_pips` / `tp_pips` принимают значения в пипсах
- `get_min_stop_level()` возвращает значение в пунктах (points), а не в пипсах
- Тайм-ауты встроены (обычно 5 секунд) -- указывать не нужно
- Все значения времени -- это серверное время MT5 (не локальное)
- Имена символов чувствительны к регистру -- используйте верхний регистр (например, "EURUSD")
- `get_profit()` возвращает валовую прибыль -- не вычитает комиссию/своп. Для чистого значения используйте `get_daily_stats()`
- `get_deals()` возвращает до 10 000 позиций за один запрос -- разбивайте большие диапазоны дат

---

## Лучшие практики

### Управление рисками

```python
# ВСЕГДА используйте calculate_position_size для торговли на основе риска
volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)  # Хорошо

# Не используйте фиксированные размеры лота -- они не масштабируются с размером счёта
# volume = 0.1  # Плохо
```

### Предторговая проверка

```python
# ВСЕГДА проверяйте перед торговлей
can_open, reason = await sugar.can_open_position("EURUSD", volume)
if not can_open:
    print(f"Cannot trade: {reason}")
else:
    ticket = await sugar.buy_market_with_sltp("EURUSD", volume, sl_pips=50, tp_pips=100)
```

### Обработка ошибок

```python
# ВСЕГДА проверяйте ошибки
try:
    ticket = await sugar.buy_market("EURUSD", volume=0.1)
    print(f"Success: #{ticket}")
except RuntimeError as e:
    print(f"Trade failed: {e}")
```

### Используйте методы на основе пунктов

```python
# Предпочитайте запись в пунктах (более интуитивно)
await sugar.buy_market_with_sltp("EURUSD", 0.1, sl_pips=50, tp_pips=100)  # Хорошо

# Вместо ручного расчёта цен (подвержено ошибкам)
# ask = await sugar.get_ask("EURUSD")
# sl = ask - 0.00050  # Плохо -- ручной расчёт
```

### Управление подключением

```python
# Проверяйте подключение перед торговлей
if not sugar.is_connected():  # is_connected() синхронный (без await)
    await sugar.quick_connect("FxPro-MT5 Demo")

# Проверьте с помощью ping
if not await sugar.ping():
    raise RuntimeError("Connection lost")
```

---

## Быстрый старт

```python
from pymt5 import MT5Sugar, MT5Service, MT5Account

async def main():
    # 1. Создать экземпляры
    account = MT5Account.create(
        user=591129415,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )
    service = MT5Service(account)
    sugar = MT5Sugar(service)

    # 2. Подключение
    await sugar.quick_connect("FxPro-MT5 Demo")

    # 3. Расчёт размера позиции (риск 2%)
    volume = await sugar.calculate_position_size("EURUSD", 2.0, 50)

    # 4. Проверка
    can_open, reason = await sugar.can_open_position("EURUSD", volume)
    if not can_open:
        raise RuntimeError(f"Cannot trade: {reason}")

    # 5. Торговля с пунктами
    ticket = await sugar.buy_market_with_sltp(
        "EURUSD", volume,
        sl_pips=50, tp_pips=100
    )
    print(f"Position #{ticket} opened")
    print(f"Risk: 2% | SL: 50 pips | TP: 100 pips | R:R 1:2")
```

---

Начните с `buy_market_with_sltp()`, `calculate_position_size()` и `can_open_position()` -- эти три метода покрывают 80% торговых потребностей.
