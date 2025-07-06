import factory
from src.models import InboundDeliveryAttachment
from src.tests.factories import BaseFactory

class InboundDeliveryAttachmentFactory(BaseFactory):
    class Meta:
        model = InboundDeliveryAttachment