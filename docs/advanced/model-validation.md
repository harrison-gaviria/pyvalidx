# Model Validation

PyValidX provides the `ValidatedModel` class that extends Pydantic's `BaseModel` to add custom validation capabilities.

## ValidatedModel Class

The `ValidatedModel` class is the core component that enables custom field validation:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

class User(ValidatedModel):
    name: str = field_validated(is_required(), min_length(2))
    email: str = field_validated(is_required(), is_email())
    age: int
```

## Automatic Validation

Validation occurs automatically when creating model instances:

```python
# Valid instance
user = User(name='John', email='john@example.com', age=25)

# Invalid instance - raises ValidationException
try:
    invalid_user = User(name='', email='invalid-email', age=25)
except ValidationException as e:
    print(e.validations)
```

## Model Configuration

The `ValidatedModel` comes with sensible defaults:

```python
class ValidatedModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,    # Validates on field assignment
        extra='forbid',             # Prevents extra fields
        str_strip_whitespace=True,  # Strips whitespace from strings
    )
```

## Custom Model Configuration

You can override the default configuration:

```python
from pydantic import ConfigDict

class CustomUser(ValidatedModel):
    model_config = ConfigDict(
        validate_assignment=False,  # Disable assignment validation
        extra='allow',             # Allow extra fields
        str_strip_whitespace=False # Don't strip whitespace
    )

    name: str = field_validated(is_required())
    email: str = field_validated(is_email())
```

## Validation Context

Some validators need access to other field values through context:

```python
from pyvalidx.core import same_as

class PasswordChangeModel(ValidatedModel):
    current_password: str = field_validated(is_required())
    new_password: str = field_validated(is_required(), min_length(8))
    confirm_password: str = field_validated(
        same_as('new_password', 'Passwords must match')
    )

# The context automatically includes all field values
change = PasswordChangeModel(
    current_password='old123',
    new_password='newSecure456',
    confirm_password='newSecure456'
)
```

## Inheritance and Validation

Validation rules are inherited by subclasses:

```python
class BaseUser(ValidatedModel):
    name: str = field_validated(is_required(), min_length(2))
    email: str = field_validated(is_required(), is_email())

class AdminUser(BaseUser):
    # Inherits name and email validation
    admin_level: int = field_validated(is_required(), min_value(1))

class SuperUser(AdminUser):
    # Inherits all previous validations
    super_powers: list = field_validated(is_required(), is_not_empty())
```

## Optional Fields

Handle optional fields with proper type annotations:

```python
from typing import Optional

class UserProfile(ValidatedModel):
    name: str = field_validated(is_required())
    bio: Optional[str] = field_validated(max_length(500))
    website: Optional[str] = field_validated(is_url())

    # Optional fields can be None
    age: Optional[int] = None
```

## Complex Validation Scenarios

### Conditional Validation

```python
from pyvalidx.core import required_if

class OrderModel(ValidatedModel):
    payment_method: str = field_validated(
        is_required(),
        is_in(['cash', 'credit_card', 'paypal'])
    )

    card_number: Optional[str] = field_validated(
        required_if('payment_method', 'credit_card', 'Card number required for credit card payments')
    )

    paypal_email: Optional[str] = field_validated(
        required_if('payment_method', 'paypal', 'PayPal email required for PayPal payments'),
        is_email('Invalid PayPal email format')
    )
```

### Cross-Field Validation

```python
from datetime import datetime, timedelta

class EventModel(ValidatedModel):
    start_date: str = field_validated(
        is_required(),
        is_date('%Y-%m-%d'),
        is_future_date('%Y-%m-%d')
    )

    end_date: str = field_validated(
        is_required(),
        is_date('%Y-%m-%d'),
        is_future_date('%Y-%m-%d')
    )

    @model_validator(mode='after')
    def validate_date_order(self) -> 'EventModel':
        '''
        Validates that the end date is after the start date

        Returns:
            EventModel: Self instance if validation passes
        '''
        if self.start_date and self.end_date:
            start = datetime.strptime(self.start_date, '%Y-%m-%d')
            end = datetime.strptime(self.end_date, '%Y-%m-%d')
            if end <= start:
                raise ValueError('End date must be after start date')
        return self
```

## Performance Considerations

### Validator Ordering

Place faster validators first to optimize performance:

```python
class OptimizedUser(ValidatedModel):
    email: str = field_validated(
        is_required(),      # Fast check first
        min_length(5),      # Medium speed
        is_email()          # Slower regex check last
    )
```

### Caching Validation Results

For expensive validations, consider caching:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_validation(value):
    # Expensive operation here
    return True

class CachedValidationModel(ValidatedModel):
    data: str = field_validated(
        custom(expensive_validation, "Expensive validation failed")
    )
```

## Error Handling Strategies

### Collecting All Errors

```python
def validate_user_data(data: dict[str, Any]) -> dict[str, Any]:
    '''
    Validates user data and returns result

    Args:
        data (dict[str, Any]): User data to validate

    Returns:
        dict[str, Any]: Validation result
    '''
    try:
        user = User(**data)
        return {'success': True, 'user': user}
    except ValidationException as e:
        return {
            'success': False,
            'errors': e.validations,
            'status_code': e.status_code
        }
```

### Custom Error Messages

```python
class UserWithCustomMessages(ValidatedModel):
    name: str = field_validated(
        is_required('Please provide your full name'),
        min_length(2, 'Name must be at least 2 characters long')
    )

    email: str = field_validated(
        is_required('Email address is required'),
        is_email('Please provide a valid email address')
    )
```

## Testing Validated Models

```python
import pytest
from pyvalidx.exception import ValidationException

def test_valid_user() -> None:
    '''
    Test valid user creation
    '''
    user = User(name='John Doe', email='john@example.com', age=25)
    assert user.name == 'John Doe'
    assert user.email == 'john@example.com'

def test_invalid_user() -> None:
    '''
    Test invalid user creation
    '''
    with pytest.raises(ValidationException) as exc_info:
        User(name='', email='invalid-email', age=25)

    errors = exc_info.value.validations
    assert 'name' in errors
    assert 'email' in errors
```

## Best Practices

1. **Keep validators simple**: Each validator should check one thing
2. **Order validators logically**: Fast checks first, expensive checks last
3. **Use meaningful error messages**: Help users understand what went wrong
4. **Combine validators thoughtfully**: Don't over-validate
5. **Test edge cases**: Include tests for boundary conditions
6. **Document complex validations**: Explain business rules in comments
