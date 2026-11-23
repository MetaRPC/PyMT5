# Obtener las órdenes y posiciones abiertas actualmente

> **Solicitud:** obtener una instantánea completa de todas las órdenes y posiciones abiertas actualmente, con todos sus detalles.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.opened_orders(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `OpenedOrders` (definido en `mt5-term-api-account-helper.proto`)

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `OpenedOrders(OpenedOrdersRequest) -> OpenedOrdersReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.OpenedOrders(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene información detallada de todas las órdenes pendientes y posiciones abiertas.
- **Por qué lo necesitas.** Proporciona una visión completa del estado actual de las operaciones, con todos los detalles de las órdenes y posiciones.
- **Cuándo utilizarlo.** Utiliza este método para obtener información completa. Usa `positions_total()` si solo necesitas los recuentos y `opened_orders_tickets()` si solo necesitas los identificadores de ticket.

---

## 🎯 Propósito

Utiliza este método para obtener información detallada sobre las órdenes y posiciones actuales:

- Obtener todas las órdenes pendientes (Buy Limit, Sell Stop, etc.).
- Obtener todas las posiciones abiertas (Buy/Sell con P/L).
- Supervisar el estado actual de las operaciones.
- Implementar la lógica de gestión de posiciones.
- Mostrar las órdenes y posiciones actuales en la interfaz de usuario.
- Calcular la exposición total.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [opened_orders - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW\.md)**

---

## Firma del método

```python
async def opened_orders(
    self,
    sort_mode: account_helper_pb2.BMT5_ENUM_OPENED_ORDER_SORT_TYPE = account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OpenedOrdersData
```

**Mensaje de solicitud:**

```protobuf
message OpenedOrdersRequest {
  BMT5_ENUM_OPENED_ORDER_SORT_TYPE inputSortMode = 1;
}
```

**Mensaje de respuesta:**

```protobuf
message OpenedOrdersReply {
  oneof response {
    OpenedOrdersData data = 1;
    Error error = 2;
  }
}

message OpenedOrdersData {
  repeated OpenedOrderInfo opened_orders = 1;
  repeated PositionInfo position_infos = 2;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `sort_mode` | `BMT5_ENUM_OPENED_ORDER_SORT_TYPE` (enum) | Modo de ordenación de las órdenes (por hora o por ID de ticket). |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC). |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación. |

**Opciones de deadline:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Con modo de ordenación y deadline
deadline = datetime.now(timezone.utc) + timedelta(seconds=5)
data = await account.opened_orders(
    sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
    deadline=deadline
)

# Ordenación predeterminada (por hora de apertura, ascendente)
data = await account.opened_orders()
```

---

## ⬆️ Salida - `OpenedOrdersData`

| Campo | Tipo | Tipo de Python | Descripción |
|---|---|---|---|
| `opened_orders` | `repeated OpenedOrderInfo` | `list[OpenedOrderInfo]` | Lista de órdenes pendientes. |
| `position_infos` | `repeated PositionInfo` | `list[PositionInfo]` | Lista de posiciones abiertas. |

**Valor de retorno:** el método devuelve un objeto `OpenedOrdersData` con ambas listas accesibles como atributos.

### `OpenedOrderInfo` (elemento de `opened_orders`) — orden pendiente

| Campo | Tipo | Descripción |
|---|---|---|
| `index` | `uint32` | Índice basado en cero dentro de la lista de resultados. |
| `ticket` | `uint64` | Ticket de la orden (identificador único). |
| `price_current` | `double` | Precio actual del mercado. |
| `price_open` | `double` | Precio solicitado/de apertura de la orden. |
| `stop_limit` | `double` | Precio de activación de la orden Stop Limit. |
| `stop_loss` | `double` | Precio de Stop Loss. |
| `take_profit` | `double` | Precio de Take Profit. |
| `volume_current` | `double` | Volumen restante (no ejecutado), en lotes. |
| `volume_initial` | `double` | Volumen inicial, en lotes. |
| `magic_number` | `int64` | Número mágico del Asesor Experto. |
| `reason` | `int32` | Código del motivo de creación de la orden. |
| `type` | `BMT5_ENUM_ORDER_TYPE` | Tipo de orden (buy/sell/limit/stop/…). |
| `state` | `BMT5_ENUM_ORDER_STATE` | Estado de la orden (colocada/ejecutada/…). |
| `time_expiration` | `Timestamp` | Hora de vencimiento (hora del servidor). |
| `time_setup` | `Timestamp` | Hora de colocación (hora del servidor). |
| `time_done` | `Timestamp` | Hora de ejecución/cancelación (hora del servidor). |
| `type_filling` | `BMT5_ENUM_ORDER_TYPE_FILLING` | Política de ejecución. |
| `type_time` | `BMT5_ENUM_ORDER_TYPE_TIME` | Política de vencimiento. |
| `position_id` | `int64` | ID de la posición a la que pertenece esta orden. |
| `position_by_id` | `int64` | ID de la posición opuesta (para close-by). |
| `symbol` | `string` | Símbolo de trading. |
| `external_id` | `string` | ID externo del lado del bróker. |
| `comment` | `string` | Comentario de la orden. |
| `account_login` | `int64` | Login de la cuenta (propietario). |
| `time_expiration_utc` | `Timestamp` | Hora de vencimiento (UTC). |
| `time_setup_utc` | `Timestamp` | Hora de colocación (UTC). |
| `time_done_utc` | `Timestamp` | Hora de ejecución/cancelación (UTC). |

### `PositionInfo` (elemento de `position_infos`) — posición abierta

| Campo | Tipo | Descripción |
|---|---|---|
| `index` | `uint32` | Índice basado en cero dentro de la lista de resultados. |
| `ticket` | `uint64` | Ticket de la posición (identificador único). |
| `open_time` | `Timestamp` | Hora de apertura de la posición (hora del servidor). |
| `volume` | `double` | Volumen de la posición, en lotes. |
| `price_open` | `double` | Precio de apertura. |
| `stop_loss` | `double` | Precio de Stop Loss. |
| `take_profit` | `double` | Precio de Take Profit. |
| `price_current` | `double` | Precio actual del mercado. |
| `swap` | `double` | Swap acumulado. |
| `profit` | `double` | Beneficio/pérdida flotante actual. |
| `last_update_time` | `Timestamp` | Hora de la última actualización (hora del servidor). |
| `type` | `BMT5_ENUM_POSITION_TYPE` | Tipo de posición (buy/sell). |
| `magic_number` | `int64` | Número mágico del Asesor Experto. |
| `identifier` | `int64` | Identificador de la posición. |
| `reason` | `BMT5_ENUM_POSITION_REASON` | Motivo por el que se abrió la posición. |
| `symbol` | `string` | Símbolo de trading. |
| `comment` | `string` | Comentario de la posición. |
| `external_id` | `string` | ID externo del lado del bróker. |
| `position_commission` | `double` | Comisión de la posición. |
| `account_login` | `int64` | Login de la cuenta (propietario). |
| `open_time_utc` | `Timestamp` | Hora de apertura de la posición (UTC). |
| `last_update_time_utc` | `Timestamp` | Hora de la última actualización (UTC). |

---

## 🧱 Enums relacionados (de proto)

> **Nota:** en el código Python, puedes utilizar el enum del módulo `account_helper_pb2`. Este método utiliza **7 enums** con un total de **40 constantes**.

### `BMT5_ENUM_OPENED_ORDER_SORT_TYPE`

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC` | 0 | Ordenar por hora de apertura (primero las más antiguas). |
| `BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_DESC` | 1 | Ordenar por hora de apertura (primero las más recientes). |
| `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_ASC` | 2 | Ordenar por ID de ticket (orden ascendente). |
| `BMT5_OPENED_ORDER_SORT_BY_ORDER_TICKET_ID_DESC` | 3 | Ordenar por ID de ticket (orden descendente). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.opened_orders(
    sort_mode=pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC
)
```

### `BMT5_ENUM_ORDER_TYPE` (para el campo `OpenedOrderInfo.type`)

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_TYPE_BUY` | 0 | Orden de compra a mercado (posición larga). |
| `BMT5_ORDER_TYPE_SELL` | 1 | Orden de venta a mercado (posición corta). |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit. |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit. |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop. |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop. |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden Buy Stop Limit. |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden Sell Stop Limit. |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Orden para cerrar mediante una posición opuesta. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de orden
for order in data.opened_orders:
    if order.type == pb2.BMT5_ORDER_TYPE_BUY_LIMIT:
        print(f"Orden Buy Limit: {order.ticket}")
```

### `BMT5_ENUM_ORDER_STATE` (para el campo `OpenedOrderInfo.state`)

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_STATE_STARTED` | 0 | Orden comprobada, pero todavía no aceptada por el bróker. |
| `BMT5_ORDER_STATE_PLACED` | 1 | Orden aceptada. |
| `BMT5_ORDER_STATE_CANCELED` | 2 | Orden cancelada por el cliente. |
| `BMT5_ORDER_STATE_PARTIAL` | 3 | Orden ejecutada parcialmente. |
| `BMT5_ORDER_STATE_FILLED` | 4 | Orden ejecutada por completo. |
| `BMT5_ORDER_STATE_REJECTED` | 5 | Orden rechazada. |
| `BMT5_ORDER_STATE_EXPIRED` | 6 | Orden vencida. |
| `BMT5_ORDER_STATE_REQUEST_ADD` | 7 | La orden se está registrando (añadiendo al sistema de trading). |
| `BMT5_ORDER_STATE_REQUEST_MODIFY` | 8 | La orden se está modificando (cambiando sus parámetros). |
| `BMT5_ORDER_STATE_REQUEST_CANCEL` | 9 | La orden se está eliminando (borrando del sistema de trading). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el estado de la orden
for order in data.opened_orders:
    if order.state == pb2.BMT5_ORDER_STATE_PLACED:
        print(f"La orden {order.ticket} está activa")
```

### `BMT5_ENUM_ORDER_TYPE_FILLING` (para el campo `OpenedOrderInfo.type_filling`)

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill: ejecutar por completo o cancelar. |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel: ejecutar el volumen disponible. |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Modo de ejecución Return. |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel: colocar la orden en el libro de órdenes. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de ejecución
for order in data.opened_orders:
    if order.type_filling == pb2.BMT5_ORDER_FILLING_FOK:
        print(f"La orden {order.ticket} utiliza Fill-or-Kill")
```

### `BMT5_ENUM_ORDER_TYPE_TIME` (para el campo `OpenedOrderInfo.type_time`)

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_TIME_GTC` | 0 | Good Till Cancelled (válida hasta su cancelación). |
| `BMT5_ORDER_TIME_DAY` | 1 | Good Till Day (válida hasta el final del día). |
| `BMT5_ORDER_TIME_SPECIFIED` | 2 | Good Till Specified Time (válida hasta la hora especificada). |
| `BMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Good Till Specified Day (válida hasta el final del día especificado). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de duración
for order in data.opened_orders:
    if order.type_time == pb2.BMT5_ORDER_TIME_GTC:
        print(f"La orden {order.ticket} es GTC")
```

### `BMT5_ENUM_POSITION_TYPE` (para el campo `PositionInfo.type`)

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_POSITION_TYPE_BUY` | 0 | Posición de compra (larga). |
| `BMT5_POSITION_TYPE_SELL` | 1 | Posición de venta (corta). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de posición
for pos in data.position_infos:
    if pos.type == pb2.BMT5_POSITION_TYPE_BUY:
        print(f"Posición larga: {pos.ticket}")
```

### `BMT5_ENUM_POSITION_REASON` (para el campo `PositionInfo.reason`)

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_POSITION_REASON_CLIENT` | 0 | Posición abierta manualmente por el cliente. |
| `BMT5_POSITION_REASON_MOBILE` | 1 | Posición abierta mediante la aplicación móvil. |
| `BMT5_POSITION_REASON_WEB` | 2 | Posición abierta mediante la plataforma web. |
| `BMT5_POSITION_REASON_EXPERT` | 3 | Posición abierta por un Asesor Experto. |
| `ORDER_REASON_SL` | 4 | Posición cerrada mediante Stop Loss. |
| `ORDER_REASON_TP` | 5 | Posición cerrada mediante Take Profit. |
| `ORDER_REASON_SO` | 6 | Posición cerrada mediante Stop Out. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el motivo de apertura de la posición
for pos in data.position_infos:
    if pos.reason == pb2.BMT5_POSITION_REASON_EXPERT:
        print(f"La posición {pos.ticket} fue abierta por un EA")
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de `MT5Account` incorporan protección contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Tiempo de espera predeterminado:** si `deadline` es `None`, el método esperará indefinidamente (o hasta que se agote el tiempo de espera del servidor).
- **Dos listas independientes:** las órdenes y las posiciones se devuelven en listas separadas. Comprueba ambas.
- **Conexión necesaria:** debes llamar a `connect_by_host_port()` o `connect_by_server_name()` antes de utilizar este método.
- **Información completa:** este método devuelve información completa sobre las órdenes y posiciones. Utiliza `opened_orders_tickets()` si necesitas una carga de datos más ligera.
- **Seguridad de los hilos:** todos los métodos asíncronos se pueden ejecutar de forma segura y simultánea desde varias tareas de asyncio.
- **Gestión de UUID:** el UUID de la instancia del terminal se genera automáticamente en el servidor si no se proporciona. Para controlarlo explícitamente (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener todas las órdenes y posiciones abiertas

```python
import asyncio
from datetime import datetime, timedelta, timezone
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2


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
        deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

        data = await account.opened_orders(
            sort_mode=account_helper_pb2.BMT5_OPENED_ORDER_SORT_BY_OPEN_TIME_ASC,
            deadline=deadline
        )

        print(f"Órdenes pendientes: {len(data.opened_orders)}")
        print(f"Posiciones abiertas: {len(data.position_infos)}")

        # Mostrar las posiciones
        for pos in data.position_infos:
            print(f"Posición #{pos.ticket} {pos.symbol}: "
                  f"{pos.volume} lotes @ {pos.price_open}, P/L: ${pos.profit:.2f}")

        # Mostrar las órdenes
        for order in data.opened_orders:
            print(f"Orden #{order.ticket} {order.symbol}: "
                  f"{order.volume_initial} lotes @ {order.price_open}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 2) Contar por separado las órdenes y las posiciones

```python
async def get_opened_summary(account: MT5Account) -> dict:
    """Obtener un resumen de las órdenes y posiciones abiertas"""
    data = await account.opened_orders()

    summary = {
        "orders_count": len(data.opened_orders),
        "positions_count": len(data.position_infos),
        "total_count": len(data.opened_orders) + len(data.position_infos)
    }

    print(f"[OK] Órdenes pendientes: {summary['orders_count']}")
    print(f"[OK] Posiciones abiertas: {summary['positions_count']}")
    print(f"[OK] Total: {summary['total_count']}")

    return summary


# Uso:
summary = await get_opened_summary(account)
```

### 3) Calcular el P/L flotante total

```python
async def get_total_profit(account: MT5Account) -> float:
    """Calcular el beneficio/pérdida flotante total de todas las posiciones"""
    data = await account.opened_orders()

    total_profit = sum(pos.profit for pos in data.position_infos)

    print(f"P/L flotante total: ${total_profit:+.2f}")
    return total_profit


# Uso:
profit = await get_total_profit(account)
if profit < 0:
    print(f"[ADVERTENCIA] La cuenta está en pérdidas: ${profit:.2f}")
```

### 4) Buscar posiciones por símbolo

```python
async def get_positions_by_symbol(
    account: MT5Account,
    symbol: str
) -> list:
    """Obtener todas las posiciones abiertas para un símbolo específico"""
    data = await account.opened_orders()

    positions = [
        pos for pos in data.position_infos
        if pos.symbol == symbol
    ]

    print(f"[OK] Se encontraron {len(positions)} posición(es) para {symbol}")
    return positions


# Uso:
eurusd_positions = await get_positions_by_symbol(account, "EURUSD")
for pos in eurusd_positions:
    print(f"  #{pos.ticket}: {pos.volume} lotes, P/L: ${pos.profit:.2f}")
```

### 5) Mostrar las posiciones con sus detalles

```python
async def display_positions(account: MT5Account):
    """Mostrar todas las posiciones con información formateada"""
    data = await account.opened_orders()

    if not data.position_infos:
        print("[INFO] No hay posiciones abiertas")
        return

    print(f"\n{'='*80}")
    print(f"POSICIONES ABIERTAS ({len(data.position_infos)})")
    print(f"{'='*80}")
    print(f"{'Ticket':<12} {'Símbolo':<10} {'Volumen':<8} {'Precio':<10} {'Actual':<10} {'Beneficio':<12}")
    print(f"{'-'*80}")

    for pos in data.position_infos:
        type_str = "BUY" if pos.type == 0 else "SELL"
        print(f"{pos.ticket:<12} {pos.symbol:<10} {pos.volume:<8.2f} "
              f"{pos.price_open:<10.5f} {pos.price_current:<10.5f} ${pos.profit:+11.2f}")

    total = sum(pos.profit for pos in data.position_infos)
    print(f"{'-'*80}")
    print(f"{'TOTAL:':<62} ${total:+11.2f}")
    print(f"{'='*80}\n")


# Uso:
await display_positions(account)
```

### 6) Supervisar las nuevas órdenes y posiciones

```python
async def monitor_opened(account: MT5Account, interval: float = 5.0):
    """Supervisar los cambios en las órdenes y posiciones"""
    previous_tickets = set()

    while True:
        try:
            data = await account.opened_orders()

            # Recopilar todos los tickets actuales
            current_tickets = set()
            for order in data.opened_orders:
                current_tickets.add(("ORDER", order.ticket))
            for pos in data.position_infos:
                current_tickets.add(("POSITION", pos.ticket))

            # Detectar nuevos elementos
            if previous_tickets:
                new_items = current_tickets - previous_tickets
                closed_items = previous_tickets - current_tickets

                for item_type, ticket in new_items:
                    print(f"[+] Nuevo {item_type}: #{ticket}")

                for item_type, ticket in closed_items:
                    print(f"[-] Cerrado {item_type}: #{ticket}")

            previous_tickets = current_tickets

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(interval)


# Uso:
# await monitor_opened(account, interval=5.0)
```

### 7) Obtener las posiciones ordenadas por beneficio

```python
async def get_worst_positions(account: MT5Account, limit: int = 5):
    """Obtener las posiciones con el peor rendimiento"""
    data = await account.opened_orders()

    # Ordenar por beneficio (primero las peores)
    sorted_positions = sorted(
        data.position_infos,
        key=lambda p: p.profit
    )

    worst = sorted_positions[:limit]

    print(f"\nLas {limit} peores posiciones:")
    for i, pos in enumerate(worst, 1):
        print(f"{i}. #{pos.ticket} {pos.symbol}: ${pos.profit:+.2f}")

    return worst


# Uso:
worst = await get_worst_positions(account, limit=5)
```

### 8) Comprobar si un símbolo tiene una posición abierta

```python
async def has_position_for_symbol(
    account: MT5Account,
    symbol: str
) -> bool:
    """Comprobar si un símbolo tiene una posición abierta"""
    data = await account.opened_orders()

    has_pos = any(pos.symbol == symbol for pos in data.position_infos)

    if has_pos:
        print(f"[OK] Se encontró una posición para {symbol}")
    else:
        print(f"[INFO] No hay ninguna posición para {symbol}")

    return has_pos


# Uso:
if not await has_position_for_symbol(account, "EURUSD"):
    print("Se puede abrir una nueva posición EURUSD")
```

---

## Patrones de uso comunes

### Búsqueda rápida de una posición

```python
async def get_position_by_ticket(account: MT5Account, ticket: int):
    """Buscar una posición específica por ticket"""
    data = await account.opened_orders()
    for pos in data.position_infos:
        if pos.ticket == ticket:
            return pos
    return None
```

### Calcular la exposición por símbolo

```python
async def get_symbol_exposure(account: MT5Account) -> dict:
    """Calcular el volumen total por símbolo"""
    data = await account.opened_orders()

    exposure = {}
    for pos in data.position_infos:
        exposure[pos.symbol] = exposure.get(pos.symbol, 0) + pos.volume

    return exposure
```

---

## 📚 Véase también

- [positions_total](./positions_total.md) - Obtener solo el recuento (más rápido).
- [opened_orders_tickets](./opened_orders_tickets.md) - Obtener únicamente los ID de los tickets.
- [positions_history](./positions_history.md) - Obtener el historial de posiciones cerradas.
- [order_history](./order_history.md) - Obtener el historial de órdenes.