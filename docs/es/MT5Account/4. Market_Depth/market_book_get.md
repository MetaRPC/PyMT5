# Obtener datos de profundidad de mercado

> **Solicitud:** Obtener los datos actuales de profundidad de mercado (libro de órdenes) de un símbolo suscrito.

**Información de la API:**

- **API de Python:** `MT5Account.market_book_get(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `MarketBookGet` (definido en `mt5-term-api-market-info.proto`)
- **Enums en este método:** 1 enum con 4 constantes (1 de salida)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `MarketBookGet(MarketBookGetRequest) -> MarketBookGetReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.MarketBookGet(request, metadata)`

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def market_book_get(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookGetData:
        """
        Obtiene los datos actuales de profundidad de mercado (DOM) de un símbolo.

        Returns:
            MarketBookGetData: Una lista de entradas del libro de órdenes del DOM del símbolo.
        """
```

**Mensaje de solicitud:**

```protobuf
MarketBookGetRequest {
  string symbol = 1;  // Nombre del símbolo
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` | Nombre del símbolo (por ejemplo, "EURUSD") |
| `deadline` | `Optional[datetime]` | Plazo límite de la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

---

## ⬆️ Salida

Devuelve un objeto `MarketBookGetData`.

**Campos de `MarketBookGetData`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `mql_book_infos` | `list[MrpcMqlBookInfo]` | Lista de entradas del libro de órdenes |

**Campos de `MrpcMqlBookInfo`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `type` | `BookType` | Tipo de orden (enum) |
| `price` | `double` | Nivel de precio |
| `volume` | `int64` | Volumen en lotes (legado) |
| `volume_real` | `double` | Volumen real en lotes |

---

## 🧱 Enums relacionados (del proto)

### `BookType`

Se utiliza en `MrpcMqlBookInfo` para indicar el tipo de entrada del libro de órdenes.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `BOOK_TYPE_SELL` | 0 | Orden de venta |
| `BOOK_TYPE_BUY` | 1 | Orden de compra |
| `BOOK_TYPE_SELL_MARKET` | 2 | Orden de venta al precio de mercado |
| `BOOK_TYPE_BUY_MARKET` | 3 | Orden de compra al precio de mercado |

**Uso:**

```python
from MetaRpcMT5 import mt5_term_api_market_info_pb2 as market_pb2


# Acceder a los valores del enum

market_pb2.BOOK_TYPE_SELL        # = 0
market_pb2.BOOK_TYPE_BUY         # = 1
```

---

## 💬 Lo esencial

- **Qué es.** Obtiene los datos actuales del mercado de Nivel 2 (libro de órdenes) de un símbolo.
- **Para qué sirve.** Analizar la profundidad del mercado, la liquidez de compra/venta y el flujo de órdenes.
- **Se requiere una suscripción.** Primero se debe llamar a `market_book_add`.

---

## 🎯 Finalidad

Utilízalo para:

- Obtener una instantánea actual del DOM.
- Analizar los niveles de liquidez de compra y venta.
- Supervisar la profundidad del libro de órdenes.
- Identificar zonas de soporte y resistencia.
- Calcular el volumen en los distintos niveles de precio.
- Detectar órdenes grandes (detección de órdenes iceberg).
- Analizar la microestructura del mercado.

---

## 📚 Tutorial

Para obtener una explicación detallada, línea por línea y con ejemplos, consulta:

**[MarketBookGet - Cómo funciona](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incorporan protección contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Se requiere una suscripción:** Es necesario llamar a `market_book_add` antes de utilizar este método.
- **Datos vacíos:** Devuelve una lista vacía si no hay datos DOM disponibles.
- **Compatibilidad del bróker:** No todos los brókeres proporcionan datos DOM.
- **Instantánea en tiempo real:** Devuelve el estado actual en el momento de la solicitud.
- **Campos de volumen:** Utiliza `volume_real` (`double`) en lugar de `volume` (`int64`).
- **Niveles de precio:** Están ordenados por precio (mejor oferta de compra/venta primero).

---

## 🔗 Ejemplos de uso

### 1) Obtener los datos actuales del DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def get_dom():
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
        # Primero, suscribirse al DOM
        await account.market_book_add("EURUSD")

        # Obtener los datos DOM
        dom_data = await account.market_book_get("EURUSD")

        print(f"[DOM] Profundidad de mercado de EURUSD:")
        print(f"Niveles totales: {len(dom_data.mql_book_infos)}\n")

        print(f"{'Tipo':<10} {'Precio':<15} {'Volumen':<15}")
        print("-" * 45)

        for entry in dom_data.mql_book_infos[:10]:  # Mostrar los primeros 10 niveles
            entry_type = "VENTA" if entry.type in [0, 2] else "COMPRA"
            print(f"{entry_type:<10} {entry.price:<15.5f} {entry.volume_real:<15.2f}")

    finally:
        await account.channel.close()


asyncio.run(get_dom())
```

### 2) Analizar el diferencial entre compra y venta (spread)

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def analyze_spread():
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
        symbol = "EURUSD"

        # Suscribirse y obtener el DOM
        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        if not dom_data.mql_book_infos:
            print(f"[ADVERTENCIA] No hay datos DOM disponibles para {symbol}")
            return

        # Separar las órdenes de compra y venta
        sell_orders = [e for e in dom_data.mql_book_infos if e.type in [0, 2]]
        buy_orders = [e for e in dom_data.mql_book_infos if e.type in [1, 3]]

        if sell_orders and buy_orders:
            best_ask = min(sell_orders, key=lambda x: x.price)
            best_bid = max(buy_orders, key=lambda x: x.price)

            spread = best_ask.price - best_bid.price
            spread_pips = spread / 0.0001

            print(f"[ANÁLISIS DEL SPREAD] {symbol}")
            print(f"  Mejor Bid: {best_bid.price:.5f} (Volumen: {best_bid.volume_real:.2f})")
            print(f"  Mejor Ask: {best_ask.price:.5f} (Volumen: {best_ask.volume_real:.2f})")
            print(f"  Spread: {spread:.5f} ({spread_pips:.1f} pips)")

    finally:
        await account.channel.close()


asyncio.run(analyze_spread())
```

### 3) Calcular la liquidez total

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def calculate_liquidity():
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
        symbol = "EURUSD"

        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Calcular el volumen total por lado
        sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
        buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])
        total_volume = sell_volume + buy_volume

        print(f"[LIQUIDEZ] {symbol}")
        print(f"  Niveles DOM totales: {len(dom_data.mql_book_infos)}")
        print(f"  Volumen del lado COMPRA: {buy_volume:.2f} lotes")
        print(f"  Volumen del lado VENTA: {sell_volume:.2f} lotes")
        print(f"  Volumen total: {total_volume:.2f} lotes")

        if total_volume > 0:
            buy_percent = (buy_volume / total_volume) * 100
            sell_percent = (sell_volume / total_volume) * 100
            print(f"\n  COMPRA: {buy_percent:.1f}% | VENTA: {sell_percent:.1f}%")

            if buy_percent > 60:
                print("  [SEÑAL] Fuerte liquidez del lado de COMPRA")
            elif sell_percent > 60:
                print("  [SEÑAL] Fuerte liquidez del lado de VENTA")
            else:
                print("  [SEÑAL] Liquidez equilibrada")

    finally:
        await account.channel.close()


asyncio.run(calculate_liquidity())
```

### 4) Encontrar niveles de soporte y resistencia

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def find_key_levels():
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
        symbol = "EURUSD"

        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Encontrar los 5 niveles con mayor volumen
        sorted_levels = sorted(dom_data.mql_book_infos, key=lambda x: x.volume_real, reverse=True)

        print(f"[NIVELES CLAVE] {symbol} - Niveles con mayor volumen:\n")
        print(f"{'Posición':<6} {'Tipo':<10} {'Precio':<15} {'Volumen':<15}")
        print("-" * 50)

        for i, entry in enumerate(sorted_levels[:5], 1):
            entry_type = "VENTA" if entry.type in [0, 2] else "COMPRA"
            print(f"{i:<6} {entry_type:<10} {entry.price:<15.5f} {entry.volume_real:<15.2f}")

        print("\n[NOTA] Las concentraciones de gran volumen pueden actuar como niveles de soporte o resistencia")

    finally:
        await account.channel.close()


asyncio.run(find_key_levels())
```

### 5) Supervisar el desequilibrio del DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_imbalance(duration: int = 30):
    """Supervisa el desequilibrio del DOM durante el período especificado"""
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
        symbol = "EURUSD"

        await account.market_book_add(symbol)
        print(f"[SUPERVISIÓN] Desequilibrio del DOM de {symbol} durante {duration} segundos\n")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            dom_data = await account.market_book_get(symbol)

            # Calcular el desequilibrio
            sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
            buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

            if sell_volume + buy_volume > 0:
                imbalance = ((buy_volume - sell_volume) / (buy_volume + sell_volume)) * 100

                # Limpiar la pantalla
                print("\033[2J\033[H")

                print(f"=== Desequilibrio del DOM de {symbol} ===\n")
                print(f"COMPRA: {buy_volume:>8.2f} lotes")
                print(f"VENTA:  {sell_volume:>8.2f} lotes")
                print(f"\nDesequilibrio: {imbalance:+.2f}%")

                if imbalance > 20:
                    print("\n[SEÑAL] Fuerte presión compradora")
                elif imbalance < -20:
                    print("\n[SEÑAL] Fuerte presión vendedora")
                else:
                    print("\n[SEÑAL] Mercado equilibrado")

            await asyncio.sleep(1)

        await account.market_book_release(symbol)
        print(f"\n[DETENIDO] La supervisión ha finalizado")

    finally:
        await account.channel.close()


asyncio.run(monitor_imbalance(duration=30))
```

### 6) Análisis del volumen por precio (VAP)

```python
import asyncio
from MetaRpcMT5 import MT5Account
from collections import defaultdict


async def volume_at_price():
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
        symbol = "EURUSD"

        await account.market_book_add(symbol)
        dom_data = await account.market_book_get(symbol)

        # Agrupar el volumen por intervalos de precio (por ejemplo, rangos de 5 pips)
        pip_range = 5
        pip_size = 0.0001
        bin_size = pip_range * pip_size

        volume_bins = defaultdict(float)

        for entry in dom_data.mql_book_infos:
            # Redondear el precio al intervalo más cercano
            bin_price = round(entry.price / bin_size) * bin_size
            volume_bins[bin_price] += entry.volume_real

        # Ordenar por precio
        sorted_bins = sorted(volume_bins.items(), key=lambda x: x[0])

        print(f"[VOLUMEN POR PRECIO] {symbol} (intervalos de {pip_range} pips)\n")
        print(f"{'Rango de precios':<20} {'Volumen':<15} {'Barra':<30}")
        print("-" * 70)

        max_volume = max(volume_bins.values()) if volume_bins else 1

        for price, volume in sorted_bins[:15]:  # Mostrar los 15 primeros intervalos
            bar_length = int((volume / max_volume) * 30)
            bar = "#" * bar_length
            print(f"{price:.5f}-{price+bin_size:.5f}  {volume:>8.2f} lotes  {bar}")

    finally:
        await account.channel.close()


asyncio.run(volume_at_price())
```

---

## 📚 Véase también

- [MarketBookAdd](./market_book_add.md) - Suscribirse a las actualizaciones del DOM.
- [MarketBookRelease](./market_book_release.md) - Cancelar la suscripción al DOM.
- [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Obtener los precios actuales de los ticks.