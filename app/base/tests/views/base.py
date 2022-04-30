from typing import Any, Callable
from urllib.parse import urlencode

from app.base.exceptions.base import APIException
from app.base.tests.base import BaseTest
from app.users.models import User
from app.users.tests.factories.token import TokenFactory
from app.users.tests.factories.users import UserFactory


class BaseViewTest(BaseTest):
    path: str
    
    me_class: Callable[..., User] = UserFactory
    me_data: dict[str, Any] | None = {}
    
    def setUp(self):
        super().setUp()
        if self.me_data is None:
            self._me = None
        else:
            self.me = self.me_class(**self.me_data)
    
    @property
    def me(self) -> User | None:
        return self._me
    
    @me.setter
    def me(self, me):
        self._me = me
        self.client.force_login(self.me)
        self.me.token = TokenFactory(user=self.me)
    
    @me.deleter
    def me(self):
        self.client.logout()
        self._me.token.delete()
        self._me.delete()
        self._me = None
    
    def get(self, path=None, query=None):
        return self.client.get(f'{path}?{urlencode(query or {})}')
    
    def post(self, path=None, data=None):
        return self.client.post(path or self.path, data)
    
    def put(self, path=None, data=None):
        return self.client.put(path or self.path, data)
    
    def patch(self, path=None, data=None):
        return self.client.patch(path or self.path, data)
    
    def delete(self, path=None, data=None):
        return self.client.delete(path or self.path, data)
    
    def assert_response(self, response, status=200, data: dict = None):
        self.assert_equal(response.status_code, status)
        self.assert_json(response.json() if response.content else {}, data or {})
    
    def _test(
        self, method: str, exp_data: dict[str, Any] = None, data: dict[str, Any] = None,
        status: int = None, path: str = None
    ):
        status = status or {'post': 201, 'delete': 204}.get(method, 200)
        self.assert_response(getattr(self, method)(path, data), status, exp_data)
    
    def _test_api_exception(
        self, method: str, api_exception: APIException, data: dict[str, Any] = None,
        path: str = None
    ):
        self._test(method, api_exception.serialize(), data, api_exception.status, path)
