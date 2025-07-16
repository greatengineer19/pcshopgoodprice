from src.models import ( SalesQuote )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( StatusEnum )

class Service:
    def __init__(self, db: Session):
        self.db = db

    def generate_transaction_no(self, sales_quote: SalesQuote):
        if sales_quote.sales_quote_no is not None:
            return sales_quote
        
        last_no = self.db.execute(text(
                "SELECT sales_quote_no " \
                "FROM sales_quotes " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()
        
        if last_no and last_no[0]:
            match = re.search(r"HSF-QUOT-(\d+)", last_no[0])
            if match:
                last_number = int(match.group(1))
                next_number = last_number + 1
            else:
                next_number = 1
        else:
            next_number = 1

        sales_quote.sales_quote_no = f"HSF-QUOT-{next_number:05d}"
        return sales_quote
    
    def calculate_total_columns(self, sales_quote: SalesQuote):
        sales_quote.sum_total_line_amounts = sum(quote_line.total_line_amount for quote_line in sales_quote.sales_quote_lines)
        sales_quote.total_payable_amount = sales_quote.sum_total_line_amounts
