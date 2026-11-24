# Obtener el historial de órdenes

> **Solicitud:** obtener datos históricos de órdenes dentro de un intervalo de tiempo especificado, con compatibilidad para la paginación.

**Información de la API:**

- **API de bajo nivel:** `MT5Account.order_history(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.AccountHelper`
- **Definición Proto:** `OrderHistory` (definido en `mt5-term-api-account-helper.proto`)
- **Enums en este método:** 8 enums con un total de 66 constantes (1 de entrada y 7 de salida).

### RPC

- **Servicio:** `mt5_term_api.AccountHelper`
- **Método:** `OrderHistory(OrderHistoryRequest) -> OrderHistoryReply`
- **Cliente de bajo nivel (generado):** `AccountHelperStub.OrderHistory(request, metadata, timeout)`

## 💬 Lo esencial

- **Qué es.** Obtiene el historial de órdenes y operaciones dentro de un intervalo de tiempo, con opciones de ordenación y paginación.
- **Por qué lo necesitas.** Para analizar el historial de trading, calcular estadísticas y auditar órdenes.
- **Cuándo utilizarlo.** Utiliza este método para consultar el historial de órdenes. Utiliza `positions_history()` para consultar las posiciones cerradas.

---

## 🎯 Propósito

Utiliza este método para recuperar datos históricos de trading:

- Obtener órdenes y operaciones anteriores dentro de un intervalo de fechas.
- Analizar el rendimiento del trading.
- Calcular estadísticas de beneficios y pérdidas.
- Auditar la actividad de trading.
- Exportar el historial de trading.
- Utilizar la paginación para conjuntos de datos grandes.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**-> [order_history - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW\.md)**

---

## Firma del método

```python
async def order_history(
    self,
    from_dt: datetime,
    to_dt: datetime,
    sort_mode: account_helper_pb2.BMT5_ENUM_ORDER_HISTORY_SORT_TYPE = account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_ASC,
    page_number: int = 0,
    items_per_page: int = 0,
    deadline: Optional[datetime] = None,
    cancellation_event: Optional[asyncio.Event] = None,
) -> account_helper_pb2.OrdersHistoryData
```

**Mensaje de solicitud:**

```protobuf
message OrderHistoryRequest {
  google.protobuf.Timestamp inputFrom = 1;
  google.protobuf.Timestamp inputTo = 2;
  BMT5_ENUM_ORDER_HISTORY_SORT_TYPE inputSortMode = 3;
  int32 pageNumber = 4;
  int32 itemsPerPage = 5;
}
```

**Mensaje de respuesta:**

```protobuf
message OrderHistoryReply {
  oneof response {
    OrdersHistoryData data = 1;
    Error error = 2;
  }
}

message OrdersHistoryData {
  int32 arrayTotal = 1;
  int32 pageNumber = 2;
  int32 itemsPerPage = 3;
  repeated HistoryData history_data = 4;
}
```

---

## 🔽 Parámetros de entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `from_dt` | `datetime` (obligatorio) | Hora inicial de la consulta del historial (hora del servidor). |
| `to_dt` | `datetime` (obligatorio) | Hora final de la consulta del historial (hora del servidor). |
| `sort_mode` | `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE` (enum) | Modo de ordenación (por hora o por ID de ticket). |
| `page_number` | `int` (opcional) | Número de página para la paginación (predeterminado: 0). |
| `items_per_page` | `int` (opcional) | Elementos por página (predeterminado: 0 = todos). |
| `deadline` | `datetime` (opcional) | Plazo límite para la llamada gRPC (fecha y hora UTC). |
| `cancellation_event` | `asyncio.Event` (opcional) | Evento para cancelar la operación. |

**Uso:**

```python
from datetime import datetime, timedelta, timezone
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2

# Obtener el historial de los últimos 7 días
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=7)

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
    page_number=0,
    items_per_page=100
)
```

---

## ⬆️ Salida - `OrdersHistoryData`

| Campo | Tipo | Tipo de Python | Descripción |
|---|---|---|---|
| `arrayTotal` | `int32` | `int` | Número total de registros (todas las páginas). |
| `pageNumber` | `int32` | `int` | Número de la página actual. |
| `itemsPerPage` | `int32` | `int` | Número de elementos por página. |
| `history_data` | `repeated HistoryData` | `list[HistoryData]` | Lista de registros históricos de órdenes y operaciones. |
| `next_page_token` | `string` | `str` | Cursor para la página siguiente (vacío si es la última). |

**Cada elemento `HistoryData` contiene:**

| Campo | Tipo | Descripción |
|---|---|---|
| `index` | `uint32` | Índice dentro del conjunto de resultados. |
| `history_order` | `OrderHistoryData` | Detalles de la orden (si corresponde). |
| `history_deal` | `DealHistoryData` | Detalles de la operación (si corresponde). |

**Campos de `OrderHistoryData`:**

- `ticket` (uint64) - Número de ticket de la orden.
- `setup_time` (Timestamp) - Hora de creación de la orden.
- `done_time` (Timestamp) - Hora de ejecución de la orden.
- `state` (BMT5_ENUM_ORDER_STATE) - Estado de la orden.
- `price_current` (double) - Precio actual.
- `price_open` (double) - Precio de apertura de la orden.
- `stop_limit` (double) - Precio Stop Limit.
- `stop_loss` (double) - Nivel de Stop Loss.
- `take_profit` (double) - Nivel de Take Profit.
- `volume_current` (double) - Volumen actual.
- `volume_initial` (double) - Volumen inicial.
- `magic_number` (int64) - ID del Asesor Experto.
- `type` (BMT5_ENUM_ORDER_TYPE) - Tipo de orden.
- `time_expiration` (Timestamp) - Hora de vencimiento de la orden.
- `type_filling` (BMT5_ENUM_ORDER_TYPE_FILLING) - Tipo de ejecución.
- `type_time` (BMT5_ENUM_ORDER_TYPE_TIME) - Tipo de vigencia de la orden.
- `position_id` (uint64) - Ticket de la posición.
- `symbol` (string) - Nombre del símbolo.
- `external_id` (string) - ID externo.
- `comment` (string) - Comentario de la orden.
- `account_login` (int64) - Login de la cuenta.
- `setup_time_utc` (Timestamp) - Hora de creación de la orden (UTC).
- `done_time_utc` (Timestamp) - Hora de ejecución de la orden (UTC).
- `time_expiration_utc` (Timestamp) - Hora de vencimiento de la orden (UTC).

**Campos de `DealHistoryData`:**

- `ticket` (uint64) - Número de ticket de la operación.
- `profit` (double) - Beneficio de la operación.
- `commission` (double) - Comisión.
- `fee` (double) - Cargo adicional.
- `price` (double) - Precio de la operación.
- `stop_loss` (double) - Nivel de Stop Loss en el momento de la operación.
- `take_profit` (double) - Nivel de Take Profit en el momento de la operación.
- `swap` (double) - Swap.
- `volume` (double) - Volumen de la operación.
- `entry_type` (BMT5_ENUM_DEAL_ENTRY_TYPE) - Tipo de entrada de la operación.
- `time` (Timestamp) - Hora de la operación.
- `type` (BMT5_ENUM_DEAL_TYPE) - Tipo de operación.
- `reason` (BMT5_ENUM_DEAL_REASON) - Motivo de la operación.
- `position_id` (uint64) - ID de la posición.
- `comment` (string) - Comentario de la operación.
- `symbol` (string) - Nombre del símbolo.
- `external_id` (string) - ID externo.
- `account_login` (int64) - Login de la cuenta.
- `time_utc` (Timestamp) - Hora de la operación (UTC).
- `order` (uint64) - Ticket de la orden que generó la operación.
- `magic` (int64) - Número mágico del Asesor Experto.

---

## 🧱 Enums relacionados (de proto)

### `BMT5_ENUM_ORDER_HISTORY_SORT_TYPE`

Definido en `mt5-term-api-account-helper.proto`.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_SORT_BY_OPEN_TIME_ASC` | 0 | Ordenar por hora de apertura ascendente. |
| `BMT5_SORT_BY_OPEN_TIME_DESC` | 1 | Ordenar por hora de apertura descendente. |
| `BMT5_SORT_BY_CLOSE_TIME_ASC` | 2 | Ordenar por hora de cierre ascendente. |
| `BMT5_SORT_BY_CLOSE_TIME_DESC` | 3 | Ordenar por hora de cierre descendente. |
| `BMT5_SORT_BY_ORDER_TICKET_ID_ASC` | 4 | Ordenar por ID de ticket ascendente. |
| `BMT5_SORT_BY_ORDER_TICKET_ID_DESC` | 5 | Ordenar por ID de ticket descendente. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=pb2.BMT5_SORT_BY_CLOSE_TIME_DESC
)
```

### `BMT5_ENUM_ORDER_STATE`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `OrderHistoryData` para indicar el estado de la orden.

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

# Comprobar el estado de la orden en el historial
for item in data.history_data:
    if item.history_order.state == pb2.BMT5_ORDER_STATE_FILLED:
        print(f"La orden {item.history_order.ticket} se ejecutó")
```

### `BMT5_ENUM_ORDER_TYPE`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `OrderHistoryData` para indicar el tipo de orden.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_TYPE_BUY` | 0 | Orden de compra a mercado. |
| `BMT5_ORDER_TYPE_SELL` | 1 | Orden de venta a mercado. |
| `BMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit. |
| `BMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit. |
| `BMT5_ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop. |
| `BMT5_ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop. |
| `BMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden Buy Stop Limit pendiente. |
| `BMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden Sell Stop Limit pendiente. |
| `BMT5_ORDER_TYPE_CLOSE_BY` | 8 | Cierre mediante una posición opuesta. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Filtrar órdenes de compra
for item in data.history_data:
    if item.history_order.type == pb2.BMT5_ORDER_TYPE_BUY:
        print(f"Orden de compra: {item.history_order.ticket}")
```

### `BMT5_ENUM_ORDER_TYPE_FILLING`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `OrderHistoryData` para indicar el tipo de ejecución de la orden.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_FILLING_FOK` | 0 | Fill or Kill (ejecutar por completo o cancelar). |
| `BMT5_ORDER_FILLING_IOC` | 1 | Immediate or Cancel (ejecutar inmediatamente o cancelar). |
| `BMT5_ORDER_FILLING_RETURN` | 2 | Return. |
| `BMT5_ORDER_FILLING_BOC` | 3 | Book or Cancel (colocar en el libro de órdenes o cancelar). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de ejecución
for item in data.history_data:
    if item.history_order.type_filling == pb2.BMT5_ORDER_FILLING_FOK:
        print(f"Orden FOK: {item.history_order.ticket}")
```

### `BMT5_ENUM_ORDER_TYPE_TIME`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `OrderHistoryData` para indicar el tipo de vigencia de la orden.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_ORDER_TIME_GTC` | 0 | Good Till Cancelled (válida hasta su cancelación). |
| `BMT5_ORDER_TIME_DAY` | 1 | Good Till Day (válida hasta el final del día de trading actual). |
| `BMT5_ORDER_TIME_SPECIFIED` | 2 | Good Till Specified Time (válida hasta la fecha y hora especificadas). |
| `BMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Good Till Specified Day (válida hasta el día especificado). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de vigencia
for item in data.history_data:
    if item.history_order.type_time == pb2.BMT5_ORDER_TIME_GTC:
        print(f"Orden GTC: {item.history_order.ticket}")
```

### `BMT5_ENUM_DEAL_ENTRY_TYPE`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `DealHistoryData` para indicar el tipo de entrada de la operación.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_DEAL_ENTRY_IN` | 0 | Entrada (apertura). |
| `BMT5_DEAL_ENTRY_OUT` | 1 | Salida (cierre). |
| `BMT5_DEAL_ENTRY_INOUT` | 2 | Reversión de posición. |
| `BMT5_DEAL_ENTRY_OUT_BY` | 3 | Cierre mediante una posición opuesta. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el tipo de entrada de la operación
for item in data.history_data:
    if item.history_deal.entry_type == pb2.BMT5_DEAL_ENTRY_IN:
        print(f"Operación de apertura: {item.history_deal.ticket}")
```

### `BMT5_ENUM_DEAL_TYPE`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `DealHistoryData` para indicar el tipo de operación.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_DEAL_TYPE_BUY` | 0 | Compra. |
| `BMT5_DEAL_TYPE_SELL` | 1 | Venta. |
| `BMT5_DEAL_TYPE_BALANCE` | 2 | Saldo. |
| `BMT5_DEAL_TYPE_CREDIT` | 3 | Crédito. |
| `BMT5_DEAL_TYPE_CHARGE` | 4 | Cargo adicional. |
| `BMT5_DEAL_TYPE_CORRECTION` | 5 | Corrección. |
| `BMT5_DEAL_TYPE_BONUS` | 6 | Bonificación. |
| `BMT5_DEAL_TYPE_COMMISSION` | 7 | Comisión adicional. |
| `BMT5_DEAL_TYPE_COMMISSION_DAILY` | 8 | Comisión diaria. |
| `BMT5_DEAL_TYPE_COMMISSION_MONTHLY` | 9 | Comisión mensual. |
| `BMT5_DEAL_TYPE_COMMISSION_AGENT_DAILY` | 10 | Comisión diaria del agente. |
| `BMT5_DEAL_TYPE_COMMISSION_AGENT_MONTHLY` | 11 | Comisión mensual del agente. |
| `BMT5_DEAL_TYPE_INTEREST` | 12 | Intereses (cargo por intereses). |
| `BMT5_DEAL_TYPE_BUY_CANCELED` | 13 | Operación de compra cancelada. |
| `BMT5_DEAL_TYPE_SELL_CANCELED` | 14 | Operación de venta cancelada. |
| `BMT5_DEAL_DIVIDEND` | 15 | Dividendo. |
| `BMT5_DEAL_DIVIDEND_FRANKED` | 16 | Dividendo con crédito fiscal. |
| `BMT5_DEAL_TAX` | 17 | Impuesto. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Filtrar operaciones de compra/venta
for item in data.history_data:
    if item.history_deal.type == pb2.BMT5_DEAL_TYPE_BUY:
        print(f"Operación de compra: {item.history_deal.ticket}")
    elif item.history_deal.type == pb2.BMT5_DEAL_TYPE_BALANCE:
        print(f"Operación de saldo: {item.history_deal.ticket}")
```

### `BMT5_ENUM_DEAL_REASON`

Definido en `mt5-term-api-account-helper.proto`. Se utiliza en `DealHistoryData` para indicar el motivo de la operación.

| Constante | Valor | Descripción |
|---|---:|---|
| `BMT5_DEAL_REASON_CLIENT` | 0 | Operación realizada manualmente. |
| `BMT5_DEAL_REASON_MOBILE` | 1 | Operación realizada desde un dispositivo móvil. |
| `BMT5_DEAL_REASON_WEB` | 2 | Operación realizada desde la plataforma web. |
| `BMT5_DEAL_REASON_EXPERT` | 3 | Operación realizada por un Asesor Experto. |
| `BMT5_DEAL_REASON_SL` | 4 | Operación realizada debido a un Stop Loss. |
| `BMT5_DEAL_REASON_TP` | 5 | Operación realizada debido a un Take Profit. |
| `BMT5_DEAL_REASON_SO` | 6 | Operación realizada debido a un Stop Out. |
| `BMT5_DEAL_REASON_ROLLOVER` | 7 | Operación por traspaso al día siguiente (rollover). |
| `BMT5_DEAL_REASON_VMARGIN` | 8 | Operación debido al margen de variación. |
| `BMT5_DEAL_REASON_SPLIT` | 9 | Operación debido a una división de acciones (split). |
| `BMT5_DEAL_REASON_CORPORATE_ACTION` | 10 | Operación debido a una acción corporativa. |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as pb2

# Comprobar el motivo de la operación
for item in data.history_data:
    if item.history_deal.reason == pb2.BMT5_DEAL_REASON_SL:
        print(f"Operación por Stop Loss: {item.history_deal.ticket}")
    elif item.history_deal.reason == pb2.BMT5_DEAL_REASON_EXPERT:
        print(f"Operación del Asesor Experto: {item.history_deal.ticket}")
```

---

## 🧩 Notas y consejos

- **Hora del servidor:** los parámetros `from_dt` y `to_dt` utilizan la hora del servidor, no UTC.
- **Paginación:** utiliza `page_number` y `items_per_page` para conjuntos de datos grandes. Establece `items_per_page=0` para obtener todos los resultados.
- **Recuento total:** el campo `arrayTotal` muestra el número total de registros de todas las páginas.
- **Reconexión automática:** protección integrada contra errores gRPC transitorios.
- **Conexión necesaria:** llama primero a `connect_by_host_port()` o `connect_by_server_name()`.
- **Seguridad de los hilos:** se puede llamar de forma segura y simultánea desde varias tareas de asyncio.
- **Gestión de UUID:** el UUID de la instancia del terminal se genera automáticamente en el servidor si no se proporciona. 

  Para controlarlo explícitamente (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener el historial de los últimos 7 días

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
        # Últimos 7 días
        to_dt = datetime.now(timezone.utc)
        from_dt = to_dt - timedelta(days=7)

        data = await account.order_history(
            from_dt=from_dt,
            to_dt=to_dt,
            sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
            items_per_page=100
        )

        print(f"Total de registros: {data.arrayTotal}")
        print(f"Registros devueltos: {len(data.history_data)}")

        for item in data.history_data:
            if item.history_deal:
                deal = item.history_deal
                print(f"Operación #{deal.ticket}: ${deal.profit:.2f}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 2) Obtener el historial mediante paginación

```python
async def get_all_history_paginated(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    page_size: int = 100
):
    """Obtener todos los registros del historial mediante paginación"""
    all_records = []
    page = 0

    while True:
        data = await account.order_history(
            from_dt=from_dt,
            to_dt=to_dt,
            sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_ASC,
            page_number=page,
            items_per_page=page_size
        )

        print(f"[OK] Página {page + 1}: {len(data.history_data)} registros")

        all_records.extend(data.history_data)

        # Comprobar si se han obtenido todos los registros
        if len(all_records) >= data.arrayTotal:
            break

        page += 1

    print(f"[OK] Total de registros recuperados: {len(all_records)}")
    return all_records


# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
history = await get_all_history_paginated(account, from_dt, to_dt)
```

### 3) Calcular el beneficio total de un período

```python
async def calculate_period_profit(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> float:
    """Calcular el beneficio/pérdida total de un período"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0  # Obtener todos
    )

    total_profit = 0.0
    for item in data.history_data:
        if item.history_deal:
            total_profit += item.history_deal.profit

    print(f"Beneficio total ({from_dt.date()} a {to_dt.date()}): ${total_profit:+.2f}")
    return total_profit


# Uso:
from_dt = datetime(2024, 1, 1)
to_dt = datetime(2024, 1, 31)
profit = await calculate_period_profit(account, from_dt, to_dt)
```

### 4) Obtener el historial de trading de hoy

```python
async def get_today_history(account: MT5Account):
    """Obtener todas las operaciones de hoy"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    data = await account.order_history(
        from_dt=today_start,
        to_dt=now,
        sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC
    )

    print(f"\nActividad de trading de hoy:")
    print(f"Total de registros: {data.arrayTotal}")

    for item in data.history_data:
        if item.history_deal:
            deal = item.history_deal
            time = deal.time.ToDatetime()
            print(f"  {time.strftime('%H:%M:%S')} - "
                  f"#{deal.ticket} {deal.symbol}: ${deal.profit:+.2f}")

    return data


# Uso:
await get_today_history(account)
```

### 5) Exportar el historial a CSV

```python
import csv


async def export_history_to_csv(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime,
    filename: str = "order_history.csv"
):
    """Exportar el historial de órdenes a un archivo CSV"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Ticket', 'Hora', 'Símbolo', 'Tipo', 'Volumen',
            'Precio', 'Beneficio', 'Comisión', 'Swap'
        ])

        for item in data.history_data:
            if item.history_deal:
                deal = item.history_deal
                time = deal.time.ToDatetime()
                writer.writerow([
                    deal.ticket,
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    deal.symbol,
                    deal.type,
                    deal.volume,
                    deal.price,
                    deal.profit,
                    deal.commission,
                    deal.swap
                ])

    print(f"[OK] Se exportaron {data.arrayTotal} registros a {filename}")


# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
await export_history_to_csv(account, from_dt, to_dt)
```

### 6) Obtener las operaciones ganadoras y perdedoras

```python
async def analyze_win_loss(
    account: MT5Account,
    from_dt: datetime,
    to_dt: datetime
) -> dict:
    """Analizar las operaciones ganadoras y perdedoras"""
    data = await account.order_history(
        from_dt=from_dt,
        to_dt=to_dt,
        items_per_page=0
    )

    wins = 0
    losses = 0
    total_win_profit = 0.0
    total_loss_profit = 0.0

    for item in data.history_data:
        if item.history_deal:
            profit = item.history_deal.profit
            if profit > 0:
                wins += 1
                total_win_profit += profit
            elif profit < 0:
                losses += 1
                total_loss_profit += profit

    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

    result = {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "total_win_profit": total_win_profit,
        "total_loss_profit": total_loss_profit,
        "net_profit": total_win_profit + total_loss_profit
    }

    print(f"\nEstadísticas de trading:")
    print(f"  Operaciones totales: {total_trades}")
    print(f"  Ganadoras: {wins} ({win_rate:.1f}%)")
    print(f"  Perdedoras: {losses}")
    print(f"  Beneficio de operaciones ganadoras: ${total_win_profit:.2f}")
    print(f"  Pérdida de operaciones perdedoras: ${total_loss_profit:.2f}")
    print(f"  Beneficio neto: ${result['net_profit']:+.2f}")

    return result


# Uso:
from_dt = datetime.now(timezone.utc) - timedelta(days=30)
to_dt = datetime.now(timezone.utc)
stats = await analyze_win_loss(account, from_dt, to_dt)
```

---

## Patrones de uso comunes

### Obtener el historial de un símbolo específico

```python
async def get_symbol_history(
    account: MT5Account,
    symbol: str,
    from_dt: datetime,
    to_dt: datetime
):
    """Filtrar el historial por símbolo"""
    data = await account.order_history(from_dt=from_dt, to_dt=to_dt)

    symbol_deals = [
        item for item in data.history_data
        if item.history_deal and item.history_deal.symbol == symbol
    ]

    return symbol_deals
```

### Calcular el beneficio diario

```python
from collections import defaultdict


async def get_daily_profit(account: MT5Account, from_dt: datetime, to_dt: datetime):
    """Calcular el beneficio por día"""
    data = await account.order_history(from_dt=from_dt, to_dt=to_dt, items_per_page=0)

    daily_profit = defaultdict(float)

    for item in data.history_data:
        if item.history_deal:
            deal = item.history_deal
            date = deal.time.ToDatetime().date()
            daily_profit[date] += deal.profit

    return dict(daily_profit)
```

---

## 📚 Véase también

- [positions_history](./positions_history.md) - Obtener el historial de posiciones cerradas.
- [opened_orders](./opened_orders.md) - Obtener las órdenes abiertas actualmente.
- [positions_total](./positions_total.md) - Obtener el número de posiciones abiertas.