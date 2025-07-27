# ValidatedModel API Reference

The `ValidatedModel` class is the core component of PyValidX that extends Pydantic's `BaseModel` to support custom field validation.

## Class Definition

```python
class ValidatedModel(BaseModel):
    '''
    Model for validation.

    Args:
        **data (Any): The data to validate.

    Raises:
        ValidationException: If the validation fails.
    '''
```

## Configuration

The model comes with the following default configuration:

```python
model_config = ConfigDict(
    validate_assignment=True,    # Validates data when fields are assigned
    extra='forbid',             # Prevents extra fields not defined in the model
    str_strip_whitespace=True,  # Automatically strips whitespace from strings
)
```

### Configuration Options

#### `validate_assignment: bool`

When `True`, validates field values when they are assigned after model creation.

**Default:** `True`

**Example:**
```python
user = User(name='John', email='john@example.com')
user.email = 'invalid-email'  # Raises ValidationException
```

#### `extra: str`

Controls how extra fields (not defined in the model) are handled.

**Options:**
- `'forbid'`: Raises an error if extra fields are provided
- `'allow'`: Allows extra fields
- `'ignore'`: Ignores extra fields silently

**Default:** `'forbid'`

#### `str_strip_whitespace: bool`

When `True`, automatically strips leading and trailing whitespace from string fields.

**Default:** `True`

**Example:**
```python
user = User(name='  John  ')  # Becomes 'John'
```

## Methods

### `__init__(**data) -> None`

Creates a new instance of the validated model.

**Parameters:**
- `**data`: Keyword arguments representing field values

**Raises:**
- `ValidationException`: If any field validation fails

**Example:**
```python
user = User(name='John Doe', email='john@example.com', age=25)
```

### `dict() -> Dict[str, Any]`

Returns the model as a dictionary (inherited from Pydantic).

**Returns:**
- `Dict[str, Any]`: Dictionary representation of the model

**Example:**
```python
user = User(name='John', email='john@example.com')
user_dict = user.dict()
# {'name': 'John', 'email': 'john@example.com'}
```

### `json() -> str`

Returns the model as a JSON string (inherited from Pydantic).

**Returns:**
- `str`: JSON representation of the model

**Example:**
```python
user = User(name='John', email='john@example.com')
user_json = user.json()
# '{'name': 'John', 'email': 'john@example.com'}'
```

### `copy() -> 'ValidatedModel'`

Creates a copy of the model (inherited from Pydantic).

**Returns:**
- `ValidatedModel`: A new instance with the same field values

**Example:**
```python
user = User(name='John', email='john@example.com')
user_copy = user.copy()
```

## Class Methods

### `parse_obj(obj: Dict[str, Any]) -> 'ValidatedModel'`

Creates a model instance from a dictionary (inherited from Pydantic).

**Parameters:**
- `obj`: Dictionary containing field values

**Returns:**
- `ValidatedModel`: New model instance

**Raises:**
- `ValidationException`: If validation fails

**Example:**
```python
user_data = {'name': 'John', 'email': 'john@example.com'}
user = User.parse_obj(user_data)
```

### `parse_raw(data: str) -> 'ValidatedModel'`

Creates a model instance from a JSON string (inherited from Pydantic).

**Parameters:**
- `data`: JSON string containing field values

**Returns:**
- `ValidatedModel`: New model instance

**Raises:**
- `ValidationException`: If validation fails

**Example:**
```python
json_data = '{'name': 'John', 'email': 'john@example.com'}'
user = User.parse_raw(json_data)
```

## Usage Examples

### Basic Model Definition

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

class User(ValidatedModel):
    name: str = field_validated(is_required(), min_length(2))
    email: str = field_validated(is_required(), is_email())
    age: int
    bio: str = None  # Optional field without validation
```

### Custom Configuration

```python
from pydantic import ConfigDict

class FlexibleUser(ValidatedModel):
    model_config = ConfigDict(
        validate_assignment=False,  # Don't validate on assignment
        extra='allow',             # Allow extra fields
        str_strip_whitespace=False # Don't strip whitespace
    )

    name: str = field_validated(is_required())
    email: str = field_validated(is_email())
```

### Inheritance

```python
class BaseUser(ValidatedModel):
    name: str = field_validated(is_required(), min_length(2))
    email: str = field_validated(is_required(), is_email())

class AdminUser(BaseUser):
    admin_level: int = field_validated(is_required(), min_value(1))
    permissions: list = field_validated(is_required(), is_not_empty())

class SuperUser(AdminUser):
    super_powers: list = field_validated(is_required())
```

### Optional Fields

```python
from typing import Optional

class UserProfile(ValidatedModel):
    # Required fields
    username: str = field_validated(is_required(), min_length(3))
    email: str = field_validated(is_required(), is_email())

    # Optional fields with validation
    bio: Optional[str] = field_validated(max_length(500))
    website: Optional[str] = field_validated(is_url())

    # Optional fields without validation
    avatar_url: Optional[str] = None
    last_login: Optional[str] = None
```

### Complex Validation

```python
from pyvalidx.core import same_as, required_if
from pyvalidx.string import is_strong_password

class RegistrationModel(ValidatedModel):
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        max_length(20, 'Username must be at most 20 characters')
    )

    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address')
    )

    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password('Password is not strong enough')
    )

    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('password', 'Passwords must match')
    )

    terms_accepted: bool = field_validated(
        is_required('You must accept the terms'),
        custom(lambda x, _: x is True, 'Terms must be accepted')
    )
```

### Model with Custom Validators

```python
from pyvalidx.core import custom

def validate_age_range(value, context=None) -> bool:
    '''
    Custom validator for age range.

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True
    return 13 <= value <= 120

def validate_username_format(value, context=None) -> bool:
    '''
    Custom validator for username format.

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True
    import re
    return re.match(r'^[a-zA-Z0-9_]+$', value) is not None

class CustomUser(ValidatedModel):
    username: str = field_validated(
        is_required(),
        custom(validate_username_format, 'Username can only contain letters, numbers, and underscores')
    )

    age: int = field_validated(
        is_required(),
        custom(validate_age_range, 'Age must be between 13 and 120')
    )
```

### Error Handling

```python
from pyvalidx.exception import ValidationException

def create_user_safely(user_data: dict[str, Any]) -> dict[str, Any]:
    '''
    Safely create a user with proper error handling.

    Args:
        user_data (dict[str, Any]): User data to create

    Returns:
        dict[str, Any]: Result of the operation
    '''
    try:
        user = User(**user_data)
        return {'success': True, 'user': user}
    except ValidationException as e:
        return {
            'success': False,
            'errors': e.validations,
            'status_code': e.status_code
        }

# Usage
result = create_user_safely({
    'name': '',
    'email': 'invalid-email'
})

if not result['success']:
    print('Validation failed:')
    for field, error in result['errors'].items():
        print(f'- {field}: {error}')
```

### Testing Models

```python
import pytest

def test_valid_user_creation() -> None:
    '''
    Test creating a valid user.

    Returns:
        None
    '''
    user = User(
        name='John Doe',
        email='john@example.com',
        age=25
    )
    assert user.name == 'John Doe'
    assert user.email == 'john@example.com'
    assert user.age == 25

def test_invalid_user_creation() -> None:
    '''
    Test validation errors on invalid data.

    Returns:
        None
    '''
    with pytest.raises(ValidationException) as exc_info:
        User(name='', email='invalid-email', age=-5)

    errors = exc_info.value.validations
    assert 'name' in errors
    assert 'email' in errors

def test_user_serialization() -> None:
    '''
    Test model serialization methods.

    Returns:
        None
    '''
    user = User(name='John', email='john@example.com', age=25)

    # Test dict conversion
    user_dict = user.dict()
    assert isinstance(user_dict, dict)
    assert user_dict['name'] == 'John'

    # Test JSON conversion
    user_json = user.json()
    assert isinstance(user_json, str)
    assert 'John' in user_json
```

## Best Practices

1. **Use type hints**: Always provide proper type annotations for fields
2. **Validate required fields**: Use `is_required()` for mandatory fields
3. **Order validators logically**: Place fast validators before slow ones
4. **Provide meaningful error messages**: Help users understand validation failures
5. **Test thoroughly**: Include tests for both valid and invalid data
6. **Document complex models**: Add docstrings for business logic
7. **Use inheritance wisely**: Share common validation rules through base classes
8. **Handle optional fields properly**: Use `Optional` type hints and consider None values
