from django.conf import settings

from app.base.utils.common import response_204
from app.base.views.base import BaseView

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class UsersRegisterResendView(BaseView):
    @response_204
    def post(self, _):
        self.handle()
