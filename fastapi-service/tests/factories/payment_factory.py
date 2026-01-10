import factory
from src.infrastructure.persistence.models.payment import Payment
from src.domain.payment.value_objects.currency import CurrencyEnum
from src.domain.payment.value_objects.payment_method import PaymentMethod
from tests.factories import BaseFactory

class PaymentFactory(BaseFactory):
    class Meta:
        model = Payment

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        if 'currency' in kwargs:
            kwargs['currency'] = CurrencyEnum.from_value(kwargs['currency']).value

        if 'payment_method' in kwargs:
            kwargs['payment_method'] = PaymentMethod.from_value(kwargs['payment_method']).value

        return kwargs
    