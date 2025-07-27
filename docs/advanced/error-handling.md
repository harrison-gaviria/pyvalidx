# Error Handling

PyValidX proporciona un sistema robusto de manejo de errores a través de la clase `ValidationException`, que permite capturar, procesar y responder a errores de validación de manera estructurada.

## ValidationException Básica

### Estructura de Errores

```python
from pyvalidx import ValidatedModel, field_validated, ValidationException
from pyvalidx.core import is_required, min_length
from pyvalidx.string import is_email

class UserModel(ValidatedModel):
    name: str = field_validated(
        is_required("Name is required"),
        min_length(2, "Name must be at least 2 characters")
    )
    email: str = field_validated(
        is_required("Email is required"),
        is_email("Invalid email format")
    )

# Capturar y examinar errores
try:
    user = UserModel(name="A", email="invalid-email")
except ValidationException as e:
    print("Status Code:", e.status_code)  # 400
    print("Validations:", e.validations)
    # {'name': 'Name must be at least 2 characters', 'email': 'Invalid email format'}
    
    # Obtener como diccionario
    error_dict = e.to_dict()
    print("Error Dict:", error_dict)
    
    # Obtener como JSON
    error_json = e.to_json()
    print("Error JSON:", error_json)
```

### Múltiples Errores por Campo

```python
class PasswordModel(ValidatedModel):
    password: str = field_validated(
        is_required("Password is required"),
        min_length(8, "Password must be at least 8 characters"),
        is_strong_password("Password must contain uppercase, lowercase, numbers and symbols")
    )

try:
    # Password que falla múltiples validaciones
    pwd_model = PasswordModel(password="123")
except ValidationException as e:
    print(e.validations)
    # {'password': 'Password must be at least 8 characters'}
    # Nota: Solo se reporta el primer error que falla
```

---

## Manejo Personalizado de Errores

### Custom Status Codes

```python
class ValidationException(Exception):
    def __init__(self, validations, status_code=400):
        # El status_code por defecto es 400, pero se puede personalizar
        pass

# Para crear errores con códigos específicos
def validate_admin_user(data):
    try:
        return AdminUserModel(**data)
    except ValidationException as e:
        # Re-lanzar con código 403 para errores de autorización
        if "admin_key" in e.validations:
            raise ValidationException(e.validations, status_code=403)
        raise  # Re-lanzar con código original
```

### Wrapper para Manejo de Errores

```python
from typing import Dict, Any, Tuple, Optional
import json

class ValidationErrorHandler:
    """Manejador centralizado de errores de validación"""
    
    @staticmethod
    def handle_validation_error(e: ValidationException) -> Dict[str, Any]:
        """Convierte ValidationException a formato estándar de respuesta"""
        return {
            "success": False,
            "status_code": e.status_code,
            "message": "Validation failed",
            "errors": e.validations,
            "error_count": len(e.validations)
        }
    
    @staticmethod
    def safe_validate(model_class, data: Dict[str, Any]) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        """Validación segura que retorna tupla (modelo, error)"""
        try:
            model = model_class(**data)
            return model, None
        except ValidationException as e:
            return None, ValidationErrorHandler.handle_validation_error(e)
    
    @staticmethod
    def validate_or_raise_http_error(model_class, data: Dict[str, Any]):
        """Para uso en APIs web - convierte a formato HTTP"""
        try:
            return model_class(**data)
        except ValidationException as e:
            # Formato compatible con FastAPI/Flask
            http_error = {
                "detail": e.validations,
                "status_code": e.status_code
            }
            raise HTTPException(
                status_code=e.status_code,
                detail=http_error["detail"]
            )

# Uso del handler
class UserRegistrationModel(ValidatedModel):
    username: str = field_validated(is_required(), min_length(3))
    email: str = field_validated(is_required(), is_email())

# Validación segura
user_data = {"username": "ab", "email": "invalid"}
user, error = ValidationErrorHandler.safe_validate(UserRegistrationModel, user_data)

if error:
    print(json.dumps(error, indent=2))
    # {
    #   "success": false,
    #   "status_code": 400,
    #   "message": "Validation failed",
    #   "errors": {
    #     "username": "Must have at least 3 characters",
    #     "email": "Invalid email format"
    #   },
    #   "error_count": 2
    # }
```

---

## Errores Contextuales y Debugging

### Información de Debug en Errores

```python
class DebugValidationException(ValidationException):
    """ValidationException extendida con información de debug"""
    
    def __init__(self, validations, status_code=400, debug_info=None):
        super().__init__(validations, status_code)
        self.debug_info = debug_info or {}
    
    def to_dict(self):
        result = super().to_dict()
        if self.debug_info:
            result["debug_info"] = self.debug_info
        return result

def debug_validator(validator_func, field_name="unknown"):
    """Wrapper que añade información de debug a validadores"""
    def wrapper(value, context=None):
        import time
        start_time = time.time()
        
        try:
            result = validator_func(value, context)
            end_time = time.time()
            
            # Información de debug
            debug_info = {
                "field_name": field_name,
                "validation_time_ms": round((end_time - start_time) * 1000, 2),
                "input_value": str(value)[:100],  # Primeros 100 caracteres
                "context_keys": list(context.keys()) if context else []
            }
            
            if not result:
                # Si la validación falla, incluir debug info
                wrapper.__debug_info__ = debug_info
            
            return result
            
        except Exception as e:
            end_time = time.time()
            debug_info = {
                "field_name": field_name,
                "validation_time_ms": round((end_time - start_time) * 1000, 2),
                "exception": str(e),
                "input_value": str(value)[:100]
            }
            wrapper.__debug_info__ = debug_info
            return False
    
    wrapper.__message__ = getattr(validator_func, '__message__', 'Validation failed')
    return wrapper

# Modelo con debug
class DebugUserModel(ValidatedModel):
    email: str = field_validated(
        custom(debug_validator(is_email(), "email"))
    )
```

### Logging de Errores de Validación

```python
import logging
from datetime import datetime

class ValidationLogger:
    """Logger especializado para errores de validación"""
    
    def __init__(self, logger_name="pyvalidx"):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_validation_error(self, model_class, data, exception: ValidationException):
        """Log detallado de errores de validación"""
        self.logger.error(
            f"Validation failed for {model_class.__name__}: "
            f"Fields with errors: {list(exception.validations.keys())}"
        )
        
        for field, error in exception.validations.items():
            self.logger.error(f"  {field}: {error}")
        
        # Log de datos de entrada (sin información sensible)
        safe_data = self._sanitize_data(data)
        self.logger.debug(f"Input data: {safe_data}")
    
    def _sanitize_data(self, data):
        """Remover información sensible de los logs"""
        sensitive_fields = {'password', 'card_number', 'ssn', 'api_key'}
        
        sanitized = {}
        for key, value in data.items():
            if key.lower() in sensitive_fields:
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = str(value)[:100]  # Truncar valores largos
        
        return sanitized

# Uso del logger
validation_logger = ValidationLogger()

def safe_create_user(user_data):
    try:
        return UserModel(**user_data)
    except ValidationException as e:
        validation_logger.log_validation_error(UserModel, user_data, e)
        raise  # Re-lanzar después de loggear
```

---

## Manejo de Errores en Aplicaciones Web

### Integración con FastAPI

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    """Handler global para ValidationException en FastAPI"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": "Validation failed",
            "errors": exc.validations,
            "status_code": exc.status_code
        }
    )

@app.post("/users/")
async def create_user(user_data: dict):
    # La ValidationException será capturada automáticamente
    user = UserModel(**user_data)
    return {"message": "User created", "user": user.model_dump()}

# Uso:
# POST /users/ con datos inválidos retornará automáticamente error 400
```

### Integración con Flask

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.errorhandler(ValidationException)
def handle_validation_error(e):
    """Handler global para ValidationException en Flask"""
    return jsonify(e.to_dict()), e.status_code

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    
    # La ValidationException será capturada automáticamente
    user = UserModel(**user_data)
    return jsonify({"message": "User created", "user": user.model_dump()})

# Uso:
# POST /users con datos inválidos retornará automáticamente error 400
```

---

## Patrones Avanzados de Manejo de Errores

### Acumulación de Errores de Múltiples Modelos

```python
class BatchValidationResult:
    """Resultado de validación por lotes"""
    
    def __init__(self):
        self.valid_items = []
        self.invalid_items = []
        self.error_summary = {}
    
    def add_valid(self, index, item):
        self.valid_items.append({"index": index, "item": item})
    
    def add_invalid(self, index, data, errors):
        self.invalid_items.append({
            "index": index,
            "data": data,
            "errors": errors
        })
        
        # Acumular errores por campo
        for field, error in errors.items():
            if field not in self.error_summary:
                self.error_summary[field] = []
            self.error_summary[field].append(f"Row {index}: {error}")
    
    @property
    def has_errors(self):
        return len(self.invalid_items) > 0
    
    def to_dict(self):
        return {
            "valid_count": len(self.valid_items),
            "invalid_count": len(self.invalid_items),
            "valid_items": self.valid_items,
            "invalid_items": self.invalid_items,
            "error_summary": self.error_summary
        }

def batch_validate(model_class, data_list):
    """Validar una lista de elementos y acumular errores"""
    result = BatchValidationResult()
    
    for index, data in enumerate(data_list):
        try:
            item = model_class(**data)
            result.add_valid(index, item.model_dump())
        except ValidationException as e:
            result.add_invalid(index, data, e.validations)
    
    return result

# Uso
users_data = [
    {"name": "John", "email": "john@example.com"},
    {"name": "A", "email": "invalid"},  # Error
    {"name": "Jane", "email": "jane@example.com"},
    {"name": "", "email": ""}  # Error
]

batch_result = batch_validate(UserModel, users_data)
print(f"Valid: {batch_result.valid_count}, Invalid: {batch_result.invalid_count}")
```

### Retry con Backoff para Validaciones Externas

```python
import time
import random

def retry_validation(max_retries=3, backoff_factor=2):
    """Decorator para reintentar validaciones que dependen de servicios externos"""
    def decorator(validator_func):
        def wrapper(value, context=None):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return validator_func(value, context)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = backoff_factor ** attempt + random.uniform(0, 1)
                        time.sleep(delay)
                    continue
            
            # Si todos los intentos fallan, retornar False
            return False
        
        wrapper.__message__ = getattr(validator_func, '__message__', 'Validation failed')
        return wrapper
    return decorator

# Validador que consulta servicio externo con retry
@retry_validation(max_retries=3)
def validate_with_external_service(value, context=None):
    """Ejemplo de validador que consulta un servicio externo"""
    if value is None:
        return True
    
    # Simular llamada a servicio externo que puede fallar
    import requests
    try:
        response = requests.get(f"https://api.example.com/validate/{value}", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        raise  # Se reintentará automáticamente

class ExternalValidatedModel(ValidatedModel):
    external_id: str = field_validated(
        custom(validate_with_external_service, "External validation failed")
    )
```

El manejo robusto de errores es crucial para crear aplicaciones confiables que puedan diagnosticar y responder apropiadamente a problemas de validación, proporcionando información útil tanto para desarrolladores como para usuarios finales.
