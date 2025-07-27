# Core Validators

Los validadores core proporcionan funcionalidades básicas de validación que son fundamentales para la mayoría de casos de uso.

## is_required

Valida que el campo no sea `None`, cadena vacía, o lista vacía.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required

class UserModel(ValidatedModel):
    name: str = field_validated(is_required())
    email: str = field_validated(is_required("Email is mandatory"))

# Uso
try:
    user = UserModel(name="", email="john@example.com")
except ValidationException as e:
    print(e.validations)  # {'name': 'This field is required'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "This field is required"

---

## min_length

Valida que el campo tenga al menos la longitud especificada.

```python
from pyvalidx.core import min_length

class ProductModel(ValidatedModel):
    name: str = field_validated(min_length(3))
    description: str = field_validated(min_length(10, "Description too short"))

# Uso
product = ProductModel(
    name="iPhone", 
    description="Latest smartphone model"
)
```

### Parámetros
- `length` (int): Longitud mínima requerida
- `message` (str, opcional): Mensaje de error personalizado

---

## max_length

Valida que el campo tenga como máximo la longitud especificada.

```python
from pyvalidx.core import max_length

class CommentModel(ValidatedModel):
    title: str = field_validated(max_length(100))
    content: str = field_validated(max_length(500, "Comment too long"))

# Uso
comment = CommentModel(
    title="Great product!",
    content="I really enjoyed using this product..."
)
```

### Parámetros
- `length` (int): Longitud máxima permitida
- `message` (str, opcional): Mensaje de error personalizado

---

## custom

Envuelve una función de validación personalizada con un mensaje.

```python
from pyvalidx.core import custom

def is_even(value, context=None):
    if value is None:
        return True
    return value % 2 == 0

class NumberModel(ValidatedModel):
    even_number: int = field_validated(
        custom(is_even, "Number must be even")
    )

# Uso
number = NumberModel(even_number=4)  # Válido
```

### Parámetros
- `validator_func`: Función que recibe (value, context) y retorna bool
- `message` (str): Mensaje de error si la validación falla

---

## same_as

Valida que el campo tenga el mismo valor que otro campo.

```python
from pyvalidx.core import same_as

class RegistrationModel(ValidatedModel):
    password: str = field_validated(is_required())
    confirm_password: str = field_validated(
        same_as("password", "Passwords must match")
    )

# Uso
registration = RegistrationModel(
    password="mypass123",
    confirm_password="mypass123"
)
```

### Parámetros
- `other_field` (str): Nombre del campo a comparar
- `message` (str, opcional): Mensaje de error personalizado

---

## is_not_empty

Valida que el campo no esté vacío (diferente de `is_required`).

```python
from pyvalidx.core import is_not_empty

class TagModel(ValidatedModel):
    tags: list = field_validated(is_not_empty("Tags list cannot be empty"))

# Uso
tag_model = TagModel(tags=["python", "validation"])
```

### Parámetros
- `message` (str): Mensaje de error si el campo está vacío

---

## required_if

Valida que el campo sea requerido si otro campo tiene un valor específico.

```python
from pyvalidx.core import required_if

class OrderModel(ValidatedModel):
    payment_method: str = field_validated(is_required())
    card_number: str = field_validated(
        required_if("payment_method", "credit_card", "Card number required for credit card payments")
    )

# Uso
order = OrderModel(
    payment_method="credit_card",
    card_number="1234-5678-9012-3456"
)
```

### Parámetros
- `other_field` (str): Campo que condiciona la validación
- `other_value` (Any): Valor que hace requerido este campo
- `message` (str): Mensaje de error personalizado

---

## Combinando Validadores

Puedes combinar múltiples validadores core:

```python
class UserProfileModel(ValidatedModel):
    username: str = field_validated(
        is_required("Username is required"),
        min_length(3, "Username too short"),
        max_length(20, "Username too long")
    )
    bio: str = field_validated(
        max_length(500, "Bio too long")
    )
    website: str = field_validated(
        required_if("bio", "", "Website required if no bio provided")
    )
```
