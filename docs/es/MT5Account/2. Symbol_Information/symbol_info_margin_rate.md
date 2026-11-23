

# Obtener las tasas de margen de un símbolo

> **Solicitud:** obtener las tasas de margen de un símbolo y un tipo de orden.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.symbol_info_margin_rate(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `SymbolInfoMarginRate` (definido en `mt5-term-api-market-info.proto`)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `SymbolInfoMarginRate(SymbolInfoMarginRateRequest) -> SymbolInfoMarginRateReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.SymbolInfoMarginRate(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene las tasas de margen inicial y de mantenimiento para un símbolo y un tipo de orden específicos.
- **Por qué lo necesitas.** Permite calcular los requisitos de margen antes de enviar órdenes y comprender las condiciones de apalancamiento.
- **Cuándo utilizarlo.** Antes de operar para estimar los requisitos de margen, especialmente para distintos tipos de órdenes (BUY/SELL).

---

## 🎯 Propósito

Utiliza este método para consultar los requisitos de margen:

- Calcular el margen necesario antes de abrir posiciones.
- Comprender las diferencias de margen entre las órdenes BUY y SELL.
- Estimar el impacto del apalancamiento en el margen.
- Verificar el margen disponible antes de operar.
- Comparar los requisitos de margen entre distintos símbolos.
- Planificar el tamaño de las posiciones según el margen disponible.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [symbol_info_margin_rate - Cómo funciona](../HOW_IT_WORK/2. Symbol_information_HOW/symbol_info_margin_rate_HOW.md)**

---

## Firma del método

```python
async def symbol_info_margin_rate(
    self,
    symbol: str,
    order_type: market_info_pb2.ENUM_ORDER_TYPE,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> market_info_pb2.SymbolInfoMarginRateData
```

**Mensaje de solicitud:**

```protobuf
message SymbolInfoMarginRateRequest {
    string symbol = 1;
    ENUM_ORDER_TYPE order_type = 2;
}
```

**Mensaje de respuesta:**

```protobuf
message SymbolInfoMarginRateReply {
    oneof response {
        SymbolInfoMarginRateData data = 1;
        Error error = 2;
    }
}

message SymbolInfoMarginRateData {
    double maintenance_margin_rate = 1;
    double initial_margin_rate = 2;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` (obligatorio) | Nombre del símbolo |
| `order_type` | `ENUM_ORDER_TYPE` (enum) | Tipo de orden (BUY, SELL, etc.) |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

---

## ⬆️ Salida

| Campo | Tipo | Tipo de Python | Descripción |
|---|---|---|---|
| `initial_margin_rate` | `double` | `float` | Tasa de margen inicial |
| `maintenance_margin_rate` | `double` | `float` | Tasa de margen de mantenimiento |

**Valor devuelto:** el método devuelve un objeto `SymbolInfoMarginRateData` con los campos de las tasas de margen.

---

## 🧱 Enums relacionados (del proto)

> **Nota:** En el código Python, utiliza la ruta completa del enum del módulo `market_info`.

### `ENUM_ORDER_TYPE`

Definido en `mt5-term-api-market-info.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `ORDER_TYPE_BUY` | 0 | Orden de mercado de compra |
| `ORDER_TYPE_SELL` | 1 | Orden de mercado de venta |
| `ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit |
| `ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit |
| `ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop |
| `ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop |
| `ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit |
| `ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit |
| `ORDER_TYPE_CLOSE_BY` | 8 | Cierre mediante una orden opuesta |

**Uso en Python:**

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener las tasas de margen para órdenes BUY
rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Tasa de margen inicial: {rates.initial_margin_rate}")
print(f"Tasa de margen de mantenimiento: {rates.maintenance_margin_rate}")
```

---

## 🧩 Notas y recomendaciones

- **Reconexión automática:** protección integrada contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se produzca un timeout del servidor).
- **Significado de las tasas de margen:**
  - **Tasa de margen inicial:** tasa utilizada al abrir una posición (multiplicada por el valor del contrato).
  - **Tasa de margen de mantenimiento:** tasa utilizada para mantener una posición abierta.
- **Diferencias entre tasas:** las órdenes BUY y SELL pueden tener tasas de margen diferentes para un mismo símbolo.
- **Cuentas con cobertura (Hedge):** en las cuentas con cobertura, las tasas de margen suelen ser iguales para BUY y SELL.
- **Cuentas con compensación (Netting):** en las cuentas con compensación, los cálculos de margen pueden variar según la dirección de la posición.
- **Cálculo:** Margen requerido = (Tamaño del contrato × Volumen × Precio) × Tasa de margen.
- **Gestión de UUID:** el servidor genera automáticamente el UUID de la instancia del terminal si no se proporciona.  
  Para tener un control explícito (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener las tasas de margen para una orden BUY

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener las tasas de margen para una orden BUY
rates = await account.symbol_info_margin_rate(
    symbol="EURUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Tasas de margen de la orden BUY:")
print(f"  Inicial: {rates.initial_margin_rate}")
print(f"  Mantenimiento: {rates.maintenance_margin_rate}")
```

### 2) Comparar las tasas de margen de BUY y SELL

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

# Obtener las tasas de margen BUY
buy_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

# Obtener las tasas de margen SELL
sell_rates = await account.symbol_info_margin_rate(
    symbol="XAUUSD",
    order_type=market_info_pb2.ORDER_TYPE_SELL
)

print(f"Tasas de margen de XAUUSD:")
print(f"  BUY  - Inicial: {buy_rates.initial_margin_rate}, Mantenimiento: {buy_rates.maintenance_margin_rate}")
print(f"  SELL - Inicial: {sell_rates.initial_margin_rate}, Mantenimiento: {sell_rates.maintenance_margin_rate}")

if buy_rates.initial_margin_rate == sell_rates.initial_margin_rate:
    print("  Las tasas de margen son iguales para ambas direcciones (cuenta Hedge)")
else:
    print("  Las tasas de margen son diferentes (comprueba el tipo de cuenta)")
```

### 3) Calcular el margen requerido antes de operar

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def calculate_required_margin(
    account,
    symbol: str,
    volume: float,
    order_type: int = market_info_pb2.ORDER_TYPE_BUY
) -> float:
    """Calcula el margen necesario para abrir una posición"""

    # Obtener las tasas de margen
    rates = await account.symbol_info_margin_rate(
        symbol=symbol,
        order_type=order_type
    )

    # Obtener el tamaño del contrato
    contract_size_data = await account.symbol_info_double(
        symbol=symbol,
        property=market_info_pb2.SYMBOL_TRADE_CONTRACT_SIZE
    )

    # Obtener el precio actual (ASK para BUY, BID para SELL)
    if order_type in [market_info_pb2.ORDER_TYPE_BUY, market_info_pb2.ORDER_TYPE_BUY_LIMIT, market_info_pb2.ORDER_TYPE_BUY_STOP]:
        price_data = await account.symbol_info_double(symbol=symbol, property=market_info_pb2.SYMBOL_ASK)
    else:
        price_data = await account.symbol_info_double(symbol=symbol, property=market_info_pb2.SYMBOL_BID)

    # Calcular el margen
    contract_value = contract_size_data.value * volume * price_data.value
    required_margin = contract_value * rates.initial_margin_rate

    return required_margin


# Uso
margin = await calculate_required_margin(
    account=account,
    symbol="EURUSD",
    volume=1.0,
    order_type=market_info_pb2.ORDER_TYPE_BUY
)

print(f"Margen requerido para 1.0 lote de EURUSD BUY: ${margin:.2f}")
```

### 4) Comprobar si hay margen suficiente disponible

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

async def can_open_position(
    account,
    symbol: str,
    volume: float,
    order_type: int = market_info_pb2.ORDER_TYPE_BUY
) -> bool:
    """Comprueba si la cuenta tiene margen suficiente para abrir una posición"""

    # Calcular el margen requerido (a partir del ejemplo anterior)
    required_margin = await calculate_required_margin(account, symbol, volume, order_type)

    # Obtener el margen libre
    free_margin = await account.account_info_double(
        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    # Comprobar si es suficiente
    if free_margin >= required_margin:
        print(f"[OK] Margen suficiente:")
        print(f"  Requerido: ${required_margin:.2f}")
        print(f"  Disponible: ${free_margin:.2f}")
        return True
    else:
        print(f"[ERROR] Margen insuficiente:")
        print(f"  Requerido: ${required_margin:.2f}")
        print(f"  Disponible: ${free_margin:.2f}")
        print(f"  Déficit: ${required_margin - free_margin:.2f}")
        return False


# Uso
if await can_open_position(account, "EURUSD", 2.0):
    print("La cuenta tiene margen libre suficiente para abrir la posición de 2.0 lotes según esta estimación")
```

### 5) Obtener las tasas de margen con un plazo límite

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
from datetime import datetime, timedelta, timezone

# Establecer el plazo límite
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

try:
    rates = await account.symbol_info_margin_rate(
        symbol="GBPUSD",
        order_type=market_info_pb2.ORDER_TYPE_BUY,
        deadline=deadline
    )
    print(f"Tasas de margen obtenidas: {rates.initial_margin_rate}")
except Exception as e:
    print(f"Timeout o error: {e}")
```

### 6) Comparar los requisitos de margen entre símbolos

```python
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2

async def compare_symbol_margins(account, symbols: list[str]):
    """Compara los requisitos de margen de varios símbolos"""

    print(f"{'Símbolo':<10} {'Tasa inicial':<15} {'Tasa de mantenimiento':<20}")
    print("=" * 45)

    for symbol in symbols:
        try:
            rates = await account.symbol_info_margin_rate(
                symbol=symbol,
                order_type=market_info_pb2.ORDER_TYPE_BUY
            )
            print(f"{symbol:<10} {rates.initial_margin_rate:<15.4f} {rates.maintenance_margin_rate:<20.4f}")
        except Exception as e:
            print(f"{symbol:<10} ERROR: {e}")


# Uso
await compare_symbol_margins(account, ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"])
```

---

## 📚 Véase también

- [symbol_info_double](./symbol_info_double.md) - Obtener propiedades `double` del símbolo (tamaño del contrato, precios).
- [order_calc_margin](../5. Trading_Operations/order_calc_margin.md) - Calcular el margen para parámetros de una orden específica.
- [account_info_double](../1. Account_Information/account_info_double.md) - Obtener información sobre el margen de la cuenta.

