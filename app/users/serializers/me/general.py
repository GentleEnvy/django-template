from app.base.serializers.base import BaseModelSerializer
from app.users.models import User
from app.users.enums.users import UserType


class GET_UsersMeSerializer(BaseModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'type': {'help_text': UserType.help_text}}
        read_only_fields = ['id', 'first_name', 'last_name', 'email', 'type']


class PATCH_UsersMeSerializer(BaseModelSerializer):
    class Meta:
        model = User
        write_only_fields = ['first_name', 'last_name']
