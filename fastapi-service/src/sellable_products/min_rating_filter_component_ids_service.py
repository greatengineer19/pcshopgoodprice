from src.models import ( ComputerComponentReview )
from sqlalchemy.orm import Session
from sqlalchemy import ( func )
from fastapi import ( HTTPException )

class MinRatingFilterComponentIdsService:
    def __init__(
        self,
        *,
        db: Session,
        min_rating):
        self.db = db
        min_rating = min_rating or None
        self.min_rating = int(min_rating) if min_rating else None

    def call(self):
        try:
            # Subquery for components with average rating >= min_rating
            avg_rating = self.db.query(
                ComputerComponentReview.component_id,
                func.avg(ComputerComponentReview.rating).label('avg_rating')
            ).group_by(ComputerComponentReview.component_id).subquery()
            
            query = self.db.query(avg_rating.c.component_id)
            if self.min_rating:
                query = query.filter(avg_rating.c.avg_rating >= self.min_rating)
            component_ids = [comp_id for comp_id, in query.all()]

            return component_ids
        except (ValueError, TypeError):
            raise HTTPException(status_code=500, detail="Error while filtering min rating")
