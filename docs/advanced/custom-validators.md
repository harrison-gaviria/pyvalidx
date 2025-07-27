# Custom Validators

PyValidX allows creating custom validators for specific use cases that are not covered by predefined validators.

## Creating Custom Validators

### Basic Validation Function

A custom validator is a function that:
- Receives two parameters: `value` and `context` (optional)
- Returns `True` if validation is successful, `False` if it fails
- Has a `__message__` attribute with the error message

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import custom

def is_even(value, context=None) -> bool:
    '''
    Validates that the number is even

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True
    try:
        return int(value) % 2 == 0
    except (ValueError, TypeError):
        return False

# Add error message
is_even.__message__ = 'Number must be even'

class NumberModel(ValidatedModel):
    even_number: int = field_validated(
        custom(is_even, 'Number must be even')
    )

# Usage
valid_model = NumberModel(even_number=4)  # Valid
# invalid_model = NumberModel(even_number=3)  # Raises ValidationException
```

### Validador como Función Factory

Para validadores más flexibles, crea una función que retorne el validador:

```python
def min_words(word_count: int, message: str = None) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Factory para validar cantidad mínima de palabras

    Args:
        word_count (int): Minimum number of words
        message (str, optional): Error message if validation fails

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Validator function
    '''
    message = message or f'Must contain at least {word_count} words'

    def validator(value, context=None):
        if value is None:
            return True
        word_list = str(value).strip().split()
        return len(word_list) >= word_count

    validator.__message__ = message
    return validator

class ArticleModel(ValidatedModel):
    title: str = field_validated(min_words(2, 'Title must have at least 2 words'))
    content: str = field_validated(min_words(10, 'Content must have at least 10 words'))

# Uso
article = ArticleModel(
    title='Python Validation Guide',
    content='This is a comprehensive guide about creating custom validators in Python...'
)
```

---

## Contextual Validators

Validators can access other model fields through the `context` parameter:

```python
def password_not_contains_username(value, context=None) -> bool:
    '''
    Validates that password does not contain username

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None or context is None:
        return True

    username = context.get('username', '').lower()
    password = str(value).lower()

    return username not in password

class UserRegistrationModel(ValidatedModel):
    username: str = field_validated(is_required())
    password: str = field_validated(
        is_required(),
        custom(password_not_contains_username, 'Password cannot contain username')
    )

# Valid usage
user = UserRegistrationModel(
    username='johndoe',
    password='SecurePass123!'
)

# Invalid usage
try:
    invalid_user = UserRegistrationModel(
        username='johndoe',
        password='johndoe123'
    )
except ValidationException as e:
    print(e.validations)  # {'password': 'Password cannot contain username'}
```

---

## Complex Validation Examples

### Credit Card and ISBN Validators

```python
def is_credit_card(value, context=None) -> bool:
    '''
    Validates credit card number using Luhn algorithm

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True

    # Remove spaces and hyphens
    card_number = str(value).replace(' ', '').replace('-', '')

    # Check if all digits
    if not card_number.isdigit():
        return False

    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10

    return luhn_checksum(card_number) == 0

def is_isbn(value, context=None) -> bool:
    '''
    Validates ISBN-10 or ISBN-13

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True

    isbn = str(value).replace('-', '').replace(' ', '')

    if len(isbn) == 10:
        return _validate_isbn10(isbn)
    elif len(isbn) == 13:
        return _validate_isbn13(isbn)
    else:
        return False

def _validate_isbn10(isbn: str) -> bool:
    '''
    Validates ISBN-10

    Args:
        isbn (str): ISBN-10 number

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if not (isbn[:-1].isdigit() and (isbn[-1].isdigit() or isbn[-1].upper() == 'X')):
        return False

    total = 0
    for i, digit in enumerate(isbn[:-1]):
        total += int(digit) * (10 - i)

    check_digit = isbn[-1]
    if check_digit.upper() == 'X':
        total += 10
    else:
        total += int(check_digit)

    return total % 11 == 0

def _validate_isbn13(isbn: str) -> bool:
    """Validates ISBN-13"""
    if not isbn.isdigit():
        return False

    total = 0
    for i, digit in enumerate(isbn[:-1]):
        multiplier = 1 if i % 2 == 0 else 3
        total += int(digit) * multiplier

    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[-1])

# Usage of custom validators
class PaymentModel(ValidatedModel):
    card_number: str = field_validated(
        is_required(),
        custom(is_credit_card, 'Invalid credit card number')
    )

class BookModel(ValidatedModel):
    title: str = field_validated(is_required())
    isbn: str = field_validated(
        custom(is_isbn, 'Invalid ISBN format')
    )
```

---

## Validators with External Dependencies

### Database Validation

```python
def username_not_exists(value, context=None) -> bool:
    '''
    Validates that username does not exist in database
    
    
    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True

    # Database query simulation
    existing_usernames = ['admin', 'root', 'test', 'demo']  # In practice, this would come from DB

    return str(value).lower() not in existing_usernames

class NewUserModel(ValidatedModel):
    username: str = field_validated(
        is_required(),
        min_length(3),
        custom(username_not_exists, 'Username already exists')
    )
    email: str = field_validated(is_required(), is_email())
```

### External API Validation

```python
def is_valid_country_code(value, context=None) -> bool:
    '''
    Validates country code using a predefined list
    
    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True

    # ISO 3166-1 alpha-2 codes list (simulated)
    valid_codes = {
        'US', 'CA', 'GB', 'FR', 'DE', 'IT', 'ES', 'BR', 'AR', 'CO',
        'MX', 'JP', 'CN', 'IN', 'AU', 'NZ', 'ZA', 'EG', 'NG', 'KE'
    }

    return str(value).upper() in valid_codes

class InternationalOrderModel(ValidatedModel):
    customer_name: str = field_validated(is_required())
    country_code: str = field_validated(
        is_required(),
        custom(is_valid_country_code, 'Invalid country code')
    )
```

---

## Validators with Advanced Configuration

### Configurable File Validator

```python
def file_extension_validator(allowed_extensions: list) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Creates a validator for file extensions
    
    Args:
        allowed_extensions (list): List of allowed file extensions

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Validator function
    '''
    def validator(value, context=None):
        if value is None:
            return True

        file_path = str(value)
        if '.' not in file_path:
            return False

        extension = file_path.split('.')[-1].lower()
        return extension in [ext.lower() for ext in allowed_extensions]

    validator.__message__ = f"File must have one of these extensions: {', '.join(allowed_extensions)}"
    return validator

class DocumentModel(ValidatedModel):
    document_name: str = field_validated(is_required())
    file_path: str = field_validated(
        is_required(),
        custom(
            file_extension_validator(['pdf', 'doc', 'docx', 'txt']),
            'Document must be PDF, DOC, DOCX, or TXT'
        )
    )

# Usage
document = DocumentModel(
    document_name='User Manual',
    file_path='manual.pdf'
)
```

---

## Best Practices

### 1. Error Handling

```python
def safe_validator(validation_func) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Decorator to handle errors in validators
    
    Args:
        validation_func (Callable[[Any, Optional[Dict[str, Any]]], bool]): Validator function

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Wrapped validator function
    '''
    def wrapper(value, context=None):
        try:
            return validation_func(value, context)
        except Exception:
            return False
    return wrapper

@safe_validator
def complex_validation(value, context=None):
    # Validation code that might throw exceptions
    result = some_complex_operation(value)
    return result.is_valid()
```

### 2. Composable Validators

```python
def compose_validators(*validators) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Combines multiple validators into one
    
    Args:
        *validators (Callable[[Any, Optional[Dict[str, Any]]], bool]): Validator functions

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Composed validator function
    '''
    def composed_validator(value, context=None):
        return all(validator(value, context) for validator in validators)

    return composed_validator

# Usage
def is_valid_product_code(value, context=None):
    # Specific product code validations
    return True

def is_unique_product_code(value, context=None):
    # Check uniqueness in database
    return True

class ProductModel(ValidatedModel):
    product_code: str = field_validated(
        custom(
            compose_validators(is_valid_product_code, is_unique_product_code),
            'Invalid or duplicate product code'
        )
    )
```

### 3. Testing Validators

```python
import pytest

def test_custom_validator():
    def is_palindrome(value, context=None):
        if value is None:
            return True
        clean_value = str(value).replace(' ', '').lower()
        return clean_value == clean_value[::-1]

    # Tests
    assert is_palindrome('racecar') == True
    assert is_palindrome('race a car') == False
    assert is_palindrome('A man a plan a canal Panama') == False
    assert is_palindrome(None) == True

def test_validator_with_model():
    class TestModel(ValidatedModel):
        palindrome_text: str = field_validated(
            custom(is_palindrome, 'Text must be a palindrome')
        )

    # Valid case
    model = TestModel(palindrome_text='racecar')
    assert model.palindrome_text == 'racecar'

    # Invalid case
    with pytest.raises(ValidationException):
        TestModel(palindrome_text='not a palindrome')

# Run: pytest test_custom_validators.py -v
```

### 4. Performance Optimization

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_validation(value) -> bool:
    '''
    Cached expensive validation

    Args:
        value (Any): Value to validate

    Returns:
        bool: True if validation passes, False otherwise
    '''
    # Expensive operation here
    import time
    time.sleep(0.1)  # Simulate expensive operation
    return len(str(value)) > 5

class OptimizedModel(ValidatedModel):
    data: str = field_validated(
        custom(expensive_validation, 'Data validation failed')
    )
```

Custom validators provide the flexibility to implement any validation logic specific to your business requirements while maintaining consistency with PyValidX's validation framework.
