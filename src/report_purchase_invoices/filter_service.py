from src.models import ( PurchaseInvoice, PurchaseInvoiceLine, InboundDelivery, InboundDeliveryLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from datetime import datetime

class FilterService:
    def __init__(
        self,
        *,
        db: Session,
        start_date,
        end_date,
        page,
        item_per_page,
        component_name,
        component_category_id,
        invoice_status,
        keyword):
        self.db = db
        start_date = start_date or None
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date is not None else None
        self.start_date = start_date

        end_date = end_date or None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date is not None else None
        self.end_date = end_date
        self.page = int(page)
        self.item_per_page = item_per_page
        self.component_name = component_name or None

        component_category_id = component_category_id or None
        component_category_id = int(component_category_id) if component_category_id is not None else None
        self.component_category_id = component_category_id

        invoice_status = invoice_status or None
        invoice_status = int(invoice_status) if invoice_status is not None else None
        self.invoice_status = invoice_status
        self.keyword = keyword or None

    def call(self):
        query = (
            self.db.query(PurchaseInvoice.id)
                .join(PurchaseInvoice.purchase_invoice_lines)
                .filter(PurchaseInvoice.deleted == False)
        )

        if self.start_date:
            query = query.filter(PurchaseInvoice.invoice_date >= self.start_date)
        if self.end_date:
            query = query.filter(PurchaseInvoice.invoice_date <= self.end_date)
        if self.invoice_status is not None:
            query = query.filter(PurchaseInvoice.status == self.invoice_status)
        if self.keyword:
            query = query.filter((PurchaseInvoice.purchase_invoice_no.ilike(f"%{self.keyword}%")))
        if self.component_name:
            query = query.filter(PurchaseInvoiceLine.component_name.ilike(f"%{self.component_name}%"))
        if self.component_category_id:
            query = query.filter(PurchaseInvoiceLine.component_category_id == self.component_category_id)

        invoice_ids = [id[0] for id in query.distinct().limit(100).all()]
        purchase_invoices = (
            self.db.query(PurchaseInvoice)
                .options(joinedload(PurchaseInvoice.purchase_invoice_lines)
                            .subqueryload(PurchaseInvoiceLine.inbound_delivery_lines)
                            .subqueryload(InboundDeliveryLine.inbound_delivery))
                .filter(PurchaseInvoice.id.in_(invoice_ids))
                .order_by(desc(PurchaseInvoice.created_at))
                .offset((self.page - 1) * self.item_per_page)
                .limit(self.item_per_page)
        )

        return purchase_invoices
