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
    SalesInvoiceResponse
)
from src.models import (
    SalesInvoice,
    SalesInvoiceLine,
    User
)
import logging
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from datetime import datetime
from utils.auth import get_current_user
import re
from fastapi.encoders import jsonable_encoder
import gc

router = APIRouter(
    prefix='/api/sales-invoices'
)

@router.get('/{id}', response_model=SalesInvoiceResponse)
def show(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:    
        sales = (
            db.query(SalesInvoice)
            .options(joinedload(SalesInvoice.sales_invoice_lines))
            .filter(SalesInvoice.id == id)
            .first()
        )

        if sales is None:
            raise HTTPException(status_code=404, detail="Data not found")
        sales.status = 'ok'
        return sales
    finally:
        db.close()
