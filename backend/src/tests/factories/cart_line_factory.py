import factory
from src.models import CartLine
from src.tests.factories import BaseFactory

class CartLineFactory(BaseFactory):
    class Meta:
        model = CartLine