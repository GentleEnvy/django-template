from django.conf import settings
from django.contrib.auth import login, logout

from app.users.models import User, Token
from app.base.logs import debug


class AuthService:
    def __init__(self, request, user=None):
        self.request = request
        self.user = user or request.user
    
    def login(self) -> str:
        token = Token.objects.get_or_create(user=self.user)[0].key
        if settings.SESSION_ON_LOGIN:
            try:
                login(self.request, self.user)
            except ValueError as e:
                debug(e)
        return token
    
    def logout(self) -> None:
        self.delete_token(self.user)
        if settings.SESSION_ON_LOGIN:
            logout(self.request)
    
    @classmethod
    def delete_token(cls, user) -> None:
        Token.objects.filter(user=user).delete()
