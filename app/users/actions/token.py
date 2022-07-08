from app.base.actions.base import BaseAction
from app.users.services.auth import AuthService


class POST_UsersTokenAction(BaseAction):
    def run(self, data):
        return {
            'token': AuthService(
                self.view.request, self.view.serializer.instance
            ).login()
        }


class DELETE_UsersTokenAction(BaseAction):
    def run(self, data):
        AuthService(self.view.request).logout()
