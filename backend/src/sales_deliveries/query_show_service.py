from src.models import ( SalesInvoice, SalesDelivery, SalesDeliveryLine )
from sqlalchemy.orm import joinedload, Session
from src.sales_deliveries.show_service import ShowService

class QueryShowService:
    def __init__(self, *, db: Session, sales_delivery_id: int, user_id: int):
        self.db = db
        self.sales_delivery_id = sales_delivery_id or None
        self.user_id = user_id or None

    def call(self):
        query = (
            self.db
            .query(SalesDelivery)
            .join(SalesDelivery.sales_invoice)
            .options(joinedload(SalesDelivery.sales_invoice))
              .options(joinedload(SalesDelivery.sales_delivery_lines).subqueryload(SalesDeliveryLine.component))
        )

        if self.sales_delivery_id:
            query = query.filter(SalesDelivery.id == self.sales_delivery_id)
        if self.user_id:
            query = query.filter(SalesInvoice.customer_id == self.user_id)
        query = query.first()

        show_service = ShowService(db=self.db, sales_delivery=query)
        sales_delivery = show_service.call()

        return sales_delivery