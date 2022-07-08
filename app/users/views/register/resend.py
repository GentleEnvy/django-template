from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.serializers.register.resend import *
from app.users.actions.register.resend import *

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class UsersRegisterResendView(BaseView):
    serializer_map = {'post': POST_UsersRegisterResendSerializer}
    action_map = {'post': POST_UsersRegisterResendAction}

    @response_204
    def post(self, _):
        self.handle()
