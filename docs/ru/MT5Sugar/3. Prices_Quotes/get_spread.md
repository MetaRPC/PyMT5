# Получение спреда (`get_spread`)

> **Sugar-метод:** Возвращает текущий спред (ASK - BID) в ценовых единицах.

**Информация об API:**

* **Метод:** `sugar.get_spread(symbol)`
* **Возвращает:** спред как `float` (в ценовых единицах, не в пунктах)
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_spread(self, symbol: Optional[str] = None) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| `symbol` | `Optional[str]` | Торговый символ (например, "EURUSD"). Использует default_symbol, если None |

| Выход | Тип | Описание |
|--------|------|-------------|
| `spread` | `float` | Текущий спред (ASK - BID) в ценовых единицах |

---

## 🏛️ Основное

* **Что это:** спред = ASK - BID, комиссия брокера за сделку.
* **Зачем нужно:** оценка торговых издержек, выбор периодов с низким спредом.
* **Формула:** спред (пункты) = (ASK - BID) × 10000 (для EURUSD)

---

## ⚡ Под капотом

```
MT5Sugar.get_spread(symbol)
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ calls
MT5Account.symbol_info_tick(symbol)
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Расчёт:** Sugar-слой вычисляет `tick.ask - tick.bid`

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:516`
- Service: `src/pymt5/mt5_service.py:680`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1095`

---

## Когда использовать

**Анализ издержек** — понимание торговых комиссий

**Выбор времени сделки** — выбор периодов с низким спредом

**Сравнение брокеров** — сравнение издержек исполнения

**Скальпинг** — критично для краткосрочных стратегий

**Расчёт риска** — учёт спреда в P/L

---

## 🔗 Примеры использования

### 1) Проверка текущего спреда

```python
spread = await sugar.get_spread("EURUSD")
spread_pips = spread * 10000  # Перевод в пункты

print(f"EURUSD Spread: {spread:.5f}")
print(f"Spread (pips): {spread_pips:.1f}")
# Вывод: Spread (pips): 1.2
```

---

### 2) Ожидание низкого спреда перед торговлей

```python
max_spread_pips = 2.0

spread = await sugar.get_spread("EURUSD")
spread_pips = spread * 10000

if spread_pips <= max_spread_pips:
    print(f"Good spread: {spread_pips:.1f} pips")
    ticket = await sugar.buy_market("EURUSD", 0.1)
else:
    print(f"Spread too high: {spread_pips:.1f} pips - waiting")
```

---

### 3) Расчёт цены безубыточности

```python
ask = await sugar.get_ask("EURUSD")
spread = await sugar.get_spread("EURUSD")

# После покупки по ASK цена должна вырасти на спред, чтобы выйти в ноль
breakeven = ask + spread

print(f"Entry (ASK):  {ask:.5f}")
print(f"Spread:       {spread:.5f}")
print(f"Break-even:   {breakeven:.5f}")
print(f"Must move:    {spread * 10000:.1f} pips to profit")
```

---

## Связанные методы

**Методы цен:**

* `get_bid()` — цена BID
* `get_ask()` — цена ASK
* `get_price_info()` — полные данные о цене, включая спред
* `get_symbol_info()` — параметры символа, включая типичный спред

**Ручной расчёт:**

```python
# Метод возвращает это автоматически:
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
spread = ask - bid

# Или используйте get_spread() напрямую:
spread = await sugar.get_spread("EURUSD")
```

---

## Частые ошибки

### 1) Путаница ценовых единиц с пунктами

```python
# НЕВЕРНО - спред в ценовых единицах, а не в пунктах
spread = await sugar.get_spread("EURUSD")
print(f"Spread: {spread} pips")  # Неверно! Показывает 0.00012, а не 1.2

# ВЕРНО - перевод в пункты
spread = await sugar.get_spread("EURUSD")
spread_pips = spread * 10000
print(f"Spread: {spread_pips:.1f} pips")
```

### 2) Неучёт спреда в расчётах прибыли

```python
# НЕВЕРНО - игнорируем спред
entry = await sugar.get_ask("EURUSD")
current = await sugar.get_bid("EURUSD")
profit_pips = (current - entry) * 10000  # Не учитывает спред!

# ВЕРНО - спред уже учтён
# При покупке по ASK и продаже по BID спред — автоматическая издержка
entry_ask = await sugar.get_ask("EURUSD")
current_bid = await sugar.get_bid("EURUSD")
profit_pips = (current_bid - entry_ask) * 10000  # Включает издержку спреда
```

---

## Советы профи

1. **Зависит от времени** — спред возрастает при низкой ликвидности (новости, открытие/закрытие рынка)

2. **Чем ниже, тем лучше** — типичный спред EURUSD: 0.5-2 пункта

3. **Скрытая стоимость** — спред платится в каждой сделке, и на входе, и на выходе

4. **Убийца скальпинга** — высокий спред делает краткосрочную торговлю убыточной

5. **Используйте get_price_info()** — получите BID, ASK и спред за один вызов

---

## 📚 См. также

- [get_bid](get_bid.md) - Получение цены BID
- [get_ask](get_ask.md) - Получение цены ASK
- [get_price_info](get_price_info.md) - Получение BID, ASK и спреда вместе
