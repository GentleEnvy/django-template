from django.conf import settings
from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse
from rest_framework.response import Response
from templated_mail.mail import BaseEmailMessage

from app.base.utils.common import response_204
from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView
from app.users.models import User
from app.users.serializers.password import (
    PostUsersPasswordSerializer, PutUsersPasswordSerializer
)
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService
from app.users.services.password_session import PasswordSessionService

PASSWORD_SUCCESS_URL = settings.VERIFICATION_PASSWORD_SUCCESS_URL
PASSWORD_FAILURE_URL = settings.VERIFICATION_PASSWORD_FAILURE_URL


class UsersPasswordView(BaseView):
    serializer_map = {
        'post': PostUsersPasswordSerializer, 'put': PutUsersPasswordSerializer
    }
    
    @extend_schema(
        responses={
            200: None, 302: OpenApiResponse(
                description=f'redirect:\n\n{"&nbsp;" * 4}что-то пошло не так: '
                            f'{PASSWORD_FAILURE_URL}\n\n{"&nbsp;" * 4}всё'
                            f' нормально: {PASSWORD_SUCCESS_URL % "&lt;session_id&gt;"}'
            )
        }
    )
    def get(self, request, *args, **kwargs):
        email, code = request.query_params.get('email'), request.query_params.get('code')
        if email is None or code is None:
            return HttpResponseRedirect(PASSWORD_FAILURE_URL)
        is_confirmed, _ = EmailVerificationService(scope='password').check(email, code)
        if is_confirmed:
            session_service = PasswordSessionService()
            session_id = session_service.create(email)
            return HttpResponseRedirect(PASSWORD_SUCCESS_URL % session_id)
        return HttpResponseRedirect(PASSWORD_FAILURE_URL)
    
    @response_204
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        EmailVerificationService(scope='password').send(
            BaseEmailMessage(
                request=self.request, template_name='users/password.html', to=[email]
            )
        )
    
    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_service = PasswordSessionService()
        if (email := session_service.check(serializer.validated_data['session'])) is None:
            raise serializer.WARNINGS[408]
        user = User.objects.get(email=email)
        user.set_password(serializer.validated_data['password'])
        user.save()
        token = AuthService(request, user).login()
        return Response({'token': token})
