# User Registration Example

This comprehensive example demonstrates how to build a complete user registration system using PyValidX with advanced validation rules, custom validators, and real-world integration patterns.

## Table of Contents

- [Basic User Registration](#basic-user-registration)
- [Advanced Registration with Custom Validators](#advanced-registration-with-custom-validators)
- [Email Verification Workflow](#email-verification-workflow)
- [Web Framework Integration](#web-framework-integration)
- [Testing Strategies](#testing-strategies)
- [Best Practices](#best-practices)

## Basic User Registration

### Simple Registration Model

The foundation of any registration system starts with a well-defined model:

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length, max_length, same_as
from pyvalidx.string import is_email, is_strong_password
from pyvalidx.numeric import min_value, max_value
from pyvalidx.exception import ValidationException
from typing import Optional
from datetime import datetime
import uuid

class UserRegistrationModel(ValidatedModel):
    '''
    Basic user registration model with essential validation rules

    This model demonstrates fundamental validation patterns for user registration,
    including password confirmation and age verification.
    '''

    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        max_length(20, 'Username cannot exceed 20 characters')
    )

    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address')
    )

    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password('Password must contain uppercase, lowercase, numbers and special characters')
    )

    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('password', 'Passwords do not match')
    )

    first_name: str = field_validated(
        is_required('First name is required'),
        min_length(2, 'First name must be at least 2 characters'),
        max_length(50, 'First name cannot exceed 50 characters')
    )

    last_name: str = field_validated(
        is_required('Last name is required'),
        min_length(2, 'Last name must be at least 2 characters'),
        max_length(50, 'Last name cannot exceed 50 characters')
    )

    age: int = field_validated(
        is_required('Age is required'),
        min_value(13, 'You must be at least 13 years old to register'),
        max_value(120, 'Please enter a valid age')
    )

    terms_accepted: bool = field_validated(
        is_required('You must accept the terms and conditions')
    )

def register_user(user_data: dict) -> dict:
    '''
    Process user registration with comprehensive validation

    Args:
        user_data (dict): User registration data

    Returns:
        dict: Registration result with success status and user data or errors

    Example:
        >>> user_data = {
        ...     'username': 'johndoe123',
        ...     'email': 'john@example.com',
        ...     'password': 'SecurePass123!',
        ...     'confirm_password': 'SecurePass123!',
        ...     'first_name': 'John',
        ...     'last_name': 'Doe',
        ...     'age': 25,
        ...     'terms_accepted': True
        ... }
        >>> result = register_user(user_data)
        >>> print(result['success'])
        True
    '''
    try:
        user = UserRegistrationModel(**user_data)

        # Simulate saving to database
        user_id = str(uuid.uuid4())

        return {
            'success': True,
            'user_id': user_id,
            'message': 'User registered successfully',
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age
            }
        }

    except ValidationException as e:
        return {
            'success': False,
            'errors': e.validations,
            'message': 'Registration failed due to validation errors'
        }
```

### Usage Example

```python
# Valid registration
valid_user_data = {
    'username': 'johndoe123',
    'email': 'john.doe@example.com',
    'password': 'SecurePass123!',
    'confirm_password': 'SecurePass123!',
    'first_name': 'John',
    'last_name': 'Doe',
    'age': 25,
    'terms_accepted': True
}

result = register_user(valid_user_data)
print(result)
# Output: {'success': True, 'user_id': '...', 'message': 'User registered successfully', ...}

# Invalid registration
invalid_user_data = {
    'username': 'jo',  # Too short
    'email': 'invalid-email',  # Invalid format
    'password': 'weak',  # Too weak
    'confirm_password': 'different',  # Doesn't match
    'first_name': '',  # Empty
    'last_name': 'Doe',
    'age': 12,  # Too young
    'terms_accepted': False  # Not accepted
}

result = register_user(invalid_user_data)
print(result)
# Output: {'success': False, 'errors': {...}, 'message': 'Registration failed...'}
```

## Advanced Registration with Custom Validators

### Custom Business Logic Validators

For real-world applications, you often need custom validation logic:

```python
from pyvalidx.core import custom
import re

def username_format_validator(value, context=None):
    '''
    Validates username format according to business rules

    Rules:
    - Must start with a letter
    - Can contain letters, numbers, and underscores
    - Cannot end with underscore
    - Cannot have consecutive underscores

    Args:
        value: Username to validate
        context: Validation context (unused)

    Returns:
        bool: True if valid, False otherwise
    '''
    if value is None:
        return True

    # Must start with letter
    if not re.match(r'^[a-zA-Z]', str(value)):
        return False

    # Can only contain letters, numbers, underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', str(value)):
        return False

    # Cannot end with underscore
    if str(value).endswith('_'):
        return False

    # Cannot have consecutive underscores
    if '__' in str(value):
        return False

    return True

username_format_validator.__message__ = 'Username must start with a letter and contain only letters, numbers, and underscores (no consecutive underscores or ending underscore)'

def no_profanity_validator(value, context=None):
    '''
    Validates that username doesn't contain profanity

    Args:
        value: Username to validate
        context: Validation context (unused)

    Returns:
        bool: True if valid, False otherwise
    '''
    if value is None:
        return True

    # Simple profanity filter (in practice, use a comprehensive list)
    profanity_words = ['badword1', 'badword2', 'inappropriate']
    username_lower = str(value).lower()

    return not any(word in username_lower for word in profanity_words)

no_profanity_validator.__message__ = 'Username contains inappropriate content'

def unique_username_validator(value, context=None):
    '''
    Validates that username is unique in the system

    Args:
        value: Username to validate
        context: Validation context (unused)

    Returns:
        bool: True if unique, False otherwise
    '''
    if value is None:
        return True

    # Simulate database check
    existing_usernames = ['admin', 'root', 'test', 'demo', 'user', 'guest']
    return str(value).lower() not in existing_usernames

unique_username_validator.__message__ = 'Username is already taken'

def unique_email_validator(value, context=None):
    '''
    Validates that email is unique in the system

    Args:
        value: Email to validate
        context: Validation context (unused)

    Returns:
        bool: True if unique, False otherwise
    '''
    if value is None:
        return True

    # Simulate database check
    existing_emails = ['admin@example.com', 'test@example.com']
    return str(value).lower() not in existing_emails

unique_email_validator.__message__ = 'Email is already registered'

def password_not_contains_username(value, context=None):
    '''
    Validates that password doesn't contain username

    Args:
        value: Password to validate
        context: Validation context containing other field values

    Returns:
        bool: True if valid, False otherwise
    '''
    if value is None or context is None:
        return True

    username = context.get('username')
    if username is None:
        return True

    return str(username).lower() not in str(value).lower()

password_not_contains_username.__message__ = 'Password cannot contain username'

class AdvancedUserRegistrationModel(ValidatedModel):
    '''
    Advanced user registration model with custom business logic validators

    This model demonstrates how to implement complex business rules
    using custom validators while maintaining clean, readable code.
    '''

    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        max_length(20, 'Username cannot exceed 20 characters'),
        custom(username_format_validator),
        custom(no_profanity_validator),
        custom(unique_username_validator)
    )

    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address'),
        custom(unique_email_validator)
    )

    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password('Password must contain uppercase, lowercase, numbers and special characters'),
        custom(password_not_contains_username)
    )

    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('password', 'Passwords do not match')
    )

    first_name: str = field_validated(
        is_required('First name is required'),
        min_length(2, 'First name must be at least 2 characters'),
        max_length(50, 'First name cannot exceed 50 characters')
    )

    last_name: str = field_validated(
        is_required('Last name is required'),
        min_length(2, 'Last name must be at least 2 characters'),
        max_length(50, 'Last name cannot exceed 50 characters')
    )

    age: int = field_validated(
        is_required('Age is required'),
        min_value(13, 'You must be at least 13 years old to register'),
        max_value(120, 'Please enter a valid age')
    )

    phone: Optional[str] = field_validated(
        min_length(10, 'Phone number must be at least 10 digits'),
        max_length(15, 'Phone number cannot exceed 15 digits')
    )

    terms_accepted: bool = field_validated(
        is_required('You must accept the terms and conditions')
    )

    newsletter_signup: Optional[bool] = None
```

## Email Verification Workflow

### Email Verification Model

```python
from pyvalidx.core import custom

def verification_code_validator(value, context=None):
    '''
    Validates verification code format

    Args:
        value: Verification code to validate
        context: Validation context (unused)

    Returns:
        bool: True if valid format, False otherwise
    '''
    if value is None:
        return True

    # Must be exactly 6 digits
    return re.match(r'^\d{6}$', str(value)) is not None

verification_code_validator.__message__ = 'Verification code must be exactly 6 digits'

class EmailVerificationModel(AdvancedUserRegistrationModel):
    '''
    Extended registration model with email verification

    This model adds email verification capability to the registration process,
    requiring users to verify their email address before completing registration.
    '''

    verification_code: str = field_validated(
        is_required('Verification code is required'),
        custom(verification_code_validator)
    )

class RegistrationService:
    '''
    Service class for handling user registration with email verification

    This service demonstrates a complete registration workflow including
    email verification, temporary data storage, and multi-step validation.
    '''

    def __init__(self):
        # In practice, this would be a database or cache
        self.pending_verifications = {}

    def initiate_registration(self, user_data: dict) -> dict:
        '''
        Start the registration process and send verification email

        Args:
            user_data (dict): User registration data

        Returns:
            dict: Result with success status and next steps
        '''
        try:
            # Validate initial registration data (without verification code)
            user = AdvancedUserRegistrationModel(**user_data)

            # Generate verification code
            verification_code = self.generate_verification_code()

            # Store pending registration
            self.pending_verifications[user.email] = {
                'user_data': user_data,
                'verification_code': verification_code,
                'timestamp': datetime.now()
            }

            # Send verification email
            self.send_verification_email(user.email, verification_code)

            return {
                'success': True,
                'message': 'Verification email sent. Please check your inbox.',
                'email': user.email
            }

        except ValidationException as e:
            return {
                'success': False,
                'errors': e.validations,
                'message': 'Registration data validation failed'
            }

    def complete_registration(self, email: str, verification_code: str) -> dict:
        '''
        Complete registration after email verification

        Args:
            email (str): User's email address
            verification_code (str): Verification code from email

        Returns:
            dict: Final registration result
        '''
        # Check if verification is pending
        if email not in self.pending_verifications:
            return {
                'success': False,
                'error': 'No pending verification for this email'
            }

        pending = self.pending_verifications[email]

        # Check verification code
        if pending['verification_code'] != verification_code:
            return {
                'success': False,
                'error': 'Invalid verification code'
            }

        # Check if code is expired (5 minutes)
        if (datetime.now() - pending['timestamp']).seconds > 300:
            del self.pending_verifications[email]
            return {
                'success': False,
                'error': 'Verification code has expired'
            }

        try:
            # Complete validation with verification code
            user_data = pending['user_data']
            user_data['verification_code'] = verification_code

            user = EmailVerificationModel(**user_data)

            # Remove from pending
            del self.pending_verifications[email]

            # Simulate saving to database
            user_id = str(uuid.uuid4())

            return {
                'success': True,
                'user_id': user_id,
                'message': 'Registration completed successfully',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }

        except ValidationException as e:
            return {
                'success': False,
                'errors': e.validations,
                'message': 'Final validation failed'
            }

    def generate_verification_code(self) -> str:
        '''Generate 6-digit verification code'''
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])

    def send_verification_email(self, email: str, code: str):
        '''Simulate sending verification email'''
        print(f'Sending verification email to {email}')
        print(f'Verification code: {code}')
        print('Subject: Verify your email address')
        print(f'Body: Your verification code is: {code}')
```

### Email Verification Usage

```python
# Initialize registration service
registration_service = RegistrationService()

# Step 1: Initiate registration
user_data = {
    'username': 'newuser123',
    'email': 'newuser@example.com',
    'password': 'SecurePass123!',
    'confirm_password': 'SecurePass123!',
    'first_name': 'New',
    'last_name': 'User',
    'age': 25,
    'terms_accepted': True
}

result = registration_service.initiate_registration(user_data)
print('Initiation result:', result)

# Step 2: Complete registration with verification code
if result['success']:
    # User receives verification code via email
    verification_code = '123456'  # This would come from the email

    complete_result = registration_service.complete_registration(
        'newuser@example.com',
        verification_code
    )
    print('Completion result:', complete_result)
```

## Web Framework Integration

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title='User Registration API', version='1.0.0')

# Global exception handler for ValidationException
@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    '''
    Global handler for validation exceptions

    This handler ensures consistent error responses across all endpoints
    and provides structured error information to clients.
    '''
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'message': 'Validation failed',
            'errors': exc.validations,
            'status_code': exc.status_code
        }
    )

# Initialize registration service
registration_service = RegistrationService()

@app.post('/register/initiate', status_code=200)
async def initiate_registration_endpoint(
    user_data: dict,
    background_tasks: BackgroundTasks
):
    '''
    Initiate user registration with email verification

    This endpoint validates initial user data and sends a verification email.
    The actual registration is completed when the user verifies their email.

    Args:
        user_data (dict): User registration data
        background_tasks (BackgroundTasks): FastAPI background tasks

    Returns:
        dict: Registration initiation result

    Raises:
        HTTPException: If validation fails or registration cannot be initiated
    '''
    result = registration_service.initiate_registration(user_data)

    if not result['success']:
        raise HTTPException(
            status_code=400,
            detail=result
        )

    return result

@app.post('/register/verify', status_code=201)
async def verify_registration_endpoint(
    email: str,
    verification_code: str
):
    '''
    Complete user registration with email verification

    This endpoint completes the registration process after the user
    provides the verification code received via email.

    Args:
        email (str): User's email address
        verification_code (str): Verification code from email

    Returns:
        dict: Final registration result

    Raises:
        HTTPException: If verification fails or registration cannot be completed
    '''
    result = registration_service.complete_registration(email, verification_code)

    if not result['success']:
        raise HTTPException(
            status_code=400,
            detail=result
        )

    return result

@app.post('/register/direct', status_code=201)
async def register_user_direct(user_data: dict):
    '''
    Direct user registration without email verification

    This endpoint provides immediate registration for scenarios where
    email verification is not required.

    Args:
        user_data (dict): Complete user registration data

    Returns:
        dict: Registration result
    '''
    # ValidationException will be caught by global handler
    user = AdvancedUserRegistrationModel(**user_data)

    # Simulate saving to database
    user_id = str(uuid.uuid4())

    return {
        'success': True,
        'user_id': user_id,
        'message': 'User registered successfully',
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    }

# Health check endpoint
@app.get('/health')
async def health_check():
    '''API health check endpoint'''
    return {'status': 'healthy', 'service': 'user-registration'}
```

### Flask Integration

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Global error handler for ValidationException
@app.errorhandler(ValidationException)
def handle_validation_error(e):
    '''
    Global handler for validation exceptions in Flask

    Args:
        e (ValidationException): The validation exception

    Returns:
        tuple: JSON response and status code
    '''
    return jsonify(e.to_dict()), e.status_code

# Initialize registration service
registration_service = RegistrationService()

@app.route('/register/initiate', methods=['POST'])
def initiate_registration_flask():
    '''Flask endpoint for initiating registration'''
    user_data = request.get_json()

    if not user_data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400

    result = registration_service.initiate_registration(user_data)

    if not result['success']:
        return jsonify(result), 400

    return jsonify(result)

@app.route('/register/verify', methods=['POST'])
def verify_registration_flask():
    '''Flask endpoint for completing registration'''
    data = request.get_json()

    if not data or 'email' not in data or 'verification_code' not in data:
        return jsonify({
            'success': False,
            'message': 'Email and verification_code are required'
        }), 400

    result = registration_service.complete_registration(
        data['email'],
        data['verification_code']
    )

    if not result['success']:
        return jsonify(result), 400

    return jsonify(result), 201

@app.route('/register/direct', methods=['POST'])
def register_user_flask():
    '''Flask endpoint for direct registration'''
    user_data = request.get_json()

    if not user_data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400

    # ValidationException will be caught by global handler
    user = AdvancedUserRegistrationModel(**user_data)

    # Simulate saving to database
    user_id = str(uuid.uuid4())

    return jsonify({
        'success': True,
        'user_id': user_id,
        'message': 'User registered successfully',
        'user': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
    }), 201

if __name__ == '__main__':
    app.run(debug=True)
```

## Testing Strategies

### Comprehensive Test Suite

```python
import pytest
from pyvalidx.exception import ValidationException
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

class TestUserRegistrationModel:
    '''Test suite for basic user registration model'''

    def test_valid_registration(self):
        '''Test successful user registration with valid data'''
        valid_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        user = UserRegistrationModel(**valid_data)
        assert user.username == 'testuser123'
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.age == 25
        assert user.terms_accepted is True

    def test_invalid_email(self):
        '''Test registration with invalid email format'''
        invalid_data = {
            'username': 'testuser123',
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            UserRegistrationModel(**invalid_data)

        assert 'email' in exc_info.value.validations
        assert 'valid email' in exc_info.value.validations['email'].lower()

    def test_password_mismatch(self):
        '''Test registration with password confirmation mismatch'''
        invalid_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'DifferentPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            UserRegistrationModel(**invalid_data)

        assert 'confirm_password' in exc_info.value.validations
        assert 'match' in exc_info.value.validations['confirm_password'].lower()

    def test_underage_user(self):
        '''Test registration with underage user'''
        invalid_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 12,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            UserRegistrationModel(**invalid_data)

        assert 'age' in exc_info.value.validations
        assert '13' in exc_info.value.validations['age']

    def test_weak_password(self):
        '''Test registration with weak password'''
        invalid_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'weak',
            'confirm_password': 'weak',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            UserRegistrationModel(**invalid_data)

        assert 'password' in exc_info.value.validations

    def test_terms_not_accepted(self):
        '''Test registration without accepting terms'''
        invalid_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': False
        }

        with pytest.raises(ValidationException) as exc_info:
            UserRegistrationModel(**invalid_data)

        assert 'terms_accepted' in exc_info.value.validations

class TestAdvancedUserRegistrationModel:
    '''Test suite for advanced user registration model with custom validators'''

    def test_invalid_username_format(self):
        '''Test username format validation'''
        invalid_data = {
            'username': '123invalid',  # Starts with number
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            AdvancedUserRegistrationModel(**invalid_data)

        assert 'username' in exc_info.value.validations

    def test_username_with_profanity(self):
        '''Test profanity filter in username'''
        invalid_data = {
            'username': 'badword1user',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            AdvancedUserRegistrationModel(**invalid_data)

        assert 'username' in exc_info.value.validations
        assert 'inappropriate' in exc_info.value.validations['username'].lower()

    def test_duplicate_username(self):
        '''Test duplicate username validation'''
        invalid_data = {
            'username': 'admin',  # Reserved username
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            AdvancedUserRegistrationModel(**invalid_data)

        assert 'username' in exc_info.value.validations
        assert 'taken' in exc_info.value.validations['username'].lower()

    def test_password_contains_username(self):
        '''Test password cannot contain username'''
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testuser123!',  # Contains username
            'confirm_password': 'testuser123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        with pytest.raises(ValidationException) as exc_info:
            AdvancedUserRegistrationModel(**invalid_data)

        assert 'password' in exc_info.value.validations
        assert 'username' in exc_info.value.validations['password'].lower()

class TestRegistrationService:
    '''Test suite for registration service with email verification'''

    def setup_method(self):
        '''Set up test fixtures'''
        self.service = RegistrationService()
        self.valid_user_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

    def test_initiate_registration_success(self):
        '''Test successful registration initiation'''
        result = self.service.initiate_registration(self.valid_user_data)

        assert result['success'] is True
        assert 'message' in result
        assert result['email'] == 'test@example.com'
        assert 'test@example.com' in self.service.pending_verifications

    def test_initiate_registration_invalid_data(self):
        '''Test registration initiation with invalid data'''
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid-email'

        result = self.service.initiate_registration(invalid_data)

        assert result['success'] is False
        assert 'errors' in result
        assert 'email' in result['errors']

    def test_complete_registration_success(self):
        '''Test successful registration completion'''
        # First initiate registration
        self.service.initiate_registration(self.valid_user_data)

        # Get the verification code
        pending = self.service.pending_verifications['test@example.com']
        verification_code = pending['verification_code']

        # Complete registration
        result = self.service.complete_registration('test@example.com', verification_code)

        assert result['success'] is True
        assert 'user_id' in result
        assert 'test@example.com' not in self.service.pending_verifications

    def test_complete_registration_invalid_code(self):
        '''Test registration completion with invalid verification code'''
        # First initiate registration
        self.service.initiate_registration(self.valid_user_data)

        # Try to complete with wrong code
        result = self.service.complete_registration('test@example.com', '000000')

        assert result['success'] is False
        assert 'Invalid verification code' in result['error']

    def test_complete_registration_expired_code(self):
        '''Test registration completion with expired verification code'''
        # First initiate registration
        self.service.initiate_registration(self.valid_user_data)

        # Manually set timestamp to past
        pending = self.service.pending_verifications['test@example.com']
        pending['timestamp'] = datetime.now() - timedelta(minutes=10)

        verification_code = pending['verification_code']

        # Try to complete with expired code
        result = self.service.complete_registration('test@example.com', verification_code)

        assert result['success'] is False
        assert 'expired' in result['error'].lower()

    def test_complete_registration_no_pending(self):
        '''Test registration completion without pending verification'''
        result = self.service.complete_registration('nonexistent@example.com', '123456')

        assert result['success'] is False
        assert 'No pending verification' in result['error']

class TestRegistrationFunction:
    '''Test suite for the register_user function'''

    def test_register_user_success(self):
        '''Test successful user registration'''
        valid_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'terms_accepted': True
        }

        result = register_user(valid_data)

        assert result['success'] is True
        assert 'user_id' in result
        assert result['user']['username'] == 'testuser123'
        assert result['user']['email'] == 'test@example.com'

    def test_register_user_validation_failure(self):
        '''Test user registration with validation errors'''
        invalid_data = {
            'username': 'a',  # Too short
            'email': 'invalid',  # Invalid format
            'password': 'weak',  # Too weak
            'confirm_password': 'different',  # Doesn't match
            'first_name': '',  # Empty
            'last_name': 'User',
            'age': 12,  # Too young
            'terms_accepted': False  # Not accepted
        }

        result = register_user(invalid_data)

        assert result['success'] is False
        assert 'errors' in result
        assert len(result['errors']) > 0

# Performance tests
class TestRegistrationPerformance:
    '''Performance tests for registration system'''

    def test_registration_performance(self):
        '''Test registration performance with valid data'''
        import time

        valid_data = {
            'username': 'perftest123',
            'email': 'perf@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'Performance',
            'last_name': 'Test',
            'age': 25,
            'terms_accepted': True
        }

        start_time = time.time()

        # Run registration 100 times
        for i in range(100):
            data = valid_data.copy()
            data['username'] = f'perftest{i}'
            data['email'] = f'perf{i}@example.com'

            try:
                user = UserRegistrationModel(**data)
                assert user.username == f'perftest{i}'
            except ValidationException:
                pass  # Expected for some iterations due to validation

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete 100 validations in less than 1 second
        assert execution_time < 1.0, f'Registration took {execution_time:.2f} seconds'

# Integration tests
class TestWebFrameworkIntegration:
    '''Integration tests for web framework endpoints'''

    @pytest.fixture
    def client(self):
        '''Create test client for FastAPI'''
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_fastapi_direct_registration(self, client):
        '''Test FastAPI direct registration endpoint'''
        valid_data = {
            'username': 'apitest123',
            'email': 'api@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'first_name': 'API',
            'last_name': 'Test',
            'age': 25,
            'terms_accepted': True
        }

        response = client.post('/register/direct', json=valid_data)

        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert 'user_id' in data

    def test_fastapi_registration_validation_error(self, client):
        '''Test FastAPI registration with validation errors'''
        invalid_data = {
            'username': 'a',  # Too short
            'email': 'invalid',  # Invalid format
            'password': 'weak',  # Too weak
            'confirm_password': 'different',  # Doesn't match
            'first_name': '',  # Empty
            'last_name': 'Test',
            'age': 12,  # Too young
            'terms_accepted': False  # Not accepted
        }

        response = client.post('/register/direct', json=invalid_data)

        assert response.status_code == 400
        data = response.json()
        assert data['success'] is False
        assert 'errors' in data

# Run tests with: pytest test_user_registration.py -v --cov=user_registration
```

## Best Practices

### 1. Validation Strategy

```python
# ✅ Good: Layered validation approach
class UserModel(ValidatedModel):
    username: str = field_validated(
        is_required(),           # Basic requirement
        min_length(3),          # Format validation
        custom(username_format), # Business rules
        custom(unique_username)  # External validation
    )

# ❌ Bad: Single complex validator
def complex_username_validator(value, context=None):
    # Don't combine all validation logic in one function
    if not value:
        return False
    if len(value) < 3:
        return False
    if not re.match(pattern, value):
        return False
    if value in existing_usernames:
        return False
    return True
```

### 2. Error Message Design

```python
# ✅ Good: Clear, actionable error messages
username: str = field_validated(
    is_required('Please enter a username'),
    min_length(3, 'Username must be at least 3 characters long'),
    custom(username_format_validator, 'Username must start with a letter and contain only letters, numbers, and underscores')
)

# ❌ Bad: Generic or unclear messages
username: str = field_validated(
    is_required('Required'),
    min_length(3, 'Too short'),
    custom(username_format_validator, 'Invalid format')
)
```

### 3. Performance Optimization

```python
# ✅ Good: Cache expensive validations
from functools import lru_cache

@lru_cache(maxsize=1000)
def check_username_availability(username: str) -> bool:
    # Expensive database operation
    return not database.username_exists(username)

# ✅ Good: Order validators by cost (cheap first)
username: str = field_validated(
    is_required(),              # Instant
    min_length(3),             # Very fast
    custom(format_validator),   # Fast regex
    custom(profanity_filter),   # Medium (list lookup)
    custom(unique_validator)    # Expensive (database)
)
```

### 4. Security Considerations

```python
# ✅ Good: Validate and sanitize all inputs
class SecureUserModel(ValidatedModel):
    username: str = field_validated(
        is_required(),
        min_length(3),
        max_length(20),
        custom(no_sql_injection),
        custom(no_xss_patterns),
        custom(no_profanity)
    )

    # ✅ Good: Strong password requirements
    password: str = field_validated(
        is_required(),
        min_length(8),
        is_strong_password(),
        custom(not_common_password),
        custom(not_contains_username)
    )

# ✅ Good: Rate limiting for registration attempts
class RegistrationService:
    def __init__(self):
        self.attempt_tracker = {}

    def check_rate_limit(self, ip_address: str) -> bool:
        # Implement rate limiting logic
        pass
```

### 5. Testing Strategy

```python
# ✅ Good: Comprehensive test coverage
class TestUserRegistration:

    # Test valid scenarios
    def test_valid_registration(self):
        pass

    # Test each validation rule
    def test_username_too_short(self):
        pass

    def test_invalid_email_format(self):
        pass

    # Test edge cases
    def test_boundary_values(self):
        pass

    # Test integration scenarios
    def test_web_framework_integration(self):
        pass

    # Test performance
    def test_registration_performance(self):
        pass
```

### 6. Documentation and Maintenance

```python
class UserRegistrationModel(ValidatedModel):
    '''
    User registration model with comprehensive validation

    This model implements the complete user registration workflow including:
    - Basic field validation (required, format, length)
    - Business rule validation (uniqueness, profanity filtering)
    - Security validation (password strength, injection prevention)

    Usage:
        user = UserRegistrationModel(**user_data)

    Raises:
        ValidationException: If any validation rules fail

    Example:
        >>> user_data = {
        ...     'username': 'johndoe',
        ...     'email': 'john@example.com',
        ...     'password': 'SecurePass123!',
        ...     'confirm_password': 'SecurePass123!',
        ...     'first_name': 'John',
        ...     'last_name': 'Doe',
        ...     'age': 25,
        ...     'terms_accepted': True
        ... }
        >>> user = UserRegistrationModel(**user_data)
        >>> print(user.username)
        'johndoe'
    '''

    # Document each field's validation rules
    username: str = field_validated(
        is_required('Username is required for account identification'),
        min_length(3, 'Username must be at least 3 characters for uniqueness'),
        max_length(20, 'Username cannot exceed 20 characters for display purposes'),
        custom(username_format_validator, 'Username format must follow platform standards'),
        custom(unique_username_validator, 'Username must be unique across the platform')
    )
```

This comprehensive user registration example demonstrates how PyValidX can be used to build robust, secure, and maintainable registration systems that handle real-world complexity while maintaining clean, readable code.
