import factory
from src.models import User
from tests.factories import BaseFactory

class UserFactory(BaseFactory):
    class Meta:
        model = User