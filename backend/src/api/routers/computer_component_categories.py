from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import (
    select,
    func
)
from src.schemas import (
    ComputerComponentCategoryAsListResponse
)
from src.models import (
    ComputerComponentCategory
)
import logging
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db

router = APIRouter(
    prefix='/api/computer-component-categories'
)
  
@router.get("", response_model=ComputerComponentCategoryAsListResponse)
def index(db: Session = Depends(get_db)):
    try:
        components = db.query(ComputerComponentCategory).order_by(ComputerComponentCategory.name).all()

        if not components:
            return { 'computer_component_categories': [] }
        
        return { 'computer_component_categories': components }
    finally:
        db.close()
