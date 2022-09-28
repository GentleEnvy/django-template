from django.conf import settings
from pydantic.networks import HttpUrl, EmailStr
from rest_framework.request import Request
from templated_mail.mail import BaseEmailMessage

from app.base.actions.base import BaseAction
from app.base.entities.base import BaseEntity
from app.users.models import User
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService


class GET_UsersRegisterAction(BaseAction):
    class InEntity(BaseEntity):
        request: Request
        email: EmailStr
        code: str

    class OutEntity(BaseEntity):
        url: HttpUrl

    def __init__(self):
        self.email_verification = EmailVerificationService(scope='register')
        self.user_manager = User.objects

    def run(self, data: InEntity) -> OutEntity:
        if self.email_verification.check(data.email, data.code):
            try:
                user = self.user_manager.get(email=data.email)
            except User.DoesNotExist:
                return self.OutEntity(url=settings.VERIFICATION_ACTIVATE_FAILURE_URL)
            user.is_active = True
            user.save()
            token = AuthService().login(user, data.request)
            print(settings.VERIFICATION_ACTIVATE_SUCCESS_URL % token)
            return self.OutEntity(
                url=settings.VERIFICATION_ACTIVATE_SUCCESS_URL % token
            )
        return self.OutEntity(url=settings.VERIFICATION_ACTIVATE_FAILURE_URL)


class POST_UsersRegisterAction(BaseAction):
    class InEntity(BaseEntity):
        email: EmailStr
        password: str

    OutEntity = User

    def __init__(self):
        self.email_verification = EmailVerificationService(scope='register')
        self.user_manager = User.objects

    def run(self, data: InEntity) -> OutEntity:
        user = self.user_manager.create_user(
            email=data.email, password=data.password, is_active=False
        )
        self.email_verification.send(
            BaseEmailMessage(template_name='users/activation.html', to=[user.email])
        )
        return user
