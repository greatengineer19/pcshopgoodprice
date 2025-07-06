from fastapi import APIRouter, Depends, Query, HTTPException
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
    SalesQuoteCreateParam,
    SalesQuoteResponse,
    SalesQuoteList
)
from src.models import (
    ComputerComponent,
    SalesQuote,
    SalesQuoteLine,
    ComputerComponentSellPriceSetting,
    User,
    CartLine
)
import logging
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from datetime import datetime
from utils.auth import get_current_user
import re

router = APIRouter(
    prefix='/api/sales-quotes'
)

@event.listens_for(Session, "before_flush")
def check_change_object(session: Session, flush_context, instances):
    for obj in session.new.union(session.dirty):
        if isinstance(obj, SalesQuote) and not obj.sales_quote_no:
            result = session.execute(text(
                "SELECT sales_quote_no " \
                "FROM sales_quotes " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()

            if result and result[0]:
                match = re.search(r"HSF-QUOT-(\d+)", result[0])
                if match:
                    last_number = int(match.group(1))
                    next_number = last_number + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            obj.sales_quote_no = f"HSF-QUOT-{next_number:05d}"
            if obj.sales_quote_lines:
                obj.sum_total_line_amounts = sum(quote_line.total_line_amount for quote_line in obj.sales_quote_lines)
                obj.total_payable_amount = obj.sum_total_line_amounts
        elif isinstance(obj, SalesQuote):
            if obj.sales_quote_lines:
                obj.sum_total_line_amounts = sum(quote_line.total_line_amount for quote_line in obj.sales_quote_lines)
                obj.total_payable_amount = obj.sum_total_line_amounts

@router.get("", response_model=SalesQuoteList)
def index(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_quotes = (
            db.query(SalesQuote)
              .options(joinedload(SalesQuote.sales_quote_lines)
                        .subqueryload(SalesQuoteLine.component))
              .filter(SalesQuote.customer_id == user.id)
              .order_by(desc(SalesQuote.id)).all()
        )

        if sales_quotes is None:
            return { 'sales_quotes': [] }
        
        for sales_quote in sales_quotes:
            for quote_line in sales_quote.sales_quote_lines:
                quote_line.component_name = quote_line.component.name

        return { 'sales_quotes': sales_quotes }
    finally:
        db.close()

@router.post("", response_model=SalesQuoteResponse)
def create(
        param: SalesQuoteCreateParam,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        existing = (
            db.query(SalesQuote)
            .options(joinedload(SalesQuote.sales_quote_lines))
            .filter(SalesQuote.customer_id == user.id)
            .order_by(desc(SalesQuote.id))
            .first()
        )
        if existing:
            return existing

        sales_quote = SalesQuote(
            customer_id=param.customer_id,
            customer_name=param.customer_name,
            shipping_address=param.shipping_address,
            payment_method_id=param.payment_method_id,
            payment_method_name=param.payment_method_name,
            virtual_account_no=param.virtual_account_no,
            paylater_account_reference=param.paylater_account_reference,
            credit_card_customer_name=param.credit_card_customer_name,
            credit_card_customer_address=param.credit_card_customer_address,
            credit_card_bank_name=param.credit_card_bank_name
        )

        cart_lines = (
            db
            .query(CartLine)
            .filter(and_(CartLine.customer_id == user.id))
            .order_by(CartLine.id)
            .all()
        )

        components = (
            db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
            .filter(ComputerComponent.id.in_([p.component_id for p in cart_lines]))
        )
        components_dict = { component.id: component for component in components}
        weekday = datetime.now().isoweekday() or 7  # Returns 1-7 (Mon-Sun)

        for cart_line in cart_lines:
            component = components_dict[cart_line.component_id]
            price_settings = component.computer_component_sell_price_settings

            default_price = next((sps.price_per_unit for sps in price_settings if sps.day_type == 0), 0)
            price = next(
                (sps.price_per_unit for sps in price_settings 
                if sps.day_type == weekday and sps.status == 0),
                default_price
            )

            quote_line = SalesQuoteLine(
                component_id=cart_line.component_id,
                quantity=cart_line.quantity,
                price_per_unit=price,
                total_line_amount= price * cart_line.quantity
            )
            sales_quote.sales_quote_lines.append(quote_line)

        delete_q = CartLine.__table__.delete().where(CartLine.id.in_([cart_line.id for cart_line in cart_lines]))
        db.execute(delete_q)
        
        db.add(sales_quote)
        db.commit()

        sales_quote = (
            db.query(SalesQuote)
            .options(joinedload(SalesQuote.sales_quote_lines))
            .filter(SalesQuote.id == sales_quote.id)
            .first()
        )

        return sales_quote
    finally:
        db.close()

@router.get("/{id}", response_model=SalesQuoteResponse)
def show(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_quote = (
            db.query(SalesQuote)
            .options(joinedload(SalesQuote.sales_quote_lines))
            .filter(and_(SalesQuote.customer_id == user.id, SalesQuote.id == id))
            .order_by(desc(SalesQuote.id))
            .first()
        )

        return sales_quote
    finally:
        db.close()

@router.delete("/{id}", status_code=204)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        sales_quote = (
            db.query(SalesQuote)
            .filter(SalesQuote.id == id)
            .first()
        )

        if not sales_quote:
            raise HTTPException(status_code=404, detail="Data not found")
        
        db.delete(sales_quote)
        db.commit()

        return { "message": "Data deleted successfully" }
    finally:
        db.close()