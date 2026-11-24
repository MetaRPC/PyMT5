

# Transmisión de eventos de trading

> **Solicitud:** suscribirse a todos los eventos relacionados con el trading: órdenes, operaciones y posiciones.

## Información de la API

- **API de Python:** `MT5Account.on_trade(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.SubscriptionService`
- **Definición Proto:** `OnTrade` (definido en `mt5-term-api-subscriptions.proto`)

### RPC

- **Servicio:** `mt5_term_api.SubscriptionService`
- **Método:** `OnTrade(OnTradeRequest) -> stream OnTradeReply`
- **Cliente de bajo nivel (generado):** `SubscriptionServiceStub.OnTrade(request, metadata)`

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def on_trade(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Se suscribe a todos los eventos relacionados con el trading: órdenes, operaciones y posiciones.

        Yields:
            OnTradeData: Datos de eventos de trading.
        """
```

**Mensaje de solicitud:**

```protobuf
message OnTradeRequest {
  // Sin parámetros: se suscribe a todos los eventos de trading
}
```

## 💬 Lo esencial

- **Qué es:** flujo en tiempo real de toda la actividad de trading de la cuenta.
- **Por qué lo necesitas:** supervisar operaciones, detectar cambios en las posiciones y seguir la ejecución de órdenes.
- **Basado en eventos:** las actualizaciones se activan inmediatamente cuando se producen eventos de trading.

---

## 🎯 Propósito

Utilízalo para:

- Supervisar toda la actividad de trading en tiempo real.
- Detectar cuándo se abren o cierran posiciones.
- Seguir el ciclo de vida de las órdenes pendientes.
- Crear sistemas de registro de eventos de trading.
- Implementar notificaciones de trading.
- Sincronizar el estado local con MT5.

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la transmisión (opcional) |

---

## ⬆️ Salida: generador asíncrono

Devuelve un generador asíncrono que produce objetos `OnTradeData`.

**Campos de `OnTradeData`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `type` | `int` | Tipo de evento |
| `event_data` | `OnTradeEventData` | Información detallada del evento |
| `account_info` | `OnEventAccountInfo` | Estado actual de la cuenta |
| `terminal_instance_guid_id` | `str` | Identificador de la instancia del terminal |

**Campos de `OnTradeEventData` (todos son listas/repeated):**

| Campo | Tipo | Descripción |
|---|---|---|
| `new_orders` | `repeated OnTradeOrderInfo` | Nuevas órdenes pendientes creadas |
| `disappeared_orders` | `repeated OnTradeOrderInfo` | Órdenes pendientes eliminadas |
| `state_changed_orders` | `repeated OnTradeOrderStateChange` | Órdenes cuyo estado ha cambiado |
| `new_positions` | `repeated OnTradePositionInfo` | Nuevas posiciones abiertas |
| `disappeared_positions` | `repeated OnTradePositionInfo` | Posiciones cerradas |
| `updated_positions` | `repeated OnTradePositionUpdate` | Posiciones modificadas |
| `new_history_orders` | `repeated OnTradeHistoryOrderInfo` | Nuevas órdenes en el historial |
| `disappeared_history_orders` | `repeated OnTradeHistoryOrderInfo` | Órdenes eliminadas del historial |
| `updated_history_orders` | `repeated OnTradeHistoryOrderUpdate` | Órdenes del historial actualizadas |
| `new_history_deals` | `repeated OnTradeHistoryDealInfo` | Nuevas operaciones en el historial |
| `disappeared_history_deals` | `repeated OnTradeHistoryDealInfo` | Operaciones eliminadas del historial |
| `updated_history_deals` | `repeated OnTradeHistoryDealUpdate` | Operaciones del historial actualizadas |

**Estructura y uso de ENUMs:**

```text
OnTradeData
├── type (MT5_SUB_ENUM_EVENT_GROUP_TYPE) - Tipo de grupo de eventos
├── event_data (OnTradeEventData)
│   ├── new_positions (list[OnTradePositionInfo])
│   │   └── Utiliza: SUB_ENUM_POSITION_TYPE, SUB_ENUM_POSITION_REASON
│   ├── disappeared_positions (list[OnTradePositionInfo])
│   │   └── Utiliza: SUB_ENUM_POSITION_TYPE, SUB_ENUM_POSITION_REASON
│   ├── new_orders (list[OnTradeOrderInfo])
│   │   └── Utiliza: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │                SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │                SUB_ENUM_ORDER_REASON
│   ├── disappeared_orders (list[OnTradeOrderInfo])
│   │   └── Utiliza: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │                SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │                SUB_ENUM_ORDER_REASON
│   ├── new_history_orders (list[OnTradeHistoryOrderInfo])
│   │   └── Utiliza: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │                SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │                SUB_ENUM_DEAL_REASON
│   ├── disappeared_history_orders (list[OnTradeHistoryOrderInfo])
│   │   └── Utiliza: SUB_ENUM_ORDER_TYPE, SUB_ENUM_ORDER_STATE,
│   │                SUB_ENUM_ORDER_TYPE_TIME, SUB_ENUM_ORDER_TYPE_FILLING,
│   │                SUB_ENUM_DEAL_REASON
│   ├── new_history_deals (list[OnTradeHistoryDealInfo])
│   │   └── Utiliza: SUB_ENUM_DEAL_TYPE, SUB_ENUM_DEAL_ENTRY, SUB_ENUM_DEAL_REASON
│   └── disappeared_history_deals (list[OnTradeHistoryDealInfo])
│       └── Utiliza: SUB_ENUM_DEAL_TYPE, SUB_ENUM_DEAL_ENTRY, SUB_ENUM_DEAL_REASON
├── account_info (OnEventAccountInfo)
└── terminal_instance_guid_id (str)
```

---

**Enum del tipo de grupo de eventos (`MT5_SUB_ENUM_EVENT_GROUP_TYPE`):**

Se utiliza en el campo `OnTradeData.type`:

| Nombre | Valor | Descripción |
|---|---:|---|
| `OrderProfit` | 0 | Evento de beneficio de una orden |
| `OrderUpdate` | 1 | Evento de actualización de una orden |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.OrderProfit   # = 0
```

---

**Enums utilizados en las estructuras anidadas:**

Los siguientes enums se utilizan en los tipos de mensajes anidados dentro de `OnTradeEventData`:

| Estructura anidada | Campos donde se utiliza | Enums utilizados |
|---|---|---|
| `OnTradePositionInfo` | `new_positions`, `disappeared_positions` | `SUB_ENUM_POSITION_TYPE`, `SUB_ENUM_POSITION_REASON` |
| `OnTradeOrderInfo` | `new_orders`, `disappeared_orders` | `SUB_ENUM_ORDER_TYPE`, `SUB_ENUM_ORDER_STATE`, `SUB_ENUM_ORDER_TYPE_TIME`, `SUB_ENUM_ORDER_TYPE_FILLING`, `SUB_ENUM_ORDER_REASON` |
| `OnTradeHistoryOrderInfo` | `new_history_orders`, `disappeared_history_orders` | `SUB_ENUM_ORDER_TYPE`, `SUB_ENUM_ORDER_STATE`, `SUB_ENUM_ORDER_TYPE_TIME`, `SUB_ENUM_ORDER_TYPE_FILLING`, `SUB_ENUM_DEAL_REASON` |
| `OnTradeHistoryDealInfo` | `new_history_deals`, `disappeared_history_deals` | `SUB_ENUM_DEAL_TYPE`, `SUB_ENUM_DEAL_ENTRY`, `SUB_ENUM_DEAL_REASON` |

**Enum del tipo de posición (`SUB_ENUM_POSITION_TYPE`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_POSITION_TYPE_BUY` | 0 | Posición de compra |
| `SUB_POSITION_TYPE_SELL` | 1 | Posición de venta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
```

**Enum del motivo de la posición (`SUB_ENUM_POSITION_REASON`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_POSITION_REASON_CLIENT` | 0 | Posición abierta desde el terminal de escritorio |
| `SUB_POSITION_REASON_MOBILE` | 1 | Posición abierta desde la aplicación móvil |
| `SUB_POSITION_REASON_WEB` | 2 | Posición abierta desde el terminal web |
| `SUB_POSITION_REASON_EXPERT` | 3 | Posición abierta por un Asesor Experto |
| `SUB_POSITION_REASON_SL` | 4 | Posición cerrada por Stop Loss |
| `SUB_POSITION_REASON_TP` | 5 | Posición cerrada por Take Profit |
| `SUB_POSITION_REASON_SO` | 6 | Posición cerrada por Stop Out |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_POSITION_REASON_CLIENT  # = 0
```

**Enum del tipo de orden (`SUB_ENUM_ORDER_TYPE`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_ORDER_TYPE_BUY` | 0 | Orden de compra a mercado |
| `SUB_ORDER_TYPE_SELL` | 1 | Orden de venta a mercado |
| `SUB_ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit |
| `SUB_ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit |
| `SUB_ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop |
| `SUB_ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop |
| `SUB_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit |
| `SUB_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit |
| `SUB_ORDER_TYPE_CLOSE_BY` | 8 | Cierre mediante una posición opuesta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_ORDER_TYPE_BUY   # = 0
```

**Enum del estado de la orden (`SUB_ENUM_ORDER_STATE`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_ORDER_STATE_STARTED` | 0 | Orden comprobada, pero todavía no aceptada |
| `SUB_ORDER_STATE_PLACED` | 1 | Orden aceptada |
| `SUB_ORDER_STATE_CANCELED` | 2 | Orden cancelada por el cliente |
| `SUB_ORDER_STATE_PARTIAL` | 3 | Orden ejecutada parcialmente |
| `SUB_ORDER_STATE_FILLED` | 4 | Orden ejecutada por completo |
| `SUB_ORDER_STATE_REJECTED` | 5 | Orden rechazada |
| `SUB_ORDER_STATE_EXPIRED` | 6 | Orden caducada |
| `SUB_ORDER_STATE_REQUEST_ADD` | 7 | Orden en proceso de registro |
| `SUB_ORDER_STATE_REQUEST_MODIFY` | 8 | Orden en proceso de modificación |
| `SUB_ORDER_STATE_REQUEST_CANCEL` | 9 | Orden en proceso de eliminación |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_ORDER_STATE_STARTED   # = 0
```

**Enum del tipo de operación (`SUB_ENUM_DEAL_TYPE`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_DEAL_TYPE_BUY` | 0 | Operación de compra |
| `SUB_DEAL_TYPE_SELL` | 1 | Operación de venta |
| `SUB_DEAL_TYPE_BALANCE` | 2 | Operación de saldo |
| `SUB_DEAL_TYPE_CREDIT` | 3 | Operación de crédito |
| `SUB_DEAL_TYPE_CHARGE` | 4 | Cargo adicional |
| `SUB_DEAL_TYPE_CORRECTION` | 5 | Corrección |
| `SUB_DEAL_TYPE_BONUS` | 6 | Bono |
| `SUB_DEAL_TYPE_COMMISSION` | 7 | Comisión |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_DEAL_TYPE_BUY   # = 0
```

**Enum del tipo de tiempo de la orden (`SUB_ENUM_ORDER_TYPE_TIME`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_ORDER_TIME_GTC` | 0 | Válida hasta su cancelación |
| `SUB_ORDER_TIME_DAY` | 1 | Válida hasta el final del día de trading actual |
| `SUB_ORDER_TIME_SPECIFIED` | 2 | Válida hasta la fecha especificada |
| `SUB_ORDER_TIME_SPECIFIED_DAY` | 3 | Válida hasta el día especificado |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_ORDER_TIME_GTC   # = 0
```

**Enum del tipo de ejecución de la orden (`SUB_ENUM_ORDER_TYPE_FILLING`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_ORDER_FILLING_FOK` | 0 | Ejecutar o cancelar (Fill or Kill) |
| `SUB_ORDER_FILLING_IOC` | 1 | Ejecución inmediata o cancelación (Immediate or Cancel) |
| `SUB_ORDER_FILLING_BOC` | 2 | Registrar en el libro o cancelar (Book or Cancel) |
| `SUB_ORDER_FILLING_RETURN` | 3 | Devolver |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_ORDER_FILLING_FOK   # = 0
```

**Enum del motivo de la orden (`SUB_ENUM_ORDER_REASON`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_ORDER_REASON_CLIENT` | 0 | Orden realizada desde el terminal de escritorio |
| `SUB_ORDER_REASON_MOBILE` | 2 | Orden realizada desde la aplicación móvil |
| `SUB_ORDER_REASON_WEB` | 3 | Orden realizada desde el terminal web |
| `SUB_ORDER_REASON_EXPERT` | 4 | Orden realizada por un Asesor Experto |
| `SUB_ORDER_REASON_SL` | 5 | Orden activada por Stop Loss |
| `SUB_ORDER_REASON_TP` | 6 | Orden activada por Take Profit |
| `SUB_ORDER_REASON_SO` | 7 | Orden activada por Stop Out |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_ORDER_REASON_CLIENT   # = 0
```

**Enum del tipo de entrada de la operación (`SUB_ENUM_DEAL_ENTRY`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_DEAL_ENTRY_IN` | 0 | Entrada al mercado |
| `SUB_DEAL_ENTRY_OUT` | 1 | Salida del mercado |
| `SUB_DEAL_ENTRY_INOUT` | 2 | Reversión de posición |
| `SUB_DEAL_ENTRY_OUT_BY` | 3 | Cierre mediante una posición opuesta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_DEAL_ENTRY_IN   # = 0
```

**Enum del motivo de la operación (`SUB_ENUM_DEAL_REASON`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_DEAL_REASON_CLIENT` | 0 | Operación realizada desde el terminal de escritorio |
| `SUB_DEAL_REASON_MOBILE` | 1 | Operación realizada desde la aplicación móvil |
| `SUB_DEAL_REASON_WEB` | 2 | Operación realizada desde el terminal web |
| `SUB_DEAL_REASON_EXPERT` | 3 | Operación realizada por un Asesor Experto |
| `SUB_DEAL_REASON_SL` | 4 | Operación causada por Stop Loss |
| `SUB_DEAL_REASON_TP` | 5 | Operación causada por Take Profit |
| `SUB_DEAL_REASON_SO` | 6 | Operación causada por Stop Out |
| `SUB_DEAL_REASON_ROLLOVER` | 7 | Operación causada por rollover |
| `SUB_DEAL_REASON_VMARGIN` | 8 | Operación causada por el margen de variación |
| `SUB_DEAL_REASON_SPLIT` | 9 | Operación causada por un desdoblamiento |
| `SUB_DEAL_REASON_CORPORATE_ACTION` | 10 | Operación causada por una acción corporativa |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_DEAL_REASON_CLIENT   # = 0
```

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OnTrade - Cómo funciona](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de transmisión de `MT5Account` incorporan protección contra errores gRPC transitorios, con reconexión automática mediante `execute_stream_with_reconnect`.
- **Generador asíncrono:** el método devuelve un generador asíncrono; utiliza `async for` para consumir los datos.
- **Sin parámetros:** este flujo se suscribe automáticamente a TODOS los eventos de trading.
- **Cobertura completa:** realiza un seguimiento de órdenes, posiciones y operaciones, tanto activas como históricas.
- **Basado en eventos:** las actualizaciones llegan inmediatamente cuando se producen eventos, no de forma periódica.
- **Múltiples listas:** cada actualización puede contener varios tipos de eventos simultáneamente.
- **Gestión de recursos:** cancela siempre las transmisiones cuando hayas terminado para liberar recursos.

---

## 🔗 Ejemplos de uso

### 1) Monitorizar todos los eventos de trading

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_trades():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Nuevas posiciones
            if event.new_positions:
                for pos in event.new_positions:
                    print(f"[NUEVA POSICIÓN] #{pos.index}")

            # Posiciones cerradas
            if event.disappeared_positions:
                for pos in event.disappeared_positions:
                    print(f"[POSICIÓN CERRADA] #{pos.index}")

            # Posiciones actualizadas
            if event.updated_positions:
                for pos in event.updated_positions:
                    print(f"[POSICIÓN ACTUALIZADA] #{pos.index}")

            # Nuevas órdenes pendientes
            if event.new_orders:
                for order in event.new_orders:
                    print(f"[NUEVA ORDEN] #{order.index}")

            # Órdenes pendientes eliminadas
            if event.disappeared_orders:
                for order in event.disappeared_orders:
                    print(f"[ORDEN ELIMINADA] #{order.index}")

            # Información de la cuenta
            if trade_data.account_info:
                acc = trade_data.account_info
                print(f"[CUENTA] Saldo: ${acc.balance:.2f}, "
                      f"Equity: ${acc.equity:.2f}\n")

    except KeyboardInterrupt:
        print("Deteniendo el monitor de trading...")

    finally:
        await account.channel.close()


asyncio.run(monitor_trades())
```

### 2) Registro de eventos de trading

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def log_trade_events():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    event_count = 0

    try:
        async for trade_data in account.on_trade():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event = trade_data.event_data

            # Registrar nuevas posiciones
            for pos in event.new_positions:
                event_count += 1
                print(f"[{timestamp}] NUEVA_POSICIÓN | Índice: {pos.index}")

            # Registrar posiciones cerradas
            for pos in event.disappeared_positions:
                event_count += 1
                print(f"[{timestamp}] POSICIÓN_CERRADA | Índice: {pos.index}")

            # Registrar posiciones actualizadas
            for pos in event.updated_positions:
                event_count += 1
                print(f"[{timestamp}] POSICIÓN_ACTUALIZADA | Índice: {pos.index}")

            # Registrar nuevas órdenes pendientes
            for order in event.new_orders:
                event_count += 1
                print(f"[{timestamp}] NUEVA_ORDEN | Índice: {order.index}")

            # Registrar cambios en el estado de las órdenes
            for order in event.state_changed_orders:
                event_count += 1
                print(f"[{timestamp}] CAMBIO_ESTADO_ORDEN | Índice: {order.index}")

            # Registrar nuevas operaciones
            for deal in event.new_history_deals:
                event_count += 1
                print(f"[{timestamp}] NUEVA_OPERACIÓN | Índice: {deal.index}")

            if event_count % 10 == 0:
                print(f"\n--- Total de eventos registrados: {event_count} ---\n")

    except KeyboardInterrupt:
        print(f"\nDeteniendo el registrador. Total de eventos: {event_count}")

    finally:
        await account.channel.close()


asyncio.run(log_trade_events())
```

### 3) Seguimiento de apertura y cierre de posiciones

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def track_position_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    active_positions = set()
    total_opened = 0
    total_closed = 0

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Seguir las nuevas posiciones
            for pos in event.new_positions:
                active_positions.add(pos.index)
                total_opened += 1
                print(f"[ABIERTA] Posición #{pos.index}")
                print(f"   Activas: {len(active_positions)}, "
                      f"Total abiertas: {total_opened}")

            # Seguir las posiciones cerradas
            for pos in event.disappeared_positions:
                if pos.index in active_positions:
                    active_positions.remove(pos.index)
                total_closed += 1
                print(f"[CERRADA] Posición #{pos.index}")
                print(f"   Activas: {len(active_positions)}, "
                      f"Total cerradas: {total_closed}")

            # Mostrar el estado actual
            if event.new_positions or event.disappeared_positions:
                print(f"\n[ESTADÍSTICAS] Estado actual:")
                print(f"   Posiciones activas: {len(active_positions)}")
                print(f"   Total abiertas: {total_opened}")
                print(f"   Total cerradas: {total_closed}")
                print(f"   Tasa de operaciones cerradas: "
                      f"{(total_closed / total_opened * 100) if total_opened > 0 else 0:.1f}%\n")

    except KeyboardInterrupt:
        print("\nDeteniendo el seguimiento...")

    finally:
        await account.channel.close()


asyncio.run(track_position_lifecycle())
```

### 4) Notificaciones de trading en tiempo real

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def trade_notifications():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    try:
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Notificar nuevas posiciones
            if event.new_positions:
                count = len(event.new_positions)
                print(f"\n[NOTIFICACIÓN] Se han abierto {count} nueva(s) posición(es)")

                if trade_data.account_info:
                    print(f"   Saldo actual: ${trade_data.account_info.balance:.2f}")
                    print(f"   Equity actual: ${trade_data.account_info.equity:.2f}")

            # Notificar posiciones cerradas
            if event.disappeared_positions:
                count = len(event.disappeared_positions)
                print(f"\n[NOTIFICACIÓN] Se han cerrado {count} posición(es)")

                if trade_data.account_info:
                    print(f"   Saldo actual: ${trade_data.account_info.balance:.2f}")
                    print(f"   Beneficio total: ${trade_data.account_info.profit:.2f}")

            # Notificar órdenes pendientes
            if event.new_orders:
                count = len(event.new_orders)
                print(f"\n[NOTIFICACIÓN] Se han creado {count} orden(es) pendiente(s)")

            # Notificar la ejecución de órdenes
            if event.disappeared_orders:
                count = len(event.disappeared_orders)
                print(f"\n[NOTIFICACIÓN] Se han ejecutado/cancelado {count} orden(es) pendiente(s)")

    except KeyboardInterrupt:
        print("\nDeteniendo las notificaciones...")

    finally:
        await account.channel.close()


asyncio.run(trade_notifications())
```

### 5) Recopilador de estadísticas de trading

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def collect_trade_statistics(duration_seconds=300):
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    stats = {
        'positions_opened': 0,
        'positions_closed': 0,
        'positions_modified': 0,
        'orders_created': 0,
        'orders_removed': 0,
        'deals_executed': 0,
    }

    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for trade_data in account.on_trade(
            cancellation_event=cancel_event
        ):
            event = trade_data.event_data

            stats['positions_opened'] += len(event.new_positions)
            stats['positions_closed'] += len(event.disappeared_positions)
            stats['positions_modified'] += len(event.updated_positions)
            stats['orders_created'] += len(event.new_orders)
            stats['orders_removed'] += len(event.disappeared_orders)
            stats['deals_executed'] += len(event.new_history_deals)

        await stop_task

        # Mostrar las estadísticas finales
        print("\n" + "=" * 60)
        print("INFORME DE ESTADÍSTICAS DE TRADING")
        print("=" * 60)
        print(f"Posiciones abiertas:    {stats['positions_opened']:>6,}")
        print(f"Posiciones cerradas:    {stats['positions_closed']:>6,}")
        print(f"Posiciones modificadas: {stats['positions_modified']:>6,}")
        print(f"Órdenes creadas:        {stats['orders_created']:>6,}")
        print(f"Órdenes eliminadas:     {stats['orders_removed']:>6,}")
        print(f"Operaciones ejecutadas: {stats['deals_executed']:>6,}")
        print("=" * 60)

    finally:
        await account.channel.close()


# Recopilar estadísticas durante 5 minutos
asyncio.run(collect_trade_statistics(300))
```

### 6) Sincronizador de trading en tiempo real

```python
import asyncio
from MetaRpcMT5 import MT5Account


class TradeSynchronizer:
    def __init__(self):
        self.positions = {}  # index -> datos de la posición
        self.orders = {}     # index -> datos de la orden

    async def sync_trades(self, account):
        """Sincronizar el estado local con la cuenta MT5"""
        async for trade_data in account.on_trade():
            event = trade_data.event_data

            # Sincronizar posiciones
            for pos in event.new_positions:
                self.positions[pos.index] = pos
                print(f"[SINCRONIZACIÓN] Posición añadida #{pos.index}")

            for pos in event.disappeared_positions:
                if pos.index in self.positions:
                    del self.positions[pos.index]
                    print(f"[SINCRONIZACIÓN] Posición eliminada #{pos.index}")

            for pos in event.updated_positions:
                if pos.index in self.positions:
                    # Actualizar los datos de la posición
                    print(f"[SINCRONIZACIÓN] Posición actualizada #{pos.index}")

            # Sincronizar órdenes
            for order in event.new_orders:
                self.orders[order.index] = order
                print(f"[SINCRONIZACIÓN] Orden añadida #{order.index}")

            for order in event.disappeared_orders:
                if order.index in self.orders:
                    del self.orders[order.index]
                    print(f"[SINCRONIZACIÓN] Orden eliminada #{order.index}")

            # Mostrar el estado actual
            print(f"\n[ESTADO] Estado local: {len(self.positions)} posiciones, "
                  f"{len(self.orders)} órdenes\n")


async def main():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    synchronizer = TradeSynchronizer()

    try:
        await synchronizer.sync_trades(account)
    except KeyboardInterrupt:
        print("\nDeteniendo el sincronizador...")
    finally:
        await account.channel.close()


asyncio.run(main())
```

---

## 📚 Véase también

- [OnTradeTransaction](./on_trade_transaction.md) - Eventos de transacciones más detallados.
- [OnPositionProfit](./on_position_profit.md) - Flujo de actualizaciones del beneficio de las posiciones.
- [OpenedOrders](../3.%20Positions_Orders/opened_orders.md) - Obtener una instantánea de las posiciones actuales.
- [OrderHistory](../3.%20Positions_Orders/order_history.md) - Obtener las órdenes históricas.

