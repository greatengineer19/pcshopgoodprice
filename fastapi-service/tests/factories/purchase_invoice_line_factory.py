import factory
from src.models import PurchaseInvoiceLine
from tests.factories import BaseFactory

class PurchaseInvoiceLineFactory(BaseFactory):
    class Meta:
        model = PurchaseInvoiceLine