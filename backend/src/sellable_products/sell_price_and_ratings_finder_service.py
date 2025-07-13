from sqlalchemy.orm import Session
from datetime import datetime

class SellPriceAndRatingsFinderService:
    def __init__(
        self,
        *,
        db: Session,
        ratings,
        component):
        self.db = db
        self.component = component
        self.ratings = ratings

    def call(self):
        weekday = datetime.now().isoweekday() or 7
        rating_data = self.ratings.get(self.component.id, {'rating': 0.0, 'count_review_given': 0})
        self.component.rating = rating_data['rating']
        self.component.count_review_given = rating_data['count_review_given']

        default_price = next(
            (sps.price_per_unit for sps in self.component.computer_component_sell_price_settings if sps.day_type == 0),
            0
        )

        price = next(
            (sps.price_per_unit for sps in self.component.computer_component_sell_price_settings
            if sps.day_type == weekday and sps.active is True),
            default_price
        )

        self.component.sell_price = price
        return self.component