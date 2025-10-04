from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import ( event, desc, text, and_ )
from src.schemas import (
    PurchaseInvoiceAsParams,
    PurchaseInvoiceAsResponse,
    PurchaseInvoicesList,
    PurchaseInvoiceStatusEnum
)
from src.models import (
    PurchaseInvoice,
    ComputerComponent
)
import logging
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from src.purchase_invoices.build_service import BuildService
from src.purchase_invoices.show_service import ShowService
from src.purchase_invoices.update_service import UpdateService
import random
from datetime import datetime, timedelta
from types import SimpleNamespace
import re

router = APIRouter(prefix='/api/purchase-invoices', tags=["Purchase Invoices"])

@router.get("", response_model=PurchaseInvoicesList)
def index(db: Session = Depends(get_db)):
    try:
        purchase_invoices = (
            db.query(PurchaseInvoice)
            .options(joinedload(PurchaseInvoice.purchase_invoice_lines))
            .order_by(desc(PurchaseInvoice.created_at))
            .limit(100)
        ).all()
        
        for invoice in purchase_invoices:
            invoice.status = PurchaseInvoiceStatusEnum(invoice.status).name.lower()
            if invoice.expected_delivery_date:
                invoice.expected_delivery_date = invoice.expected_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
            if invoice.invoice_date:
                invoice.invoice_date = invoice.invoice_date.strftime("%Y-%m-%d %H:%M:%S")
            if invoice.created_at:
                invoice.created_at = invoice.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if invoice.updated_at:
                invoice.updated_at = invoice.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        
        return { 'purchase_invoices': purchase_invoices }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
    
@router.get('/{id}', response_model=PurchaseInvoiceAsResponse)
def show(id: int, db: Session = Depends(get_db)):
    try:    
        show_service = ShowService(db)
        purchase_invoice = show_service.call(id)
        
        return purchase_invoice
    finally:
        db.close()

@router.post("", response_model=PurchaseInvoiceAsResponse)
def create(params: PurchaseInvoiceAsParams, db: Session = Depends(get_db)):
    try:
        build_service = BuildService(db)

        purchase_invoice = build_service.build(params)
        db.add(purchase_invoice)
        db.commit()

        show_service = ShowService(db)
        purchase_invoice = show_service.call(purchase_invoice.id)

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
        update_service = UpdateService(db)

        purchase_invoice = update_service.call(id, params)
        db.add(purchase_invoice)
        db.commit()

        show_service = ShowService(db)
        purchase_invoice = show_service.call(purchase_invoice.id)
        
        return purchase_invoice
    except Exception as e:
        logging.error(f"An error occurred in update: {e}")
        raise
    finally:
        db.close()

@router.delete("/{id}", status_code=204)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        purchase_invoice = (
            db.query(PurchaseInvoice)
            .filter(PurchaseInvoice.id == id)
            .first()
        )

        if not purchase_invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        elif purchase_invoice.status != 0:
            raise HTTPException(status_code=422, detail="Purchase invoice is not pending")
        
        db.delete(purchase_invoice)
        db.commit()

        return { "message": "Invoice deleted successfully" }
    finally:
        db.close()
