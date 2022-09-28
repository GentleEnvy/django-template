from django.contrib.auth import authenticate
from pydantic import EmailStr
from rest_framework.request import Request

from app.base.actions.base import BaseAction
from app.base.entities.base import BaseEntity
from app.users.enums.users import UserType
from app.users.models import User
from app.users.services.auth import AuthService


class POST_UsersTokenAction(BaseAction):
    class InEntity(BaseEntity):
        email: EmailStr
        password: str
        request: Request

    class OutEntity(BaseEntity):
        token: str

    def __init__(self):
        self.auth_service = AuthService()

    def run(self, data: InEntity):
        user = authenticate(
            request=data.request, email=data.email, password=data.password
        )
        if user is None:
            try:
                user = User.objects.get(email=data.email)
            except User.DoesNotExist:
                raise PermissionError
        if not user.check_password(data.password):
            raise PermissionError
        if user.type == UserType.BANNED:
            raise PermissionError
        if not user.is_active:
            raise PermissionError
        return self.OutEntity(token=self.auth_service.login(user, data.request).key)


class DELETE_UsersTokenAction(BaseAction):
    class InEntity(BaseEntity):
        user: User
        request: Request

    def __init__(self):
        self.auth_service = AuthService()

    def run(self, data: InEntity) -> None:
        self.auth_service.logout(data.user, data.request)
