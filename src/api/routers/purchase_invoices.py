from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import ( event, desc, text, and_ )
from src.schemas import (
    PurchaseInvoiceAsParams,
    PurchaseInvoiceAsResponse,
    PurchaseInvoicesList,
    PurchaseInvoiceStatusEnum,
    BulkInsertParams,
    PurchaseInvoiceLineAsParams
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

def random_date_in_august_2025():
    start_date = datetime(2025, 8, 1)
    end_date = datetime(2025, 8, 31)

    delta = end_date - start_date
    random_days = random.randint(0, delta.days)

    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

def random_supplier_name():
    supplier_names = ["Aftershock PC Singapore",
                      "COC Computer Indonesia", "Yodobashi PC Japan",
                      "Amazon Sydney", "Amazon Canada",
                      "Amazon Germany",
                      "Amazon Denmark"]
    supplier_name = random.choice(supplier_names)
    return supplier_name

@router.post("/bulk_insert", response_model=str)
def bulk_insert(params: BulkInsertParams, db: Session = Depends(get_db)):
    try:
        count = params.count
        components = db.query(ComputerComponent).options(joinedload(ComputerComponent.component_category)).all()

        purchase_invoice_no = None
        for i in range(count):
            component = random.choice(components)
            create_params = PurchaseInvoiceAsParams(invoice_date=random_date_in_august_2025(),
                expected_delivery_date=None,
                notes=None,
                supplier_name=random_supplier_name(),
                status=0,
                purchase_invoice_lines_attributes= [
                    PurchaseInvoiceLineAsParams(
                        quantity=5,
                        price_per_unit=9900000,
                        component_id=component.id,
                        component_name=component.name,
                        component_category_id=component.component_category.id,
                        component_category_name=component.component_category.name
                    )
                ])
            build_service = BuildService(db)
            purchase_invoice = build_service.build(create_params)
            if purchase_invoice_no is not None:
                purchase_invoice.purchase_invoice_no = purchase_invoice_no
            else:
                purchase_invoice_no = purchase_invoice.purchase_invoice_no
            db.add(purchase_invoice)
            match = re.search(r"BUY-(\d+)", purchase_invoice_no)
            last_number = int(match.group(1))
            next_number = last_number + 1
            purchase_invoice_no = f"BUY-{next_number:05d}"

        db.commit()
        return "OK"
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()

@router.get("", response_model=PurchaseInvoicesList)
def index(db: Session = Depends(get_db)):
    try:
        purchase_invoices = (
            db.query(PurchaseInvoice)
            .options(joinedload(PurchaseInvoice.purchase_invoice_lines))
            .order_by(desc(PurchaseInvoice.created_at))
            .all()
        )
        
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
