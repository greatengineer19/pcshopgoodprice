from src.models import ( ComputerComponentReview )
from sqlalchemy.orm import Session
from sqlalchemy import func

class RatingsInComponentIdsService:
    def __init__(
        self,
        *,
        db: Session,
        component_ids):
        self.db = db
        self.component_ids = component_ids

    def call(self) -> dict:
        ratings_query = self.db.query(
                            ComputerComponentReview.component_id,
                            func.count(ComputerComponentReview.id).label('count_review_given'),
                            func.avg(ComputerComponentReview.rating).label('avg_rating')
                        ).filter(
                            ComputerComponentReview.component_id.in_(self.component_ids)
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

        return ratings