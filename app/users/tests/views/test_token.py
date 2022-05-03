from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.models import Token
from app.users.models.choices import UserType
from app.users.serializers.token import POST_UsersTokenSerializer
from app.users.tests.factories.users import UserFactory


class UsersTokenTest(BaseViewTest):
    path = '/users/token/'
    
    def test_post(self):
        self.me.auth_token.delete()
        self._test(
            'post', {
                'token': lambda token: self.assert_model(
                    Token, {'key': token}, user_id=self.me.id
                )
            }, {'email': self.me.email, 'password': self.me.raw_password}
        )
    
    def test_post_warn_401(self):
        self.me.auth_token.delete()
        self._test(
            'post', POST_UsersTokenSerializer.WARNINGS[401],
            {'email': self.me.email, 'password': fake.password()}
        )
        self.assert_equal(Token.objects.count(), 0)
    
    def test_post_warn_404(self):
        del self.me
        self._test(
            'post', POST_UsersTokenSerializer.WARNINGS[404],
            {'email': fake.email(), 'password': fake.password()}
        )
        self.assert_equal(Token.objects.count(), 0)
    
    def test_post_warn_406(self):
        self.me.auth_token.delete()
        self.me.is_active = False
        self.me.save()
        self._test(
            'post', POST_UsersTokenSerializer.WARNINGS[406],
            {'email': self.me.email, 'password': self.me.raw_password}
        )
        self.assert_equal(Token.objects.count(), 0)
    
    def test_post_warn_410(self):
        self.me.auth_token.delete()
        self.me.type = UserType.BANNED
        self.me.save()
        self._test(
            'post', POST_UsersTokenSerializer.WARNINGS[410],
            {'email': self.me.email, 'password': self.me.raw_password}
        )
        self.assert_equal(Token.objects.count(), 0)
    
    def test_delete(self):
        self.me = UserFactory()
        self._test('delete')
        self.assert_equal(Token.objects.count(), 0)
