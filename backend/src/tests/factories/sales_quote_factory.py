import factory
from src.models import SalesQuote
from src.tests.factories import BaseFactory

class SalesQuoteFactory(BaseFactory):
    class Meta:
        model = SalesQuote