from src.models import ( ComputerComponent, ComputerComponentSellPriceSetting )
from sqlalchemy.orm import Session
from sqlalchemy import ( and_, not_)
from datetime import datetime
from fastapi import ( HTTPException )
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

class ComponentIdsFilterByPricesService:
    def __init__(
        self,
        *,
        db: Session,
        start_price,
        end_price):
        self.db = db

        start_price = start_price or None
        self.start_price = int(start_price) if start_price else 0

        end_price = end_price or None
        self.end_price = int(end_price) if end_price else float('inf')

    def call(self):
        try:
            current_weekday = datetime.now().isoweekday()  # Returns 1-7 (Mon-Sun)

            weekday_setting = aliased(ComputerComponentSellPriceSetting)
            default_setting = aliased(ComputerComponentSellPriceSetting)

            base_query = (
                self.db.query(ComputerComponent.id)
                .join(weekday_setting, and_(
                    weekday_setting.component_id == ComputerComponent.id,
                    weekday_setting.active.is_(True),
                    weekday_setting.day_type == current_weekday
                    ), isouter=True)
                .join(
                    default_setting, and_(
                    default_setting.component_id == ComputerComponent.id,
                    default_setting.active.is_(True),
                    default_setting.day_type == 0
                    ), isouter=True
                )
            )

            weekday_ids = [
                comp_id for comp_id, in base_query.filter(
                    weekday_setting.price_per_unit >= self.start_price,
                    weekday_setting.price_per_unit <= self.end_price
                ).all()
            ]

            default_ids = [
                comp_id for comp_id, in base_query.filter(
                    weekday_setting.id == None,
                    default_setting.price_per_unit >= self.start_price,
                    default_setting.price_per_unit <= self.end_price
                ).all()
            ]

            result_ids = weekday_ids + default_ids
            result_ids = list(set(result_ids))

            return result_ids
        except SQLAlchemyError as e:
            # Catch SQLAlchemy-specific errors for better granularity
            raise HTTPException(status_code=500, detail=f"Database error while filtering price range: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
