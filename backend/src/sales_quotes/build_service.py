from src.models import ( SalesQuote, User )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( SalesQuoteCreateParam )
from src.sales_quotes.sales_quote_line_build_from_cart_service import SalesQuoteLineBuildFromCartService
from src.sales_quotes.service import Service

class BuildService:
    def __init__(self, db: Session, param: SalesQuoteCreateParam, user: User):
        self.db = db
        self.param = param
        self.user = user

    def build(self):
        sales_quote = SalesQuote(
            customer_id=self.param.customer_id,
            customer_name=self.param.customer_name,
            shipping_address=self.param.shipping_address,
            payment_method_id=self.param.payment_method_id,
            payment_method_name=self.param.payment_method_name,
            virtual_account_no=self.param.virtual_account_no,
            paylater_account_reference=self.param.paylater_account_reference,
            credit_card_customer_name=self.param.credit_card_customer_name,
            credit_card_customer_address=self.param.credit_card_customer_address,
            credit_card_bank_name=self.param.credit_card_bank_name
        )

        quote_lines_service = SalesQuoteLineBuildFromCartService(self.db, self.user, sales_quote)
        sales_quote, delete_cart_query = quote_lines_service.build()

        service = Service(self.db)
        service.generate_transaction_no(sales_quote)
        service.calculate_total_columns(sales_quote)
        
        return sales_quote, delete_cart_query
