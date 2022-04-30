from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from drf_spectacular.utils import OpenApiResponse
from rest_framework.mixins import CreateModelMixin
from templated_mail.mail import BaseEmailMessage

from app.base.utils.common import response_204
from app.base.utils.schema import extend_schema
from app.base.views.base import BaseView
from app.users.models import User
from app.users.serializers.register import (
    PostUsersRegisterResendSerializer, PostUsersRegisterSerializer
)
from app.users.services.auth import AuthService
from app.users.services.email_verification import EmailVerificationService

ACTIVATE_SUCCESS_URL = settings.VERIFICATION_ACTIVATE_SUCCESS_URL
ACTIVATE_FAILURE_URL = settings.VERIFICATION_ACTIVATE_FAILURE_URL


class UsersRegisterView(CreateModelMixin, BaseView):
    serializer_map = {'post': PostUsersRegisterSerializer}
    
    @extend_schema(
        responses={
            200: None, 302: OpenApiResponse(
                description=f'redirect:\n\n{"&nbsp;" * 4}что-то пошло не так: '
                            f'{ACTIVATE_FAILURE_URL}\n\n{"&nbsp;" * 4}'
                            rf'всё нормально: {ACTIVATE_SUCCESS_URL % "&lt;token&gt;"}'
            )
        }
    )
    def get(self, request):
        email, code = request.query_params.get('email'), request.query_params.get('code')
        if email is None or code is None:
            return HttpResponseRedirect(ACTIVATE_FAILURE_URL)
        if EmailVerificationService(scope='register').check(email, code)[0]:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            token = AuthService(request, user).login()
            return HttpResponseRedirect(ACTIVATE_SUCCESS_URL % token)
        return HttpResponseRedirect(ACTIVATE_FAILURE_URL)
    
    def post(self, request):
        return self.create(request)
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        EmailVerificationService(scope='register').send(
            BaseEmailMessage(
                request=self.request, template_name='users/activation.html',
                to=[serializer.instance.email]
            )
        )


class UsersRegisterResendView(BaseView):
    serializer_map = {'post': PostUsersRegisterResendSerializer}
    
    @response_204
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        EmailVerificationService(scope='register').send(
            BaseEmailMessage(
                request=self.request, template_name='users/activation.html',
                to=[serializer.instance.email], context={'path': reverse('register')}
            )
        )
