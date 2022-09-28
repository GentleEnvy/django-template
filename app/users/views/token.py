from rest_framework.fields import CharField
from rest_framework.response import Response

from app.base.utils.common import response_204
from app.base.utils.schema import extend_schema, schema_serializer
from app.base.views.base import BaseView
from app.users.permissions import IsAuthenticatedPermission
from app.users.serializers.token import *
from app.users.actions.token import *


class UsersTokenView(BaseView):
    serializer_map = {'post': POST_UsersTokenSerializer}
    permissions_map = {'delete': [IsAuthenticatedPermission]}

    @extend_schema(
        responses={
            201: schema_serializer('POST_UsersToken', token=CharField(read_only=True))
        }
    )
    def post(self):
        action = POST_UsersTokenAction()
        serializer = self.get_valid_serializer()
        try:
            serializer.instance = action.run(
                action.InEntity(**serializer.validated_data, request=self.request)
            ).dict()
        except PermissionError:
            raise serializer.WARNINGS[401]
        return Response(serializer.data, status=201)

    @response_204
    def delete(self):
        action = DELETE_UsersTokenAction()
        action.run(action.InEntity(user=self.request.user, request=self.request))
