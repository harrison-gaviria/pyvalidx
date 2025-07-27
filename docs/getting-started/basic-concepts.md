# Basic Concepts

Understanding the core concepts of PyValidX will help you use the library effectively.

## Validators

Validators are functions that check if a value meets certain criteria. They return `True` if the value is valid, `False` otherwise.

### How Validators Work

```python
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

# Create validators
required_validator = is_required()
length_validator = min_length(5)
email_validator = is_email()

# Test validators
print(required_validator('hello', None))      # True
print(required_validator('', None))           # False
print(length_validator('hello', None))        # True
print(length_validator('hi', None))           # False
print(email_validator('test@test.com', None)) # True
print(email_validator('invalid', None))       # False
```

### Validator Properties

Every validator has a `__message__` attribute that contains the error message:

```python
from pyvalidx.core import is_required

validator = is_required('This field cannot be empty')
print(validator.__message__)  # 'This field cannot be empty'
```

### Context-Aware Validators

Some validators need access to other field values. The `context` parameter provides this:

```python
from pyvalidx.core import same_as

# This validator compares with another field
password_confirm = same_as('password', 'Passwords must match')

# When validating, context contains all field values
# context = {'password': 'secret123', 'password_confirm': 'secret123'}
```

## ValidatedModel

The `ValidatedModel` class extends Pydantic's `BaseModel` to add custom validation capabilities.

### Basic Usage

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required

class User(ValidatedModel):
    name: str = field_validated(is_required())
    email: str = field_validated(is_required())
    age: int

# Create an instance - validation happens automatically
user = User(name='John', email='john@example.com', age=25)
```

### Validation Timing

Validation occurs at three different times:

```python
# 1. Validation on creation
user = User(name='John')

# 2. Validation on assignment (if enabled)
user.name = 'Jane'  # Validates automatically

# 3. Manual validation
current_data = user.validate()  # Returns validated data
```

## field_validated

The `field_validated` function attaches validators to model fields:

```python
from pyvalidx import field_validated
from pyvalidx.core import is_required

class User(ValidatedModel):
    name: str = field_validated(is_required())
    #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #           This creates a Pydantic field with custom validators
```

### Multiple Validators

You can apply multiple validators to one field:

```python
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

email: str = field_validated(
    is_required(),
    is_email(),
    min_length(5)
)
```

### Validator Order

Validators are executed in the order you specify them. If any validator fails, the remaining validators are not executed:

```python
field_validated(
    is_required(),      # Runs first
    min_length(8),      # Runs second (if first passes)
    is_strong_password() # Runs third (if first two pass)
)
```

## ValidationException

When validation fails, PyValidX raises a `ValidationException`:

```python
from pyvalidx.exception import ValidationException

try:
    user = User(name='', email='invalid')
except ValidationException as e:
    print(e.status_code)  # 400
    print(e.validations)  # {'name': 'This field is required', ...}
    print(e.to_dict())    # Complete error structure
    print(e.to_json())    # JSON string
```

### Error Structure

The exception provides structured error information:

```python
{
    'status_code': 400,
    'validations': {
        'name': 'This field is required',
        'email': 'Invalid email format',
        'age': 'Must be a positive number'
    }
}
```

## Optional Fields and None Values

PyValidX handles `None` values gracefully:

```python
from typing import Optional

class User(ValidatedModel):
    name: str = field_validated(is_required())
    nickname: Optional[str] = field_validated(min_length(2))
    #         ^^^^^^^^^^^^^ Optional field
    bio: Optional[str] = None  # No validation
```

### How None Values Work

- **Required validators**: Fail if value is `None`
- **Other validators**: Return `True` if value is `None` (skip validation)
- **Optional fields**: Can be `None` without triggering validation errors

```python
# This works - nickname is optional
user = User(name='John', nickname=None)

# This fails - name is required
try:
    user = User()
except ValidationException as e:
    print(e.validations)  # {'name': 'This field is required'}
```

## Validation Context

The validation context contains all field values and is passed to validators that need it:

```python
from pyvalidx.core import same_as

class PasswordForm(ValidatedModel):
    password: str = field_validated(is_required())
    confirm_password: str = field_validated(
        same_as('password')  # This validator uses context
    )

# When validating confirm_password, context will be:
# {'password': 'secret123', 'confirm_password': 'secret123'}
```

## Custom Validators

You can create custom validators using the `custom` function:

```python
from pyvalidx.core import custom

def is_even(value, context=None) -> bool:
    '''
    Check if a number is even.

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True
    return value % 2 == 0

class NumberModel(ValidatedModel):
    even_number: int = field_validated(
        custom(is_even, 'Number must be even')
    )
```

### Custom Validator Requirements

Custom validators must:
1. Accept two parameters: `value` and `context`
2. Return `True` for valid values, `False` for invalid
3. Handle `None` values appropriately (usually return `True`)

## Combining Concepts

Here's how all concepts work together:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length, same_as, custom
from pyvalidx.string import is_email, is_strong_password
from typing import Optional

def is_adult(value, context=None) -> bool:
    '''
    Custom validator to check if age indicates adult.

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True
    return value >= 18

class UserRegistration(ValidatedModel):
    # Required field with multiple validators
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username too short')
    )

    # Email validation
    email: str = field_validated(
        is_required('Email is required'),
        is_email('Invalid email format')
    )

    # Password with custom and built-in validators
    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password too short'),
        is_strong_password('Password not strong enough')
    )

    # Context-aware validator
    confirm_password: str = field_validated(
        is_required('Password confirmation required'),
        same_as('password', 'Passwords must match')
    )

    # Custom validator
    age: int = field_validated(
        is_required('Age is required'),
        custom(is_adult, 'Must be 18 or older')
    )

    # Optional field
    bio: Optional[str] = field_validated(
        min_length(10, 'Bio too short')
    )

# Usage
try:
    user = UserRegistration(
        username='johndoe',
        email='john@example.com',
        password='SecurePass123!',
        confirm_password='SecurePass123!',
        age=25,
        bio='I love programming'
    )
    print('Registration successful!')
except ValidationException as e:
    print('Registration failed:')
    for field, error in e.validations.items():
        print(f'- {field}: {error}')
```

## Best Practices

1. **Start simple**: Begin with basic validators and add complexity as needed
2. **Use meaningful names**: Choose descriptive field names and error messages
3. **Order validators logically**: Put fast checks before slow ones
4. **Handle optional fields**: Use `Optional` type hints for nullable fields
5. **Test thoroughly**: Include tests for both valid and invalid data
6. **Document custom validators**: Explain what your custom validators do
7. **Keep validators focused**: Each validator should check one specific thing
