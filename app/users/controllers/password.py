import dataclasses

from django.conf import settings
from templated_mail.mail import BaseEmailMessage

from app.base.controllers.base import BaseController
from app.base.entities.base import BaseEntity
from app.base.exceptions import EntityValidationError
from app.users.models import User
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService
from app.users.services.password_session import PasswordSessionService

PASSWORD_SUCCESS_URL = settings.VERIFICATION_PASSWORD_SUCCESS_URL
PASSWORD_FAILURE_URL = settings.VERIFICATION_PASSWORD_FAILURE_URL


class GET_UsersPasswordController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'password'}
    password_session: PasswordSessionService

    @dataclasses.dataclass
    class _dataclass(BaseEntity):
        email: str
        code: str

    def dto(self) -> _dataclass | None:
        query_params = self.view.request.query_params
        try:
            return self._dataclass(
                email=query_params.get('email'), code=query_params.get('code')
            )
        except (TypeError, EntityValidationError):
            return None

    def control(self, data: _dataclass | None):
        if data is not None and self.email_verification.check(data.email, data.code):
            session_id = self.password_session.create(data.email)
            return PASSWORD_SUCCESS_URL % session_id
        return PASSWORD_FAILURE_URL


class POST_UsersPasswordController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'password'}

    @dataclasses.dataclass
    class dto(BaseEntity):
        email: str

    def control(self, data: dto):
        self.email_verification.send(
            BaseEmailMessage(
                request=self.view.request,
                template_name='users/password.html',
                to=[data.email],
            )
        )


class PUT_UsersPasswordController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'password'}
    password_session: PasswordSessionService

    @dataclasses.dataclass
    class dto(BaseEntity):
        session_id: str
        password: str

    def control(self, data: dto):
        if (email := self.password_session.check(data.session_id)) is None:
            raise self.view.serializer.WARNINGS[408]
        user = User.objects.get(email=email)
        user.set_password(data.password)
        user.save()
        token = AuthService(self.view.request, user).login()
        return {'token': token}
