from django.core.exceptions import ValidationError


class EntityValidationError(ValidationError):
    pass
