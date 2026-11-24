# Obtener una propiedad double de un símbolo

> **Solicitud:** obtener el valor de una propiedad de tipo `double` de un símbolo.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_double(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoDouble` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoDouble(SymbolInfoDoubleRequest) -> SymbolInfoDoubleReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoDouble(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es:** permite obtener el valor de una única propiedad de tipo `double` de un símbolo (BID, ASK, VOLUME, etc.).
- **Por qué lo necesitas:** permite obtener propiedades numéricas específicas de un símbolo sin tener que recuperar todos sus datos.
- **Cuándo utilizarlo:** utiliza `symbol_params_many()` para consultar varias propiedades. Utiliza este método cuando necesites consultar una sola propiedad.

---

## 🎯 Propósito

Utiliza este método para consultar propiedades específicas de tipo `double` de un símbolo:

- Obtener los precios actuales BID/ASK.
- Comprobar los volúmenes de trading.
- Obtener los requisitos de margen.
- Consultar los valores de swap.
- Consultar los valores de tick y los tamaños de contrato.
- Supervisar los precios y límites de la sesión.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [symbol_info_double - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_double_HOW.md)**

---

## Firma del método

```python
async def symbol_info_double(
    self,
    symbol: str,
    property: market_info_pb2.SymbolInfoDoubleProperty,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
)
```

**Mensaje de solicitud:**

```protobuf
message SymbolInfoDoubleRequest {
  string symbol = 1;
  SymbolInfoDoubleProperty type = 2;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolInfoDoubleReply {
  oneof response {
    SymbolInfoDoubleData data = 1;
    Error error = 2;
  }
}

message SymbolInfoDoubleData {
  double value = 1;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo. |
| `property` | `SymbolInfoDoubleProperty` (enum) | Propiedad que se desea obtener (BID, ASK, etc.). |
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

## ⬆️ Parámetros de salida - `SymbolInfoDoubleData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `value` | `double` | `float` | Valor de la propiedad solicitada. |

**Valor de retorno:** el método devuelve un objeto `SymbolInfoDoubleData`. Se puede acceder al valor numérico mediante el atributo `.value`.

---

## 🧱 Enums relacionados (de Proto)

> **Nota:** en el código Python, utiliza la ruta completa del enum del módulo `market_info`.

### `SymbolInfoDoubleProperty`

Definido en `mt5-term-api-market-info.proto`.

### Propiedades de precios

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_BID` | 0 | Precio Bid actual. |
| `SYMBOL_BIDHIGH` | 1 | Precio Bid máximo del día. |
| `SYMBOL_BIDLOW` | 2 | Precio Bid mínimo del día. |
| `SYMBOL_ASK` | 3 | Precio Ask actual. |
| `SYMBOL_ASKHIGH` | 4 | Precio Ask máximo del día. |
| `SYMBOL_ASKLOW` | 5 | Precio Ask mínimo del día. |
| `SYMBOL_LAST` | 6 | Precio de la última operación. |
| `SYMBOL_LASTHIGH` | 7 | Precio Last máximo del día. |
| `SYMBOL_LASTLOW` | 8 | Precio Last mínimo del día. |

### Propiedades de volumen

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_VOLUME_REAL` | 9 | Volumen real del día. |
| `SYMBOL_VOLUMEHIGH_REAL` | 10 | Volumen real máximo del día. |
| `SYMBOL_VOLUMELOW_REAL` | 11 | Volumen real mínimo del día. |
| `SYMBOL_VOLUME_MIN` | 22 | Volumen mínimo de una operación. |
| `SYMBOL_VOLUME_MAX` | 23 | Volumen máximo de una operación. |
| `SYMBOL_VOLUME_STEP` | 24 | Incremento mínimo del volumen. |
| `SYMBOL_VOLUME_LIMIT` | 25 | Volumen agregado máximo permitido. |

### Propiedades de trading

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_POINT` | 13 | Valor del punto del símbolo. |
| `SYMBOL_TRADE_TICK_VALUE` | 14 | Valor calculado del tick para una posición. |
| `SYMBOL_TRADE_TICK_VALUE_PROFIT` | 15 | Valor calculado del tick para las ganancias. |
| `SYMBOL_TRADE_TICK_VALUE_LOSS` | 16 | Valor calculado del tick para las pérdidas. |
| `SYMBOL_TRADE_TICK_SIZE` | 17 | Variación mínima del precio. |
| `SYMBOL_TRADE_CONTRACT_SIZE` | 18 | Tamaño del contrato de trading. |
| `SYMBOL_TRADE_ACCRUED_INTEREST` | 19 | Intereses acumulados. |
| `SYMBOL_TRADE_FACE_VALUE` | 20 | Valor nominal. |
| `SYMBOL_TRADE_LIQUIDITY_RATE` | 21 | Tasa de liquidez. |

### Tasas de swap

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_SWAP_LONG` | 26 | Valor del swap para posiciones largas. |
| `SYMBOL_SWAP_SHORT` | 27 | Valor del swap para posiciones cortas. |
| `SYMBOL_SWAP_SUNDAY` | 28 | Valor del swap del domingo. |
| `SYMBOL_SWAP_MONDAY` | 29 | Valor del swap del lunes. |
| `SYMBOL_SWAP_TUESDAY` | 30 | Valor del swap del martes. |
| `SYMBOL_SWAP_WEDNESDAY` | 31 | Valor del swap del miércoles. |
| `SYMBOL_SWAP_THURSDAY` | 32 | Valor del swap del jueves. |
| `SYMBOL_SWAP_FRIDAY` | 33 | Valor del swap del viernes. |
| `SYMBOL_SWAP_SATURDAY` | 34 | Valor del swap del sábado. |

### Requisitos de margen

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_MARGIN_INITIAL` | 35 | Margen inicial. |
| `SYMBOL_MARGIN_MAINTENANCE` | 36 | Margen de mantenimiento. |
| `SYMBOL_MARGIN_HEDGED` | 48 | Margen para posiciones con cobertura. |

### Propiedades de sesión

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_SESSION_VOLUME` | 37 | Volumen total de la sesión actual. |
| `SYMBOL_SESSION_TURNOVER` | 38 | Importe total negociado durante la sesión actual. |
| `SYMBOL_SESSION_INTEREST` | 39 | Interés abierto total. |
| `SYMBOL_SESSION_BUY_ORDERS_VOLUME` | 40 | Volumen actual de órdenes de compra. |
| `SYMBOL_SESSION_SELL_ORDERS_VOLUME` | 41 | Volumen actual de órdenes de venta. |
| `SYMBOL_SESSION_OPEN` | 42 | Precio de apertura de la sesión actual. |
| `SYMBOL_SESSION_CLOSE` | 43 | Precio de cierre de la sesión actual. |
| `SYMBOL_SESSION_AW` | 44 | Precio medio ponderado. |
| `SYMBOL_SESSION_PRICE_SETTLEMENT` | 45 | Precio de liquidación de la sesión actual. |
| `SYMBOL_SESSION_PRICE_LIMIT_MIN` | 46 | Precio mínimo permitido de la sesión actual. |
| `SYMBOL_SESSION_PRICE_LIMIT_MAX` | 47 | Precio máximo permitido de la sesión actual. |

### Análisis de precios y opciones

| Constante | Valor | Descripción |
|---|---:|---|
| `SYMBOL_OPTION_STRIKE` | 12 | Precio de ejercicio de la opción. |
| `SYMBOL_PRICE_CHANGE` | 49 | Variación del precio en %. |
| `SYMBOL_PRICE_VOLATILITY` | 50 | Volatilidad del precio en %. |
| `SYMBOL_PRICE_THEORETICAL` | 51 | Precio teórico de la opción. |
| `SYMBOL_PRICE_DELTA` | 52 | Delta de la opción o warrant. |
| `SYMBOL_PRICE_THETA` | 53 | Theta de la opción o warrant. |
| `SYMBOL_PRICE_GAMMA` | 54 | Gamma de la opción o warrant. |
| `SYMBOL_PRICE_VEGA` | 55 | Vega de la opción o warrant. |
| `SYMBOL_PRICE_RHO` | 56 | Rho de la opción o warrant. |
| `SYMBOL_PRICE_OMEGA` | 57 | Omega de la opción o warrant. |
| `SYMBOL_PRICE_SENSITIVITY` | 58 | Sensibilidad de la opción o warrant. |
| `SYMBOL_COUNT` | 59 | Número total de propiedades. |

**Uso en Python:**

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Acceder a las constantes de precios
bid_property = market_info_pb2.SYMBOL_BID  # = 0
ask_property = market_info_pb2.SYMBOL_ASK  # = 3

# Utilizar en una llamada al método
bid_data = await account.symbol_info_double("EURUSD", market_info_pb2.SYMBOL_BID)

print(f"BID: {bid_data.value}")
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** protección integrada contra errores gRPC transitorios con reconexión automática mediante `execute_with_reconnect`.
- **Timeout predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Disponibilidad de propiedades:** no todas las propiedades están disponibles para todos los símbolos. Consulta la documentación del bróker para conocer las propiedades específicas de cada símbolo.
- **Valores de tick:** utiliza las propiedades `SYMBOL_TRADE_TICK_VALUE` para realizar cálculos precisos de ganancias y pérdidas.
- **Límites de volumen:** comprueba siempre `SYMBOL_VOLUME_MIN`, `SYMBOL_VOLUME_MAX` y `SYMBOL_VOLUME_STEP` antes de enviar órdenes.

---

## 🔗 Ejemplos de uso

### 1) Obtener los precios BID y ASK

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener el precio BID (formato abreviado, recomendado)
bid_data = await account.symbol_info_double("EURUSD", market_info_pb2.SYMBOL_BID)

print(f"BID: {bid_data.value}")

# Obtener el precio ASK
ask_data = await account.symbol_info_double(
    symbol="EURUSD",
    property=market_info_pb2.SYMBOL_ASK
)

print(f"ASK: {ask_data.value}")

# Calcular el spread
spread = ask_data.value - bid_data.value
print(f"Spread: {spread:.5f}")
```

### 2) Obtener los límites de volumen para operar

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import MT5Account


async def get_volume_limits(account: MT5Account, symbol: str):
    """Obtiene los límites de volumen de un símbolo."""

    # Obtener el volumen mínimo
    min_vol_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_MIN
    )

    # Obtener el volumen máximo
    max_vol_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_MAX
    )

    # Obtener el incremento de volumen
    step_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_VOLUME_STEP
    )

    print(f"Límites de volumen para {symbol}:")
    print(f"  Mínimo: {min_vol_data.value:.2f} lotes")
    print(f"  Máximo: {max_vol_data.value:.2f} lotes")
    print(f"  Incremento: {step_data.value:.2f} lotes")

    return {
        "min": min_vol_data.value,
        "max": max_vol_data.value,
        "step": step_data.value
    }


# Uso:
limits = await get_volume_limits(account, "EURUSD")
```

### 3) Obtener las tasas de swap

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import MT5Account


async def get_swap_info(account: MT5Account, symbol: str):
    """Obtiene las tasas de swap para posiciones largas y cortas."""

    # Obtener el swap para posiciones largas
    long_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_LONG
    )

    # Obtener el swap para posiciones cortas
    short_swap_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SWAP_SHORT
    )

    print(f"Swap para {symbol}:")
    print(f"  Largo: {long_swap_data.value:.2f}")
    print(f"  Corto: {short_swap_data.value:.2f}")

    return {
        "long": long_swap_data.value,
        "short": short_swap_data.value
    }


# Uso:
swaps = await get_swap_info(account, "GBPUSD")
```

### 4) Obtener el tamaño del tick y el tamaño del contrato

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import MT5Account


async def get_trading_specs(account: MT5Account, symbol: str):
    """Obtiene el tamaño del tick y del contrato para realizar cálculos precisos."""

    # Obtener el tamaño del tick (variación mínima del precio)
    tick_size_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_TRADE_TICK_SIZE
    )

    # Obtener el tamaño del contrato
    contract_size_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_TRADE_CONTRACT_SIZE
    )

    # Obtener el valor del punto
    point_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_POINT
    )

    print(f"Especificaciones de trading para {symbol}:")
    print(f"  Tamaño del tick: {tick_size_data.value}")
    print(f"  Tamaño del contrato: {contract_size_data.value}")
    print(f"  Valor del punto: {point_data.value}")

    return {
        "tick_size": tick_size_data.value,
        "contract_size": contract_size_data.value,
        "point": point_data.value
    }


# Uso:
specs = await get_trading_specs(account, "EURUSD")
```

### 5) Comprobar si el precio está dentro de los límites de la sesión

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import MT5Account


async def check_price_limits(account: MT5Account, symbol: str, price: float) -> bool:
    """Comprueba si el precio está dentro de los límites de la sesión actual."""

    # Obtener los límites de precio de la sesión
    min_price_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SESSION_PRICE_LIMIT_MIN
    )

    max_price_data = await account.symbol_info_double(
        symbol,
        market_info_pb2.SYMBOL_SESSION_PRICE_LIMIT_MAX
    )

    min_price = min_price_data.value
    max_price = max_price_data.value

    if min_price <= price <= max_price:
        print(f"[OK] El precio {price} está dentro de los límites [{min_price}, {max_price}]")
        return True
    else:
        print(f"[ERROR] El precio {price} está fuera de los límites [{min_price}, {max_price}]")
        return False


# Uso:
is_valid = await check_price_limits(account, "EURUSD", 1.08500)
```

---

## Patrones comunes

### Validar el volumen antes de enviar una orden

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import MT5Account


async def validate_volume(account: MT5Account, symbol: str, volume: float) -> bool:
    """Valida que el volumen cumpla los requisitos del símbolo."""

    min_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_MIN)
    max_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_MAX)
    step_data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_VOLUME_STEP)

    min_vol = min_data.value
    max_vol = max_data.value
    step = step_data.value

    # Comprobar el rango
    if volume < min_vol or volume > max_vol:
        print(f"[ERROR] El volumen {volume} está fuera del rango [{min_vol}, {max_vol}]")
        return False

    # Comprobar el incremento
    if (volume - min_vol) % step != 0:
        print(f"[ERROR] El volumen {volume} no coincide con el incremento {step}")
        return False

    return True
```

### Obtener el precio actual del mercado

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from MetaRpcMT5 import MT5Account


async def get_market_price(account: MT5Account, symbol: str, side: str) -> float:
    """Obtiene el precio actual del mercado para una compra o una venta."""

    if side.upper() == "BUY":
        # Para órdenes de compra, utilizar el precio ASK
        data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_ASK)
    else:
        # Para órdenes de venta, utilizar el precio BID
        data = await account.symbol_info_double(symbol, market_info_pb2.SYMBOL_BID)

    return data.value
```

---

## 📚 Véase también

- [symbol_info_integer](./symbol_info_integer.md) - Obtener propiedades de tipo entero.
- [symbol_info_string](./symbol_info_string.md) - Obtener propiedades de tipo cadena.
- [symbol_params_many](./symbol_params_many.md) - Obtener todos los parámetros de un símbolo de una sola vez.