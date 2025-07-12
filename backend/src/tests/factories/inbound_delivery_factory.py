import factory
from src.models import InboundDelivery
from src.tests.factories import BaseFactory
from src.inbound_deliveries.service import Service

class InboundDeliveryFactory(BaseFactory):
    class Meta:
        model = InboundDelivery

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        db = cls._meta.sqlalchemy_session if hasattr(cls._meta, 'sqlalchemy_session') and cls._meta.sqlalchemy_session is not None else None

        if db:
            service = Service(db)
            delivery = model_class(*args, **kwargs)
            delivery = service.generate_delivery_no(delivery)

            db.add(delivery)
            db.commit()

            return delivery
        else:
            print("Warning: No database session available for generate_delivery_no in factory.")