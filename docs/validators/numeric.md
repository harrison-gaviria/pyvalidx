# Numeric Validators

Numeric validators provide functionalities for validating numbers, ranges, and specific numeric types.

## is_positive

Validates that the field is a positive number.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.numeric import is_positive

class ProductModel(ValidatedModel):
    price: float = field_validated(is_positive())
    discount: float = field_validated(is_positive('Discount must be positive'))

# Valid usage
product = ProductModel(
    price=29.99,
    discount=5.0
)

# Invalid usage
try:
    invalid_product = ProductModel(price=-10.0)
except ValidationException as e:
    print(e.validations)  # {'price': 'Must be a positive number'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be a positive number'

---

## is_integer

Validates that the field is an integer.

```python
from pyvalidx.numeric import is_integer

class InventoryModel(ValidatedModel):
    quantity: int = field_validated(is_integer())
    reorder_level: int = field_validated(is_integer('Reorder level must be an integer'))

# Valid usage
inventory = InventoryModel(
    quantity=100,
    reorder_level=10
)

# Invalid usage
try:
    invalid_inventory = InventoryModel(quantity=50.5)
except ValidationException as e:
    print(e.validations)  # {'quantity': 'Must be an integer'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be an integer'

---

## is_float

Validates that the field is a floating-point number.

```python
from pyvalidx.numeric import is_float

class MeasurementModel(ValidatedModel):
    weight: float = field_validated(is_float())
    height: float = field_validated(is_float('Height must be a decimal number'))

# Valid usage
measurement = MeasurementModel(
    weight=70.5,
    height=1.75
)
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be a float'

---

## max_value

Validates that the field has a value less than or equal to the specified maximum.

```python
from pyvalidx.numeric import max_value

class ScoreModel(ValidatedModel):
    exam_score: float = field_validated(max_value(100))
    rating: int = field_validated(max_value(5, 'Rating cannot exceed 5 stars'))

# Valid usage
score = ScoreModel(
    exam_score=95.5,
    rating=4
)

# Invalid usage
try:
    invalid_score = ScoreModel(exam_score=110)
except ValidationException as e:
    print(e.validations)  # {'exam_score': 'Must be less than or equal to 100'}
```

### Parameters
- `max_val` (Union[int, float]): Maximum allowed value
- `message` (str, optional): Custom error message

---

## min_value

Validates that the field has a value greater than or equal to the specified minimum.

```python
from pyvalidx.numeric import min_value

class PersonModel(ValidatedModel):
    age: int = field_validated(min_value(0))
    salary: float = field_validated(min_value(0, 'Salary cannot be negative'))

# Valid usage
person = PersonModel(
    age=25,
    salary=50000.0
)

# Invalid usage
try:
    invalid_person = PersonModel(age=-5)
except ValidationException as e:
    print(e.validations)  # {'age': 'Must be greater than or equal to 0'}
```

### Parameters
- `min_val` (Union[int, float]): Minimum allowed value
- `message` (str, optional): Custom error message

---

## Combining Numeric Validators

You can combine multiple validators to create more complex validations:

```python
from pyvalidx.numeric import is_positive, min_value, max_value, is_integer

class ProductRatingModel(ValidatedModel):
    rating: int = field_validated(
        is_integer('Rating must be a whole number'),
        min_value(1, 'Rating must be at least 1'),
        max_value(5, 'Rating cannot exceed 5')
    )

    price: float = field_validated(
        is_positive('Price must be positive'),
        max_value(10000, 'Price cannot exceed $10,000')
    )

# Valid usage
product_rating = ProductRatingModel(
    rating=4,
    price=299.99
)
```

---

## Complete Example: Grading System

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.numeric import is_integer, is_float, min_value, max_value, is_positive

class StudentGradeModel(ValidatedModel):
    student_id: int = field_validated(
        is_required('Student ID is required'),
        is_integer('Student ID must be an integer'),
        is_positive('Student ID must be positive')
    )

    exam_score: float = field_validated(
        is_required('Exam score is required'),
        is_float('Exam score must be a decimal number'),
        min_value(0, 'Score cannot be negative'),
        max_value(100, 'Score cannot exceed 100')
    )

    attendance_percentage: float = field_validated(
        is_float('Attendance must be a decimal number'),
        min_value(0, 'Attendance cannot be negative'),
        max_value(100, 'Attendance cannot exceed 100%')
    )

    extra_credit: int = field_validated(
        is_integer('Extra credit must be whole points'),
        min_value(0, 'Extra credit cannot be negative'),
        max_value(10, 'Extra credit cannot exceed 10 points')
    )

# Usage
grade = StudentGradeModel(
    student_id=12345,
    exam_score=87.5,
    attendance_percentage=95.0,
    extra_credit=3
)

print(f'Final score: {grade.exam_score + grade.extra_credit}')
```

---

## Complex Range Validation

```python
class TemperatureModel(ValidatedModel):
    celsius: float = field_validated(
        is_float('Temperature must be a decimal number'),
        min_value(-273.15, 'Temperature cannot be below absolute zero'),
        max_value(1000, 'Temperature too high for normal measurements')
    )

    @property
    def fahrenheit(self) -> float:
        '''
        Converts Celsius to Fahrenheit

        Returns:
            float: Temperature in Fahrenheit
        '''
        return (self.celsius * 9/5) + 32

    @property
    def kelvin(self) -> float:
        '''
        Converts Celsius to Kelvin

        Returns:
            float: Temperature in Kelvin
        '''
        return self.celsius + 273.15

# Usage
temp = TemperatureModel(celsius=25.0)
print(f'Temperature: {temp.celsius}°C, {temp.fahrenheit}°F, {temp.kelvin}K')
```

---

## Important Notes

- Numeric validators return `True` if the value is `None` (for optional fields)
- Validators attempt to convert values to `float` when necessary for comparisons
- If conversion fails, the validator returns `False`
- Combine numeric validators with core validators for more robust validations
