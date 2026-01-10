import factory
from src.models import SalesDeliveryLine
from tests.factories import BaseFactory

class SalesDeliveryLineFactory(BaseFactory):
    class Meta:
        model = SalesDeliveryLine