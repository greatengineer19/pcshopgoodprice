import factory
from src.models import SalesDeliveryLine
from src.tests.factories import BaseFactory

class SalesDeliveryLineFactory(BaseFactory):
    class Meta:
        model = SalesDeliveryLine