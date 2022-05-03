from django.conf import settings

from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.controllers.register.resend import POST_UsersRegisterResendController
from app.users.serializers.register.resend import POST_UsersRegisterResendSerializer

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class UsersRegisterResendView(BaseView):
    serializer_map = {'post': POST_UsersRegisterResendSerializer}
    controller_map = {'post': POST_UsersRegisterResendController}
    
    @response_204
    def post(self, _):
        self.handle()
