# Form Validation Example

This example demonstrates how to validate different types of forms using PyValidX, from simple contact forms to complex multi-step forms.

## Contact Form Validation

```python
from pyvalidx import ValidatedModel, field_validated
from pyvalidx.core import is_required, min_length, max_length, is_in
from pyvalidx.string import is_email, is_phone
from pyvalidx.exception import ValidationException
from typing import Optional

class ContactFormModel(ValidatedModel):
    # Basic contact information
    name: str = field_validated(
        is_required('Name is required'),
        min_length(2, 'Name must be at least 2 characters'),
        max_length(100, 'Name cannot exceed 100 characters')
    )

    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address')
    )

    phone: Optional[str] = field_validated(
        is_phone('Please provide a valid phone number')
    )

    # Subject and message
    subject: str = field_validated(
        is_required('Subject is required'),
        is_in([
            'General Inquiry',
            'Technical Support',
            'Sales Question',
            'Bug Report',
            'Feature Request',
            'Other'
        ], 'Please select a valid subject')
    )

    message: str = field_validated(
        is_required('Message is required'),
        min_length(10, 'Message must be at least 10 characters'),
        max_length(1000, 'Message cannot exceed 1000 characters')
    )

    # Optional fields
    company: Optional[str] = field_validated(
        max_length(100, 'Company name cannot exceed 100 characters')
    )

    newsletter_signup: bool = False

# Usage example
def process_contact_form(form_data: dict):
    '''Process contact form submission'''
    try:
        contact = ContactFormModel(**form_data)

        # Simulate sending email
        print(f'Contact form submitted by {contact.name}')
        print(f'Email: {contact.email}')
        print(f'Subject: {contact.subject}')
        print(f'Message: {contact.message[:50]}...')

        if contact.newsletter_signup:
            print('User signed up for newsletter')

        return {
            'success': True,
            'message': 'Thank you for your message. We'll get back to you soon!'
        }

    except ValidationException as e:
        return {
            'success': False,
            'errors': e.validations,
            'message': 'Please correct the errors below'
        }

# Test with valid data
valid_form_data = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'phone': '3001234567',
    'subject': 'Technical Support',
    'message': 'I'm having trouble with the login feature. Could you please help?',
    'company': 'Tech Corp',
    'newsletter_signup': True
}

result = process_contact_form(valid_form_data)
print(result)
```

## Survey Form with Conditional Fields

```python
from pyvalidx.core import required_if, custom
from pyvalidx.numeric import min_value, max_value, is_in_range

def age_group_validator(value, context=None):
    '''Custom validator for age groups'''
    if value is None:
        return True

    valid_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
    return str(value) in valid_groups

class SurveyFormModel(ValidatedModel):
    # Basic demographics
    age_group: str = field_validated(
        is_required('Age group is required'),
        custom(age_group_validator, 'Please select a valid age group')
    )

    gender: str = field_validated(
        is_required('Gender is required'),
        is_in(['Male', 'Female', 'Non-binary', 'Prefer not to say'], 'Please select a valid option')
    )

    employment_status: str = field_validated(
        is_required('Employment status is required'),
        is_in([
            'Employed full-time',
            'Employed part-time',
            'Self-employed',
            'Unemployed',
            'Student',
            'Retired'
        ], 'Please select a valid employment status')
    )

    # Conditional fields based on employment
    company_size: Optional[str] = field_validated(
        required_if('employment_status', 'Employed full-time', 'Company size is required for full-time employees'),
        is_in(['1-10', '11-50', '51-200', '201-1000', '1000+'], 'Please select a valid company size')
    )

    industry: Optional[str] = field_validated(
        required_if('employment_status', 'Employed full-time', 'Industry is required for full-time employees')
    )

    # Product satisfaction
    product_satisfaction: int = field_validated(
        is_required('Product satisfaction rating is required'),
        min_value(1, 'Rating must be between 1 and 5'),
        max_value(5, 'Rating must be between 1 and 5')
    )

    # Conditional feedback
    improvement_suggestions: Optional[str] = field_validated(
        required_if('product_satisfaction', 3, 'Please provide suggestions for ratings of 3 or below'),
        min_length(10, 'Please provide at least 10 characters of feedback')
    )

    # Recommendation
    would_recommend: bool = field_validated(
        is_required('Recommendation question is required')
    )

    additional_comments: Optional[str] = field_validated(
        max_length(500, 'Comments cannot exceed 500 characters')
    )

# Custom validator for conditional improvement suggestions
def improvement_required_for_low_rating(value, context=None):
    '''Require improvement suggestions for low ratings'''
    if context is None:
        return True

    satisfaction = context.get('product_satisfaction')
    if satisfaction is not None and satisfaction <= 3:
        return value is not None and len(str(value).strip()) >= 10
    return True

# Enhanced model with custom conditional validation
class EnhancedSurveyFormModel(SurveyFormModel):
    improvement_suggestions: Optional[str] = field_validated(
        custom(improvement_required_for_low_rating, 'Please provide improvement suggestions for ratings of 3 or below'),
        max_length(500, 'Suggestions cannot exceed 500 characters')
    )

def process_survey_form(form_data: dict):
    '''Process survey form submission'''
    try:
        survey = EnhancedSurveyFormModel(**form_data)

        # Process survey data
        print(f'Survey submitted by {survey.age_group} {survey.gender}')
        print(f'Employment: {survey.employment_status}')
        print(f'Satisfaction: {survey.product_satisfaction}/5')
        print(f'Would recommend: {survey.would_recommend}')

        # Store in database (simulated)
        survey_id = 'SURVEY_' + str(hash(str(form_data)))[:8]

        return {
            'success': True,
            'survey_id': survey_id,
            'message': 'Thank you for completing our survey!'
        }

    except ValidationException as e:
        return {
            'success': False,
            'errors': e.validations,
            'message': 'Please complete all required fields'
        }
```

## Multi-Step Registration Form

```python
from pyvalidx.date import is_date, is_past_date
from datetime import datetime

# Step 1: Personal Information
class PersonalInfoStep(ValidatedModel):
    first_name: str = field_validated(
        is_required('First name is required'),
        min_length(2, 'First name must be at least 2 characters')
    )

    last_name: str = field_validated(
        is_required('Last name is required'),
        min_length(2, 'Last name must be at least 2 characters')
    )

    birth_date: str = field_validated(
        is_required('Birth date is required'),
        is_date('%Y-%m-%d', 'Birth date must be in YYYY-MM-DD format'),
        is_past_date('%Y-%m-%d', 'Birth date must be in the past')
    )

    gender: str = field_validated(
        is_required('Gender is required'),
        is_in(['Male', 'Female', 'Non-binary', 'Prefer not to say'], 'Please select a valid option')
    )

# Step 2: Contact Information
class ContactInfoStep(ValidatedModel):
    email: str = field_validated(
        is_required('Email is required'),
        is_email('Please provide a valid email address')
    )

    phone: str = field_validated(
        is_required('Phone number is required'),
        is_phone('Please provide a valid phone number')
    )

    address: str = field_validated(
        is_required('Address is required'),
        min_length(10, 'Please provide a complete address')
    )

    city: str = field_validated(
        is_required('City is required'),
        min_length(2, 'City name must be at least 2 characters')
    )

    postal_code: str = field_validated(
        is_required('Postal code is required'),
        min_length(5, 'Postal code must be at least 5 characters')
    )

    country: str = field_validated(
        is_required('Country is required'),
        min_length(2, 'Country must be at least 2 characters')
    )

# Step 3: Account Information
class AccountInfoStep(ValidatedModel):
    username: str = field_validated(
        is_required('Username is required'),
        min_length(3, 'Username must be at least 3 characters'),
        max_length(20, 'Username cannot exceed 20 characters')
    )

    password: str = field_validated(
        is_required('Password is required'),
        min_length(8, 'Password must be at least 8 characters'),
        is_strong_password('Password must contain uppercase, lowercase, numbers and special characters')
    )

    confirm_password: str = field_validated(
        is_required('Password confirmation is required'),
        same_as('password', 'Passwords must match')
    )

    security_question: str = field_validated(
        is_required('Security question is required'),
        is_in([
            'What was your first pet's name?',
            'What city were you born in?',
            'What was your mother's maiden name?',
            'What was the name of your first school?'
        ], 'Please select a valid security question')
    )

    security_answer: str = field_validated(
        is_required('Security answer is required'),
        min_length(3, 'Security answer must be at least 3 characters')
    )

# Step 4: Preferences
class PreferencesStep(ValidatedModel):
    newsletter_subscription: bool = False
    sms_notifications: bool = False
    email_notifications: bool = True

    preferred_language: str = field_validated(
        is_required('Preferred language is required'),
        is_in(['English', 'Spanish', 'French', 'German', 'Portuguese'], 'Please select a valid language')
    )

    timezone: str = field_validated(
        is_required('Timezone is required')
    )

    terms_accepted: bool = field_validated(
        is_required('You must accept the terms and conditions'),
        custom(lambda x, _: x is True, 'Terms and conditions must be accepted')
    )

    privacy_policy_accepted: bool = field_validated(
        is_required('You must accept the privacy policy'),
        custom(lambda x, _: x is True, 'Privacy policy must be accepted')
    )

class MultiStepFormHandler:
    '''Handler for multi-step form validation and processing'''

    def __init__(self):
        self.steps = {
            1: PersonalInfoStep,
            2: ContactInfoStep,
            3: AccountInfoStep,
            4: PreferencesStep
        }
        self.form_data = {}

    def validate_step(self, step_number: int, step_data: dict):
        '''Validate a specific step'''
        if step_number not in self.steps:
            return {
                'success': False,
                'error': 'Invalid step number'
            }

        try:
            step_model = self.steps[step_number]
            validated_data = step_model(**step_data)

            # Store validated data
            self.form_data[step_number] = validated_data.model_dump()

            return {
                'success': True,
                'message': f'Step {step_number} completed successfully',
                'next_step': step_number + 1 if step_number < len(self.steps) else None
            }

        except ValidationException as e:
            return {
                'success': False,
                'errors': e.validations,
                'message': f'Please correct the errors in step {step_number}'
            }

    def get_progress(self):
        '''Get form completion progress'''
        completed_steps = len(self.form_data)
        total_steps = len(self.steps)

        return {
            'completed_steps': completed_steps,
            'total_steps': total_steps,
            'progress_percentage': (completed_steps / total_steps) * 100,
            'current_step': completed_steps + 1 if completed_steps < total_steps else total_steps
        }

    def complete_registration(self):
        '''Complete the registration process'''
        if len(self.form_data) != len(self.steps):
            return {
                'success': False,
                'error': 'All steps must be completed before registration'
            }

        # Combine all step data
        complete_data = {}
        for step_data in self.form_data.values():
            complete_data.update(step_data)

        # Simulate saving to database
        user_id = str(hash(str(complete_data)))[:10]

        return {
            'success': True,
            'user_id': user_id,
            'message': 'Registration completed successfully!',
            'user_data': complete_data
        }

# Usage example
form_handler = MultiStepFormHandler()

# Step 1: Personal Information
step1_data = {
    'first_name': 'John',
    'last_name': 'Doe',
    'birth_date': '1990-05-15',
    'gender': 'Male'
}

result1 = form_handler.validate_step(1, step1_data)
print('Step 1 result:', result1)
print('Progress:', form_handler.get_progress())

# Step 2: Contact Information
step2_data = {
    'email': 'john.doe@example.com',
    'phone': '3001234567',
    'address': '123 Main Street, Apt 4B',
    'city': 'New York',
    'postal_code': '10001',
    'country': 'United States'
}

result2 = form_handler.validate_step(2, step2_data)
print('Step 2 result:', result2)
print('Progress:', form_handler.get_progress())

# Continue with remaining steps...
```

## File Upload Form Validation

```python
from pyvalidx.core import custom
import os

def file_size_validator(max_size_mb: int):
    '''Custom validator for file size'''
    def validator(value, context=None):
        if value is None:
            return True

        # In a real application, this would check actual file size
        # For demo purposes, we'll simulate based on filename
        if hasattr(value, 'size'):
            size_mb = value.size / (1024 * 1024)
            return size_mb <= max_size_mb

        return True

    validator.__message__ = f'File size must not exceed {max_size_mb}MB'
    return validator

def file_type_validator(allowed_types: list):
    '''Custom validator for file types'''
    def validator(value, context=None):
        if value is None:
            return True

        if hasattr(value, 'filename'):
            filename = value.filename.lower()
            return any(filename.endswith(ext.lower()) for ext in allowed_types)

        # For string filenames
        filename = str(value).lower()
        return any(filename.endswith(ext.lower()) for ext in allowed_types)

    validator.__message__ = f'File must be one of: {', '.join(allowed_types)}'
    return validator

class FileUploadFormModel(ValidatedModel):
    title: str = field_validated(
        is_required('Title is required'),
        min_length(3, 'Title must be at least 3 characters'),
        max_length(100, 'Title cannot exceed 100 characters')
    )

    description: Optional[str] = field_validated(
        max_length(500, 'Description cannot exceed 500 characters')
    )

    category: str = field_validated(
        is_required('Category is required'),
        is_in([
            'Document',
            'Image',
            'Video',
            'Audio',
            'Archive',
            'Other'
        ], 'Please select a valid category')
    )

    file_path: str = field_validated(
        is_required('File is required'),
        custom(file_type_validator(['.pdf', '.doc', '.docx', '.txt', '.jpg', '.png', '.gif']),
               'File must be PDF, DOC, DOCX, TXT, JPG, PNG, or GIF'),
        custom(file_size_validator(10), 'File size must not exceed 10MB')
    )

    tags: Optional[str] = field_validated(
        max_length(200, 'Tags cannot exceed 200 characters')
    )

    is_public: bool = False

    upload_date: str = field_validated(
        is_date('%Y-%m-%d %H:%M:%S', 'Invalid upload date format')
    )

def process_file_upload(form_data: dict):
    '''Process file upload form'''
    try:
        # Add current timestamp if not provided
        if 'upload_date' not in form_data:
            form_data['upload_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        upload = FileUploadFormModel(**form_data)

        # Simulate file processing
        file_id = str(hash(upload.file_path))[:8]

        print(f'File uploaded: {upload.title}')
        print(f'Category: {upload.category}')
        print(f'File: {upload.file_path}')
        print(f'Public: {upload.is_public}')

        return {
            'success': True,
            'file_id': file_id,
            'message': 'File uploaded successfully',
            'file_url': f'/files/{file_id}'
        }

    except ValidationException as e:
        return {
            'success': False,
            'errors': e.validations,
            'message': 'Please correct the errors below'
        }

# Test file upload
upload_data = {
    'title': 'Project Documentation',
    'description': 'Complete documentation for the new project',
    'category': 'Document',
    'file_path': 'project_docs.pdf',
    'tags': 'documentation, project, important',
    'is_public': False
}

result = process_file_upload(upload_data)
print(result)
```

## Form Validation Testing

```python
import pytest

class TestFormValidation:

    def test_valid_contact_form(self):
        '''Test valid contact form submission'''
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Technical Support',
            'message': 'I need help with the application'
        }

        contact = ContactFormModel(**valid_data)
        assert contact.name == 'John Doe'
        assert contact.subject == 'Technical Support'

    def test_invalid_email_contact_form(self):
        '''Test contact form with invalid email'''
        invalid_data = {
            'name': 'John Doe',
            'email': 'invalid-email',
            'subject': 'Technical Support',
            'message': 'I need help with the application'
        }

        with pytest.raises(ValidationException) as exc_info:
            ContactFormModel(**invalid_data)

        assert 'email' in exc_info.value.validations

    def test_survey_conditional_validation(self):
        '''Test survey form conditional validation'''
        # Low satisfaction should require improvement suggestions
        survey_data = {
            'age_group': '26-35',
            'gender': 'Male',
            'employment_status': 'Employed full-time',
            'company_size': '51-200',
            'industry': 'Technology',
            'product_satisfaction': 2,  # Low rating
            'would_recommend': False
        }

        with pytest.raises(ValidationException) as exc_info:
            EnhancedSurveyFormModel(**survey_data)

        assert 'improvement_suggestions' in exc_info.value.validations

    def test_multi_step_form_handler(self):
        '''Test multi-step form handler'''
        handler = MultiStepFormHandler()

        # Test step validation
        step1_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': '1990-05-15',
            'gender': 'Male'
        }

        result = handler.validate_step(1, step1_data)
        assert result['success'] is True

        # Test progress tracking
        progress = handler.get_progress()
        assert progress['completed_steps'] == 1
        assert progress['progress_percentage'] == 25.0

# Run tests: pytest test_form_validation.py -v
```

This comprehensive form validation example demonstrates:

- Simple contact forms with basic validation
- Complex survey forms with conditional fields
- Multi-step forms with progress tracking
- File upload forms with custom validators
- Comprehensive testing strategies

The examples show how PyValidX can handle various form validation scenarios while maintaining clean, maintainable code.
