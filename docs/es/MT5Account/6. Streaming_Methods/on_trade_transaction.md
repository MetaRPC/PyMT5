

# Transmisión de eventos de transacciones comerciales

> **Solicitud:** suscribirse a eventos de transacciones comerciales en tiempo real (registro de auditoría detallado).

## Información de la API

- **API de Python:** `MT5Account.on_trade_transaction(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.SubscriptionService`
- **Definición Proto:** `OnTradeTransaction` (definido en `mt5-term-api-subscriptions.proto`)

### RPC

- **Servicio:** `mt5_term_api.SubscriptionService`
- **Método:** `OnTradeTransaction(OnTradeTransactionRequest) -> stream OnTradeTransactionReply`
- **Cliente de bajo nivel (generado):** `SubscriptionServiceStub.OnTradeTransaction(request, metadata)`

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def on_trade_transaction(
        self,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Se suscribe a los eventos de transacciones comerciales en tiempo real.

        Yields:
            OnTradeTransactionData: Datos de la transacción comercial.
        """
```

**Mensaje de solicitud:**

```protobuf
message OnTradeTransactionRequest {
  // Sin parámetros: se suscribe a todas las transacciones comerciales
}
```

## 💬 Lo esencial

- **Qué es:** flujo en tiempo real de eventos detallados de transacciones comerciales (el más completo).
- **Por qué lo necesitas:** registro de auditoría completo, registro detallado de transacciones y verificación de operaciones.
- **Basado en eventos:** las actualizaciones se activan inmediatamente con cada evento de transacción.

---

## 🎯 Propósito

Utilízalo para:

- Crear registros de auditoría comerciales completos.
- Seguir el ciclo de vida detallado de las transacciones.
- Supervisar detalladamente los cambios en el estado de las órdenes.
- Verificar la ejecución de las operaciones.
- Depurar las operaciones de trading.
- Implementar lógica basada en transacciones.
- Crear diarios de trading detallados.

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la transmisión (opcional) |

---

## ⬆️ Salida: generador asíncrono

Devuelve un generador asíncrono que produce objetos `OnTradeTransactionData`.

**Campos de `OnTradeTransactionData`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `type` | `int` | Tipo de transacción |
| `trade_transaction` | `MqlTradeTransaction` | Información detallada de la transacción |
| `trade_request` | `MqlTradeRequest` | Solicitud de trading original |
| `trade_result` | `MqlTradeResult` | Resultado de la ejecución de la operación |
| `account_info` | `OnEventAccountInfo` | Estado actual de la cuenta |
| `terminal_instance_guid_id` | `str` | Identificador de la instancia del terminal |

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

subscriptions_pb2.SUB_ORDER_STATE_FILLED   # = 4
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
| `SUB_DEAL_TYPE_COMMISSION_DAILY` | 8 | Comisión diaria |
| `SUB_DEAL_TYPE_COMMISSION_MONTHLY` | 9 | Comisión mensual |
| `SUB_DEAL_TYPE_COMMISSION_AGENT_DAILY` | 10 | Comisión diaria del agente |
| `SUB_DEAL_TYPE_COMMISSION_AGENT_MONTHLY` | 11 | Comisión mensual del agente |
| `SUB_DEAL_TYPE_INTEREST` | 12 | Tipo de interés |
| `SUB_DEAL_TYPE_BUY_CANCELED` | 13 | Operación de compra cancelada |
| `SUB_DEAL_TYPE_SELL_CANCELED` | 14 | Operación de venta cancelada |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_DEAL_TYPE_BUY   # = 0
```

**Enum de entrada de la operación (`SUB_ENUM_DEAL_ENTRY`):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_DEAL_ENTRY_IN` | 0 | Entrada en una posición |
| `SUB_DEAL_ENTRY_OUT` | 1 | Salida de una posición |
| `SUB_DEAL_ENTRY_INOUT` | 2 | Inversión de una posición |
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
| `SUB_DEAL_REASON_SL` | 4 | Operación causada por la activación del Stop Loss |
| `SUB_DEAL_REASON_TP` | 5 | Operación causada por la activación del Take Profit |
| `SUB_DEAL_REASON_SO` | 6 | Operación causada por un Stop Out |
| `SUB_DEAL_REASON_ROLLOVER` | 7 | Operación causada por el rollover |
| `SUB_DEAL_REASON_VMARGIN` | 8 | Operación causada por el margen de variación |
| `SUB_DEAL_REASON_SPLIT` | 9 | Operación causada por un desdoblamiento |
| `SUB_DEAL_REASON_CORPORATE_ACTION` | 10 | Operación causada por una acción corporativa |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_DEAL_REASON_CLIENT   # = 0
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
| `SUB_ORDER_REASON_SL` | 5 | Orden activada por el Stop Loss |
| `SUB_ORDER_REASON_TP` | 6 | Orden activada por el Take Profit |
| `SUB_ORDER_REASON_SO` | 7 | Orden activada por un Stop Out |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_ORDER_REASON_CLIENT   # = 0
```

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
| `SUB_POSITION_REASON_MOBILE` | 2 | Posición abierta desde la aplicación móvil |
| `SUB_POSITION_REASON_WEB` | 3 | Posición abierta desde el terminal web |
| `SUB_POSITION_REASON_EXPERT` | 4 | Posición abierta por un Asesor Experto |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

subscriptions_pb2.SUB_POSITION_REASON_CLIENT   # = 0
```

---

**Campos de `MqlTradeTransaction` (lista parcial):**

| Campo | Tipo | Descripción |
|---|---|---|
| `deal_ticket` | `uint64` | Número de ticket de la operación |
| `order_ticket` | `uint64` | Número de ticket de la orden |
| `symbol` | `string` | Símbolo de trading |
| `type` | `enum` | Tipo de transacción |
| `order_type` | `enum` | Tipo de orden (mercado, límite, stop, etc.) |
| `order_state` | `enum` | Estado de la orden (iniciada, colocada, etc.) |
| `deal_type` | `enum` | Tipo de operación (compra, venta) |
| `order_time_type` | `enum` | Tipo de tiempo de la orden (GTC, DAY, etc.) |
| `price` | `double` | Precio |
| `price_stop_loss` | `double` | Precio del Stop Loss |
| `price_take_profit` | `double` | Precio del Take Profit |
| `volume` | `double` | Volumen |
| `position_ticket` | `uint64` | Ticket de la posición |

**Campos de `MqlTradeRequest`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `action` | `enum` | Tipo de operación de trading |
| `magic` | `uint64` | Identificador del Asesor Experto |
| `order` | `uint64` | Ticket de la orden |
| `symbol` | `string` | Símbolo de trading |
| `volume` | `double` | Volumen solicitado |
| `price` | `double` | Precio |

**Campos de `MqlTradeResult`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `trade_return_int_code` | `int32` | Código de retorno interno |
| `trade_return_code` | `uint32` | Código de retorno de la operación |
| `deal_ticket` | `uint64` | Ticket de la operación |
| `order_ticket` | `uint64` | Ticket de la orden |
| `deal_volume` | `double` | Volumen de la operación |
| `deal_price` | `double` | Precio de la operación |
| `current_bid` | `double` | Precio Bid actual |
| `current_ask` | `double` | Precio Ask actual |
| `broker_comment_to_operation` | `string` | Comentario del bróker |
| `terminal_dispatch_request_id` | `uint32` | ID de solicitud del terminal |
| `return_code_external` | `int32` | Código de retorno externo (del bróker) |

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OnTradeTransaction - Cómo funciona](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de transmisión de `MT5Account` incorporan protección contra errores gRPC transitorios, con reconexión automática mediante `execute_stream_with_reconnect`.
- **Generador asíncrono:** el método devuelve un generador asíncrono; utiliza `async for` para consumir los datos.
- **El más detallado:** este es el flujo de transacciones más completo; incluye todos los datos de solicitud y resultado.
- **Sin parámetros:** se suscribe automáticamente a TODAS las transacciones comerciales.
- **Basado en eventos:** las actualizaciones llegan inmediatamente cuando se producen transacciones (no de forma periódica).
- **Ciclo de vida completo:** registra la creación, modificación, ejecución y cancelación de órdenes.
- **Incluye errores:** recibe eventos tanto de transacciones exitosas como fallidas.
- **Alto consumo de recursos:** es el flujo más detallado; utiliza `on_trade` si no necesitas este nivel de detalle.

---

## 🔗 Ejemplos de uso

### 1) Monitor básico de transacciones

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_transactions():
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
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            print(f"\n[EVENTO DE TRANSACCIÓN]")
            print(f"   Tipo: {tx.type}")
            print(f"   Símbolo: {tx.symbol}")
            print(f"   Orden: #{tx.order_ticket}")
            print(f"   Operación: #{tx.deal_ticket}")
            print(f"   Posición: #{tx.position_ticket}")
            print(f"   Precio: {tx.price}")
            print(f"   Volumen: {tx.volume}")
            print(f"   Estado de la orden: {tx.order_state}")

            # Mostrar la solicitud si está disponible
            if tx_data.trade_request and tx_data.trade_request.symbol:
                req = tx_data.trade_request
                print(f"\n   Solicitud:")
                print(f"     Símbolo: {req.symbol}")
                print(f"     Volumen: {req.volume}")
                print(f"     Precio: {req.price}")

            # Mostrar el resultado si está disponible
            if tx_data.trade_result and tx_data.trade_result.trade_return_code != 0:
                res = tx_data.trade_result
                print(f"\n   Resultado:")
                print(f"     Código de retorno: {res.trade_return_code}")
                print(f"     Comentario: {res.broker_comment_to_operation}")

    except KeyboardInterrupt:
        print("\nDeteniendo el monitor de transacciones...")

    finally:
        await account.channel.close()


asyncio.run(monitor_transactions())
```

### 2) Registro de auditoría completo de transacciones

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def audit_log():
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
        with open('trade_audit.log', 'w') as logfile:
            logfile.write("Marca de tiempo,Tipo,Simbolo,Orden,Operacion,Posicion,Precio,Volumen,Estado\n")

            async for tx_data in account.on_trade_transaction():
                tx = tx_data.trade_transaction
                timestamp = datetime.now().isoformat()

                # Escribir en el registro de auditoría
                logfile.write(
                    f"{timestamp},"
                    f"{tx.type},"
                    f"{tx.symbol},"
                    f"{tx.order_ticket},"
                    f"{tx.deal_ticket},"
                    f"{tx.position_ticket},"
                    f"{tx.price},"
                    f"{tx.volume},"
                    f"{tx.order_state}\n"
                )
                logfile.flush()

                print(f"[{timestamp}] Transacción registrada: "
                      f"Orden #{tx.order_ticket}, Operación #{tx.deal_ticket}")

    except KeyboardInterrupt:
        print("\nDeteniendo el registro de auditoría...")

    finally:
        await account.channel.close()


asyncio.run(audit_log())
```

### 3) Seguimiento del ciclo de vida de las órdenes

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def track_order_lifecycle():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    order_states = {}  # order_ticket -> lista de estados

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            if tx.order_ticket > 0:
                # Registrar los cambios de estado de la orden
                if tx.order_ticket not in order_states:
                    order_states[tx.order_ticket] = []

                order_states[tx.order_ticket].append({
                    'state': tx.order_state,
                    'type': tx.type,
                    'price': tx.price,
                    'volume': tx.volume
                })

                print(f"\n[CICLO DE VIDA] Orden #{tx.order_ticket}:")
                for i, state in enumerate(order_states[tx.order_ticket], 1):
                    print(f"   {i}. Estado: {state['state']}, "
                          f"Tipo: {state['type']}, "
                          f"Precio: {state['price']}")

    except KeyboardInterrupt:
        print("\nDeteniendo el seguimiento del ciclo de vida...")
        print(f"\nTotal de órdenes registradas: {len(order_states)}")

    finally:
        await account.channel.close()


asyncio.run(track_order_lifecycle())
```

### 4) Monitor de transacciones fallidas

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_failed_transactions():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    failed_count = 0

    try:
        async for tx_data in account.on_trade_transaction():
            # Comprobar si hay transacciones fallidas
            if tx_data.trade_result and tx_data.trade_result.trade_return_code != 10009:  # No es DONE
                failed_count += 1
                res = tx_data.trade_result
                tx = tx_data.trade_transaction

                print(f"\n[TRANSACCIÓN FALLIDA #{failed_count}]")
                print(f"   Código de retorno: {res.trade_return_code}")
                print(f"   Comentario: {res.broker_comment_to_operation}")
                print(f"   Símbolo: {tx.symbol}")
                print(f"   Orden: #{tx.order_ticket}")
                print(f"   Volumen solicitado: {tx.volume}")
                print(f"   Precio: {tx.price}")

                if tx_data.trade_request:
                    req = tx_data.trade_request
                    print(f"\n   Solicitud original:")
                    print(f"     Acción: {req.action}")
                    print(f"     Símbolo: {req.symbol}")
                    print(f"     Volumen: {req.volume}")

    except KeyboardInterrupt:
        print(f"\n\nDeteniendo el monitor. Total de fallos: {failed_count}")

    finally:
        await account.channel.close()


asyncio.run(monitor_failed_transactions())
```

### 5) Recopilador de estadísticas de transacciones

```python
import asyncio
from collections import defaultdict
from MetaRpcMT5 import MT5Account


async def collect_transaction_stats(duration_seconds=300):
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
        'total_transactions': 0,
        'by_type': defaultdict(int),
        'by_state': defaultdict(int),
        'by_symbol': defaultdict(int),
        'successful': 0,
        'failed': 0,
    }

    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for tx_data in account.on_trade_transaction(
            cancellation_event=cancel_event
        ):
            tx = tx_data.trade_transaction
            stats['total_transactions'] += 1
            stats['by_type'][tx.type] += 1
            stats['by_state'][tx.order_state] += 1

            if tx.symbol:
                stats['by_symbol'][tx.symbol] += 1

            # Comprobar el éxito o el fallo
            if tx_data.trade_result:
                if tx_data.trade_result.trade_return_code == 10009:  # DONE
                    stats['successful'] += 1
                else:
                    stats['failed'] += 1

        await stop_task

        # Mostrar las estadísticas
        print("\n" + "=" * 70)
        print("INFORME DE ESTADÍSTICAS DE TRANSACCIONES")
        print("=" * 70)
        print(f"Total de transacciones: {stats['total_transactions']:>6,}")
        print(f"Exitosas:               {stats['successful']:>6,}")
        print(f"Fallidas:               {stats['failed']:>6,}")

        print("\nPor tipo:")
        for tx_type, count in sorted(stats['by_type'].items()):
            print(f"  Tipo {tx_type}: {count:>6,}")

        print("\nPor estado:")
        for state, count in sorted(stats['by_state'].items()):
            print(f"  Estado {state}: {count:>6,}")

        print("\nPor símbolo:")
        for symbol, count in sorted(stats['by_symbol'].items(),
                                    key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {symbol}: {count:>6,}")

        print("=" * 70)

    finally:
        await account.channel.close()


# Recopilar estadísticas durante 5 minutos
asyncio.run(collect_transaction_stats(300))
```

### 6) Diario de trading en tiempo real

```python
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def trade_journal():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )
    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    journal_entries = []

    try:
        async for tx_data in account.on_trade_transaction():
            tx = tx_data.trade_transaction

            # Crear una entrada en el diario
            entry = {
                'timestamp': datetime.now(),
                'type': tx.type,
                'symbol': tx.symbol,
                'order_ticket': tx.order_ticket,
                'deal_ticket': tx.deal_ticket,
                'position_ticket': tx.position_ticket,
                'price': tx.price,
                'volume': tx.volume,
                'order_state': tx.order_state,
                'sl': tx.price_stop_loss,
                'tp': tx.price_take_profit,
            }

            # Añadir información del resultado si está disponible
            if tx_data.trade_result:
                entry['retcode'] = tx_data.trade_result.trade_return_code
                entry['comment'] = tx_data.trade_result.broker_comment_to_operation

            # Añadir el saldo de la cuenta
            if tx_data.account_info:
                entry['balance'] = tx_data.account_info.balance
                entry['equity'] = tx_data.account_info.equity

            journal_entries.append(entry)

            # Mostrar la entrada
            print(f"\n{'=' * 70}")
            print(f"ENTRADA DEL DIARIO #{len(journal_entries)}")
            print(f"{'=' * 70}")
            print(f"Hora:       {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Símbolo:    {entry['symbol']}")
            print(f"Tipo:       {entry['type']}")
            print(f"Orden:      #{entry['order_ticket']}")
            print(f"Operación:  #{entry['deal_ticket']}")
            print(f"Posición:   #{entry['position_ticket']}")
            print(f"Precio:     {entry['price']}")
            print(f"Volumen:    {entry['volume']}")
            print(f"SL:         {entry['sl']}")
            print(f"TP:         {entry['tp']}")
            print(f"Estado:     {entry['order_state']}")

            if 'balance' in entry:
                print(f"Saldo:      ${entry['balance']:.2f}")
                print(f"Equity:     ${entry['equity']:.2f}")

            # Guardar el diario periódicamente
            if len(journal_entries) % 10 == 0:
                print(f"\n[GUARDADO] {len(journal_entries)} entradas en el diario")

    except KeyboardInterrupt:
        print(f"\n\nDeteniendo el diario. Total de entradas: {len(journal_entries)}")

        # Exportar el diario
        with open('trade_journal.txt', 'w') as f:
            f.write("DIARIO DE TRADING\n")
            f.write("=" * 70 + "\n\n")

            for i, entry in enumerate(journal_entries, 1):
                f.write(f"Entrada #{i}\n")
                f.write(f"  Hora: {entry['timestamp']}\n")
                f.write(f"  Símbolo: {entry['symbol']}\n")
                f.write(f"  Orden: #{entry['order_ticket']}\n")
                f.write(f"  Precio: {entry['price']}\n")
                f.write("\n")

        print(f"Diario exportado a trade_journal.txt")

    finally:
        await account.channel.close()


asyncio.run(trade_journal())
```

---

## 🔗 Véase también

- [OnTrade](./on_trade.md) - Flujo de eventos de trading más sencillo y menos detallado.
- [OrderSend](../5.%20Trading_Operations/order_send.md) - Enviar órdenes de trading.
- [OrderCheck](../5.%20Trading_Operations/order_check.md) - Verificar una orden antes de enviarla.
- [OrderHistory](../3.%20Positions_Orders/order_history.md) - Obtener el historial de órdenes.

