# Transmitir ticks de símbolos en tiempo real

> **Solicitud:** suscribirse a los datos de ticks en tiempo real de los símbolos especificados.

**Información de la API:**

- **API de Python:** `MT5Account.on_symbol_tick(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.SubscriptionService`
- **Definición Proto:** `OnSymbolTick` (definido en `mt5-term-api-subscriptions.proto`)

### RPC

- **Servicio:** `mt5_term_api.SubscriptionService`
- **Método:** `OnSymbolTick(OnSymbolTickRequest) -> stream OnSymbolTickReply`
- **Cliente de bajo nivel (generado):** `SubscriptionServiceStub.OnSymbolTick(request, metadata)`

---

## 💬 Lo esencial

- **Qué es.** Flujo de ticks de precios en tiempo real para los símbolos especificados.
- **Para qué sirve.** Supervisar precios en directo, implementar estrategias basadas en ticks y seguir los movimientos del mercado.
- **Alta frecuencia.** Durante los períodos de actividad del mercado, puede generar numerosas actualizaciones por segundo.

---

## 🎯 Propósito

Utilízalo para:

- Supervisar los cambios de precios de los símbolos en tiempo real.
- Implementar estrategias de trading basadas en ticks.
- Seguir los spreads Bid/Ask en tiempo real.
- Crear paneles de precios en directo.
- Detectar inmediatamente los movimientos de precios.
- Recopilar datos de ticks para su análisis.

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def on_symbol_tick(
        self,
        symbols: list[str],
        cancellation_event: Optional[asyncio.Event] = None,
    ):
        """
        Se suscribe a los datos de ticks en tiempo real de los símbolos especificados.

        Yields:
            OnSymbolTickData: Flujo asíncrono de respuestas con datos de ticks.
        """
```

**Mensaje de solicitud:**

```protobuf
message OnSymbolTickRequest {
  repeated string symbol_names = 1;  // Lista de símbolos a los que suscribirse
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbols` | `list[str]` | Nombres de los símbolos a los que suscribirse (por ejemplo, `["EURUSD", "GBPUSD"]`). |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la transmisión (opcional). |

---

## ⬆️ Salida - Generador asíncrono

Devuelve un generador asíncrono que produce objetos `OnSymbolTickData`.

**Campos de OnSymbolTickData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `symbol_tick` | `MrpcSubscriptionMqlTick` | Datos del tick (véase más abajo). |
| `terminal_instance_guid_id` | `str` | Identificador de la instancia del terminal. |

**Campos de MrpcSubscriptionMqlTick:**

| Campo | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` | Nombre del símbolo. |
| `time` | `google.protobuf.Timestamp` | Hora de la última actualización del precio. |
| `time_msc` | `int64` | Hora de la última actualización del precio (en milisegundos). |
| `bid` | `float64` | Precio Bid actual. |
| `ask` | `float64` | Precio Ask actual. |
| `last` | `float64` | Precio de la última operación (Last). |
| `volume` | `uint64` | Volumen correspondiente al precio Last actual. |
| `volume_real` | `float64` | Volumen real correspondiente al precio Last actual. |
| `flags` | `uint32` | Indicadores del tick (indicación de compra/venta). |

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OnSymbolTick - Cómo funciona](../HOW_IT_WORK/6. Streaming_Methods_HOW/on_symbol_tick_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de streaming de `MT5Account` incorporan protección contra errores gRPC transitorios mediante reconexión automática a través de `execute_stream_with_reconnect`.
- **Generador asíncrono:** el método devuelve un generador asíncrono; utiliza `async for` para consumir los datos.
- **Varios símbolos:** puedes suscribirte a varios símbolos dentro de un mismo flujo.
- **Cancelación:** pasa un `asyncio.Event` y llama a `event.set()` para detener el flujo de forma controlada.
- **Alta frecuencia:** los flujos de ticks pueden tener una frecuencia muy elevada; asegúrate de que el procesamiento sea eficiente.
- **Gestión de recursos:** cancela siempre los flujos cuando hayas terminado para liberar recursos.
- **Gestión de errores:** los errores se generan como excepciones; utiliza `try/except` para gestionarlos.
- **Gestión de UUID:** el UUID de la instancia del terminal se genera automáticamente en el servidor si no se proporciona. Para controlarlo explícitamente (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Supervisar los ticks en directo de EURUSD

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_ticks():
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
        # Suscribirse a los ticks de EURUSD
        async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
            tick = tick_data.symbol_tick
            print(f"{tick.symbol}: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, "
                  f"Spread={tick.ask - tick.bid:.5f}")

    except KeyboardInterrupt:
        print("Deteniendo el flujo de ticks...")

    finally:
        await account.channel.close()


# Ejecutar
asyncio.run(monitor_ticks())
```

### 2) Supervisar varios símbolos con cancelación

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_multiple_symbols():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Crear un evento de cancelación
    cancel_event = asyncio.Event()

    # Detener después de 30 segundos
    async def auto_cancel():
        await asyncio.sleep(30)
        cancel_event.set()
        print("\nDeteniendo el flujo...")

    try:
        # Iniciar la tarea de cancelación automática
        cancel_task = asyncio.create_task(auto_cancel())

        # Suscribirse a varios símbolos
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            spread_pips = (tick.ask - tick.bid) * 10000  # Para pares con 4 dígitos

            print(f"[{tick.time_msc}] {tick.symbol}: "
                  f"Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, "
                  f"Spread={spread_pips:.1f} pips")

        await cancel_task

    finally:
        await account.channel.close()


asyncio.run(monitor_multiple_symbols())
```

### 3) Registrar estadísticas del spread Bid-Ask

```python
import asyncio
from collections import defaultdict
from MetaRpcMT5 import MT5Account


async def track_spread_stats():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Almacenamiento de estadísticas
    spreads = defaultdict(list)
    cancel_event = asyncio.Event()

    async def stop_after_duration(seconds):
        await asyncio.sleep(seconds)
        cancel_event.set()

    try:
        # Detener después de 60 segundos
        stop_task = asyncio.create_task(stop_after_duration(60))

        symbols = ["EURUSD", "GBPUSD"]

        async for tick_data in account.on_symbol_tick(
            symbols=symbols,
            cancellation_event=cancel_event
        ):
            tick = tick_data.symbol_tick
            spread = tick.ask - tick.bid
            spreads[tick.symbol].append(spread)

        await stop_task

        # Mostrar estadísticas
        print("\n=== Estadísticas del spread ===")
        for symbol, spread_list in spreads.items():
            avg_spread = sum(spread_list) / len(spread_list)
            min_spread = min(spread_list)
            max_spread = max(spread_list)

            print(f"\n{symbol}:")
            print(f"  Ticks recibidos: {len(spread_list)}")
            print(f"  Spread promedio: {avg_spread * 10000:.1f} pips")
            print(f"  Spread mínimo: {min_spread * 10000:.1f} pips")
            print(f"  Spread máximo: {max_spread * 10000:.1f} pips")

    finally:
        await account.channel.close()


asyncio.run(track_spread_stats())
```

### 4) Sistema de alertas de precios

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def price_alert_system():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    # Configurar alertas de precios
    alerts = {
        "EURUSD": {"above": 1.1000, "below": 1.0900},
        "GBPUSD": {"above": 1.2700, "below": 1.2500},
    }

    triggered = set()

    try:
        async for tick_data in account.on_symbol_tick(
            symbols=list(alerts.keys())
        ):
            tick = tick_data.symbol_tick
            symbol = tick.symbol

            if symbol not in alerts:
                continue

            # Comprobar si se supera el umbral superior
            if tick.bid >= alerts[symbol]["above"]:
                alert_key = f"{symbol}_above"
                if alert_key not in triggered:
                    print(f"\n[ALERTA] El bid de {symbol}, {tick.bid:.5f}, "
                          f"está POR ENCIMA de {alerts[symbol]['above']:.5f}")
                    triggered.add(alert_key)

            # Comprobar si se alcanza el umbral inferior
            if tick.bid <= alerts[symbol]["below"]:
                alert_key = f"{symbol}_below"
                if alert_key not in triggered:
                    print(f"\n[ALERTA] El bid de {symbol}, {tick.bid:.5f}, "
                          f"está POR DEBAJO de {alerts[symbol]['below']:.5f}")
                    triggered.add(alert_key)

            # Detener si se han activado todas las alertas
            if len(triggered) == len(alerts) * 2:
                print("\nTodas las alertas se han activado. Deteniendo...")
                break

    finally:
        await account.channel.close()


asyncio.run(price_alert_system())
```

### 5) Registrar ticks en tiempo real en un archivo CSV

```python
import asyncio
import csv
from datetime import datetime
from MetaRpcMT5 import MT5Account


async def log_ticks_to_csv():
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

    # Detener después de 5 minutos
    async def auto_stop():
        await asyncio.sleep(300)
        cancel_event.set()

    try:
        stop_task = asyncio.create_task(auto_stop())

        # Abrir el archivo CSV
        with open('ticks.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'Symbol', 'Bid', 'Ask', 'Last', 'Volume'])

            tick_count = 0

            async for tick_data in account.on_symbol_tick(
                symbols=["EURUSD"],
                cancellation_event=cancel_event
            ):
                tick = tick_data.symbol_tick

                # Escribir en el archivo CSV
                writer.writerow([
                    datetime.fromtimestamp(tick.time_msc / 1000).isoformat(),
                    tick.symbol,
                    tick.bid,
                    tick.ask,
                    tick.last,
                    tick.volume_real
                ])

                tick_count += 1

                if tick_count % 100 == 0:
                    print(f"Se han registrado {tick_count} ticks...")
                    csvfile.flush()  # Vaciar el búfer al disco

        await stop_task
        print(f"\nTotal de ticks registrados: {tick_count}")

    finally:
        await account.channel.close()


asyncio.run(log_ticks_to_csv())
```

### 6) Supervisar ticks de forma concurrente mediante tareas

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def process_eurusd_ticks(account):
    """Procesar ticks de EURUSD"""
    async for tick_data in account.on_symbol_tick(symbols=["EURUSD"]):
        tick = tick_data.symbol_tick
        print(f"[EUR] {tick.bid:.5f}")
        await asyncio.sleep(0.1)  # Limitar la frecuencia de salida


async def process_gbpusd_ticks(account):
    """Procesar ticks de GBPUSD"""
    async for tick_data in account.on_symbol_tick(symbols=["GBPUSD"]):
        tick = tick_data.symbol_tick
        print(f"[GBP] {tick.bid:.5f}")
        await asyncio.sleep(0.1)  # Limitar la frecuencia de salida


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

    try:
        # Ejecutar varios flujos simultáneamente
        await asyncio.gather(
            process_eurusd_ticks(account),
            process_gbpusd_ticks(account),
        )

    except KeyboardInterrupt:
        print("\nDeteniendo los flujos...")

    finally:
        await account.channel.close()


asyncio.run(main())
```

---

## 📚 Véase también

- [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - obtener una instantánea del tick actual (una sola consulta).
- [OnTrade](./on_trade.md) - transmitir eventos de trading.
- [OnPositionProfit](./on_position_profit.md) - transmitir actualizaciones del beneficio de las posiciones.