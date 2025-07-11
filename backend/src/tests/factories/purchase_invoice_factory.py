import factory
from src.models import PurchaseInvoice
from src.tests.factories import BaseFactory
from src.purchase_invoices.service import Service

class PurchaseInvoiceFactory(BaseFactory):
    class Meta:
        model = PurchaseInvoice

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        db = cls._meta.sqlalchemy_session if hasattr(cls._meta, 'sqlalchemy_session') and cls._meta.sqlalchemy_session is not None else None

        if db:
            service = Service(db)
            invoice = model_class(*args, **kwargs)
            invoice = service.generate_invoice_no(invoice)
            service.calculate_sum_total_line_amounts(invoice)

            db.add(invoice)
            db.commit()

            return invoice
        else:
            print("Warning: No database session available for generate_invoice_no in factory.")