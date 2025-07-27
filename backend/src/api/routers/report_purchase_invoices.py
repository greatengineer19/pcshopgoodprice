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
    InboundDelivery
)
import logging
from sqlalchemy.orm import joinedload, Session
from decimal import Decimal
import re
from src.api.dependencies import get_db
from datetime import datetime, date
from src.report_purchase_invoices.filter_service import FilterService
from src.report_purchase_invoices.total_item_query_service import TotalItemQueryService
from src.report.paging_service import PagingService
from src.report.header_generator_service import HeaderGeneratorService
from src.report_purchase_invoices.response_generator_service import ResponseGeneratorService

router = APIRouter(
    prefix='/api/report/purchase-invoice'
)

@router.get("", response_model=ReportResponse, status_code = 200)
def index(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: str = Query('1'),
    item_per_page: int = 25,
    component_name: Optional[str] = Query(None),
    component_category_id: Optional[str] = Query(None),
    invoice_status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
    ):
    try:
        filter_service = FilterService(db=db,
            start_date=start_date,
            end_date=end_date,
            page=page,
            item_per_page=item_per_page,
            component_name=component_name,
            component_category_id=component_category_id,
            invoice_status=invoice_status,
            keyword=keyword)
        purchase_invoices = filter_service.call()

        total_query = TotalItemQueryService(db)
        total_item = total_query.call()

        paging_service = PagingService(db)
        paging = paging_service.call(
            page=page,
            item_per_page=item_per_page,
            total_item=total_item,
            endpoint="http://localhost:8000/api/report/purchase-invoice"
        )

        return {
            'report_headers': generate_headers(),
            'report_body': generate_report(purchase_invoices, component_name, component_category_id),
            'paging': paging
        }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

def generate_report(purchase_invoices, component_name, component_category_id):
    service = ResponseGeneratorService()
    return service.call(purchase_invoices, component_name, component_category_id)

def generate_headers():
    text_headers = [
        'Purchase Invoice No', 'Invoice Date', 'Component Name',
        'Category Name', 'Quantity', 'Price Per Unit', 'Total Price',
        'Inbound Received Qty', 'Inbound Damaged Qty', 'Total Amount Received',
        'Inbound Delivery Dates', 'Inbound Delivery No(s)'
    ]

    service = HeaderGeneratorService()
    return service.call(text_headers)
    