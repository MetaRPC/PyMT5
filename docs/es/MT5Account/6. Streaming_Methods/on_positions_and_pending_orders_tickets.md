# Transmitir los tickets de posiciones y órdenes pendientes

> **Solicitud:** suscribirse a las actualizaciones periódicas de los identificadores de tickets de posiciones y órdenes pendientes.

**Información de la API:**

- **API de Python:** `MT5Account.on_positions_and_pending_orders_tickets(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.SubscriptionService`
- **Definición Proto:** `OnPositionsAndPendingOrdersTickets` (definido en `mt5-term-api-subscriptions.proto`)

### RPC

- **Servicio:** `mt5_term_api.SubscriptionService`
- **Método:** `OnPositionsAndPendingOrdersTickets(OnPositionsAndPendingOrdersTicketsRequest) -> stream OnPositionsAndPendingOrdersTicketsReply`
- **Cliente de bajo nivel (generado):** `SubscriptionServiceStub.OnPositionsAndPendingOrdersTickets(request, metadata)`

---

## 💬 Lo esencial

- **Qué es.** Flujo periódico de identificadores de tickets de posiciones abiertas y órdenes pendientes.
- **Para qué sirve.** Supervisar posiciones y órdenes de forma ligera y detectar cambios sin tener que obtener todos sus datos.
- **Actualizaciones periódicas.** Se envía una instantánea a intervalos especificados (por ejemplo, cada 1000 ms).

---

## 🎯 Propósito

Utilízalo para:

- Supervisar los cambios en el número de posiciones y órdenes.
- Detectar cuándo se abren nuevas posiciones (aparecen nuevos tickets).
- Detectar cuándo se cierran posiciones (desaparecen tickets).
- Utilizarlo como alternativa ligera a `on_trade` cuando solo necesitas los identificadores de tickets.
- Seguir el ciclo de vida de los tickets sin obtener todos los datos de las posiciones.
- Crear sistemas eficientes de detección de cambios.

```
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def on_positions_and_pending_orders_tickets(
        self,
        interval_ms: int,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Se suscribe a las actualizaciones de los identificadores de tickets
        de posiciones y órdenes pendientes.

        Yields:
            OnPositionsAndPendingOrdersTicketsData: Instantánea de los tickets.
        """
```

**Mensaje de solicitud:**

```
message OnPositionsAndPendingOrdersTicketsRequest {
  int32 timer_period_milliseconds = 1;  // Intervalo de sondeo en milisegundos
}
```

---

## 🔽 Entrada

| Parámetro            | Tipo                      | Descripción                                     |
| -------------------- | ------------------------- | ----------------------------------------------- |
| `interval_ms`        | `int`                     | Intervalo de sondeo en milisegundos.            |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la transmisión (opcional). |

---

## ⬆️ Salida - Generador asíncrono

Devuelve un generador asíncrono que produce objetos `OnPositionsAndPendingOrdersTicketsData`.

**Campos de OnPositionsAndPendingOrdersTicketsData:**

| Campo                       | Tipo                        | Descripción                                                 |
| --------------------------- | --------------------------- | ----------------------------------------------------------- |
| `position_tickets`          | `repeated uint64`           | Lista de identificadores de tickets de posiciones abiertas. |
| `pending_order_tickets`     | `repeated uint64`           | Lista de identificadores de tickets de órdenes pendientes.  |
| `server_time`               | `google.protobuf.Timestamp` | Marca de tiempo del servidor.                               |
| `terminal_instance_guid_id` | `str`                       | Identificador de la instancia del terminal.                 |

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OnPositionsAndPendingOrdersTickets - Cómo funciona]\(../HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW\.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de streaming de `MT5Account` incorporan protección contra errores gRPC transitorios mediante reconexión automática a través de `execute_stream_with_reconnect`.
- **Generador asíncrono:** el método devuelve un generador asíncrono; utiliza `async for` para consumir los datos.
- **Instantáneas periódicas:** cada actualización es una instantánea completa, no un conjunto de cambios incrementales.
- **Ligero:** solo devuelve identificadores de tickets. Utilízalo cuando no necesites todos los datos de las posiciones y órdenes.
- **Detección de cambios:** compara las listas de tickets entre actualizaciones para detectar posiciones nuevas o cerradas.
- **Intervalo de sondeo:** elige el intervalo según tus necesidades. Un intervalo más corto proporciona actualizaciones más frecuentes.
- **Eficiencia de recursos:** es mucho más ligero que `on_trade` o `on_position_profit`.

---

## 🔗 Ejemplos de uso

### 1) Supervisar los cambios en los tickets

```
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_tickets():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_positions = set()
    prev_orders = set()

    try:
        # Consultar cada segundo
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            current_positions = set(update.position_tickets)
            current_orders = set(update.pending_order_tickets)

            # Detectar posiciones nuevas
            new_positions = current_positions - prev_positions
            if new_positions:
                print(f"[NUEVAS] Posiciones: {new_positions}")

            # Detectar posiciones cerradas
            closed_positions = prev_positions - current_positions
            if closed_positions:
                print(f"[CERRADAS] Posiciones: {closed_positions}")

            # Detectar nuevas órdenes pendientes
            new_orders = current_orders - prev_orders
            if new_orders:
                print(f"[NUEVAS] Órdenes: {new_orders}")

            # Detectar órdenes pendientes eliminadas
            removed_orders = prev_orders - current_orders
            if removed_orders:
                print(f"[ELIMINADAS] Órdenes: {removed_orders}")

            # Mostrar el estado actual
            print(f"[ESTADO] Posiciones: {len(current_positions)}, "
                  f"Órdenes: {len(current_orders)}\n")

            prev_positions = current_positions
            prev_orders = current_orders

    except KeyboardInterrupt:
        print("Deteniendo el monitor...")

    finally:
        await account.channel.close()


asyncio.run(monitor_tickets())
```

### 2) Alertar cuando cambia el número de posiciones

```
import asyncio
from MetaRpcMT5 import MT5Account


async def alert_on_position_changes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_count = 0

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=500
        ):
            current_count = len(update.position_tickets)

            # Alertar cuando se producen cambios
            if current_count > prev_count:
                print(f"\n[ALERTA] Se han ABIERTO {current_count - prev_count} posición(es)")
                print(f"   Total de posiciones: {current_count}")
                print(f"   Tickets: {list(update.position_tickets)}")

            elif current_count < prev_count:
                print(f"\n[ALERTA] Se han CERRADO {prev_count - current_count} posición(es)")
                print(f"   Posiciones restantes: {current_count}")
                print(f"   Tickets: {list(update.position_tickets)}")

            prev_count = current_count

    except KeyboardInterrupt:
        print("\nDeteniendo las alertas...")

    finally:
        await account.channel.close()


asyncio.run(alert_on_position_changes())
```

### 3) Registrar estadísticas de posiciones y órdenes

```
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def track_ticket_statistics(duration_seconds=300):
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
        'max_positions': 0,
        'max_orders': 0,
        'total_opened': 0,
        'total_closed': 0,
        'updates': 0,
    }

    prev_positions = set()
    cancel_event = asyncio.Event()

    async def auto_stop():
        await asyncio.sleep(duration_seconds)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000,
            cancellation_event=cancel_event
        ):
            current_positions = set(update.position_tickets)
            stats['updates'] += 1

            # Actualizar los recuentos máximos
            stats['max_positions'] = max(stats['max_positions'], len(current_positions))
            stats['max_orders'] = max(stats['max_orders'], len(update.pending_order_tickets))

            # Contabilizar las posiciones abiertas y cerradas
            stats['total_opened'] += len(current_positions - prev_positions)
            stats['total_closed'] += len(prev_positions - current_positions)

            prev_positions = current_positions

        await stop_task

        # Mostrar las estadísticas
        print("\n" + "=" * 60)
        print("INFORME DE ESTADÍSTICAS DE TICKETS")
        print("=" * 60)
        print(f"Duración:                 {duration_seconds} segundos")
        print(f"Actualizaciones recibidas: {stats['updates']}")
        print(f"Máximo de posiciones:     {stats['max_positions']}")
        print(f"Máximo de órdenes:        {stats['max_orders']}")
        print(f"Total abiertas:           {stats['total_opened']}")
        print(f"Total cerradas:           {stats['total_closed']}")
        print("=" * 60)

    finally:
        await account.channel.close()


# Realizar el seguimiento durante 5 minutos
asyncio.run(track_ticket_statistics(300))
```

### 4) Limitador del número de posiciones

```
import asyncio
from MetaRpcMT5 import MT5Account


async def position_count_limiter(max_positions=5):
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
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=500
        ):
            position_count = len(update.position_tickets)

            if position_count >= max_positions:
                print(f"\n[ADVERTENCIA] ¡Se ha alcanzado el límite de posiciones!")
                print(f"   Posiciones actuales: {position_count}/{max_positions}")
                print(f"   Tickets: {list(update.position_tickets)}")
                print(f"   [BLOQUEO] Se debe impedir la apertura de nuevas posiciones\n")
            else:
                available = max_positions - position_count
                print(f"[OK] Posiciones: {position_count}/{max_positions} "
                      f"({available} plazas disponibles)")

    except KeyboardInterrupt:
        print("\nDeteniendo el limitador...")

    finally:
        await account.channel.close()


# Alertar cuando haya 5 o más posiciones abiertas
asyncio.run(position_count_limiter(5))
```

### 5) Registrar los cambios de tickets en un archivo

```
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def log_ticket_changes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    prev_positions = set()
    prev_orders = set()

    try:
        with open('ticket_changes.log', 'w') as logfile:
            logfile.write("Timestamp,Event,Ticket\n")

            async for update in account.on_positions_and_pending_orders_tickets(
                interval_ms=1000
            ):
                timestamp = datetime.now().isoformat()
                current_positions = set(update.position_tickets)
                current_orders = set(update.pending_order_tickets)

                # Registrar las posiciones nuevas
                for ticket in current_positions - prev_positions:
                    logfile.write(f"{timestamp},POSITION_OPENED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Posición abierta: {ticket}")

                # Registrar las posiciones cerradas
                for ticket in prev_positions - current_positions:
                    logfile.write(f"{timestamp},POSITION_CLOSED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Posición cerrada: {ticket}")

                # Registrar las órdenes nuevas
                for ticket in current_orders - prev_orders:
                    logfile.write(f"{timestamp},ORDER_CREATED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Orden creada: {ticket}")

                # Registrar las órdenes eliminadas
                for ticket in prev_orders - current_orders:
                    logfile.write(f"{timestamp},ORDER_REMOVED,{ticket}\n")
                    logfile.flush()
                    print(f"[{timestamp}] Orden eliminada: {ticket}")

                prev_positions = current_positions
                prev_orders = current_orders

    except KeyboardInterrupt:
        print("\nDeteniendo el registrador...")

    finally:
        await account.channel.close()


asyncio.run(log_ticket_changes())
```

### 6) Panel ligero de supervisión de posiciones

```
import asyncio
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def position_dashboard():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    start_time = datetime.now()

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            # Limpiar la pantalla
            print("\033[2J\033[H")

            runtime = datetime.now() - start_time
            server_time = datetime.fromtimestamp(update.server_time.seconds)

            print("=" * 70)
            print(f"PANEL DE SUPERVISIÓN DE POSICIONES")
            print("=" * 70)
            print(f"Tiempo de ejecución: {runtime}")
            print(f"Hora del servidor:   {server_time}")
            print(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
            print("-" * 70)

            print(f"\nPosiciones abiertas: {len(update.position_tickets)}")
            if update.position_tickets:
                for i, ticket in enumerate(update.position_tickets, 1):
                    print(f"  {i}. Ticket #{ticket}")
            else:
                print("  (ninguna)")

            print(f"\nÓrdenes pendientes: {len(update.pending_order_tickets)}")
            if update.pending_order_tickets:
                for i, ticket in enumerate(update.pending_order_tickets, 1):
                    print(f"  {i}. Ticket #{ticket}")
            else:
                print("  (ninguna)")

            print("\n" + "=" * 70)
            print("Pulsa Ctrl+C para detener")

    except KeyboardInterrupt:
        print("\n\nDeteniendo el panel de control...")

    finally:
        await account.channel.close()


asyncio.run(position_dashboard())
```

---

## 📚 Véase también

- OpenedOrdersTickets - obtener una instantánea de los tickets (una sola consulta).
- OpenedOrders - obtener todos los datos de las posiciones (una sola consulta).
- OnTrade - transmitir eventos detallados de trading.
- OnPositionProfit - transmitir actualizaciones del beneficio de las posiciones.

Corrige el ejemplo de estadísticasAñade una nota sobre instantáneas iniciales