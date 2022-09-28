from pydantic import EmailStr
from templated_mail.mail import BaseEmailMessage

from app.base.actions.base import BaseAction
from app.base.entities.base import BaseEntity
from app.users.services.email_verification import EmailVerificationService


class POST_UsersRegisterResendAction(BaseAction):
    class InEntity(BaseEntity):
        email: EmailStr

    def __init__(self):
        self.email_verification = EmailVerificationService(scope='register')

    def run(self, data: InEntity) -> None:
        self.email_verification.send(
            BaseEmailMessage(template_name='users/activation.html', to=[data.email])
        )
