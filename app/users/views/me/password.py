from django.conf import settings
from django.contrib.auth import login
from rest_framework.mixins import UpdateModelMixin

from app.base.views.base import BaseView
from app.users.serializers.me.password import *


class UsersMePasswordView(UpdateModelMixin, BaseView):
    serializer_map = {'put': PUT_UsersMePasswordSerializer}

    def put(self, request):
        result = self.update(request)
        if settings.SESSION_ON_LOGIN:
            login(request, request.user)
        return result

    def get_object(self):
        return self.request.user
