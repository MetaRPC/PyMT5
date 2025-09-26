# Low-Level Walkthrough — Step number one
**Covers:** Steps **1–8** (connect, account summary/info, symbols basics & params, opened orders, positions, order history).  
**Audience:** Beginners who want to understand raw MT5 gRPC calls without wrappers.

> This part focuses on *read-only* and safe operations. No trading actions here.

---

## Helpers used in this part
Эти хелперы используются в шагах ниже (пути относительно этой страницы `docs/Examples/Base_example/Step_number_one.md`).

- **Env и диагностика подключения** — см.:  
  - [`env.md`](../Common/env.md)  
  - [`diag_connect.md`](../Common/diag_connect.md)
- **Знакомство с базовым API** — см.:  
  - [`Getting_Started.md`](../../MT5Account/Getting_Started.md)  
  - [`BASE.md`](../../MT5Account/BASE.md)  
  - [`Under_the_Hood.md`](../../MT5Account/Under_the_Hood.md)

---

## Prerequisites
- Python **3.13.x** (виртуальное окружение).
- Доступный gRPC‑endpoint.
- Валидные MT5 креды.

### Environment variables used here
| Name | Default | Purpose |
|---|---:|---|
| `GRPC_SERVER` | `mt5.mrpc.pro:443` | gRPC backend endpoint |
| `MT5_LOGIN` | `0` | MT5 login |
| `MT5_PASSWORD` | `""` | MT5 password |
| `MT5_SERVER` | `""` | MT5 server name (for ConnectEx) |
| `MT5_SYMBOL` | `EURUSD` | Base symbol for examples |
| `TIMEOUT_SECONDS` | `90` | Deadline for most RPC calls |

> No trading flags required in this part (`RUN_TRADING` not used).

---

## How to run this part
PowerShell (Windows):
```powershell
$env:MT5_LOGIN=1234567
$env:MT5_PASSWORD='pass'
$env:MT5_SERVER='MetaQuotes-Demo'
$env:GRPC_SERVER='mt5.mrpc.pro:443'
python - <<'PY'
import asyncio
# Ensure the shim is applied before any pb2 usage
from examples.common.pb2_shim import apply_patch 
apply_patch()

from examples.base_example.lowlevel_walkthrough import main  # entrypoint
asyncio.run(main(only_steps=range(1,9)))  # run steps 1..8
PY
```

Bash:
```bash
export MT5_LOGIN=1234567
export MT5_PASSWORD='pass'
export MT5_SERVER="MetaQuotes-Demo"
export GRPC_SERVER="mt5.mrpc.pro:443"
python - <<'PY'
import asyncio
from examples.common.pb2_shim import apply_patch  # comments in English only
apply_patch()

from examples.base_example.lowlevel_walkthrough import main
asyncio.run(main(only_steps=range(1,9)))  # 1..8
PY
```

---

# |||| Step 1: one-shot account_summary 🔌📊 ||||
**Цель:** Подключиться по `server_name` (ConnectEx) и вывести ключевые метрики счёта: equity, balance, margin, free, free_ratio, drawdown, server_time.  
**Docs:** [`account_summary.md`](../../MT5Account/Account_Information/account_summary.md), [`Getting_Started.md`](../../MT5Account/Getting_Started.md)

**Method signatures (pb):**
```python
ConnectEx(request: ConnectExRequest) -> ConnectExReply
AccountSummary(request: AccountSummaryRequest) -> AccountSummaryReply
```
**Грабли:** корректность `MT5_SERVER`; при высокой задержке увеличьте `TIMEOUT_SECONDS`.

---

# |||| Step 2: account_info_* (pb2) 🧾 ||||
**Цель:** Показать прямые pb2-вызовы `AccountInfo*` и безопасное извлечение полей.  
**Docs:** [`account_info_double.md`](../../MT5Account/Account_Information/account_info_double.md),  
[`account_info_integer.md`](../../MT5Account/Account_Information/account_info_integer.md),  
[`account_info_string.md`](../../MT5Account/Account_Information/account_info_string.md),  
[`Account_Information_Overview.md`](../../MT5Account/Account_Information/Account_Information_Overview.md)

**Method signatures (pb):**
```python
AccountInfoDouble(request: AccountInfoDoubleRequest) -> AccountInfoDoubleReply
AccountInfoInteger(request: AccountInfoIntegerRequest) -> AccountInfoIntegerReply
AccountInfoString(request: AccountInfoStringRequest) -> AccountInfoStringReply
```
**Грабли:** поля могут отсутствовать в зависимости от сервера → используйте safe-getters.

---

# |||| Step 3: symbol_* basics 🏷️ ||||
**Цель:** Убедиться, что символ доступен, и прочитать ключевые атрибуты.  
**Docs:** [`symbol_exist.md`](../../MT5Account/Symbols_and_Market/symbol_exist.md),  
[`symbol_select.md`](../../MT5Account/Symbols_and_Market/symbol_select.md),  
[`symbols_total.md`](../../MT5Account/Symbols_and_Market/symbols_total.md),  
[`symbol_info_double.md`](../../MT5Account/Symbols_and_Market/symbol_info_double.md),  
[`symbol_info_integer.md`](../../MT5Account/Symbols_and_Market/symbol_info_integer.md),  
[`symbol_info_string.md`](../../MT5Account/Symbols_and_Market/symbol_info_string.md),  
[`symbol_info_tick.md`](../../MT5Account/Symbols_and_Market/symbol_info_tick.md),  
[`tick_value_with_size.md`](../../MT5Account/Symbols_and_Market/tick_value_with_size.md),  
[`symbol_is_synchronized.md`](../../MT5Account/Symbols_and_Market/symbol_is_synchronized.md)  
**Extras:** [`symbol_info_session_quote.md`](../../MT5Account/Symbols_and_Market/symbol_info_session_quote.md), [`symbol_info_session_trade.md`](../../MT5Account/Symbols_and_Market/symbol_info_session_trade.md), [`symbol_info_margin_rate.md`](../../MT5Account/Symbols_and_Market/symbol_info_margin_rate.md), [`symbol_name.md`](../../MT5Account/Symbols_and_Market/symbol_name.md)

**Method signatures (pb):**
```python
SymbolsTotal(request: SymbolsTotalRequest) -> SymbolsTotalReply
SymbolExist(request: SymbolExistRequest) -> SymbolExistReply
SymbolName(request: SymbolNameRequest) -> SymbolNameReply
SymbolSelect(request: SymbolSelectRequest) -> SymbolSelectReply
SymbolIsSynchronized(request: SymbolIsSynchronizedRequest) -> SymbolIsSynchronizedReply
SymbolInfoDouble(request: SymbolInfoDoubleRequest) -> SymbolInfoDoubleReply
SymbolInfoInteger(request: SymbolInfoIntegerRequest) -> SymbolInfoIntegerReply
SymbolInfoString(request: SymbolInfoStringRequest) -> SymbolInfoStringReply
SymbolInfoTick(request: SymbolInfoTickRequest) -> SymbolInfoTickRequestReply
TickValueWithSize(request: TickValueWithSizeRequest) -> TickValueWithSizeReply
```
**Грабли:** перед `symbol_info_*` обязательно `symbol_select(SYMBOL, True)` — иначе поля пустые.

---

# |||| Step 4: symbol_params_many (batch) ⚙️ ||||
**Цель:** Считать набор параметров для одного/нескольких символов: спред, tick size/value, шаг/лимиты лота и т.д.  
**Docs:** [`symbol_params_many.md`](../../MT5Account/Symbols_and_Market/symbol_params_many.md)

**Method signatures (pb):**
```python
SymbolParamsMany(request: SymbolParamsManyRequest) -> SymbolParamsManyReply
```
**Грабли:** учитывайте `lot_step`, `min_volume`, `max_volume` при планировании торговых операций.

---

# |||| Step 5: opened_orders (snapshot) 🗂️ ||||
**Цель:** Вывести активные отложенные ордера компактными строками.  
**Docs:** [`opened_orders.md`](../../MT5Account/Orders_Positions_History/opened_orders.md)

**Method signatures (pb):**
```python
OpenedOrders(request: OpenedOrdersRequest) -> OpenedOrdersReply
```
**Грабли:** нормализуйте время (UTC), корректно обрабатывайте пустые списки.

---

# |||| Step 6: opened_orders_tickets 🎟️ ||||
**Цель:** Получить только тикеты активных отложенных ордеров (пригодится для точечных операций).  
**Docs:** [`opened_orders_tickets.md`](../../MT5Account/Orders_Positions_History/opened_orders_tickets.md)

**Method signatures (pb):**
```python
OpenedOrdersTickets(request: OpenedOrdersTicketsRequest) -> OpenedOrdersTicketsReply
```

---

# |||| Step 7: positions_total 📊 ||||
**Цель:** Показать количество открытых позиций (с фоллбеком на прямой вызов стаба при необходимости).  
**Docs:** [`positions_total.md`](../../MT5Account/Orders_Positions_History/positions_total.md)

**Method signatures (pb):**
```python
PositionsTotal(request: Empty) -> PositionsTotalReply
```

---

# |||| Step 8: order_history (last 7d) 🕰️ ||||
**Цель:** Получить историю ордеров за окно времени, используя pb2 `Timestamp` (UTC).  
**Docs:** [`order_history.md`](../../MT5Account/Orders_Positions_History/order_history.md), [`OrdersPositionsHistory_Overview.md`](../../MT5Account/Orders_Positions_History/OrdersPositionsHistory_Overview.md)

**Method signatures (pb):**
```python
OrderHistory(request: OrderHistoryRequest) -> OrderHistoryReply
```

---

## Gotchas (quick)
- `MT5_SERVER` должен точно соответствовать строке сервера брокера.
- Если `symbol_info_*` пусто — вызовите `symbol_select(SYMBOL, True)`.
- Нормализуйте время к UTC для history-эндпоинтов.
- Увеличьте `TIMEOUT_SECONDS`, если наблюдается высокая задержка.

---

## Next
Continue with **Step_number_(two).md** для DOM и pre-trade checks (Steps 9–12).
