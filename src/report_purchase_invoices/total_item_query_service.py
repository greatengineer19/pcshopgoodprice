from src.models import ( PurchaseInvoice, PurchaseInvoiceLine, InboundDelivery, InboundDeliveryLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( PurchaseInvoiceStatusEnum )
from datetime import datetime

class TotalItemQueryService:
    def __init__(self, db: Session):
        self.db = db

    def call(self) -> int:
        query_total_item = self.db.execute(text(
                "SELECT COUNT(*) " \
                "FROM purchase_invoices pi " \
                "LEFT JOIN purchase_invoice_lines pil ON pil.purchase_invoice_id = pi.id " \
                "LEFT JOIN inbound_delivery_lines idl ON idl.purchase_invoice_line_id = pil.id " \
                "LEFT JOIN inbound_deliveries id ON id.id = idl.inbound_delivery_id " \
                "WHERE pi.deleted = FALSE AND id.deleted = FALSE"
            )).first()
        total_item = query_total_item[0] if query_total_item else 0
        return total_item