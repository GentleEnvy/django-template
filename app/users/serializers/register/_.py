from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from app.base.exceptions import APIWarning
from app.base.schemas.mixins import SerializerSchemaMixin
from app.users.models import User


class _EmailUniqueValidator(UniqueValidator):
    def __call__(self, value, serializer_field):
        try:
            super().__call__(value, serializer_field)
        except ValidationError:
            raise POST_UsersRegisterSerializer.WARNINGS[409]


class POST_UsersRegisterSerializer(SerializerSchemaMixin, serializers.ModelSerializer):
    WARNINGS = {
        409: APIWarning('User с таким email уже существует', 409, 'register_email_unique')
    }
    
    class Meta:
        model = User
        extra_kwargs = {
            'email': {
                'validators': [_EmailUniqueValidator(queryset=User.objects.all())],
                'write_only': True
            }, 'password': {'write_only': True}, 'first_name': {'write_only': True},
            'last_name': {'write_only': True}, 'id': {}
        }
        fields = list(extra_kwargs.keys())
    
    def validate(self, attrs):
        validate_password(attrs['password'], User(**attrs))
        return attrs
