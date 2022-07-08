import dataclasses

from django.conf import settings
from django.contrib.auth.hashers import make_password
from templated_mail.mail import BaseEmailMessage

from app.base.actions.base import BaseAction
from app.users.models import User
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class GET_UsersRegisterAction(BaseAction):
    def __init__(self, view):
        super().__init__(view)
        self.email_verification = EmailVerificationService(scope='register')

    @dataclasses.dataclass
    class DTO:
        email: str
        code: str

    def dto(self):
        try:
            return self.DTO(**{k: v for k, v in self.view.request.query_params.items()})
        except TypeError:
            return None

    def run(self, data: DTO):
        if data is None:
            return ACTIVATE_FAILURE_URL
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


class POST_UsersRegisterAction(BaseAction):
    def __init__(self, view):
        super().__init__(view)
        self.email_verification = EmailVerificationService(scope='register')

    @dataclasses.dataclass
    class dto:
        email: str
        password: str
        first_name: str | None = dataclasses.field(default=None)
        last_name: str | None = dataclasses.field(default=None)

    def run(self, data: dto):
        data.password = make_password(data.password)
        user = self.view.serializer.create(data.__dict__ | {'is_active': False})
        self.email_verification.send(
            BaseEmailMessage(
                request=self.view.request,
                template_name='users/activation.html',
                to=[user.email],
            )
        )
        return user
