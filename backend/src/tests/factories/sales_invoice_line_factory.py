import factory
from src.models import SalesInvoiceLine
from src.tests.factories import BaseFactory

class SalesInvoiceLineFactory(BaseFactory):
    class Meta:
        model = SalesInvoiceLine