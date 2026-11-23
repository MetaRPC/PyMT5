# Получение цены BID (`get_bid`)

> **Sugar-метод:** Возвращает текущую цену BID для символа.

**Информация об API:**

* **Метод:** `sugar.get_bid(symbol)`
* **Возвращает:** цену BID как `float`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_bid(self, symbol: Optional[str] = None) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| `symbol` | `Optional[str]` | Торговый символ (например, "EURUSD"). Использует default_symbol, если None |

| Выход | Тип | Описание |
|--------|------|-------------|
| `bid` | `float` | Текущая цена BID |

---

## 🏛️ Основное

* **Что это:** цена BID — цена, по которой вы можете ПРОДАВАТЬ (закрыть long / открыть short).
* **Зачем нужно:** проверка текущей рыночной цены, расчёт точек входа/выхода.
* **Запомните:** BID < ASK всегда (спред = ASK - BID)

---

## ⚡ Под капотом

```
MT5Sugar.get_bid(symbol)
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ calls
MT5Account.symbol_info_tick(symbol)
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Что происходит:**

1. **Sugar-слой:** проверяет символ, извлекает поле bid из тика
2. **Service-слой:** возвращает dataclass SymbolTick
3. **Account-слой:** gRPC-вызов для получения последнего тика
4. **Результат:** текущая цена BID

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:488`
- Service: `src/pymt5/mt5_service.py:680`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1095`

---

## Когда использовать

**Закрытие длинных позиций** — продажа по цене BID

**Открытие коротких позиций** — цена входа для шортов

**Мониторинг цены** — отслеживание текущей рыночной цены

**Расчёт спреда** — сравнение BID и ASK

**Проверка ордера** — проверить, выгодна ли цена

---

## 🔗 Примеры использования

### 1) Получение текущей цены BID

```python
bid = await sugar.get_bid("EURUSD")
print(f"EURUSD BID: {bid:.5f}")
# Вывод: EURUSD BID: 1.08530
```

---

### 2) Проверка выгодности цены перед закрытием long

```python
# У вас есть длинная позиция по 1.08000
entry_price = 1.08000
target_profit = 50  # пункты

bid = await sugar.get_bid("EURUSD")
profit_pips = (bid - entry_price) * 10000

if profit_pips >= target_profit:
    print(f"Target reached! Profit: {profit_pips:.1f} pips")
    ticket = await sugar.close_position(position_ticket)
else:
    print(f"Waiting... Current profit: {profit_pips:.1f} pips")
```

---

### 3) Расчёт спреда

```python
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
spread = (ask - bid) * 10000  # Перевод в пункты

print(f"BID:    {bid:.5f}")
print(f"ASK:    {ask:.5f}")
print(f"Spread: {spread:.1f} pips")
```

---

## Связанные методы

**Методы цен:**

* `get_ask()` — цена ASK (цена покупки)
* `get_spread()` — спред в пунктах
* `get_price_info()` — полные данные о цене (BID, ASK, спред, время)
* `wait_for_price()` — ожидание обновления цены

**BID против ASK:**

```python
# BID = цена, по которой вы ПРОДАЁТЕ (закрытие long, открытие short)
bid = await sugar.get_bid("EURUSD")

# ASK = цена, по которой вы ПОКУПАЕТЕ (открытие long, закрытие short)
ask = await sugar.get_ask("EURUSD")

# Spread = комиссия брокера
spread = ask - bid
```

---

## Частые ошибки

### 1) Использование BID, когда нужен ASK

```python
# НЕВЕРНО - используем BID для открытия длинной позиции
bid = await sugar.get_bid("EURUSD")
# Длинные позиции открываются по ASK, а не по BID!

# ВЕРНО - используем ASK для открытия long
ask = await sugar.get_ask("EURUSD")
ticket = await sugar.buy_market("EURUSD", 0.1)
```

### 2) Не указан символ

```python
# НЕВЕРНО - символ по умолчанию не задан
sugar = MT5Sugar(service)  # Нет default_symbol
bid = await sugar.get_bid()  # ValueError!

# ВЕРНО - укажите символ или задайте символ по умолчанию
sugar = MT5Sugar(service, default_symbol="EURUSD")
bid = await sugar.get_bid()  # Работает
# ИЛИ
bid = await sugar.get_bid("EURUSD")  # Работает всегда
```

---

## Советы профи

1. **BID для закрытия long** — вы продаёте по цене BID

2. **BID для открытия short** — вход в short по BID

3. **Всегда ниже ASK** — BID + спред = ASK

4. **Используйте get_price_info()** — получите BID, ASK, спред за один вызов

5. **Обновляется в реальном времени** — цена меняется с каждым тиком

---

## 📚 См. также

- [get_ask](get_ask.md) - Получение цены ASK
- [get_spread](get_spread.md) - Получение спреда bid-ask
- [get_price_info](get_price_info.md) - Получение BID, ASK и спреда вместе
