from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import ( and_, event, desc, text, delete )
from src.schemas import (
    InboundDeliveryAsParams,
    InboundDeliveryAsResponse,
    InboundDeliveriesList,
    InboundDeliveryStatusEnum,
    PurchaseInvoiceStatusEnum,
    DeliverablePurchaseInvoiceLine,
    DeliverablePurchaseInvoice,
    DeliverablePurchaseInvoicesList
)
from src.models import (
    InboundDelivery,
    InboundDeliveryAttachment,
    InboundDeliveryLine,
    Inventory,
    PurchaseInvoice,
    PurchaseInvoiceLine
)
import logging
from sqlalchemy.orm import joinedload, Session, subqueryload
from decimal import Decimal
import re
from src.api.dependencies import get_db
from src.api.s3_dependencies import ( bucket_name, s3_client )
from src.inbound_deliveries.build_service import ( BuildService )
from src.inbound_deliveries.show_service import ( ShowService )
from src.purchase_invoices.service import Service as PurchaseInvoiceService
from src.inventories.create_from_inbound_delivery_service import CreateFromInboundDeliveryService
from datetime import datetime
from dateutil.parser import parse as datetime_parse

router = APIRouter(
    prefix='/api/inbound-deliveries'
)

@router.get("", response_model=InboundDeliveriesList)
def index(db: Session = Depends(get_db)):
    try:
        inbound_deliveries = (
            db.query(InboundDelivery)
            .order_by(desc(InboundDelivery.id))
            .all()
        )
        
        for inbound_delivery in inbound_deliveries:
            inbound_delivery.status = InboundDeliveryStatusEnum(inbound_delivery.status).name.lower()
            if inbound_delivery.inbound_delivery_date:
                inbound_delivery.inbound_delivery_date = inbound_delivery.inbound_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
            if inbound_delivery.created_at:
                inbound_delivery.created_at = inbound_delivery.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if inbound_delivery.updated_at:
                inbound_delivery.updated_at = inbound_delivery.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        
        return { 'inbound_deliveries': inbound_deliveries }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/deliverable-purchase-invoices", response_model=DeliverablePurchaseInvoicesList)
def deliverable_purchase_invoices(db: Session = Depends(get_db)):
    try:
        purchase_invoices = (
            db.query(PurchaseInvoice)
            .options(
                joinedload(PurchaseInvoice.purchase_invoice_lines)
                    .subqueryload(PurchaseInvoiceLine.inbound_delivery_lines)
            )
            .filter(PurchaseInvoice.status == PurchaseInvoiceStatusEnum.PENDING)
            .order_by(desc(PurchaseInvoice.purchase_invoice_no))
        )

        final_result = []
        for invoice in purchase_invoices:
            dr_invoice = DeliverablePurchaseInvoice(
                id=invoice.id,
                purchase_invoice_no=invoice.purchase_invoice_no,
                invoice_date=invoice.invoice_date,
                supplier_name=invoice.supplier_name,
                deliverable_invoice_lines=[]
            )
            dr_invoice_lines = []

            for invoice_line in invoice.purchase_invoice_lines:
                dr_invoice_line = DeliverablePurchaseInvoiceLine(
                    id=invoice_line.id,
                    component_id=invoice_line.component_id,
                    component_name=invoice_line.component_name,
                    component_category_id=invoice_line.component_category_id,
                    component_category_name=invoice_line.component_category_name,
                    deliverable_quantity=invoice_line.quantity - sum(ib_line.received_quantity + ib_line.damaged_quantity for ib_line in invoice_line.inbound_delivery_lines),
                    price_per_unit=invoice_line.price_per_unit
                )
                dr_invoice_lines.append(dr_invoice_line)

            dr_invoice.deliverable_invoice_lines = dr_invoice_lines
            final_result.append(dr_invoice)

        return { 'purchase_invoices': final_result }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get('/{id}', response_model=InboundDeliveryAsResponse)
def show(id: int, db: Session = Depends(get_db)):
    try:
        show_service = ShowService(db)
        inbound_delivery = show_service.build_response(id)
        
        return inbound_delivery
    finally:
        db.close()

@router.post("", response_model=InboundDeliveryAsResponse)
def create(params: InboundDeliveryAsParams, db: Session = Depends(get_db)):
    try:
        purchase_invoice = (
            db.query(PurchaseInvoice)
              .options(
                    joinedload(PurchaseInvoice.purchase_invoice_lines)
                    .subqueryload(PurchaseInvoiceLine.inbound_delivery_lines)
                )
              .filter(PurchaseInvoice.id == params.purchase_invoice_id).first()
        )

        if purchase_invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        elif purchase_invoice.invoice_date > datetime_parse(params.inbound_delivery_date):
            raise HTTPException(status_code=422, detail="Invoice date cannot be greater than delivery date")
        
        build_service = BuildService(db)
        inbound_delivery = build_service.build(params, purchase_invoice)

        db.add(inbound_delivery)
        db.commit()
        db.refresh(inbound_delivery)

        invoice_service = PurchaseInvoiceService(db)
        invoice_service.assign_status_after_create_inbound_delivery(purchase_invoice)

        inventory_service = CreateFromInboundDeliveryService(db)
        inventory_service.create_inventories(inbound_delivery)

        show_service = ShowService(db)
        inbound_delivery = show_service.build_response(inbound_delivery.id)

        return inbound_delivery
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()

@router.delete("/{id}", status_code=204)
def destroy(id: int, db: Session = Depends(get_db)):
    try:
        inbound_delivery = (
            db.query(InboundDelivery)
            .filter(InboundDelivery.id == id)
            .first()
        )
        purchase_invoice_id = inbound_delivery.purchase_invoice_id

        if not inbound_delivery:
            raise HTTPException(status_code=404, detail="Data not found")
        
        db.delete(inbound_delivery)
        stmt = delete(Inventory).where(and_(Inventory.resource_id == id, Inventory.resource_type == "InboundDelivery"))
        db.execute(stmt)
        db.commit()

        purchase_invoice = (
            db.query(PurchaseInvoice)
              .filter(PurchaseInvoice.id == purchase_invoice_id).first()
        )

        purchase_invoice.status = PurchaseInvoiceStatusEnum.PENDING
        db.add(purchase_invoice)
        db.commit()
        db.refresh(purchase_invoice)

        return { "message": "Data deleted successfully" }
    finally:
        db.close()
