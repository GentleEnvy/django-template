from django.conf import settings
from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse
from rest_framework.mixins import CreateModelMixin

from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView
from app.users.serializers.register.general import *
from app.users.actions.register.general import *

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class UsersRegisterView(CreateModelMixin, BaseView):
    serializer_map = {'post': POST_UsersRegisterSerializer}
    action_map = {'get': GET_UsersRegisterAction, 'post': POST_UsersRegisterAction}

    @extend_schema(
        responses={
            200: None,
            302: OpenApiResponse(
                description=f'redirect:\n\n{"&nbsp;" * 4}что-то пошло не так: '
                f'{ACTIVATE_FAILURE_URL}\n\n{"&nbsp;" * 4}всё'
                f' нормально: {ACTIVATE_SUCCESS_URL % "&lt;token&gt;"}'
            ),
        }
    )
    def get(self, _):
        return self.handle()

    def post(self, _):
        return self.handle()

    def _create_response(self, result_data):
        if self.method == 'get':
            return HttpResponseRedirect(result_data)
        return super()._create_response(result_data)
