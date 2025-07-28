from src.models import ( PurchaseInvoice, InboundDelivery )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( StatusEnum )

class Service:
    def __init__(self, db: Session):
        self.db = db

    def generate_invoice_no(self, invoice: PurchaseInvoice):
        if invoice.purchase_invoice_no is not None:
            return invoice
        
        last_no = self.db.execute(text(
                "SELECT purchase_invoice_no " \
                "FROM purchase_invoices " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()
        
        if last_no and last_no[0]:
            match = re.search(r"BUY-(\d+)", last_no[0])
            if match:
                last_number = int(match.group(1))
                next_number = last_number + 1
            else:
                next_number = 1
        else:
            next_number = 1

        invoice.purchase_invoice_no = f"BUY-{next_number:05d}"
        return invoice
    
    def calculate_sum_total_line_amounts(self, invoice: PurchaseInvoice):
        invoice.sum_total_line_amounts = sum(invoice_line.total_line_amount for invoice_line in invoice.purchase_invoice_lines)

    def assign_status_after_create_inbound_delivery(self, purchase_invoice: PurchaseInvoice):
        db = self.db

        total_unsent_quantity = 0
        for invoice_line in purchase_invoice.purchase_invoice_lines:
            delivery_lines = invoice_line.inbound_delivery_lines
            total_unsent_quantity += ( invoice_line.quantity -
                                      sum(ib_line.received_quantity + ib_line.damaged_quantity for ib_line in delivery_lines)
                                    )

        if total_unsent_quantity == 0:
            purchase_invoice.status = StatusEnum.COMPLETED
            db.add(purchase_invoice)
            db.commit()

