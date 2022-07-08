from unittest import mock

from django.conf import settings
from django.core import mail
from parameterized import parameterized

from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.models import User
from app.users.serializers.password import (
    POST_UsersPasswordSerializer,
    PUT_UsersPasswordSerializer,
)
from app.users.services.email_verification import EmailVerificationService
from app.users.services.password_session import PasswordSessionService
from app.users.tests.factories.token import TokenFactory
from app.users.tests.factories.users import UserFactory


class UsersPasswordTest(BaseViewTest):
    path = '/users/password/'

    me_data = None

    def test_get(self):
        session_id = fake.random_string()
        with mock.patch.object(
            EmailVerificationService, 'check', return_value=True
        ), mock.patch.object(
            PasswordSessionService, '_generate_session_id', return_value=session_id
        ):
            response = self.get(
                query={'code': fake.random_string(), 'email': fake.email()}
            )
        self.assert_equal(response.status_code, 302)
        self.assert_equal(
            response.url, settings.VERIFICATION_PASSWORD_SUCCESS_URL % session_id
        )
        self.assert_true(PasswordSessionService().check(session_id))

    def test_get_fail_check_false(self):
        session_id = fake.random_string()
        with mock.patch.object(
            EmailVerificationService, 'check', return_value=False
        ), mock.patch.object(
            PasswordSessionService, '_generate_session_id', return_value=session_id
        ):
            response = self.get(
                query={'code': fake.random_string(), 'email': fake.email()}
            )
        self.assert_equal(response.status_code, 302)
        self.assert_equal(response.url, settings.VERIFICATION_PASSWORD_FAILURE_URL)
        self.assert_false(PasswordSessionService().check(session_id))

    @parameterized.expand(
        [[{'code': fake.random_string()}], [{'email': fake.email()}], [{}]]
    )
    def test_get_fail_invalid_query(self, query):
        session_id = fake.random_string()
        with mock.patch.object(
            EmailVerificationService, 'check', return_value=True
        ), mock.patch.object(
            PasswordSessionService, '_generate_session_id', return_value=session_id
        ):
            response = self.get(query=query)
        self.assert_equal(response.status_code, 302)
        self.assert_equal(response.url, settings.VERIFICATION_PASSWORD_FAILURE_URL)
        self.assert_false(PasswordSessionService().check(session_id))

    def test_post(self):
        email = UserFactory().email
        code = fake.random_string()
        with mock.patch.object(
            EmailVerificationService, '_generate_code', return_value=code
        ):
            self._test('post', data={'email': email})
        self.assert_equal(len(mail.outbox), 1)
        self.assert_equal(mail.outbox[0].to, [email])
        self.assert_true(EmailVerificationService(scope='password').check(email, code))

    def test_post_warn_404(self):
        email = fake.email()
        code = fake.random_string()
        with mock.patch.object(
            EmailVerificationService, '_generate_code', return_value=code
        ):
            self._test(
                'post', POST_UsersPasswordSerializer.WARNINGS[404], {'email': email}
            )
        self.assert_equal(len(mail.outbox), 0)
        self.assert_false(EmailVerificationService(scope='password').check(email, code))

    def test_put(self):
        token = TokenFactory()
        new_password = fake.password()
        with mock.patch.object(
            PasswordSessionService, 'check', return_value=token.user.email
        ):
            self._test(
                'put',
                {'token': token.key},
                {'session_id': fake.random_string(), 'new_password': new_password},
            )
        self.assert_true(User.objects.get().check_password(new_password))

    def test_put_warn_408(self):
        with mock.patch.object(PasswordSessionService, 'check', return_value=None):
            self._test(
                'put',
                PUT_UsersPasswordSerializer.WARNINGS[408],
                {'session_id': fake.random_string(), 'new_password': fake.password()},
            )
