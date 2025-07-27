# Date Validators

Date validators provide functionalities for validating dates and times in different formats.

## is_date

Validates that the field is a valid date in the specified format.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.date import is_date

class EventModel(ValidatedModel):
    event_date: str = field_validated(is_date())
    custom_date: str = field_validated(
        is_date('%d/%m/%Y', 'Date must be in DD/MM/YYYY format')
    )

# Valid usage
event = EventModel(
    event_date='2024-12-25',
    custom_date='25/12/2024'
)

# Invalid usage
try:
    invalid_event = EventModel(event_date='invalid-date')
except ValidationException as e:
    print(e.validations)  # {'event_date': 'Invalid date format'}
```

### Parameters
- `format` (str, optional): Expected date format. Default: '%Y-%m-%d'
- `message` (str, optional): Custom error message. Default: 'Invalid date format'

---

## is_future_date

Validates that the date is in the future.

```python
from pyvalidx.date import is_future_date

class AppointmentModel(ValidatedModel):
    appointment_date: str = field_validated(is_future_date())
    deadline: str = field_validated(
        is_future_date('%d-%m-%Y', 'Deadline must be in the future')
    )

# Valid usage
from datetime import datetime, timedelta
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

appointment = AppointmentModel(
    appointment_date=tomorrow,
    deadline=(datetime.now() + timedelta(days=7)).strftime('%d-%m-%Y')
)

# Invalid usage
try:
    past_appointment = AppointmentModel(appointment_date='2020-01-01')
except ValidationException as e:
    print(e.validations)  # {'appointment_date': 'Date must be in the future'}
```

### Parameters
- `format` (str, optional): Expected date format. Default: '%Y-%m-%d'
- `message` (str, optional): Custom error message. Default: 'Date must be in the future'

---

## is_past_date

Validates that the date is in the past.

```python
from pyvalidx.date import is_past_date

class HistoryModel(ValidatedModel):
    birth_date: str = field_validated(is_past_date())
    graduation_date: str = field_validated(
        is_past_date('%d/%m/%Y', 'Graduation date must be in the past')
    )

# Valid usage
history = HistoryModel(
    birth_date='1990-03-15',
    graduation_date='15/06/2020'
)

# Invalid usage
try:
    future_birth = HistoryModel(birth_date='2030-01-01')
except ValidationException as e:
    print(e.validations)  # {'birth_date': 'Date must be in the past'}
```

### Parameters
- `format` (str, optional): Expected date format. Default: '%Y-%m-%d'
- `message` (str, optional): Custom error message. Default: 'Date must be in the past'

---

## is_today

Validates that the date is exactly today.

```python
from pyvalidx.date import is_today

class DailyReportModel(ValidatedModel):
    report_date: str = field_validated(is_today())
    submission_date: str = field_validated(
        is_today('%d-%m-%Y', 'Report must be submitted today')
    )

# Valid usage
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')

report = DailyReportModel(
    report_date=today,
    submission_date=datetime.now().strftime('%d-%m-%Y')
)

# Invalid usage
try:
    wrong_report = DailyReportModel(report_date='2024-01-01')
except ValidationException as e:
    print(e.validations)  # {'report_date': 'Date must be today'}
```

### Parameters
- `format` (str, optional): Expected date format. Default: '%Y-%m-%d'
- `message` (str, optional): Custom error message. Default: 'Date must be today'

---

## Complete Example: Hotel Reservation System

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.date import is_date, is_future_date
from datetime import datetime, timedelta

class HotelReservationModel(ValidatedModel):
    guest_name: str = field_validated(is_required('Guest name is required'))

    check_in_date: str = field_validated(
        is_required('Check-in date is required'),
        is_date('%Y-%m-%d', 'Check-in date must be in YYYY-MM-DD format'),
        is_future_date('%Y-%m-%d', 'Check-in date must be in the future')
    )

    check_out_date: str = field_validated(
        is_required('Check-out date is required'),
        is_date('%Y-%m-%d', 'Check-out date must be in YYYY-MM-DD format'),
        is_future_date('%Y-%m-%d', 'Check-out date must be in the future')
    )

# Valid usage
tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

reservation = HotelReservationModel(
    guest_name='John Doe',
    check_in_date=tomorrow,
    check_out_date=next_week
)
```

---

## Example: Birth Date Validation

```python
from pyvalidx.date import is_past_date
from pyvalidx.numeric import min_value, max_value
from datetime import datetime

class PersonModel(ValidatedModel):
    name: str = field_validated(is_required())
    birth_date: str = field_validated(
        is_required('Birth date is required'),
        is_date('%Y-%m-%d', 'Birth date must be in YYYY-MM-DD format'),
        is_past_date('%Y-%m-%d', 'Birth date must be in the past')
    )

    @property
    def age(self) -> int:
        '''
        Calculates the age based on the birth date

        Returns:
            int: Age in years
        '''
        birth = datetime.strptime(self.birth_date, '%Y-%m-%d')
        today = datetime.now()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

# Usage
person = PersonModel(
    name='Alice Smith',
    birth_date='1990-03-15'
)
print(f'{person.name} is {person.age} years old')
```

---

## Example: Event Validation with Multiple Dates

```python
class ConferenceModel(ValidatedModel):
    title: str = field_validated(is_required())

    registration_deadline: str = field_validated(
        is_date('%Y-%m-%d'),
        is_future_date('%Y-%m-%d', 'Registration deadline must be in the future')
    )

    event_start: str = field_validated(
        is_date('%Y-%m-%d'),
        is_future_date('%Y-%m-%d', 'Event start date must be in the future')
    )

    event_end: str = field_validated(
        is_date('%Y-%m-%d'),
        is_future_date('%Y-%m-%d', 'Event end date must be in the future')
    )

# Usage
from datetime import datetime, timedelta

conference = ConferenceModel(
    title='Python Conference 2024',
    registration_deadline=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
    event_start=(datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
    event_end=(datetime.now() + timedelta(days=63)).strftime('%Y-%m-%d')
)
```

---

## Supported Date Formats

| Format | Example | Description |
|---------|---------|-------------|
| `%Y-%m-%d` | 2024-12-25 | Year-Month-Day (ISO) |
| `%d/%m/%Y` | 25/12/2024 | Day/Month/Year (European) |
| `%m/%d/%Y` | 12/25/2024 | Month/Day/Year (American) |
| `%Y-%m-%d %H:%M:%S` | 2024-12-25 14:30:00 | Full date and time |
| `%d-%m-%Y` | 25-12-2024 | Day-Month-Year with hyphens |
| `%Y/%m/%d` | 2024/12/25 | Year/Month/Day with slashes |

---

## Important Notes

- Date validators return `True` if the value is `None` (for optional fields)
- Dates are compared using `datetime.now()` at validation time
- If the date format is invalid, the validator returns `False`
- You can combine date validators with other validators for more complex validations
- For optional date fields, consider using `Optional[str]` in the type annotation
