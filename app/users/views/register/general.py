from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse
from rest_framework.response import Response

from app.base.utils.common import response_201
from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView
from app.users.serializers.register.general import *
from app.users.actions.register.general import *


class UsersRegisterView(BaseView):
    serializer_map = {'post': POST_UsersRegisterSerializer}

    @extend_schema(
        responses={
            200: None,
            302: OpenApiResponse(
                description=(
                    f'redirect:\n\n'
                    f'{"&nbsp;" * 4}something wrong: '
                    f'{settings.VERIFICATION_ACTIVATE_FAILURE_URL}\n\n'
                    f'{"&nbsp;" * 4}all right: '
                    f'{settings.VERIFICATION_ACTIVATE_SUCCESS_URL % "&lt;token&gt;"}'
                )
            ),
        }
    )
    def get(self):
        action = GET_UsersRegisterAction()
        try:
            redirect_url = action.run(
                action.InEntity(
                    request=self.request,
                    email=self.request.query_params['email'],
                    code=self.request.query_params['code'],
                )
            ).url
        except KeyError:
            redirect_url = settings.VERIFICATION_ACTIVATE_FAILURE_URL
        return HttpResponseRedirect(redirect_url)

    @response_201
    def post(self):
        action = POST_UsersRegisterAction()
        serializer = self.get_valid_serializer()
        serializer.instance = action.run(action.InEntity(**serializer.validated_data))
        return Response(serializer.data, status=201)
