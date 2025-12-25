# field_validated API Reference

The `field_validated` function creates Pydantic fields with custom validators attached.

## Function Definition

```python
def field_validated(
    *validators: Callable[[Any, Optional[Dict[str, Any]]], bool],
    **kwargs: Any
) -> Any:
    '''
    Creates a Pydantic field with custom validators.

    Args:
        *validators: The custom validation functions.
        **kwargs: The keyword arguments to pass to the Pydantic Field function.

    Returns:
        Any: A Pydantic field with the custom validators.
    '''
```

## Parameters

### `*validators`
- **Type:** `Callable[[Any, Optional[Dict[str, Any]]], bool]`
- **Description:** One or more validator functions to apply to the field
- **Required:** At least one validator must be provided

### `**kwargs`
- **Type:** `Any`
- **Description:** Additional keyword arguments passed to Pydantic's `Field()` function
- **Optional:** Standard Pydantic field options like `default`, `description`, `alias`, etc.

## Returns

Returns a Pydantic `Field` instance with custom validators attached through the metadata.

## Usage Examples

### Single Validator

```python
from pyvalidx import field_validated
from pyvalidx.core import is_required

class User(ValidatedModel):
    name: str = field_validated(is_required())
```

### Multiple Validators

Validators are applied in the order they are specified:

```python
from pyvalidx import field_validated
from pyvalidx.core import is_required, min_length, max_length

class User(ValidatedModel):
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        max_length(20, 'Username cannot exceed 20 characters')
    )
```

### With Pydantic Field Options

You can combine custom validators with standard Pydantic field options:

```python
from pyvalidx import field_validated
from pyvalidx.core import is_required
from pyvalidx.string import is_email

class User(ValidatedModel):
    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address'),
        description='User's email address',
        alias='email_address',
        default=None
    )

    age: int = field_validated(
        min_value(0, 'Age cannot be negative'),
        max_value(150, 'Age must be realistic'),
        description='User's age in years',
        default=18,
        ge=0,  # Pydantic constraint
        le=150  # Pydantic constraint
    )
```

### Optional Fields

Fields can be optional while still having validation when a value is provided:

```python
from typing import Optional

class User(ValidatedModel):
    name: str = field_validated(is_required())

    # Optional field with validation when provided
    website: Optional[str] = field_validated(
        matches_regex(
            r'^https?://.+',
            'Website must start with http:// or https://'
        ),
        default=None
    )

    # Optional field with multiple validators
    phone: Optional[str] = field_validated(
        is_phone('Please provide a valid phone number'),
        no_whitespace('Phone number cannot contain spaces'),
        default=None
    )
```

### Custom Default Values

```python
from datetime import datetime

class Post(ValidatedModel):
    title: str = field_validated(
        is_required('Title is required'),
        min_length(5, 'Title must be at least 5 characters')
    )

    created_at: str = field_validated(
        is_date('%Y-%m-%d %H:%M:%S', 'Invalid datetime format'),
        default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    status: str = field_validated(
        is_in(['draft', 'published', 'archived'], 'Invalid status'),
        default='draft'
    )
```

### Field Aliases

```python
class APIUser(ValidatedModel):
    full_name: str = field_validated(
        is_required('Full name is required'),
        min_length(2, 'Name must be at least 2 characters'),
        alias='name'  # JSON will use 'name' but Python uses 'full_name'
    )

    email_address: str = field_validated(
        is_required('Email is required'),
        is_email('Invalid email format'),
        alias='email'
    )

# Usage with alias
user = APIUser(**{'name': 'John Doe', 'email': 'john@example.com'})
print(user.full_name)  # 'John Doe'
print(user.email_address)  # 'john@example.com'
```

### Field Descriptions and Documentation

```python
class Product(ValidatedModel):
    name: str = field_validated(
        is_required('Product name is required'),
        min_length(3, 'Name must be at least 3 characters'),
        max_length(100, 'Name cannot exceed 100 characters'),
        description='The name of the product',
        examples=['iPhone 15', 'MacBook Pro']
    )

    price: float = field_validated(
        is_required('Price is required'),
        is_positive('Price must be positive'),
        description='Product price in USD',
        examples=[99.99, 1299.00],
        gt=0  # Additional Pydantic constraint
    )

    category: str = field_validated(
        is_required('Category is required'),
        is_in(
            ['electronics', 'clothing', 'books', 'home'],
            'Invalid category'
        ),
        description='Product category',
        examples=['electronics']
    )
```

### Complex Validation Combinations

```python
class UserRegistration(ValidatedModel):
    # Username with multiple constraints
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        max_length(20, 'Username cannot exceed 20 characters'),
        matches_regex(
            r'^[a-zA-Z0-9_]+$',
            'Username can only contain letters, numbers, and underscores'
        ),
        no_whitespace('Username cannot contain spaces')
    )

    # Email with validation
    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address'),
        max_length(255, 'Email address is too long')
    )

    # Strong password requirements
    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password(
            'Password must contain uppercase, lowercase, digit and special character'
        ),
        no_whitespace('Password cannot contain spaces')
    )

    # Password confirmation
    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('password', 'Passwords must match')
    )

    # Age with business logic
    age: int = field_validated(
        is_required('Age is required'),
        is_integer('Age must be a whole number'),
        min_value(13, 'Must be at least 13 years old'),
        max_value(120, 'Age must be realistic')
    )
```

## Validator Function Requirements

For a function to work with `field_validated`, it must:

1. **Have the correct signature:**
   ```python
   def validator(value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
   ```

2. **Return a boolean:**
   - `True` if validation passes
   - `False` if validation fails

3. **Have a `__message__` attribute:**
   ```python
   def my_validator(value, context=None):
       return some_validation_logic(value)

   my_validator.__message__ = 'Validation failed'
   ```

## Error Handling

When validation fails, the error message from the validator's `__message__` attribute is included in the `ValidationException`:

```python
try:
    user = User(name='')  # Empty name
except ValidationException as e:
    print(e.validations)
    # {'name': 'This field is required'}
```

For multiple validators on the same field, only the first failing validator's message is returned:

```python
class User(ValidatedModel):
    name: str = field_validated(
        is_required('Name is required'),        # This fails first
        min_length(3, 'Name too short')         # This won't be checked
    )

try:
    user = User(name='')
except ValidationException as e:
    print(e.validations)
    # {'name': 'Name is required'}
```

## Best Practices

1. **Order validators logically:** Place required checks before length/format checks
2. **Use descriptive messages:** Provide clear, user-friendly error messages
3. **Combine with Pydantic features:** Use aliases, defaults, and descriptions for better API design
4. **Keep validators focused:** Each validator should check one specific rule
5. **Document your fields:** Use descriptions and examples for API documentation
