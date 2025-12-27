import factory
from src.models import PaymentMethod
from tests.factories import BaseFactory

class PaymentMethodFactory(BaseFactory):
    class Meta:
        model = PaymentMethod