# Cancelar la suscripción a la profundidad de mercado

> **Solicitud:** Cancelar la suscripción a las actualizaciones de profundidad de mercado (libro de órdenes) de un símbolo.

**Información de la API:**

- **API de Python:** `MT5Account.market_book_release(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.MarketInfo`
- **Definición Proto:** `MarketBookRelease` (definido en `mt5-term-api-market-info.proto`)
- **Enums en este método:** 0 enums (resultado booleano simple)

### RPC

- **Servicio:** `mt5_term_api.MarketInfo`
- **Método:** `MarketBookRelease(MarketBookReleaseRequest) -> MarketBookReleaseReply`
- **Cliente de bajo nivel (generado):** `MarketInfoStub.MarketBookRelease(request, metadata)`

```python
from MetaRpcMT5 import MT5Account


class MT5Account:
    # ...

    async def market_book_release(
        self,
        symbol: str,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> market_info_pb2.MarketBookReleaseData:
        """
        Cierra la profundidad de mercado (DOM) de un símbolo y cancela la suscripción a sus actualizaciones.

        Returns:
            MarketBookReleaseData: Resultado de la cancelación de la suscripción.
        """
```

**Mensaje de solicitud:**

```protobuf
MarketBookReleaseRequest {
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

Devuelve un objeto `MarketBookReleaseData`.

**Campos de `MarketBookReleaseData`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `closed_successfully` | `bool` | True si la cancelación de la suscripción se realizó correctamente |

---

## 💬 Lo esencial

- **Qué es.** Cancela la suscripción a los datos de mercado de Nivel 2 (libro de órdenes) de un símbolo.
- **Para qué sirve.** Liberar recursos y dejar de recibir actualizaciones del DOM cuando ya no sean necesarias.
- **Buena práctica.** Llama siempre a este método cuando termines de supervisar el DOM para liberar recursos.

---

## 🎯 Finalidad

Utilízalo para:

- Cancelar la suscripción a las actualizaciones del DOM.
- Liberar recursos del sistema.
- Realizar la limpieza después del análisis del DOM.
- Detener la supervisión de la profundidad de mercado.
- Gestionar el ciclo de vida de las suscripciones.
- Reducir el uso del ancho de banda.

---

## 📚 Tutorial

Para obtener una explicación detallada, línea por línea y con ejemplos, consulta:

**[MarketBookRelease - Cómo funciona](../HOW_IT_WORK/4. Market_Depth(DOM)_HOW/market_book_release_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incorporan protección contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Liberación de recursos:** Llama siempre a este método cuando termines de supervisar el DOM.
- **Sin errores si no hay suscripción:** Es seguro llamar al método incluso si no existe una suscripción activa.
- **Por símbolo:** Cada símbolo debe liberarse por separado.
- **Emparejado con add:** Cada llamada a `market_book_add` debe tener su correspondiente llamada a `market_book_release`.
- **Limpieza de sesión:** Las suscripciones permanecen activas hasta que se cancelan explícitamente o finaliza la sesión.
- **Comprobar el resultado:** Verifica siempre que `closed_successfully == True`.

---

## 🔗 Ejemplos de uso

### 1) Cancelación básica de la suscripción

```python
import asyncio
from MetaRpcMT5 import MT5Account


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
        symbol = "EURUSD"

        # Suscribirse al DOM
        add_result = await account.market_book_add(symbol)
        if add_result.opened_successfully:
            print(f"[SUSCRITO] DOM de {symbol}")

        # Realizar el análisis...
        dom_data = await account.market_book_get(symbol)
        print(f"[ANÁLISIS] {len(dom_data.mql_book_infos)} niveles DOM")

        # Cancelar la suscripción al terminar
        release_result = await account.market_book_release(symbol)
        if release_result.closed_successfully:
            print(f"[CANCELACIÓN] Suscripción al DOM de {symbol} liberada")

    finally:
        await account.channel.close()


asyncio.run(unsubscribe_dom())
```

### 2) Patrón con administrador de contexto

```python
import asyncio
from MetaRpcMT5 import MT5Account
from contextlib import asynccontextmanager


@asynccontextmanager
async def dom_subscription(account, symbol):
    """Administrador de contexto para la limpieza automática de la suscripción DOM"""
    try:
        # Suscribirse
        result = await account.market_book_add(symbol)
        if not result.opened_successfully:
            raise Exception(f"No se pudo suscribir al DOM de {symbol}")

        print(f"[SUSCRITO] DOM de {symbol}")
        yield

    finally:
        # Liberar siempre al salir
        await account.market_book_release(symbol)
        print(f"[LIBERADO] DOM de {symbol}")


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
        async with dom_subscription(account, "EURUSD"):
            # El DOM está activo aquí
            dom_data = await account.market_book_get("EURUSD")
            print(f"[ANÁLISIS] {len(dom_data.mql_book_infos)} niveles DOM")
        # El DOM se libera automáticamente aquí

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 3) Liberar varios símbolos

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def release_multiple_symbols():
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
        # Suscribirse a varios símbolos
        print("[SUSCRIPCIÓN] Suscribiéndose a varios símbolos...")
        for symbol in symbols:
            result = await account.market_book_add(symbol)
            if result.opened_successfully:
                print(f"  [OK] Suscripción a {symbol} realizada")

        # Realizar el análisis...
        await asyncio.sleep(5)

        # Liberar todos los símbolos
        print("\n[LIBERACIÓN] Liberando todas las suscripciones...")
        for symbol in symbols:
            result = await account.market_book_release(symbol)
            if result.closed_successfully:
                print(f"  [OK] {symbol} liberado")

    finally:
        await account.channel.close()


asyncio.run(release_multiple_symbols())
```

### 4) Gestión de errores y limpieza

```python
import asyncio
from MetaRpcMT5 import MT5Account, ApiExceptionMT5


async def safe_dom_usage():
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
    subscribed = False

    try:
        # Suscribirse
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] No se pudo suscribir a {symbol}")
            return

        subscribed = True
        print(f"[SUSCRITO] DOM de {symbol}")

        # Realizar el análisis
        dom_data = await account.market_book_get(symbol)
        print(f"[ANÁLISIS] {len(dom_data.mql_book_infos)} niveles")

    except ApiExceptionMT5 as e:
        print(f"[ERROR DE API] {e}")

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")

    finally:
        # Realizar siempre la limpieza si existe una suscripción
        if subscribed:
            try:
                release_result = await account.market_book_release(symbol)
                if release_result.closed_successfully:
                    print(f"[LIMPIEZA] DOM de {symbol} liberado correctamente")
                else:
                    print(f"[ADVERTENCIA] No se pudo liberar el DOM de {symbol}")
            except Exception as e:
                print(f"[ERROR DE LIMPIEZA] {e}")

        await account.channel.close()


asyncio.run(safe_dom_usage())
```

### 5) Clase administradora de suscripciones

```python
import asyncio
from MetaRpcMT5 import MT5Account


class DOMSubscriptionManager:
    def __init__(self, account):
        self.account = account
        self.active_subscriptions = set()

    async def subscribe(self, symbol: str):
        """Suscribirse al DOM y registrar la suscripción"""
        result = await self.account.market_book_add(symbol)

        if result.opened_successfully:
            self.active_subscriptions.add(symbol)
            print(f"[SUSCRITO] {symbol} (Total: {len(self.active_subscriptions)})")
            return True
        else:
            print(f"[ERROR] No se pudo suscribir a {symbol}")
            return False

    async def unsubscribe(self, symbol: str):
        """Cancelar la suscripción al DOM"""
        if symbol not in self.active_subscriptions:
            print(f"[ADVERTENCIA] {symbol} no está entre las suscripciones activas")
            return False

        result = await self.account.market_book_release(symbol)

        if result.closed_successfully:
            self.active_subscriptions.remove(symbol)
            print(f"[CANCELACIÓN] {symbol} (Restantes: {len(self.active_subscriptions)})")
            return True
        else:
            print(f"[ERROR] No se pudo cancelar la suscripción de {symbol}")
            return False

    async def release_all(self):
        """Liberar todas las suscripciones activas"""
        print(f"[LIBERACIÓN] Liberando las {len(self.active_subscriptions)} suscripciones...")

        for symbol in list(self.active_subscriptions):
            await self.unsubscribe(symbol)

        print(f"[FINALIZADO] Todas las suscripciones han sido liberadas")

    def list_active(self):
        """Enumerar todas las suscripciones activas"""
        return list(self.active_subscriptions)


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

    manager = DOMSubscriptionManager(account)

    try:
        # Suscribirse a varios símbolos
        await manager.subscribe("EURUSD")
        await manager.subscribe("GBPUSD")
        await manager.subscribe("USDJPY")

        print(f"\n[ACTIVAS] Suscripciones: {manager.list_active()}")

        # Realizar el análisis...
        await asyncio.sleep(5)

        # Liberar un símbolo específico
        await manager.unsubscribe("GBPUSD")

        # Liberar todas las suscripciones restantes
        await manager.release_all()

    finally:
        await account.channel.close()


asyncio.run(main())
```

### 6) Función auxiliar para obtener una instantánea temporal del DOM

```python
import asyncio
from MetaRpcMT5 import MT5Account


async def get_dom_snapshot(account, symbol: str):
    """
    Función auxiliar para obtener rápidamente una instantánea del DOM con limpieza automática.
    Suscribirse -> Obtener datos -> Liberar
    """
    try:
        # Suscribirse
        add_result = await account.market_book_add(symbol)
        if not add_result.opened_successfully:
            print(f"[ERROR] No se pudo suscribir a {symbol}")
            return None

        # Obtener los datos DOM
        dom_data = await account.market_book_get(symbol)

        return dom_data

    finally:
        # Liberar siempre
        try:
            await account.market_book_release(symbol)
        except Exception as e:
            print(f"[ADVERTENCIA] Error durante la limpieza: {e}")


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
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        for symbol in symbols:
            print(f"\n[INSTANTÁNEA] Obteniendo el DOM de {symbol}...")

            dom_data = await get_dom_snapshot(account, symbol)

            if dom_data:
                sell_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [0, 2])
                buy_volume = sum(e.volume_real for e in dom_data.mql_book_infos if e.type in [1, 3])

                print(f"  Niveles: {len(dom_data.mql_book_infos)}")
                print(f"  Volumen de COMPRA: {buy_volume:.2f} lotes")
                print(f"  Volumen de VENTA: {sell_volume:.2f} lotes")

            await asyncio.sleep(1)  # Breve pausa entre instantáneas

    finally:
        await account.channel.close()


asyncio.run(main())
```

---

## 📚 Véase también

- [MarketBookAdd](./market_book_add.md) - Suscribirse a las actualizaciones del DOM.
- [MarketBookGet](./market_book_get.md) - Obtener los datos del DOM.
- [SymbolSelect](../2.%20Symbol_Information/symbol_select.md) - Gestionar los símbolos de Market Watch.