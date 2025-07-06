# TODO: This class should support api to 3rd party such as Xendit to process dummy virtual account
# TODO: Create Job to create sales invoice, not here

from fastapi import APIRouter, Depends, Query, HTTPException, Response
from typing import List, Optional
from sqlalchemy import (
        select,
        func,
        delete,
        desc,
        text,
        and_,
        event,
        or_
)
from src.schemas import (
    SalesPaymentParam
)
from src.models import (
    SalesQuote,
    SalesQuoteLine,
    SalesInvoice,
    SalesInvoiceLine,
    User,
    PaymentMethod
)
import logging
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from datetime import datetime
from utils.auth import get_current_user
import re
from .constants import bbb_virtual_account
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix='/api/sales-payment/virtual-account'
)

@event.listens_for(Session, "before_flush")
def check_change_object(session: Session, flush_context, instances):
    for obj in session.new.union(session.dirty):
        if isinstance(obj, SalesInvoice) and not obj.sales_invoice_no:
            result = session.execute(text(
                "SELECT sales_invoice_no " \
                "FROM sales_invoices " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()

            if result and result[0]:
                match = re.search(r"HSF-SALES-(\d+)", result[0])
                if match:
                    last_number = int(match.group(1))
                    next_number = last_number + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            obj.sales_invoice_no = f"HSF-SALES-{next_number:05d}"

@router.post("", status_code=201)
def pay(
        param: SalesPaymentParam,
        response: Response,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        sales_quote = (
            db.query(SalesQuote)
            .options(joinedload(SalesQuote.sales_quote_lines)
                        .subqueryload(SalesQuoteLine.component))
            .filter(and_(SalesQuote.customer_id == user.id, SalesQuote.id == param.id))
            .order_by(desc(SalesQuote.id))
            .first()
        )

        payment_method = (
            db.query(PaymentMethod.id)
              .filter(PaymentMethod.name == bbb_virtual_account).first()
        )

        if sales_quote is None or sales_quote.payment_method_id != payment_method.id:
            response.status_code = 422
            return 'Quotation cant be found' if sales_quote is None else 'Doesnt support this type of payment method'

        sales_invoice = SalesInvoice(
                customer_id=sales_quote.customer_id,
                status=0,
                sales_quote_no=sales_quote.sales_quote_no,
                sum_total_line_amounts=sales_quote.sum_total_line_amounts,
                total_payable_amount=sales_quote.total_payable_amount,
                customer_name=sales_quote.customer_name,
                shipping_address=sales_quote.shipping_address,
                payment_method_id=sales_quote.payment_method_id,
                payment_method_name=sales_quote.payment_method_name,
                virtual_account_no=sales_quote.virtual_account_no,
                paylater_account_reference=sales_quote.paylater_account_reference,
                credit_card_customer_name=sales_quote.credit_card_customer_name,
                credit_card_customer_address=sales_quote.credit_card_customer_address,
                credit_card_bank_name=sales_quote.credit_card_bank_name,
            )

        invoice_lines = []
        for quote_line in sales_quote.sales_quote_lines:
            sales_invoice_line = SalesInvoiceLine(
                component_id=quote_line.component_id,
                component_name=quote_line.component.name,
                quantity=quote_line.quantity,
                price_per_unit=quote_line.price_per_unit,
                total_line_amount=quote_line.total_line_amount
            )
            invoice_lines.append(sales_invoice_line)

        sales_invoice.sales_invoice_lines = invoice_lines
        db.add(sales_invoice)
        db.commit()

        db.delete(sales_quote)
        db.commit()

        return 'sales invoice created'
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()
