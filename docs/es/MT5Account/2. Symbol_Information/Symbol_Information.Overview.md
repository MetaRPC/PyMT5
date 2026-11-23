# MT5Account - Información del símbolo - Descripción general

> Precios, propiedades, parámetros y condiciones de trading de los símbolos. Consulta propiedades individuales u obtén todos los datos del símbolo.

## 📁 Contenido de esta sección

- **symbols_total** - **recuento** de los símbolos disponibles.
- **symbol_exist** - **comprobar si un símbolo existe** en la plataforma.
- **symbol_name** - **obtener el nombre del símbolo** según su posición en el índice.
- **symbol_select** - **añadir o eliminar un símbolo** de Market Watch.
- **symbol_is_synchronized** - **comprobar si los datos del símbolo** están sincronizados.
- **symbol_info_double** - **una propiedad double** (BID, ASK, POINT, etc.).
- **symbol_info_integer** - **una propiedad integer** (DIGITS, SPREAD, etc.).
- **symbol_info_string** - **una propiedad string** (DESCRIPTION, CURRENCY_BASE, etc.).
- **symbol_info_tick** - **datos del tick actual** (BID, ASK, volumen y hora).
- **symbol_info_margin_rate** - **tasas de margen** para el símbolo y el tipo de orden.
- **symbol_info_session_quote** - **horarios de las sesiones de cotización** para cada día de la semana.
- **symbol_info_session_trade** - **horarios de las sesiones de trading** para cada día de la semana.
- **symbol_params_many** - **todos los parámetros del símbolo a la vez** (RECOMENDADO para consultar varias propiedades).

---

## 📚 Tutoriales paso a paso

¿Quieres explicaciones detalladas con un análisis del código línea por línea? Consulta estas guías:

- **[symbols_total - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbols_total_HOW\.md)**
- **[symbol_exist - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_exist_HOW\.md)**
- **[symbol_name - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_name_HOW\.md)**
- **[symbol_select - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_select_HOW\.md)**
- **[symbol_is_synchronized - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_is_synchronized_HOW\.md)**
- **[symbol_info_double - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW\.md)**
- **[symbol_info_integer - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW\.md)**
- **[symbol_info_string - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_string_HOW\.md)**
- **[symbol_info_tick - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_tick_HOW\.md)**
- **[symbol_info_margin_rate - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW\.md)**
- **[symbol_info_session_quote - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_quote_HOW\.md)**
- **[symbol_info_session_trade - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_session_trade_HOW\.md)**
- **[symbol_params_many - Cómo funciona]\(../HOW_IT_WORK/2. Symbol_information_HOW/symbol_params_many_HOW\.md)**

---

## 🧭 En lenguaje sencillo

- **symbols_total** - indica cuántos símbolos están disponibles (todos o solo los de Market Watch).
- **symbol_exist** - comprueba si el nombre de un símbolo es válido.
- **symbol_name** - obtiene el nombre del símbolo según su número de posición.
- **symbol_select** - muestra u oculta un símbolo en Market Watch.
- **symbol_is_synchronized** - verifica si los datos del símbolo están actualizados.
- **symbol_info_double** - obtiene un valor numérico (precio, spread, etc.).
- **symbol_info_integer** - obtiene un valor entero (dígitos, puntos de spread, etc.).
- **symbol_info_string** - obtiene un valor de texto (descripción, divisa, etc.).
- **symbol_info_tick** - obtiene una instantánea del precio actual.
- **symbol_info_margin_rate** - obtiene los requisitos de margen.
- **symbol_info_session_quote/trade** - obtiene los horarios de trading.
- **symbol_params_many** - obtiene TODAS las propiedades en una sola llamada (la opción más eficiente).

> Regla general: si necesitas **todas las propiedades**, utiliza `symbol_params_many()` (RECOMENDADO); si necesitas **una sola propiedad**, utiliza `symbol_info_*`; si necesitas el **precio actual**, utiliza `symbol_info_tick()`.

---

## Quick choose

| Si necesitas                                   | Utiliza                     | Devuelve                    | Parámetros principales             |
| ---------------------------------------------- | --------------------------- | --------------------------- | ---------------------------------- |
| Número de símbolos                             | `symbols_total`             | SymbolsTotalData (recuento) | `selected_only`               |
| Comprobar si existe un símbolo                 | `symbol_exist`              | SymbolExistData (bool)      | `symbol`                 |
| Nombre del símbolo por posición                | `symbol_name`               | SymbolNameData (string)     | `index`, `selected`                    |
| Añadir o eliminar de Market Watch              | `symbol_select`             | SymbolSelectData (bool)     | `symbol`, `select`                     |
| Comprobar si los datos están sincronizados     | `symbol_is_synchronized`    | SymbolIsSynchronizedData    | `symbol`                 |
| Un único valor double                          | `symbol_info_double`        | SymbolInfoDoubleData        | `symbol`, `property`          |
| Un único valor integer                         | `symbol_info_integer`       | SymbolInfoIntegerData       | `symbol`, `property`          |
| Un único valor string                          | `symbol_info_string`        | SymbolInfoStringData        | `symbol`, `property`          |
| Tick actual (BID/ASK/volumen)                  | `symbol_info_tick`          | MrpcMqlTick                 | `symbol`                 |
| Tasas de margen                                | `symbol_info_margin_rate`   | SymbolInfoMarginRateData    | `symbol`, `order_type`                 |
| Horarios de las sesiones de cotización         | `symbol_info_session_quote` | SymbolInfoSessionQuoteData  | `symbol`, `day_of_week`, `session_index`         |
| Horarios de las sesiones de trading            | `symbol_info_session_trade` | SymbolInfoSessionTradeData  | `symbol`, `day_of_week`, `session_index`         |
| TODOS los parámetros del símbolo (RECOMENDADO) | `symbol_params_many`        | SymbolParamsManyData        | `request` |

---

## ℹ️ Referencias cruzadas y aspectos importantes

- **symbol_params_many** - RECOMENDADO para obtener varias propiedades (una sola llamada en lugar de muchas).
- **symbol_params_many · `request`** - el parámetro `request` es un `SymbolParamsManyRequest` con los campos: `symbol_name`, `sort_type`, `page_number`, `items_per_page`.
- **BID vs ASK** - BID es el mejor precio comprador del mercado (el precio al que puedes vender); ASK es el mejor precio vendedor (el precio al que puedes comprar). Spread = ASK - BID.
- **DIGITS** - número de posiciones decimales del símbolo (por ejemplo, 5 para EURUSD = 1.12345).
- **SPREAD** - spread actual expresado en puntos, no en pips (para 5 dígitos: 1 pip = 10 puntos).
- **Market Watch** - los símbolos deben estar en Market Watch para obtener sus precios.
- **Sincronización** - comprueba `symbol_is_synchronized()` antes de operar.
- **Horarios de las sesiones** - se devuelven en segundos desde la medianoche (convierte el valor a horas:minutos).
- **Datos del tick** - utiliza `symbol_info_tick()` para obtener una instantánea del precio en tiempo real.

---

## 🟢 Fragmentos mínimos de código

```
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Obtener todos los parámetros del símbolo (RECOMENDADO)
request = account_helper_pb2.SymbolParamsManyRequest(symbol_name="EURUSD")
data = await account.symbol_params_many(request=request)
if data.symbol_infos:
    info = data.symbol_infos[0]
    print(f"BID: {info.bid}, ASK: {info.ask}")
    print(f"Spread: {info.spread}, Digits: {info.digits}")
    print(f"Tamaño del contrato: {info.trade_contract_size}")
```

```
# Obtener el tick actual
tick = await account.symbol_info_tick(symbol="EURUSD")
print(f"BID: {tick.bid}, ASK: {tick.ask}")
print(f"Spread: {tick.ask - tick.bid}")
```

```
# Obtener propiedades específicas
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

bid_data = await account.symbol_info_double(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_BID
)

digits_data = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)

print(f"BID: {bid_data.value:.{digits_data.value}f}")
```

```
# Comprobar si existe un símbolo
data = await account.symbol_exist(symbol="EURUSD")
if data.exists:
    print(f"[OK] EURUSD existe ({'personalizado' if data.is_custom else 'estándar'})")
```

```
# Obtener todos los símbolos de Market Watch
count_data = await account.symbols_total(selected_only=True)

symbols = []

for i in range(count_data.total):
    name_data = await account.symbol_name(index=i, selected=True)
    symbols.append(name_data.name)

print(f"Símbolos de Market Watch: {symbols}")
```

```
# Añadir un símbolo a Market Watch
result = await account.symbol_select(symbol="EURUSD", select=True)
if result.success:
    print("[OK] Símbolo añadido a Market Watch")
```

```
# Calcular el spread en pips
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

tick = await account.symbol_info_tick(symbol="EURUSD")
digits_data = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)

digits = digits_data.value
spread_points = (tick.ask - tick.bid) * (10 ** digits)
spread_pips = spread_points / 10 if digits == 5 else spread_points

print(f"Spread: {spread_pips:.1f} pips")
```

```
# Obtener todos los símbolos con sus parámetros
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

request = account_helper_pb2.SymbolParamsManyRequest(items_per_page=100)
data = await account.symbol_params_many(request=request)

print(f"Total de símbolos: {data.symbols_total}")
for info in data.symbol_infos:
    print(f"{info.name}: BID={info.bid}, ASK={info.ask}, Spread={info.spread}")
```

```
# Obtener las tasas de margen
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Tasa de margen inicial: {rates.initial_margin_rate}")
print(f"Tasa de margen de mantenimiento: {rates.maintenance_margin_rate}")
```

```
# Comprobar los horarios de trading
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

session = await account.symbol_info_session_trade(
    symbol="EURUSD",
    day_of_week=market_info_pb2.MONDAY,
    session_index=0
)

from_hours = getattr(session, 'from').seconds // 3600
from_mins = (getattr(session, 'from').seconds % 3600) // 60
to_hours = session.to.seconds // 3600
to_mins = (session.to.seconds % 3600) // 60

print(f"Trading del lunes: {from_hours:02d}:{from_mins:02d} - {to_hours:02d}:{to_mins:02d}")
```

---

## 📚 Véase también

- **Información de la cuenta:** [Account_Information.Overview]\(../1. Account_Information/Account_Information.Overview\.md) - obtener el saldo, el equity y el apalancamiento de la cuenta.
- **Posiciones y órdenes:** [Positions_Orders.Overview]\(../3. Positions_Orders/Positions_Orders.Overview\.md) - gestionar posiciones abiertas y órdenes.
- **Operaciones de trading:** [Trading_Operations.Overview]\(../5. Trading_Operations/Trading_Operations.Overview\.md) - enviar y gestionar operaciones.

Corrige la definición de BID y ASKUnifica los nombres de los parámetros