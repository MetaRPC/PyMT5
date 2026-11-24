# Obtener el valor del tick y el tamaño del contrato de los símbolos

> **Solicitud:** obtener información sobre el valor del tick y el tamaño del contrato de varios símbolos.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.tick_value_with_size(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `TickValueWithSize` (definido en `mt5-term-api-account-helper.proto`)
- **Enums de este método:** 0 enums (estructura de datos simple)

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `TickValueWithSize(TickValueWithSizeRequest) -> TickValueWithSizeReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.TickValueWithSize(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene los valores del tick y los tamaños de los contratos de varios símbolos en una sola llamada.
- **Por qué lo necesitas.** Permite calcular el valor de las posiciones, los requisitos de margen y las ganancias/pérdidas en la divisa de la cuenta.
- **Cuándo utilizarlo.** Utiliza este método antes de operar para conocer el valor del tick y el tamaño del contrato necesarios para calcular el riesgo.

---

## 🎯 Propósito

Utiliza este método para obtener parámetros de trading importantes:

- Obtener el valor del tick (valor de un movimiento de un tick).
- Obtener el tamaño del tick (cambio mínimo del precio).
- Obtener el tamaño del contrato (unidades del activo subyacente por lote).
- Calcular las ganancias/pérdidas por tick.
- Conocer los requisitos de margen.
- Consultar varios símbolos en una sola solicitud de forma eficiente.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [tick_value_with_size - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW.md)**

---

## Firma del método

```python
async def tick_value_with_size(
    self,
    symbols: list[str],
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.TickValueWithSizeData
```

**Mensaje de solicitud:**

```protobuf
message TickValueWithSizeRequest {
    repeated string symbol_names = 1;
}
```

**Mensaje de respuesta:**

```protobuf
message TickValueWithSizeReply {
    TickValueWithSizeData data = 1;
    Error error = 2;
}

message TickValueWithSizeData {
    repeated TickSizeSymbol symbol_tick_size_infos = 1;
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbols` | `list[str]` (obligatorio) | Lista de nombres de símbolos que se van a consultar |
| `deadline` | `datetime` (opcional) | Fecha límite para la llamada gRPC (fecha y hora UTC) |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación |

**Uso:**

```python
from datetime import datetime, timedelta, timezone

# Consultar varios símbolos
symbols = ["EURUSD", "GBPUSD", "USDJPY"]

deadline = datetime.now(timezone.utc) + timedelta(seconds=5)
data = await account.tick_value_with_size(
    symbols=symbols,
    deadline=deadline
)
```

---

## ⬆️ Salida - `TickValueWithSizeData`

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `symbol_tick_size_infos` | `repeated TickSizeSymbol` | `list[TickSizeSymbol]` | Lista con información sobre el valor y el tamaño del tick de cada símbolo |

**Cada `TickSizeSymbol` contiene:**

| Campo | Tipo | Tipo Python | Descripción |
|---|---|---|---|
| `Index` | `int32` | `int` | Índice en el conjunto de resultados |
| `Name` | `string` | `str` | Nombre del símbolo |
| `TradeTickValue` | `double` | `float` | Valor del tick (tanto para el cálculo de ganancias como de pérdidas) |
| `TradeTickValueProfit` | `double` | `float` | Valor del tick para el cálculo de ganancias |
| `TradeTickValueLoss` | `double` | `float` | Valor del tick para el cálculo de pérdidas |
| `TradeTickSize` | `double` | `float` | Cambio mínimo del precio (tamaño del tick) |
| `TradeContractSize` | `double` | `float` | Unidades del activo subyacente por lote (por ejemplo, 100 000 para EURUSD) |

---

## 🧩 Notas y consejos

- **Consulta por lotes:** consulta varios símbolos en una sola llamada para mejorar la eficiencia.
- **Valor del tick:** valor, en la divisa de la cuenta, de un movimiento de un tick.
- **Tamaño del contrato:** unidades del activo subyacente por lote (por ejemplo, 100 000 unidades para EURUSD).
- **Cálculo de ganancias/pérdidas:** utiliza el valor del tick y el tamaño del tick para calcular las ganancias/pérdidas por pip o tick.
- **Reconexión automática:** protección integrada contra errores gRPC transitorios.
- **Se requiere conexión:** llama primero a `connect_by_host_port()` o `connect_by_server_name()`.
- **Seguridad de hilos:** se puede llamar de forma segura simultáneamente desde varias tareas de asyncio.

---

## 🔗 Ejemplos de uso

### 1) Obtener los valores del tick de varios símbolos

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account


async def main():
    account = MT5Account(
        user=12345678,
        password="your_password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

        data = await account.tick_value_with_size(
            symbols=symbols,
            deadline=deadline
        )

        for info in data.symbol_tick_size_infos:
            print(f"\n{info.Name}:")
            print(f"  Valor del tick: ${info.TradeTickValue:.2f}")
            print(f"  Tamaño del tick: {info.TradeTickSize}")
            print(f"  Tamaño del contrato: {info.TradeContractSize:.0f}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 2) Calcular la ganancia por pip

```python
async def calculate_profit_per_pip(
    account: MT5Account,
    symbol: str,
    lots: float
) -> float:
    """Calcula la ganancia por pip para el símbolo y el volumen indicados"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Símbolo {symbol} no encontrado")

    info = data.symbol_tick_size_infos[0]

    # Calcular la ganancia por pip (suponiendo 10 ticks por pip para la mayoría de los pares)
    profit_per_pip = info.TradeTickValue * 10 * lots

    print(f"{symbol}:")
    print(f"  Volumen: {lots} lotes")
    print(f"  Ganancia por pip: ${profit_per_pip:.2f}")

    return profit_per_pip


# Uso:
profit_per_pip = await calculate_profit_per_pip(account, "EURUSD", 1.0)
```

### 3) Calcular el margen requerido

```python
async def calculate_margin(
    account: MT5Account,
    symbol: str,
    lots: float,
    price: float,
    leverage: int
) -> float:
    """Calcula el margen requerido para una posición"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Símbolo {symbol} no encontrado")

    info = data.symbol_tick_size_infos[0]

    # Margen = (Tamaño del contrato * Lotes * Precio) / Apalancamiento
    contract_value = info.TradeContractSize * lots * price
    margin = contract_value / leverage

    print(f"Cálculo del margen para {symbol}:")
    print(f"  Volumen: {lots} lotes")
    print(f"  Precio: {price}")
    print(f"  Apalancamiento: 1:{leverage}")
    print(f"  Tamaño del contrato: {info.TradeContractSize:.0f}")
    print(f"  Margen requerido: ${margin:.2f}")

    return margin


# Uso:
margin = await calculate_margin(account, "EURUSD", 1.0, 1.10000, 100)
```

### 4) Obtener información del tick de los principales pares

```python
async def get_major_pairs_info(account: MT5Account):
    """Obtiene información sobre el valor del tick de los principales pares de divisas"""
    major_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "USDCAD", "NZDUSD"
    ]

    data = await account.tick_value_with_size(symbols=major_pairs)

    print("\nInformación de los ticks de los principales pares:")
    print(f"{'Símbolo':<10} {'Valor del tick':<12} {'Tamaño del tick':<12} {'Tamaño del contrato':<15}")
    print("-" * 60)

    for info in data.symbol_tick_size_infos:
        print(f"{info.Name:<10} ${info.TradeTickValue:<11.2f} "
              f"{info.TradeTickSize:<12} {info.TradeContractSize:<15.0f}")

    return data


# Uso:
await get_major_pairs_info(account)
```

### 5) Calcular el valor de una posición

```python
async def calculate_position_value(
    account: MT5Account,
    symbol: str,
    lots: float,
    price: float
) -> dict:
    """Calcula el valor total de una posición"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Símbolo {symbol} no encontrado")

    info = data.symbol_tick_size_infos[0]

    # Valor de la posición = Tamaño del contrato * Lotes * Precio
    position_value = info.TradeContractSize * lots * price

    result = {
        "symbol": symbol,
        "lots": lots,
        "price": price,
        "contract_size": info.TradeContractSize,
        "position_value": position_value,
        "tick_value": info.TradeTickValue,
        "tick_size": info.TradeTickSize
    }

    print(f"\nCálculo del valor de la posición:")
    print(f"  Símbolo: {symbol}")
    print(f"  Volumen: {lots} lotes")
    print(f"  Precio: {price}")
    print(f"  Tamaño del contrato: {info.TradeContractSize:.0f}")
    print(f"  Valor de la posición: ${position_value:,.2f}")

    return result


# Uso:
value = await calculate_position_value(account, "EURUSD", 1.0, 1.10000)
```

### 6) Comparar los valores del tick entre símbolos

```python
async def compare_tick_values(account: MT5Account, symbols: list[str]):
    """Compara los valores del tick de varios símbolos"""
    data = await account.tick_value_with_size(symbols=symbols)

    # Ordenar por valor del tick
    sorted_infos = sorted(
        data.symbol_tick_size_infos,
        key=lambda x: x.TradeTickValue,
        reverse=True
    )

    print("\nSímbolos ordenados por valor del tick:")
    for i, info in enumerate(sorted_infos, 1):
        print(f"{i}. {info.Name}: ${info.TradeTickValue:.2f} por tick")

    return sorted_infos


# Uso:
symbols = ["EURUSD", "GBPUSD", "USDJPY", "GOLD", "OIL"]
await compare_tick_values(account, symbols)
```

### 7) Calcular la distancia del Stop Loss

```python
async def calculate_sl_distance(
    account: MT5Account,
    symbol: str,
    lots: float,
    max_loss: float
) -> float:
    """Calcula la distancia máxima del SL para la pérdida máxima indicada"""
    data = await account.tick_value_with_size(symbols=[symbol])

    if not data.symbol_tick_size_infos:
        raise ValueError(f"Símbolo {symbol} no encontrado")

    info = data.symbol_tick_size_infos[0]

    # Calcular los pips permitidos (suponiendo 10 ticks por pip; la mayoría de los pares)
    profit_per_pip = info.TradeTickValue * 10 * lots
    max_pips = max_loss / profit_per_pip if profit_per_pip > 0 else 0

    print(f"\nCálculo del Stop Loss para {symbol}:")
    print(f"  Volumen: {lots} lotes")
    print(f"  Pérdida máxima: ${max_loss:.2f}")
    print(f"  Ganancia por pip: ${profit_per_pip:.2f}")
    print(f"  Distancia máxima del SL: {max_pips:.1f} pips")

    return max_pips


# Uso:
max_pips = await calculate_sl_distance(account, "EURUSD", 1.0, 100.0)
```

### 8) Validar la existencia de los símbolos

```python
async def validate_symbols(
    account: MT5Account,
    symbols: list[str]
) -> dict:
    """Comprueba qué símbolos son válidos y están disponibles"""
    data = await account.tick_value_with_size(symbols=symbols)

    returned_symbols = {info.Name for info in data.symbol_tick_size_infos}
    requested_symbols = set(symbols)

    valid = list(returned_symbols)
    invalid = list(requested_symbols - returned_symbols)

    result = {
        "valid": valid,
        "invalid": invalid,
        "valid_count": len(valid),
        "invalid_count": len(invalid)
    }

    print(f"\nValidación de símbolos:")
    print(f"  Símbolos válidos: {valid}")
    if invalid:
        print(f"  Símbolos no válidos: {invalid}")

    return result


# Uso:
symbols = ["EURUSD", "INVALID_SYMBOL", "GBPUSD"]
validation = await validate_symbols(account, symbols)
```

---

## Patrones comunes

### Obtener el valor del tick de un solo símbolo

```python
async def get_symbol_tick_value(account: MT5Account, symbol: str) -> float:
    """Obtiene el valor del tick de un solo símbolo"""
    data = await account.tick_value_with_size(symbols=[symbol])
    if data.symbol_tick_size_infos:
        return data.symbol_tick_size_infos[0].TradeTickValue
    return 0.0
```

### Calcular el riesgo por posición

```python
async def calculate_risk(
    account: MT5Account,
    symbol: str,
    lots: float,
    sl_pips: float
) -> float:
    """Calcula el importe del riesgo de una posición con SL"""
    data = await account.tick_value_with_size(symbols=[symbol])
    if not data.symbol_tick_size_infos:
        return 0.0

    info = data.symbol_tick_size_infos[0]
    # suponiendo 10 ticks por pip (la mayoría de los pares)
    profit_per_pip = info.TradeTickValue * 10 * lots
    risk = profit_per_pip * sl_pips

    return risk
```

---

## 📚 Véase también

- [opened_orders](./opened_orders.md) - Obtener las posiciones abiertas actualmente
- [positions_total](./positions_total.md) - Obtener el número de posiciones abiertas