# MT5Account - Информация о счёте - Обзор

> Баланс счёта, средства (equity), маржа, кредитное плечо, валюта и другие свойства счёта. Используйте эту страницу, чтобы выбрать подходящий API для доступа к состоянию счёта.

## 📁 Что здесь находится

* **[account_summary](./account_summary.md)** - **вся информация о счёте** за один раз (баланс, средства (equity), кредитное плечо, кредит, время сервера и т. д.). **РЕКОМЕНДУЕТСЯ**
* **[account_info_double](./account_info_double.md)** - **одно значение типа double** со счёта (баланс, средства (equity), маржа, прибыль, кредит, уровень маржи и т. д.).
* **[account_info_integer](./account_info_integer.md)** - **одно целочисленное значение** со счёта (логин, кредитное плечо, режим торговли, лимит ордеров, разрешение на торговлю и т. д.).
* **[account_info_string](./account_info_string.md)** - **одно строковое значение** со счёта (имя, сервер, валюта, компания).

---

## 📚 Пошаговые руководства

Нужны подробные объяснения с построчным разбором кода? Посмотрите эти руководства:

* **[account_summary - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW.md)**
* **[account_info_double - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW.md)**
* **[account_info_integer - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW.md)**
* **[account_info_string - Как это работает](../HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW.md)**

---

## 🧭 Простыми словами

* **account_summary** - **универсальное решение** для полного снимка счёта (баланс, средства (equity), кредитное плечо, валюта и т. д.).
* **account_info_double** - получить **одно числовое свойство**, когда нужны только баланс или маржа.
* **account_info_integer** - получить **одно целочисленное свойство**, например номер логина или кредитное плечо.
* **account_info_string** - получить **одно текстовое свойство**, например имя счёта или валюту.

> Правило большого пальца: нужен **полный снимок** - `account_summary()`; нужно **одно конкретное значение** - `account_info_*` (double/integer/string).

---

## Быстрый выбор

| Если вам нужно                                       | Используйте               | Возвращает                 | Ключевые входы                      |
| ---------------------------------------------------- | ------------------------- | -------------------------- | ----------------------------------- |
| Полный снимок счёта (все значения)                   | `account_summary`         | AccountSummaryData         | *(нет)*                             |
| Одно числовое значение (баланс, средства (equity), маржа и т. д.) | `account_info_double`     | Одно значение `float`             | Enum свойства (BALANCE, EQUITY и т. д.) |
| Одно целочисленное значение (логин, кредитное плечо и т. д.) | `account_info_integer`    | Одно значение `int`               | Enum свойства (LOGIN, LEVERAGE и т. д.) |
| Одно текстовое значение (имя, валюта, сервер и т. д.) | `account_info_string`     | Одно значение `str`               | Enum свойства (NAME, CURRENCY и т. д.) |

---

## ℹ️ Перекрёстные ссылки и подводные камни

* **Уровень маржи** - используйте `account_info_double(ACCOUNT_MARGIN_LEVEL)`, чтобы получить значение в процентах.
* **Свободная маржа** - используйте `account_info_double(ACCOUNT_MARGIN_FREE)` для доступной маржи.
* **account_summary** включает базовую информацию (баланс, средства (equity), кредитное плечо); для маржи используйте `account_info_double`.
* Методы **account_info_*** легче, если вам нужно только одно свойство.
* **Валюта** влияет на то, как рассчитывается прибыль - всегда проверяйте валюту счёта.
* **Кредитное плечо** определяет требования к марже - выше кредитное плечо = меньше требуется маржи.
* **Дедлайн/таймаут** - не забудьте установить подходящий дедлайн для асинхронных вызовов.

---

## 🟢 Минимальные сниппеты

```python
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
from datetime import datetime, timedelta, timezone

# Получить полный снимок счёта
summary = await account.account_summary()

print(f"Balance: ${summary.account_balance:.2f}, "
      f"Equity: ${summary.account_equity:.2f}, "
      f"Leverage: 1:{summary.account_leverage}")
```

```python
# Получить одно свойство - баланс счёта
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

balance = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    deadline=deadline
)

print(f"Balance: ${balance:.2f}")
```

```python
# Получить кредитное плечо счёта
leverage = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE
)

print(f"Leverage: 1:{leverage}")
```

```python
# Получить валюту счёта
currency = await account.account_info_string(
    property_id=account_info_pb2.ACCOUNT_CURRENCY
)

print(f"Currency: {currency}")
```

```python
# Проверить состояние счёта
summary = await account.account_summary()

# Получить уровень маржи (account_summary не включает маржу, нужен отдельный вызов)
margin_level = await account.account_info_double(
    account_info_pb2.ACCOUNT_MARGIN_LEVEL
)

if margin_level < 100:
    print("[WARNING] Margin level critical!")
elif margin_level < 200:
    print("[WARNING] Low margin level")
else:
    print("[OK] Healthy margin level")
```

```python
# Проверить счёт перед торговлей
summary = await account.account_summary()

# Проверить, разрешена ли торговля
trade_allowed = await account.account_info_integer(
    account_info_pb2.ACCOUNT_TRADE_ALLOWED
)

if not trade_allowed:
    raise RuntimeError("Trading is disabled on this account")

# Проверить минимальный баланс
if summary.account_balance < 100:
    raise ValueError(f"Balance too low: ${summary.account_balance:.2f}")

print(f"[OK] Account ready to trade")
print(f"   Balance: ${summary.account_balance:.2f} {summary.account_currency}")
print(f"   Leverage: 1:{summary.account_leverage}")
```

```python
# Мониторинг средств (equity) счёта в реальном времени
async def monitor_equity(interval: float = 5.0):
    """Monitor equity every N seconds"""
    while True:
        summary = await account.account_summary()

        floating_pnl = summary.account_equity - summary.account_balance

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Equity: ${summary.account_equity:,.2f} | "
              f"Floating P/L: ${floating_pnl:+,.2f}")

        await asyncio.sleep(interval)

# await monitor_equity(interval=5.0)
```

```python
# Получить все детали счёта для логирования
async def log_account_details():
    """Log comprehensive account information"""
    summary = await account.account_summary()

    # Получить дополнительную информацию о марже
    margin_level = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_LEVEL
    )

    free_margin = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    mode_names = {0: "DEMO", 1: "CONTEST", 2: "REAL"}
    mode = mode_names.get(summary.account_trade_mode, "UNKNOWN")

    print(f"{'='*60}")
    print(f"ACCOUNT DETAILS")
    print(f"{'='*60}")
    print(f"Login:          #{summary.account_login}")
    print(f"Name:           {summary.account_user_name}")
    print(f"Broker:         {summary.account_company_name}")
    print(f"Mode:           {mode}")
    print(f"Currency:       {summary.account_currency}")
    print(f"Leverage:       1:{summary.account_leverage}")
    print(f"")
    print(f"Balance:        ${summary.account_balance:,.2f}")
    print(f"Equity:         ${summary.account_equity:,.2f}")
    print(f"Credit:         ${summary.account_credit:,.2f}")
    print(f"Free Margin:    ${free_margin:,.2f}")
    print(f"Margin Level:   {margin_level:.2f}%")
    print(f"{'='*60}")

# await log_account_details()
```

---

## 📚 См. также

* **Информация о символах:** [Symbol_Information.Overview](../2. Symbol_Information/Symbol_Information.Overview.md) - получить данные символа/рынка
* **Позиции и ордера:** [Positions_Orders.Overview](../3. Positions_Orders/Positions_Orders.Overview.md) - управление позициями и ордерами
* **Торговля:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - размещение и управление сделками
