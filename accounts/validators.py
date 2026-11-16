import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.contrib.auth.password_validation import validate_password


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


def validate_username(value):
    username = (value or "").strip()
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValidationError(
            "Username must be 3–30 characters and may contain letters, numbers, dots, underscores, and hyphens."
        )
    return username


def validate_account_email(value):
    email = (value or "").strip().lower()
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError("Enter a valid email address.")
    return email


def validate_account_password(value):
    # Django's configured password validators are explicitly permitted.
    validate_password(value)
    return value
