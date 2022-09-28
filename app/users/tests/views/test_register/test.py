from functools import partial
from unittest import mock

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core import mail
from parameterized import parameterized

from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.models import Token, User
from app.users.enums.users import UserType
from app.users.serializers.register import POST_UsersRegisterSerializer
from app.users.services.email_verification import EmailVerificationService
from app.users.tests.factories.users import UserFactory


class UsersRegisterTest(BaseViewTest):
    path = '/users/register/'

    me_data = None

    @parameterized.expand([[{'email': fake.email(), 'password': fake.password()}]])
    def test_post(self, data):
        def check_id(id):
            self.assert_model(
                User,
                data
                | {
                    'password': partial(check_password, data['password']),
                    'is_active': False,
                    'type': UserType.DEFAULT.value,
                },
                id=id,
            )

        email_verification = EmailVerificationService(scope='register')
        code = fake.random_string(email_verification.code_length)
        with mock.patch.object(
            EmailVerificationService, '_generate_code', return_value=code
        ):
            self._test('post', {'id': check_id}, data)
        self.assert_equal(len(mail.outbox), 1)
        self.assert_equal(mail.outbox[0].to, [data['email']])
        self.assert_true(email_verification.check(data['email'], code))

    def test_post_warn_409(self):
        user = UserFactory()
        self._test(
            'post',
            POST_UsersRegisterSerializer.WARNINGS[409],
            {'email': user.email, 'password': fake.password()},
        )

    def test_get(self):
        with mock.patch.object(EmailVerificationService, 'check', return_value=True):
            user = UserFactory(is_active=False)
            response = self.get(query={'email': user.email, 'code': 'valid_code'})
            token = self.assert_model(Token, {}, user=user)
            self.assert_response(response, 302)
            self.assert_equal(
                response.url, settings.VERIFICATION_ACTIVATE_SUCCESS_URL % token.key
            )
            self.assert_model(User, {'is_active': True})

    def test_get_fail_check_false(self):
        with mock.patch.object(EmailVerificationService, 'check', return_value=False):
            user = UserFactory(is_active=False)
            response = self.get(query={'email': user.email, 'code': 'valid_code'})
            self.assert_response(response, 302)
            self.assert_equal(response.url, settings.VERIFICATION_ACTIVATE_FAILURE_URL)
            self.assert_model(User, {'is_active': False})

    def test_get_fail_no_user(self):
        response = self.get(query={'email': fake.email(), 'code': 'valid_code'})
        self.assert_response(response, 302)
        self.assert_equal(response.url, settings.VERIFICATION_ACTIVATE_FAILURE_URL)

    @parameterized.expand([[{'email': fake.email()}], [{'code': 'valid_code'}], [{}]])
    def test_get_fail_query(self, query):
        with mock.patch.object(EmailVerificationService, 'check', return_value=True):
            UserFactory(email=query.get('email', fake.email()), is_active=False)
            response = self.get(query=query)
            self.assert_response(response, 302)
            self.assert_equal(response.url, settings.VERIFICATION_ACTIVATE_FAILURE_URL)
            self.assert_model(User, {'is_active': False})
