from app.base.models.choices.base import IntegerChoices


class UserType(IntegerChoices):
    BANNED = ...
    DEFAULT = ...
    ADMIN = ...
    SUPER = ...
