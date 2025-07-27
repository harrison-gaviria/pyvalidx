# Basic Concepts

Understanding PyValidX's core concepts will help you use the library effectively.

## Validators

A validator is a function that checks if a value meets certain criteria. Validators in PyValidX follow a specific pattern:

```python
def validator_function(value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
    # Validation logic here
    return True  # if valid, False if invalid
```

### Validator Properties

Every validator has a `__message__` attribute that contains the error message:

```python
from pyvalidx.core import is_required

validator = is_required("This field cannot be empty")
print(validator.__message__)  # "This field cannot be empty"
```

### Context-Aware Validators

Some validators need access to other field values. The `context` parameter provides this:

```python
from pyvalidx.core import same_as

# This validator compares with another field
password_confirm = same_as("password", "Passwords must match")

# When validating, context contains all field values
# context = {"password": "secret123", "password_confirm": "secret123"}
```

## ValidatedModel

`ValidatedModel` is the base class for models with custom validation. It extends Pydantic's `BaseModel`:

```python
from pyvalidx import ValidatedModel

class MyModel(ValidatedModel):
    # Your fields with validation here
    pass
```

### Key Features

1. **Automatic Validation**: Runs custom validators on initialization
2. **Error Handling**: Raises `ValidationException` with structured errors
3. **Pydantic Integration**: All Pydantic features work normally
4. **Type Safety**: Full type annotation support

### Model Configuration

`ValidatedModel` comes with sensible defaults:

```python
model_config = ConfigDict(
    validate_assignment=True,  # Validate on assignment
    extra='forbid',           # Forbid extra fields
    str_strip_whitespace=True # Strip whitespace from strings
)
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
    user = User(name="", email="invalid")
except ValidationException as e:
    print(e.status_code)  # 400
    print(e.validations)  # {"name": "This field is required", ...}
    print(e.to_dict())    # Complete error structure
    print(e.to_json())    # JSON string
```

### Error Structure

The exception contains structured error information:

```python
{
    "status_code": 400,
    "validations": {
        "field_name": "Error message",
        "another_field": ["Error 1", "Error 2"]  # Multiple errors
    }
}
```

## Validation Lifecycle

Understanding when validation occurs:

1. **Model Creation**: All validators run when creating an instance
2. **Assignment**: If `validate_assignment=True`, validators run on field updates
3. **Manual Validation**: Call `model.validate()` to re-run validation

```python
class User(ValidatedModel):
    name: str = field_validated(is_required())

# 1. Validation on creation
user = User(name="John")

# 2. Validation on assignment (if enabled)
user.name = "Jane"  # Validates automatically

# 3. Manual validation
current_data = user.validate()  # Returns validated data
```

## Optional Fields and None Values

PyValidX handles `None` values gracefully:

```python
from typing import Optional

class User(ValidatedModel):
    name: str = field_validated(is_required())
    nickname: Optional[str] = field_validated(min_length(2))
    #         ^^^^^^^^^^^^^ Optional field

# If nickname is None, min_length validator passes
user = User(name="John", nickname=None)  # Valid

# But if nickname has a value, it must be valid
user = User(name="John", nickname="A")   # Invalid - too short
```

**Key Rule**: Most validators return `True` for `None` values, making them effectively optional unless you use `is_required()`.

## Custom Validators

You can create custom validators using the `custom()` function:

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
```

## Best Practices

1. **Order Matters**: Put `is_required()` first if the field is mandatory
2. **Custom Messages**: Provide user-friendly error messages
3. **None Handling**: Most validators allow `None` by default
4. **Context Usage**: Use context for cross-field validation
5. **Validator Composition**: Combine simple validators for complex rules

## Next Steps

Now that you understand the concepts:

- [Core Validators](../validators/core.md) - Explore built-in validators
- [Custom Validators](../advanced/custom-validators.md) - Create your own
- [Error Handling](../advanced/error-handling.md) - Advanced error management
