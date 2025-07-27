# String Validators

Los validadores de cadenas proporcionan funcionalidades específicas para validar y verificar formatos de texto.

## is_email

Valida que el campo tenga un formato de email válido.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.string import is_email

class ContactModel(ValidatedModel):
    email: str = field_validated(is_email())
    backup_email: str = field_validated(is_email("Please provide a valid backup email"))

# Uso válido
contact = ContactModel(
    email="user@example.com",
    backup_email="backup@domain.org"
)

# Uso inválido
try:
    invalid_contact = ContactModel(email="invalid-email")
except ValidationException as e:
    print(e.validations)  # {'email': 'Invalid email format'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Invalid email format"

---

## is_strong_password

Valida que la contraseña sea fuerte (mínimo 8 caracteres, mayúsculas, minúsculas, números y símbolos).

```python
from pyvalidx.string import is_strong_password

class SecurityModel(ValidatedModel):
    password: str = field_validated(is_strong_password())
    admin_password: str = field_validated(
        is_strong_password("Admin password must be extra secure")
    )

# Uso válido
security = SecurityModel(
    password="MySecure123!",
    admin_password="AdminPass456@"
)

# Uso inválido
try:
    weak_security = SecurityModel(password="123")
except ValidationException as e:
    print(e.validations)  # {'password': 'Password must be strong'}
```

### Requisitos de contraseña fuerte:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula  
- Al menos un número
- Al menos un símbolo especial

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Password must be strong"

---

## matches_regex

Valida que el campo coincida con una expresión regular específica.

```python
from pyvalidx.string import matches_regex

class ProductModel(ValidatedModel):
    sku: str = field_validated(
        matches_regex(r'^[A-Z]{2}\d{4}$', "SKU must be 2 letters followed by 4 numbers")
    )
    postal_code: str = field_validated(
        matches_regex(r'^\d{5}$', "Postal code must be 5 digits")
    )

# Uso válido
product = ProductModel(
    sku="AB1234",
    postal_code="12345"
)
```

### Parámetros
- `pattern` (str): Expresión regular a coincidir
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Invalid format"

---

## no_whitespace

Valida que el campo no contenga espacios en blanco.

```python
from pyvalidx.string import no_whitespace

class UserModel(ValidatedModel):
    username: str = field_validated(no_whitespace())
    api_key: str = field_validated(no_whitespace("API key cannot contain spaces"))

# Uso válido
user = UserModel(
    username="johndoe",
    api_key="abc123def456"
)

# Uso inválido
try:
    invalid_user = UserModel(username="john doe")
except ValidationException as e:
    print(e.validations)  # {'username': 'Must not contain spaces'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must not contain spaces"

---

## is_phone

Valida números de teléfono colombianos (móviles y fijos).

```python
from pyvalidx.string import is_phone

class ContactInfoModel(ValidatedModel):
    mobile: str = field_validated(is_phone())
    landline: str = field_validated(is_phone("Invalid landline format"))

# Uso válido
contact = ContactInfoModel(
    mobile="3001234567",      # Móvil
    landline="6012345678"     # Fijo
)

# También acepta formato internacional
international_contact = ContactInfoModel(
    mobile="+573001234567",
    landline="6012345678"
)
```

### Formatos soportados:
- **Móviles**: `3XXXXXXXXX` (10 dígitos empezando por 3)
- **Fijos**: `[1-8]XXXXXXX` o `[1-8]XXXXXXXX` (7-8 dígitos)
- **Internacional**: `+573XXXXXXXXX` para móviles

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Invalid phone format"

---

## has_no_common_password

Valida que la contraseña no esté en una lista de contraseñas comunes.

```python
from pyvalidx.string import has_no_common_password

# Lista de contraseñas comunes
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", 
    "123456789", "12345", "1234", "111111"
}

class SecureUserModel(ValidatedModel):
    password: str = field_validated(
        has_no_common_password(
            COMMON_PASSWORDS, 
            "Please choose a more unique password"
        )
    )

# Uso válido
user = SecureUserModel(password="MyUniquePass123!")

# Uso inválido
try:
    weak_user = SecureUserModel(password="123456")
except ValidationException as e:
    print(e.validations)  # {'password': 'Please choose a more unique password'}
```

### Parámetros
- `dictionary` (Union[List[str], Set[str]]): Lista o set de contraseñas prohibidas
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Password is too common"

---

## Ejemplo Completo: Registro de Usuario

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length, same_as
from pyvalidx.string import is_email, is_strong_password, no_whitespace

COMMON_PASSWORDS = {"123456", "password", "qwerty"}

class UserRegistrationModel(ValidatedModel):
    username: str = field_validated(
        is_required("Username is required"),
        min_length(3, "Username must be at least 3 characters"),
        no_whitespace("Username cannot contain spaces")
    )
    
    email: str = field_validated(
        is_required("Email is required"),
        is_email("Please provide a valid email address")
    )
    
    password: str = field_validated(
        is_required("Password is required"),
        is_strong_password("Password must be strong"),
        has_no_common_password(COMMON_PASSWORDS, "Password is too common")
    )
    
    confirm_password: str = field_validated(
        same_as("password", "Passwords must match")
    )

# Uso
registration = UserRegistrationModel(
    username="johndoe",
    email="john@example.com",
    password="SecurePass123!",
    confirm_password="SecurePass123!"
)
```
