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
    SalesDeliveryCreateParam,
    SalesDeliveryStatusEnum,
    SalesDeliveryResponse
)
from src.models import (
    SalesDelivery,
    SalesDeliveryLine,
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
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix='/api/sales-deliveries'
)

@event.listens_for(Session, "before_flush")
def check_change_object(session: Session, flush_context, instances):
    for obj in session.new.union(session.dirty):
        if isinstance(obj, SalesDelivery) and not obj.sales_delivery_no:
            result = session.execute(text(
                "SELECT sales_delivery_no " \
                "FROM sales_deliveries " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()

            if result and result[0]:
                match = re.search(r"HSF-OBD-(\d+)", result[0])
                if match:
                    last_number = int(match.group(1))
                    next_number = last_number + 1
                else:
                    next_number = 1
            else:
                next_number = 1
            
            obj.sales_delivery_no = f"HSF-OBD-{next_number:05d}"

@router.post("", status_code=201)
def create(
        param: SalesDeliveryCreateParam,
        response: Response,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        exist = (
            db.query(SalesDelivery)
            .filter(and_(SalesDelivery.status != 2, SalesDelivery.sales_invoice_id == param.id))
            .first()
        )

        if exist:
            return 'sales delivery is exist'

        sales_invoice = (
            db.query(SalesInvoice)
            .options(joinedload(SalesInvoice.sales_invoice_lines))
            .filter(SalesInvoice.id == param.id)
            .first()
        )

        sales_delivery = SalesDelivery(
                status=0,
                sales_invoice_id=param.id
            )

        delivery_lines = []
        for invoice_line in sales_invoice.sales_invoice_lines:
            delivery_line = SalesDeliveryLine(
                component_id=invoice_line.component_id,
                quantity=invoice_line.quantity
            )
            delivery_lines.append(delivery_line)

        sales_delivery.sales_delivery_lines = delivery_lines
        db.add(sales_delivery)
        db.commit()

        return 'sales delivery created'
    except Exception as e:
        db.rollback()
        logging.error(f"An error occured: {e}")
        raise
    finally:
        db.close()

@router.get("/{id}", response_model=SalesDeliveryResponse)
def show(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_delivery = (
            db.query(SalesDelivery)
            .options(joinedload(SalesDelivery.sales_delivery_lines))
            .filter(SalesDelivery.id == id)
            .first()
        )

        if sales_delivery is None:
            raise HTTPException(status_code=404, detail="Data not found")

        return sales_delivery
    finally:
        db.close()

@router.patch("/{id}/fully_delivered", response_model=SalesDeliveryResponse)
def fully_delivered(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_delivery = db.query(SalesDelivery).filter(SalesDelivery.id == id).first()

        if sales_delivery is None:
            raise HTTPException(status_code=404, detail="Data not found")
        
        sales_delivery.status = 1
        db.add(sales_delivery)
        db.commit()

        sales_delivery = (
            db.query(SalesDelivery)
            .options(joinedload(SalesDelivery.sales_delivery_lines))
            .filter(SalesDelivery.id == id)
            .first()
        )

        return sales_delivery
    finally:
        db.close()

@router.patch("/{id}/void", response_model=SalesDeliveryResponse)
def void(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        sales_delivery = db.query(SalesDelivery).filter(SalesDelivery.id == id).first()

        if sales_delivery is None:
            raise HTTPException(status_code=404, detail="Data not found")
        
        sales_delivery.status = 2
        db.add(sales_delivery)
        db.commit()

        sales_delivery = (
            db.query(SalesDelivery)
            .options(joinedload(SalesDelivery.sales_delivery_lines))
            .filter(SalesDelivery.id == id)
            .first()
        )

        return sales_delivery
    finally:
        db.close()