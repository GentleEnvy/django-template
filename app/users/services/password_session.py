from django.utils.crypto import get_random_string

from app.base.services.cache import Cache


class PasswordSessionService:
    def __init__(self):
        self.session_length: int = 10
        self.cache = Cache('password_session', 3600)

    def _generate_session_id(self) -> str:
        return get_random_string(self.session_length)

    def create(self, email: str) -> str:
        """:return: session_id"""
        session_id = self._generate_session_id()
        self.cache.set(email, session_id)
        return session_id

    def check(self, session_id: str) -> str | None:
        email = self.cache.get(session_id)
        if email is None:
            return None
        self.cache.delete(session_id)
        return email
