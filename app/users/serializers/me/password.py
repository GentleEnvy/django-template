from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from app.base.exceptions import APIWarning
from app.base.serializers.base import BaseModelSerializer
from app.users.models import User


class PUT_UsersMePasswordSerializer(BaseModelSerializer):
    WARNINGS = {403: APIWarning("Invalid old password", 403, 'invalid_old_password')}

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    def validate(self, attrs):
        user = self.instance
        validate_password(attrs['new_password'])
        if not user.check_password(attrs['old_password']):
            raise self.WARNINGS[403]
        return attrs

    def update(self, user, validated_data):
        user.set_password(validated_data['new_password'])
        user.save()
        return user
