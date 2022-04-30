from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.controllers.token import (
    DELETEUsersTokenController,
    POSTUsersTokenController
)
from app.users.permissions import IsAuthenticatedPermission
from app.users.serializers.token import PostUsersTokenSerializer


class UsersTokenView(BaseView):
    serializer_map = {'post': PostUsersTokenSerializer}
    permissions_map = {'delete': [IsAuthenticatedPermission]}
    controller_map = {
        'post': POSTUsersTokenController, 'delete': DELETEUsersTokenController
    }
    
    def post(self, _):
        return self.handle()
    
    @response_204
    def delete(self, _):
        self.handle()
