from src.models import ( SalesQuote, SalesQuoteLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( desc )
from typing import Optional
from src.computer_components.image_service import ImageService

class ShowService:
    def __init__(self, db: Session, id: Optional[int], user_id: Optional[int]):
        self.db = db
        self.id = id
        self.user_id = user_id

    def call(self):
        query = self.db.query(SalesQuote).options(joinedload(SalesQuote.sales_quote_lines).subqueryload(SalesQuoteLine.component))
        if self.id:
            query = query.filter(SalesQuote.id == self.id)
        if self.user_id:
            query = query.filter(SalesQuote.customer_id == self.user_id)
        query = query.order_by(desc(SalesQuote.id)).first()

        if not query:
            return

        image_service = ImageService()

        for quote_line in query.sales_quote_lines:
            quote_line.images = image_service.presigned_url_generator(quote_line.component)
            quote_line.component_name = quote_line.component.name

        return query
