

# MT5Account - Profundidad de mercado - Descripción general

> Suscribirse a los datos de profundidad de mercado (DOM), obtenerlos y gestionarlos: supervisar el libro de órdenes, analizar la liquidez y seguir los niveles de compra y venta.

## 📁 Contenido de esta sección

### Operaciones DOM

- **[market_book_add](./market_book_add.md)** - suscribirse a las actualizaciones DOM de un símbolo.
- **[market_book_get](./market_book_get.md)** - obtener los datos DOM actuales.
- **[market_book_release](./market_book_release.md)** - cancelar la suscripción a las actualizaciones DOM.

---

## 📚 Tutoriales paso a paso

**Nota:** Todas las operaciones DOM son métodos asíncronos. Consulta las páginas de cada método para ver ejemplos detallados.

- **[market_book_add](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW.md)** - ejemplos de suscripción.
- **[market_book_get](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_get_HOW.md)** - patrones de análisis DOM.
- **[market_book_release](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW.md)** - ejemplos de liberación de recursos.

---

## 🧭 En términos sencillos

- **market_book_add** -> **suscribirse** a los datos de mercado de Nivel 2 (libro de órdenes).
- **market_book_get** -> **obtener** una instantánea del DOM actual con los niveles de compra y venta.
- **market_book_release** -> **cancelar la suscripción** y liberar los recursos cuando ya no sean necesarios.

> Regla general: **suscribirse una vez** con `market_book_add`, **consultar repetidamente** con `market_book_get` y **liberar los recursos** con `market_book_release`.

---

## Selección rápida

| Si necesitas... | Usar | Devuelve | Parámetros clave |
|---|---|---|---|
| Suscribirte a las actualizaciones DOM | `market_book_add` | MarketBookAddData | symbol |
| Obtener una instantánea del libro de órdenes actual | `market_book_get` | MarketBookGetData | symbol |
| Cancelar la suscripción al DOM | `market_book_release` | MarketBookReleaseData | symbol |
| Analizar la liquidez de compra y venta | `market_book_get` | MarketBookGetData | symbol |
| Supervisar el flujo de órdenes | `market_book_get` | MarketBookGetData | symbol (en un bucle) |
| Encontrar niveles de soporte y resistencia | `market_book_get` | MarketBookGetData | symbol |

---

## ℹ️ Referencias cruzadas y aspectos importantes

- **Compatibilidad del bróker:** no todos los brókeres proporcionan datos DOM. Comprueba la disponibilidad con tu bróker.
- **Suscripción obligatoria:** debes llamar a `market_book_add` antes de utilizar `market_book_get`.
- **El símbolo debe estar seleccionado:** asegúrate de que el símbolo esté en Market Watch antes de suscribirte.
- **Liberar siempre los recursos:** llama a `market_book_release` cuando hayas terminado.
- **Datos vacíos:** devuelve una lista vacía si no hay datos DOM disponibles o si no existe una suscripción activa.
- **Métodos asíncronos:** todas las operaciones DOM son asíncronas; utiliza `await`.
- **Reconexión automática:** todos los métodos incluyen reconexión integrada mediante `execute_with_reconnect`.
- **Por símbolo:** cada símbolo debe suscribirse y cancelar su suscripción por separado.
- **Enum de tipo:** en `MrpcMqlBookInfo`, el tipo 1 corresponde a órdenes SELL y el tipo 2 a órdenes BUY.
- **Campos de volumen:** utiliza `volume_real` (double) en lugar de `volume` (int64).
- **Datos en tiempo real:** el DOM se actualiza en tiempo real. Llama repetidamente a `market_book_get` para supervisarlo.

---

## 🟢 Fragmentos mínimos de código

### Suscribirse al DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account

# Suscribirse al DOM
async def subscribe_dom():
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
        # Suscribirse al DOM de EURUSD
        result = await account.market_book_add("EURUSD")

        if result.opened_successfully:
            print(f"[ÉXITO] Suscripción al DOM de EURUSD realizada")
        else:
            print(f"[ERROR] No se pudo realizar la suscripción")

    finally:
        await account.channel.close()

asyncio.run(subscribe_dom())
```

### Obtener datos DOM

```python
# Obtener datos DOM
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
        # Suscribirse primero
        await account.market_book_add("EURUSD")

        # Obtener una instantánea del DOM
        dom_data = await account.market_book_get("EURUSD")

        print(f"[DOM] EURUSD tiene {len(dom_data.mql_book_infos)} niveles")

        for entry in dom_data.mql_book_infos[:5]:  # Mostrar los primeros 5
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{entry_type:<6} {entry.price:.5f} Vol: {entry.volume_real:.2f}")

    finally:
        await account.channel.close()

asyncio.run(get_dom())
```

### Cancelar la suscripción al DOM

```python
# Cancelar la suscripción al DOM
async def unsubscribe_dom():
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
        # Suscribirse
        await account.market_book_add("EURUSD")

        # Realizar el análisis...
        dom_data = await account.market_book_get("EURUSD")
        print(f"[ANÁLISIS] {len(dom_data.mql_book_infos)} niveles")

        # Cancelar la suscripción cuando se haya terminado
        result = await account.market_book_release("EURUSD")

        if result.closed_successfully:
            print(f"[ÉXITO] Suscripción DOM liberada")

    finally:
        await account.channel.close()

asyncio.run(unsubscribe_dom())
```

### Flujo de trabajo DOM completo

```python
# Flujo de trabajo DOM completo
async def dom_workflow():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbol = "EURUSD"

    try:
        # 1. Suscribirse al DOM
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] No se pudo realizar la suscripción a {symbol}")
            return

        print(f"[1] Suscripción al DOM de {symbol} realizada")

        # 2. Supervisar el DOM durante 10 segundos
        print(f"[2] Supervisando el DOM...")

        for i in range(10):
            dom_data = await account.market_book_get(symbol)

            # Calcular la liquidez
            sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
            buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

            print(f"  [{i+1}/10] Niveles: {len(dom_data.mql_book_infos)}, "
                  f"BUY: {buy_volume:.2f}, SELL: {sell_volume:.2f}")

            await asyncio.sleep(1)

        # 3. Cancelar la suscripción
        release_result = await account.market_book_release(symbol)
        if release_result.closed_successfully:
            print(f"[3] DOM liberado correctamente")

    finally:
        await account.channel.close()

asyncio.run(dom_workflow())
```

### Analizar el spread entre compra y venta

```python
# Analizar el spread entre compra y venta
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

        # Separar las órdenes de compra y venta
        sell_orders = [e for e in dom_data.mql_book_infos if e.type in [0, 2]]
        buy_orders = [e for e in dom_data.mql_book_infos if e.type in [1, 3]]

        if sell_orders and buy_orders:
            best_ask = min(sell_orders, key=lambda x: x.price)
            best_bid = max(buy_orders, key=lambda x: x.price)

            spread = best_ask.price - best_bid.price
            spread_pips = spread / 0.0001

            print(f"[SPREAD] {symbol}")
            print(f"  Mejor Bid: {best_bid.price:.5f}")
            print(f"  Mejor Ask: {best_ask.price:.5f}")
            print(f"  Spread: {spread_pips:.1f} pips")

        # Liberar recursos
        await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(analyze_spread())
```

### Supervisar varios símbolos

```python
# Supervisar varios símbolos
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

    symbols = ["EURUSD", "GBPUSD", "USDJPY"]

    try:
        # Suscribirse a todos los símbolos
        for symbol in symbols:
            result = await account.market_book_add(symbol)
            if result.opened_successfully:
                print(f"[SUSCRITO] {symbol}")

        # Supervisar todos los símbolos
        print("\n[SUPERVISIÓN] DOM de todos los símbolos:")

        for _ in range(5):  # Supervisar durante 5 iteraciones
            print("\n" + "="*50)

            for symbol in symbols:
                dom_data = await account.market_book_get(symbol)

                sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
                buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

                print(f"{symbol:<8} Niveles: {len(dom_data.mql_book_infos):<4} "
                      f"BUY: {buy_volume:>8.2f}  SELL: {sell_volume:>8.2f}")

            await asyncio.sleep(2)

        # Cancelar las suscripciones de todos los símbolos
        print("\n[LIBERACIÓN] Todas las suscripciones...")
        for symbol in symbols:
            await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(monitor_multiple_symbols())
```

### Administrador de contexto para la liberación automática de recursos

```python
# Administrador de contexto para la liberación automática de recursos
from contextlib import asynccontextmanager

@asynccontextmanager
async def dom_subscription(account, symbol):
    """Administrador de contexto para la liberación automática de la suscripción DOM"""
    try:
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"No se pudo realizar la suscripción al DOM de {symbol}")
        yield
    finally:
        await account.market_book_release(symbol)


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
        # El DOM se libera automáticamente al salir del bloque
        async with dom_subscription(account, "EURUSD"):
            dom_data = await account.market_book_get("EURUSD")
            print(f"[DOM] {len(dom_data.mql_book_infos)} niveles")

    finally:
        await account.channel.close()

asyncio.run(main())
```

### Encontrar niveles clave de liquidez

```python
# Encontrar niveles clave de liquidez
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
        sorted_levels = sorted(dom_data.mql_book_infos,
                                key=lambda x: x.volume_real,
                                reverse=True)

        print(f"[NIVELES CLAVE] {symbol} - Los 5 niveles con mayor volumen:\n")

        for i, entry in enumerate(sorted_levels[:5], 1):
            entry_type = "SELL" if entry.type in [0, 2] else "BUY"
            print(f"{i}. {entry_type:<6} {entry.price:.5f} - {entry.volume_real:.2f} lotes")

        # Liberar recursos
        await account.market_book_release(symbol)

    finally:
        await account.channel.close()

asyncio.run(find_key_levels())
```

---

## 📚 Véase también

- **Símbolos:** [symbol_select](../2.%20Symbol_Information/symbol_select.md) - añadir un símbolo a Market Watch antes de suscribirse.
- **Precios:** [symbol_info_tick](../2.%20Symbol_Information/symbol_info_tick.md) - obtener los precios actuales del tick.
- **Transmisión de datos:** [on_symbol_tick](../6.%20Streaming_Methods/on_symbol_tick.md) - flujo de ticks en tiempo real.

