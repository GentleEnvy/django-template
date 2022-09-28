from app.base.exceptions import APIWarning
from app.base.serializers.base import BaseModelSerializer
from app.users.models import User


class POST_UsersRegisterResendSerializer(BaseModelSerializer):
    WARNINGS = {
        404: APIWarning(
            'Пользователь с таким email не регистрировался',
            404,
            'register_resend_email_not_found',
        ),
        409: APIWarning(
            'Пользователь уже верифицирован', 409, 'register_resend_already_verified'
        ),
    }

    class Meta:
        model = User
        extra_kwargs = {'email': {'write_only': True, 'validators': []}}
        fields = list(extra_kwargs.keys())

    def validate(self, attrs):
        try:
            self.instance = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise self.WARNINGS[404]
        if self.instance.is_active:
            raise self.WARNINGS[409]
        return attrs
