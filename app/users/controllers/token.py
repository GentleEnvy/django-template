from app.base.controllers.base import BaseController
from app.users.services.auth import AuthService


class POST_UsersTokenController(BaseController):
    def control(self, data):
        return {
            'token': AuthService(self.view.request, self.view.serializer.instance).login()
        }


class DELETE_UsersTokenController(BaseController):
    def control(self, data):
        AuthService(self.view.request).logout()
