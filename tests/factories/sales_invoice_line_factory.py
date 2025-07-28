import factory
from src.models import SalesInvoiceLine
from tests.factories import BaseFactory

class SalesInvoiceLineFactory(BaseFactory):
    class Meta:
        model = SalesInvoiceLine