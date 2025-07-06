import factory
from src.models import SalesDelivery
from src.tests.factories import BaseFactory

class SalesDeliveryFactory(BaseFactory):
    class Meta:
        model = SalesDelivery