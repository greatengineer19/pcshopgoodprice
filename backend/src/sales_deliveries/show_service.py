from src.models import ( SalesInvoice, SalesDelivery )
from sqlalchemy.orm import joinedload, Session
from src.schemas import ( SalesDeliveryStatusEnum )
from typing import Optional

class ShowService:
    def __init__(self, *, db: Session, sales_delivery: SalesDelivery):
        self.db = db
        self.sales_delivery = sales_delivery

    def call(self):
        self.sales_delivery.status = SalesDeliveryStatusEnum(self.sales_delivery.status).name
        sales_invoice = self.sales_delivery.sales_invoice

        self.sales_delivery.customer_id = sales_invoice.customer_id
        self.sales_delivery.customer_name = sales_invoice.customer_name
        self.sales_delivery.shipping_address = sales_invoice.shipping_address

        for delivery_line in self.sales_delivery.sales_delivery_lines:
            delivery_line.component_name = delivery_line.component.name

        return self.sales_delivery