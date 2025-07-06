import factory
from src.models import PaymentMethod
from src.tests.factories import BaseFactory

class PaymentMethodFactory(BaseFactory):
    class Meta:
        model = PaymentMethod