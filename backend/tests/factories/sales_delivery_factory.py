import factory
from src.models import SalesDelivery
from tests.factories import BaseFactory
from src.sales_deliveries.service import Service

class SalesDeliveryFactory(BaseFactory):
    class Meta:
        model = SalesDelivery

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        db = cls._meta.sqlalchemy_session if hasattr(cls._meta, 'sqlalchemy_session') and cls._meta.sqlalchemy_session is not None else None

        if db:
            service = Service(db)
            service.generate_latest_sales_delivery_no()

            sales_delivery = model_class(*args, **kwargs)
            sales_delivery = service.assign_sales_delivery_no(sales_delivery)

            db.add(sales_delivery)
            db.commit()

            return sales_delivery
        else:
            print("Warning: No database session available for assign_sales_delivery_no in factory.")