from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.models import User
from app.users.serializers.me.password import PUT_UsersMePasswordSerializer


class UsersMePasswordTest(BaseViewTest):
    path = '/users/me/password/'

    def test_put(self):
        new_password = fake.password()
        self._test(
            'put',
            {},
            {'old_password': self.me.raw_password, 'new_password': new_password},
        )
        self.assert_true(User.objects.get(id=self.me.id).check_password(new_password))

    def test_put_warn_403(self):
        password = self.me.raw_password
        self._test(
            'put',
            PUT_UsersMePasswordSerializer.WARNINGS[403],
            {'old_password': fake.password(), 'new_password': fake.password()},
        )
        self.assert_true(self.me.check_password(password))
