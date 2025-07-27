# API Validation Example

This example demonstrates how to use PyValidX for comprehensive API request and response validation in different scenarios.

## REST API Endpoints

### User Management API

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length, max_length, is_in, same_as
from pyvalidx.string import is_email, is_strong_password
from pyvalidx.numeric import min_value, max_value, is_positive
from pyvalidx.exception import ValidationException
from typing import Optional, List
from datetime import datetime
import uuid

# Request Models
class CreateUserRequest(ValidatedModel):
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

    first_name: str = field_validated(
        is_required('First name is required'),
        min_length(2, 'First name must be at least 2 characters')
    )

    last_name: str = field_validated(
        is_required('Last name is required'),
        min_length(2, 'Last name must be at least 2 characters')
    )

    role: str = field_validated(
        is_required('Role is required'),
        is_in(['user', 'admin', 'moderator'], 'Invalid role specified')
    )

class UpdateUserRequest(ValidatedModel):
    first_name: Optional[str] = field_validated(
        min_length(2, 'First name must be at least 2 characters')
    )

    last_name: Optional[str] = field_validated(
        min_length(2, 'Last name must be at least 2 characters')
    )

    email: Optional[str] = field_validated(
        is_email('Please provide a valid email address')
    )

    role: Optional[str] = field_validated(
        is_in(['user', 'admin', 'moderator'], 'Invalid role specified')
    )

class ChangePasswordRequest(ValidatedModel):
    current_password: str = field_validated(
        is_required('Current password is required')
    )

    new_password: str = field_validated(
        is_required('New password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password('Password must contain uppercase, lowercase, numbers and special characters')
    )

    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('new_password', 'Passwords must match')
    )

# Response Models
class UserResponse(ValidatedModel):
    id: str = field_validated(is_required())
    username: str = field_validated(is_required())
    email: str = field_validated(is_required(), is_email())
    first_name: str = field_validated(is_required())
    last_name: str = field_validated(is_required())
    role: str = field_validated(is_required())
    created_at: str = field_validated(is_required())
    updated_at: str = field_validated(is_required())
    is_active: bool = True

class ApiResponse(ValidatedModel):
    success: bool = field_validated(is_required())
    message: str = field_validated(is_required())
    data: Optional[dict] = None
    errors: Optional[dict] = None
    status_code: int = field_validated(
        is_required(),
        min_value(100, 'Invalid HTTP status code'),
        max_value(599, 'Invalid HTTP status code')
    )

# API Service Class
class UserApiService:
    '''Service class for user API operations'''

    def __init__(self):
        self.users_db = {}  # Simulated database

    def create_user(self, request_data: dict) -> dict:
        '''Create a new user'''
        try:
            # Validate request
            request = CreateUserRequest(**request_data)

            # Check if username/email already exists
            if self._username_exists(request.username):
                return self._error_response(
                    'Username already exists',
                    {'username': 'This username is already taken'},
                    400
                )

            if self._email_exists(request.email):
                return self._error_response(
                    'Email already exists',
                    {'email': 'This email is already registered'},
                    400
                )

            # Create user
            user_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()

            user_data = {
                'id': user_id,
                'username': request.username,
                'email': request.email,
                'first_name': request.first_name,
                'last_name': request.last_name,
                'role': request.role,
                'created_at': current_time,
                'updated_at': current_time,
                'is_active': True
            }

            # Validate response data
            user_response = UserResponse(**user_data)

            # Store in 'database'
            self.users_db[user_id] = user_data

            return self._success_response(
                'User created successfully',
                user_response.model_dump(),
                201
            )

        except ValidationException as e:
            return self._error_response(
                'Validation failed',
                e.validations,
                400
            )

    def get_user(self, user_id: str) -> dict:
        '''Get user by ID'''
        if user_id not in self.users_db:
            return self._error_response(
                'User not found',
                {'user_id': 'User does not exist'},
                404
            )

        user_data = self.users_db[user_id]
        user_response = UserResponse(**user_data)

        return self._success_response(
            'User retrieved successfully',
            user_response.model_dump(),
            200
        )

    def update_user(self, user_id: str, request_data: dict) -> dict:
        '''Update user information'''
        try:
            # Validate request
            request = UpdateUserRequest(**request_data)

            if user_id not in self.users_db:
                return self._error_response(
                    'User not found',
                    {'user_id': 'User does not exist'},
                    404
                )

            # Check email uniqueness if email is being updated
            if request.email and request.email != self.users_db[user_id]['email']:
                if self._email_exists(request.email):
                    return self._error_response(
                        'Email already exists',
                        {'email': 'This email is already registered'},
                        400
                    )

            # Update user data
            user_data = self.users_db[user_id].copy()

            if request.first_name:
                user_data['first_name'] = request.first_name
            if request.last_name:
                user_data['last_name'] = request.last_name
            if request.email:
                user_data['email'] = request.email
            if request.role:
                user_data['role'] = request.role

            user_data['updated_at'] = datetime.now().isoformat()

            # Validate updated data
            user_response = UserResponse(**user_data)

            # Store updated data
            self.users_db[user_id] = user_data

            return self._success_response(
                'User updated successfully',
                user_response.model_dump(),
                200
            )

        except ValidationException as e:
            return self._error_response(
                'Validation failed',
                e.validations,
                400
            )

    def change_password(self, user_id: str, request_data: dict) -> dict:
        '''Change user password'''
        try:
            # Validate request
            request = ChangePasswordRequest(**request_data)

            if user_id not in self.users_db:
                return self._error_response(
                    'User not found',
                    {'user_id': 'User does not exist'},
                    404
                )

            # In a real application, you would verify the current password
            # For this example, we'll assume it's correct

            return self._success_response(
                'Password changed successfully',
                {'message': 'Password has been updated'},
                200
            )

        except ValidationException as e:
            return self._error_response(
                'Validation failed',
                e.validations,
                400
            )

    def list_users(self, page: int = 1, limit: int = 10, role: Optional[str] = None) -> dict:
        '''List users with pagination and filtering'''
        try:
            # Validate pagination parameters
            if page < 1:
                return self._error_response(
                    'Invalid page number',
                    {'page': 'Page number must be greater than 0'},
                    400
                )

            if limit < 1 or limit > 100:
                return self._error_response(
                    'Invalid limit',
                    {'limit': 'Limit must be between 1 and 100'},
                    400
                )

            if role and role not in ['user', 'admin', 'moderator']:
                return self._error_response(
                    'Invalid role filter',
                    {'role': 'Role must be user, admin, or moderator'},
                    400
                )

            # Filter users
            users = list(self.users_db.values())

            if role:
                users = [user for user in users if user['role'] == role]

            # Paginate
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_users = users[start_idx:end_idx]

            # Validate each user response
            validated_users = []
            for user_data in paginated_users:
                user_response = UserResponse(**user_data)
                validated_users.append(user_response.model_dump())

            response_data = {
                'users': validated_users,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': len(users),
                    'pages': (len(users) + limit - 1) // limit
                }
            }

            return self._success_response(
                'Users retrieved successfully',
                response_data,
                200
            )

        except ValidationException as e:
            return self._error_response(
                'Validation failed',
                e.validations,
                400
            )

    def _username_exists(self, username: str) -> bool:
        '''Check if username already exists'''
        return any(user['username'] == username for user in self.users_db.values())

    def _email_exists(self, email: str) -> bool:
        '''Check if email already exists'''
        return any(user['email'] == email for user in self.users_db.values())

    def _success_response(self, message: str, data: dict, status_code: int) -> dict:
        '''Create success response'''
        response = ApiResponse(
            success=True,
            message=message,
            data=data,
            status_code=status_code
        )
        return response.model_dump()

    def _error_response(self, message: str, errors: dict, status_code: int) -> dict:
        '''Create error response'''
        response = ApiResponse(
            success=False,
            message=message,
            errors=errors,
            status_code=status_code
        )
        return response.model_dump()

# Usage examples
api_service = UserApiService()

# Create user
create_request = {
    'username': 'johndoe',
    'email': 'john.doe@example.com',
    'password': 'SecurePass123!',
    'first_name': 'John',
    'last_name': 'Doe',
    'role': 'user'
}

result = api_service.create_user(create_request)
print('Create user result:', result)

# Get user (assuming user was created)
if result['success']:
    user_id = result['data']['id']
    get_result = api_service.get_user(user_id)
    print('Get user result:', get_result)
```

## Product Catalog API

```python
from pyvalidx.numeric import is_positive
from pyvalidx.types import is_list
from decimal import Decimal

class CreateProductRequest(ValidatedModel):
    name: str = field_validated(
        is_required('Product name is required'),
        min_length(3, 'Product name must be at least 3 characters'),
        max_length(100, 'Product name cannot exceed 100 characters')
    )

    description: str = field_validated(
        is_required('Description is required'),
        min_length(10, 'Description must be at least 10 characters'),
        max_length(1000, 'Description cannot exceed 1000 characters')
    )

    price: float = field_validated(
        is_required('Price is required'),
        is_positive('Price must be positive')
    )

    category: str = field_validated(
        is_required('Category is required'),
        is_in([
            'Electronics',
            'Clothing',
            'Books',
            'Home & Garden',
            'Sports',
            'Toys',
            'Health & Beauty'
        ], 'Invalid category')
    )

    tags: List[str] = field_validated(
        is_list('Tags must be a list')
    )

    stock_quantity: int = field_validated(
        is_required('Stock quantity is required'),
        min_value(0, 'Stock quantity cannot be negative')
    )

    sku: str = field_validated(
        is_required('SKU is required'),
        min_length(3, 'SKU must be at least 3 characters'),
        max_length(20, 'SKU cannot exceed 20 characters')
    )

    is_active: bool = True

class UpdateProductRequest(ValidatedModel):
    name: Optional[str] = field_validated(
        min_length(3, 'Product name must be at least 3 characters'),
        max_length(100, 'Product name cannot exceed 100 characters')
    )

    description: Optional[str] = field_validated(
        min_length(10, 'Description must be at least 10 characters'),
        max_length(1000, 'Description cannot exceed 1000 characters')
    )

    price: Optional[float] = field_validated(
        is_positive('Price must be positive')
    )

    category: Optional[str] = field_validated(
        is_in([
            'Electronics',
            'Clothing',
            'Books',
            'Home & Garden',
            'Sports',
            'Toys',
            'Health & Beauty'
        ], 'Invalid category')
    )

    tags: Optional[List[str]] = field_validated(
        is_list('Tags must be a list')
    )

    stock_quantity: Optional[int] = field_validated(
        min_value(0, 'Stock quantity cannot be negative')
    )

    is_active: Optional[bool] = None

class ProductResponse(ValidatedModel):
    id: str = field_validated(is_required())
    name: str = field_validated(is_required())
    description: str = field_validated(is_required())
    price: float = field_validated(is_required(), is_positive())
    category: str = field_validated(is_required())
    tags: List[str] = field_validated(is_required())
    stock_quantity: int = field_validated(is_required())
    sku: str = field_validated(is_required())
    is_active: bool = field_validated(is_required())
    created_at: str = field_validated(is_required())
    updated_at: str = field_validated(is_required())

class ProductSearchRequest(ValidatedModel):
    query: Optional[str] = field_validated(
        min_length(2, 'Search query must be at least 2 characters')
    )

    category: Optional[str] = field_validated(
        is_in([
            'Electronics',
            'Clothing',
            'Books',
            'Home & Garden',
            'Sports',
            'Toys',
            'Health & Beauty'
        ], 'Invalid category')
    )

    min_price: Optional[float] = field_validated(
        is_positive('Minimum price must be positive')
    )

    max_price: Optional[float] = field_validated(
        is_positive('Maximum price must be positive')
    )

    in_stock_only: bool = False

    page: int = field_validated(
        min_value(1, 'Page must be greater than 0')
    )

    limit: int = field_validated(
        min_value(1, 'Limit must be greater than 0'),
        max_value(100, 'Limit cannot exceed 100')
    )

    sort_by: str = field_validated(
        is_in(['name', 'price', 'created_at', 'stock_quantity'], 'Invalid sort field')
    )

    sort_order: str = field_validated(
        is_in(['asc', 'desc'], 'Sort order must be 'asc' or 'desc'')
    )

class ProductApiService:
    '''Service class for product API operations'''

    def __init__(self):
        self.products_db = {}

    def create_product(self, request_data: dict) -> dict:
        '''Create a new product'''
        try:
            request = CreateProductRequest(**request_data)

            # Check SKU uniqueness
            if self._sku_exists(request.sku):
                return self._error_response(
                    'SKU already exists',
                    {'sku': 'This SKU is already in use'},
                    400
                )

            # Create product
            product_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()

            product_data = {
                'id': product_id,
                'name': request.name,
                'description': request.description,
                'price': request.price,
                'category': request.category,
                'tags': request.tags,
                'stock_quantity': request.stock_quantity,
                'sku': request.sku,
                'is_active': request.is_active,
                'created_at': current_time,
                'updated_at': current_time
            }

            product_response = ProductResponse(**product_data)
            self.products_db[product_id] = product_data

            return self._success_response(
                'Product created successfully',
                product_response.model_dump(),
                201
            )

        except ValidationException as e:
            return self._error_response(
                'Validation failed',
                e.validations,
                400
            )

    def search_products(self, search_params: dict) -> dict:
        '''Search products with filters and pagination'''
        try:
            # Set defaults
            search_params.setdefault('page', 1)
            search_params.setdefault('limit', 10)
            search_params.setdefault('sort_by', 'created_at')
            search_params.setdefault('sort_order', 'desc')

            search_request = ProductSearchRequest(**search_params)

            # Filter products
            products = list(self.products_db.values())

            # Apply filters
            if search_request.query:
                query_lower = search_request.query.lower()
                products = [
                    p for p in products
                    if query_lower in p['name'].lower() or query_lower in p['description'].lower()
                ]

            if search_request.category:
                products = [p for p in products if p['category'] == search_request.category]

            if search_request.min_price:
                products = [p for p in products if p['price'] >= search_request.min_price]

            if search_request.max_price:
                products = [p for p in products if p['price'] <= search_request.max_price]

            if search_request.in_stock_only:
                products = [p for p in products if p['stock_quantity'] > 0]

            # Sort products
            reverse = search_request.sort_order == 'desc'
            products.sort(key=lambda x: x[search_request.sort_by], reverse=reverse)

            # Paginate
            start_idx = (search_request.page - 1) * search_request.limit
            end_idx = start_idx + search_request.limit
            paginated_products = products[start_idx:end_idx]

            # Validate responses
            validated_products = []
            for product_data in paginated_products:
                product_response = ProductResponse(**product_data)
                validated_products.append(product_response.model_dump())

            response_data = {
                'products': validated_products,
                'pagination': {
                    'page': search_request.page,
                    'limit': search_request.limit,
                    'total': len(products),
                    'pages': (len(products) + search_request.limit - 1) // search_request.limit
                },
                'filters': {
                    'query': search_request.query,
                    'category': search_request.category,
                    'min_price': search_request.min_price,
                    'max_price': search_request.max_price,
                    'in_stock_only': search_request.in_stock_only
                }
            }

            return self._success_response(
                'Products retrieved successfully',
                response_data,
                200
            )

        except ValidationException as e:
            return self._error_response(
                'Validation failed',
                e.validations,
                400
            )

    def _sku_exists(self, sku: str) -> bool:
        '''Check if SKU already exists'''
        return any(product['sku'] == sku for product in self.products_db.values())

    def _success_response(self, message: str, data: dict, status_code: int) -> dict:
        '''Create success response'''
        response = ApiResponse(
            success=True,
            message=message,
            data=data,
            status_code=status_code
        )
        return response.model_dump()

    def _error_response(self, message: str, errors: dict, status_code: int) -> dict:
        '''Create error response'''
        response = ApiResponse(
            success=False,
            message=message,
            errors=errors,
            status_code=status_code
        )
        return response.model_dump()
```

## FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title='PyValidX API Example',
    description='API validation example using PyValidX',
    version='1.0.0'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Initialize services
user_service = UserApiService()
product_service = ProductApiService()

# Exception handler for ValidationException
@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'message': 'Validation failed',
            'errors': exc.validations
        }
    )

# User endpoints
@app.post('/users', status_code=201)
async def create_user(user_data: dict):
    '''Create a new user'''
    result = user_service.create_user(user_data)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

@app.get('/users/{user_id}')
async def get_user(user_id: str):
    '''Get user by ID'''
    result = user_service.get_user(user_id)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

@app.put('/users/{user_id}')
async def update_user(user_id: str, user_data: dict):
    '''Update user information'''
    result = user_service.update_user(user_id, user_data)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

@app.post('/users/{user_id}/change-password')
async def change_password(user_id: str, password_data: dict):
    '''Change user password'''
    result = user_service.change_password(user_id, password_data)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

@app.get('/users')
async def list_users(
    page: int = Query(1, ge=1, description='Page number'),
    limit: int = Query(10, ge=1, le=100, description='Items per page'),
    role: Optional[str] = Query(None, description='Filter by role')
):
    '''List users with pagination and filtering'''
    result = user_service.list_users(page=page, limit=limit, role=role)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

# Product endpoints
@app.post('/products', status_code=201)
async def create_product(product_data: dict):
    '''Create a new product'''
    result = product_service.create_product(product_data)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

@app.get('/products/search')
async def search_products(
    query: Optional[str] = Query(None, description='Search query'),
    category: Optional[str] = Query(None, description='Product category'),
    min_price: Optional[float] = Query(None, ge=0, description='Minimum price'),
    max_price: Optional[float] = Query(None, ge=0, description='Maximum price'),
    in_stock_only: bool = Query(False, description='Show only in-stock products'),
    page: int = Query(1, ge=1, description='Page number'),
    limit: int = Query(10, ge=1, le=100, description='Items per page'),
    sort_by: str = Query('created_at', description='Sort field'),
    sort_order: str = Query('desc', description='Sort order')
):
    '''Search products with filters and pagination'''
    search_params = {
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock_only': in_stock_only,
        'page': page,
        'limit': limit,
        'sort_by': sort_by,
        'sort_order': sort_order
    }

    result = product_service.search_products(search_params)

    if not result['success']:
        raise HTTPException(
            status_code=result['status_code'],
            detail=result
        )

    return result

# Health check endpoint
@app.get('/health')
async def health_check():
    '''Health check endpoint'''
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

## Flask Integration

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize services
user_service = UserApiService()
product_service = ProductApiService()

@app.errorhandler(ValidationException)
def handle_validation_error(e):
    '''Handle validation exceptions'''
    return jsonify(e.to_dict()), e.status_code

@app.errorhandler(404)
def handle_not_found(e):
    '''Handle 404 errors'''
    return jsonify({
        'success': False,
        'message': 'Endpoint not found',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def handle_internal_error(e):
    '''Handle internal server errors'''
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'status_code': 500
    }), 500

# User routes
@app.route('/users', methods=['POST'])
def create_user_flask():
    '''Create a new user'''
    user_data = request.get_json()

    if not user_data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'status_code': 400
        }), 400

    result = user_service.create_user(user_data)
    return jsonify(result), result['status_code']

@app.route('/users/<user_id>', methods=['GET'])
def get_user_flask(user_id):
    '''Get user by ID'''
    result = user_service.get_user(user_id)
    return jsonify(result), result['status_code']

@app.route('/users/<user_id>', methods=['PUT'])
def update_user_flask(user_id):
    '''Update user information'''
    user_data = request.get_json()

    if not user_data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'status_code': 400
        }), 400

    result = user_service.update_user(user_id, user_data)
    return jsonify(result), result['status_code']

@app.route('/users', methods=['GET'])
def list_users_flask():
    '''List users with pagination and filtering'''
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    role = request.args.get('role', None)

    result = user_service.list_users(page=page, limit=limit, role=role)
    return jsonify(result), result['status_code']

# Product routes
@app.route('/products', methods=['POST'])
def create_product_flask():
    '''Create a new product'''
    product_data = request.get_json()

    if not product_data:
        return jsonify({
            'success': False,
            'message': 'Request body is required',
            'status_code': 400
        }), 400

    result = product_service.create_product(product_data)
    return jsonify(result), result['status_code']

@app.route('/products/search', methods=['GET'])
def search_products_flask():
    '''Search products with filters and pagination'''
    search_params = {
        'query': request.args.get('query'),
        'category': request.args.get('category'),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float),
        'in_stock_only': request.args.get('in_stock_only', False, type=bool),
        'page': request.args.get('page', 1, type=int),
        'limit': request.args.get('limit', 10, type=int),
        'sort_by': request.args.get('sort_by', 'created_at'),
        'sort_order': request.args.get('sort_order', 'desc')
    }

    result = product_service.search_products(search_params)
    return jsonify(result), result['status_code']

@app.route('/health', methods=['GET'])
def health_check_flask():
    '''Health check endpoint'''
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Django REST Framework Integration

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse

class UserAPIView(APIView):
    '''User API view using PyValidX validation'''

    def __init__(self):
        super().__init__()
        self.user_service = UserApiService()

    def post(self, request):
        '''Create a new user'''
        result = self.user_service.create_user(request.data)
        return Response(result, status=result['status_code'])

    def get(self, request, user_id=None):
        '''Get user by ID or list users'''
        if user_id:
            result = self.user_service.get_user(user_id)
        else:
            page = request.query_params.get('page', 1)
            limit = request.query_params.get('limit', 10)
            role = request.query_params.get('role', None)

            try:
                page = int(page)
                limit = int(limit)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Invalid pagination parameters',
                    'status_code': 400
                }, status=400)

            result = self.user_service.list_users(page=page, limit=limit, role=role)

        return Response(result, status=result['status_code'])

    def put(self, request, user_id):
        '''Update user information'''
        result = self.user_service.update_user(user_id, request.data)
        return Response(result, status=result['status_code'])

class ProductAPIView(APIView):
    '''Product API view using PyValidX validation'''

    def __init__(self):
        super().__init__()
        self.product_service = ProductApiService()

    def post(self, request):
        '''Create a new product'''
        result = self.product_service.create_product(request.data)
        return Response(result, status=result['status_code'])

@api_view(['GET'])
def search_products_django(request):
    '''Search products endpoint'''
    product_service = ProductApiService()

    search_params = {
        'query': request.query_params.get('query'),
        'category': request.query_params.get('category'),
        'min_price': request.query_params.get('min_price'),
        'max_price': request.query_params.get('max_price'),
        'in_stock_only': request.query_params.get('in_stock_only', False),
        'page': request.query_params.get('page', 1),
        'limit': request.query_params.get('limit', 10),
        'sort_by': request.query_params.get('sort_by', 'created_at'),
        'sort_order': request.query_params.get('sort_order', 'desc')
    }

    # Convert string parameters to appropriate types
    try:
        if search_params['min_price']:
            search_params['min_price'] = float(search_params['min_price'])
        if search_params['max_price']:
            search_params['max_price'] = float(search_params['max_price'])
        search_params['page'] = int(search_params['page'])
        search_params['limit'] = int(search_params['limit'])
        search_params['in_stock_only'] = str(search_params['in_stock_only']).lower() == 'true'
    except (ValueError, TypeError):
        return Response({
            'success': False,
            'message': 'Invalid parameter types',
            'status_code': 400
        }, status=400)

    result = product_service.search_products(search_params)
    return Response(result, status=result['status_code'])
```

## API Testing

```python
import pytest
import requests
from unittest.mock import Mock

class TestUserAPI:
    '''Test cases for User API'''

    def setup_method(self):
        '''Setup test environment'''
        self.user_service = UserApiService()
        self.base_url = 'http://localhost:8000'

    def test_create_user_success(self):
        '''Test successful user creation'''
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user'
        }

        result = self.user_service.create_user(user_data)

        assert result['success'] is True
        assert result['status_code'] == 201
        assert result['data']['username'] == 'testuser'
        assert result['data']['email'] == 'test@example.com'

    def test_create_user_validation_error(self):
        '''Test user creation with validation errors'''
        invalid_user_data = {
            'username': 'te',  # Too short
            'email': 'invalid-email',  # Invalid format
            'password': 'weak',  # Too weak
            'first_name': '',  # Empty
            'last_name': 'User',
            'role': 'invalid_role'  # Invalid role
        }

        result = self.user_service.create_user(invalid_user_data)

        assert result['success'] is False
        assert result['status_code'] == 400
        assert 'username' in result['errors']
        assert 'email' in result['errors']
        assert 'password' in result['errors']
        assert 'first_name' in result['errors']
        assert 'role' in result['errors']

    def test_create_user_duplicate_username(self):
        '''Test user creation with duplicate username'''
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'user'
        }

        # Create first user
        result1 = self.user_service.create_user(user_data)
        assert result1['success'] is True

        # Try to create second user with same username
        user_data['email'] = 'different@example.com'
        result2 = self.user_service.create_user(user_data)

        assert result2['success'] is False
        assert result2['status_code'] == 400
        assert 'username' in result2['errors']

    def test_get_user_success(self):
        '''Test successful user retrieval'''
        # Create user first
        user_data = {
            'username': 'getuser',
            'email': 'getuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Get',
            'last_name': 'User',
            'role': 'user'
        }

        create_result = self.user_service.create_user(user_data)
        user_id = create_result['data']['id']

        # Get user
        get_result = self.user_service.get_user(user_id)

        assert get_result['success'] is True
        assert get_result['status_code'] == 200
        assert get_result['data']['id'] == user_id
        assert get_result['data']['username'] == 'getuser'

    def test_get_user_not_found(self):
        '''Test user retrieval with non-existent ID'''
        result = self.user_service.get_user('non-existent-id')

        assert result['success'] is False
        assert result['status_code'] == 404
        assert 'user_id' in result['errors']

class TestProductAPI:
    '''Test cases for Product API'''

    def setup_method(self):
        '''Setup test environment'''
        self.product_service = ProductApiService()

    def test_create_product_success(self):
        '''Test successful product creation'''
        product_data = {
            'name': 'Test Product',
            'description': 'This is a test product for validation',
            'price': 29.99,
            'category': 'Electronics',
            'tags': ['test', 'electronics', 'gadget'],
            'stock_quantity': 100,
            'sku': 'TEST001',
            'is_active': True
        }

        result = self.product_service.create_product(product_data)

        assert result['success'] is True
        assert result['status_code'] == 201
        assert result['data']['name'] == 'Test Product'
        assert result['data']['price'] == 29.99
        assert result['data']['sku'] == 'TEST001'

    def test_create_product_validation_error(self):
        '''Test product creation with validation errors'''
        invalid_product_data = {
            'name': 'Te',  # Too short
            'description': 'Short',  # Too short
            'price': -10,  # Negative price
            'category': 'InvalidCategory',  # Invalid category
            'tags': 'not_a_list',  # Should be list
            'stock_quantity': -5,  # Negative stock
            'sku': 'AB',  # Too short
        }

        result = self.product_service.create_product(invalid_product_data)

        assert result['success'] is False
        assert result['status_code'] == 400
        assert 'name' in result['errors']
        assert 'description' in result['errors']
        assert 'price' in result['errors']
        assert 'category' in result['errors']

    def test_search_products_success(self):
        '''Test successful product search'''
        # Create some test products first
        products = [
            {
                'name': 'Laptop Computer',
                'description': 'High-performance laptop for professionals',
                'price': 999.99,
                'category': 'Electronics',
                'tags': ['laptop', 'computer', 'professional'],
                'stock_quantity': 50,
                'sku': 'LAP001',
                'is_active': True
            },
            {
                'name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with precision tracking',
                'price': 29.99,
                'category': 'Electronics',
                'tags': ['mouse', 'wireless', 'ergonomic'],
                'stock_quantity': 200,
                'sku': 'MOU001',
                'is_active': True
            }
        ]

        for product_data in products:
            self.product_service.create_product(product_data)

        # Search products
        search_params = {
            'query': 'laptop',
            'category': 'Electronics',
            'min_price': 500,
            'max_price': 1500,
            'page': 1,
            'limit': 10,
            'sort_by': 'price',
            'sort_order': 'desc'
        }

        result = self.product_service.search_products(search_params)

        assert result['success'] is True
        assert result['status_code'] == 200
        assert len(result['data']['products']) >= 1
        assert result['data']['pagination']['page'] == 1
        assert result['data']['pagination']['limit'] == 10

# Integration tests with actual HTTP requests
class TestAPIIntegration:
    '''Integration tests for API endpoints'''

    @pytest.fixture(autouse=True)
    def setup(self):
        '''Setup for integration tests'''
        self.base_url = 'http://localhost:8000'
        # Note: These tests require the API server to be running

    def test_create_user_endpoint(self):
        '''Test user creation endpoint'''
        user_data = {
            'username': 'apitest',
            'email': 'apitest@example.com',
            'password': 'SecurePass123!',
            'first_name': 'API',
            'last_name': 'Test',
            'role': 'user'
        }

        response = requests.post(f'{self.base_url}/users', json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert data['data']['username'] == 'apitest'

    def test_search_products_endpoint(self):
        '''Test product search endpoint'''
        params = {
            'query': 'test',
            'category': 'Electronics',
            'page': 1,
            'limit': 5
        }

        response = requests.get(f'{self.base_url}/products/search', params=params)

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'products' in data['data']
        assert 'pagination' in data['data']

# Run tests: pytest test_api_validation.py -v
```

## Performance and Monitoring

```python
import time
import logging
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_performance(func):
    '''Decorator to monitor API performance'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            logger.info(f'{func.__name__} executed in {execution_time:.3f}s - Success')
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f'{func.__name__} failed in {execution_time:.3f}s - Error: {str(e)}')
            raise

    return wrapper

def validate_api_limits(func):
    '''Decorator to validate API rate limits'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Simple rate limiting logic (in production, use Redis or similar)
        # This is just for demonstration
        return func(*args, **kwargs)

    return wrapper

# Enhanced API service with monitoring
class MonitoredUserApiService(UserApiService):
    '''User API service with performance monitoring'''

    @monitor_performance
    @validate_api_limits
    def create_user(self, request_data: dict) -> dict:
        return super().create_user(request_data)

    @monitor_performance
    def get_user(self, user_id: str) -> dict:
        return super().get_user(user_id)

    @monitor_performance
    def list_users(self, page: int = 1, limit: int = 10, role: Optional[str] = None) -> dict:
        return super().list_users(page, limit, role)

# Usage example with monitoring
monitored_user_service = MonitoredUserApiService()

# This will log performance metrics
result = monitored_user_service.create_user({
    'username': 'monitored_user',
    'email': 'monitored@example.com',
    'password': 'SecurePass123!',
    'first_name': 'Monitored',
    'last_name': 'User',
    'role': 'user'
})
```

This comprehensive API validation example demonstrates:

- Complete CRUD operations with validation
- Request/response model validation
- Multiple web framework integrations (FastAPI, Flask, Django)
- Comprehensive error handling
- API testing strategies
- Performance monitoring
- Real-world API patterns

The example shows how PyValidX can be used to build robust, well-validated APIs that handle complex business logic while maintaining clean, maintainable code.
