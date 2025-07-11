from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import ( event, desc, text )
from src.schemas import (
    PurchaseInvoiceAsParams,
    PurchaseInvoiceAsResponse,
    PurchaseInvoicesList,
    StatusEnum
)
from src.models import (
    PurchaseInvoice,
    PurchaseInvoiceLine
)
import src.models
import logging
from sqlalchemy.orm import joinedload, Session
from decimal import Decimal
import re
from src.api.dependencies import get_db
from src.purchase_invoices.service import Service

router = APIRouter(prefix='/api/purchase-invoices', tags=["Purchase Invoices"])

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
        service = Service(db)
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
        purchase_invoice = service.generate_invoice_no(purchase_invoice)
        service.calculate_sum_total_line_amounts(purchase_invoice)
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
        service = Service(db)
        purchase_invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == id).first()

        if not purchase_invoice:
            raise HTTPException(status_code=404, detail="Purchase invoice not found")

        # Update the purchase invoice
        for key, value in params.model_dump(exclude_unset=True).items():
            setattr(purchase_invoice, key, value)
        
        existing_invoice_lines = { line.id: line for line in purchase_invoice.purchase_invoice_lines }

        purchase_invoice.supplier_name = params.supplier_name
        purchase_invoice.expected_delivery_date = params.expected_delivery_date
        purchase_invoice.notes = params.notes

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
                purchase_invoice.purchase_invoice_lines.append(invoice_line)

        service.calculate_sum_total_line_amounts(purchase_invoice)

        db.add(purchase_invoice)
        db.commit()
        db.refresh(purchase_invoice)
        
        # Convert status enum to string
        purchase_invoice.status = StatusEnum(purchase_invoice.status).name.lower()
        
        # Format dates
        if purchase_invoice.expected_delivery_date:
            purchase_invoice.expected_delivery_date = purchase_invoice.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        if purchase_invoice.invoice_date:
            purchase_invoice.invoice_date = purchase_invoice.invoice_date.strftime("%Y-%m-%d %H:%M:%S")
        
        return purchase_invoice
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
