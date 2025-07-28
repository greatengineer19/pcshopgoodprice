import factory
from src.models import InboundDeliveryAttachment
from tests.factories import BaseFactory

class InboundDeliveryAttachmentFactory(BaseFactory):
    class Meta:
        model = InboundDeliveryAttachment