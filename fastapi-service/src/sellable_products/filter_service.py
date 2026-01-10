from src.models import ( ComputerComponent, ComputerComponentCategory )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( or_, and_ )
from fastapi import ( HTTPException )
from src.sellable_products.min_rating_filter_component_ids_service import MinRatingFilterComponentIdsService
from src.sellable_products.component_ids_filter_by_prices_service import ComponentIdsFilterByPricesService
from sqlalchemy.dialects import postgresql

class FilterService:
    def __init__(
        self,
        *,
        db: Session,
        start_price,
        end_price,
        min_rating,
        component_category_ids):
        self.db = db
        self.start_price = start_price
        self.end_price = end_price
        self.min_rating = min_rating
        self.component_category_ids = component_category_ids

    def call(self):
        base_query = (
                self.db.query(ComputerComponent)
                .join(ComputerComponent.component_category)
                .options(
                    joinedload(ComputerComponent.computer_component_sell_price_settings
                )
            )
        )
      
        component_ids = None
        if self.min_rating:
            min_rating_service = MinRatingFilterComponentIdsService(db=self.db, min_rating=self.min_rating)
            rating_filtered_component_ids = min_rating_service.call()
            if not rating_filtered_component_ids:
                return []
            component_ids = rating_filtered_component_ids
    
        if self.start_price or self.end_price:
            prices_service = ComponentIdsFilterByPricesService(db=self.db, start_price=self.start_price, end_price=self.end_price)
            default_ids = prices_service.call()
            if not default_ids:
                return []
            component_ids = list(set(component_ids) & set(default_ids)) if component_ids else default_ids

        if self.component_category_ids:
            try:
                category_ids = list(map(int, self.component_category_ids.split(',')))
                base_query = base_query.filter(
                    ComputerComponent.component_category_id.in_(category_ids)
                )
            except (ValueError, AttributeError):
                raise HTTPException(status_code=500, detail="Invalid category IDs")
            
        if component_ids is not None:
            if not component_ids:
                return []
            base_query = base_query.filter(ComputerComponent.id.in_(component_ids))
        
        # Calculate and attach ratings in a single query
        components = base_query.order_by(ComputerComponentCategory.name, ComputerComponent.name).all()
        return components


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
