from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import ( event, desc, text )
import src.schemas
import src.models
import logging
from sqlalchemy.orm import joinedload, Session
from decimal import Decimal
import re
from src.api.dependencies import get_db

router = APIRouter(
    prefix='/api/purchase-invoices'
)

PurchaseInvoiceAsParams = src.schemas.PurchaseInvoiceAsParams
PurchaseInvoiceAsResponse = src.schemas.PurchaseInvoiceAsResponse
PurchaseInvoicesList = src.schemas.PurchaseInvoicesList
PurchaseInvoice = src.models.PurchaseInvoice
PurchaseInvoiceLine = src.models.PurchaseInvoiceLine
StatusEnum = src.schemas.StatusEnum

@event.listens_for(Session, "before_flush")
def check_change_object(session: Session, flush_context, instances):
    for obj in session.new.union(session.dirty):
        if isinstance(obj, PurchaseInvoice) and not obj.purchase_invoice_no:
            result = session.execute(text(
                "SELECT purchase_invoice_no " \
                "FROM purchase_invoices " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()

            if result and result[0]:
                match = re.search(r"BUY-(\d+)", result[0])
                if match:
                    last_number = int(match.group(1))
                    next_number = last_number + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            obj.purchase_invoice_no = f"BUY-{next_number:05d}"
            obj.sum_total_line_amounts = sum(invoice_line.total_line_amount for invoice_line in obj.purchase_invoice_lines)
        elif isinstance(obj, PurchaseInvoice):
            obj.sum_total_line_amounts = sum(invoice_line.total_line_amount for invoice_line in obj.purchase_invoice_lines)

@router.get("", response_model=PurchaseInvoicesList)
def index(db: Session = Depends(get_db)):
    try:
        # Query with explicit join to ensure all data is loaded
        purchase_invoices = (
            db.query(PurchaseInvoice)
            .options(joinedload(PurchaseInvoice.purchase_invoice_lines))
            .order_by(desc(PurchaseInvoice.created_at))
            .all()
        )
        
        for invoice in purchase_invoices:
            invoice.status = StatusEnum(invoice.status).name.lower()
            if invoice.expected_delivery_date:
                invoice.expected_delivery_date = invoice.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
            if invoice.invoice_date:
                invoice.invoice_date = invoice.invoice_date.strftime("%Y-%m-%d %H:%M:%S")
            if invoice.created_at:
                invoice.created_at = invoice.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if invoice.updated_at:
                invoice.updated_at = invoice.updated_at.strftime("%Y-%m-%d %H:%M:%S")

        print(f"\nFound {len(purchase_invoices)} purchase invoices")
        for invoice in purchase_invoices:
            print(f"Invoice ID: {invoice.id}, Supplier: {invoice.supplier_name}, Status: {invoice.status}")
        
        return { 'purchase_invoices': purchase_invoices }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
    
@router.get('/{id}', response_model=PurchaseInvoiceAsResponse)
def show(id: int, db: Session = Depends(get_db)):
    try:    
        purchase_invoice = (
            db.query(PurchaseInvoice)
            .options(joinedload(PurchaseInvoice.purchase_invoice_lines))
            .filter(PurchaseInvoice.id == id)
            .first()
        )

        if purchase_invoice is None:
            raise HTTPException(status_code=404, detail="Data not found")
        
        if purchase_invoice.expected_delivery_date is not None:
            purchase_invoice.expected_delivery_date = purchase_invoice.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        purchase_invoice.status = StatusEnum(purchase_invoice.status).name
        
        return purchase_invoice
    finally:
        db.close()

@router.post("", response_model=PurchaseInvoiceAsResponse)
def create(params: PurchaseInvoiceAsParams, db: Session = Depends(get_db)):
    try:
        purchase_invoice = PurchaseInvoice(
            invoice_date=params.invoice_date,
            expected_delivery_date=params.expected_delivery_date,
            notes=params.notes,
            supplier_name=params.supplier_name,
            status=StatusEnum.PENDING
        )

        invoice_lines = []
        for param_line in params.purchase_invoice_lines_attributes:
            quantity = Decimal(param_line.quantity)
            price = Decimal(param_line.price_per_unit)

            invoice_line = PurchaseInvoiceLine(
                component_id=param_line.component_id,
                component_name=param_line.component_name,
                component_category_id=param_line.component_category_id,
                component_category_name=param_line.component_category_name,
                quantity=quantity,
                price_per_unit=price,
                total_line_amount=quantity * price
            )

            invoice_lines.append(invoice_line)

        purchase_invoice.purchase_invoice_lines = invoice_lines
        db.add(purchase_invoice)
        db.commit()

        purchase_invoice = (
            db.query(PurchaseInvoice)
            .options(joinedload(PurchaseInvoice.purchase_invoice_lines))
            .filter(PurchaseInvoice.id == purchase_invoice.id)
            .first()
        )

        if purchase_invoice.expected_delivery_date is not None:
            purchase_invoice.expected_delivery_date = purchase_invoice.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        purchase_invoice.status = StatusEnum(purchase_invoice.status).name

        return purchase_invoice
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()

@router.patch("/{id}", response_model=PurchaseInvoiceAsResponse)
def update(id: int, params: PurchaseInvoiceAsParams, db: Session = Depends(get_db)):
    try:
        purchase_invoice_db = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == id).first()

        if not purchase_invoice_db:
            raise HTTPException(status_code=404, detail="Purchase invoice not found")

        # Update the purchase invoice
        for key, value in params.model_dump(exclude_unset=True).items():
            setattr(purchase_invoice_db, key, value)
        
        existing_invoice_lines = { line.id: line for line in purchase_invoice_db.purchase_invoice_lines }

        purchase_invoice_db.supplier_name = params.supplier_name
        purchase_invoice_db.expected_delivery_date = params.expected_delivery_date
        purchase_invoice_db.notes = params.notes

        for param_line in params.purchase_invoice_lines_attributes:
            if param_line.id:
                invoice_line = existing_invoice_lines.get(param_line.id)
                if not invoice_line:
                    continue
                # Use model_dump to get the actual destroy value
                line_data = param_line.model_dump()

                if line_data.get('destroy', False):
                    db.delete(invoice_line)
                else:
                    quantity = Decimal(param_line.quantity)
                    price = Decimal(param_line.price_per_unit)

                    invoice_line.component_id = param_line.component_id
                    invoice_line.component_name = param_line.component_name
                    invoice_line.component_category_id = param_line.component_category_id
                    invoice_line.component_category_name = param_line.component_category_name
                    invoice_line.quantity = quantity
                    invoice_line.price_per_unit = price
                    invoice_line.total_line_amount = quantity * price
            else:
                quantity = Decimal(param_line.quantity)
                price = Decimal(param_line.price_per_unit)

                invoice_line = PurchaseInvoiceLine(
                    component_id=param_line.component_id,
                    component_name=param_line.component_name,
                    component_category_id=param_line.component_category_id,
                    component_category_name=param_line.component_category_name,
                    quantity=quantity,
                    price_per_unit=price,
                    total_line_amount=quantity * price
                )
                purchase_invoice_db.purchase_invoice_lines.append(invoice_line)

        purchase_invoice_db.sum_total_line_amounts = sum(invoice_line.total_line_amount for invoice_line in purchase_invoice_db.purchase_invoice_lines)

        db.add(purchase_invoice_db)
        db.commit()
        db.refresh(purchase_invoice_db)
        
        # Convert status enum to string
        purchase_invoice_db.status = StatusEnum(purchase_invoice_db.status).name.lower()
        
        # Format dates
        if purchase_invoice_db.expected_delivery_date:
            purchase_invoice_db.expected_delivery_date = purchase_invoice_db.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        if purchase_invoice_db.invoice_date:
            purchase_invoice_db.invoice_date = purchase_invoice_db.invoice_date.strftime("%Y-%m-%d %H:%M:%S")
        
        return purchase_invoice_db
    except Exception as e:
        logging.error(f"An error occurred in update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}", status_code=204)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        purchase_invoice = (
            db.query(PurchaseInvoice)
            .filter(PurchaseInvoice.id == id)
            .first()
        )

        if not purchase_invoice:
            raise HTTPException(status_code=404, detail="Data not found")
        
        db.delete(purchase_invoice)
        db.commit()

        return { "message": "Data deleted successfully" }
    finally:
        db.close()
