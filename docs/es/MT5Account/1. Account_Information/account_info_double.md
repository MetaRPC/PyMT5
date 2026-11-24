# Obtener propiedades de tipo double de la cuenta

> **Request:** una propiedad específica de tipo double de la cuenta desde el terminal **MT5** mediante el identificador de propiedad.

**Información de la API:**

* **API de bajo nivel:** `MT5Account.account_info_double(...)` (defined in `package/MetaRpcMT5/mt5_account.py`)

* **Servicio gRPC:** `mt5_term_api.AccountInformation`

* **Definición de Proto:** `AccountInfoDouble` (defined in `mt5-term-api-account-information.proto`)

### RPC

* **Servicio:** `mt5_term_api.AccountInformation`

* **Método:** `AccountInfoDouble(AccountInfoDoubleRequest) -> AccountInfoDoubleReply`

* **Cliente de bajo nivel (generado):** `AccountInformationStub.AccountInfoDouble(request, metadata, timeout)`

## 💬 Lo esencial

* **Qué es.** Obtiene una propiedad específica de tipo double de la cuenta mediante su ID (saldo, capital, margen, etc.).

* **Para qué lo necesitas.** Obtén métricas individuales de la cuenta sin recuperar todos los datos. Es útil para comprobaciones específicas.

* **Cuándo utilizarlo.** Utiliza `account_summary()` para obtener varias propiedades. Utiliza este método para consultar una sola propiedad.

---

## 🎯 Objetivo

Utilízalo para consultar propiedades numéricas específicas de la cuenta:

* Comprobar el saldo de la cuenta antes de operar

* Supervisar el uso del margen y el nivel de margen

* Verificar la disponibilidad de margen libre

* Seguir las ganancias/pérdidas flotantes

* Supervisar los niveles de margin call y stop out

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [account_info_double - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_info_double_HOW.md)**

---

## Firma del método

```python

async def account_info_double(

    self,

    property_id: account_info_pb2.AccountInfoDoublePropertyType,

    deadline: Optional[datetime] = None,

    cancellation_event: Optional[asyncio.Event] = None,

) -> float

```

**Mensaje de solicitud:**

```protobuf

message AccountInfoDoubleRequest {

  AccountInfoDoublePropertyType property_id = 1;

}

```

**Mensaje de respuesta:**

```protobuf

message AccountInfoDoubleReply {

  oneof response {

    AccountInfoDoubleData data = 1;

    Error error = 2;

  }

}

message AccountInfoDoubleData {

  double requested_value = 1;

}

```

---

## 🔽 Entrada

| Parámetro     | Tipo                              | Descripción                                             |

| ------------- | --------------------------------- | ------------------------------------------------------- |

| `property_id` | `AccountInfoDoublePropertyType` (enum) | Identificador de la propiedad que especifica qué propiedad se debe obtener |

| `deadline`    | `datetime` (optional)             | Fecha límite para la llamada gRPC (fecha y hora UTC)              |

| `cancellation_event` | `asyncio.Event` (optional) | Evento para cancelar la operación                           |

**Opciones de fecha límite:**

```python

from datetime import datetime, timedelta, timezone

import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. Con fecha límite (recomendado)

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

value = await account.account_info_double(

    property_id=account_info_pb2.ACCOUNT_BALANCE,

    deadline=deadline

)

# 2. Con evento de cancelación

cancel_event = asyncio.Event()

value = await account.account_info_double(

    property_id=account_info_pb2.ACCOUNT_BALANCE,

    cancellation_event=cancel_event

)

# Más tarde: cancel_event.set()

# 3. Sin fecha límite (se aplicará el tiempo de espera predeterminado si está configurado)

value = await account.account_info_double(

    property_id=account_info_pb2.ACCOUNT_BALANCE

)

```

---

## ⬆️ Salida

| Campo             | Tipo      | Tipo de Python | Descripción                                      |

| ----------------- | --------- | ----------- | ------------------------------------------------ |

| `requested_value` | `double`  | `float`     | El valor de la propiedad de cuenta solicitada      |

**Valor devuelto:** El método devuelve directamente `float` (extraído de `AccountInfoDoubleData.requested_value`).

---

## 🧱 Enumeraciones relacionadas (de Proto)

> **💡 Nota:** Las tablas muestran nombres de constantes simplificados para facilitar la lectura.

> En el código Python, puedes utilizar tanto el formato completo como el abreviado:

>

> **Formato completo:** `account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE`

> **Formato abreviado:** `account_info_pb2.ACCOUNT_BALANCE`

>

> Ambos formatos son válidos en Python protobuf. Recomendamos el **formato abreviado** por simplicidad.

### `AccountInfoDoublePropertyType`

Definido en `mt5-term-api-account-information.proto`.

| Constante | Valor | Descripción |

|----------|-------|-------------|

| `ACCOUNT_BALANCE` | 0 | Saldo de la cuenta en la divisa de depósito |

| `ACCOUNT_CREDIT` | 1 | Crédito de la cuenta en la divisa de depósito |

| `ACCOUNT_PROFIT` | 2 | Beneficio actual de la cuenta en la divisa de depósito |

| `ACCOUNT_EQUITY` | 3 | Patrimonio de la cuenta en la divisa de depósito |

| `ACCOUNT_MARGIN` | 4 | Margen utilizado de la cuenta en la divisa de depósito |

| `ACCOUNT_MARGIN_FREE` | 5 | Margen libre de la cuenta en la divisa de depósito |

| `ACCOUNT_MARGIN_LEVEL` | 6 | Nivel de margen de la cuenta en porcentaje |

| `ACCOUNT_MARGIN_SO_CALL` | 7 | Nivel de margin call (en % o en la divisa de depósito) |

| `ACCOUNT_MARGIN_SO_SO` | 8 | Nivel de stop out del margen (en % o en la divisa de depósito) |

| `ACCOUNT_MARGIN_INITIAL` | 9 | Margen inicial (reservado para órdenes pendientes) |

| `ACCOUNT_MARGIN_MAINTENANCE` | 10 | Margen de mantenimiento (patrimonio mínimo reservado) |

| `ACCOUNT_ASSETS` | 11 | Activos actuales de la cuenta |

| `ACCOUNT_LIABILITIES` | 12 | Pasivos actuales de la cuenta |

| `ACCOUNT_COMMISSION_BLOCKED` | 13 | Importe actual de la comisión bloqueada |

**Uso en Python:**

```python

import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Accede directamente a las constantes

property_id = account_info_pb2.ACCOUNT_BALANCE  # = 0

# o utiliza el nombre completo de la enumeración

property_id = account_info_pb2.AccountInfoDoublePropertyType.ACCOUNT_BALANCE  # = 0

```

---

## 🧩 Notas y consejos

* **Reconexión automática:** Todos los métodos de `MT5Account` cuentan con protección integrada contra errores gRPC transitorios, con reconexión automática mediante `execute_with_reconnect`.

* **Tiempo de espera predeterminado:** Si `deadline` es `None`, el método esperará indefinidamente (o hasta que se agote el tiempo de espera del servidor).

* **Tipos de propiedades:** Los niveles de margin call y stop out pueden expresarse en porcentajes o en la divisa de depósito, según la configuración de la cuenta.

* **Seguridad de subprocesos:** Todos los métodos asíncronos se pueden llamar de forma segura y simultánea desde varias tareas de asyncio.

---

## 🔗 Ejemplos de uso

### 1) Obtener el saldo de la cuenta

```python

import asyncio

from datetime import datetime, timedelta, timezone

from MetaRpcMT5.mt5_account import MT5Account

import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

async def main():

    # Crear una instancia de la cuenta

    account = MT5Account(

        user=12345678,

        password="your_password",

        grpc_server="your-server.com:443"

    )

    # Conectar primero

    await account.connect_by_server_name("MetaQuotes-Demo")

    try:

        # Establecer la fecha límite

        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

        # Obtener el saldo

        balance = await account.account_info_double(

            property_id=account_info_pb2.ACCOUNT_BALANCE,

            deadline=deadline

        )

        print(f"Saldo de la cuenta: ${balance:.2f}")

    finally:

        await account.channel.close()

asyncio.run(main())

```

### 2) Obtener el patrimonio actual

```python

async def get_equity(account: MT5Account) -> float:

    """Obtener el patrimonio actual de la cuenta"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    equity = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_EQUITY,

        deadline=deadline

    )

    return equity

# Uso:

equity = await get_equity(account)

print(f"Patrimonio actual: ${equity:.2f}")

```

### 3) Comprobar el nivel de margen antes de operar

```python

async def check_margin_level(account: MT5Account, min_level: float = 200.0) -> bool:

    """

    Comprueba si el nivel de margen está por encima del umbral mínimo.

    Argumentos:

        account: instancia de MT5Account

        min_level: nivel mínimo de margen requerido (%)

    Devuelve:

        True si el nivel de margen es suficiente

    Lanza:

        ValueError: si el nivel de margen está por debajo del mínimo

    """

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    margin_level = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,

        deadline=deadline

    )

    print(f"Nivel de margen: {margin_level:.2f}%")

    if margin_level < min_level:

        raise ValueError(

            f"Nivel de margen {margin_level:.2f}% está por debajo del mínimo {min_level:.2f}%"

        )

    return True

# Uso:

try:

    await check_margin_level(account, min_level=200.0)

    print("[OK] Es seguro operar")

except ValueError as e:

    print(f"[ERROR] No se puede operar: {e}")

```

### 4) Obtener el margen libre

```python

async def get_free_margin(account: MT5Account) -> float:

    """Obtener el margen libre desponible"""

    # Sin fecha límite: se aplicará el tiempo de espera predeterminado

    free_margin = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE

    )

    return free_margin

# Uso:

free_margin = await get_free_margin(account)

print(f"Margen libre: ${free_margin:.2f}")

```

### 5) Supervisar las ganancias/pérdidas flotantes

```python

async def monitor_profit(account: MT5Account, interval: float = 5.0):

    """Supervisar las ganancias/pérdidas flotantes cada N segundos"""

    while True:

        try:

            deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

            profit = await account.account_info_double(

                property_id=account_info_pb2.ACCOUNT_PROFIT,

                deadline=deadline

            )

            sign = "+" if profit >= 0 else ""

            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] Ganancias/pérdidas flotantes: {sign}${profit:.2f}")

        except Exception as e:

            print(f"Error: {e}")

        await asyncio.sleep(interval)

# Uso:

# await monitor_profit(account, interval=5.0)  # Actualizar cada 5 segundos

```

### 6) Comprobar varias propiedades secuencialmente

```python

from dataclasses import dataclass

@dataclass

class MarginInfo:

    used_margin: float

    free_margin: float

    margin_level: float

async def get_margin_info(account: MT5Account) -> MarginInfo:

    """Obtener información completa sobre el margen"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

    # Obtener el margen utilizado

    used_margin = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN,

        deadline=deadline

    )

    # Obtener el margen libre

    free_margin = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE,

        deadline=deadline

    )

    # Obtener el nivel de margen

    margin_level = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,

        deadline=deadline

    )

    return MarginInfo(

        used_margin=used_margin,

        free_margin=free_margin,

        margin_level=margin_level

    )

# Uso:

info = await get_margin_info(account)

print(f"Información del margen:")

print(f"  Utilizado: ${info.used_margin:.2f}")

print(f"  Libre: ${info.free_margin:.2f}")

print(f"  Nivel: {info.margin_level:.2f}%")

# Nota: para obtener un mejor rendimiento, utiliza account_summary() en su lugar

# para obtener todas las propiedades en una sola llamada

```

### 7) Con evento de cancelación

```python

async def get_balance_cancellable(account: MT5Account, cancel_event: asyncio.Event) -> float:

    """Obtener el saldo con compatibilidad con la cancelación"""

    try:

        balance = await account.account_info_double(

            property_id=account_info_pb2.ACCOUNT_BALANCE,

            cancellation_event=cancel_event

        )

        return balance

    except asyncio.CancelledError:

        print("Operación cancelada")

        raise

# Uso:

cancel_event = asyncio.Event()

# Iniciar la operación

task = asyncio.create_task(get_balance_cancellable(account, cancel_event))

# Cancelar después de 1 segundo

await asyncio.sleep(1)

cancel_event.set()

try:

    balance = await task

except asyncio.CancelledError:

    print("Cancelado por el usuario")

```

---

## 🔧 Patrones habituales

### Comprobación de seguridad antes de operar

```python

async def can_trade(account: MT5Account, required_margin: float) -> bool:

    """

    Comprueba si la cuenta tiene suficiente margen libre para operar.

    Argumentos:

        account: instancia de MT5Account

        required_margin: margen necesario para la operación

    Devuelve:

        True si hay suficiente margen desponible

    """

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    free_margin = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN_FREE,

        deadline=deadline

    )

    if free_margin < required_margin:

        print(f"[ERROR] Margen insuficiente: se necesitan ${required_margin:.2f}, disponibles ${free_margin:.2f}")

        return False

    print(f"[OK] Margen suficiente: ${free_margin:.2f} disponibles")

    return True

```

### Sistema de advertencia del nivel de margen

```python

async def check_margin_warning(account: MT5Account):

    """Comprobar el nivel de margen y emitir una advertencia si es demasiado bajo"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    level = await account.account_info_double(

        property_id=account_info_pb2.ACCOUNT_MARGIN_LEVEL,

        deadline=deadline

    )

    if level < 100:

        print(f"[CRÍTICO] Nivel de margen {level:.2f}% - ¡El stop out es inminente!")

    elif level < 200:

        print(f"[ADVERTENCIA] Nivel de margen {level:.2f}% - Zona de margin call")

    elif level < 500:

        print(f"[PRECAUCIÓN] Nivel de margen {level:.2f}% - Supervisar atentamente")

    else:

        print(f"[OK] Nivel de margen {level:.2f}%")

```

### Comprobación del estado de la cuenta

```python

async def check_account_health(account: MT5Account):

    """Comprobación completa del estado de la cuenta"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Obtener todas las métricas críticas

    balance = await account.account_info_double(

        account_info_pb2.ACCOUNT_BALANCE,

        deadline

    )

    equity = await account.account_info_double(

        account_info_pb2.ACCOUNT_EQUITY,

        deadline

    )

    profit = await account.account_info_double(

        account_info_pb2.ACCOUNT_PROFIT,

        deadline

    )

    margin_level = await account.account_info_double(

        account_info_pb2.ACCOUNT_MARGIN_LEVEL,

        deadline

    )

    print(f"Informe del estado de la cuenta:")

    print(f"  Saldo: ${balance:.2f}")

    print(f"  Patrimonio: ${equity:.2f}")

    print(f"  Ganancias/pérdidas flotantes: ${profit:+.2f}")

    print(f"  Nivel de margen: {margin_level:.2f}%")

    # Evaluación del estado

    if margin_level > 500 and equity >= balance:

        print("  Estado: [SALUDABLE]")

    elif margin_level > 200:

        print("  Estado: [MODERADO]")

    else:

        print("  Estado: [DE RIESGO]")

```

---

## 📚 Ver también

* [account_summary](./account_summary.md) - Obtener todas las propiedades de la cuenta en una sola llamada (RECOMENDADO)

* [account_info_integer](./account_info_integer.md) - Obtener propiedades específicas de tipo entero de la cuenta

* [account_info_string](./account_info_string.md) - Obtener propiedades específicas de tipo cadena de la cuenta