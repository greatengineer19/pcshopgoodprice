from fastapi import APIRouter, Depends, HTTPException, Query
from typing import ( Optional )
from sqlalchemy import (desc)
from src.schemas import (
    SalesDeliveryList,
    SalesDeliveryStatusEnum,
    SalesDeliveryResponse
)
from src.models import (
    SalesDelivery,
    SalesInvoice,
    SalesDeliveryLine,
    User
)
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from utils.auth import get_current_user
from src.sales_deliveries.query_show_service import QueryShowService
from src.sales_deliveries.show_service import ShowService
from src.sales_deliveries.create_inventory_service import CreateInventoryService
from src.sales_deliveries.void_service import VoidService
from datetime import datetime

router = APIRouter(prefix='/api/sales-deliveries', tags=["Sales Deliveries"])

@router.get("", response_model=SalesDeliveryList, status_code=200)
def index(user: User = Depends(get_current_user), db: Session = Depends(get_db), start_date: Optional[str] = Query(None)):
    try:
        query = (
            db.query(SalesDelivery)
              .join(SalesDelivery.sales_invoice)
              .options(joinedload(SalesDelivery.sales_invoice))
              .options(joinedload(SalesDelivery.sales_delivery_lines).subqueryload(SalesDeliveryLine.component))
              .filter(SalesInvoice.customer_id == user.id)
        )

        if start_date is not None:
            # Convert string date to datetime object for proper comparison
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(SalesDelivery.created_at >= start_datetime)

        sales_deliveries = query.order_by(desc(SalesDelivery.id)).all()
        if sales_deliveries is None:
            return { 'sales_deliveries': [] }
        
        for sales_delivery in sales_deliveries:
            show_service = ShowService(db=db, sales_delivery=sales_delivery)
            sales_delivery = show_service.call()

        return { 'sales_deliveries': sales_deliveries }
    finally:
        db.close()

@router.get("/{id}", response_model=SalesDeliveryResponse)
def show(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        show_service = QueryShowService(db=db, sales_delivery_id=id, user_id=user.id)
        sales_delivery = show_service.call()

        if sales_delivery is None:
            raise HTTPException(status_code=404, detail="Sales Delivery not found")

        return sales_delivery
    finally:
        db.close()

@router.patch("/{id}/fully_delivered", response_model=SalesDeliveryResponse)
def fully_delivered(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        show_service = QueryShowService(db=db, sales_delivery_id=id, user_id=user.id)
        sales_delivery = show_service.call()

        if sales_delivery is None:
            raise HTTPException(status_code=404, detail="Sales Delivery not found")
        
        sales_delivery.status = SalesDeliveryStatusEnum(1).value
        inventory_service = CreateInventoryService(db=db, sales_delivery=sales_delivery)
        inventories = inventory_service.call()

        db.add(sales_delivery)
        db.add_all(inventories)
        db.commit()

        show_service = QueryShowService(db=db, sales_delivery_id=id, user_id=user.id)
        sales_delivery = show_service.call()

        return sales_delivery
    finally:
        db.close()

@router.patch("/{id}/void", response_model=SalesDeliveryResponse)
def void(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        show_service = QueryShowService(db=db, sales_delivery_id=id, user_id=user.id)
        sales_delivery = show_service.call()

        if sales_delivery is None:
            raise HTTPException(status_code=404, detail="Sales Delivery not found")
        
        void_service = VoidService(db=db, sales_delivery=sales_delivery)
        sales_delivery, sales_invoice, statement_delete_inventory = void_service.call()
        
        db.execute(statement_delete_inventory)
        db.add(sales_delivery)
        db.add(sales_invoice)
        db.commit()

        show_service = QueryShowService(db=db, sales_delivery_id=id, user_id=user.id)
        sales_delivery = show_service.call()

        return sales_delivery
    finally:
        db.close()