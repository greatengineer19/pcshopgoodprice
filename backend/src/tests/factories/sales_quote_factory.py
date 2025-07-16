import factory
from src.models import SalesQuote
from src.tests.factories import BaseFactory
from src.sales_quotes.service import Service

class SalesQuoteFactory(BaseFactory):
    class Meta:
        model = SalesQuote

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        db = cls._meta.sqlalchemy_session if hasattr(cls._meta, 'sqlalchemy_session') and cls._meta.sqlalchemy_session is not None else None

        if db:
            service = Service(db)
            sales_quote = model_class(*args, **kwargs)
            sales_quote = service.generate_transaction_no(sales_quote)
            service.calculate_total_columns(sales_quote)

            db.add(sales_quote)
            db.commit()

            return sales_quote
        else:
            print("Warning: No database session available for generate_transaction_no in factory.")