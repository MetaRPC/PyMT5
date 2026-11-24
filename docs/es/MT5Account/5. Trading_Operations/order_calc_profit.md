# Calcular el beneficio o la pérdida potencial

> **Solicitud:** Calcular el beneficio o la pérdida potencial de una operación de trading planificada.

**Información de la API:**

- **API de Python:** `MT5Account.order_calc_profit(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)
- **Servicio gRPC:** `mt5_term_api.TradeFunctions`
- **Definición Proto:** `OrderCalcProfit` (definido en `mt5-term-api-trade-functions.proto`)
- **Enums en este método:** 1 enum con 9 constantes (1 parámetro de entrada)

### RPC

- **Servicio:** `mt5_term_api.TradeFunctions`
- **Método:** `OrderCalcProfit(OrderCalcProfitRequest) -> OrderCalcProfitReply`
- **Cliente de bajo nivel (generado):** `TradeFunctionsStub.OrderCalcProfit(request, metadata)`

---

## 💬 Lo esencial

- **Qué es.** Calcula el beneficio o la pérdida potencial de una operación sin ejecutarla.
- **Para qué sirve.** Planificar operaciones, calcular ratios de riesgo/recompensa y determinar el tamaño de las posiciones.
- **Moneda de la cuenta.** Devuelve el beneficio o la pérdida en la moneda de la cuenta (USD, EUR, etc.).

---

## 🎯 Finalidad

Utilízalo para:

- Calcular el beneficio o la pérdida antes de abrir una operación.
- Determinar el ratio de riesgo/recompensa.
- Planificar estrategias de salida.
- Comparar la rentabilidad entre distintos símbolos.
- Calcular el valor de un pip para diferentes tamaños de lote.
- Realizar proyecciones de beneficios y pérdidas de una cartera.

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea, con ejemplos, consulta:

**[OrderCalcProfit - Cómo funciona](../HOW_IT_WORK/5. Trading_Operations_HOW/order_calc_profit_HOW.md)**

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


class MT5Account:
    # ...

    async def order_calc_profit(
        self,
        request: trade_pb2.OrderCalcProfitRequest,
        deadline: Optional[datetime] = None,
        cancellation_event: Optional[asyncio.Event] = None,
    ) -> trade_pb2.OrderCalcProfitData:
        """
        Calcula el beneficio o la pérdida potencial de una operación de trading planificada.

        Returns:
            OrderCalcProfitData: El beneficio o la pérdida potencial en la moneda de la cuenta.
        """
```

**Mensaje de solicitud:**

```protobuf
message OrderCalcProfitRequest {
  ENUM_ORDER_TYPE_TF order_type = 1;  // Tipo de orden
  string symbol = 2;                  // Nombre del símbolo
  double volume = 3;                  // Volumen de trading en lotes
  double open_price = 4;              // Precio de entrada
  double close_price = 5;             // Precio de salida
}
```

---

## 🔽 Entrada

| Parámetro | Tipo | Descripción |
|---|---|---|
| `request` | `OrderCalcProfitRequest` | Solicitud de cálculo del beneficio |
| `deadline` | `Optional[datetime]` | Plazo límite de la operación (opcional) |
| `cancellation_event` | `Optional[asyncio.Event]` | Evento para cancelar la solicitud (opcional) |

**Campos de OrderCalcProfitRequest:**

| Campo | Tipo | Descripción |
|---|---|---|
| `order_type` | `ENUM_ORDER_TYPE_TF` | Tipo de orden (enum) |
| `symbol` | `string` | Nombre del símbolo (por ejemplo, "EURUSD") |
| `volume` | `double` | Volumen de trading en lotes |
| `open_price` | `double` | Precio de entrada |
| `close_price` | `double` | Precio de salida |

---

## ⬆️ Salida

Devuelve un objeto `OrderCalcProfitData`.

**Campos de OrderCalcProfitData:**

| Campo | Tipo | Descripción |
|---|---|---|
| `profit` | `double` | Beneficio o pérdida en la moneda de la cuenta (un valor negativo indica una pérdida) |

---

## 🧱 Enums relacionados (del proto)

### `ENUM_ORDER_TYPE_TF`

Se utiliza en `OrderCalcProfitRequest` para especificar el tipo de orden.

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

trade_pb2.ORDER_TYPE_TF_BUY          # = 0
trade_pb2.ORDER_TYPE_TF_SELL         # = 1
trade_pb2.ORDER_TYPE_TF_BUY_LIMIT    # = 2
trade_pb2.ORDER_TYPE_TF_SELL_LIMIT   # = 3
```

---

## 🧩 Notas y consejos

- **Reconexión automática:** Todos los métodos de `MT5Account` incorporan protección contra errores gRPC transitorios mediante la reconexión automática a través de `execute_with_reconnect`.
- **Código de retorno:** Comprueba que `returned_code == 0` para confirmar el éxito (los métodos de validación utilizan 0, no 10009).
- **Valores positivos y negativos:** Un beneficio positivo representa una ganancia; un beneficio negativo representa una pérdida.
- **Moneda de la cuenta:** El resultado siempre se expresa en la moneda de la cuenta (USD, EUR, etc.).
- **El spread no está incluido:** Este método calcula el beneficio teórico; el beneficio real puede diferir debido al spread y las comisiones.
- **Uso para la planificación:** Es útil para calcular el riesgo y la recompensa antes de abrir una operación.
- **Valor del pip:** Utilízalo para calcular cuánto vale 1 pip para el tamaño de lote elegido.

---

## 🔗 Ejemplos de uso

### 1) Calcular el beneficio de una operación BUY

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def calc_buy_profit():
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
        # Calcular el beneficio de una operación BUY de 0.10 lotes de EURUSD
        # Entrada: 1.10000, salida: 1.10100 (beneficio de 100 pips)
        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=1.10000,
            close_price=1.10100
        )

        result = await account.order_calc_profit(request)

        print(f"[CÁLCULO DEL BENEFICIO]")
        print(f"  Entrada: 1.10000")
        print(f"  Salida: 1.10100")
        print(f"  Volumen: 0.10 lotes")
        print(f"  Beneficio: ${result.profit:.2f}")

    finally:
        await account.channel.close()


asyncio.run(calc_buy_profit())
```

### 2) Calcular la pérdida de una operación SELL

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def calc_sell_loss():
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
        # Calcular la pérdida de una operación SELL de 0.01 lotes de EURUSD
        # Entrada: 1.10000, salida: 1.10050 (pérdida de 50 pips)
        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_SELL,
            symbol="EURUSD",
            volume=0.01,
            open_price=1.10000,
            close_price=1.10050  # El precio se movió en nuestra contra
        )

        result = await account.order_calc_profit(request)

        print(f"[CÁLCULO DE LA PÉRDIDA]")
        print(f"  Entrada: 1.10000")
        print(f"  Salida: 1.10050")
        print(f"  Volumen: 0.01 lotes")
        print(f"  Pérdida: ${result.profit:.2f}")  # Será un valor negativo

    finally:
        await account.channel.close()


asyncio.run(calc_sell_loss())
```

### 3) Calcular el ratio de riesgo/recompensa

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def calc_risk_reward():
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
        entry = 1.10000
        stop_loss = 1.09950  # SL de 50 pips
        take_profit = 1.10100  # TP de 100 pips

        # Calcular la pérdida potencial (si se alcanza el SL)
        loss_req = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=entry,
            close_price=stop_loss
        )

        loss_result = await account.order_calc_profit(loss_req)
        risk = abs(loss_result.profit)

        # Calcular el beneficio potencial (si se alcanza el TP)
        profit_req = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=entry,
            close_price=take_profit
        )

        profit_result = await account.order_calc_profit(profit_req)
        reward = profit_result.profit

        rr_ratio = reward / risk

        print(f"[ANÁLISIS DE RIESGO/RECOMPENSA]")
        print(f"  Entrada: {entry}")
        print(f"  SL: {stop_loss} (Riesgo: ${risk:.2f})")
        print(f"  TP: {take_profit} (Recompensa: ${reward:.2f})")
        print(f"  Ratio R:R: 1:{rr_ratio:.2f}")

    finally:
        await account.channel.close()


asyncio.run(calc_risk_reward())
```

### 4) Calcular el valor de un pip

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def calc_pip_value():
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
        # Calcular el valor de 1 pip para 0.10 lotes de EURUSD
        pip_size = 0.0001

        request = trade_pb2.OrderCalcProfitRequest(
            order_type=trade_pb2.ORDER_TYPE_TF_BUY,
            symbol="EURUSD",
            volume=0.10,
            open_price=1.10000,
            close_price=1.10000 + pip_size  # Movimiento de 1 pip
        )

        result = await account.order_calc_profit(request)

        print(f"[CÁLCULO DEL VALOR DEL PIP]")
        print(f"  Símbolo: EURUSD")
        print(f"  Volumen: 0.10 lotes")
        print(f"  1 pip = ${result.profit:.2f}")

    finally:
        await account.channel.close()


asyncio.run(calc_pip_value())
```

### 5) Comparar la rentabilidad entre distintos símbolos

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def compare_symbols():
    account = MT5Account(
        user=12345,
        password="password",
        grpc_server="mt5.mrpc.pro:443"
    )

    await account.connect_by_server_name(
        server_name="YourBroker-Demo",
        base_chart_symbol="EURUSD"
    )

    symbols = [
        ("EURUSD", 1.10000, 1.10100),
        ("GBPUSD", 1.30000, 1.30100),
        ("USDJPY", 150.000, 150.100),
    ]

    try:
        print("[COMPARACIÓN DE RENTABILIDAD]")
        print("Mismo movimiento de precio (100 pips), mismo tamaño de lote (0.10)")
        print()

        for symbol, entry, exit in symbols:
            request = trade_pb2.OrderCalcProfitRequest(
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                symbol=symbol,
                volume=0.10,
                open_price=entry,
                close_price=exit
            )

            result = await account.order_calc_profit(request)

            print(f"{symbol}: ${result.profit:.2f}")

    finally:
        await account.channel.close()


asyncio.run(compare_symbols())
```

### 6) Determinar el tamaño de la posición según el riesgo

```python
import asyncio
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trade_pb2


async def calc_position_size():
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
        max_risk = 100.00  # Riesgo máximo de 100 $
        entry = 1.10000
        stop_loss = 1.09950  # SL de 50 pips

        # Probar diferentes tamaños de lote para encontrar el adecuado
        for volume in [0.01, 0.05, 0.10, 0.20]:
            request = trade_pb2.OrderCalcProfitRequest(
                order_type=trade_pb2.ORDER_TYPE_TF_BUY,
                symbol="EURUSD",
                volume=volume,
                open_price=entry,
                close_price=stop_loss
            )

            result = await account.order_calc_profit(request)
            risk = abs(result.profit)

            print(f"Volumen: {volume} lotes -> Riesgo: ${risk:.2f}")

            if risk <= max_risk:
                recommended_size = volume
            else:
                break

        print(f"\n[RECOMENDACIÓN] Utiliza {recommended_size} lotes para un riesgo máximo de ${max_risk}")

    finally:
        await account.channel.close()


asyncio.run(calc_position_size())
```

---

## 📚 Véase también

- [OrderCalcMargin](./order_calc_margin.md) - Calcular el margen requerido.
- [OrderCheck](./order_check.md) - Validar una orden antes de enviarla.
- [OrderSend](./order_send.md) - Enviar órdenes de mercado o pendientes.
- [SymbolInfoTick](../2.%20Symbol_Information/symbol_info_tick.md) - Obtener los precios actuales.