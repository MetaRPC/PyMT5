# Obtener propiedades enteras de la cuenta

> **Solicitud:** una propiedad de cuenta de tipo entero específica desde el terminal **MT5** mediante un identificador de propiedad.

**Información de la API:**

* **API de bajo nivel:** `MT5Account.account_info_integer(...)` (definido en `package/MetaRpcMT5/mt5_account.py`)

* **Servicio gRPC:** `mt5_term_api.AccountInformation`

* **Definición de Proto:** `AccountInfoInteger` (definido en `mt5-term-api-account-information.proto`)

### RPC

* **Servicio:** `mt5_term_api.AccountInformation`

* **Método:** `AccountInfoInteger(AccountInfoIntegerRequest) -> AccountInfoIntegerReply`

* **Cliente de bajo nivel (generado):** `AccountInformationStub.AccountInfoInteger(request, metadata, timeout)`

## 💬 Lo esencial

* **Qué es.** Obtiene una propiedad de cuenta específica de tipo entero mediante su ID (inicio de sesión, apalancamiento, modo de trading, etc.).

* **Para qué lo necesitas.** Obtiene ajustes individuales de la cuenta sin recuperar todos los datos. Es útil para comprobar la configuración.

* **Cuándo utilizarlo.** Utilice `account_summary()` para consultar varias propiedades. Utilice este método para consultas de una sola propiedad.

---

## 🎯 Propósito

Utilízalo para consultar propiedades enteras específicas de la cuenta:

* Obtener el número de inicio de sesión de la cuenta

* Comprobar el apalancamiento de la cuenta

* Verificar los permisos de trading (trading permitido, trading permitido para expertos)

* Comprobar el modo de trading de la cuenta (demo/real/concurso)

* Obtener el límite máximo de órdenes pendientes

* Verificar el modo de cálculo del margen

* Comprobar los ajustes de cierre FIFO y cobertura

---

## 📚 Tutorial

Para obtener una explicación detallada línea por línea con ejemplos, consulta:

**-> [account_info_integer - Cómo funciona](../HOW_IT_WORK/1. Account_information_HOW/account_info_integer_HOW.md)**

---

## Firma del método

```python

async def account_info_integer(

    self,

    property_id: account_info_pb2.AccountInfoIntegerPropertyType,

    deadline: Optional[datetime] = None,

    cancellation_event: Optional[asyncio.Event] = None,

) -> int

```

**Mensaje de solicitud:**

```protobuf

message AccountInfoIntegerRequest {

  AccountInfoIntegerPropertyType property_id = 1;

}

```

**Mensaje de respuesta:**

```protobuf

message AccountInfoIntegerReply {

  oneof response {

    AccountInfoIntegerData data = 1;

    Error error = 2;

  }

}

message AccountInfoIntegerData {

  int64 requested_value = 1;

}

```

---

## 🔽 Entrada

| Parámetro     | Tipo                              | Descripción                                             |

| ------------- | --------------------------------- | ------------------------------------------------------- |

| `property_id` | `AccountInfoIntegerPropertyType` (enum) | Identificador de la propiedad que especifica qué propiedad se debe obtener |

| `deadline`    | `datetime` (optional)             | Plazo límite para la llamada gRPC (fecha y hora UTC)              |

| `cancellation_event` | `asyncio.Event` (optional) | Evento para cancelar la operación                           |

**Opciones de plazo límite:**

```python

from datetime import datetime, timedelta, timezone

import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# 1. Con plazo límite (recomendado)

deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

value = await account.account_info_integer(

    property_id=account_info_pb2.ACCOUNT_LEVERAGE,

    deadline=deadline

)

# 2. Con evento de cancelación

cancel_event = asyncio.Event()

value = await account.account_info_integer(

    property_id=account_info_pb2.ACCOUNT_LEVERAGE,

    cancellation_event=cancel_event

)

# 3. Sin plazo límite (utiliza el tiempo de espera predeterminado si está configurado)

value = await account.account_info_integer(

    property_id=account_info_pb2.ACCOUNT_LEVERAGE

)

```

---

## ⬆️ Salida

| Campo             | Tipo    | Tipo de Python | Descripción                                      |

| ----------------- | ------- | ----------- | ------------------------------------------------ |

| `requested_value` | `int64` | `int`       | El valor de la propiedad de cuenta solicitada      |

**Valor devuelto:** El método devuelve directamente `int` (extraído de `AccountInfoIntegerData.requested_value`).

---

## 🧱 Enumeraciones relacionadas (de proto)

> **Nota:** Las tablas muestran nombres de constantes simplificados para facilitar la lectura.

> En el código Python, puedes utilizar el formato completo o el abreviado:

>

> **Formato completo:** `account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE`

> **Formato abreviado:** `account_info_pb2.ACCOUNT_LEVERAGE`

>

> Ambos formatos son válidos en Python protobuf. Recomendamos el **formato corto** por simplicidad.

### `AccountInfoIntegerPropertyType`

Definido en `mt5-term-api-account-information.proto`.

| Constante | Valor | Descripción |

|----------|-------|-------------|

| `ACCOUNT_LOGIN` | 0 | Número de cuenta |

| `ACCOUNT_TRADE_MODE` | 1 | Modo de trading de la cuenta (demo/real/concurso) |

| `ACCOUNT_LEVERAGE` | 2 | Apalancamiento de la cuenta |

| `ACCOUNT_LIMIT_ORDERS` | 3 | Número máximo permitido de órdenes pendientes activas |

| `ACCOUNT_MARGIN_SO_MODE` | 4 | Modo para establecer el margen mínimo permitido |

| `ACCOUNT_TRADE_ALLOWED` | 5 | Trading permitido para la cuenta actual |

| `ACCOUNT_TRADE_EXPERT` | 6 | Trading permitido para un Asesor Experto |

| `ACCOUNT_MARGIN_MODE` | 7 | Modo de cálculo del margen |

| `ACCOUNT_CURRENCY_DIGITS` | 8 | Número de dígitos después del separador decimal para la divisa de la cuenta |

| `ACCOUNT_FIFO_CLOSE` | 9 | Indicador de que una posición solo puede cerrarse según la regla FIFO |

| `ACCOUNT_HEDGE_ALLOWED` | 10 | La cobertura está permitida |

**Uso en Python:**

```python

import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2

# Accede directamente a las constantes

property_id = account_info_pb2.ACCOUNT_LEVERAGE  # = 2

# o utiliza el nombre completo de la enumeración

property_id = account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE  # = 2

```

---

## 🧩 Notas y consejos

* **Reconexión automática:** Todos los métodos de `MT5Account` cuentan con protección integrada frente a errores transitorios de gRPC, con reconexión automática mediante `execute_with_reconnect`.

* **Tiempo de espera predeterminado:** Si `deadline` es `None`, el método esperará indefinidamente (o hasta el tiempo de espera del servidor).

* **Es preferible account_summary:** Para varias propiedades, utiliza `account_summary()` en su lugar para evitar múltiples viajes de ida y vuelta.

* **Conexión obligatoria:** Debe llamar a `connect_by_host_port()` o `connect_by_server_name()` antes de utilizar este método.

* **Valores booleanos:** Propiedades como `TRADE_ALLOWED`, `TRADE_EXPERT`, `FIFO_CLOSE`, `HEDGE_ALLOWED` devuelven 1 (true) o 0 (false).

* **Seguridad de subprocesos:** Todos los métodos asíncronos pueden llamarse simultáneamente de forma segura desde varias tareas de asyncio.

* **Gestión del UUID:** El servidor genera automáticamente el UUID de la instancia del terminal si no se proporciona. 

  Para un control explícito (por ejemplo, en escenarios de streaming), pasa `id_=uuid4()` al constructor.

---

## 🔗 Ejemplos de uso

### 1) Obtener el apalancamiento de la cuenta

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

        # Establecer el plazo límite

        deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

        # Obtener el apalancamiento

        leverage = await account.account_info_integer(

            property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,

            deadline=deadline

        )

        print(f"Apalancamiento de la cuenta: 1:{leverage}")

    finally:

        await account.channel.close()

asyncio.run(main())

```

### 2) Obtener el número de inicio de sesión de la cuenta

```python

async def get_account_login(account: MT5Account) -> int:

    """Obtener el número de inicio de sesión de la cuenta"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    login = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LOGIN,

        deadline=deadline

    )

    return login

# Uso:

login = await get_account_login(account)

print(f"Inicio de sesión de la cuenta: {login}")

```

### 3) Comprobar si el trading está permitido

```python

async def is_trading_allowed(account: MT5Account) -> bool:

    """

    Comprueba si el trading está permitido para esta cuenta.

    Devuelve:

        True si el trading está permitido; False en caso contrario

    """

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    trade_allowed = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,

        deadline=deadline

    )

    # Devuelve 1 (verdadero) o 0 (falso)

    is_allowed = bool(trade_allowed)

    if is_allowed:

        print("[OK] El trading está permitido")

    else:

        print("[ERROR] El trading está deshabilitado")

    return is_allowed

# Uso:

if await is_trading_allowed(account):

    # Colocar órdenes

    pass

else:

    print("No se puede operar con esta cuenta")

```

### 4) Comprobar los permisos del Asesor Experto

```python

async def is_ea_allowed(account: MT5Account) -> bool:

    """Comprueba si los Asesores Expertos tienen permitido operar"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    ea_allowed = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_EXPERT,

        deadline=deadline

    )

    return bool(ea_allowed)

# Uso:

if await is_ea_allowed(account):

    print("[OK] Los Asesores Expertos pueden operar")

else:

    print("[ERROR] Los Asesores Expertos están deshabilitados")

```

### 5) Obtener el límite máximo de órdenes pendientes

```python

async def get_max_pending_orders(account: MT5Account) -> int:

    """Obtiene el número máximo permitido de órdenes pendientes"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    limit = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LIMIT_ORDERS,

        deadline=deadline

    )

    return limit

# Uso:

max_orders = await get_max_pending_orders(account)

print(f"Máximo de órdenes pendientes: {max_orders}")

if max_orders == 0:

    print("[WARNING] No hay límite para las órdenes pendientes (o es ilimitado)")

```

### 6) Comprobar el tipo de cuenta (demo/real/concurso)

```python

async def get_account_type(account: MT5Account) -> str:

    """

    Obtiene el modo de trading de la cuenta.

    Devuelve:

        "DEMO", "CONTEST" o "REAL"

    """

    deadline = datetime.now(timezone.utc) + timedelta(seconds=3)

    trade_mode = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_MODE,

        deadline=deadline

    )

    # Asignar nombres legibles

    mode_map = {

        0: "DEMO",

        1: "CONTEST",

        2: "REAL"

    }

    mode_name = mode_map.get(trade_mode, f"UNKNOWN ({trade_mode})")

    print(f"Tipo de cuenta: {mode_name}")

    return mode_name

# Uso:

account_type = await get_account_type(account)

if account_type == "DEMO":

    print("[WARNING] Ejecutándose en una cuenta demo")

elif account_type == "REAL":

    print("[CRITICAL] Ejecutándose en una cuenta real: ¡ten cuidado!")

```

### 7) Comprobar los ajustes de cobertura

```python

async def check_hedging_settings(account: MT5Account):

    """Comprueba si la cobertura y el cierre FIFO están habilitados"""

    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Comprobar si la cobertura está permitida

    hedge_allowed = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_HEDGE_ALLOWED,

        deadline=deadline

    )

    # Comprobar la regla de cierre FIFO

    fifo_close = await account.account_info_integer(

        property_id=account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_FIFO_CLOSE,

        deadline=deadline

    )

    print(f"Ajustes de cobertura:")

    print(f"  Cobertura permitida: {'Sí' if hedge_allowed else 'No'}")

    print(f"  Cierre FIFO: {'Habilitado' if fifo_close else 'Deshabilitado'}")

    return {

        "hedge_allowed": bool(hedge_allowed),

        "fifo_close": bool(fifo_close)

    }

# Uso:

settings = await check_hedging_settings(account)

if settings["hedge_allowed"]:

    print("[OK] Se pueden abrir posiciones opuestas en el mismo símbolo")

else:

    print("[INFO] No se puede realizar cobertura: solo está disponible el modo netting")

```

---

## Patrones comunes

### Validación previa al trading

```python

async def validate_account_for_trading(account: MT5Account) -> bool:

    """

    Valida que la cuenta esté lista para operar.

    Devuelve:

        True si la cuenta está lista para operar

    """

    deadline = datetime.now(timezone.utc) + timedelta(seconds=5)

    # Comprobar que el trading esté permitido

    trade_allowed = await account.account_info_integer(

        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_ALLOWED,

        deadline

    )

    if not trade_allowed:

        print("[ERROR] El trading está deshabilitado en esta cuenta")

        return False

    # Comprobar que el apalancamiento sea razonable

    leverage = await account.account_info_integer(

        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_LEVERAGE,

        deadline

    )

    if leverage < 1:

        print("[ERROR] Configuración de apalancamiento no válida")

        return False

    print(f"[OK] La cuenta está lista para operar (apalancamiento: 1:{leverage})")

    return True

```

### Comprobador del tipo de cuenta

```python

async def require_demo_account(account: MT5Account):

    """Asegura que se esté ejecutando en una cuenta demo (comprobación de seguridad)"""

    trade_mode = await account.account_info_integer(

        account_info_pb2.AccountInfoIntegerPropertyType.ACCOUNT_TRADE_MODE

    )

    if trade_mode != 0:  # 0 = DEMO

        raise RuntimeError(

            f"[CRITICAL] ¡Este script requiere una cuenta DEMO! Modo actual: {trade_mode}"

        )

    print("[OK] Confirmado: se está ejecutando en una cuenta DEMO")

```

---

## 📚 Véase también

* [account_summary](./account_summary.md) - Obtener todas las propiedades de la cuenta en una sola llamada (RECOMENDADO)

* [account_info_double](./account_info_double.md) - Obtener propiedades específicas de la cuenta de tipo double

* [account_info_string](./account_info_string.md) - Obtener propiedades específicas de la cuenta de tipo string