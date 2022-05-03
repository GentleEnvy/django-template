from django.conf import settings
from django.urls import reverse
from templated_mail.mail import BaseEmailMessage

from app.base.controllers.base import BaseController
from app.users.services.email_verification import EmailVerificationService

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class POST_UsersRegisterResendController(BaseController):
    email_verification: EmailVerificationService = {'scope': 'register'}
    
    def control(self, data):
        self.email_verification.send(
            BaseEmailMessage(
                request=self.view.request, template_name='users/activation.html',
                to=[self.view.serializer.instance.email],
                context={'path': reverse('register')}
            )
        )
