# Error Handling

PyValidX provides a robust error handling system through the `ValidationException` class, which allows capturing, processing, and responding to validation errors in a structured way.

## Basic ValidationException

### Error Structure

```python
from pyvalidx import ValidatedModel, field_validated, ValidationException
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

class UserModel(ValidatedModel):
    name: str = field_validated(
        is_required('Name is required'),
        min_length(2, 'Name must be at least 2 characters')
    )
    email: str = field_validated(
        is_required('Email is required'),
        is_email('Invalid email format')
    )

# Capture and examine errors
try:
    user = UserModel(name='A', email='invalid-email')
except ValidationException as e:
    print('Status Code:', e.status_code)  # 400
    print('Validations:', e.validations)
    # {'name': 'Name must be at least 2 characters', 'email': 'Invalid email format'}

    # Get as dictionary
    error_dict = e.to_dict()
    print('Error Dict:', error_dict)

    # Get as JSON
    error_json = e.to_json()
    print('Error JSON:', error_json)
```

### Multiple Errors per Field

```python
class PasswordModel(ValidatedModel):
    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password('Password must contain uppercase, lowercase, numbers and symbols')
    )

try:
    # Password that fails multiple validations
    pwd_model = PasswordModel(password='123')
except ValidationException as e:
    print(e.validations)
    # {'password': 'Password must be at least 8 characters'}
    # Note: Only the first failing error is reported
```

---

## Custom Error Handling

### Custom Status Codes

```python
class ValidationException(Exception):
    def __init__(self, validations, status_code=400):
        # Default status_code is 400, but can be customized
        pass

# To create errors with specific codes
def validate_admin_user(data):
    try:
        return AdminUserModel(**data)
    except ValidationException as e:
        # Re-raise with 403 code for authorization errors
        if 'admin_key' in e.validations:
            raise ValidationException(e.validations, status_code=403)
        raise  # Re-raise with original code
```

### Error Handling Wrapper

```python
from typing import Dict, Any, Tuple, Optional
import json

class ValidationErrorHandler:
    '''
    Centralized validation error handler
    '''

    @staticmethod
    def handle_validation_error(e: ValidationException) -> Dict[str, Any]:
        '''
        Converts ValidationException to standard response format

        Args:
            e (ValidationException): ValidationException to handle

        Returns:
            Dict[str, Any]: Standard response format
        '''
        return {
            'success': False,
            'status_code': e.status_code,
            'message': 'Validation failed',
            'errors': e.validations,
            'error_count': len(e.validations)
        }

    @staticmethod
    def safe_validate(model_class, data: Dict[str, Any]) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        '''
        Safe validation that returns tuple (model, error)

        Args:
            model_class (type): Model class to validate
            data (Dict[str, Any]): Data to validate

        Returns:
            Tuple[Optional[Any], Optional[Dict[str, Any]]]: Tuple of (model, error)
        '''
        try:
            model = model_class(**data)
            return model, None
        except ValidationException as e:
            return None, ValidationErrorHandler.handle_validation_error(e)
```

---

## Contextual Errors and Debugging

### Debug Information in Errors

```python
class DebugValidationException(ValidationException):
    '''
    Extended ValidationException with debug information
    '''

    def __init__(self, validations, status_code=400, debug_info=None):
        super().__init__(validations, status_code)
        self.debug_info = debug_info or {}

    def to_dict(self) -> Dict[str, Any]:
        '''
        Converts exception to dictionary including debug info

        Returns:
            Dict[str, Any]: Dictionary representation of the exception including debug info
        '''
        result = super().to_dict()
        if self.debug_info:
            result['debug_info'] = self.debug_info
        return result
```

### Validation Error Logging

```python
import logging
from datetime import datetime

class ValidationLogger:
    '''
    Logger for validation errors
    '''

    def __init__(self):
        self.logger = logging.getLogger('pyvalidx.validation')

    def log_validation_error(self, model_name: str, errors: dict, context: dict = None):
        '''
        Log validation errors with context

        Args:
            model_name (str): Name of the model
            errors (dict): Validation errors
            context (dict, optional): Additional context for logging
        '''
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model_name,
            'errors': errors,
            'context': context or {}
        }
        self.logger.error(f'Validation failed: {log_entry}')
```

---

## Error Handling in Web Applications

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

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
        content={
            'message': 'Validation failed',
            'errors': exc.validations,
            'status_code': exc.status_code
        }
    )

@app.post('/users/')
async def create_user(user_data: dict):
    # ValidationException will be caught automatically
    user = UserModel(**user_data)
    return {'message': 'User created', 'user': user.model_dump()}

# Usage:
# POST /users/ with invalid data will automatically return 400 error
```

### Flask Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.errorhandler(ValidationException)
def handle_validation_error(e) -> tuple[dict, int]:
    '''
    Global handler for ValidationException in Flask

    Args:
        e (ValidationException): ValidationException to handle

    Returns:
        tuple: Tuple of (response, status_code)
    '''
    return jsonify(e.to_dict()), e.status_code

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()

    # ValidationException will be caught automatically
    user = UserModel(**user_data)
    return jsonify({'message': 'User created', 'user': user.model_dump()})

# Usage:
# POST /users with invalid data will automatically return 400 error
```

---

## Advanced Error Handling Patterns

### Error Accumulation from Multiple Models

```python
class BatchValidationResult:
    '''
    Result container for batch validation
    '''

    def __init__(self):
        self.valid_models = []
        self.invalid_models = []
        self.errors = {}

    @property
    def valid_count(self) -> int:
        return len(self.valid_models)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid_models)

def batch_validate(model_class, data_list: list) -> BatchValidationResult:
    '''
    Validate multiple instances and collect all errors

    Args:
        model_class (type): Model class to validate
        data_list (list): List of data to validate

    Returns:
        BatchValidationResult: Result container with validation results
    '''
    result = BatchValidationResult()

    for i, data in enumerate(data_list):
        try:
            model = model_class(**data)
            result.valid_models.append(model)
        except ValidationException as e:
            result.invalid_models.append(data)
            result.errors[f"item_{i}"] = e.validations

    return result

# Usage
users_data = [
    {'name': 'John', 'email': 'john@example.com'},
    {'name': 'A', 'email': 'invalid-email'},
    {'name': 'Jane', 'email': 'jane@example.com'}
]

batch_result = batch_validate(UserModel, users_data)
print(f'Valid: {batch_result.valid_count}, Invalid: {batch_result.invalid_count}')
```

### Retry with Backoff for External Validations

```python
import time
import random
from functools import wraps

def retry_validation(max_retries=3, backoff_factor=1.0) -> Callable[[Any, Optional[Dict[str, Any]]], bool]:
    '''
    Decorator for retrying validations with exponential backoff

    Args:
        max_retries (int, optional): Maximum number of retries. Defaults to 3.
        backoff_factor (float, optional): Backoff factor for exponential backoff. Defaults to 1.0.

    Returns:
        Callable: Decorated validator function
    '''
    def decorator(validator_func):
        @wraps(validator_func)
        def wrapper(value, context=None):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return validator_func(value, context)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                    else:
                        raise last_exception

        return wrapper
    return decorator

# Validator that queries external service with retry
@retry_validation(max_retries=3)
def validate_with_external_service(value, context=None) -> bool:
    '''
    Example validator that queries an external service

    Args:
        value (Any): Value to validate
        context (Dict[str, Any], optional): Context containing other field values

    Returns:
        bool: True if validation passes, False otherwise
    '''
    if value is None:
        return True

    # Simulate external service call that may fail
    import requests
    try:
        response = requests.get(f'https://api.example.com/validate/{value}', timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        raise  # Will be retried automatically

class ExternalValidatedModel(ValidatedModel):
    external_id: str = field_validated(
        custom(validate_with_external_service, 'External validation failed')
    )
```

The robust handling of errors is crucial for creating reliable applications that can diagnose and respond appropriately to validation problems, providing useful information for both developers and end-users.
