import dataclasses

from django.conf import settings
from django.contrib.auth.hashers import make_password
from templated_mail.mail import BaseEmailMessage

from app.base.controllers.base import BaseController
from app.users.models import User
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class GET_UsersRegisterController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'register'}
    
    @dataclasses.dataclass
    class _dataclass:
        email: str
        code: str
    
    def dataclass(self):
        try:
            return self._dataclass(
                **{k: v for k, v in self.view.request.query_params.items()}
            )
        except TypeError:
            return None
    
    def control(self, data: _dataclass):
        if data is None:
            return ACTIVATE_FAILURE_URL
        print(data)
        if self.email_verification.check(data.email, data.code):
            try:
                user = User.objects.get(email=data.email)
            except User.DoesNotExist:
                return ACTIVATE_FAILURE_URL
            user.is_active = True
            user.save()
            token = AuthService(self.view.request, user).login()
            return ACTIVATE_SUCCESS_URL % token
        return ACTIVATE_FAILURE_URL


class POST_UsersRegisterController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'register'}
    
    @dataclasses.dataclass
    class dataclass:
        email: str
        password: str
        first_name: str | None = dataclasses.field(default=None)
        last_name: str | None = dataclasses.field(default=None)
    
    def control(self, data: dataclass):
        data.password = make_password(data.password)
        user = self.view.serializer.create(data.__dict__ | {'is_active': False})
        self.email_verification.send(
            BaseEmailMessage(
                request=self.view.request, template_name='users/activation.html',
                to=[user.email]
            )
        )
        return user
