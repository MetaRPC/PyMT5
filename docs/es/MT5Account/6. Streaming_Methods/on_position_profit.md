# Transmitir en tiempo real el beneficio/pérdida de las posiciones

> **Solicitud:** suscribirse a las actualizaciones en tiempo real del beneficio/pérdida de las posiciones abiertas.

**Información de la API:**

- **API de Python:** `MT5Account.on_position_profit(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.SubscriptionService`
- **Definición Proto:** `OnPositionProfit` (definido en `mt5-term-api-subscriptions.proto`)

### RPC

- **Servicio:** `mt5_term_api.SubscriptionService`
- **Método:** `OnPositionProfit(OnPositionProfitRequest) -> stream OnPositionProfitReply`
- **Cliente de bajo nivel (generado):** `SubscriptionServiceStub.OnPositionProfit(request, metadata)`

---

## 💬 Lo esencial

- **Qué es.** Flujo periódico de actualizaciones del beneficio/pérdida de las posiciones.
- **Para qué sirve.** Supervisar P&L, implementar lógica de Stop Loss y realizar un seguimiento del rendimiento de la cuenta.
- **Actualizaciones periódicas.** Las actualizaciones se envían a intervalos especificados (por ejemplo, cada 500 ms).

---

## 🎯 Propósito

Utilízalo para:

- Supervisar en tiempo real el beneficio/pérdida de las posiciones abiertas.
- Implementar una lógica dinámica de Stop Loss y Take Profit.
- Realizar un seguimiento del rendimiento de la cuenta en tiempo real.
- Configurar alertas de beneficios/pérdidas.
- Crear paneles de control de P&L en tiempo real.
- Detectar inmediatamente los cambios en las posiciones.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OnPositionProfit - Cómo funciona](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_position_profit_HOW.md)**

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def on_position_profit(
        self,
        interval_ms: int,
        ignore_empty: bool = True,
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Se suscribe a las actualizaciones en tiempo real del beneficio
        de las posiciones abiertas.

        Yields:
            OnPositionProfitData: Datos de actualización del beneficio.
        """
```

**Mensaje de solicitud:**

```protobuf
message OnPositionProfitRequest {
  int32 timer_period_milliseconds = 1;  // Intervalo de sondeo en milisegundos
  bool ignore_empty_data = 2;           // Omitir los intervalos sin cambios (valor predeterminado: true)
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `interval_ms` | `int` | Intervalo en milisegundos para consultar el servidor. |
| `ignore_empty` | `bool` | Omitir los intervalos sin cambios (valor predeterminado: True). |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la transmisión (opcional). |

---

## ⬆️ Salida - Generador asíncrono

Devuelve un generador asíncrono que produce objetos `OnPositionProfitData`.

**Campos de OnPositionProfitData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `type` | `int` | Tipo de actualización. |
| `new_positions` | `repeated OnPositionProfitPositionInfo` | Posiciones recién abiertas. |
| `updated_positions` | `repeated OnPositionProfitPositionInfo` | Posiciones cuyo beneficio ha cambiado. |
| `deleted_positions` | `repeated OnPositionProfitPositionInfo` | Posiciones cerradas. |
| `account_info` | `OnEventAccountInfo` | Información actual de la cuenta. |
| `terminal_instance_guid_id` | `str` | Identificador de la instancia del terminal. |

**Campos de OnPositionProfitPositionInfo:**

| Campo | Tipo | Descripción |
|---|---|---|
| `index` | `int32` | Índice de la posición en la lista. |
| `ticket` | `uint64` | Número de ticket de la posición. |
| `profit` | `double` | Beneficio/pérdida actual. |
| `position_symbol` | `string` | Símbolo de trading. |

**Campos de OnEventAccountInfo:**

| Campo | Tipo | Descripción |
|---|---|---|
| `balance` | `double` | Balance de la cuenta. |
| `equity` | `double` | Equity de la cuenta. |
| `profit` | `double` | Beneficio total. |
| `margin` | `double` | Margen utilizado. |
| `margin_free` | `double` | Margen libre. |

**Enum de tipo de posición (SUB_ENUM_POSITION_TYPE):**

| Nombre | Valor | Descripción |
|---|---:|---|
| `SUB_POSITION_TYPE_BUY` | 0 | Posición de compra (larga). |
| `SUB_POSITION_TYPE_SELL` | 1 | Posición de venta (corta). |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2

# Acceder a los valores del enum
subscriptions_pb2.SUB_POSITION_TYPE_BUY   # = 0
subscriptions_pb2.SUB_POSITION_TYPE_SELL  # = 1
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de streaming de `MT5Account` incorporan protección contra errores gRPC transitorios mediante reconexión automática a través de `execute_stream_with_reconnect`.
- **Generador asíncrono:** el método devuelve un generador asíncrono; utiliza `async for` para consumir los datos.
- **Intervalo de sondeo:** elige el intervalo según tus necesidades: los intervalos más cortos ofrecen actualizaciones más frecuentes, pero aumentan la carga.
- **Ignorar datos vacíos:** establece `ignore_empty=True` para omitir las actualizaciones cuando no haya cambios (recomendado).
- **Tres listas:** cada actualización contiene `new_positions`, `updated_positions` y `deleted_positions`.
- **Información de la cuenta:** cada actualización incluye el balance, el equity y el margen actuales de la cuenta.
- **Gestión de recursos:** cancela siempre los flujos cuando termines para liberar recursos.

---

## 🔗 Ejemplos de uso

### 1) Supervisar el P&L de todas las posiciones

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_positions_pnl():
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
        # Consultar cada 500 ms y omitir las actualizaciones vacías
        async for update in account.on_position_profit(
            interval_ms=500,
            ignore_empty=True
        ):
            # Posiciones nuevas
            if update.new_positions:
                for pos in update.new_positions:
                    print(f"[NUEVA] Posición #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L={pos.profit:.2f}")

            # Posiciones actualizadas (el beneficio ha cambiado)
            if update.updated_positions:
                for pos in update.updated_positions:
                    print(f"[ACTUALIZACIÓN] Posición #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L={pos.profit:.2f}")

            # Posiciones cerradas
            if update.deleted_positions:
                for pos in update.deleted_positions:
                    print(f"[CERRADA] Posición #{pos.ticket} ({pos.position_symbol}): "
                          f"P&L final={pos.profit:.2f}")

            # Resumen de la cuenta
            if update.account_info:
                acc = update.account_info
                print(f"[CUENTA] Balance={acc.balance:.2f}, "
                      f"Equity={acc.equity:.2f}, Beneficio={acc.profit:.2f}\n")

    except KeyboardInterrupt:
        print("Deteniendo el flujo...")

    finally:
        await account.channel.close()


asyncio.run(monitor_positions_pnl())
```

### 2) Panel de control del P&L total en tiempo real

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def realtime_pnl_dashboard():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Realizar un seguimiento de todas las posiciones
    positions = {}  # ticket -> (symbol, profit)

    try:
        async for update in account.on_position_profit(
            interval_ms=1000,
            ignore_empty=True
        ):
            # Añadir posiciones nuevas
            for pos in update.new_positions:
                positions[pos.ticket] = (pos.position_symbol, pos.profit)

            # Actualizar posiciones existentes
            for pos in update.updated_positions:
                positions[pos.ticket] = (pos.position_symbol, pos.profit)

            # Eliminar posiciones cerradas
            for pos in update.deleted_positions:
                if pos.ticket in positions:
                    del positions[pos.ticket]

            # Calcular el P&L total
            total_profit = sum(profit for _, profit in positions.values())

            # Mostrar el panel de control
            print("\033[2J\033[H")  # Limpiar la pantalla
            print("=" * 60)
            print(f"PANEL DE CONTROL DE P&L EN TIEMPO REAL")
            print("=" * 60)

            if update.account_info:
                acc = update.account_info
                print(f"Balance:  ${acc.balance:,.2f}")
                print(f"Equity:   ${acc.equity:,.2f}")
                print(f"Margen:   ${acc.margin:,.2f}")
                print(f"Libre:    ${acc.free_margin:,.2f}")
                print(f"Beneficio: ${acc.profit:,.2f}")
                print("-" * 60)

            print(f"\nPosiciones abiertas: {len(positions)}")
            print(f"P&L total: ${total_profit:,.2f}\n")

            # Mostrar las posiciones individuales
            for ticket, (symbol, profit) in sorted(positions.items()):
                status = "[+]" if profit >= 0 else "[-]"
                print(f"{status} #{ticket} {symbol:8s} ${profit:>10,.2f}")

    except KeyboardInterrupt:
        print("\nDeteniendo el panel de control...")

    finally:
        await account.channel.close()


asyncio.run(realtime_pnl_dashboard())
```

### 3) Take Profit automático al alcanzar un objetivo de beneficio

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2


async def auto_take_profit(target_profit: float = 100.0):
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
            # Comprobar si las posiciones actualizadas han alcanzado el objetivo de beneficio
            for pos in update.updated_positions:
                if pos.profit >= target_profit:
                    print(f"\n[OBJETIVO] Beneficio alcanzado para #{pos.ticket}: "
                          f"${pos.profit:.2f}")

                    # Cerrar la posición
                    close_req = trading_pb2.OrderCloseRequest(
                        ticket=pos.ticket,
                        volume=0,  # Cerrar todo
                        deviation=20,
                        comment="Auto TP"
                    )

                    result = await account.order_close(close_req)

                    if result.error.error_type == 0:  # Éxito
                        print(f"[ÉXITO] Posición #{pos.ticket} cerrada")
                    else:
                        print(f"[ERROR] No se pudo cerrar #{pos.ticket}: "
                              f"{result.error.description}")

    except KeyboardInterrupt:
        print("\nDeteniendo el Take Profit automático...")

    finally:
        await account.channel.close()


# Cerrar las posiciones cuando alcancen un beneficio de 100 $
asyncio.run(auto_take_profit(100.0))
```

### 4) Protección mediante límite de pérdidas

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_pb2 as trading_pb2


async def loss_limit_protection(max_loss: float = -50.0):
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
            # Comprobar si hay pérdidas excesivas
            for pos in update.updated_positions:
                if pos.profit <= max_loss:
                    print(f"\n[ADVERTENCIA] Límite de pérdidas superado para #{pos.ticket}: "
                          f"${pos.profit:.2f}")

                    # Cierre de emergencia
                    close_req = trading_pb2.OrderCloseRequest(
                        ticket=pos.ticket,
                        volume=0,
                        deviation=50,  # Permitir un mayor des