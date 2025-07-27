# Quick Start

Get up and running with PyValidX in just a few minutes!

## Your First Validated Model

Let's create a simple user model with validation:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.string import is_email

class User(ValidatedModel):
    name: str = field_validated(is_required())
    email: str = field_validated(is_required(), is_email())
    age: int = field_validated(is_required())

# Create a valid user
user = User(
    name='John Doe',
    email='john@example.com',
    age=25
)
print(f'Created user: {user.name}')

# Try to create an invalid user
try:
    invalid_user = User(name='', email='invalid-email', age=25)
except ValidationException as e:
    print('Validation failed:')
    for field, error in e.validations.items():
        print(f'- {field}: {error}')
```

## Multiple Validators on One Field

You can apply multiple validators to a single field:

```python
from pyvalidx.core import min_length, max_length
from pyvalidx.string import is_strong_password

class SecureUser(ValidatedModel):
    username: str = field_validated(
        is_required(),
        min_length(3),
        max_length(20)
    )
    password: str = field_validated(
        is_required(),
        min_length(8),
        is_strong_password()
    )

# This will validate all conditions
secure_user = SecureUser(
    username='alice123',
    password='MySecurePass123!'
)
```

## Custom Error Messages

Customize error messages for better user experience:

```python
from pyvalidx.core import is_required

class Product(ValidatedModel):
    name: str = field_validated(
        is_required('Product name is required')
    )
    price: float = field_validated(
        is_required('Price must be specified')
    )

try:
    Product(name='', price=None)
except ValidationException as e:
    print(e.to_dict())
    # Custom messages will be shown
```

## Conditional Validation

Make fields required based on other fields:

```python
from pyvalidx.core import required_if

class Order(ValidatedModel):
    payment_method: str = field_validated(is_required())
    credit_card_number: str = field_validated(
        required_if('payment_method', 'credit_card', 
                   'Credit card number required for card payments')
    )

# Valid - no card payment
order1 = Order(payment_method='cash')

# Valid - card payment with number
order2 = Order(
    payment_method='credit_card',
    credit_card_number='4111111111111111'
)

# Invalid - card payment without number
try:
    Order(payment_method='credit_card')
except ValidationException as e:
    print('Card number required!')
```

## Working with Dates

Validate date fields easily:

```python
from pyvalidx.date import is_date, is_future_date

class Event(ValidatedModel):
    name: str = field_validated(is_required())
    start_date: str = field_validated(
        is_required(),
        is_date('%Y-%m-%d'),
        is_future_date('%Y-%m-%d', 'Event must be in the future')
    )

# Valid future event
event = Event(name='Conference', start_date='2025-12-01')
```

## Numeric Validation

Validate numbers with range constraints:

```python
from pyvalidx.numeric import is_positive, min_value, max_value

class Product(ValidatedModel):
    name: str = field_validated(is_required())
    price: float = field_validated(
        is_required(),
        is_positive('Price must be positive'),
        min_value(0.01, 'Minimum price is $0.01')
    )
    quantity: int = field_validated(
        is_required(),
        min_value(1),
        max_value(1000, 'Maximum quantity is 1000')
    )

product = Product(name='Widget', price=19.99, quantity=5)
```

## What's Next?

Now that you've seen the basics, explore more advanced features:

- [Basic Concepts](basic-concepts.md) - Understand PyValidX architecture
- [All Validators](../validators/core.md) - Complete validator reference
- [Custom Validators](../advanced/custom-validators.md) - Create your own validators
- [Real Examples](../examples/user-registration.md) - Production-ready examples
