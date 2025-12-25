# PyValidX

[![PyPI version](https://badge.fury.io/py/pyvalidx.svg)](https://badge.fury.io/py/pyvalidx)
[![Python versions](https://img.shields.io/pypi/pyversions/pyvalidx.svg)](https://pypi.org/project/pyvalidx/)
[![PyPI - Status](https://img.shields.io/pypi/status/pyvalidx)](https://pypi.org/project/pyvalidx/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Custom field validation for Python with Pydantic**

PyValidX is a powerful and flexible validation library built on top of Pydantic that provides a rich set of validators for common use cases while allowing you to create custom validation logic with ease.

## ✨ Features

- **🎯 Easy to Use**: Simple validation with clear, readable syntax
- **🔧 Flexible**: Support for custom validators and conditional validation
- **📝 Type Safe**: Built on Pydantic with full type annotation support
- **🌍 Comprehensive**: Wide range of built-in validators for strings, numbers, dates, and more
- **🚀 Performance**: Efficient validation with minimal overhead
- **📖 Well Documented**: Comprehensive documentation with examples

## 🚀 Quick Example

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.string import is_email, is_strong_password
from pyvalidx.numeric import min_value

class User(ValidatedModel):
    name: str = field_validated(is_required())
    email: str = field_validated(is_required(), is_email())
    password: str = field_validated(is_required(), is_strong_password())
    age: int = field_validated(is_required(), min_value(18))

# This will validate automatically
try:
    user = User(
        name='John Doe',
        email='john@example.com', 
        password='SecurePass123!',
        age=25
    )
    print('User created successfully!')
except ValidationException as e:
    print(f'Validation failed: {e.to_dict()}')
```

## 📦 Installation

Install PyValidX using pip:

```bash
pip install pyvalidx
```

Or with poetry:

```bash
poetry add pyvalidx
```

## 🔌 FastAPI Integration

PyValidX works seamlessly with FastAPI for robust API validation:

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pyvalidx import ValidatedModel, ValidationException, field_validated
from pyvalidx.core import is_required
from pyvalidx.string import is_email, is_strong_password

app = FastAPI()

# Configure global exception handler
@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "details": exc.to_dict()}
    )

# Define your DTO
class CreateUserDto(ValidatedModel):
    username: str = field_validated(is_required())
    email: str = field_validated(is_required(), is_email())
    password: str = field_validated(is_required(), is_strong_password())

# Use it in your endpoint
@app.post("/users")
async def create_user(payload: CreateUserDto):
    # Validation happens automatically!
    return {"message": "User created", "username": payload.username}
```

**Error Response Example:**
```json
{
  "error": "Validation failed",
  "details": {
    "email": ["Invalid email format"],
    "password": ["Password must contain at least one uppercase letter"]
  }
}
```

## 🎯 Core Concepts

### Validators
Validators are functions that check if a value meets certain criteria. They return `True` if valid, `False` otherwise.

### ValidatedModel
A Pydantic model that automatically runs custom validators on initialization and provides error handling.

### field_validated
A field decorator that attaches validators to model fields.

### ValidationException
A custom exception that provides structured error information when validation fails.

## 📚 Available Validators

### Core Validators
- `is_required()` - Ensures field is not None, empty string, or empty list
- `min_length()` - Minimum string/list length
- `max_length()` - Maximum string/list length
- `same_as()` - Field must match another field
- `required_if()` - Conditional requirement based on another field

### String Validators
- `is_email()` - Valid email format
- `is_strong_password()` - Strong password requirements
- `matches_regex()` - Custom regex pattern matching
- `no_whitespace()` - No spaces allowed
- `is_phone()` - Colombian phone number format

### Numeric Validators
- `is_positive()` - Positive numbers only
- `is_integer()` - Integer type validation
- `is_float()` - Float type validation
- `min_value()` - Minimum numeric value
- `max_value()` - Maximum numeric value

### Date Validators
- `is_date()` - Valid date format
- `is_future_date()` - Date must be in the future
- `is_past_date()` - Date must be in the past
- `is_today()` - Date must be today

### Type Validators
- `is_dict()` - Dictionary type validation
- `is_list()` - List type validation
- `is_boolean()` - Boolean type validation
- `is_in()` - Value must be in specified choices

## 🔗 Quick Links

- [Getting Started](getting-started/installation.md) - Install and set up PyValidX
- [Validators](validators/core.md) - Explore all available validators
- [API Reference](api-reference/validated-model.md) - Complete API documentation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/harrison-gaviria/pyvalidx/blob/main/LICENSE) file for details.

## 👤 Author

**Harrison Alonso Arroyave Gaviria**
- GitHub: [@harrison-gaviria](https://github.com/harrison-gaviria)
- Email: harrisonarroyaveg@gmail.com