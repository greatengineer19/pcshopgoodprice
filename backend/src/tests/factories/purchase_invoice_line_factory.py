import factory
from src.models import PurchaseInvoiceLine
from src.tests.factories import BaseFactory

class PurchaseInvoiceLineFactory(BaseFactory):
    class Meta:
        model = PurchaseInvoiceLine