from typing import Any

from django.core.cache import cache


class Cache:
    _NOTSET = object()

    def __init__(self, scope: str = '_', timeout: int = _NOTSET, default: Any = None):
        self.scope = scope
        self.default = default
        self.timeout = timeout

    def cache_key(self, *keys: str) -> str:
        return f'cache:{self.scope}-{"-".join(keys)}'

    def get(self, *keys: str, default: int = _NOTSET) -> Any:
        cache_default = self.default if default is self._NOTSET else default
        if cache_default is self._NOTSET:
            return cache.get(self.cache_key(*keys))
        return cache.get(self.cache_key(*keys), default=cache_default)

    def set(self, value, *keys: str, timeout: int = _NOTSET) -> None:
        cache_timeout = self.timeout if timeout is self._NOTSET else timeout
        if cache_timeout is self._NOTSET:
            cache.set(self.cache_key(*keys), value)
        else:
            cache.set(self.cache_key(*keys), value, timeout=cache_timeout)

    def delete(self, *keys: str) -> None:
        cache.delete(self.cache_key(*keys))
