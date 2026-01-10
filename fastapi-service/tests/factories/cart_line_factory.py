import factory
from src.models import CartLine
from tests.factories import BaseFactory

class CartLineFactory(BaseFactory):
    class Meta:
        model = CartLine