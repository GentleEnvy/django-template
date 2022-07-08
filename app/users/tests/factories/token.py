import factory

from app.base.tests.factories.base import BaseFactory
from app.users.models import Token
from app.users.tests.factories.users import UserFactory


class TokenFactory(BaseFactory):
    class Meta:
        model = Token

    user = factory.SubFactory(UserFactory)
