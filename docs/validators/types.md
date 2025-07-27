# Type Validators

Type validators provide functionalities for validating specific data types and values within predefined sets.

## is_dict

Validates that the field is a dictionary.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.types import is_dict

class ConfigModel(ValidatedModel):
    settings: dict = field_validated(is_dict())
    metadata: dict = field_validated(is_dict('Metadata must be a dictionary'))

# Valid usage
config = ConfigModel(
    settings={'debug': True, 'port': 8080},
    metadata={'version': '1.0', 'author': 'John Doe'}
)

# Invalid usage
try:
    invalid_config = ConfigModel(settings='not a dict')
except ValidationException as e:
    print(e.validations)  # {'settings': 'Must be a dictionary'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be a dictionary'

---

## is_list

Validates that the field is a list.

```python
from pyvalidx.types import is_list

class PlaylistModel(ValidatedModel):
    songs: list = field_validated(is_list())
    genres: list = field_validated(is_list('Genres must be a list'))

# Valid usage
playlist = PlaylistModel(
    songs=['Song 1', 'Song 2', 'Song 3'],
    genres=['Rock', 'Pop', 'Jazz']
)

# Invalid usage
try:
    invalid_playlist = PlaylistModel(songs='not a list')
except ValidationException as e:
    print(e.validations)  # {'songs': 'Must be a list'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be a list'

---

## is_boolean

Validates that the field is a boolean.

```python
from pyvalidx.types import is_boolean

class SettingsModel(ValidatedModel):
    enabled: bool = field_validated(is_boolean())
    debug_mode: bool = field_validated(is_boolean('Debug mode must be true or false'))

# Valid usage
settings = SettingsModel(
    enabled=True,
    debug_mode=False
)

# Invalid usage
try:
    invalid_settings = SettingsModel(enabled='yes')
except ValidationException as e:
    print(e.validations)  # {'enabled': 'Must be a boolean'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be a boolean'

---

## is_integer

Validates that the field is an integer.

```python
from pyvalidx.types import is_integer

class CounterModel(ValidatedModel):
    count: int = field_validated(is_integer())
    max_items: int = field_validated(is_integer('Max items must be an integer'))

# Valid usage
counter = CounterModel(
    count=42,
    max_items=100
)

# Invalid usage
try:
    invalid_counter = CounterModel(count='not a number')
except ValidationException as e:
    print(e.validations)  # {'count': 'Must be an integer'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be an integer'

---

## is_float

Validates that the field is a float.

```python
from pyvalidx.types import is_float

class MeasurementModel(ValidatedModel):
    temperature: float = field_validated(is_float())
    pressure: float = field_validated(is_float('Pressure must be a decimal number'))

# Valid usage
measurement = MeasurementModel(
    temperature=23.5,
    pressure=1013.25
)

# Invalid usage
try:
    invalid_measurement = MeasurementModel(temperature='hot')
except ValidationException as e:
    print(e.validations)  # {'temperature': 'Must be a float'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must be a float'

---

## is_in

Validates that the field value is within a predefined set of valid values.

```python
from pyvalidx.types import is_in

class UserModel(ValidatedModel):
    role: str = field_validated(is_in(['admin', 'user', 'guest']))
    status: str = field_validated(
        is_in(['active', 'inactive', 'pending'], 'Invalid user status')
    )

# Valid usage
user = UserModel(
    role='admin',
    status='active'
)

# Invalid usage
try:
    invalid_user = UserModel(role='invalid_role')
except ValidationException as e:
    print(e.validations)  # {'role': 'Must be one of: ['admin', 'user', 'guest']'}
```

### Parameters
- `choices` (Union[List[Any], Set[Any]]): List or set of valid values
- `message` (str, optional): Custom error message

---

## Complete Example: Configuration System

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required
from pyvalidx.types import is_dict, is_list, is_boolean, is_in
from pyvalidx.numeric import is_positive, min_value, max_value

class ApplicationConfigModel(ValidatedModel):
    # Basic configuration
    app_name: str = field_validated(is_required('Application name is required'))

    # Environment validation
    environment: str = field_validated(
        is_required('Environment is required'),
        is_in(['development', 'staging', 'production'], 'Invalid environment')
    )

    # Feature flags
    debug_mode: bool = field_validated(
        is_required('Debug mode setting is required'),
        is_boolean('Debug mode must be true or false')
    )

    # Database configuration
    database_config: dict = field_validated(
        is_required('Database configuration is required'),
        is_dict('Database config must be a dictionary')
    )

    # Allowed hosts
    allowed_hosts: list = field_validated(
        is_required('Allowed hosts are required'),
        is_list('Allowed hosts must be a list')
    )

    # Port configuration
    port: int = field_validated(
        is_required('Port is required'),
        is_positive('Port must be positive'),
        min_value(1024, 'Port must be at least 1024'),
        max_value(65535, 'Port must be at most 65535')
    )

# Valid usage
config = ApplicationConfigModel(
    app_name='MyWebApp',
    environment='production',
    debug_mode=False,
    database_config={
        'host': 'localhost',
        'port': 5432,
        'name': 'myapp_db'
    },
    allowed_hosts=['example.com', 'www.example.com'],
    port=8080
)
```

---

## Example: JSON Data Validation

```python
from pyvalidx.types import is_dict, is_list
from pyvalidx.string import is_email

class ApiRequestModel(ValidatedModel):
    user_data: dict = field_validated(
        is_required('User data is required'),
        is_dict('User data must be a valid JSON object')
    )

    tags: list = field_validated(
        is_list('Tags must be an array')
    )

    action: str = field_validated(
        is_required('Action is required'),
        is_in(['create', 'update', 'delete'], 'Invalid action type')
    )

# Valid usage
api_request = ApiRequestModel(
    user_data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30
    },
    tags=['important', 'user', 'profile'],
    action='create'
)

# Invalid usage
try:
    invalid_request = ApiRequestModel(
        user_data='not a dict',
        tags='not a list',
        action='invalid_action'
    )
except ValidationException as e:
    print(e.validations)
    # Multiple validation errors will be shown
```

---

## Example: Game Configuration

```python
from pyvalidx.types import is_in, is_boolean, is_integer

class GameSettingsModel(ValidatedModel):
    difficulty: str = field_validated(
        is_required('Difficulty is required'),
        is_in(['easy', 'medium', 'hard', 'expert'], 'Invalid difficulty level')
    )

    sound_enabled: bool = field_validated(
        is_boolean('Sound setting must be true or false')
    )

    max_players: int = field_validated(
        is_required('Max players is required'),
        is_integer('Max players must be a number'),
        is_in([2, 4, 6, 8], 'Max players must be 2, 4, 6, or 8')
    )

    game_modes: list = field_validated(
        is_required('Game modes are required'),
        is_list('Game modes must be a list')
    )

# Usage
game_settings = GameSettingsModel(
    difficulty='medium',
    sound_enabled=True,
    max_players=4,
    game_modes=['classic', 'tournament', 'practice']
)
```

---

## Important Notes

- Type validators return `True` if the value is `None` (for optional fields)
- `is_in` validator performs case-sensitive comparison
- For `is_in`, you can use both lists and sets for better performance with large choice sets
- Type validators can be combined with other validators for comprehensive validation
- When using `is_in` with numbers, ensure the choices match the expected data type
