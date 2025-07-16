from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import (
        desc,
)
from src.schemas import (
    SalesQuoteCreateParam,
    SalesQuoteResponse,
    SalesQuoteList
)
from src.models import (
    SalesQuote,
    SalesQuoteLine,
    User
)
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from utils.auth import get_current_user
from src.sales_quotes.show_service import ShowService
from src.sales_quotes.build_service import BuildService

router = APIRouter(prefix='/api/sales-quotes', tags=["Sales Quotes"])

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
        show_service = ShowService(db, None, user.id)
        existing = show_service.call()
        if existing:
            return existing

        build_service = BuildService(db, param, user)
        sales_quote, delete_cart_query = build_service.build()
    
        db.execute(delete_cart_query)    
        db.add(sales_quote)
        db.commit()

        show_service = ShowService(db, sales_quote.id, None)
        sales_quote = show_service.call()

        return sales_quote
    finally:
        db.close()

@router.get("/{id}", response_model=SalesQuoteResponse)
def show(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        show_service = ShowService(db, id, user.id)
        sales_quote = show_service.call()

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
