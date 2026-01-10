from src.models import ( SalesInvoice )
from sqlalchemy.orm import Session
from sqlalchemy import ( text )
import re

class Service:
    def __init__(self, db: Session):
        self.db = db

    def generate_invoice_no(self, sales_invoice: SalesInvoice):
        if sales_invoice.sales_invoice_no is not None:
            return sales_invoice
        
        last_no = self.db.execute(text(
                "SELECT sales_invoice_no " \
                "FROM sales_invoices " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()
        
        if last_no and last_no[0]:
            match = re.search(r"PS-CUAN-(\d+)", last_no[0])
            if match:
                last_number = int(match.group(1))
                next_number = last_number + 1
            else:
                next_number = 1
        else:
            next_number = 1

        sales_invoice.sales_invoice_no = f"PS-CUAN-{next_number:08d}"
        return sales_invoice
