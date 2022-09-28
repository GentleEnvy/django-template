from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.serializers.register.resend import *
from app.users.actions.register.resend import *


class UsersRegisterResendView(BaseView):
    serializer_map = {'post': POST_UsersRegisterResendSerializer}

    @response_204
    def post(self):
        action = POST_UsersRegisterResendAction()
        serializer = self.get_valid_serializer()
        action.run(action.InEntity(**serializer.validated_data))
