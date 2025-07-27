# Conditional Validation

La validación condicional permite aplicar reglas de validación basadas en los valores de otros campos o condiciones específicas del contexto.

## required_if Básico

El validador `required_if` es la forma más simple de validación condicional:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import required_if, is_required

class PaymentModel(ValidatedModel):
    payment_method: str = field_validated(
        is_required("Payment method is required")
    )
    
    # Solo requerido si payment_method es "credit_card"
    card_number: str = field_validated(
        required_if("payment_method", "credit_card", "Card number required for credit card payments")
    )
    
    # Solo requerido si payment_method es "bank_transfer"
    bank_account: str = field_validated(
        required_if("payment_method", "bank_transfer", "Bank account required for transfers")
    )

# Uso válido - Tarjeta de crédito
payment1 = PaymentModel(
    payment_method="credit_card",
    card_number="1234-5678-9012-3456"
)

# Uso válido - Transferencia bancaria
payment2 = PaymentModel(
    payment_method="bank_transfer",
    bank_account="123456789"
)

# Uso válido - Efectivo (no requiere campos adicionales)
payment3 = PaymentModel(payment_method="cash")
```

---

## Validación Condicional Personalizada

### Múltiples Condiciones

```python
from pyvalidx.core import custom

def required_if_multiple(field_conditions: dict, message: str = "Field is required"):
    """
    Validador que requiere el campo si múltiples condiciones se cumplen
    field_conditions: dict con formato {"field_name": "expected_value"}
    """
    def validator(value, context=None):
        if context is None:
            return True
        
        # Verificar si todas las condiciones se cumplen
        conditions_met = all(
            context.get(field) == expected_value 
            for field, expected_value in field_conditions.items()
        )
        
        if conditions_met:
            # Si las condiciones se cumplen, el campo es requerido
            return value is not None and value != ''
        
        # Si las condiciones no se cumplen, el campo es opcional
        return True
    
    validator.__message__ = message
    return validator

class ShippingModel(ValidatedModel):
    country: str = field_validated(is_required())
    shipping_method: str = field_validated(is_required())
    
    # Solo requerido si country="US" Y shipping_method="express"
    signature_required: bool = field_validated(
        custom(
            required_if_multiple(
                {"country": "US", "shipping_method": "express"},
                "Signature is required for express shipping in US"
            )
        )
    )

# Uso
shipping = ShippingModel(
    country="US",
    shipping_method="express",
    signature_required=True
)
```

### Validación Basada en Rangos

```python
def required_if_range(field_name: str, min_val, max_val, message: str = "Field is required"):
    """Requiere el campo si otro campo está en un rango específico"""
    def validator(value, context=None):
        if context is None:
            return True
        
        other_value = context.get(field_name)
        if other_value is None:
            return True
        
        try:
            other_numeric = float(other_value)
            if min_val <= other_numeric <= max_val:
                return value is not None and value != ''
            return True
        except (ValueError, TypeError):
            return True
    
    validator.__message__ = message
    return validator

class InsuranceModel(ValidatedModel):
    age: int = field_validated(is_required())
    coverage_type: str = field_validated(is_required())
    
    # Solo requerido si la edad está entre 65 y 100 años
    medical_certificate: str = field_validated(
        custom(
            required_if_range("age", 65, 100, "Medical certificate required for seniors"),
        )
    )

# Uso
insurance = InsuranceModel(
    age=70,
    coverage_type="comprehensive",
    medical_certificate="cert_123456.pdf"
)
```

---

## Validación Condicional Compleja

### Validación Basada en Listas

```python
def required_if_contains(field_name: str, search_values: list, message: str = "Field is required"):
    """Requiere el campo si otro campo (lista) contiene alguno de los valores especificados"""
    def validator(value, context=None):
        if context is None:
            return True
        
        other_value = context.get(field_name, [])
        if not isinstance(other_value, list):
            return True
        
        # Si la lista contiene alguno de los valores buscados, el campo es requerido
        if any(item in other_value for item in search_values):
            return value is not None and value != ''
        
        return True
    
    validator.__message__ = message
    return validator

class EventModel(ValidatedModel):
    event_type: str = field_validated(is_required())
    features: list = field_validated(is_required())
    
    # Solo requerido si features contiene "catering" o "bar"
    catering_details: str = field_validated(
        custom(
            required_if_contains("features", ["catering", "bar"], "Catering details required"),
        )
    )

# Uso
event = EventModel(
    event_type="wedding",
    features=["music", "catering", "photography"],
    catering_details="Vegetarian menu for 100 guests"
)
```

### Validación Jerárquica

```python
def conditional_format_validator(condition_field: str, condition_value, format_pattern: str, message: str):
    """Valida formato solo si se cumple una condición"""
    import re
    
    def validator(value, context=None):
        if context is None or value is None:
            return True
        
        # Si la condición no se cumple, no validar formato
        if context.get(condition_field) != condition_value:
            return True
        
        # Si la condición se cumple, validar formato
        return re.match(format_pattern, str(value)) is not None
    
    validator.__message__ = message
    return validator

class ContactModel(ValidatedModel):
    contact_type: str = field_validated(is_required())
    contact_value: str = field_validated(is_required())
    
    # Validar formato de email solo si contact_type es "email"
    formatted_contact: str = field_validated(
        custom(
            conditional_format_validator(
                "contact_type", 
                "email", 
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,},
                "Invalid email format"
            )
        )
    )

# Uso
contact = ContactModel(
    contact_type="email",
    contact_value="user@example.com",
    formatted_contact="user@example.com"
)
```

---

## Validación Condicional con Lógica de Negocio

### Sistema de Descuentos

```python
def discount_validation(value, context=None):
    """Valida descuentos basado en reglas de negocio"""
    if value is None or context is None:
        return True
    
    customer_type = context.get('customer_type')
    order_amount = context.get('order_amount', 0)
    discount = float(value)
    
    # Reglas de descuento por tipo de cliente
    max_discounts = {
        'regular': 10,      # 10% máximo
        'premium': 20,      # 20% máximo
        'vip': 30,         # 30% máximo
        'employee': 50      # 50% máximo
    }
    
    max_discount = max_discounts.get(customer_type, 0)
    
    # Validar que el descuento no exceda el máximo permitido
    if discount > max_discount:
        return False
    
    # Descuentos mayores al 15% requieren orden mínima de $100
    if discount > 15 and order_amount < 100:
        return False
    
    return True

class OrderModel(ValidatedModel):
    customer_type: str = field_validated(
        is_required(),
        is_in(["regular", "premium", "vip", "employee"])
    )
    
    order_amount: float = field_validated(
        is_required(),
        is_positive()
    )
    
    discount_percentage: float = field_validated(
        custom(discount_validation, "Invalid discount for customer type or order amount")
    )

# Uso válido
order = OrderModel(
    customer_type="premium",
    order_amount=150.0,
    discount_percentage=18.0
)

# Uso inválido - descuento muy alto para cliente regular
try:
    invalid_order = OrderModel(
        customer_type="regular",
        order_amount=50.0,
        discount_percentage=25.0
    )
except ValidationException as e:
    print(e.validations)
```

### Validación de Fechas Relacionadas

```python
from datetime import datetime

def end_date_after_start(value, context=None):
    """Valida que end_date sea posterior a start_date"""
    if value is None or context is None:
        return True
    
    start_date_str = context.get('start_date')
    if not start_date_str:
        return True
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(str(value), "%Y-%m-%d")
        return end_date > start_date
    except ValueError:
        return False

def reservation_duration_valid(value, context=None):
    """Valida que la duración de la reserva sea válida según el tipo"""
    if value is None or context is None:
        return True
    
    reservation_type = context.get('reservation_type')
    start_date_str = context.get('start_date')
    
    if not start_date_str or not reservation_type:
        return True
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(str(value), "%Y-%m-%d")
        duration_days = (end_date - start_date).days
        
        # Reglas de duración por tipo de reserva
        max_durations = {
            'hourly': 1,        # Máximo 1 día
            'daily': 30,        # Máximo 30 días
            'weekly': 90,       # Máximo 90 días  
            'monthly': 365      # Máximo 365 días
        }
        
        max_duration = max_durations.get(reservation_type, 30)
        return duration_days <= max_duration
        
    except ValueError:
        return False

class ReservationModel(ValidatedModel):
    reservation_type: str = field_validated(
        is_required(),
        is_in(["hourly", "daily", "weekly", "monthly"])
    )
    
    start_date: str = field_validated(
        is_required(),
        is_date("%Y-%m-%d"),
        is_future_date("%Y-%m-%d")
    )
    
    end_date: str = field_validated(
        is_required(),
        is_date("%Y-%m-%d"),
        custom(end_date_after_start, "End date must be after start date"),
        custom(reservation_duration_valid, "Reservation duration exceeds maximum for this type")
    )

# Uso
from datetime import timedelta

tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

reservation = ReservationModel(
    reservation_type="daily",
    start_date=tomorrow,
    end_date=next_week
)
```

---

## Patrones Avanzados de Validación Condicional

### Validación en Cascada

```python
class EmployeeModel(ValidatedModel):
    employee_type: str = field_validated(
        is_required(),
        is_in(["full_time", "part_time", "contractor", "intern"])
    )
    
    # Solo para empleados de tiempo completo y medio tiempo
    benefits_eligible: bool = field_validated(
        custom(
            required_if_multiple(
                {"employee_type": "full_time"}, 
                "Benefits eligibility required for full-time employees"
            )
        )
    )
    
    # Solo si es elegible para beneficios
    health_plan: str = field_validated(
        custom(
            conditional_requirement(
                lambda ctx: ctx.get('benefits_eligible') == True,
                "Health plan selection required for benefits-eligible employees"
            )
        )
    )
    
    # Solo para contratistas
    contract_end_date: str = field_validated(
        custom(
            required_if("employee_type", "contractor", "Contract end date required for contractors"),
        ),
        is_date("%Y-%m-%d"),
        is_future_date("%Y-%m-%d")
    )

def conditional_requirement(condition_func, message):
    """Factory para crear validadores con condiciones lambda"""
    def validator(value, context=None):
        if context is None:
            return True
        
        if condition_func(context):
            return value is not None and value != ''
        return True
    
    validator.__message__ = message
    return validator
```

### Validación de Grupos de Campos

```python
def at_least_one_required(field_names: list, message: str = "At least one field is required"):
    """Valida que al menos uno de los campos especificados tenga valor"""
    def validator(value, context=None):
        if context is None:
            return True
        
        # Verificar si al menos uno de los campos tiene valor
        has_value = any(
            context.get(field_name) is not None and context.get(field_name) != ''
            for field_name in field_names
        )
        
        return has_value
    
    validator.__message__ = message
    return validator

class ContactFormModel(ValidatedModel):
    name: str = field_validated(is_required())
    
    # Al menos uno de estos debe estar presente
    email: str = field_validated(
        custom(
            at_least_one_required(['email', 'phone'], "Either email or phone is required")
        ),
        is_email()
    )
    
    phone: str = field_validated(
        custom(
            at_least_one_required(['email', 'phone'], "Either email or phone is required")
        ),
        is_phone()
    )

# Uso válido - solo email
contact1 = ContactFormModel(
    name="John Doe",
    email="john@example.com"
)

# Uso válido - solo teléfono  
contact2 = ContactFormModel(
    name="Jane Doe",
    phone="3001234567"
)

# Uso válido - ambos
contact3 = ContactFormModel(
    name="Bob Smith",
    email="bob@example.com",
    phone="3009876543"
)
```

---

## Debugging y Testing de Validación Condicional

### Logging de Validaciones Condicionales

```python
import logging

def debug_conditional_validator(validator_func, validator_name="custom"):
    """Wrapper para debuggear validadores condicionales"""
    def wrapper(value, context=None):
        logger = logging.getLogger(__name__)
        logger.debug(f"Validating {validator_name}: value={value}, context={context}")
        
        result = validator_func(value, context)
        
        logger.debug(f"Validation {validator_name} result: {result}")
        return result
    
    wrapper.__message__ = getattr(validator_func, '__message__', 'Validation failed')
    return wrapper

# Uso en desarrollo
class DebugModel(ValidatedModel):
    field1: str = field_validated(is_required())
    field2: str = field_validated(
        custom(
            debug_conditional_validator(
                required_if("field1", "special_value"),
                "required_if_debug"
            )
        )
    )
```

### Testing Sistemático

```python
import pytest

def test_conditional_validation():
    """Test exhaustivo de validación condicional"""
    
    # Caso 1: Condición no se cumple, campo opcional
    model1 = PaymentModel(payment_method="cash")
    assert model1.payment_method == "cash"
    
    # Caso 2: Condición se cumple, campo requerido y presente
    model2 = PaymentModel(
        payment_method="credit_card", 
        card_number="1234-5678-9012-3456"
    )
    assert model2.card_number is not None
    
    # Caso 3: Condición se cumple, campo requerido pero ausente
    with pytest.raises(ValidationException) as exc_info:
        PaymentModel(payment_method="credit_card")
    
    assert "card_number" in exc_info.value.validations

# Ejecutar: pytest test_conditional.py -v
```

La validación condicional es una herramienta poderosa que permite crear reglas de negocio complejas y flexibles, adaptándose a diferentes escenarios según el contexto de los datos.
