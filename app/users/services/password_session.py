from django.core.cache import cache
from django.utils.crypto import get_random_string


class PasswordSessionService:
    SESSION_LENGTH: int = 10
    SESSION_EXPIRE: int = 3600
    SESSION_PREFIX: str = 'password_session'
    
    def _generate_session_id(self) -> str:
        return get_random_string(self.SESSION_LENGTH)
    
    def create(self, email: str) -> str:
        """:return: session_id"""
        session_id = self._generate_session_id()
        key = f'{self.SESSION_PREFIX}:{session_id}'
        cache.set(key, email, self.SESSION_EXPIRE)
        return session_id
    
    def check(self, session_id: str) -> str | None:
        key = f'{self.SESSION_PREFIX}:{session_id}'
        email = cache.get(key)
        if email is None:
            return None
        cache.delete(key)
        return email
