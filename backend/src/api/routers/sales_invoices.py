from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import ( desc, and_, func )
from src.schemas import ( SalesInvoiceResponse, SalesInvoiceList, SalesInvoiceStatusEnum, SalesDeliveryStatusEnum, SalesInvoiceCreateParam )
from src.models import ( SalesInvoice, SalesInvoiceLine, User, SalesQuote, SalesQuoteLine, SalesDelivery )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from utils.auth import get_current_user
from src.sales_invoices.show_service import ShowService
from src.sales_invoices.build_service import BuildService
from src.computer_components.image_service import ImageService

router = APIRouter(prefix='/api/sales-invoices', tags=["Sales Invoices"])

@router.get("", response_model=SalesInvoiceList, status_code=200)
def index(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_invoices = (
            db.query(SalesInvoice)
              .options(joinedload(SalesInvoice.sales_invoice_lines).subqueryload(SalesInvoiceLine.component))
              .filter(SalesInvoice.customer_id == user.id)
              .order_by(desc(SalesInvoice.id)).all()
        )

        if sales_invoices is None:
            return { 'sales_invoices': [] }
        
        image_service = ImageService()
        for sales_invoice in sales_invoices:
            sales_invoice.status = SalesInvoiceStatusEnum(sales_invoice.status).name

            for invoice_line in sales_invoice.sales_invoice_lines:
                invoice_line.images = image_service.presigned_url_generator(invoice_line.component)

        return { 'sales_invoices': sales_invoices }
    finally:
        db.close()

@router.post("", response_model=SalesInvoiceResponse, status_code=201)
def create(
        params: SalesInvoiceCreateParam,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        sales_quote_no = params.sales_quote_no
        sales_quote_id = params.sales_quote_id

        show_service = ShowService(db=db, sales_quote_no=sales_quote_no, sales_invoice_id=None, user_id=user.id)
        existing = show_service.call()
        if existing:
            return existing

        build_service = BuildService(db, sales_quote_id, user)
        sales_invoice = build_service.build()

        delete_query = SalesQuoteLine.__table__.delete().where(and_(SalesQuoteLine.sales_quote_id == sales_quote_id))
        db.execute(delete_query)

        delete_query = SalesQuote.__table__.delete().where(and_(SalesQuote.id == sales_quote_id, SalesQuote.customer_id == user.id))
        db.execute(delete_query)
     
        db.add(sales_invoice)
        db.commit()
        show_service = ShowService(db=db, sales_quote_no=None, sales_invoice_id=sales_invoice.id, user_id=user.id)
        sales_invoice = show_service.call()

        return sales_invoice
    finally:
        db.close()

@router.get("/{id}", response_model=SalesInvoiceResponse, status_code=200)
def show(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:    
        show_service = ShowService(db=db, sales_quote_no=None,sales_invoice_id=id, user_id=user.id)
        sales_invoice = show_service.call()

        if sales_invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return sales_invoice
    finally:
        db.close()

@router.patch("/{id}/void", response_model=SalesInvoiceResponse, status_code=200)
def void(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_invoice = (
                db.query(SalesInvoice)
                .filter(and_(
                    SalesInvoice.id == id,
                    SalesInvoice.customer_id == user.id,
                    SalesInvoice.status == SalesInvoiceStatusEnum(0).value))
                .first()
            )

        if not sales_invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        count_ids = db.query(func.count(SalesDelivery.id)).filter(and_(SalesDelivery.id == sales_invoice.id, SalesDelivery.status != SalesDeliveryStatusEnum(2).value)).scalar()
        if count_ids > 0:
            raise HTTPException(status_code=422, detail="Invoice have sales delivery, unable to void")

        sales_invoice.status = SalesInvoiceStatusEnum(2).value

        db.add(sales_invoice)
        db.commit()
        
        show_service = ShowService(db=db, sales_quote_no=None, sales_invoice_id=id, user_id=user.id)
        sales_invoice = show_service.call()

        return sales_invoice
    finally:
        db.close()
