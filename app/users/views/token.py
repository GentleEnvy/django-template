from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.permissions import IsAuthenticatedPermission
from app.users.serializers.token import *
from app.users.actions.token import *


class UsersTokenView(BaseView):
    serializer_map = {'post': POST_UsersTokenSerializer}
    action_map = {'post': POST_UsersTokenAction, 'delete': DELETE_UsersTokenAction}
    permissions_map = {'delete': [IsAuthenticatedPermission]}

    def post(self, _):
        return self.handle()

    @response_204
    def delete(self, _):
        self.handle()
