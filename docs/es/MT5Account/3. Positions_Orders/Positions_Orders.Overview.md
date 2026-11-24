# MT5Account - Posiciones y órdenes - Descripción general

Gestiona posiciones abiertas, órdenes pendientes y datos históricos de trading. Consulta los valores de tick y analiza el rendimiento de las operaciones.

## 📁 Qué contiene esta sección

- **[positions_total](./positions_total.md)** - únicamente el **recuento** de posiciones abiertas (consulta ligera).
- **[opened_orders](./opened_orders.md)** - **detalles completos** de todas las órdenes pendientes y posiciones abiertas.
- **[opened_orders_tickets](./opened_orders_tickets.md)** - únicamente los **identificadores de ticket** de las órdenes pendientes y posiciones abiertas (más ligero que obtener todos los detalles).
- **[order_history](./order_history.md)** - **órdenes y operaciones históricas** dentro de un intervalo de tiempo, con paginación.
- **[positions_history](./positions_history.md)** - **posiciones históricas cerradas**, filtradas por hora de apertura.
- **[tick_value_with_size](./tick_value_with_size.md)** - **valores de tick y tamaños de contrato** para varios símbolos (para calcular P/L).

---

## 📚 Tutoriales paso a paso

¿Quieres explicaciones detalladas con un desglose del código línea por línea? Consulta estas guías:

- **[positions_total - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_total_HOW.md)**
- **[opened_orders - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_HOW.md)**
- **[opened_orders_tickets - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/opened_orders_tickets_HOW.md)**
- **[order_history - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/order_history_HOW.md)**
- **[positions_history - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/positions_history_HOW.md)**
- **[tick_value_with_size - Cómo funciona](../HOW_IT_WORK/3. Position_Orders_Information_HOW/tick_value_with_size_HOW.md)**

---

## 🧭 En términos sencillos

- **`positions_total`** - consulta rápidamente **cuántas posiciones** están abiertas (sin detalles).
- **`opened_orders`** - obtiene una **instantánea completa** de todas las órdenes pendientes y posiciones abiertas.
- **`opened_orders_tickets`** - obtiene **únicamente los identificadores de ticket** (más eficiente que solicitar todos los detalles).
- **`order_history`** - obtiene **órdenes y operaciones anteriores** dentro de un intervalo de fechas.
- **`positions_history`** - obtiene **posiciones cerradas** con datos de ganancias y pérdidas.
- **`tick_value_with_size`** - obtiene **valores de tick** para calcular las ganancias por pip.

> Regla general: si necesitas **solo el recuento**, utiliza `positions_total()`; si necesitas **los identificadores de ticket**, utiliza `opened_orders_tickets()`; si necesitas **todos los detalles**, utiliza `opened_orders()`; si necesitas **el historial**, utiliza `order_history()` o `positions_history()`.

---

## Elección rápida

| Si necesitas | Utiliza | Devuelve | Parámetros principales |
|---|---|---|---|
| Número de posiciones abiertas | `positions_total` | PositionsTotalData (recuento) | **Ninguno** |
| Detalles completos de órdenes pendientes y posiciones abiertas | `opened_orders` | OpenedOrdersData (listas) | Modo de ordenación (opcional) |
| Únicamente los identificadores de ticket de los elementos abiertos | `opened_orders_tickets` | Listas de identificadores de ticket | **Ninguno** |
| Órdenes históricas dentro de un intervalo de tiempo | `order_history` | OrdersHistoryData | from_dt, to_dt, modo de ordenación, página |
| Posiciones históricas cerradas | `positions_history` | PositionsHistoryData | sort_type, intervalo de tiempo de apertura, página |
| Valores de tick y tamaños de contrato | `tick_value_with_size` | TickValueWithSizeData | Lista de nombres de símbolos |

---

## ℹ️ Referencias cruzadas y aspectos importantes

- **`positions_total`** - la forma más rápida de comprobar si existen posiciones (solo devuelve el recuento, sin detalles).
- **`opened_orders` frente a `opened_orders_tickets`** - utiliza la versión de tickets para obtener una respuesta más ligera cuando solo necesitas los ID.
- **`order_history` frente a `positions_history`** - `order_history` obtiene órdenes y operaciones; `positions_history` obtiene posiciones cerradas.
- **Paginación** - `order_history` y `positions_history` admiten paginación para grandes conjuntos de datos (utiliza los parámetros page y size).
- **Filtros de tiempo** - `order_history` utiliza la hora de cierre; `positions_history` utiliza la hora de apertura.
- **Valor del tick** - es necesario para calcular las ganancias y pérdidas por pip/tick; multiplícalo por el movimiento en pips y el tamaño del lote.
- **Tamaño del contrato** - normalmente es 100 000 para los principales pares de divisas y 100 para los metales (varía según el símbolo).

---

## 🟢 Fragmentos mínimos

```python
from MetaRpcMT5 import MT5Account
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
from datetime import datetime, timedelta, timezone
import asyncio

# Obtener el número de posiciones abiertas
data = await account.positions_total()
print(f"Posiciones abiertas: {data.total_positions}")
```

```python
# Obtener todas las órdenes pendientes y posiciones abiertas
data = await account.opened_orders()

print(f"Órdenes pendientes: {len(data.opened_orders)}")
print(f"Posiciones abiertas: {len(data.position_infos)}")

# Mostrar las posiciones
for pos in data.position_infos:
    print(f"Posición #{pos.ticket} {pos.symbol}: ${pos.profit:+.2f}")
```

```python
# Obtener únicamente los identificadores de ticket (consulta ligera)
data = await account.opened_orders_tickets()

print(f"Tickets de órdenes: {data.opened_orders_tickets}")
print(f"Tickets de posiciones: {data.opened_position_tickets}")
```

```python
# Obtener el historial de órdenes de los últimos 7 días
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=7)

data = await account.order_history(
    from_dt=from_dt,
    to_dt=to_dt,
    sort_mode=account_helper_pb2.BMT5_SORT_BY_CLOSE_TIME_DESC,
    items_per_page=100
)

print(f"Órdenes totales: {data.arrayTotal}")
for item in data.history_data:
    if item.history_deal:
        print(f"Operación: ${item.history_deal.profit:.2f}")
```

```python
# Obtener las posiciones cerradas de los últimos 30 días
to_dt = datetime.now(timezone.utc)
from_dt = to_dt - timedelta(days=30)

data = await account.positions_history(
    sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_DESC,
    open_from=from_dt,
    open_to=to_dt
)

total_profit = sum(pos.profit for pos in data.history_positions)
print(f"Posiciones cerradas: {len(data.history_positions)}")
print(f"Ganancia total: ${total_profit:+.2f}")
```

```python
# Obtener los valores de tick de los símbolos
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
data = await account.tick_value_with_size(symbols=symbols)

for info in data.symbol_tick_size_infos:
    print(f"{info.Name}: Valor del tick=${info.TradeTickValue:.2f}, "
          f"Tamaño del contrato={info.TradeContractSize:.0f}")
```

```python
# Comprobar si se puede abrir una nueva posición (límite de posiciones)
data = await account.positions_total()

max_positions = 10
if data.total_positions >= max_positions:
    print("[ADVERTENCIA] ¡Se ha alcanzado el límite de posiciones!")
else:
    print(f"[OK] Se pueden abrir {max_positions - data.total_positions} posición(es) más")
```

```python
# Calcular el beneficio/pérdida flotante (P/L) total
data = await account.opened_orders()

total_profit = sum(pos.profit for pos in data.position_infos)
print(f"P/L flotante total: ${total_profit:+.2f}")

if total_profit < 0:
    print("[ADVERTENCIA] La cuenta está en drawdown")
```

```python
# Supervisar las nuevas posiciones
async def monitor_positions(interval: float = 5.0):
    """Supervisar los cambios en las posiciones"""
    previous_tickets = set()

    while True:
        data = await account.opened_orders_tickets()
        current_tickets = set(data.opened_position_tickets)

        new = current_tickets - previous_tickets
        closed = previous_tickets - current_tickets

        for ticket in new:
            print(f"[+] Nueva posición: #{ticket}")
        for ticket in closed:
            print(f"[-] Posición cerrada: #{ticket}")

        previous_tickets = current_tickets
        await asyncio.sleep(interval)

# await monitor_positions()
```

```python
# Analizar el rendimiento del trading
async def analyze_performance(days: int = 30):
    """Analizar el rendimiento del trading durante los últimos N días"""
    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(days=days)

    data = await account.positions_history(
        sort_type=account_helper_pb2.AH_POSITION_OPEN_TIME_ASC,
        open_from=from_dt,
        open_to=to_dt
    )

    wins = sum(1 for pos in data.history_positions if pos.profit > 0)
    losses = sum(1 for pos in data.history_positions if pos.profit < 0)
    total = wins + losses

    win_rate = (wins / total * 100) if total > 0 else 0
    total_profit = sum(pos.profit for pos in data.history_positions)

    print(f"\nRendimiento (últimos {days} días):")
    print(f"  Total de operaciones: {total}")
    print(f"  Ganadoras: {wins} ({win_rate:.1f}%)")
    print(f"  Perdedoras: {losses}")
    print(f"  Ganancia neta: ${total_profit:+.2f}")

# await analyze_performance(days=30)
```

```python
# Calcular la ganancia por pip para determinar el tamaño de la posición
async def calculate_position_size(
    symbol: str,
    risk_amount: float,
    sl_pips: float
) -> float:
    """Calcular el tamaño de la posición en función del riesgo"""
    # Obtener el valor del tick
    data = await account.tick_value_with_size(symbols=[symbol])
    if not data.symbol_tick_size_infos:
        raise ValueError(f"Símbolo {symbol} no encontrado")

    info = data.symbol_tick_size_infos[0]

    # Suponiendo 1 lote
    profit_per_pip = info.TradeTickValue * 10  # 10 ticks por pip (asume un símbolo de 5 decimales)

    # Calcular el tamaño del lote
    lots = risk_amount / (sl_pips * profit_per_pip)

    print(f"Tamaño de la posición para {symbol}:")
    print(f"  Riesgo: ${risk_amount:.2f}")
    print(f"  SL: {sl_pips} pips")
    print(f"  Tamaño del lote: {lots:.2f}")

    return lots

# Uso:
# lot_size = await calculate_position_size("EURUSD", risk_amount=100, sl_pips=50)
```

---

## 📚 Véase también

- **Información de la cuenta:** [Account_Information.Overview](../1. Account_Information/Account_Information.Overview.md) - obtener el saldo, el equity y el apalancamiento de la cuenta.
- **Información de los símbolos:** [Symbol_Information.Overview](../2. Symbol_Information/Symbol_Information.Overview.md) - obtener los precios y parámetros de los símbolos.
- **Operaciones de trading:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - realizar y gestionar operaciones.