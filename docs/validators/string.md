# String Validators

String validators provide specific functionalities for validating and verifying text formats.

## is_email

Validates that the field has a valid email format.

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.string import is_email

class ContactModel(ValidatedModel):
    email: str = field_validated(is_email())
    backup_email: str = field_validated(is_email('Please provide a valid backup email'))

# Valid usage
contact = ContactModel(
    email='user@example.com',
    backup_email='backup@domain.org'
)

# Invalid usage
try:
    invalid_contact = ContactModel(email='invalid-email')
except ValidationException as e:
    print(e.validations)  # {'email': 'Invalid email format'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Invalid email format'

---

## is_strong_password

Validates that the password meets security criteria.

```python
from pyvalidx.string import is_strong_password

class UserModel(ValidatedModel):
    password: str = field_validated(is_strong_password())
    admin_password: str = field_validated(
        is_strong_password('Admin password must be stronger')
    )

# Valid usage
user = UserModel(
    password='MySecurePass123!',
    admin_password='AdminPass456@'
)

# Invalid usage
try:
    weak_user = UserModel(password='123')
except ValidationException as e:
    print(e.validations)  # {'password': 'Password is not strong enough'}
```

### Security criteria:
- **Minimum length**: 8 characters
- **Uppercase letters**: At least 1
- **Lowercase letters**: At least 1
- **Numbers**: At least 1
- **Special characters**: At least 1 (!@#$%^&*()_+-=[]{}|;:,.<>?)

### Parameters
- `message` (str, optional): Custom error message. Default: 'Password is not strong enough'

---

## matches_regex

Validates that the field matches a regular expression pattern.

```python
from pyvalidx.string import matches_regex

class ProductModel(ValidatedModel):
    sku: str = field_validated(
        matches_regex(r'^[A-Z]{3}-\d{4}$', 'SKU must follow format ABC-1234')
    )
    license_plate: str = field_validated(
        matches_regex(r'^[A-Z]{3}\d{3}$')
    )

# Valid usage
product = ProductModel(
    sku='ABC-1234',
    license_plate='ABC123'
)
```

### Parameters
- `pattern` (str): Regular expression to match
- `message` (str, optional): Custom error message. Default: 'Invalid format'

---

## no_whitespace

Validates that the field does not contain whitespace.

```python
from pyvalidx.string import no_whitespace

class UserModel(ValidatedModel):
    username: str = field_validated(no_whitespace())
    api_key: str = field_validated(no_whitespace('API key cannot contain spaces'))

# Valid usage
user = UserModel(
    username='johndoe',
    api_key='abc123def456'
)

# Invalid usage
try:
    invalid_user = UserModel(username='john doe')
except ValidationException as e:
    print(e.validations)  # {'username': 'Must not contain spaces'}
```

### Parameters
- `message` (str, optional): Custom error message. Default: 'Must not contain spaces'

---

## is_phone

Validates that the field is a valid phone number (Colombian format).

```python
from pyvalidx.string import is_phone

class ContactModel(ValidatedModel):
    mobile: str = field_validated(is_phone())
    landline: str = field_validated(is_phone('Invalid landline format'))

# Valid usage
contact = ContactModel(
    mobile='3001234567',
    landline='6012345678'
)

# Invalid usage
try:
    invalid_contact = ContactModel(mobile='123')
except ValidationException as e:
    print(e.validations)  # {'mobile': 'Invalid phone format'}
```

### Supported formats:
- **Mobile**: `3XXXXXXXXX` (10 digits starting with 3)
- **Landline**: `[1-8]XXXXXXX` or `[1-8]XXXXXXXX` (7-8 digits)
- **International**: `+573XXXXXXXXX` for mobile

### Parameters
- `message` (str, optional): Custom error message. Default: 'Invalid phone format'

---

## has_no_common_password

Validates that the password is not in a list of common passwords.

```python
from pyvalidx.string import has_no_common_password

# List of common passwords
COMMON_PASSWORDS = {
    '123456', 'password', '12345678', 'qwerty',
    '123456789', '12345', '1234', '111111'
}

class SecureUserModel(ValidatedModel):
    password: str = field_validated(
        has_no_common_password(COMMON_PASSWORDS)
    )
    backup_password: str = field_validated(
        has_no_common_password(
            COMMON_PASSWORDS,
            'Backup password is too common'
        )
    )

# Valid usage
user = SecureUserModel(
    password='MyUniquePass123!',
    backup_password='AnotherSecurePass456@'
)

# Invalid usage
try:
    weak_user = SecureUserModel(password='123456')
except ValidationException as e:
    print(e.validations)  # {'password': 'Password is too common'}
```

### Parameters
- `dictionary` (Union[List[str], Set[str]]): List or set of forbidden passwords
- `message` (str, optional): Custom error message. Default: 'Password is too common'

---

## Complete Example: User Registration

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length, same_as
from pyvalidx.string import is_email, is_strong_password, no_whitespace

COMMON_PASSWORDS = {'123456', 'password', 'qwerty'}

class UserRegistrationModel(ValidatedModel):
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        no_whitespace('Username cannot contain spaces')
    )

    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address')
    )

    password: str = field_validated(
        is_required('Password is required'),
        is_strong_password('Password must be strong'),
        has_no_common_password(COMMON_PASSWORDS, 'Password is too common')
    )

    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('password', 'Passwords must match')
    )

# Usage
registration = UserRegistrationModel(
    username='johndoe',
    email='john@example.com',
    password='MySecurePass123!',
    confirm_password='MySecurePass123!'
)
```

---

## Advanced String Validation

```python
from pyvalidx.string import matches_regex, no_whitespace
from pyvalidx.core import min_length, max_length

class ProductCodeModel(ValidatedModel):
    # Product code: 3 letters + hyphen + 4 numbers
    product_code: str = field_validated(
        is_required('Product code is required'),
        matches_regex(
            r'^[A-Z]{3}-\d{4}$',
            'Product code must follow format ABC-1234'
        )
    )

    # Internal reference: no spaces, 6-12 characters
    internal_ref: str = field_validated(
        is_required('Internal reference is required'),
        min_length(6, 'Reference too short'),
        max_length(12, 'Reference too long'),
        no_whitespace('Reference cannot contain spaces')
    )

# Usage
product = ProductCodeModel(
    product_code='ABC-1234',
    internal_ref='REF123456'
)
```


