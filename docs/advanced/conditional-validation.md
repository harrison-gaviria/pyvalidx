# Conditional Validation

Conditional validation allows applying validation rules based on the values of other fields or specific context conditions.

## Basic required_if

The `required_if` validator is the simplest form of conditional validation:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import required_if, is_required

class PaymentModel(ValidatedModel):
    payment_method: str = field_validated(
        is_required('Payment method is required')
    )

    # Only required if payment_method is 'credit_card'
    card_number: str = field_validated(
        required_if('payment_method', 'credit_card', 'Card number required for credit card payments')
    )

    # Only required if payment_method is 'bank_transfer'
    bank_account: str = field_validated(
        required_if('payment_method', 'bank_transfer', 'Bank account required for transfers')
    )

# Valid usage - Credit card
payment1 = PaymentModel(
    payment_method='credit_card',
    card_number='1234-5678-9012-3456'
)

# Valid usage - Bank transfer
payment2 = PaymentModel(
    payment_method='bank_transfer',
    bank_account='123456789'
)

# Valid usage - Cash (no additional fields required)
payment3 = PaymentModel(payment_method='cash')
```

---

## Custom Conditional Validation

### Multiple Conditions

```python
from pyvalidx.core import custom

def required_if_multiple(conditions: dict, message: str):
    '''Validator that requires field if multiple conditions are met'''
    def validator(value, context=None):
        if context is None:
            return True

        # Check if all conditions are met
        all_conditions_met = all(
            context.get(field) == expected_value
            for field, expected_value in conditions.items()
        )

        if all_conditions_met:
            return value is not None and str(value).strip() != ''
        return True

    validator.__message__ = message
    return validator

class ShippingModel(ValidatedModel):
    country: str = field_validated(is_required())
    shipping_method: str = field_validated(is_required())

    # Only required if country='US' AND shipping_method='express'
    signature_required: bool = field_validated(
        custom(
            required_if_multiple(
                {'country': 'US', 'shipping_method': 'express'},
                'Signature is required for express shipping in US'
            )
        )
    )

# Usage
shipping = ShippingModel(
    country='US',
    shipping_method='express',
    signature_required=True
)
```

### Conditional Format Validation

```python
def conditional_format_validator(condition_field: str, condition_value: str, pattern: str, message: str) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Validates format only when condition is met

    Args:
        condition_field (str): Field to check for condition
        condition_value (str): Value that makes format validation active
        pattern (str): Regex pattern to validate against
        message (str): Error message if validation fails

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Validator function
    '''
    def validator(value, context=None):
        if context is None or value is None:
            return True

        if context.get(condition_field) == condition_value:
            import re
            return bool(re.match(pattern, str(value)))
        return True

    validator.__message__ = message
    return validator

class ContactModel(ValidatedModel):
    contact_type: str = field_validated(is_required())
    contact_value: str = field_validated(is_required())

    # Validate email format only if contact_type is "email"
    formatted_contact: str = field_validated(
        custom(
            conditional_format_validator(
                'contact_type',
                'email',
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'Invalid email format'
            )
        )
    )

# Usage
contact = ContactModel(
    contact_type='email',
    contact_value='user@example.com',
    formatted_contact='user@example.com'
)
```

---

## Conditional Validation with Business Logic

### Discount System

```python
def discount_validation(value, context=None) -> bool:
    '''
    Validates discount based on customer type and order amount

    Args:
        value (Any): Discount value to validate
        context (Dict[str, Any], optional): Context containing customer_type and order_amount

    Returns:
        bool: True if discount is valid, False otherwise
    '''
    if value is None or context is None:
        return True

    customer_type = context.get('customer_type')
    order_amount = context.get('order_amount', 0)
    discount = float(value)

    # Business rules for discounts
    if customer_type == 'regular':
        max_discount = 10 if order_amount >= 100 else 5
    elif customer_type == 'premium':
        max_discount = 20 if order_amount >= 100 else 15
    elif customer_type == 'vip':
        max_discount = 30
    elif customer_type == 'employee':
        max_discount = 50
    else:
        return False

    return 0 <= discount <= max_discount

discount_validation.__message__ = 'Invalid discount for customer type or order amount'

class OrderModel(ValidatedModel):
    customer_type: str = field_validated(
        is_required(),
        is_in(['regular', 'premium', 'vip', 'employee'])
    )

    order_amount: float = field_validated(
        is_required(),
        is_positive()
    )

    discount_percentage: float = field_validated(
        custom(discount_validation, 'Invalid discount for customer type or order amount')
    )

# Valid usage
order = OrderModel(
    customer_type='premium',
    order_amount=150.0,
    discount_percentage=18.0
)

# Invalid usage - discount too high for regular customer
try:
    invalid_order = OrderModel(
        customer_type='regular',
        order_amount=50.0,
        discount_percentage=25.0
    )
except ValidationException as e:
    print(e.validations)
```

---

## Advanced Conditional Validation Patterns

### Cascade Validation

```python
def conditional_requirement(condition_func: Callable[[Dict[str, Any]], bool], message: str) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Generic conditional requirement validator

    Args:
        condition_func (Callable[[Dict[str, Any]], bool]): Function that takes context and returns True if condition is met
        message (str): Error message if validation fails

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Validator function
    '''
    def validator(value, context=None):
        if condition_func(context):
            return value is not None and str(value).strip() != ''
        return True

    validator.__message__ = message
    return validator

class EmployeeModel(ValidatedModel):
    employee_type: str = field_validated(
        is_required(),
        is_in(['full_time', 'part_time', 'contractor', 'intern'])
    )

    # Only for full-time and part-time employees
    benefits_eligible: bool = field_validated(
        custom(
            required_if_multiple(
                {'employee_type': 'full_time'},
                'Benefits eligibility required for full-time employees'
            )
        )
    )

    # Only if eligible for benefits
    health_plan: str = field_validated(
        custom(
            conditional_requirement(
                lambda ctx: ctx.get('benefits_eligible') == True,
                'Health plan selection required for benefits-eligible employees'
            )
        )
    )
```

### At Least One Required

```python
def at_least_one_required(fields: list, message: str) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Validates that at least one of the specified fields has a value

    Args:
        fields (list): List of field names to check
        message (str): Error message if validation fails

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Validator function
    '''
    def validator(value, context=None):
        if context is None:
            return True

        # Check if at least one field has a value
        has_value = any(
            context.get(field) is not None and str(context.get(field)).strip() != ''
            for field in fields
        )

        return has_value

    validator.__message__ = message
    return validator

class ContactFormModel(ValidatedModel):
    name: str = field_validated(is_required())

    # At least one of these must be present
    email: str = field_validated(
        custom(
            at_least_one_required(['email', 'phone'], 'Either email or phone is required')
        ),
        is_email()
    )

    phone: str = field_validated(
        custom(
            at_least_one_required(['email', 'phone'], 'Either email or phone is required')
        ),
        is_phone()
    )

# Valid usage - email only
contact1 = ContactFormModel(
    name='John Doe',
    email='john@example.com'
)

# Valid usage - phone only
contact2 = ContactFormModel(
    name='Jane Doe',
    phone='3001234567'
)

# Valid usage - both
contact3 = ContactFormModel(
    name='Bob Smith',
    email='bob@example.com',
    phone='3009876543'
)
```

### Debug and Development Tools

```python
def debug_conditional_validator(validator_func: Callable[[Any, Optional[Dict[str, Any]]], bool], debug_name: str) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Wrapper that adds debug information to conditional validators

    Args:
        validator_func (Callable[[Any, Optional[Dict[str, Any]]], bool]): Validator function to wrap
        debug_name (str): Name for debugging purposes

    Returns:
        Callable[[Any, Optional[Dict[str, Any]]], bool]: Wrapped validator function
    '''
    def wrapper(value, context=None):
        import time
        start_time = time.time()

        try:
            result = validator_func(value, context)
            end_time = time.time()

            if hasattr(wrapper, '__debug_mode__') and wrapper.__debug_mode__:
                print(f'[DEBUG] {debug_name}: {result} (took {(end_time - start_time)*1000:.2f}ms)')

            return result
        except Exception as e:
            end_time = time.time()
            debug_info = {
                'validator_name': debug_name,
                'validation_time_ms': round((end_time - start_time) * 1000, 2),
                'exception': str(e),
                'input_value': str(value)[:100],
                'context': str(context)[:200] if context else None
            }
            wrapper.__debug_info__ = debug_info
            return False

    wrapper.__message__ = getattr(validator_func, '__message__', 'Validation failed')
    return wrapper

# Usage in development
class DebugModel(ValidatedModel):
    field1: str = field_validated(is_required())
    field2: str = field_validated(
        custom(
            debug_conditional_validator(
                required_if('field1', 'special_value'),
                'required_if_debug'
            )
        )
    )
```

### Systematic Testing

```python
import pytest

def test_conditional_validation() -> None:
    '''
    Comprehensive test for conditional validation

    1. Condition not met, field optional
    2. Condition met, required field present
    3. Condition met, required field missing
    '''

    # Case 1: Condition not met, field optional
    model1 = PaymentModel(payment_method='cash')
    assert model1.payment_method == 'cash'

    # Case 2: Condition met, required field present
    model2 = PaymentModel(
        payment_method='credit_card',
        card_number='1234-5678-9012-3456'
    )
    assert model2.card_number is not None

    # Case 3: Condition met, required field missing
    with pytest.raises(ValidationException) as exc_info:
        PaymentModel(payment_method='credit_card')

    assert 'card_number' in exc_info.value.validations

# Run: pytest test_conditional.py -v
```

Conditional validation is a powerful tool that allows creating complex and flexible business rules, adapting to different scenarios based on data context.
