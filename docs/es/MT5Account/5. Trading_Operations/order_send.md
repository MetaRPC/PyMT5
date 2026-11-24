# Enviar una orden de mercado o pendiente

> **Solicitud:** Enviar una orden de mercado o pendiente al servidor de trading.

**Información de la API:**

- **API de Python:** `MT5Account.order_send(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradingHelper`
- **Definición Proto:** `OrderSend` (definido en `mt5-term-api-trading-helper.proto`)
- **Enums de este método:** 2 enums con 13 constantes (2 de entrada)

### RPC

- **Servicio:** `mt5_term_api.TradingHelper`
- **Método:** `OrderSend(OrderSendRequest) -> OrderSendReply`
- **Cliente de bajo nivel (generado):** `TradingHelperStub.OrderSend(request, metadata)`

---

## 💬 Lo esencial

- **Qué es:** Envía órdenes de mercado o pendientes al servidor de trading de MT5.
- **Para qué sirve:** Es el método principal para abrir posiciones y colocar órdenes pendientes.
- **Código de éxito:** El código de retorno 10009 indica que la operación se ha realizado correctamente.

---

## 🎯 Propósito

Utiliza este método para:

- Abrir posiciones de mercado (BUY o SELL).
- Colocar órdenes pendientes (LIMIT, STOP, STOP_LIMIT).
- Establecer niveles de Stop Loss y Take Profit.
- Especificar el vencimiento de una orden.
- Añadir comentarios y números mágicos a las órdenes.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**[OrderSend - Cómo funciona](../HOW_IT_WORK/5. Trading_Operations_HOW/order_send_HOW.md)**

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


class MT5Account:
    # ...

    async def order_send(
        self,
        request: trading_pb2.OrderSendRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trading_pb2.OrderSendData:
        """
        Envía una orden de mercado o pendiente al servidor de trading de forma asíncrona.

        Returns:
            OrderSendData: Respuesta con los datos de confirmación de la operación/orden.
        """
```

**Mensaje de solicitud:**

```protobuf
message OrderSendRequest {
  string symbol = 1;                              // Símbolo de trading
  TMT5_ENUM_ORDER_TYPE operation = 2;             // Tipo de orden (BUY, SELL, BUY_LIMIT, etc.)
  double volume = 3;                              // Volumen de la orden en lotes
  double price = 4;                               // Precio de la orden (para órdenes pendientes)
  uint64 slippage = 5;                             // Deslizamiento máximo en puntos
  double stop_loss = 6;                            // Precio de Stop Loss (opcional)
  double take_profit = 7;                          // Precio de Take Profit (opcional)
  string comment = 8;                              // Comentario de la orden
  uint64 expert_id = 9;                            // ID del Asesor Experto (número mágico)
  double stop_limit_price = 10;                    // Precio Stop Limit (para órdenes STOP_LIMIT)
  TMT5_ENUM_ORDER_TYPE_TIME expiration_time_type = 11;  // Tipo de vencimiento (GTC, DAY, etc.)
  google.protobuf.Timestamp expiration_time = 12;       // Fecha y hora de vencimiento
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `OrderSendRequest` | Solicitud de orden (véanse los campos anteriores) |
| `deadline` | `Optional[datetime]` | Límite de tiempo para la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

---

## ⬆️ Salida

Devuelve un objeto `OrderSendData`.

**Campos de OrderSendData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `returned_code` | `uint32` | Código de retorno (10009 = éxito) |
| `deal` | `uint32` | Ticket de la operación (para órdenes de mercado) |
| `order` | `uint32` | Ticket de la orden (para órdenes pendientes) |
| `volume` | `double` | Volumen ejecutado |
| `price` | `double` | Precio de ejecución |
| `bid` | `double` | Precio Bid actual |
| `ask` | `double` | Precio Ask actual |
| `comment` | `string` | Comentario del bróker |
| `request_id` | `uint32` | ID de la solicitud |
| `ret_code_external` | `uint64` | Código de retorno externo |
| `returned_string_code` | `string` | Código de retorno en formato de cadena |
| `returned_code_description` | `string` | Descripción del código de retorno |

---

## 🧱 Enums relacionados (de proto)

### `TMT5_ENUM_ORDER_TYPE`

Se utiliza en `OrderSendRequest` para especificar el tipo de orden.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `TMT5_ORDER_TYPE_BUY` | 0 | Orden de compra a mercado |
| `TMT5_ORDER_TYPE_SELL` | 1 | Orden de venta a mercado |
| `TMT5_ORDER_TYPE_BUY_LIMIT` | 2 | Orden pendiente Buy Limit |
| `TMT5_ORDER_TYPE_SELL_LIMIT` | 3 | Orden pendiente Sell Limit |
| `TMT5_ORDER_TYPE_BUY_STOP` | 4 | Orden pendiente Buy Stop |
| `TMT5_ORDER_TYPE_SELL_STOP` | 5 | Orden pendiente Sell Stop |
| `TMT5_ORDER_TYPE_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit |
| `TMT5_ORDER_TYPE_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit |
| `TMT5_ORDER_TYPE_CLOSE_BY` | 8 | Cierre mediante una posición opuesta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Acceder a los valores del enum
trading_pb2.TMT5_ORDER_TYPE_BUY              # = 0
trading_pb2.TMT5_ORDER_TYPE_SELL             # = 1
trading_pb2.TMT5_ORDER_TYPE_BUY_LIMIT        # = 2
trading_pb2.TMT5_ORDER_TYPE_SELL_LIMIT       # = 3
trading_pb2.TMT5_ORDER_TYPE_BUY_STOP         # = 4
trading_pb2.TMT5_ORDER_TYPE_SELL_STOP        # = 5
trading_pb2.TMT5_ORDER_TYPE_BUY_STOP_LIMIT   # = 6
trading_pb2.TMT5_ORDER_TYPE_SELL_STOP_LIMIT  # = 7
trading_pb2.TMT5_ORDER_TYPE_CLOSE_BY         # = 8
```

### `TMT5_ENUM_ORDER_TYPE_TIME`

Se utiliza en `OrderSendRequest` para especificar el período de validez de la orden.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `TMT5_ORDER_TIME_GTC` | 0 | Válida hasta su cancelación |
| `TMT5_ORDER_TIME_DAY` | 1 | Válida hasta el final del día de negociación actual |
| `TMT5_ORDER_TIME_SPECIFIED` | 2 | Válida hasta la fecha especificada |
| `TMT5_ORDER_TIME_SPECIFIED_DAY` | 3 | Válida hasta el día especificado |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2

# Acceder a los valores del enum
trading_pb2.TMT5_ORDER_TIME_GTC            # = 0
trading_pb2.TMT5_ORDER_TIME_DAY            # = 1
trading_pb2.TMT5_ORDER_TIME_SPECIFIED      # = 2
trading_pb2.TMT5_ORDER_TIME_SPECIFIED_DAY  # = 3
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incluyen protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.
- **Código de retorno:** Comprueba siempre `returned_code == 10009` para verificar que la operación se ha realizado correctamente.
- **Mercado frente a pendiente:** Utiliza la operación 0 (BUY) o 1 (SELL) para órdenes de mercado; utiliza los demás códigos para órdenes pendientes.
- **Deslizamiento:** Establece un valor de deslizamiento adecuado para las órdenes de mercado, permitiendo movimientos del precio.
- **Volumen:** El volumen se especifica en lotes (por ejemplo, 0.01 = 1 microlote).
- **SL/TP:** Se pueden establecer al enviar la orden o modificarse posteriormente.
- **Número mágico:** Utiliza `expert_id` para identificar las órdenes de tu EA.
- **Validación:** Utiliza `order_check` antes del envío para validar la orden.

---

## 🔗 Ejemplos de uso

### 1) Enviar una orden de mercado BUY

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def market_buy():
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
        # Crear una solicitud de orden de mercado BUY
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,  # 0.01 lotes (1 microlote)
            price=0,       # 0 para órdenes de mercado
            slippage=20,   # Deslizamiento máximo de 20 puntos
            stop_loss=0,   # Sin SL
            take_profit=0, # Sin TP
            comment="Market BUY",
            expert_id=12345
        )

        # Enviar la orden
        result = await account.order_send(request)

        # Comprobar el resultado
        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Orden ejecutada!")
            print(f"  Operación: #{result.deal}")
            print(f"  Volumen: {result.volume}")
            print(f"  Precio: {result.price}")
            print(f"  Bid: {result.bid}, Ask: {result.ask}")
        else:
            print(f"[ERROR] Código: {result.returned_code}")
            print(f"  Descripción: {result.returned_code_description}")
            print(f"  Comentario: {result.comment}")

    finally:
        await account.channel.close()


asyncio.run(market_buy())
```

### 2) Enviar una orden de mercado con SL/TP

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def market_order_with_sl_tp():
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
        # Primero, obtener el precio actual
        import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2

        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_ask = tick_data.tick.ask
        current_bid = tick_data.tick.bid

        # Calcular los niveles de SL/TP (50 pips)
        pip_size = 0.0001
        sl_price = current_ask - (50 * pip_size)  # 50 pips por debajo
        tp_price = current_ask + (50 * pip_size)  # 50 pips por encima

        # Crear una orden BUY con SL/TP
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,
            price=0,
            slippage=20,
            stop_loss=sl_price,
            take_profit=tp_price,
            comment="BUY with SL/TP",
            expert_id=12345
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Orden con SL/TP ejecutada!")
            print(f"  Entrada: {result.price:.5f}")
            print(f"  SL: {sl_price:.5f}")
            print(f"  TP: {tp_price:.5f}")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(market_order_with_sl_tp())
```

### 3) Colocar una orden pendiente BUY LIMIT

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2


async def buy_limit_order():
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
        # Obtener el precio actual
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_bid = tick_data.tick.bid

        # Colocar BUY LIMIT 20 pips por debajo del precio actual
        pip_size = 0.0001
        limit_price = current_bid - (20 * pip_size)

        # Crear una orden BUY LIMIT
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY_LIMIT,
            volume=0.01,
            price=limit_price,
            slippage=0,  # No se utiliza para órdenes pendientes
            stop_loss=0,
            take_profit=0,
            comment="BUY LIMIT order",
            expert_id=12345
        )

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Orden BUY LIMIT colocada!")
            print(f"  Orden: #{result.order}")
            print(f"  Precio: {limit_price:.5f}")
            print(f"  Precio actual: {current_bid:.5f}")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(buy_limit_order())
```

### 4) Colocar una orden BUY STOP con vencimiento

```python
import asyncio
from datetime import datetime, timedelta
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_pb2


async def buy_stop_with_expiration():
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
        # Obtener el precio actual
        tick_req = market_pb2.SymbolInfoTickRequest(symbol="EURUSD")
        tick_data = await account.symbol_info_tick(tick_req)

        current_ask = tick_data.tick.ask

        # Colocar BUY STOP 20 pips por encima del precio actual
        pip_size = 0.0001
        stop_price = current_ask + (20 * pip_size)

        # Establecer el vencimiento dentro de 1 hora
        from google.protobuf.timestamp_pb2 import Timestamp
        expiration = datetime.now() + timedelta(hours=1)
        expiration_timestamp = Timestamp()
        expiration_timestamp.FromDatetime(expiration)

        # Crear una orden BUY STOP
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY_STOP,
            volume=0.01,
            price=stop_price,
            slippage=0,
            stop_loss=0,
            take_profit=0,
            comment="BUY STOP 1h expiry",
            expert_id=12345,
            expiration_time_type=trading_pb2.TMT5_ORDER_TIME_SPECIFIED
        )
        request.expiration_time.CopyFrom(expiration_timestamp)

        result = await account.order_send(request)

        if result.returned_code == 10009:
            print(f"[ÉXITO] ¡Orden BUY STOP colocada!")
            print(f"  Orden: #{result.order}")
            print(f"  Precio: {stop_price:.5f}")
            print(f"  Vence: {expiration.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[ERROR] {result.returned_code_description}")

    finally:
        await account.channel.close()


asyncio.run(buy_stop_with_expiration())
```

### 5) Varias órdenes con gestión de errores

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def multiple_orders():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    orders = [
        ("EURUSD", 0.01, "EUR order"),
        ("GBPUSD", 0.01, "GBP order"),
        ("USDJPY", 0.01, "JPY order"),
    ]

    successful = 0
    failed = 0

    try:
        for symbol, volume, comment in orders:
            request = trading_pb2.OrderSendRequest(
                symbol=symbol,
                operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
                volume=volume,
                price=0,
                slippage=20,
                comment=comment,
                expert_id=12345
            )

            try:
                result = await account.order_send(request)

                if result.returned_code == 10009:
                    successful += 1
                    print(f"[CORRECTO] {symbol}: Operación #{result.deal} @ {result.price}")
                else:
                    failed += 1
                    print(f"[FALLIDO] {symbol}: {result.returned_code_description}")

            except Exception as e:
                failed += 1
                print(f"[ERROR] {symbol}: {e}")

        print(f"\n[RESUMEN] Correctas: {successful}, Fallidas: {failed}")

    finally:
        await account.channel.close()


asyncio.run(multiple_orders())
```

### 6) Orden con lógica de reintentos

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def order_with_retry():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    max_retries = 3
    retry_delay = 1.0  # segundos

    try:
        request = trading_pb2.OrderSendRequest(
            symbol="EURUSD",
            operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
            volume=0.01,
            price=0,
            slippage=20,
            comment="Order with retry",
            expert_id=12345
        )

        for attempt in range(1, max_retries + 1):
            print(f"[INTENTO {attempt}/{max_retries}]")

            result = await account.order_send(request)

            if result.returned_code == 10009:
                print(f"[ÉXITO] ¡Orden ejecutada en el intento {attempt}!")
                print(f"  Operación: #{result.deal}")
                print(f"  Precio: {result.price}")
                break
            else:
                print(f"[ERROR] Código: {result.returned_code}")
                print(f"  Descripción: {result.returned_code_description}")

                if attempt < max_retries:
                    print(f"  Reintentando en {retry_delay} segundos...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"  Se alcanzó el número máximo de reintentos. Se cancela el proceso.")

    finally:
        await account.channel.close()


asyncio.run(order_with_retry())
```

---

## 📚 Véase también

- [OrderCheck](./order_check.md) - Validar una orden antes de enviarla.
- [OrderModify](./order_modify.md) - Modificar órdenes existentes.
- [OrderClose](./order_close.md) - Cerrar posiciones.
- [OrderCalcMargin](./order_calc_margin.md) - Calcular el margen requerido.
- [OrderCalcProfit](./order_calc_profit.md) - Calcular el beneficio/pérdida potencial.