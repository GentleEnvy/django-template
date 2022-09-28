from app.base.utils.common import response_204
from app.base.views.base import BaseView
from app.users.serializers.me.general import *


class UsersMeView(BaseView):
    serializer_map = {'get': GET_UsersMeSerializer, 'patch': PATCH_UsersMeSerializer}

    def get(self):
        return self.retrieve()

    @response_204
    def patch(self):
        return self.update()

    def get_object(self):
        return self.request.user
