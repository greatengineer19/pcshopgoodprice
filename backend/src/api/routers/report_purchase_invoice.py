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

router = APIRouter(
    prefix='/api/report/purchase-invoice'
)

@router.get("", response_model=ReportResponse)
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
        page = int(page)

        if component_category_id not in (None, ''):
            component_category_id = int(component_category_id)

        if invoice_status not in (None, ''):
            invoice_status = int(invoice_status)

        query = (
            db.query(PurchaseInvoice.id)
              .join(PurchaseInvoice.purchase_invoice_lines)
              .filter(PurchaseInvoice.deleted == False)
        )

        if start_date not in (None, ''):
            start_date_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(PurchaseInvoice.invoice_date >= start_date_date)

        if end_date not in (None, ''):
            end_date_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(PurchaseInvoice.invoice_date <= end_date_date)
        
        if invoice_status not in (None, ''):
            query = query.filter(PurchaseInvoice.status == invoice_status)

        if keyword not in (None, ''):
            query = query.filter((PurchaseInvoice.purchase_invoice_no.ilike(f"%{keyword}%")))

        if component_name not in (None, ''):
            query = query.filter(PurchaseInvoiceLine.component_name.ilike(f"%{component_name}%"))

        if component_category_id not in (None, ''):
            query = query.filter(PurchaseInvoiceLine.component_category_id == component_category_id)

        invoice_ids = [id[0] for id in query.all()]

        purchase_invoices = (
            db.query(PurchaseInvoice)
                .options(joinedload(PurchaseInvoice.purchase_invoice_lines)
                            .subqueryload(PurchaseInvoiceLine.inbound_delivery_lines)
                            .subqueryload(InboundDeliveryLine.inbound_delivery))
                .filter(PurchaseInvoice.id.in_(invoice_ids))
                .order_by(desc(PurchaseInvoice.created_at))
                .offset((page - 1) * item_per_page)
                .limit(item_per_page)
        )

        query_total_item = db.execute(text(
                "SELECT COUNT(*) " \
                "FROM purchase_invoices pi " \
                "LEFT JOIN purchase_invoice_lines pil ON pil.purchase_invoice_id = pi.id " \
                "LEFT JOIN inbound_delivery_lines idl ON idl.purchase_invoice_line_id = pil.id " \
                "LEFT JOIN inbound_deliveries id ON id.id = idl.inbound_delivery_id " \
                "WHERE pi.deleted = FALSE AND id.deleted = FALSE"
            )).first()
        total_item = query_total_item[0] if query_total_item else 0

        current_page = page
        has_next_page = (total_item > 0) and (total_item / (current_page * item_per_page) < 1)
        has_prev_page = (total_item > 0) and (current_page > 1)
        next_page_url = (f"http://localhost:8080/api/report/purchase-invoice?page={current_page + 1}" if has_next_page else None)
        prev_page_url = (f"http://localhost:8080/api/report/purchase-invoice?page={current_page - 1}" if has_prev_page else None)

        return {
            'report_headers': generate_headers(),
            'report_body': generate_report(purchase_invoices, component_name, component_category_id),
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

def generate_report(purchase_invoices, component_name, component_category_id):
    result = []

    for invoice in purchase_invoices:
        for invoice_line in invoice.purchase_invoice_lines:
            if (component_name not in (None, '')) and (component_name.casefold() not in invoice_line.component_name.casefold()):
                continue
            elif (component_category_id not in (None, '')) and (component_category_id != invoice_line.component_category_id):
                continue

            unique_delivery_dates = {}
            unique_delivery_nos = {}
            for ib_line in invoice_line.inbound_delivery_lines:
                inbound_delivery = ib_line.inbound_delivery
                unique_delivery_dates[inbound_delivery.inbound_delivery_date] = inbound_delivery.inbound_delivery_date
                unique_delivery_nos[inbound_delivery.inbound_delivery_no] = inbound_delivery.inbound_delivery_no
            delivery_nos = unique_delivery_nos.values()
            delivery_dates = unique_delivery_dates.values()

            total_received_qty = sum(ib_line.received_quantity for ib_line in invoice_line.inbound_delivery_lines)
            total_damaged_qty = sum(ib_line.damaged_quantity for ib_line in invoice_line.inbound_delivery_lines)
            total_amount_received = total_received_qty * invoice_line.price_per_unit
            inbound_delivery_dates = ", ".join({ delivery_date.strftime('%Y-%m-%d') for delivery_date in delivery_dates})
            inbound_delivery_nos = ", ".join({ delivery_no for delivery_no in delivery_nos})

            result.append([
                { 'text': invoice.purchase_invoice_no },
                { 'text': invoice.invoice_date.strftime("%Y-%m-%d") },
                { 'text': invoice_line.component_name },
                { 'text': invoice_line.component_category_name },
                { 'text': str(invoice_line.quantity) },
                { 'text': str(invoice_line.price_per_unit) },
                { 'text': str(invoice_line.total_line_amount) },
                { 'text': str(total_received_qty) },
                { 'text': str(total_damaged_qty) },
                { 'text': str(total_amount_received) },
                { 'text': inbound_delivery_dates },
                { 'text': inbound_delivery_nos }
            ])

    return result

def generate_headers():
    return [
        {
            'text': 'Purchase Invoice No'
        },
        {
            'text': 'Invoice Date'
        },
        {
            'text': 'Component Name'
        },
        {
            'text': 'Category Name'
        },
        {
            'text': 'Quantity'
        },
        {
            'text': 'Price Per Unit'
        },
        {
            'text': 'Total Price'
        },
        {
            'text': 'Inbound Received Qty'
        },
        {
            'text': 'Inbound Damaged Qty'
        },
        {
            'text': 'Total Amount Received'
        },
        {
            'text': 'Inbound Delivery Dates'
        },
        {
            'text': 'Inbound Delivery No(s)'
        }
    ]
    