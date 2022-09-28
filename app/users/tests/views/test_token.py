from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.models import Token
from app.users.enums.users import UserType
from app.users.serializers.token import POST_UsersTokenSerializer


class UsersTokenTest(BaseViewTest):
    path = '/users/token/'

    def test_post(self):
        self.me.auth_token.delete()
        self._test(
            'post',
            {
                'token': lambda token: self.assert_model(
                    Token, {'key': token}, user_id=self.me.id
                )
            },
            {'email': self.me.email, 'password': self.me.raw_password},
        )

    def test_post_warn_401_0(self):
        self.me.auth_token.delete()
        self._test(
            'post',
            POST_UsersTokenSerializer.WARNINGS[401],
            {'email': self.me.email, 'password': fake.password()},
        )
        self.assert_equal(Token.objects.count(), 0)

    def test_post_warn_401_1(self):
        del self.me
        self._test(
            'post',
            POST_UsersTokenSerializer.WARNINGS[401],
            {'email': fake.email(), 'password': fake.password()},
        )
        self.assert_equal(Token.objects.count(), 0)

    def test_post_warn_401_2(self):
        self.me.auth_token.delete()
        self.me.is_active = False
        self.me.save()
        self._test(
            'post',
            POST_UsersTokenSerializer.WARNINGS[401],
            {'email': self.me.email, 'password': self.me.raw_password},
        )
        self.assert_equal(Token.objects.count(), 0)

    def test_post_warn_401_3(self):
        self.me.auth_token.delete()
        self.me.type = UserType.BANNED
        self.me.save()
        self._test(
            'post',
            POST_UsersTokenSerializer.WARNINGS[401],
            {'email': self.me.email, 'password': self.me.raw_password},
        )
        self.assert_equal(Token.objects.count(), 0)

    def test_delete(self):
        self._test('delete')
        self.assert_equal(Token.objects.count(), 0)
