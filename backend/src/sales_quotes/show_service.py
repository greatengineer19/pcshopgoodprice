from src.models import ( SalesQuote )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( desc )
from typing import Optional

class ShowService:
    def __init__(self, db: Session, id: Optional[int], user_id: Optional[int]):
        self.db = db
        self.id = id
        self.user_id = user_id

    def call(self):
        query = self.db.query(SalesQuote).options(joinedload(SalesQuote.sales_quote_lines))
        if self.id:
            query = query.filter(SalesQuote.id == self.id)
        if self.user_id:
            query = query.filter(SalesQuote.customer_id == self.user_id)
        query = query.order_by(desc(SalesQuote.id)).first()

        return query
