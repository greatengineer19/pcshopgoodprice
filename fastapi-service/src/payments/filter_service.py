from src.infrastructure.persistence.models.payment import Payment
from sqlalchemy import desc
from sqlalchemy.orm import Session

class FilterService:
    def __init__(
        self,
        *,
        db: Session,
        page,
        item_per_page
    ):
        self.db = db
        self.page = int(page or 1)
        self.item_per_page = item_per_page or 50
        self.offset = (self.page - 1) * self.item_per_page

    def call(self):
        data = (
            self.db
                .query(Payment)
                .order_by(desc(Payment.id))
                .offset(self.offset)
                .limit(self.item_per_page)
                .all()
        )

        return data