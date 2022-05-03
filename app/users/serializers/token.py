from django.contrib.auth import authenticate
from rest_framework import serializers

from app.base.exceptions import APIWarning
from app.base.schemas.mixins import SerializerSchemaMixin
from app.users.models import User
from app.users.models.choices import UserType


class POST_UsersTokenSerializer(SerializerSchemaMixin, serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    
    WARNINGS = {
        401: APIWarning('Неверный пароль', 401, 'invalid_password'),
        404: APIWarning(
            'Пользователя с таким email не существует', 404, 'email_not_found'
        ),
        406: APIWarning('Пользователь не верифицирован', 406, 'not_verified'),
        410: APIWarning('Пользователь забанен', 410, 'banned')
    }
    
    class Meta:
        model = User
        extra_kwargs = {
            'email': {'write_only': True, 'validators': []},
            'password': {'write_only': True}, 'token': {}
        }
        fields = list(extra_kwargs.keys())
    
    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user: User = authenticate(
            request=self.context.get('request'), email=email, password=password
        )
        if user is None:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise self.WARNINGS[404]
        if not user.check_password(password):
            raise self.WARNINGS[401]
        if user.type == UserType.BANNED:
            raise self.WARNINGS[410]
        if not user.is_active:
            raise self.WARNINGS[406]
        self.instance = user
        return attrs
