import factory
from src.models import InboundDelivery
from src.tests.factories import BaseFactory

class InboundDeliveryFactory(BaseFactory):
    class Meta:
        model = InboundDelivery