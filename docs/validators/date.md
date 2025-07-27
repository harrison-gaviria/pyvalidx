# Date Validators

Los validadores de fecha proporcionan funcionalidades para validar fechas, formatos temporales y rangos de tiempo.

## is_date

Valida que el campo tenga un formato de fecha válido.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.date import is_date

class EventModel(ValidatedModel):
    start_date: str = field_validated(is_date())
    end_date: str = field_validated(is_date("%d/%m/%Y", "Use DD/MM/YYYY format"))

# Uso válido (formato por defecto: YYYY-MM-DD)
event = EventModel(
    start_date="2024-12-25",
    end_date="31/12/2024"
)

# Uso inválido
try:
    invalid_event = EventModel(start_date="invalid-date")
except ValidationException as e:
    print(e.validations)  # {'start_date': 'Invalid date format'}
```

### Parámetros
- `format` (str, opcional): Formato de fecha esperado. Por defecto: "%Y-%m-%d"
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Invalid date format"

### Formatos comunes:
- `%Y-%m-%d`: 2024-12-25
- `%d/%m/%Y`: 25/12/2024
- `%m/%d/%Y`: 12/25/2024
- `%Y-%m-%d %H:%M:%S`: 2024-12-25 14:30:00

---

## is_future_date

Valida que la fecha esté en el futuro.

```python
from pyvalidx.date import is_future_date

class ReservationModel(ValidatedModel):
    check_in: str = field_validated(is_future_date())
    check_out: str = field_validated(
        is_future_date("%d/%m/%Y", "Check-out must be a future date in DD/MM/YYYY format")
    )

# Uso válido
from datetime import datetime, timedelta
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

reservation = ReservationModel(
    check_in=tomorrow,
    check_out="25/12/2024"
)

# Uso inválido
try:
    past_reservation = ReservationModel(check_in="2020-01-01")
except ValidationException as e:
    print(e.validations)  # {'check_in': 'Date must be in the future'}
```

### Parámetros
- `format` (str, opcional): Formato de fecha esperado. Por defecto: "%Y-%m-%d"
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Date must be in the future"

---

## is_past_date

Valida que la fecha esté en el pasado.

```python
from pyvalidx.date import is_past_date

class HistoryEventModel(ValidatedModel):
    birth_date: str = field_validated(is_past_date())
    graduation_date: str = field_validated(
        is_past_date("%m/%d/%Y", "Graduation date must be in the past")
    )

# Uso válido
history = HistoryEventModel(
    birth_date="1990-05-15",
    graduation_date="12/20/2015"
)

# Uso inválido
try:
    future_history = HistoryEventModel(birth_date="2030-01-01")
except ValidationException as e:
    print(e.validations)  # {'birth_date': 'Date must be in the past'}
```

### Parámetros
- `format` (str, opcional): Formato de fecha esperado. Por defecto: "%Y-%m-%d"
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Date must be in the past"

---

## is_today

Valida que la fecha sea exactamente hoy.

```python
from pyvalidx.date import is_today

class DailyReportModel(ValidatedModel):
    report_date: str = field_validated(is_today())
    submission_date: str = field_validated(
        is_today("%d-%m-%Y", "Report must be submitted today")
    )

# Uso válido
from datetime import datetime
today = datetime.now().strftime("%Y-%m-%d")

report = DailyReportModel(
    report_date=today,
    submission_date=datetime.now().strftime("%d-%m-%Y")
)

# Uso inválido
try:
    wrong_report = DailyReportModel(report_date="2024-01-01")
except ValidationException as e:
    print(e.validations)  # {'report_date': 'Date must be today'}
```

### Parámetros
- `format` (str, opcional): Formato de fecha esperado. Por defecto: "%Y-%m-%d"
- `message` (str, opcional): Mensaje de error personalizado. Por defecto: "Date must be today"

---

## Ejemplo Completo: Sistema de Reservas

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.date import is_date, is_future_date
from datetime import datetime, timedelta

class HotelReservationModel(ValidatedModel):
    guest_name: str = field_validated(is_required("Guest name is required"))
    
    check_in_date: str = field_validated(
        is_required("Check-in date is required"),
        is_date("%Y-%m-%d", "Check-in date must be in YYYY-MM-DD format"),
        is_future_date("%Y-%m-%d", "Check-in date must be in the future")
    )
    
    check_out_date: str = field_validated(
        is_required("Check-out date is required"),
        is_date("%Y-%m-%d", "Check-out date must be in YYYY-MM-DD format"),
        is_future_date("%Y-%m-%d", "Check-out date must be in the future")
    )

# Uso válido
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

reservation = HotelReservationModel(
    guest_name="John Doe",
    check_in_date=tomorrow,
    check_out_date=next_week
)
```

---

## Ejemplo: Validación de Fechas de Nacimiento

```python
from pyvalidx.date import is_past_date
from pyvalidx.numeric import min_value, max_value
from datetime import datetime

class PersonModel(ValidatedModel):
    name: str = field_validated(is_required())
    birth_date: str = field_validated(
        is_required("Birth date is required"),
        is_date("%Y-%m-%d", "Birth date must be in YYYY-MM-DD format"),
        is_past_date("%Y-%m-%d", "Birth date must be in the past")
    )
    
    @property
    def age(self) -> int:
        birth = datetime.strptime(self.birth_date, "%Y-%m-%d")
        today = datetime.now()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

# Uso
person = PersonModel(
    name="Alice Smith",
    birth_date="1990-03-15"
)
print(f"{person.name} is {person.age} years old")
```

---

## Ejemplo: Validación de Eventos con Múltiples Fechas

```python
class ConferenceModel(ValidatedModel):
    title: str = field_validated(is_required())
    
    registration_deadline: str = field_validated(
        is_date("%Y-%m-%d"),
        is_future_date("%Y-%m-%d", "Registration deadline must be in the future")
    )
    
    event_start: str = field_validated(
        is_date("%Y-%m-%d"),
        is_future_date("%Y-%m-%d", "Event start date must be in the future")
    )
    
    event_end: str = field_validated(
        is_date("%Y-%m-%d"),
        is_future_date("%Y-%m-%d", "Event end date must be in the future")
    )

# Uso
from datetime import datetime, timedelta

conference = ConferenceModel(
    title="Python Conference 2024",
    registration_deadline=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
    event_start=(datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
    event_end=(datetime.now() + timedelta(days=63)).strftime("%Y-%m-%d")
)
```

---

## Formatos de Fecha Soportados

| Formato | Ejemplo | Descripción |
|---------|---------|-------------|
| `%Y-%m-%d` | 2024-12-25 | Año-Mes-Día (ISO) |
| `%d/%m/%Y` | 25/12/2024 | Día/Mes/Año (Europeo) |
| `%m/%d/%Y` | 12/25/2024 | Mes/Día/Año (Americano) |
| `%Y-%m-%d %H:%M:%S` | 2024-12-25 14:30:00 | Fecha y hora completa |
| `%d-%m-%Y` | 25-12-2024 | Día-Mes-Año con guiones |
| `%Y/%m/%d` | 2024/12/25 | Año/Mes/Día con barras |

---

## Notas Importantes

- Los validadores de fecha retornan `True` si el valor es `None` (para campos opcionales)
- Las fechas se comparan usando `datetime.now()` al momento de la validación
- Si el formato de fecha es inválido, el validador retorna `False`
- Puedes combinar validadores de fecha con otros validadores para crear validaciones más complejas
- Para campos opcionales de fecha, considera usar `Optional[str]` en la anotación de tipo
