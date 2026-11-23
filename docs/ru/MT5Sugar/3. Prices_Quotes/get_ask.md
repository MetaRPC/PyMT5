# Получение цены ASK (`get_ask`)

> **Sugar-метод:** Возвращает текущую цену ASK для символа.

**Информация об API:**

* **Метод:** `sugar.get_ask(symbol)`
* **Возвращает:** цену ASK как `float`
* **Слой:** HIGH (MT5Sugar)

---

## Сигнатура метода

```python
async def get_ask(self, symbol: Optional[str] = None) -> float
```

---

## ℹ️ Вход / Выход

| Вход | Тип | Описание |
|-------|------|-------------|
| `symbol` | `Optional[str]` | Торговый символ (например, "EURUSD"). Использует default_symbol, если None |

| Выход | Тип | Описание |
|--------|------|-------------|
| `ask` | `float` | Текущая цена ASK |

---

## 🏛️ Основное

* **Что это:** цена ASK — цена, по которой вы можете ПОКУПАТЬ (открыть long / закрыть short).
* **Зачем нужно:** открытие длинных позиций, закрытие коротких позиций, проверка цены исполнения.
* **Запомните:** ASK > BID всегда (вы платите спред)

---

## ⚡ Под капотом

```
MT5Sugar.get_ask(symbol)
    ↓ calls
MT5Service.get_symbol_tick(symbol)
    ↓ calls
MT5Account.symbol_info_tick(symbol)
    ↓ gRPC protobuf
MarketInfoService.SymbolInfoTick()
    ↓ MT5 Terminal
```

**Связанные файлы:**

- Sugar: `src/pymt5/mt5_sugar.py:502`
- Service: `src/pymt5/mt5_service.py:680`
- Account: `package/MetaRpcMT5/helpers/mt5_account.py:1095`

---

## Когда использовать

**Открытие длинных позиций** — покупка по цене ASK

**Закрытие коротких позиций** — цена выхода для шортов

**Расчёт стоимости входа** — ASK + спред

**Мониторинг спреда** — ASK - BID

**Проверка ордера** — убедиться в выгодной цене

---

## 🔗 Примеры использования

### 1) Открытие длинной позиции по текущему ASK

```python
ask = await sugar.get_ask("EURUSD")
print(f"Opening long at ASK: {ask:.5f}")

ticket = await sugar.buy_market("EURUSD", 0.1)
# Позиция открывается по цене ASK
```

---

### 2) Расчёт полной стоимости входа со спредом

```python
bid = await sugar.get_bid("EURUSD")
ask = await sugar.get_ask("EURUSD")
spread = ask - bid

print(f"BID:    {bid:.5f}")
print(f"ASK:    {ask:.5f}")
print(f"Spread: {spread:.5f}")
print(f"Cost:   ASK + spread = {ask:.5f}")
```

---

### 3) Ожидание выгодной цены ASK

```python
max_ask = 1.09000

while True:
    ask = await sugar.get_ask("EURUSD")
    if ask <= max_ask:
        print(f"Good price! ASK: {ask:.5f}")
        ticket = await sugar.buy_market("EURUSD", 0.1)
        break
    await asyncio.sleep(1)
```

---

## Связанные методы

**Методы цен:**

* `get_bid()` — цена BID (цена продажи)
* `get_spread()` — спред в пунктах
* `get_price_info()` — полные данные о цене
* `wait_for_price()` — ожидание обновления цены

**Соотношения цен:**
```python
# ASK = цена, по которой вы ПОКУПАЕТЕ
ask = await sugar.get_ask("EURUSD")

# BID = цена, по которой вы ПРОДАЁТЕ
bid = await sugar.get_bid("EURUSD")

# Всегда верно:
assert ask > bid
```

---

## Частые ошибки

### 1) Использование ASK, когда нужен BID

```python
# НЕВЕРНО - используем ASK для закрытия long
ask = await sugar.get_ask("EURUSD")
# Длинные позиции закрываются по BID, а не по ASK!

# ВЕРНО - закрываем long по BID
bid = await sugar.get_bid("EURUSD")
ticket = await sugar.close_position(position_ticket)
```

### 2) Забытая стоимость спреда

```python
# НЕВЕРНО - без учёта спреда
ask = await sugar.get_ask("EURUSD")
# Чтобы выйти в ноль, цена должна пройти величину спреда!

# ВЕРНО - учитываем спред
ask = await sugar.get_ask("EURUSD")
bid = await sugar.get_bid("EURUSD")
spread_pips = (ask - bid) * 10000
print(f"Need {spread_pips:.1f} pips just to break even")
```

---

## Советы профи

1. **ASK для открытия long** — вы покупаете по цене ASK

2. **ASK для закрытия short** — выход из short по ASK

3. **Всегда выше BID** — ASK = BID + спред

4. **Спред — это ваша стоимость** — чтобы получить прибыль, нужно перекрыть спред

5. **Используйте get_price_info()** — получите BID и ASK вместе

---

## 📚 См. также

- [get_bid](get_bid.md) - Получение цены BID
- [get_spread](get_spread.md) - Получение спреда bid-ask
- [get_price_info](get_price_info.md) - Получение BID, ASK и спреда вместе
