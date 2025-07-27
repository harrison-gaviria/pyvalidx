# PyValidX Examples

This directory contains comprehensive examples demonstrating how to use PyValidX in real-world scenarios. Each example includes complete, runnable code with detailed explanations.

## Available Examples

### 1. [User Registration](user-registration.md)
Complete user registration system with validation, including:
- Basic registration form validation
- Advanced validation with custom validators
- Email verification workflow
- Web framework integration (FastAPI, Flask)
- Comprehensive testing

**Key Features:**
- Password strength validation
- Email format validation
- Username uniqueness checking
- Age verification
- Custom profanity filters

### 2. [Form Validation](form-validation.md)
Various form validation scenarios, including:
- Contact forms
- Survey forms with conditional fields
- Multi-step registration forms
- File upload forms
- Form validation testing

**Key Features:**
- Conditional field validation
- Multi-step form handling
- File type and size validation
- Progress tracking
- Dynamic validation rules

### 3. [API Validation](api-validation.md)
REST API validation examples, including:
- User management API
- Product catalog API
- Request/response validation
- Multiple framework integrations
- API testing strategies

**Key Features:**
- CRUD operations validation
- Search and filtering validation
- Pagination validation
- Error handling patterns
- Performance monitoring

## Quick Start

Each example is self-contained and can be run independently. Here's how to get started:

### Prerequisites

```bash
pip install pyvalidx
```

For web framework examples, install additional dependencies:

```bash
# For FastAPI examples
pip install fastapi uvicorn

# For Flask examples
pip install flask flask-cors

# For Django examples
pip install django djangorestframework

# For testing
pip install pytest requests
```

### Running Examples

1. **User Registration Example:**
```python
from docs.examples.user_registration import UserRegistrationModel, register_user

# Test with valid data
user_data = {
    'username': 'johndoe123',
    'email': 'john.doe@example.com',
    'password': 'SecurePass123!',
    'confirm_password': 'SecurePass123!',
    'first_name': 'John',
    'last_name': 'Doe',
    'age': 25
}

result = register_user(user_data)
print(result)
```

2. **Form Validation Example:**
```python
from docs.examples.form_validation import ContactFormModel, process_contact_form

# Test contact form
form_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'subject': 'Technical Support',
    'message': 'I need help with the application'
}

result = process_contact_form(form_data)
print(result)
```

3. **API Validation Example:**
```python
from docs.examples.api_validation import UserApiService

# Initialize API service
api_service = UserApiService()

# Create user via API
user_data = {
    'username': 'apiuser',
    'email': 'api@example.com',
    'password': 'SecurePass123!',
    'first_name': 'API',
    'last_name': 'User',
    'role': 'user'
}

result = api_service.create_user(user_data)
print(result)
```

## Example Structure

Each example follows a consistent structure:

```
example-name.md
├── Basic Implementation
├── Advanced Features
├── Custom Validators
├── Error Handling
├── Web Framework Integration
├── Testing
└── Best Practices
```

## Common Patterns

### 1. Model Definition
```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

class ExampleModel(ValidatedModel):
    name: str = field_validated(
        is_required('Name is required'),
        min_length(2, 'Name must be at least 2 characters')
    )

    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address')
    )
```

### 2. Error Handling
```python
from pyvalidx.exception import ValidationException

try:
    model = ExampleModel(**data)
    # Process valid data
    return {'success': True, 'data': model.model_dump()}

except ValidationException as e:
    # Handle validation errors
    return {
        'success': False,
        'errors': e.validations,
        'status_code': e.status_code
    }
```

### 3. Custom Validators
```python
from pyvalidx.core import custom

def custom_validator(value, context=None):
    '''Custom validation logic'''
    if value is None:
        return True

    # Your validation logic here
    return your_validation_condition

custom_validator.__message__ = 'Custom validation error message'

class ModelWithCustomValidator(ValidatedModel):
    field: str = field_validated(
        is_required(),
        custom(custom_validator, 'Custom validation failed')
    )
```

### 4. Web Framework Integration
```python
# FastAPI
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.post('/endpoint')
async def endpoint(data: dict):
    model = ExampleModel(**data)
    return {'success': True, 'data': model.model_dump()}
```

## Testing Examples

All examples include comprehensive test suites:

```python
import pytest
from pyvalidx.exception import ValidationException

class TestExampleModel:
    def test_valid_data(self):
        '''Test with valid data'''
        valid_data = {'name': 'John', 'email': 'john@example.com'}
        model = ExampleModel(**valid_data)
        assert model.name == 'John'

    def test_invalid_data(self):
        '''Test with invalid data'''
        invalid_data = {'name': '', 'email': 'invalid'}

        with pytest.raises(ValidationException) as exc_info:
            ExampleModel(**invalid_data)

        assert 'name' in exc_info.value.validations
        assert 'email' in exc_info.value.validations
```

## Best Practices Demonstrated

1. **Validation Strategy:**
   - Use built-in validators when possible
   - Create reusable custom validators
   - Combine multiple validators effectively
   - Handle edge cases gracefully

2. **Error Handling:**
   - Provide clear, user-friendly error messages
   - Use structured error responses
   - Log validation errors for debugging
   - Handle validation exceptions properly

3. **Performance:**
   - Validate early and often
   - Use efficient validation patterns
   - Monitor validation performance
   - Cache validation results when appropriate

4. **Security:**
   - Validate all user inputs
   - Sanitize data appropriately
   - Use strong password validation
   - Implement rate limiting

5. **Testing:**
   - Test both valid and invalid scenarios
   - Use parameterized tests for multiple cases
   - Test edge cases and boundary conditions
   - Include integration tests

## Contributing Examples

To contribute a new example:

1. Create a new markdown file in this directory
2. Follow the established structure and patterns
3. Include complete, runnable code
4. Add comprehensive tests
5. Document all features and edge cases
6. Update this README with your example

## Support

If you have questions about these examples or need help implementing PyValidX in your project:

1. Check the [main documentation](../index.md)
2. Review the [API reference](../api-reference/)
3. Look at similar examples in this directory
4. Open an issue on GitHub

## License

These examples are part of the PyValidX project and are released under the same license.