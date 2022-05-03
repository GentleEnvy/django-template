from rest_framework import serializers

from app.users.models import User
from app.users.models.choices import UserType


class GET_UsersMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'type': {'help_text': UserType.help_text}}
        fields = ['id', 'first_name', 'last_name', 'email', 'type']


class PATCH_UsersMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        wo = {'write_only': True}
        extra_kwargs = {'id': {}, 'first_name': wo, 'last_name': wo}
        fields = list(extra_kwargs.keys())
