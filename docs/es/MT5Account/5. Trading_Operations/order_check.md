# Comprobar la validez de una orden

> **Solicitud:** Validar si una solicitud de trading puede ejecutarse en las condiciones actuales del mercado.

**Información de la API:**

- **API de Python:** `MT5Account.order_check(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradeFunctions`
- **Definición Proto:** `OrderCheck` (definido en `mt5-term-api-trade-functions.proto`)
- **Enums en este método:** 4 enums con 23 constantes (4 parámetros de entrada)

### RPC

- **Servicio:** `mt5_term_api.TradeFunctions`
- **Método:** `OrderCheck(OrderCheckRequest) -> OrderCheckReply`
- **Cliente de bajo nivel (generado):** `TradeFunctionsStub.OrderCheck(request, metadata)`

---

## 💬 Lo esencial

- **Qué es.** Valida las solicitudes de trading antes de ejecutarlas.
- **Para qué sirve.** Comprueba si la cuenta dispone de margen suficiente y valida los parámetros de la orden.
- **Antes de enviar una orden.** Comprueba siempre las órdenes antes de enviarlas para evitar rechazos.

---

## 🎯 Finalidad

Utilízalo para:

- Verificar que hay margen suficiente antes de abrir posiciones.
- Validar los parámetros de la orden (precio, volumen, SL/TP).
- Comprobar las restricciones del bróker.
- Calcular los requisitos de margen.
- Estimar los cambios en el balance y el equity.
- Evitar que las órdenes sean rechazadas.

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


class MT5Account:
    # ...

    async def order_check(
        self,
        request: trade_pb2.OrderCheckRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCheckData:
        """
        Comprueba si una solicitud de trading puede ejecutarse correctamente.

        Returns:
            OrderCheckData: Resultado de la comprobación de la solicitud de trading.
        """
```

**Mensaje de solicitud:**

```protobuf
message OrderCheckRequest {
  MrpcMqlTradeRequest mql_trade_request = 1;  // Solicitud de trading que se va a validar
}


message MrpcMqlTradeRequest {
  MRPC_ENUM_TRADE_REQUEST_ACTIONS action = 1;  // Tipo de operación de trading
  uint64 expert_advisor_magic_number = 2;      // ID del Expert Advisor
  uint64 order = 3;                            // Ticket de la orden
  string symbol = 4;                           // Nombre del símbolo
  double volume = 5;                           // Volumen en lotes
  double price = 6;                            // Precio
  double stop_limit = 7;                       // Precio Stop Limit
  double stop_loss = 8;                        // Precio Stop Loss
  double take_profit = 9;                      // Precio Take Profit
  uint64 deviation = 10;                       // Desviación máxima respecto al precio
  ENUM_ORDER_TYPE_TF order_type = 11;          // Tipo de orden
  MRPC_ENUM_ORDER_TYPE_FILLING type_filling = 12;  // Modo de ejecución
  MRPC_ENUM_ORDER_TYPE_TIME type_time = 13;    // Duración de la orden
  google.protobuf.Timestamp expiration = 14;   // Hora de vencimiento
  string comment = 15;                         // Comentario
  uint64 position = 16;                        // Ticket de la posición
  uint64 position_by = 17;                     // Ticket de la posición opuesta
  google.protobuf.Timestamp expiration_utc = 18;  // Hora de vencimiento (UTC)
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `OrderCheckRequest` | Solicitud de trading que se va a validar |
| `deadline` | `Optional[datetime]` | Plazo límite de la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

---

## ⬆️ Salida

Devuelve un objeto `OrderCheckData` con los resultados de la validación.

**Campos de OrderCheckData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `mql_trade_check_result` | `MrpcMqlTradeCheckResult` | Estructura con el resultado de la validación |

**Campos de MrpcMqlTradeCheckResult:**

| Campo | Tipo | Descripción |
|---|---|---|
| `returned_code` | `uint32` | Código de retorno (0 = éxito) |
| `balance_after_deal` | `double` | Balance después de ejecutar la orden |
| `equity_after_deal` | `double` | Equity después de ejecutar la orden |
| `profit` | `double` | Beneficio o pérdida estimados |
| `margin` | `double` | Margen requerido |
| `free_margin` | `double` | Margen libre después de la orden |
| `margin_level` | `double` | Nivel de margen en porcentaje |
| `comment` | `string` | Comentario o descripción del error |

---

## 🧱 Enums relacionados (del proto)

### `MRPC_ENUM_TRADE_REQUEST_ACTIONS`

Se utiliza en `MrpcMqlTradeRequest` para especificar el tipo de operación de trading.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `TRADE_ACTION_DEAL` | 0 | Colocar una orden de mercado |
| `TRADE_ACTION_PENDING` | 1 | Colocar una orden pendiente |
| `TRADE_ACTION_SLTP` | 2 | Modificar SL/TP |
| `TRADE_ACTION_MODIFY` | 3 | Modificar una orden |
| `TRADE_ACTION_REMOVE` | 4 | Eliminar una orden |
| `TRADE_ACTION_CLOSE_BY` | 5 | Cerrar mediante una posición opuesta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Acceder a los valores del enum

trade_pb2.TRADE_ACTION_DEAL     # = 0
trade_pb2.TRADE_ACTION_PENDING  # = 1
```

### `ENUM_ORDER_TYPE_TF`

Se utiliza en `MrpcMqlTradeRequest` para especificar el tipo de orden.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `ORDER_TYPE_TF_BUY` | 0 | Orden de compra a mercado |
| `ORDER_TYPE_TF_SELL` | 1 | Orden de venta a mercado |
| `ORDER_TYPE_TF_BUY_LIMIT` | 2 | Orden pendiente Buy Limit |
| `ORDER_TYPE_TF_SELL_LIMIT` | 3 | Orden pendiente Sell Limit |
| `ORDER_TYPE_TF_BUY_STOP` | 4 | Orden pendiente Buy Stop |
| `ORDER_TYPE_TF_SELL_STOP` | 5 | Orden pendiente Sell Stop |
| `ORDER_TYPE_TF_BUY_STOP_LIMIT` | 6 | Orden pendiente Buy Stop Limit |
| `ORDER_TYPE_TF_SELL_STOP_LIMIT` | 7 | Orden pendiente Sell Stop Limit |
| `ORDER_TYPE_TF_CLOSE_BY` | 8 | Cierre mediante una posición opuesta |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Acceder a los valores del enum

trade_pb2.ORDER_TYPE_TF_BUY         # = 0
trade_pb2.ORDER_TYPE_TF_SELL        # = 1
trade_pb2.ORDER_TYPE_TF_BUY_LIMIT   # = 2
```

### `MRPC_ENUM_ORDER_TYPE_FILLING`

Se utiliza en `MrpcMqlTradeRequest` para especificar el modo de ejecución de la orden.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `ORDER_FILLING_FOK` | 0 | Ejecutar completamente o cancelar (Fill or Kill) |
| `ORDER_FILLING_IOC` | 1 | Ejecutar inmediatamente o cancelar (Immediate or Cancel) |
| `ORDER_FILLING_RETURN` | 2 | Devolver la orden (Return) |
| `ORDER_FILLING_BOC` | 3 | Book or Cancel |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Acceder a los valores del enum

trade_pb2.ORDER_FILLING_FOK  # = 0
trade_pb2.ORDER_FILLING_IOC  # = 1
```

### `MRPC_ENUM_ORDER_TYPE_TIME`

Se utiliza en `MrpcMqlTradeRequest` para especificar la duración de la orden.

| Nombre de la constante | Valor | Descripción |
|---|---:|---|
| `ORDER_TIME_GTC` | 0 | Válida hasta su cancelación (Good till cancelled) |
| `ORDER_TIME_DAY` | 1 | Válida hasta el final del día de trading actual |
| `ORDER_TIME_SPECIFIED` | 2 | Válida hasta la fecha especificada |
| `ORDER_TIME_SPECIFIED_DAY` | 3 | Válida hasta el día especificado |

**Uso:**

```python
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2

# Acceder a los valores del enum

trade_pb2.ORDER_TIME_GTC  # = 0
trade_pb2.ORDER_TIME_DAY  # = 1
```

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**[OrderCheck - Cómo funciona](../HOW_IT_WORK/5. Trading_Operations_HOW/order_check_HOW.md)**

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incorporan protección contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **No ejecuta la orden:** Este método NO ejecuta la orden; únicamente la valida.
- **Estructura anidada:** La solicitud utiliza `OrderCheckRequest`, que contiene `MrpcMqlTradeRequest`.
- **Comprobación del margen:** Devuelve el margen requerido y el margen libre después de la orden.
- **Código de retorno:** Comprueba el campo `returned_code` (0 = éxito).
- **Buena práctica:** Comprueba siempre las órdenes antes de enviarlas, especialmente cuando se utilizan volúmenes elevados.

---

## 🔗 Ejemplos de uso

### 1) Validación básica de una orden

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def check_order():
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
        # Crear la solicitud de comprobación de la orden
        request = trade_pb2.OrderCheckRequest()
        request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        request.mql_trade_request.symbol = "EURUSD"
        request.mql_trade_request.volume = 0.10
        request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        request.mql_trade_request.price = 0.0
        request.mql_trade_request.deviation = 20
        request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC
        request.mql_trade_request.comment = "Comprobar orden"

        # Comprobar la validez de la orden
        result = await account.order_check(request)

        if result.mql_trade_check_result.returned_code == 0:  # 0 = válida
            print(f"[VÁLIDA] ¡La orden puede ejecutarse!")
            print(f"  Margen requerido: ${result.mql_trade_check_result.margin:.2f}")
            print(f"  Margen libre después: ${result.mql_trade_check_result.free_margin:.2f}")
            print(f"  Balance después: ${result.mql_trade_check_result.balance_after_deal:.2f}")
        else:
            print(f"[NO VÁLIDA] ¡La orden no puede ejecutarse!")
            print(f"  Código: {result.mql_trade_check_result.returned_code}")
            print(f"  Comentario: {result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()


asyncio.run(check_order())
```

### 2) Patrón de comprobación y envío

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


async def check_and_send():
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
        # Crear la solicitud de comprobación de la orden
        check_request = trade_pb2.OrderCheckRequest()
        check_request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        check_request.mql_trade_request.symbol = "EURUSD"
        check_request.mql_trade_request.volume = 0.05
        check_request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        check_request.mql_trade_request.price = 0.0
        check_request.mql_trade_request.deviation = 20
        check_request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        check_request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC
        check_request.mql_trade_request.comment = "Orden comprobada"

        # Primero, comprobar la orden
        check_result = await account.order_check(check_request)

        if check_result.mql_trade_check_result.returned_code == 0:
            print(f"[COMPROBACIÓN SUPERADA] La orden es válida")
            print(f"  Margen: ${check_result.mql_trade_check_result.margin:.2f}")

            # Ahora enviar la orden como una orden de mercado.
            # OrderSendRequest es una estructura plana (sin mql_trade_request)
            # y se encuentra en trading_helper.
            send_request = trading_pb2.OrderSendRequest(
                symbol="EURUSD",
                operation=trading_pb2.TMT5_ORDER_TYPE_BUY,
                volume=0.05,
                price=0.0,
                slippage=20,
                comment="Orden comprobada",
            )
            send_result = await account.order_send(send_request)

            if send_result.returned_code == 10009:
                print(f"[ÉXITO] ¡Orden ejecutada!")
                print(f"  Operación: #{send_result.deal}")
                print(f"  Precio: {send_result.price}")
            else:
                print(f"[ERROR] {send_result.returned_code_description}")
        else:
            print(f"[COMPROBACIÓN FALLIDA] No se puede enviar la orden")
            print(f"  Motivo: {check_result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()


asyncio.run(check_and_send())
```

### 3) Comprobar varios volúmenes

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def check_multiple_volumes():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    volumes = [0.01, 0.05, 0.10, 0.50, 1.00]

    try:
        print("Comprobando volúmenes para EURUSD BUY:")
        print("-" * 60)

        for volume in volumes:
            request = trade_pb2.OrderCheckRequest()
            request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
            request.mql_trade_request.symbol = "EURUSD"
            request.mql_trade_request.volume = volume
            request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
            request.mql_trade_request.price = 0.0
            request.mql_trade_request.deviation = 20
            request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
            request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC

            result = await account.order_check(request)

            if result.mql_trade_check_result.returned_code == 0:
                print(f"[OK] {volume:>6.2f} lotes - "
                      f"Margen: ${result.mql_trade_check_result.margin:>10,.2f}, "
                      f"Libre: ${result.mql_trade_check_result.free_margin:>10,.2f}")
            else:
                print(f"[ERROR] {volume:>6.2f} lotes - "
                      f"{result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()


asyncio.run(check_multiple_volumes())
```

### 4) Encontrar el volumen máximo

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def find_max_volume():
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
        max_volume = 0.01
        step = 0.01

        # Búsqueda binaria del volumen máximo
        current = 0.01

        while current <= 10.0:  # Comprobar hasta un máximo de 10 lotes
            request = trade_pb2.OrderCheckRequest()
            request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
            request.mql_trade_request.symbol = "EURUSD"
            request.mql_trade_request.volume = current
            request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
            request.mql_trade_request.price = 0.0
            request.mql_trade_request.deviation = 20
            request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
            request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC

            result = await account.order_check(request)

            if (result.mql_trade_check_result.returned_code == 0 and
                result.mql_trade_check_result.free_margin > 0):
                max_volume = current
                current += step
            else:
                break

        print(f"[RESULTADO] Volumen máximo: {max_volume:.2f} lotes")

    finally:
        await account.channel.close()


asyncio.run(find_max_volume())
```

### 5) Calculadora de riesgo

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_pb2


async def calculate_risk_percent(volume: float):
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
        # Obtener el balance actual
        summary_req = account_pb2.AccountSummaryRequest()
        summary = await account.account_summary(summary_req)
        current_balance = summary.balance

        # Comprobar la orden
        request = trade_pb2.OrderCheckRequest()
        request.mql_trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        request.mql_trade_request.symbol = "EURUSD"
        request.mql_trade_request.volume = volume
        request.mql_trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        request.mql_trade_request.price = 0.0
        request.mql_trade_request.deviation = 20
        request.mql_trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        request.mql_trade_request.type_time = trade_pb2.ORDER_TIME_GTC

        result = await account.order_check(request)

        if result.mql_trade_check_result.returned_code == 0:
            margin_required = result.mql_trade_check_result.margin
            risk_percent = (margin_required / current_balance) * 100

            print(f"[ANÁLISIS DE RIESGO]")
            print(f"  Volumen: {volume:.2f} lotes")
            print(f"  Balance actual: ${current_balance:,.2f}")
            print(f"  Margen requerido: ${margin_required:,.2f}")
            print(f"  Riesgo: {risk_percent:.2f}% del balance")
            print(f"  Margen libre después: ${result.mql_trade_check_result.free_margin:,.2f}")
        else:
            print(f"[ERROR] {result.mql_trade_check_result.comment}")

    finally:
        await account.channel.close()


asyncio.run(calculate_risk_percent(0.10))
```

### 6) Validar una orden antes del trading automatizado

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_pb2


class OrderValidator:
    def __init__(self, account):
        self.account = account

    async def validate_and_execute(self, trade_request):
        """Validar la orden antes de ejecutarla"""

        # Comprobar la orden
        check_request = trade_pb2.OrderCheckRequest()
        check_request.mql_trade_request.CopyFrom(trade_request)
        check_result = await self.account.order_check(check_request)

        if check_result.mql_trade_check_result.returned_code != 0:
            return {
                'success': False,
                'stage': 'validation',
                'error': check_result.mql_trade_check_result.comment
            }

        # Comprobar el umbral de margen libre (por ejemplo, un mínimo del 30 %)
        balance = check_result.mql_trade_check_result.balance_after_deal
        margin_free = check_result.mql_trade_check_result.free_margin

        if margin_free < (balance * 0.30):
            return {
                'success': False,
                'stage': 'margin_check',
                'error': 'Margen libre insuficiente (< 30%)'
            }

        # Ejecutar la orden. OrderSendRequest es una estructura plana
        # (sin mql_trade_request) y se encuentra en trading_helper.
        # Se transfieren los campos validados (los tipos de orden TF y TMT5
        # comparten los mismos valores numéricos, por lo que order_type -> operation es seguro).
        send_request = trading_pb2.OrderSendRequest(
            symbol=trade_request.symbol,
            operation=trade_request.order_type,
            volume=trade_request.volume,
            price=trade_request.price,
            slippage=trade_request.deviation,
            stop_loss=trade_request.stop_loss,
            take_profit=trade_request.take_profit,
            comment=trade_request.comment,
        )
        send_result = await self.account.order_send(send_request)

        if send_result.returned_code == 10009:
            return {
                'success': True,
                'deal': send_result.deal,
                'price': send_result.price
            }
        else:
            return {
                'success': False,
                'stage': 'execution',
                'error': send_result.returned_code_description
            }


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

    validator = OrderValidator(account)

    try:
        # Crear la solicitud de trading
        trade_request = trade_pb2.MrpcMqlTradeRequest()
        trade_request.action = trade_pb2.TRADE_ACTION_DEAL
        trade_request.symbol = "EURUSD"
        trade_request.volume = 0.05
        trade_request.order_type = trade_pb2.ORDER_TYPE_TF_BUY
        trade_request.price = 0.0
        trade_request.deviation = 20
        trade_request.type_filling = trade_pb2.ORDER_FILLING_FOK
        trade_request.type_time = trade_pb2.ORDER_TIME_GTC

        result = await validator.validate_and_execute(trade_request)

        if result['success']:
            print(f"[ÉXITO] Operación: #{result['deal']}, Precio: {result['price']}")
        else:
            print(f"[ERROR] Etapa: {result['stage']}, Error: {result['error']}")

    finally:
        await account.channel.close()


asyncio.run(main())
```

---

## 📚 Véase también

- [OrderSend](./order_send.md) - Enviar órdenes después de validarlas.
- [OrderCalcMargin](./order_calc_margin.md) - Calcular únicamente el margen.
- [OrderCalcProfit](./order_calc_profit.md) - Calcular el beneficio o la pérdida potencial.
- [AccountSummary](../1.%20Account_Information/account_summary.md) - Obtener el balance y el margen de la cuenta.