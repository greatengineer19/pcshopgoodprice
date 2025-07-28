import factory
from src.models import SalesInvoice
from tests.factories import BaseFactory
from src.sales_invoices.service import Service

class SalesInvoiceFactory(BaseFactory):
    class Meta:
        model = SalesInvoice

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        db = cls._meta.sqlalchemy_session if hasattr(cls._meta, 'sqlalchemy_session') and cls._meta.sqlalchemy_session is not None else None

        if db:
            service = Service(db)
            sales_invoice = model_class(*args, **kwargs)
            sales_invoice = service.generate_invoice_no(sales_invoice)

            db.add(sales_invoice)
            db.commit()

            return sales_invoice
        else:
            print("Warning: No database session available for generate_invoice_no in factory.")