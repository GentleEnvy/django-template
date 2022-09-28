from django.conf import settings
from pydantic import EmailStr, HttpUrl
from rest_framework.request import Request
from templated_mail.mail import BaseEmailMessage

from app.base.entities.base import BaseEntity
from app.users.models import User
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService
from app.users.services.password_session import PasswordSessionService


class GET_UsersPasswordAction:
    class InEntity(BaseEntity):
        email: EmailStr
        code: str

    class OutEntity(BaseEntity):
        url: HttpUrl

    def __init__(self):
        self.email_verification = EmailVerificationService(scope='password')
        self.password_session = PasswordSessionService()

    def run(self, data: InEntity) -> OutEntity:
        if data is not None and self.email_verification.check(data.email, data.code):
            session_id = self.password_session.create(data.email)
            return self.OutEntity(
                url=settings.VERIFICATION_PASSWORD_SUCCESS_URL % session_id
            )
        return self.OutEntity(url=settings.VERIFICATION_PASSWORD_FAILURE_URL)


class POST_UsersPasswordAction:
    class InEntity(BaseEntity):
        email: str
    
    def __init__(self):
        self.email_verification = EmailVerificationService(scope='password')

    def run(self, data: InEntity) -> None:
        self.email_verification.send(
            BaseEmailMessage(
                template_name='users/password.html',
                to=[data.email],
            )
        )


class PUT_UsersPasswordAction:
    class InEntity(BaseEntity):
        request: Request
        session_id: str
        password: str

    class OutEntity(BaseEntity):
        token: str

    def __init__(self):
        self.email_verification = EmailVerificationService(scope='password')
        self.password_session = PasswordSessionService()
        self.auth_service = AuthService()
        self.user_manager = User.objects

    def run(self, data: InEntity) -> OutEntity:
        if (email := self.password_session.check(data.session_id)) is None:
            raise TimeoutError
        user = self.user_manager.get(email=email)
        user.set_password(data.password)
        user.save()
        token = self.auth_service.login(user, data.request).key
        return self.OutEntity(token=token)
