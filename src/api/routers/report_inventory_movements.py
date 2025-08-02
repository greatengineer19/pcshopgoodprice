from fastapi import APIRouter, Depends, HTTPException, Query
from typing import ( Optional )
from src.schemas import (
    ReportResponse
)
import logging
from sqlalchemy.orm import  Session
from src.api.dependencies import get_db
from src.report.paging_service import PagingService
from src.report.header_generator_service import HeaderGeneratorService
from src.report_inventory_movements.filter_service import FilterService
from src.report_inventory_movements.total_item_query_service import TotalItemQueryService
from src.report_inventory_movements.response_generator_service import ResponseGeneratorService


router = APIRouter(prefix='/api/report/inventory-movement', tags=["Report Inventory Movements"])

@router.get("", response_model=ReportResponse, status_code=200)
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
        filter_service = FilterService(db=db,
            start_date=start_date,
            end_date=end_date,
            page=page,
            item_per_page=item_per_page,
            component_name=component_name,
            component_category_id=component_category_id,
            transaction_type=transaction_type,
            keyword=keyword)
        inventories = filter_service.call()

        total_query = TotalItemQueryService(db)
        total_item = total_query.call()

        paging_service = PagingService(db)
        paging = paging_service.call(
            page=page,
            item_per_page=item_per_page,
            total_item=total_item,
            endpoint="http://localhost:80/api/report/inventory-movement"
        )

        return {
            'report_headers': generate_headers(),
            'report_body': generate_report(inventories, component_name, component_category_id),
            'paging': paging

        }
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

def generate_report(inventories, component_name, component_category_id):
    service = ResponseGeneratorService()
    return service.call(inventories, component_name, component_category_id)

def generate_headers():
    text_headers = [
        'Component Category', 'Component Name', 'Stock Date', 'Created At',
        'Transaction Type', 'Transaction No.',  'Received By',
        'In Stock', 'Out Stock', 'Final Moving Stock', 'Buy Price / Unit'        
    ]
    service = HeaderGeneratorService()

    return service.call(text_headers)
    