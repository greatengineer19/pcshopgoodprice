import factory
from src.models import SalesQuoteLine
from src.tests.factories import BaseFactory

class SalesQuoteLineFactory(BaseFactory):
    class Meta:
        model = SalesQuoteLine