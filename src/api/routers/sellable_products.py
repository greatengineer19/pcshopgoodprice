from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy import (func)
from src.schemas import (
    SellableProductsAsListResponse,
    SellableProductResponse,
    OneSellableProductResponse
)
from src.models import (
    ComputerComponent,
    ComputerComponentCategory
)
from sqlalchemy.orm import joinedload, Session
from src.api.session_db import get_db
from src.sellable_products.injected_component_ids_and_rating_per_categories_service import InjectedComponentIdsAndRatingPerCategoriesService
from src.sellable_products.filter_service import FilterService
from src.sellable_products.ratings_in_component_ids_service import RatingsInComponentIdsService
from src.sellable_products.sell_price_and_ratings_finder_service import SellPriceAndRatingsFinderService
from src.api.s3_dependencies import ( bucket_name, s3_client )

router = APIRouter(prefix='/api/sellable-products', tags=["Sellable Products"])

@router.get("", response_model=SellableProductsAsListResponse)
def index(
        start_price: Optional[str] = Query(None),
        end_price: Optional[str] = Query(None),
        min_rating: Optional[str] = Query(None),
        component_category_ids: Optional[str] = Query(None),
        db: Session = Depends(get_db)
    ):
    try:
        filter_service = FilterService(
                            db=db,
                            start_price=start_price,
                            end_price=end_price,
                            min_rating=min_rating,
                            component_category_ids=component_category_ids
                         )
        components = filter_service.call()
        
        components_by_category_ids = {}
        if components:
            injected_components_service = InjectedComponentIdsAndRatingPerCategoriesService(db=db, components=components)
            components_by_category_ids = injected_components_service.call()
        else:
            return { 'sellable_products': {} }

        component_categories = db.query(ComputerComponentCategory.id, ComputerComponentCategory.name).order_by(ComputerComponentCategory.name).all()
        result = {}
        for index, component_category in enumerate(component_categories):
            select_components = components_by_category_ids.get(component_category.id, [])
            if not select_components:
                continue

            result[index] = {
                'name': component_category.name,
                'components': components_by_category_ids.get(component_category.id, [])
            }
        
        return { 'sellable_products': result }
    finally:
        db.close()

@router.get("/{product_code}", response_model=OneSellableProductResponse)
def show_by_product_code(product_code: str, db: Session = Depends(get_db)):
    try:
        computer_component = (
            db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings),
                     joinedload(ComputerComponent.computer_component_reviews))
            .filter(func.lower(ComputerComponent.product_code) == func.lower(product_code))
            .first()
        )

        if computer_component is None:
            raise HTTPException(status_code=404, detail="Requested component not found")
        
        component_ids = [computer_component.id]
        ratings_service = RatingsInComponentIdsService(db=db, component_ids=component_ids)
        ratings = ratings_service.call()

        sell_price_and_ratings_service = SellPriceAndRatingsFinderService(db=db, ratings=ratings, component=computer_component)
        computer_component = sell_price_and_ratings_service.call()
        images = []
        if computer_component.images:
            presigned_url = s3_client().generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name(), 'Key': computer_component.images[0]},
                ExpiresIn=3600
            )
            images = [presigned_url]
        computer_component.images = images

        return computer_component
    finally:
        db.close()