from src.models import ( SalesQuote, User, SalesInvoice, SalesQuoteLine, SalesInvoiceLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( SalesQuoteCreateParam )
from src.sales_quotes.sales_quote_line_build_from_cart_service import SalesQuoteLineBuildFromCartService
from src.sales_invoices.service import Service
from fastapi import HTTPException

class BuildService:
    def __init__(self, db: Session, sales_quote_id: int, user: User):
        self.db = db
        self.sales_quote_id = sales_quote_id
        self.user = user

    def build(self):
        source = (
            self.db.query(SalesQuote)
                .options(joinedload(SalesQuote.sales_quote_lines)
                         .subqueryload(SalesQuoteLine.component))
                .filter(SalesQuote.id == self.sales_quote_id).first()
        )
        if not source:
            raise HTTPException(status_code=404, detail="Quotation not found")
        
        sales_invoice = SalesInvoice(
            customer_id=source.customer_id,
            customer_name=source.customer_name,
            sales_invoice_no=None,
            sales_quote_no=source.sales_quote_no,
            sum_total_line_amounts=source.sum_total_line_amounts,
            total_payable_amount=source.total_payable_amount,
            shipping_address=source.shipping_address,
            payment_method_id=source.payment_method_id,
            payment_method_name=source.payment_method_name,
            virtual_account_no=source.virtual_account_no,
            paylater_account_reference=source.paylater_account_reference,
            credit_card_customer_name=source.credit_card_customer_name,
            credit_card_customer_address=source.credit_card_customer_address,
            credit_card_bank_name=source.credit_card_bank_name,
        )

        sales_invoice.sales_invoice_lines = self.build_lines(source)

        service = Service(self.db)
        service.generate_invoice_no(sales_invoice)

        return sales_invoice

    def build_lines(self, source: SalesQuote):
        invoice_lines = []
        for source_line in source.sales_quote_lines:
            invoice_line = SalesInvoiceLine(
                component_id=source_line.component_id,
                component_name=source_line.component.name,
                quantity=source_line.quantity,
                price_per_unit=source_line.price_per_unit,
                total_line_amount=source_line.total_line_amount
            )
            invoice_lines.append(invoice_line)

        return invoice_lines

        
