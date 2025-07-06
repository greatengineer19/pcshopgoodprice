import factory
from src.models import Inventory
from src.tests.factories import BaseFactory

class InventoryFactory(BaseFactory):
    class Meta:
        model = Inventory