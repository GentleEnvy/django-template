from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse
from rest_framework.response import Response

from app.base.utils.common import response_204
from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView
from app.users.serializers.password import *
from app.users.actions.password import *


class UsersPasswordView(BaseView):
    serializer_map = {
        'post': POST_UsersPasswordSerializer,
        'put': PUT_UsersPasswordSerializer,
    }

    @extend_schema(
        responses={
            200: None,
            302: OpenApiResponse(
                description=f'redirect:\n\n'
                f'{"&nbsp;" * 4}something wrong: '
                f'{settings.VERIFICATION_PASSWORD_FAILURE_URL}\n\n'
                f'{"&nbsp;" * 4}all right: '
                f'{settings.VERIFICATION_PASSWORD_SUCCESS_URL % "&lt;session_id&gt;"}'
            ),
        }
    )
    def get(self):
        action = GET_UsersPasswordAction()
        try:
            redirect_url = action.run(
                action.InEntity(
                    email=self.request.query_params['email'],
                    code=self.request.query_params['code'],
                )
            ).url
        except KeyError:
            redirect_url = settings.VERIFICATION_PASSWORD_FAILURE_URL
        return HttpResponseRedirect(redirect_url)

    @response_204
    def post(self):
        action = POST_UsersPasswordAction()
        serializer = self.get_valid_serializer()
        action.run(action.InEntity(**serializer.validated_data))

    def put(self):
        action = PUT_UsersPasswordAction()
        serializer = self.get_valid_serializer()
        try:
            token = action.run(
                action.InEntity(request=self.request, **serializer.validated_data)
            ).token
        except TimeoutError:
            raise serializer.WARNINGS[408]
        return Response({'token': token})
