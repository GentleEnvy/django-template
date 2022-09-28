from typing import Final

from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import get_random_string
from templated_mail.mail import BaseEmailMessage


# FIXME: django cache -> Cache
class EmailVerificationService:
    CACHE_PREFIX = 'verification'

    def __init__(self, code_length: int = 10, scope: str = ''):
        self.code_length: Final[int] = code_length
        self.scope: Final[str] = scope

    def _update_context(self, email_message: BaseEmailMessage):
        context = email_message.context
        for k, v in settings.__dict__.items():
            if k.startswith('VERIFICATION_'):
                context.setdefault(k.lower()[13:])
        email = email_message.to[0]
        email_message.context.setdefault('email', email)
        email_message.context.setdefault('code', self._get_cached_code(email))

    def _get_cache_key(self, email: str) -> str:
        return f'{self.CACHE_PREFIX}:{self.scope}:{email}'

    def _generate_code(self):
        return get_random_string(self.code_length)

    def _get_cached_code(self, email: str) -> str:
        code = self._generate_code()
        cache.set(self._get_cache_key(email), code, settings.VERIFICATION_CODE_TIMEOUT)
        return code

    def send(self, email_message: BaseEmailMessage) -> None:
        self._update_context(email_message)
        email_message.send(email_message.to)

    def check(self, email: str, code: str) -> bool:
        if (cached_code := cache.get(self._get_cache_key(email))) is None:
            return False
        if cached_code == code:
            cache.delete(email)
            return True
        return False
