from src.models import ( PurchaseInvoice, InboundDelivery, PurchaseInvoiceLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( StatusEnum, PurchaseInvoiceAsParams )
from src.purchase_invoices.service import ( Service )
from decimal import Decimal
from fastapi import HTTPException

class ShowService:
    def __init__(self, db: Session):
        self.db = db

    def call(self, purchase_invoice_id: int):
        db = self.db

        purchase_invoice = (
            db.query(PurchaseInvoice)
            .options(joinedload(PurchaseInvoice.purchase_invoice_lines))
            .filter(PurchaseInvoice.id == purchase_invoice_id)
            .first()
        )

        if purchase_invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if purchase_invoice.expected_delivery_date is not None:
            purchase_invoice.expected_delivery_date = purchase_invoice.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        if purchase_invoice.invoice_date:
            purchase_invoice.invoice_date = purchase_invoice.invoice_date.strftime("%Y-%m-%d %H:%M:%S")
        purchase_invoice.status = StatusEnum(purchase_invoice.status).name

        return purchase_invoice

    
