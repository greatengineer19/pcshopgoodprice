from fastapi import APIRouter, Depends, HTTPException, Query
from typing import ( List, Optional )
from sqlalchemy import ( event, desc, text, or_ )
from src.schemas import (
    ReportResponse,
    StatusEnum
)
from src.models import (
    PurchaseInvoice,
    PurchaseInvoiceLine,
    InboundDeliveryLine,
    InboundDelivery,
    Inventory,
    ComputerComponent,
    ComputerComponentCategory
)
import logging
from sqlalchemy.orm import joinedload, Session
from decimal import Decimal, ROUND_HALF_UP
import re
from src.api.dependencies import get_db
from datetime import datetime, date

router = APIRouter(
    prefix='/api/report/inventory-movement'
)

@router.get("", response_model=ReportResponse)
def index(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: str = Query('1'),
    item_per_page: int = 25,
    component_name: Optional[str] = Query(None),
    component_category_id: Optional[str] = Query(None),
    transaction_type: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
    ):
    try:
        page = int(page)

        if component_category_id not in (None, ''):
            component_category_id = int(component_category_id)

        query = (
            db.query(Inventory.id)
              .join(Inventory.component)
              .join(ComputerComponent.component_category)
        )

        if start_date not in (None, ''):
            start_date_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Inventory.stock_date >= start_date_date)

        if end_date not in (None, ''):
            end_date_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Inventory.stock_date <= end_date_date)
        
        if transaction_type not in (None, ''):
            query = query.filter(Inventory.resource_type == transaction_type)

        if keyword not in (None, ''):
            query = query.filter((Inventory.resource_type.ilike(f"%{keyword}%")))

        if component_name not in (None, ''):
            query = query.filter(ComputerComponent.name.ilike(f"%{component_name}%"))

        if component_category_id not in (None, ''):
            query = query.filter(ComputerComponent.component_category_id == component_category_id)

        inventory_ids = [id[0] for id in query.all()]

        inventories = (
            db.query(Inventory)
                .join(Inventory.component)
                .join(ComputerComponent.component_category)
                .options(joinedload(Inventory.component)
                            .subqueryload(ComputerComponent.component_category))
                .filter(Inventory.id.in_(inventory_ids))
                .order_by(ComputerComponentCategory.name, ComputerComponent.name, Inventory.stock_date, Inventory.created_at)
                .offset((page - 1) * item_per_page)
                .limit(item_per_page)
        )

        query_total_item = db.execute(text(
                "SELECT COUNT(*) " \
                "FROM inventories i "
            )).first()
        total_item = query_total_item[0] if query_total_item else 0

        current_page = page
        has_next_page = (total_item > 0) and (total_item / (current_page * item_per_page) < 1)
        has_prev_page = (total_item > 0) and (current_page > 1)
        next_page_url = (f"http://localhost:8080/api/report/inventory-movement?page={current_page + 1}" if has_next_page else None)
        prev_page_url = (f"http://localhost:8080/api/report/inventory-movement?page={current_page - 1}" if has_prev_page else None)

        return {
            'report_headers': generate_headers(),
            'report_body': generate_report(inventories, component_name, component_category_id),
            'paging': {
                'page': current_page,
                'total_item': total_item,
                'pagination': {
                    'prev_page_url': prev_page_url,
                    'next_page_url': next_page_url
                }
            }

        }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

def generate_report(inventories, component_name, component_category_id):
    result = []
    current_component_id = None
    total_per_component = 0

    for inventory in inventories:
        if (component_name not in (None, '')) and (component_name.casefold() not in inventory.component.name.casefold()):
            continue
        elif (component_category_id not in (None, '')) and (component_category_id != inventory.component.component_category_id):
            continue
        if current_component_id != inventory.component_id:
            total_per_component = 0
            current_component_id = inventory.component_id

        in_stock = Decimal(inventory.in_stock or 0).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        out_stock = Decimal(inventory.out_stock or 0).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        total_per_component = total_per_component + in_stock - out_stock
        final_moving_stock = total_per_component

        buy_price = Decimal(inventory.buy_price or 0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        result.append([
            { 'text': inventory.component.component_category.name },
            { 'text': inventory.component.name },
            { 'text': inventory.stock_date.strftime("%Y-%m-%d") },
            { 'text': inventory.created_at.strftime("%d-%m-%Y %H:%M:%S") },
            { 'text': inventory.resource_type },
            { 'text': inventory.resource.inbound_delivery_no },
            { 'text': inventory.resource.received_by },
            { 'text': 'Sean Ali' },
            { 'text': str(in_stock) },
            { 'text': str(out_stock) },
            { 'text': str(final_moving_stock.quantize(Decimal('1'), rounding=ROUND_HALF_UP)) },
            { 'text': str(buy_price) }
        ])

    return result

def generate_headers():
    return [
        {
            'text': 'Component Category'
        },
        {
            'text': 'Component'
        },
        {
            'text': 'Stock Date'
        },
        {
            'text': 'Created At'
        },
        {
            'text': 'Transaction Type'
        },
        {
            'text': 'Trx No.'
        },
        {
            'text': 'Received By'
        },
        {
            'text': 'Created By'
        },
        {
            'text': 'In Stock'
        },
        {
            'text': 'Out Stock'
        },
        {
            'text': 'Final Moving Stock'
        },
        {
            'text': 'Buy Price'
        }
    ]
    