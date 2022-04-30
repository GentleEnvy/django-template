from functools import partial

from django.contrib.auth.hashers import check_password
from parameterized import parameterized

from app.base.tests.views.base import BaseViewTest
from app.users.models import User
from app.users.models.choices import UserType
from app.users.serializers.register import PostUsersRegisterSerializer
from app.users.tests.factories.users import UserFactory

fake = BaseViewTest.fake


class UsersRegisterTest(BaseViewTest):
    path = '/users/register/'
    
    me_data = None
    
    @parameterized.expand(
        [
            [{'email': fake.email(), 'password': fake.password()}],
            [{
                'email': fake.email(), 'password': fake.password(),
                'first_name': fake.first_name()
            }],
            [{
                'email': fake.email(), 'password': fake.password(),
                'last_name': fake.last_name()
            }],
            [{
                'email': fake.email(), 'password': fake.password(),
                'first_name': fake.first_name(), 'last_name': fake.last_name()
            }]
        ]
    )
    def test_post(self, data):
        def check_id(id):
            self.assert_model(
                User, data | {
                    'password': partial(check_password, data['password']),
                    'is_active': False, 'type': UserType.DEFAULT.value,
                    'first_name': data.get('first_name'),
                    'last_name': data.get('last_name')
                }, id=id
            )
        
        self._test('post', {'id': check_id}, data)
    
    def test_warn_409(self):
        email = self.fake.email()
        UserFactory(email=email)
        self._test_api_exception(
            'post', PostUsersRegisterSerializer.WARNINGS[409],
            {'email': email, 'password': self.fake.password()}
        )
