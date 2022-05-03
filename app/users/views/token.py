from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.permissions import IsAuthenticatedPermission


class UsersTokenView(BaseView):
    permissions_map = {'delete': [IsAuthenticatedPermission]}
    
    def post(self, _):
        return self.handle()
    
    @response_204
    def delete(self, _):
        self.handle()
