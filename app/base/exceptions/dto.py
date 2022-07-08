from django.core.exceptions import ValidationError


class DTOValidationError(ValidationError):
    pass
