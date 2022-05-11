import dataclasses

from dataclass_type_validator import dataclass_validate, TypeValidationError
from django.conf import settings
from templated_mail.mail import BaseEmailMessage

from app.base.controllers.base import BaseController
from app.users.models import User
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService
from app.users.services.password_session import PasswordSessionService

PASSWORD_SUCCESS_URL = settings.VERIFICATION_PASSWORD_SUCCESS_URL
PASSWORD_FAILURE_URL = settings.VERIFICATION_PASSWORD_FAILURE_URL


class GET_UsersPasswordController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'password'}
    password_session: PasswordSessionService
    
    @dataclass_validate
    @dataclasses.dataclass
    class _dataclass:
        email: str
        code: str
    
    def dataclass(self) -> _dataclass | None:
        query_params = self.view.request.query_params
        try:
            return self._dataclass(
                email=query_params.get('email'), code=query_params.get('code')
            )
        except (TypeError, TypeValidationError):
            return None
    
    def control(self, data: _dataclass | None):
        if data is not None and self.email_verification.check(data.email, data.code):
            session_id = self.password_session.create(data.email)
            return PASSWORD_SUCCESS_URL % session_id
        return PASSWORD_FAILURE_URL


class POST_UsersPasswordController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'password'}
    
    @dataclass_validate
    @dataclasses.dataclass
    class dataclass:
        email: str
    
    def control(self, data: dataclass):
        self.email_verification.send(
            BaseEmailMessage(
                request=self.view.request, template_name='users/password.html',
                to=[data.email]
            )
        )


class PUT_UsersPasswordController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'password'}
    password_session: PasswordSessionService
    
    @dataclass_validate
    @dataclasses.dataclass
    class dataclass:
        session_id: str
        password: str
    
    def control(self, data: dataclass):
        if (email := self.password_session.check(data.session_id)) is None:
            raise self.view.serializer.WARNINGS[408]
        user = User.objects.get(email=email)
        user.set_password(data.password)
        user.save()
        token = AuthService(self.view.request, user).login()
        return {'token': token}
