from rest_framework import serializers

from app.users.models import User

__all__ = ['BaseSerializer', 'EmptySerializer']


class BaseSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EmptySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = []
