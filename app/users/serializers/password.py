from rest_framework import serializers

from app.base.exceptions import APIWarning
from app.base.serializers.base import BaseModelSerializer
from app.users.models import User


class POST_UsersPasswordSerializer(BaseModelSerializer):
    WARNINGS = {
        404: APIWarning(
            "User with this email not found",
            404,
            'password_forgot_email_not_found',
        )
    }

    class Meta:
        model = User
        write_only_fields = ['email']

    def validate(self, attrs):
        user_manager = User.objects
        if not user_manager.filter(email=attrs['email']).exists():
            raise self.WARNINGS[404]
        return attrs


class PUT_UsersPasswordSerializer(BaseModelSerializer):
    WARNINGS = {408: APIWarning("Session has expired", 408, 'password_session_timeout')}

    session_id = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        extra_kwargs = {'new_password': {'write_only': True, 'source': 'password'}}
        fields = ['session_id', 'new_password', 'token']
