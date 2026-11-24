# MT5Account - Métodos de streaming - Descripción general

> Flujos en tiempo real: ticks, operaciones, actualizaciones de beneficios y pérdidas, y registro de transacciones. Utiliza esta página para elegir la API adecuada para las suscripciones en tiempo real.

## 📁 Contenido de esta sección

### Actualizaciones de precios en tiempo real

- **[on_symbol_tick](./on_symbol_tick.md)** - flujo de ticks en tiempo real para los símbolos.

### Eventos de trading

- **[on_trade](./on_trade.md)** - cambios en posiciones y órdenes (apertura, cierre y modificación).
- **[on_trade_transaction](./on_trade_transaction.md)** - registro detallado de transacciones (historial de auditoría completo).

### Supervisión de posiciones

- **[on_position_profit](./on_position_profit.md)** - actualizaciones periódicas de beneficios y pérdidas.
- **[on_positions_and_pending_orders_tickets](./on_positions_and_pending_orders_tickets.md)** - listas periódicas de tickets (supervisión ligera).

---

## 📚 Tutoriales paso a paso

**Nota:** Los métodos de streaming son API basadas en generadores asíncronos. Consulta las páginas de cada método para ver ejemplos detallados de patrones `asyncio` y gestión de eventos.

- **[on_symbol_tick](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_symbol_tick_HOW.md)** - Ejemplos detallados de streaming de ticks.
- **[on_trade](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_HOW.md)** - Patrones de supervisión de eventos de trading.
- **[on_trade_transaction](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_trade_transaction_HOW.md)** - Ejemplos de registro de transacciones.
- **[on_position_profit](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW.md)** - Patrones de supervisión de beneficios y pérdidas.
- **[on_positions_and_pending_orders_tickets](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_positions_and_pending_orders_tickets_HOW.md)** - Ejemplos de seguimiento de tickets.

---

## 🧭 En términos sencillos

- **on_symbol_tick** -> **transmitir precios en vivo** de los símbolos (actualizaciones de bid, ask y volumen).
- **on_trade** -> **supervisar eventos de trading** (apertura, cierre y modificación de posiciones).
- **on_trade_transaction** -> **registro detallado de auditoría** de todas las operaciones de trading.
- **on_position_profit** -> **actualizaciones periódicas de beneficios y pérdidas** de las posiciones abiertas.
- **on_positions_and_pending_orders_tickets** -> **listas periódicas de tickets** (supervisión ligera).

> Regla general: si necesitas **precios en vivo** -> `on_symbol_tick`; si necesitas **notificaciones de trading** -> `on_trade`; si necesitas una **auditoría detallada** -> `on_trade_transaction`; si necesitas **supervisar beneficios y pérdidas** -> `on_position_profit`.

---

## Elección rápida

| Si necesitas... | Utiliza | Devuelve (flujo asíncrono) | Parámetros principales |
| ------------------------------------------------ | ------------------------------------------- | ---------------------------------- | ----------------------------------- |
| Ticks de precios en tiempo real | `on_symbol_tick` | OnSymbolTickData | Lista de nombres de símbolos |
| Notificaciones de eventos de trading | `on_trade` | OnTradeData | **(ninguno)** |
| Registro detallado de auditoría de transacciones | `on_trade_transaction` | OnTradeTransactionData | **(ninguno)** |
| Actualizaciones de beneficios y pérdidas en tiempo real | `on_position_profit` | OnPositionProfitData | Intervalo (ms), indicador `ignore_empty` |
| Cambios en la lista de tickets en tiempo real | `on_positions_and_pending_orders_tickets` | OnPositionsAndPendingOrdersTicketsData | Intervalo (ms) |

---

## ℹ️ Referencias cruzadas y aspectos importantes

- **Streaming = generadores asíncronos** - Los métodos devuelven generadores asíncronos; utiliza `async for` para consumir los datos.
- **Cancelación** - Utiliza `asyncio.Event` y llama a `event.set()` para detener los flujos de forma ordenada.
- **Se requiere async/await** - Todos los métodos de streaming deben llamarse con `await` dentro de funciones asíncronas.
- **on_symbol_tick** - Tiene una frecuencia elevada y puede generar muchas actualizaciones por segundo.
- **on_trade** - Se activa con cada evento de trading (apertura, cierre, modificación o eliminación).
- **on_trade_transaction** - Es el más detallado e incluye todos los tipos y estados de transacciones.
- **on_position_profit** - Proporciona actualizaciones periódicas en los intervalos especificados (por ejemplo, cada 500 ms).
- **Gestión de recursos** - Cancela siempre los flujos cuando termines para cerrar las conexiones y liberar recursos.
- **Gestión de errores** - Los errores se generan como excepciones; utiliza `try/except` para gestionarlos.
- **Reconexión automática** - Todos los flujos incluyen reconexión integrada mediante `execute_stream_with_reconnect`.

---

## 🟢 Ejemplos mínimos

```python
import asyncio

from MetaRpcMT5 import MT5Account


# Transmitir ticks en vivo de EURUSD
async def stream_ticks():
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
        async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
            tick = tick_data.symbol_tick
            print(f"EURUSD: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")

    except KeyboardInterrupt:
        print("Deteniendo...")
    finally:
        await account.channel.close()


asyncio.run(stream_ticks())
```

```python
# Supervisar eventos de trading
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

            if event.new_positions:
                print(f"Nuevas posiciones: {len(event.new_positions)}")
            if event.disappeared_positions:
                print(f"Posiciones cerradas: {len(event.disappeared_positions)}")

    finally:
        await account.channel.close()


asyncio.run(monitor_trades())
```

```python
# Supervisar beneficios y pérdidas de las posiciones
async def monitor_pnl():
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
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            for pos in update.updated_positions:
                print(f"#{pos.ticket} ({pos.position_symbol}): ${pos.profit:.2f}")

    finally:
        await account.channel.close()


asyncio.run(monitor_pnl())
```

```python
# Supervisar los tickets de las posiciones
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

    try:
        async for update in account.on_positions_and_pending_orders_tickets(
            interval_ms=1000
        ):
            print(f"Posiciones abiertas: {len(update.position_tickets)}")
            print(f"Órdenes pendientes: {len(update.pending_order_tickets)}")

    finally:
        await account.channel.close()


asyncio.run(monitor_tickets())
```

```python
# Registro detallado de transacciones
async def transaction_log():
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
            print(f"Transacción: Orden #{tx.order_ticket}, "
                  f"Deal #{tx.deal_ticket}, Estado: {tx.order_state}")

    finally:
        await account.channel.close()


asyncio.run(transaction_log())
```

```python
# Varios flujos con cancelación
async def multiple_streams():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    cancel_event = asyncio.Event()

    async def stop_after(seconds):
        await asyncio.sleep(seconds)
        cancel_event.set()

    async def stream_ticks():
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"[TICK] {tick.bid:.5f}")

    async def stream_trades():
        async for trade_data in account.on_trade(
            cancellation_event=cancel_event
        ):
            print("[TRADE] Evento recibido")

    try:
        # Ejecutar varios flujos simultáneamente
        await asyncio.gather(
            stream_ticks(),
            stream_trades(),
            stop_after(30)  # Detener todos después de 30 segundos
        )
    finally:
        await account.channel.close()


asyncio.run(multiple_streams())
```

```python
# Uso de un evento de cancelación para un cierre ordenado
async def stream_with_cancellation():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    cancel_event = asyncio.Event()

    async def handle_keyboard_interrupt():
        """Esperar Ctrl+C y activar la cancelación"""
        try:
            await asyncio.Event().wait()  # Esperar indefinidamente
        except asyncio.CancelledError:
            cancel_event.set()

    try:
        # Crear una tarea para gestionar la interrupción del teclado
        interrupt_task = asyncio.create_task(handle_keyboard_interrupt())

        # Flujo con soporte para cancelación
        async for tick_data in account.on_symbol_tick(
            symbols=["EURUSD", "GBPUSD"],
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            print(f"{tick.symbol}: {tick.bid:.5f}")

        interrupt_task.cancel()

    except KeyboardInterrupt:
        cancel_event.set()
        print("\nDeteniendo el flujo de forma ordenada...")

    finally:
        await account.channel.close()


asyncio.run(stream_with_cancellation())
```

---

## 📚 Véase también

- **Información de la cuenta:** [account_summary](../1.%20Account_Information/account_summary.md) - obtener el estado actual de la cuenta.
- **Posiciones:** [opened_orders](../3.%20Positions_Orders/opened_orders.md) - obtener una instantánea de las posiciones actuales.
- **Información de símbolos:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - obtener una instantánea del precio actual.