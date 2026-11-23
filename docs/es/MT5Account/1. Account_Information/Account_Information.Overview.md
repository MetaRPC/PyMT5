# MT5Account - Información de la cuenta - Descripción general

> Saldo de la cuenta, patrimonio, margen, apalancamiento, divisa y otras propiedades de la cuenta. Utiliza esta página para elegir la API adecuada para acceder al estado de la cuenta.

## 📁 Contenido de esta sección

* **[account_summary](./account_summary.md)** - **toda la información de la cuenta** de una sola vez (saldo, patrimonio, apalancamiento, crédito, hora del servidor, etc.). **RECOMENDADO**
* **[account_info_double](./account_info_double.md)** - **un único valor double** de la cuenta (saldo, patrimonio, margen, beneficio, crédito, nivel de margen, etc.).
* **[account_info_integer](./account_info_integer.md)** - **un único valor entero** de la cuenta (número de cuenta, apalancamiento, modo de trading, órdenes pendientes, permiso para operar, etc.).
* **[account_info_string](./account_info_string.md)** - **un único valor de tipo string** de la cuenta (nombre, servidor, divisa, empresa).

---

## 📚 Tutoriales paso a paso

¿Quieres explicaciones detalladas con un desglose del código línea por línea? Consulta estas guías:

* **[account_summary - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_summary_HOW.md)**
* **[account_info_double - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW.md)**
* **[account_info_integer - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW.md)**
* **[account_info_string - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_info_string_HOW.md)**

---

## 🧭 En términos sencillos

* **account_summary** - la **solución integral** para obtener una instantánea completa de la cuenta (saldo, patrimonio, apalancamiento, divisa, etc.).
* **account_info_double** - obtiene **una propiedad numérica** cuando solo necesitas el saldo o el margen.
* **account_info_integer** - obtiene **una propiedad entera**, como el número de cuenta o el apalancamiento.
* **account_info_string** - obtiene **una propiedad de texto**, como el nombre de la cuenta o la divisa.

> Regla general: si necesitas una **instantánea completa**, utiliza `account_summary()`; si necesitas **un valor específico**, utiliza `account_info_*` (double/integer/string).

---

## Elección rápida

| Si necesitas | Utiliza | Devuelve | Parámetros principales |
| ---------------------------------------------------- | ------------------------- | -------------------------- | ----------------------------------- |
| Una instantánea completa de la cuenta (todos los valores) | `account_summary` | AccountSummaryData | **(ninguno)** |
| Un valor numérico (saldo, patrimonio, margen, etc.) | `account_info_double` | Un único `float` | Enum de propiedad (BALANCE, EQUITY, etc.) |
| Un valor entero (número de cuenta, apalancamiento, etc.) | `account_info_integer` | Un único `int` | Enum de propiedad (LOGIN, LEVERAGE, etc.) |
| Un valor de texto (nombre, divisa, servidor, etc.) | `account_info_string` | Un único `str` | Enum de propiedad (NAME, CURRENCY, etc.) |

---

## ℹ️ Referencias cruzadas y aspectos importantes

* **Nivel de margen** - utiliza `account_info_double(ACCOUNT_MARGIN_LEVEL)` para obtenerlo como porcentaje.
* **Margen libre** - utiliza `account_info_double(ACCOUNT_MARGIN_FREE)` para obtener el margen disponible.
* **account_summary** incluye información básica (saldo, patrimonio, apalancamiento); para obtener el margen, utiliza `account_info_double`.
* Los métodos **account_info_*** son más ligeros cuando solo necesitas una propiedad.
* **Divisa** - afecta al cálculo de los beneficios; comprueba siempre la divisa de la cuenta.
* **Apalancamiento** - determina los requisitos de margen: en igualdad de condiciones y para la misma posición, cuanto mayor sea el apalancamiento, menos margen se necesita.
* **Plazo límite/tiempo de espera** - recuerda establecer un plazo adecuado para las llamadas asíncronas.
* **Formato de moneda** - en los ejemplos el signo `$` es solo ilustrativo; la divisa real de la cuenta la indica `account_currency` (p. ej. EUR).

---

## 🟢 Ejemplos mínimos

```python
from MetaRpcMT5.mt5_account import MT5Account
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
from datetime import datetime, timedelta, timezone

# Obtener una instantánea completa de la cuenta
summary = await account.account_summary()

print(f"Saldo: ${summary.account_balance:.2f}, "
      f"Patrimonio: ${summary.account_equity:.2f}, "
      f"Apalancamiento: 1:{summary.account_leverage}")
```

```python
# Obtener una propiedad individual: saldo de la cuenta
deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

balance = await account.account_info_double(
    property_id=account_info_pb2.ACCOUNT_BALANCE,
    deadline=deadline
)

print(f"Saldo: ${balance:.2f}")
```

```python
# Obtener el apalancamiento de la cuenta
leverage = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_LEVERAGE
)

print(f"Apalancamiento: 1:{leverage}")
```

```python
# Obtener la divisa de la cuenta
currency = await account.account_info_string(
    property_id=account_info_pb2.ACCOUNT_CURRENCY
)

print(f"Divisa: {currency}")
```

```python
# Comprobar el estado de la cuenta
summary = await account.account_summary()

# Obtener el nivel de margen (account_summary no incluye el margen; se necesita una llamada independiente)
margin_level = await account.account_info_double(
    account_info_pb2.ACCOUNT_MARGIN_LEVEL
)

if margin_level < 100:
    print("[ADVERTENCIA] ¡Nivel de margen crítico!")
elif margin_level < 200:
    print("[ADVERTENCIA] Nivel de margen bajo")
else:
    print("[OK] Nivel de margen saludable")
```

```python
# Validar la cuenta antes de operar
summary = await account.account_summary()

# Comprobar si se permite operar
trade_allowed = await account.account_info_integer(
    property_id=account_info_pb2.ACCOUNT_TRADE_ALLOWED
)

if not trade_allowed:
    raise RuntimeError("El trading está deshabilitado en esta cuenta")

# Comprobar el saldo mínimo
if summary.account_balance < 100:
    raise ValueError(f"Saldo demasiado bajo: ${summary.account_balance:.2f}")

print(f"[OK] La cuenta está lista para operar")
print(f"   Saldo: ${summary.account_balance:.2f} {summary.account_currency}")
print(f"   Apalancamiento: 1:{summary.account_leverage}")
```

```python
# Supervisar el patrimonio de la cuenta en tiempo real
async def monitor_equity(interval: float = 5.0):
    """Supervisa el patrimonio cada N segundos"""
    while True:
        summary = await account.account_summary()

        floating_pnl = summary.account_equity - summary.account_balance

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Patrimonio: ${summary.account_equity:,.2f} | "
              f"Beneficio/Pérdida flotante: ${floating_pnl:+,.2f}")

        await asyncio.sleep(interval)

# await monitor_equity(interval=5.0)
```

```python
# Obtener todos los detalles de la cuenta para el registro
async def log_account_details():
    """Registra información completa de la cuenta"""
    summary = await account.account_summary()

    # Obtener información adicional sobre el margen
    margin_level = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_LEVEL
    )

    free_margin = await account.account_info_double(
        account_info_pb2.ACCOUNT_MARGIN_FREE
    )

    mode_names = {0: "DEMO", 1: "CONCURSO", 2: "REAL"}
    mode = mode_names.get(summary.account_trade_mode, "DESCONOCIDO")

    print(f"{'='*60}")
    print(f"DETALLES DE LA CUENTA")
    print(f"{'='*60}")
    print(f"Login:          #{summary.account_login}")
    print(f"Nombre:         {summary.account_user_name}")
    print(f"Bróker:         {summary.account_company_name}")
    print(f"Modo:           {mode}")
    print(f"Divisa:         {summary.account_currency}")
    print(f"Apalancamiento: 1:{summary.account_leverage}")
    print(f"")
    print(f"Saldo:          ${summary.account_balance:,.2f}")
    print(f"Patrimonio:        ${summary.account_equity:,.2f}")
    print(f"Crédito:        ${summary.account_credit:,.2f}")
    print(f"Margen libre:   ${free_margin:,.2f}")
    print(f"Nivel de margen: {margin_level:.2f}%")
    print(f"{'='*60}")

# await log_account_details()
```

---

## 📚 Véase también

* **Información de símbolos:** [Symbol_Information.Overview](../2. Symbol_Information/Symbol_Information.Overview.md) - obtener datos de símbolos y del mercado.
* **Posiciones y órdenes:** [Positions_Orders.Overview](../3. Positions_Orders/Positions_Orders.Overview.md) - gestionar posiciones y órdenes.
* **Trading:** [Trading_Operations.Overview](../5. Trading_Operations/Trading_Operations.Overview.md) - ejecutar y gestionar operaciones.