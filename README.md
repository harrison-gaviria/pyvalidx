# pyvalidx

`pyvalidx` es un paquete de validaciones personalizadas para campos en modelos Pydantic, usando funciones reutilizables y una arquitectura clara.

## Características

- Validaciones de texto, números, fechas, tipos y más.
- Funciones como `is_required`, `min_length`, `is_email`, etc.
- Compatible con `pydantic.BaseModel`
- Fácil de extender con validadores personalizados.

## Ejemplo de uso

```python
from pyvalidx import ValidatedModel, field_validated, is_email, min_length

class User(ValidatedModel):
    email: str = field_validated(is_email(), min_length(5))
