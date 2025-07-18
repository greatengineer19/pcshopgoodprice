from src.models import ( SalesInvoice, SalesDelivery, SalesDeliveryLine )
from sqlalchemy.orm import joinedload, Session
from src.sales_deliveries.service import Service
from datetime import datetime
from src.schemas import (SalesInvoiceStatusEnum, SalesDeliveryStatusEnum)
from typing import List

class CreateService:
    def __init__(self, db: Session):
        self.db = db

    # TODO: Possibility of later scheduler run in parallel with its previous scheduler, need to ensure later scheduler WAITS previous.
    def call(self):
        print(f"<<< on SalesDeliveryCreateService at: {datetime.now()}")

        pending_invoices = (
            self.db.query(SalesInvoice).options(joinedload(SalesInvoice.sales_invoice_lines))
                .filter(SalesInvoice.status == SalesInvoiceStatusEnum(0).value)
                .all()
        )
        self.create_deliveries(pending_invoices)

    def create_deliveries(self, pending_invoices: List[SalesInvoice]) -> None:
        new_deliveries = []
        updated_invoices = []

        service = Service(self.db)
        service.generate_latest_sales_delivery_no()

        for source in pending_invoices:
            new_delivery = SalesDelivery(
                status=SalesDeliveryStatusEnum(0).value,
                sales_invoice_id=source.id
            )
            new_delivery.sales_delivery_lines = self.build_lines(source)
            service.assign_sales_delivery_no(new_delivery)
            new_deliveries.append(new_delivery)
    
            source.status = SalesInvoiceStatusEnum(1).value
            updated_invoices.append(source)

        self.db.add_all(new_deliveries)
        self.db.add_all(updated_invoices)
        self.db.commit()

        return

    def build_lines(self, source: SalesInvoice):
        delivery_lines = []
        for invoice_line in source.sales_invoice_lines:
            delivery_line = SalesDeliveryLine(
                component_id=invoice_line.component_id,
                quantity=invoice_line.quantity
            )
            delivery_lines.append(delivery_line)

        return delivery_lines

        
