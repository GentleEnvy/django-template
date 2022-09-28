from django.conf import settings
from django.contrib.auth import login, logout

from app.base.logs import warning
from app.users.models import Token, User


class AuthService:
    def __init__(self):
        self.token_manager = Token.objects
    
    def login(self, user: User, request=None) -> Token:
        token = self.token_manager.get_or_create(user=user)[0]
        if settings.SESSION_ON_LOGIN:
            try:
                login(request, user)
            except ValueError as e:
                warning(e)
        return token

    def logout(self, user: User, request=None) -> None:
        self.token_manager.filter(user=user).delete()
        if settings.SESSION_ON_LOGIN:
            try:
                logout(request)
            except ValueError as e:
                warning(e)
