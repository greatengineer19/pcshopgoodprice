import factory
from src.models import InboundDeliveryLine
from tests.factories import BaseFactory

class InboundDeliveryLineFactory(BaseFactory):
    class Meta:
        model = InboundDeliveryLine