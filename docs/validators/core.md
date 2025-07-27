# Core Validators

Core validators provide basic validation functionalities that are fundamental for most use cases.

## is_required

Validates that the field is not `None`, empty string, or empty list.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required

class UserModel(ValidatedModel):
    name: str = field_validated(is_required())
    email: str = field_validated(is_required('Email is mandatory'))

# Usage
try:
    user = UserModel(name='', email='john@example.com')
except ValidationException as e:
    print(e.validations)  # {'name': 'This field is required'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'This field is required'

---

## min_length

Validates that the field has at least the specified length.

```python
from pyvalidx.core import min_length

class ProductModel(ValidatedModel):
    name: str = field_validated(min_length(3))
    description: str = field_validated(min_length(10, 'Description too short'))

# Usage
product = ProductModel(
    name='iPhone',
    description='Latest smartphone model'
)
```

### Parameters
- `length` (int): Minimum required length
- `message` (str, optional): Custom error message

---

## max_length

Validates that the field has at most the specified length.

```python
from pyvalidx.core import max_length

class CommentModel(ValidatedModel):
    title: str = field_validated(max_length(100))
    content: str = field_validated(max_length(500, 'Comment too long'))

# Usage
comment = CommentModel(
    title='Great product!',
    content='I really enjoyed using this product...'
)
```

### Parameters
- `length` (int): Maximum allowed length
- `message` (str, optional): Custom error message

---

## custom

Wraps a custom validation function with a message.

```python
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
    return value % 2 == 0

class NumberModel(ValidatedModel):
    even_number: int = field_validated(
        custom(is_even, 'Number must be even')
    )

# Usage
number = NumberModel(even_number=4)  # Valid
```

### Parameters
- `validator_func`: Function that receives (value, context) and returns bool
- `message` (str): Error message if validation fails

---

## same_as

Validates that the field has the same value as another field.

```python
from pyvalidx.core import same_as

class RegistrationModel(ValidatedModel):
    password: str = field_validated(is_required())
    confirm_password: str = field_validated(
        same_as('password', 'Passwords must match')
    )

# Usage
registration = RegistrationModel(
    password='mypass123',
    confirm_password='mypass123'
)
```

### Parameters
- `other_field` (str): Name of the field to compare
- `message` (str, optional): Custom error message

---

## is_not_empty

Validates that the field is not empty (different from `is_required`).

```python
from pyvalidx.core import is_not_empty

class TagModel(ValidatedModel):
    tags: list = field_validated(is_not_empty('Tags list cannot be empty'))

# Usage
tag_model = TagModel(tags=['python', 'validation'])
```

### Parameters
- `message` (str): Error message if the field is empty

---

## required_if

Validates that the field is required if another field has a specific value.

```python
from pyvalidx.core import required_if

class OrderModel(ValidatedModel):
    payment_method: str = field_validated(is_required())
    card_number: str = field_validated(
        required_if('payment_method', 'credit_card', 'Card number required for credit card payments')
    )

# Usage
order = OrderModel(
    payment_method='credit_card',
    card_number='1234-5678-9012-3456'
)
```

### Parameters
- `other_field` (str): Field that conditions the validation
- `other_value` (Any): Value that makes this field required
- `message` (str): Custom error message

---

## Combining Validators

You can combine multiple core validators:

```python
class UserProfileModel(ValidatedModel):
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username too short'),
        max_length(20, 'Username too long')
    )
    bio: str = field_validated(
        max_length(500, 'Bio too long')
    )
    website: str = field_validated(
        required_if('bio', '', 'Website required if no bio provided')
    )
```
