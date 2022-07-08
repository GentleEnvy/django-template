from django.conf import settings
from django.urls import reverse
from templated_mail.mail import BaseEmailMessage

from app.base.actions.base import BaseAction
from app.users.services.email_verification import EmailVerificationService

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class POST_UsersRegisterResendAction(BaseAction):
    def __init__(self, view):
        super().__init__(view)
        self.email_verification = EmailVerificationService(scope='register')

    def run(self, data):
        self.email_verification.send(
            BaseEmailMessage(
                request=self.view.request,
                template_name='users/activation.html',
                to=[self.view.serializer.instance.email],
                context={'path': reverse('register')},
            )
        )
