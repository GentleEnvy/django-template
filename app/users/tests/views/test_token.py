from app.users.models import Token
from app.base.tests.views.base import BaseViewTest
from app.users.tests.factories.users import UserFactory


class UsersTokenTest(BaseViewTest):
    path = '/users/token/'
    
    def test_post(self):
        del self.me
        user = UserFactory()
        self.assert_equal(Token.objects.count(), 0)
        self._test(
            'post', {
                'token': lambda token: self.assert_model(
                    Token, {'key': token}, user_id=user.id
                )
            }, {'email': user.email, 'password': user.raw_password}
        )
    
    def test_delete(self):
        self.assert_equal(Token.objects.count(), 1)
        self._test('delete')
        self.assert_equal(Token.objects.count(), 0)
