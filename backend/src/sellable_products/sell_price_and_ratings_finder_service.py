from sqlalchemy.orm import Session
from datetime import datetime
from src.computer_components.service import Service

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
        rating_data = self.ratings.get(self.component.id, {'rating': 0.0, 'count_review_given': 0})
        self.component.rating = rating_data['rating']
        self.component.count_review_given = rating_data['count_review_given']

        price_service = Service()
        price = price_service.select_price(self.component)

        self.component.sell_price = price
        return self.component