# Numeric Validators

Los validadores numéricos proporcionan funcionalidades para validar números, rangos y tipos numéricos específicos.

## is_positive

Valida que el campo sea un número positivo.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.numeric import is_positive

class ProductModel(ValidatedModel):
    price: float = field_validated(is_positive())
    discount: float = field_validated(is_positive("Discount must be positive"))

# Uso válido
product = ProductModel(
    price=29.99,
    discount=5.0
)

# Uso inválido
try:
    invalid_product = ProductModel(price=-10.0)
except ValidationException as e:
    print(e.validations)  # {'price': 'Must be a positive number'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must be a positive number"

---

## is_integer

Valida que el campo sea un número entero.

```python
from pyvalidx.numeric import is_integer

class InventoryModel(ValidatedModel):
    quantity: int = field_validated(is_integer())
    reorder_level: int = field_validated(is_integer("Reorder level must be an integer"))

# Uso válido
inventory = InventoryModel(
    quantity=100,
    reorder_level=10
)

# Uso inválido
try:
    invalid_inventory = InventoryModel(quantity=50.5)
except ValidationException as e:
    print(e.validations)  # {'quantity': 'Must be an integer'}
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must be an integer"

---

## is_float

Valida que el campo sea un número flotante.

```python
from pyvalidx.numeric import is_float

class MeasurementModel(ValidatedModel):
    weight: float = field_validated(is_float())
    height: float = field_validated(is_float("Height must be a decimal number"))

# Uso válido
measurement = MeasurementModel(
    weight=70.5,
    height=1.75
)
```

### Parámetros
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Must be a float"

---

## max_value

Valida que el campo tenga un valor menor o igual al máximo especificado.

```python
from pyvalidx.numeric import max_value

class ScoreModel(ValidatedModel):
    exam_score: float = field_validated(max_value(100))
    rating: int = field_validated(max_value(5, "Rating cannot exceed 5 stars"))

# Uso válido
score = ScoreModel(
    exam_score=95.5,
    rating=4
)

# Uso inválido
try:
    invalid_score = ScoreModel(exam_score=110)
except ValidationException as e:
    print(e.validations)  # {'exam_score': 'Must be less than or equal to 100'}
```

### Parámetros
- `max_val` (Union[int, float]): Valor máximo permitido
- `message` (str, opcional): Mensaje de error personalizado

---

## min_value

Valida que el campo tenga un valor mayor o igual al mínimo especificado.

```python
from pyvalidx.numeric import min_value

class PersonModel(ValidatedModel):
    age: int = field_validated(min_value(0))
    salary: float = field_validated(min_value(0, "Salary cannot be negative"))

# Uso válido
person = PersonModel(
    age=25,
    salary=50000.0
)

# Uso inválido
try:
    invalid_person = PersonModel(age=-5)
except ValidationException as e:
    print(e.validations)  # {'age': 'Must be greater than or equal to 0'}
```

### Parámetros
- `min_val` (Union[int, float]): Valor mínimo permitido
- `message` (str, opcional): Mensaje de error personalizado

---

## Combinando Validadores Numéricos

Puedes combinar múltiples validadores para crear validaciones más complejas:

```python
from pyvalidx.numeric import is_positive, min_value, max_value, is_integer

class ProductRatingModel(ValidatedModel):
    rating: int = field_validated(
        is_integer("Rating must be a whole number"),
        min_value(1, "Rating must be at least 1"),
        max_value(5, "Rating cannot exceed 5")
    )
    
    price: float = field_validated(
        is_positive("Price must be positive"),
        max_value(10000, "Price cannot exceed $10,000")
    )

# Uso válido
product_rating = ProductRatingModel(
    rating=4,
    price=299.99
)
```

---

## Ejemplo Completo: Sistema de Calificaciones

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.numeric import is_integer, is_float, min_value, max_value, is_positive

class StudentGradeModel(ValidatedModel):
    student_id: int = field_validated(
        is_required("Student ID is required"),
        is_integer("Student ID must be an integer"),
        is_positive("Student ID must be positive")
    )
    
    exam_score: float = field_validated(
        is_required("Exam score is required"),
        is_float("Exam score must be a decimal number"),
        min_value(0, "Score cannot be negative"),
        max_value(100, "Score cannot exceed 100")
    )
    
    attendance_percentage: float = field_validated(
        is_float("Attendance must be a decimal number"),
        min_value(0, "Attendance cannot be negative"),
        max_value(100, "Attendance cannot exceed 100%")
    )
    
    extra_credit: int = field_validated(
        is_integer("Extra credit must be whole points"),
        min_value(0, "Extra credit cannot be negative"),
        max_value(10, "Extra credit cannot exceed 10 points")
    )

# Uso
grade = StudentGradeModel(
    student_id=12345,
    exam_score=87.5,
    attendance_percentage=95.0,
    extra_credit=3
)

print(f"Final score: {grade.exam_score + grade.extra_credit}")
```

---

## Validación de Rangos Complejos

```python
class TemperatureModel(ValidatedModel):
    celsius: float = field_validated(
        is_float("Temperature must be a decimal number"),
        min_value(-273.15, "Temperature cannot be below absolute zero"),
        max_value(1000, "Temperature too high for normal measurements")
    )
    
    @property
    def fahrenheit(self) -> float:
        return (self.celsius * 9/5) + 32
    
    @property
    def kelvin(self) -> float:
        return self.celsius + 273.15

# Uso
temp = TemperatureModel(celsius=25.0)
print(f"Temperature: {temp.celsius}°C, {temp.fahrenheit}°F, {temp.kelvin}K")
```

---

## Notas Importantes

- Los validadores numéricos retornan `True` si el valor es `None` (para campos opcionales)
- Los validadores intentan convertir valores a `float` cuando es necesario para comparaciones
- Si la conversión falla, el validador retorna `False`
- Combina validadores numéricos con validadores core para validaciones más robustas
