import factory
from src.infrastructure.persistence.models.account import Account
from tests.factories import BaseFactory

class AccountFactory(BaseFactory):
    class Meta:
        model = Account