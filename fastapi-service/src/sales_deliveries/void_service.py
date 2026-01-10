from src.models import ( SalesDelivery, Inventory, SalesInvoice )
from sqlalchemy.orm import Session
from src.schemas import ( SalesDeliveryStatusEnum, SalesInvoiceStatusEnum )
from src.computer_components.image_service import ImageService
from sqlalchemy import (and_, delete)

class VoidService:
    def __init__(self, *, db: Session, sales_delivery: SalesDelivery):
        self.db = db
        self.sales_delivery = sales_delivery

    def call(self):
        self.sales_delivery.status = SalesDeliveryStatusEnum(2).value
        statement_delete_inventory = delete(Inventory).where(and_(Inventory.resource_id == self.sales_delivery.id, Inventory.resource_type == "SalesDelivery"))
        sales_invoice = self.db.query(SalesInvoice).filter(SalesInvoice.id == self.sales_delivery.sales_invoice_id).first()
        sales_invoice.status = SalesInvoiceStatusEnum(0).value

        return self.sales_delivery, sales_invoice, statement_delete_inventory