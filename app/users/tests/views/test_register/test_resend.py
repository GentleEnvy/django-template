from django.core import mail

from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.serializers.register.resend import POST_UsersRegisterResendSerializer
from app.users.tests.factories.users import UserFactory


class UsersRegisterResendTest(BaseViewTest):
    path = '/users/register/resend/'

    me_data = None

    def test_post(self):
        user = UserFactory(is_active=False)
        self._test('post', data={'email': user.email})
        self.assert_equal(len(mail.outbox), 1)
        self.assert_equal(mail.outbox[0].to, [user.email])

    def test_post_warn_404(self):
        self._test(
            'post',
            POST_UsersRegisterResendSerializer.WARNINGS[404],
            {'email': fake.email()},
        )
        self.assert_equal(len(mail.outbox), 0)

    def test_post_warn_409(self):
        user = UserFactory(is_active=True)
        self._test(
            'post',
            POST_UsersRegisterResendSerializer.WARNINGS[409],
            {'email': user.email},
        )
        self.assert_equal(len(mail.outbox), 0)
