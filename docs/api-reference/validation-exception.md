# ValidationException API Reference

The `ValidationException` class is raised when field validation fails in PyValidX models.

## Class Definition

```python
class ValidationException(Exception):
    '''
    Exception raised when validation fails.

    Attributes:
        status_code (int): HTTP status code (default: 400)
        validations (Dict[str, str]): Dictionary of field names and error messages
    '''
```

## Attributes

### `status_code: int`

The HTTP status code associated with the validation error.

**Default:** `400` (Bad Request)

**Example:**
```python
try:
    user = User(name='', email='invalid-email')
except ValidationException as e:
    print(e.status_code)  # 400
```

### `validations: Dict[str, str]`

A dictionary containing field names as keys and their corresponding error messages as values.

**Example:**
```python
try:
    user = User(name='', email='invalid-email')
except ValidationException as e:
    print(e.validations)
    # {'name': 'This field is required', 'email': 'Invalid email format'}
```

## Methods

### `to_dict() -> Dict[str, Any]`

Returns the exception as a dictionary containing both status code and validation errors.

**Returns:**
- `Dict[str, Any]`: Dictionary with `status_code` and `validations` keys

**Example:**
```python
try:
    user = User(name='', email='invalid-email')
except ValidationException as e:
    error_dict = e.to_dict()
    print(error_dict)
    # {
    #     'status_code': 400,
    #     'validations': {
    #         'name': 'This field is required',
    #         'email': 'Invalid email format'
    #     }
    # }
```

### `to_json() -> str`

Returns the exception as a JSON string.

**Returns:**
- `str`: JSON string containing the exception information

**Example:**
```python
try:
    user = User(name='', email='invalid-email')
except ValidationException as e:
    json_string = e.to_json()
    print(json_string)
    # {'status_code': 400, 'validations': {'name': 'This field is required', 'email': 'Invalid email format'}}
```

## Usage Examples

### Basic Error Handling

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.string import is_email
from pyvalidx.exception import ValidationException

class User(ValidatedModel):
    name: str = field_validated(is_required())
    email: str = field_validated(is_required(), is_email())

try:
    user = User(name='', email='invalid-email')
except ValidationException as e:
    print(f'Validation failed with status {e.status_code}')
    for field, message in e.validations.items():
        print(f'- {field}: {message}')
```

### Web API Error Response

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users', methods=['POST'])
def create_user() -> tuple[dict, int]:
    '''
    Create a new user.

    Returns:
        tuple: Tuple of (response, status_code)
    '''
    try:
        user_data = request.get_json()
        user = User(**user_data)
        return jsonify({'success': True, 'user': user.dict()}), 201
    except ValidationException as e:
        return jsonify(e.to_dict()), e.status_code
```

### Custom Error Handling

```python
def handle_validation_error(e: ValidationException) -> dict[str, Any]:
    '''
    Custom error handler that formats validation errors
    for better user experience.

    Args:
        e (ValidationException): ValidationException to handle

    Returns:
        dict: Formatted error response
    '''
    formatted_errors = []
    for field, message in e.validations.items():
        formatted_errors.append({
            'field': field,
            'message': message,
            'code': f'INVALID_{field.upper()}'
        })

    return {
        'error': 'Validation failed',
        'status_code': e.status_code,
        'details': formatted_errors
    }

# Usage
try:
    user = User(name='', email='invalid')
except ValidationException as e:
    error_response = handle_validation_error(e)
    print(error_response)
```

### Logging Validation Errors

```python
import logging

logger = logging.getLogger(__name__)

def create_user_with_logging(user_data: dict[str, Any]) -> User:
    '''
    Creates a new user with logging.

    Args:
        user_data (dict[str, Any]): User data to create

    Returns:
        User: Created user
    '''
    try:
        user = User(**user_data)
        logger.info(f'User created successfully: {user.email}')
        return user
    except ValidationException as e:
        logger.warning(
            f'User creation failed: {e.validations}',
            extra={'validation_errors': e.validations}
        )
        raise
```

### Multiple Model Validation

```python
def validate_multiple_models(data_list: list[dict[str, Any]]) -> dict[str, Any]:
    '''
    Validates multiple model instances and collects all errors.

    Args:
        data_list (list[dict[str, Any]]): List of user data to validate

    Returns:
        dict: Validation results
    '''
    results = {
        'successful': [],
        'failed': [],
        'total_errors': 0
    }

    for i, data in enumerate(data_list):
        try:
            user = User(**data)
            results['successful'].append({
                'index': i,
                'user': user.dict()
            })
        except ValidationException as e:
            results['failed'].append({
                'index': i,
                'errors': e.validations
            })
            results['total_errors'] += len(e.validations)

    return results
```

### Testing with ValidationException

```python
import pytest

def test_user_validation_errors() -> None:
    '''
    Test that proper validation errors are raised.
    '''
    with pytest.raises(ValidationException) as exc_info:
        User(name='', email='invalid-email')

    exception = exc_info.value

    # Test status code
    assert exception.status_code == 400

    # Test specific validation errors
    assert 'name' in exception.validations
    assert 'email' in exception.validations
    assert exception.validations['name'] == 'This field is required'
    assert 'Invalid email format' in exception.validations['email']

def test_exception_serialization() -> None:
    '''
    Test exception serialization methods.
    '''
    try:
        User(name='', email='invalid')
    except ValidationException as e:
        # Test to_dict method
        error_dict = e.to_dict()
        assert 'status_code' in error_dict
        assert 'validations' in error_dict

        # Test to_json method
        json_str = e.to_json()
        assert isinstance(json_str, str)
        assert 'status_code' in json_str
        assert 'validations' in json_str
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException) -> JSONResponse:
    '''
    Global handler for ValidationException in FastAPI

    Args:
        request (Request): FastAPI request object
        exc (ValidationException): ValidationException to handle

    Returns:
        JSONResponse: JSON response with error details
    '''
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.post('/users')
async def create_user(user_data: dict[str, Any]) -> dict[str, Any]:
    '''
    Create a new user.

    Args:
        user_data (dict[str, Any]): User data to create

    Returns:
        dict[str, Any]: Created user
    '''
    user = User(**user_data)  # ValidationException handled automatically
    return {'user': user.dict()}
```

### Django Integration

```python
from django.http import JsonResponse
from django.views import View
import json

class UserCreateView(View):
    def post(self, request) -> JsonResponse:
        '''
        Create a new user.

        Args:
            request (HttpRequest): Django request object

        Returns:
            JsonResponse: JSON response with user data or error details
        '''
        try:
            user_data = json.loads(request.body)
            user = User(**user_data)
            return JsonResponse({'success': True, 'user': user.dict()})
        except ValidationException as e:
            return JsonResponse(e.to_dict(), status=e.status_code)
```

## Best Practices

1. **Always catch ValidationException**: Handle validation errors gracefully in your application
2. **Use appropriate HTTP status codes**: The default 400 is usually correct for validation errors
3. **Log validation errors**: Keep track of common validation failures for improvement
4. **Provide user-friendly messages**: Use custom error messages that help users fix their input
5. **Test error scenarios**: Include tests for validation failures in your test suite
6. **Don't expose internal details**: Sanitize error messages before showing them to end users
