from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy import (func)
from src.schemas import (
    SellableProductsAsListResponse,
    SellableProductResponse
)
from src.models import (
    ComputerComponent,
    ComputerComponentCategory
)
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from src.sellable_products.injected_component_ids_and_rating_per_categories_service import InjectedComponentIdsAndRatingPerCategoriesService
from src.sellable_products.filter_service import FilterService
from src.sellable_products.ratings_in_component_ids_service import RatingsInComponentIdsService
from src.sellable_products.sell_price_and_ratings_finder_service import SellPriceAndRatingsFinderService

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

@router.get("/{slug}", response_model=SellableProductResponse)
def show_by_slug(slug: str, db: Session = Depends(get_db)):
    try:
        product_name = slug.replace('_', ' ')
        computer_component = (
            db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
            .filter(func.lower(ComputerComponent.name) == func.lower(product_name))
            .first()
        )

        if computer_component is None:
            raise HTTPException(status_code=404, detail="Requested component not found")
        
        component_ids = [computer_component.id]
        ratings_service = RatingsInComponentIdsService(db=db, component_ids=component_ids)
        ratings = ratings_service.call()

        sell_price_and_ratings_service = SellPriceAndRatingsFinderService(db=db, ratings=ratings, component=computer_component)
        computer_component = sell_price_and_ratings_service.call()

        return computer_component
    finally:
        db.close()