from rest_framework import serializers

from app.base.exceptions import APIWarning
from app.base.serializers.base import BaseModelSerializer
from app.users.models import User


class POST_UsersTokenSerializer(BaseModelSerializer):
    WARNINGS = {
        401: APIWarning("Invalid email or password", 401, 'invalid_email_or_password')
    }

    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        write_only_fields = ['email', 'password']
        read_only_fields = ['token']
