import factory
from src.infrastructure.persistence.models.payment import Payment
from tests.factories import BaseFactory

class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment