from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.controllers.token import (
    POST_UsersTokenController, DELETE_UsersTokenController
)
from app.users.permissions import IsAuthenticatedPermission
from app.users.serializers.token import POST_UsersTokenSerializer


class UsersTokenView(BaseView):
    serializer_map = {'post': POST_UsersTokenSerializer}
    permissions_map = {'delete': [IsAuthenticatedPermission]}
    controller_map = {
        'post': POST_UsersTokenController, 'delete': DELETE_UsersTokenController
    }
    
    def post(self, _):
        return self.handle()
    
    @response_204
    def delete(self, _):
        self.handle()
