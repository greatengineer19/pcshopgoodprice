from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy import (
        select,
        func,
        delete,
        text,
        and_,
        or_,
        not_
)
from src.schemas import (
    SellableProductsAsListResponse,
    ComputerComponentAsResponse,
    SellableProductResponse
)
from src.models import (
    ComputerComponent,
    ComputerComponentCategory,
    ComputerComponentReview,
    ComputerComponentSellPriceSetting,
    User
)
import logging
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from src.data.review_schema import component_reviews_hash_map
import random
from datetime import datetime
from sqlalchemy.sql.expression import case
from sqlalchemy.dialects import postgresql

router = APIRouter(
    prefix='/api/sellable-products'
)

@router.get("", response_model=SellableProductsAsListResponse)
def index(
        start_price: Optional[str] = Query(None),
        end_price: Optional[str] = Query(None),
        min_rating: Optional[str] = Query(None),
        component_category_ids: Optional[str] = Query(None),
        db: Session = Depends(get_db)
    ):
    try:
        base_query = (
                db.query(ComputerComponent)
                .join(ComputerComponent.component_category)
                .options(
                joinedload(ComputerComponent.computer_component_sell_price_settings)
            )
        )
        
        # Initialize filters list
        filters = []
        
        # Filter 1: Component Categories
        if component_category_ids:
            try:
                category_ids = list(map(int, component_category_ids.split(',')))
                filters.append(ComputerComponent.component_category_id.in_(category_ids))
            except (ValueError, AttributeError):
                pass
        
        # Filter 2: Minimum Rating
        if min_rating:
            try:
                min_rating = int(min_rating)
                # Subquery for components with average rating >= min_rating
                avg_rating = db.query(
                    ComputerComponentReview.component_id,
                    func.avg(ComputerComponentReview.rating).label('avg_rating')
                ).group_by(ComputerComponentReview.component_id).subquery()
                
                filters.append(
                    ComputerComponent.id.in_(
                        db.query(avg_rating.c.component_id)
                        .filter(avg_rating.c.avg_rating >= min_rating)
                    )
                )
            except (ValueError, TypeError):
                pass
    
        # Filter 3: Price Range
        if start_price or end_price:
            try:
                weekday = datetime.now().isoweekday()  # Returns 1-7 (Mon-Sun)

                weekday_tuple_ids = (
                    db.query(ComputerComponent.id)
                    .join(ComputerComponentSellPriceSetting, and_(
                        ComputerComponentSellPriceSetting.day_type == weekday,
                        ComputerComponentSellPriceSetting.component_id == ComputerComponent.id,
                        ComputerComponentSellPriceSetting.active.is_(True)))
                    .filter(
                        ComputerComponentSellPriceSetting.price_per_unit >= (int(start_price) if start_price else 0),
                        ComputerComponentSellPriceSetting.price_per_unit <= (int(end_price) if end_price else float('inf'))
                    )
                    .scalar()
                )
                weekday_ids = [tuple[0] for tuple in weekday_tuple_ids] if weekday_tuple_ids is not None else []

                default_tuple_ids = (
                    db.query(ComputerComponent.id)
                    .join(ComputerComponentSellPriceSetting, and_(
                        ComputerComponentSellPriceSetting.day_type == 0,
                        ComputerComponentSellPriceSetting.component_id == ComputerComponent.id,
                        ComputerComponentSellPriceSetting.active.is_(True)))
                    .filter(
                        ComputerComponentSellPriceSetting.price_per_unit >= (int(start_price) if start_price else 0),
                        ComputerComponentSellPriceSetting.price_per_unit <= (int(end_price) if end_price else float('inf')),
                        not_(ComputerComponentSellPriceSetting.id.in_(weekday_ids))
                    )
                    .all()
                )
                default_ids = [tuple[0] for tuple in default_tuple_ids] if default_tuple_ids is not None else []

                # print((db.query(ComputerComponent.id)
                #     .join(ComputerComponentSellPriceSetting, and_(
                #         ComputerComponentSellPriceSetting.day_type == 0,
                #         ComputerComponentSellPriceSetting.component_id == ComputerComponent.id,
                #         ComputerComponentSellPriceSetting.active.is_(True)))
                #     .filter(
                #         ComputerComponentSellPriceSetting.price_per_unit >= (int(start_price) if start_price else 0),
                #         ComputerComponentSellPriceSetting.price_per_unit <= (int(end_price) if end_price else float('inf')),
                #         not_(ComputerComponentSellPriceSetting.id.in_(weekday_ids))
                #     )).statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

                # Then filter based on the effective price range
                filters.append(ComputerComponent.id.in_(default_ids))
            except (ValueError, TypeError):
                pass

        # Apply all filters
        if filters:
            base_query = base_query.filter(or_(*filters))
        
        # Calculate and attach ratings in a single query
        components = base_query.order_by(ComputerComponentCategory.name, ComputerComponent.name).all()
        
        components_by_category_ids = {}
        if components:
            # Prefetch ratings in one query
            component_ids = [c.id for c in components]
            
            ratings_query = db.query(
                ComputerComponentReview.component_id,
                func.count(ComputerComponentReview.id).label('count_review_given'),
                func.avg(ComputerComponentReview.rating).label('avg_rating')
            ).filter(
                ComputerComponentReview.component_id.in_(component_ids)
            ).group_by(
                ComputerComponentReview.component_id
            )
            
            # Create ratings dictionary with proper default values
            ratings = {
                r.component_id: {
                    'rating': round(float(r.avg_rating), 2) if r.avg_rating is not None else 0.0,
                    'count_review_given': int(r.count_review_given) if r.count_review_given is not None else 0
                } 
                for r in ratings_query
            }

            # Safely attach ratings to components with defaults
            weekday = datetime.now().isoweekday() or 7

            for component in components:
                rating_data = ratings.get(component.id, {'rating': 0.0, 'count_review_given': 0})
                component.rating = rating_data['rating']
                component.count_review_given = rating_data['count_review_given']

                default_price = next(
                    (sps.price_per_unit for sps in component.computer_component_sell_price_settings if sps.day_type == 0),
                    0
                )

                price = next(
                    (sps.price_per_unit for sps in component.computer_component_sell_price_settings
                    if sps.day_type == weekday and sps.status == 0),
                    default_price
                )

                component.sell_price = price

                components_by_category_ids.setdefault(component.component_category_id, []).append(component)

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
            raise HTTPException(status_code=404, detail="Computer not found")
        
        ratings_query = db.query(
            ComputerComponentReview.component_id,
            func.count(ComputerComponentReview.id).label('count_review_given'),
            func.avg(ComputerComponentReview.rating).label('avg_rating')
        ).filter(
            ComputerComponentReview.component_id == computer_component.id
        ).group_by(
            ComputerComponentReview.component_id
        )
        
        # Create ratings dictionary with proper default values
        ratings = {
            r.component_id: {
                'rating': round(float(r.avg_rating), 2) if r.avg_rating is not None else 0.0,
                'count_review_given': int(r.count_review_given) if r.count_review_given is not None else 0
            } 
            for r in ratings_query
        }

        # Safely attach ratings to components with defaults
        weekday = datetime.now().isoweekday() or 7
        
        rating_data = ratings.get(computer_component.id, {'rating': 0.0, 'count_review_given': 0})
        computer_component.rating = rating_data['rating']
        computer_component.count_review_given = rating_data['count_review_given']

        default_price = next(
            (sps.price_per_unit for sps in computer_component.computer_component_sell_price_settings if sps.day_type == 0),
            0
        )

        price = next(
            (sps.price_per_unit for sps in computer_component.computer_component_sell_price_settings
            if sps.day_type == weekday and sps.status == 0),
            default_price
        )

        computer_component.sell_price = price

        return computer_component
    finally:
        db.close()