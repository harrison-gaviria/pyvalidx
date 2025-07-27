# Custom Validators

PyValidX permite crear validadores personalizados para casos de uso específicos que no están cubiertos por los validadores predefinidos.

## Creando Validadores Personalizados

### Función Básica de Validación

Un validador personalizado es una función que:
- Recibe dos parámetros: `value` y `context` (opcional)
- Retorna `True` si la validación es exitosa, `False` si falla
- Tiene un atributo `__message__` con el mensaje de error

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import custom

def is_even(value, context=None):
    """Valida que el número sea par"""
    if value is None:
        return True
    try:
        return int(value) % 2 == 0
    except (ValueError, TypeError):
        return False

class NumberModel(ValidatedModel):
    even_number: int = field_validated(
        custom(is_even, "Number must be even")
    )

# Uso
number = NumberModel(even_number=4)  # Válido
```

### Validador como Función Factory

Para validadores más flexibles, crea una función que retorne el validador:

```python
def min_words(word_count: int, message: str = None):
    """Factory para validar cantidad mínima de palabras"""
    message = message or f"Must contain at least {word_count} words"
    
    def validator(value, context=None):
        if value is None:
            return True
        word_list = str(value).strip().split()
        return len(word_list) >= word_count
    
    validator.__message__ = message
    return validator

class ArticleModel(ValidatedModel):
    title: str = field_validated(min_words(2, "Title must have at least 2 words"))
    content: str = field_validated(min_words(10, "Content must have at least 10 words"))

# Uso
article = ArticleModel(
    title="Python Validation Guide",
    content="This is a comprehensive guide about creating custom validators in Python..."
)
```

---

## Validadores Contextuales

Los validadores pueden acceder a otros campos del modelo a través del parámetro `context`:

```python
def password_not_contains_username(value, context=None):
    """Valida que la contraseña no contenga el nombre de usuario"""
    if value is None or context is None:
        return True
    
    username = context.get('username', '').lower()
    password = str(value).lower()
    
    return username not in password

class UserRegistrationModel(ValidatedModel):
    username: str = field_validated(is_required())
    password: str = field_validated(
        is_required(),
        custom(password_not_contains_username, "Password cannot contain username")
    )

# Uso válido
user = UserRegistrationModel(
    username="johndoe",
    password="SecurePass123!"
)

# Uso inválido
try:
    invalid_user = UserRegistrationModel(
        username="johndoe",
        password="johndoepass"
    )
except ValidationException as e:
    print(e.validations)  # {'password': 'Password cannot contain username'}
```

---

## Validadores Complejos

### Validación de Estructura de Datos

```python
def is_valid_address(value, context=None):
    """Valida que el diccionario tenga la estructura de una dirección"""
    if value is None:
        return True
    
    if not isinstance(value, dict):
        return False
    
    required_fields = ['street', 'city', 'postal_code']
    return all(field in value and value[field] for field in required_fields)

class CustomerModel(ValidatedModel):
    name: str = field_validated(is_required())
    address: dict = field_validated(
        custom(is_valid_address, "Address must contain street, city, and postal_code")
    )

# Uso válido
customer = CustomerModel(
    name="John Doe",
    address={
        "street": "123 Main St",
        "city": "Anytown",
        "postal_code": "12345",
        "country": "USA"  # Campo opcional
    }
)
```

### Validación de Listas con Elementos Específicos

```python
def all_valid_emails(value, context=None):
    """Valida que todos los elementos de la lista sean emails válidos"""
    if value is None:
        return True
    
    if not isinstance(value, list):
        return False
    
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return all(re.match(email_pattern, str(email)) for email in value)

class NewsletterModel(ValidatedModel):
    subject: str = field_validated(is_required())
    recipients: list = field_validated(
        is_required(),
        custom(all_valid_emails, "All recipients must be valid email addresses")
    )

# Uso
newsletter = NewsletterModel(
    subject="Monthly Newsletter",
    recipients=["user1@example.com", "user2@example.com", "user3@example.com"]
)
```

---

## Validadores con Dependencias Externas

### Validación con Base de Datos

```python
def username_not_exists(value, context=None):
    """Valida que el username no exista en la base de datos"""
    if value is None:
        return True
    
    # Simulación de consulta a base de datos
    existing_usernames = ["admin", "root", "test", "demo"]  # En la práctica, esto vendría de la DB
    
    return str(value).lower() not in existing_usernames

class NewUserModel(ValidatedModel):
    username: str = field_validated(
        is_required(),
        min_length(3),
        custom(username_not_exists, "Username already exists")
    )
    email: str = field_validated(is_required(), is_email())
```

### Validación con APIs Externas

```python
def is_valid_country_code(value, context=None):
    """Valida código de país usando una lista predefinida"""
    if value is None:
        return True
    
    # Lista de códigos ISO 3166-1 alpha-2 (simulada)
    valid_codes = {
        "US", "CA", "GB", "FR", "DE", "IT", "ES", "BR", "AR", "CO", 
        "MX", "JP", "CN", "IN", "AU", "NZ", "ZA", "EG", "NG", "KE"
    }
    
    return str(value).upper() in valid_codes

class InternationalOrderModel(ValidatedModel):
    customer_name: str = field_validated(is_required())
    country_code: str = field_validated(
        is_required(),
        custom(is_valid_country_code, "Invalid country code")
    )
```

---

## Validadores Reutilizables

### Creando una Librería de Validadores

```python
# validators_library.py
import re
from typing import Any, Optional, Dict, List, Set

def is_credit_card(value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
    """Valida número de tarjeta de crédito usando algoritmo de Luhn"""
    if value is None:
        return True
    
    # Remover espacios y guiones
    card_number = re.sub(r'[\s-]', '', str(value))
    
    # Verificar que solo contenga dígitos
    if not card_number.isdigit():
        return False
    
    # Algoritmo de Luhn
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    
    return sum(digits) % 10 == 0

def is_isbn(value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
    """Valida código ISBN-10 o ISBN-13"""
    if value is None:
        return True
    
    isbn = re.sub(r'[\s-]', '', str(value))
    
    if len(isbn) == 10:
        return _validate_isbn10(isbn)
    elif len(isbn) == 13:
        return _validate_isbn13(isbn)
    
    return False

def _validate_isbn10(isbn: str) -> bool:
    """Valida ISBN-10"""
    if not isbn[:-1].isdigit():
        return False
    
    if isbn[-1] not in '0123456789X':
        return False
    
    total = 0
    for i, digit in enumerate(isbn[:-1]):
        total += int(digit) * (10 - i)
    
    check_digit = isbn[-1]
    if check_digit == 'X':
        total += 10
    else:
        total += int(check_digit)
    
    return total % 11 == 0

def _validate_isbn13(isbn: str) -> bool:
    """Valida ISBN-13"""
    if not isbn.isdigit():
        return False
    
    total = 0
    for i, digit in enumerate(isbn[:-1]):
        multiplier = 1 if i % 2 == 0 else 3
        total += int(digit) * multiplier
    
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[-1])

# Uso de los validadores personalizados
class PaymentModel(ValidatedModel):
    card_number: str = field_validated(
        is_required(),
        custom(is_credit_card, "Invalid credit card number")
    )

class BookModel(ValidatedModel):
    title: str = field_validated(is_required())
    isbn: str = field_validated(
        custom(is_isbn, "Invalid ISBN format")
    )
```

---

## Validadores con Configuración Avanzada

### Validador Configurable para Archivos

```python
def file_extension_validator(allowed_extensions: List[str], case_sensitive: bool = False):
    """Factory para validar extensiones de archivo"""
    
    def validator(value, context=None):
        if value is None:
            return True
        
        filename = str(value)
        if '.' not in filename:
            return False
        
        extension = filename.split('.')[-1]
        
        if not case_sensitive:
            extension = extension.lower()
            allowed_extensions_lower = [ext.lower() for ext in allowed_extensions]
            return extension in allowed_extensions_lower
        else:
            return extension in allowed_extensions
    
    extensions_str = ", ".join(allowed_extensions)
    validator.__message__ = f"File must have one of these extensions: {extensions_str}"
    return validator

class DocumentModel(ValidatedModel):
    document_name: str = field_validated(is_required())
    file_path: str = field_validated(
        is_required(),
        custom(
            file_extension_validator(["pdf", "doc", "docx", "txt"]),
            "Document must be PDF, DOC, DOCX, or TXT"
        )
    )

# Uso
document = DocumentModel(
    document_name="User Manual",
    file_path="manual.pdf"
)
```

---

## Mejores Prácticas

### 1. Manejo de Errores

```python
def safe_validator(validation_func):
    """Decorator para manejar errores en validadores"""
    def wrapper(value, context=None):
        try:
            return validation_func(value, context)
        except Exception:
            return False
    return wrapper

@safe_validator
def complex_validation(value, context=None):
    # Código de validación que puede lanzar excepciones
    result = some_complex_operation(value)
    return result.is_valid()
```

### 2. Validadores Composibles

```python
def compose_validators(*validators):
    """Combina múltiples validadores en uno solo"""
    def composed_validator(value, context=None):
        return all(validator(value, context) for validator in validators)
    
    return composed_validator

# Uso
def is_valid_product_code(value, context=None):
    # Validaciones específicas del código de producto
    return True

def is_unique_product_code(value, context=None):
    # Verificar unicidad en base de datos
    return True

class ProductModel(ValidatedModel):
    product_code: str = field_validated(
        custom(
            compose_validators(is_valid_product_code, is_unique_product_code),
            "Invalid or duplicate product code"
        )
    )
```

### 3. Testing de Validadores

```python
import pytest

def test_custom_validator():
    def is_palindrome(value, context=None):
        if value is None:
            return True
        clean_value = str(value).replace(' ', '').lower()
        return clean_value == clean_value[::-1]
    
    # Tests
    assert is_palindrome("racecar") == True
    assert is_palindrome("race a car") == False
    assert is_palindrome("A man a plan a canal Panama") == False
    assert is_palindrome(None) == True

# Ejecutar: pytest test_validators.py
```

Los validadores personalizados te dan la flexibilidad completa para manejar cualquier caso de validación específico de tu aplicación, manteniendo la consistencia con el resto del sistema de validación de PyValidX.
