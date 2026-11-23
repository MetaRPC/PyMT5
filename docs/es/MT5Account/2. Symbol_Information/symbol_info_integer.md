# Obtener una propiedad integer de un símbolo

> **Solicitud:** obtener el valor de una propiedad de tipo entero de un símbolo.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_integer(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoInteger` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoInteger(SymbolInfoIntegerRequest) -> SymbolInfoIntegerReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoInteger(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es:** permite obtener el valor de una única propiedad de tipo entero de un símbolo (DIGITS, SPREAD, TRADE_MODE, etc.).
- **Por qué lo necesitas:** permite obtener propiedades enteras específicas de un símbolo sin tener que recuperar todos sus datos.
- **Cuándo utilizarlo:** utiliza `symbol_params_many()` para consultar varias propiedades. Utiliza este método cuando necesites consultar una sola propiedad.

---

## 🎯 Propósito

Utiliza este método para consultar propiedades enteras específicas de un símbolo:

- Obtener el número de dígitos decimales del símbolo.
- Comprobar el spread actual en puntos.
- Consultar los modos de trading y de ejecución.
- Obtener marcas de tiempo (hora de inicio y vencimiento).
- Comprobar los parámetros de volumen.
- Obtener los niveles de stops y freeze de trading.
- Consultar la configuración de renovación del swap.
- Supervisar los modos de órdenes y de ejecución.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [symbol_info_integer - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_integer_HOW.md)**

---

## Firma del método

```python
async def symbol_info_integer(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoIntegerProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoIntegerData
```

**Mensaje de solicitud:**

```protobuf
message SymbolInfoIntegerRequest {
  string symbol = 1;
  SymbolInfoIntegerProperty type = 2;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolInfoIntegerReply {
  oneof response {
    SymbolInfoIntegerData data = 1;
    Error error = 2;
  }
}

message SymbolInfoIntegerData {
  int64 value = 1;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo. |
| `property` | `SymbolInfoIntegerProperty` (enum) | Propiedad que se desea obtener (DIGITS, SPREAD, etc.). |
| `deadline` | `datetime` (opcional) | Fecha y hora límite de la llamada gRPC. Debe ser una fecha y hora UTC. |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento que permite cancelar la operación. |

**Gestión de `deadline`:**

Si necesitas establecer un límite de tiempo, utiliza un objeto `datetime` con zona horaria UTC explícita:

```python
from datetime import datetime, timedelta, timezone

deadline = datetime.now(timezone.utc) + timedelta(seconds=10)
```

No utilices `datetime.now()` sin zona horaria, ya que genera un objeto `datetime` sin información de zona horaria.

Si no necesitas establecer un límite de tiempo explícito, puedes omitir `deadline` y utilizar su valor predeterminado `None`.

---

## ⬆️ Parámetros de salida

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `value` | `int64` | `int` | Valor entero de la propiedad. |

**Valor de retorno:** el método devuelve un objeto `SymbolInfoIntegerData` cuyo campo `value` contiene la propiedad solicitada.

---

## 🧱 Enums relacionados (de Proto)

> **Nota:** en el código Python, utiliza la ruta completa del enum del módulo `market_info`.

### `SymbolInfoIntegerProperty`

Definido en `mt5-term-api-market-info.proto`.

### Estado y visualización del símbolo

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_EXIST` | 6 | Indicador de existencia del símbolo. |
| `SYMBOL_SELECT` | 7 | Símbolo seleccionado en MarketWatch. |
| `SYMBOL_VISIBLE` | 8 | Símbolo visible en MarketWatch. |
| `SYMBOL_SUBSCRIPTION_DELAY` | 0 | Retraso de la suscripción. |
| `SYMBOL_CUSTOM` | 3 | Indicador de símbolo personalizado. |
| `SYMBOL_BACKGROUND_COLOR` | 4 | Color de fondo. |
| `SYMBOL_CHART_MODE` | 5 | Modo del gráfico. |

### Clasificación

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_SECTOR` | 1 | Sector. |
| `SYMBOL_INDUSTRY` | 2 | Industria. |

### Tiempo y precisión

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_TIME` | 15 | Hora de la última cotización. |
| `SYMBOL_TIME_MSC` | 16 | Hora de la última cotización en milisegundos. |
| `SYMBOL_DIGITS` | 17 | Número de dígitos después del separador decimal. |
| `SYMBOL_START_TIME` | 23 | Hora de inicio del símbolo. |
| `SYMBOL_EXPIRATION_TIME` | 24 | Hora de vencimiento del símbolo. |

### Spread y volumen

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_SPREAD` | 19 | Valor del spread en puntos. |
| `SYMBOL_SPREAD_FLOAT` | 18 | Indicador de spread flotante. |
| `SYMBOL_VOLUME` | 12 | Volumen de la última operación. |
| `SYMBOL_VOLUMEHIGH` | 13 | Volumen máximo del día. |
| `SYMBOL_VOLUMELOW` | 14 | Volumen mínimo del día. |
| `SYMBOL_TICKS_BOOKDEPTH` | 20 | Número máximo de órdenes mostradas en el libro de profundidad (DOM). |

### Datos de sesión

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_SESSION_DEALS` | 9 | Número de operaciones de la sesión actual. |
| `SYMBOL_SESSION_BUY_ORDERS` | 10 | Número de órdenes de compra. |
| `SYMBOL_SESSION_SELL_ORDERS` | 11 | Número de órdenes de venta. |

### Propiedades de trading

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_TRADE_CALC_MODE` | 21 | Modo de cálculo del precio del contrato. |
| `SYMBOL_TRADE_MODE` | 22 | Modo de negociación permitido para el símbolo. |
| `SYMBOL_TRADE_STOPS_LEVEL` | 25 | Distancia mínima de los stops. |
| `SYMBOL_TRADE_FREEZE_LEVEL` | 26 | Distancia al precio actual dentro de la cual las operaciones o modificaciones quedan restringidas. |
| `SYMBOL_TRADE_EXEMODE` | 27 | Modo de ejecución de operaciones. |

### Modos de órdenes y vencimiento

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_EXPIRATION_MODE` | 31 | Indicadores de los modos de vencimiento permitidos. |
| `SYMBOL_FILLING_MODE` | 32 | Indicadores de los modos de ejecución permitidos. |
| `SYMBOL_ORDER_MODE` | 33 | Indicadores de los tipos de órdenes permitidos. |
| `SYMBOL_ORDER_GTC_MODE` | 34 | Modo de vencimiento GTC de las órdenes pendientes. |

### Swap y margen

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_SWAP_MODE` | 28 | Modelo de cálculo del swap. |
| `SYMBOL_SWAP_ROLLOVER3DAYS` | 29 | Día de la semana en el que se cobra el swap de tres días. |
| `SYMBOL_MARGIN_HEDGED_USE_LEG` | 30 | Cálculo del margen de posiciones cubiertas utilizando la posición de mayor tamaño. |

### Opciones

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_OPTION_MODE` | 35 | Tipo de opción. |
| `SYMBOL_OPTION_RIGHT` | 36 | Derecho de la opción (Call/Put). |

**Uso en Python:**

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener el número de dígitos del símbolo
digits_data = await account.symbol_info_integer("EURUSD", market_info_pb2.SYMBOL_DIGITS)
print(f"Dígitos: {digits_data.value}")

# Comprobar el spread
spread_data = await account.symbol_info_integer("EURUSD", market_info_pb2.SYMBOL_SPREAD)
print(f"Spread: {spread_data.value} puntos")
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios con reconexión automática mediante `execute_with_reconnect`.
- **Timeout predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Acceso al valor:** el objeto `SymbolInfoIntegerData` devuelto contiene un campo `.value` con el valor entero.
- **Modos de trading:** las propiedades de modo devuelven indicadores enteros. Consulta la documentación de MT5 para conocer el significado de cada indicador.
- **Marcas de tiempo:** las propiedades TIME y TIME_MSC devuelven marcas de tiempo Unix (en segundos o milisegundos).
- **Unidades del spread:** `SYMBOL_SPREAD` devuelve el spread en puntos, no en pips.
- **Indicadores booleanos:** propiedades como `SYMBOL_EXIST`, `SYMBOL_SELECT` y `SYMBOL_VISIBLE` devuelven `0` o `1`.

---

## 🔗 Ejemplos de uso

### 1) Obtener los dígitos del símbolo y el spread

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener los dígitos (posiciones decimales)
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_DIGITS
)

print(f"Dígitos: {result.value}")  # Salida: Dígitos: 5

# Obtener el spread en puntos
spread_result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_SPREAD
)

print(f"Spread: {spread_result.value} puntos")  # Salida: Spread: 10 puntos
```

### 2) Comprobar si el símbolo está seleccionado en MarketWatch

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="GBPUSD",
    property=market_info_pb2.SYMBOL_SELECT
)

if result.value:
    print("El símbolo está en MarketWatch")
else:
    print("El símbolo NO está en MarketWatch")
```

### 3) Obtener el modo de trading

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="XAUUSD",
    property=market_info_pb2.SYMBOL_TRADE_MODE
)

# Convertir los valores a nombres de modos de trading
trade_modes = {
    0: "DISABLED",
    1: "LONG_ONLY",
    2: "SHORT_ONLY",
    3: "CLOSE_ONLY",
    4: "FULL"
}

mode_name = trade_modes.get(result.value, "UNKNOWN")
print(f"Modo de trading: {mode_name} (valor: {result.value})")
```

### 4) Obtener la marca de tiempo de la última cotización

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timezone

# Obtener la marca de tiempo en segundos
result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TIME
)

# Convertir a datetime
quote_time = datetime.fromtimestamp(result.value, tz=timezone.utc)
print(f"Hora de la última cotización: {quote_time}")

# Obtener la marca de tiempo en milisegundos
result_msc = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TIME_MSC
)

quote_time_msc = datetime.fromtimestamp(result_msc.value / 1000, tz=timezone.utc)
print(f"Hora de la última cotización (precisión de ms): {quote_time_msc}")
```

### 5) Comprobar el nivel de stops antes de enviar una orden

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TRADE_STOPS_LEVEL
)

stops_level = result.value

print(f"Nivel mínimo de stops: {stops_level} puntos")
print(f"SL/TP debe estar al menos a {stops_level} puntos del precio actual")
```

### 6) Obtener el nivel de freeze

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_TRADE_FREEZE_LEVEL
)

freeze_level = result.value

if freeze_level > 0:
    print(f"Nivel de freeze: {freeze_level} puntos")
    print(f"Las órdenes no se pueden modificar cuando el precio está a menos de {freeze_level} puntos")
else:
    print("No hay ningún nivel de freeze configurado")
```

### 7) Comprobar los tipos de órdenes permitidos

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

result = await account.symbol_info_integer(
    symbol="BTCUSD",
    property=market_info_pb2.SYMBOL_ORDER_MODE
)

# ORDER_MODE es un campo de bits
order_flags = result.value

# Comprobar tipos específicos de órdenes (valores de ejemplo de los indicadores)
if order_flags & 1:
    print("Órdenes de mercado permitidas")
if order_flags & 2:
    print("Órdenes Limit permitidas")
if order_flags & 4:
    print("Órdenes Stop permitidas")
if order_flags & 8:
    print("Órdenes Stop Limit permitidas")
```

---

## 📚 Véase también

- [symbol_info_double](./symbol_info_double.md) - Obtener propiedades de tipo double.
- [symbol_info_string](./symbol_info_string.md) - Obtener propiedades de tipo string.
- [symbol_params_many](./symbol_params_many.md) - Obtener todos los parámetros de un símbolo de una sola vez.