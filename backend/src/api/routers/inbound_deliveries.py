from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import ( event, desc, text, delete )
from src.schemas import (
    InboundDeliveryAsParams,
    InboundDeliveryAsResponse,
    InboundDeliveriesList,
    InboundDeliveryStatusEnum,
    StatusEnum,
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

router = APIRouter(
    prefix='/api/inbound-deliveries'
)

@event.listens_for(Session, "before_flush")
def check_change_object(session: Session, flush_context, instances):
    for obj in session.new.union(session.dirty):
        if isinstance(obj, InboundDelivery) and not obj.inbound_delivery_no:
            result = session.execute(text(
                "SELECT inbound_delivery_no " \
                "FROM inbound_deliveries " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()

            if result and result[0]:
                match = re.search(r"IBD-(\d+)", result[0])
                if match:
                    last_number = int(match.group(1))
                    next_number = last_number + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            obj.inbound_delivery_no = f"IBD-{next_number:05d}"

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
            .filter(PurchaseInvoice.status == StatusEnum.PENDING)
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
        inbound_delivery = (
            db.query(InboundDelivery)
            .options(
                joinedload(InboundDelivery.inbound_delivery_lines),
                joinedload(InboundDelivery.inbound_delivery_attachments)
            )
            .filter(InboundDelivery.id == id)
            .first()
        )

        if inbound_delivery is None:
            raise HTTPException(status_code=404, detail="Data not found")
        
        if inbound_delivery.inbound_delivery_date is not None:
            inbound_delivery.inbound_delivery_date = inbound_delivery.inbound_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        inbound_delivery.status = InboundDeliveryStatusEnum(inbound_delivery.status).name

        for attachment in inbound_delivery.inbound_delivery_attachments:
            attachment.file_link = s3_client().generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name(), 'Key': attachment.file_s3_key},
                    ExpiresIn=3600
                )
        
        return inbound_delivery
    finally:
        db.close()

@router.post("", response_model=InboundDeliveryAsResponse)
def create(params: InboundDeliveryAsParams, db: Session = Depends(get_db)):
    try:
        inbound_delivery = InboundDelivery(
            purchase_invoice_id=params.purchase_invoice_id,
            purchase_invoice_no=params.purchase_invoice_no,
            inbound_delivery_date=params.inbound_delivery_date,
            inbound_delivery_reference=params.inbound_delivery_reference,
            received_by=params.received_by,
            notes=params.notes,
            status=InboundDeliveryStatusEnum.DELIVERED
        )

        delivery_lines = []
        for param_line in params.inbound_delivery_lines_attributes:
            expected_quantity = Decimal(param_line.expected_quantity)
            received_quantity = Decimal(param_line.received_quantity)
            damaged_quantity = Decimal(param_line.damaged_quantity)
            price = Decimal(param_line.price_per_unit)
            total_line_amount = price * received_quantity

            delivery_line = InboundDeliveryLine(
                purchase_invoice_line_id=param_line.purchase_invoice_line_id,
                component_id=param_line.component_id,
                component_name=param_line.component_name,
                component_category_id=param_line.component_category_id,
                component_category_name=param_line.component_category_name,
                expected_quantity=expected_quantity,
                received_quantity=received_quantity,
                damaged_quantity=damaged_quantity,
                price_per_unit=price,
                total_line_amount=total_line_amount
            )
            delivery_lines.append(delivery_line)

        attachment_lines = []
        for param_attachment in params.inbound_delivery_attachments_attributes:
            attachment_line = InboundDeliveryAttachment(
                uploaded_by=param_attachment.uploaded_by,
                file_s3_key=param_attachment.file_s3_key
            )
            attachment_lines.append(attachment_line)

        inbound_delivery.inbound_delivery_lines = delivery_lines
        inbound_delivery.inbound_delivery_attachments = attachment_lines

        db.add(inbound_delivery)
        db.commit()
        db.refresh(inbound_delivery)

        purchase_invoice = (
            db.query(PurchaseInvoice)
              .options(
                    joinedload(PurchaseInvoice.purchase_invoice_lines)
                    .subqueryload(PurchaseInvoiceLine.inbound_delivery_lines)
                )
              .filter(PurchaseInvoice.id == params.purchase_invoice_id).first()
        )

        total_unsent_quantity = 0
        for invoice_line in purchase_invoice.purchase_invoice_lines:
            delivery_lines = invoice_line.inbound_delivery_lines
            total_unsent_quantity += invoice_line.quantity - sum(ib_line.received_quantity + ib_line.damaged_quantity for ib_line in delivery_lines)

        if total_unsent_quantity == 0:
            purchase_invoice.status = StatusEnum.COMPLETED
            db.add(purchase_invoice)
            db.commit()
            db.refresh(purchase_invoice)


        for delivery_line in inbound_delivery.inbound_delivery_lines:
            inventory = Inventory(
                in_stock= delivery_line.received_quantity,
                stock_date=inbound_delivery.inbound_delivery_date,
                component_id=delivery_line.component_id,
                resource_id=inbound_delivery.id,
                resource_type='InboundDelivery',
                resource_line_id=delivery_line.id,
                resource_line_type='InboundDeliveryLine',
                buy_price=delivery_line.price_per_unit
            )
            db.add(inventory)

        db.commit()

        inbound_delivery = (
            db.query(InboundDelivery)
            .options(
                joinedload(InboundDelivery.inbound_delivery_lines),
                joinedload(InboundDelivery.inbound_delivery_attachments)
            )
            .filter(InboundDelivery.id == inbound_delivery.id)
            .first()
        )

        for attachment in inbound_delivery.inbound_delivery_attachments:
            attachment.file_link = create_presigned_url(attachment.file_s3_key)

        if inbound_delivery.inbound_delivery_date is not None:
            inbound_delivery.inbound_delivery_date = inbound_delivery.inbound_delivery_date.strftime("%Y-%m-%d %H:%M:%S")
        inbound_delivery.status = InboundDeliveryStatusEnum(inbound_delivery.status).name

        return inbound_delivery
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()

def create_presigned_url(file_s3_key: str):
    return s3_client().generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name(), 'Key': file_s3_key },
        ExpiresIn=3600
    )

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
        stmt = delete(Inventory).where(Inventory.resource_id == id)
        db.execute(stmt)
        db.commit()

        purchase_invoice = (
            db.query(PurchaseInvoice)
              .filter(PurchaseInvoice.id == purchase_invoice_id).first()
        )

        purchase_invoice.status = StatusEnum.PENDING
        db.add(purchase_invoice)
        db.commit()
        db.refresh(purchase_invoice)

        return { "message": "Data deleted successfully" }
    finally:
        db.close()
