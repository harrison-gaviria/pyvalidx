# Type Validators

Los validadores de tipo proporcionan funcionalidades para validar tipos de datos específicos y valores dentro de conjuntos predefinidos.

## is_dict

Valida que el campo sea un diccionario.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.types import is_dict

class ConfigModel(ValidatedModel):
    settings: dict = field_validated(is_dict())
    metadata: dict = field_validated(is_dict("Metadata must be a dictionary"))

# Uso válido
config = ConfigModel(
    settings={"debug": True, "port": 8080},
    metadata={"version": "1.0", "author": "John Doe"}
)

# Uso inválido
try:
    invalid_config = ConfigModel(settings="not a dict")
except ValidationException as e:
    print(e.validations)  # {'settings': 'Must be a dictionary'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must be a dictionary"

---

## is_list

Valida que el campo sea una lista.

```python
from pyvalidx.types import is_list

class PlaylistModel(ValidatedModel):
    songs: list = field_validated(is_list())
    genres: list = field_validated(is_list("Genres must be a list"))

# Uso válido
playlist = PlaylistModel(
    songs=["Song 1", "Song 2", "Song 3"],
    genres=["Rock", "Pop", "Jazz"]
)

# Uso inválido
try:
    invalid_playlist = PlaylistModel(songs="not a list")
except ValidationException as e:
    print(e.validations)  # {'songs': 'Must be a list'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must be a list"

---

## is_boolean

Valida que el campo sea un booleano.

```python
from pyvalidx.types import is_boolean

class SettingsModel(ValidatedModel):
    enabled: bool = field_validated(is_boolean())
    debug_mode: bool = field_validated(is_boolean("Debug mode must be true or false"))

# Uso válido
settings = SettingsModel(
    enabled=True,
    debug_mode=False
)

# Uso inválido
try:
    invalid_settings = SettingsModel(enabled="yes")
except ValidationException as e:
    print(e.validations)  # {'enabled': 'Must be a boolean'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must be a boolean"

---

## is_in

Valida que el campo esté dentro de una lista o conjunto de opciones válidas.

```python
from pyvalidx.types import is_in

class UserModel(ValidatedModel):
    role: str = field_validated(is_in(["admin", "user", "guest"]))
    status: str = field_validated(
        is_in({"active", "inactive", "pending"}, "Status must be active, inactive, or pending")
    )
    priority: int = field_validated(is_in([1, 2, 3, 4, 5]))

# Uso válido
user = UserModel(
    role="admin",
    status="active",
    priority=3
)

# Uso inválido
try:
    invalid_user = UserModel(role="invalid_role")
except ValidationException as e:
    print(e.validations)  # {'role': "Must be one of: ['admin', 'user', 'guest']"}
```

### Parámetros
- `choices` (Union[List[Any], Set[Any]]): Lista o conjunto de valores válidos
- `message` (str, opcional): Mensaje de error personalizado

---

## Ejemplo Completo: Sistema de Configuración

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.types import is_dict, is_list, is_boolean, is_in
from pyvalidx.numeric import is_positive, min_value, max_value

class ApplicationConfigModel(ValidatedModel):
    app_name: str = field_validated(is_required("Application name is required"))
    
    environment: str = field_validated(
        is_required("Environment is required"),
        is_in(["development", "staging", "production"], "Invalid environment")
    )
    
    debug: bool = field_validated(
        is_boolean("Debug must be true or false")
    )
    
    port: int = field_validated(
        is_positive("Port must be positive"),
        min_value(1000, "Port must be at least 1000"),
        max_value(65535, "Port cannot exceed 65535")
    )
    
    allowed_hosts: list = field_validated(
        is_required("Allowed hosts list is required"),
        is_list("Allowed hosts must be a list")
    )
    
    database: dict = field_validated(
        is_required("Database configuration is required"),
        is_dict("Database configuration must be a dictionary")
    )
    
    log_level: str = field_validated(
        is_in(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    )

# Uso válido
config = ApplicationConfigModel(
    app_name="MyApp",
    environment="production",
    debug=False,
    port=8080,
    allowed_hosts=["localhost", "myapp.com"],
    database={
        "host": "localhost",
        "port": 5432,
        "name": "myapp_db"
    },
    log_level="INFO"
)
```

---

## Ejemplo: Validación de Datos JSON

```python
from pyvalidx.types import is_dict, is_list
from pyvalidx.string import is_email

class ApiRequestModel(ValidatedModel):
    user_data: dict = field_validated(
        is_required("User data is required"),
        is_dict("User data must be a valid JSON object")
    )
    
    tags: list = field_validated(
        is_list("Tags must be an array")
    )
    
    action: str = field_validated(
        is_required("Action is required"),
        is_in(["create", "update", "delete"], "Invalid action type")
    )

# Uso válido
api_request = ApiRequestModel(
    user_data={
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    },
    tags=["important", "user", "profile"],
    action="create"
)
```

---

## Ejemplo: Sistema de Roles y Permisos

```python
class UserPermissionModel(ValidatedModel):
    user_id: int = field_validated(is_required(), is_positive())
    
    role: str = field_validated(
        is_required("Role is required"),
        is_in(["admin", "moderator", "editor", "viewer"], "Invalid role")
    )
    
    permissions: list = field_validated(
        is_required("Permissions list is required"),
        is_list("Permissions must be a list")
    )
    
    is_active: bool = field_validated(
        is_boolean("Active status must be true or false")
    )
    
    settings: dict = field_validated(
        is_dict("Settings must be a dictionary")
    )

# Definir permisos válidos
VALID_PERMISSIONS = {
    "read", "write", "delete", "admin", "moderate", "publish"
}

# Validación personalizada para permisos
def validate_permissions(permissions_list, context=None):
    if not isinstance(permissions_list, list):
        return False
    return all(perm in VALID_PERMISSIONS for perm in permissions_list)

class EnhancedUserPermissionModel(ValidatedModel):
    user_id: int = field_validated(is_required(), is_positive())
    
    role: str = field_validated(
        is_required("Role is required"),
        is_in(["admin", "moderator", "editor", "viewer"])
    )
    
    permissions: list = field_validated(
        is_required("Permissions list is required"),
        is_list("Permissions must be a list"),
        custom(validate_permissions, "Invalid permissions in list")
    )
    
    is_active: bool = field_validated(is_boolean())
    
    settings: dict = field_validated(is_dict())

# Uso
user_permission = EnhancedUserPermissionModel(
    user_id=123,
    role="editor",
    permissions=["read", "write", "publish"],
    is_active=True,
    settings={"theme": "dark", "notifications": True}
)
```

---

## Combinando Validadores de Tipo

```python
class ComplexDataModel(ValidatedModel):
    # Lista que debe contener solo strings válidos
    categories: list = field_validated(
        is_required("Categories are required"),
        is_list("Categories must be a list"),
        is_not_empty("Categories list cannot be empty")
    )
    
    # Diccionario con configuración específica
    config: dict = field_validated(
        is_required("Configuration is required"),
        is_dict("Configuration must be a dictionary"),
        is_not_empty("Configuration cannot be empty")
    )
    
    # Estado que debe ser uno de los valores específicos
    status: str = field_validated(
        is_required("Status is required"),
        is_in(["draft", "published", "archived", "deleted"])
    )
    
    # Flag booleano con valor por defecto
    featured: bool = field_validated(is_boolean())

# Uso
data = ComplexDataModel(
    categories=["technology", "programming", "python"],
    config={
        "auto_save": True,
        "max_retries": 3,
        "timeout": 30
    },
    status="published",
    featured=True
)
```

---

## Notas Importantes

- Los validadores de tipo verifican el tipo exacto usando `isinstance()`
- `is_in` funciona con cualquier tipo de dato que soporte el operador `in`
- Los validadores retornan `True` si el valor es `None` (para campos opcionales)
- Para listas y diccionarios vacíos, considera usar también `is_not_empty()` si es necesario
- `is_in` es especialmente útil para validar enums o conjuntos predefinidos de valores
