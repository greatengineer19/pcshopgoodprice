import factory
from src.models import PurchaseInvoice
from src.tests.factories import BaseFactory

class PurchaseInvoiceFactory(BaseFactory):
    class Meta:
        model = PurchaseInvoice