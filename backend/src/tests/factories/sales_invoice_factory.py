import factory
from src.models import SalesInvoice
from src.tests.factories import BaseFactory

class SalesInvoiceFactory(BaseFactory):
    class Meta:
        model = SalesInvoice