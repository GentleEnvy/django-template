from django.forms import model_to_dict
from parameterized import parameterized

from app.base.tests.fakers import fake
from app.base.tests.views.base import BaseViewTest
from app.users.models import User


class UsersMeTest(BaseViewTest):
    path = '/users/me/'

    def test_get(self):
        self._test(
            'get',
            dict(
                filter(
                    lambda item: item[0]
                    in ['id', User.USERNAME_FIELD, 'type', 'first_name', 'last_name'],
                    model_to_dict(self.me).items(),
                )
            ),
        )

    @parameterized.expand(
        [
            [{'first_name': fake.first_name(), 'last_name': fake.last_name()}],
            [{'first_name': fake.first_name()}],
            [{'last_name': fake.last_name()}],
            [{}],
        ]
    )
    def test_patch(self, data):
        self._test('patch', {}, data)
        self.assert_model(User, data)
