# Suscribirse a la profundidad de mercado (DOM)

> **Solicitud:** suscribirse a las actualizaciones de la profundidad de mercado (libro de órdenes) de un símbolo.

**Información de la API:**

- **API de Python:** `MT5Account.market_book_add(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `MarketBookAdd` (definido en `mt5-term-api-market-info.proto`)
- **Enums de este método:** 0 enums (resultado booleano simple)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `MarketBookAdd(MarketBookAddRequest) -> MarketBookAddReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.MarketBookAdd(request, metadata)`

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def market_book_add(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookAddData:
        """
        Abre la profundidad de mercado (DOM) de un símbolo y se suscribe a sus actualizaciones.

        Returns:
            MarketBookAddData: resultado de la suscripción.
        """
```

**Mensaje de solicitud:**

```protobuf
MarketBookAddRequest {
    string symbol = 1;  // Nombre del símbolo
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `symbol` | `str` | Nombre del símbolo (por ejemplo, "EURUSD") |
| `deadline` | `Optional[datetime]` | Fecha límite de la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

---

## ⬆️ Salida

Devuelve un objeto `MarketBookAddData`.

**Campos de `MarketBookAddData`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `opened_successfully` | `bool` | True si la suscripción se ha realizado correctamente |

---

## 💬 Lo esencial

- **Qué es.** Se suscribe a los datos de mercado de nivel 2 (libro de órdenes) de un símbolo.
- **Por qué lo necesitas.** Es necesario antes de poder llamar a `market_book_get` para obtener los datos del DOM.
- **Suscripción única.** Llama al método una vez por símbolo y, después, utiliza `market_book_get` para obtener los datos.

---

## 🎯 Propósito

Utiliza este método para:

- Suscribirte a las actualizaciones de la profundidad de mercado (DOM).
- Habilitar el acceso a los datos de nivel 2 de un símbolo.
- Prepararte para analizar el libro de órdenes.
- Supervisar los niveles de liquidez de compra y venta (bid/ask).
- Analizar la microestructura del mercado.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[market_book_add - Cómo funciona](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_add_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** todos los métodos de `MT5Account` cuentan con protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Suscripción obligatoria:** debes llamar a este método antes de utilizar `market_book_get`.
- **El símbolo debe estar seleccionado:** asegúrate de que el símbolo esté en Market Watch antes de suscribirte.
- **Compatibilidad del bróker:** no todos los brókeres proporcionan datos DOM.
- **Liberación de recursos:** cuando termines, llama a `market_book_release` para cancelar la suscripción.
- **Una suscripción:** solo necesitas suscribirte una vez por símbolo.
- **Comprobar el resultado:** verifica siempre que `opened_successfully == True`.

---

## 🔗 Ejemplos de uso

### 1) Suscribirse al DOM de EURUSD

```python
import asyncio
from MetaRpcMT5 import MT5Account


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
        # Suscribirse al DOM
        result = await account.market_book_add("EURUSD")

        if result.opened_successfully:
            print(f"[SUCCESS] Suscripción al DOM de EURUSD realizada")
        else:
            print(f"[FAILED] No se pudo suscribir al DOM")

    finally:
        await account.channel.close()


asyncio.run(subscribe_dom())
```

### 2) Suscribirse y verificar

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def subscribe_and_verify():
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

        # Primero, asegúrate de que el símbolo esté seleccionado en Market Watch
        await account.symbol_select(symbol=symbol, select=True)
        print(f"[1] Símbolo {symbol} seleccionado en Market Watch")

        # Ahora, suscribirse al DOM
        result = await account.market_book_add(symbol)

        if result.opened_successfully:
            print(f"[2] Suscripción al DOM de {symbol} realizada correctamente")

            # Verificar obteniendo los datos del DOM
            dom_data = await account.market_book_get(symbol)
            print(f"[3] El DOM contiene {len(dom_data.mql_book_infos)} niveles")
        else:
            print(f"[2] No se pudo realizar la suscripción al DOM")

    finally:
        await account.channel.close()


asyncio.run(subscribe_and_verify())
```

### 3) Suscribirse a varios símbolos

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def subscribe_multiple():
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
        for symbol in symbols:
            result = await account.market_book_add(symbol)

            if result.opened_successfully:
                print(f"[OK] {symbol} - Suscripción al DOM realizada")
            else:
                print(f"[FAIL] {symbol} - No se pudo realizar la suscripción")

    finally:
        await account.channel.close()


asyncio.run(subscribe_multiple())
```

### 4) Suscribirse con gestión de errores

```python
import asyncio
from MetaRpcMT5 import MT5Account, ApiExceptionMT5


async def subscribe_with_error_handling():
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
        # Suscribirse al DOM
        result = await account.market_book_add(symbol)

        if result.opened_successfully:
            print(f"[SUCCESS] Suscripción al DOM de {symbol} realizada")
            return True
        else:
            print(f"[WARNING] La suscripción devolvió False")
            return False

    except ApiExceptionMT5 as e:
        print(f"[API ERROR] {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

    finally:
        await account.channel.close()


asyncio.run(subscribe_with_error_handling())
```

### 5) Comprobar la compatibilidad del DOM del bróker

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def check_dom_support():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]

    try:
        print("Comprobando la compatibilidad del DOM para los símbolos:\n")
        print(f"{'Símbolo':<10} {'Compatibilidad DOM':<15}")
        print("-" * 30)

        for symbol in test_symbols:
            try:
                result = await account.market_book_add(symbol)

                if result.opened_successfully:
                    # Intentar obtener los datos del DOM
                    dom_data = await account.market_book_get(symbol)

                    if len(dom_data.mql_book_infos) > 0:
                        print(f"{symbol:<10} {'SÍ ('+str(len(dom_data.mql_book_infos))+' niveles)':<15}")
                    else:
                        print(f"{symbol:<10} {'SIN DATOS':<15}")

                    # Liberar los recursos
                    await account.market_book_release(symbol)
                else:
                    print(f"{symbol:<10} {'NO COMPATIBLE':<15}")

            except Exception as e:
                print(f"{symbol:<10} {'ERROR':<15}")

    finally:
        await account.channel.close()


asyncio.run(check_dom_support())
```

### 6) Suscribirse y supervisar el DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def monitor_dom(symbol: str, duration: int = 10):
    """Se suscribe y supervisa el DOM durante el tiempo especificado"""
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
        # Suscribirse al DOM
        result = await account.market_book_add(symbol)

        if not result.opened_successfully:
            print(f"[FAILED] No se pudo suscribir al DOM de {symbol}")
            return

        print(f"[SUBSCRIBED] Supervisando el DOM de {symbol} durante {duration} segundos\n")

        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < duration:
            # Obtener el estado actual del DOM
            dom_data = await account.market_book_get(symbol)

            # Limpiar la pantalla
            print("\033[2J\033[H")

            print(f"=== Profundidad de mercado de {symbol} ===")
            print(f"Número total de niveles: {len(dom_data.mql_book_infos)}\n")

            print(f"{'Tipo':<10} {'Precio':<15} {'Volumen':<15}")
            print("-" * 45)

            for book_entry in dom_data.mql_book_infos[:10]:  # Mostrar los primeros 10 niveles
                entry_type = "BUY" if book_entry.type in [1, 3] else "SELL"
                print(f"{entry_type:<10} {book_entry.price:<15.5f} {book_entry.volume_real:<15.2f}")

            await asyncio.sleep(1)  # Actualizar cada segundo

        # Cancelar la suscripción al terminar
        await account.market_book_release(symbol)
        print(f"\n[UNSUBSCRIBED] Se ha detenido la supervisión del DOM de {symbol}")

    finally:
        await account.channel.close()


asyncio.run(monitor_dom("EURUSD", duration=10))
```

---

## 📚 Véase también

- [MarketBookGet](./market_book_get.md) - Obtener los datos actuales del DOM
- [MarketBookRelease](./market_book_release.md) - Cancelar la suscripción al DOM
- [SymbolSelect](../2.%20Symbol_Information/symbol_select.md) - Añadir un símbolo a Market Watch