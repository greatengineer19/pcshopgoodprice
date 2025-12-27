from src.models import ( SalesQuote )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( PurchaseInvoiceStatusEnum )
import uuid

class Service:
    def __init__(self, db: Session):
        self.db = db

    def generate_transaction_no(self, sales_quote: SalesQuote):
        if sales_quote.sales_quote_no is not None:
            return sales_quote
        
        uuid4_value = str(uuid.uuid4())
        sales_quote.sales_quote_no = uuid4_value[:8]
        return sales_quote
    
    def calculate_total_columns(self, sales_quote: SalesQuote):
        sales_quote.sum_total_line_amounts = sum(quote_line.total_line_amount for quote_line in sales_quote.sales_quote_lines)
        sales_quote.total_payable_amount = sales_quote.sum_total_line_amounts
