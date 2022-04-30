from django.conf import settings
from django.contrib.auth import login
from rest_framework.mixins import UpdateModelMixin

from app.base.utils.common import response_204
from app.users.serializers.me.password import PutUsersMePasswordSerializer
from app.users.views.base import BaseAuthView


class UsersMePasswordView(UpdateModelMixin, BaseAuthView):
    serializer_map = {'put': PutUsersMePasswordSerializer}
    
    @response_204
    def put(self, request):
        self.update(request)
        if settings.SESSION_ON_LOGIN:
            login(request, request.user)
    
    def get_object(self):
        return self.request.user
