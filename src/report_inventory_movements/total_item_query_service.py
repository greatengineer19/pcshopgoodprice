from sqlalchemy.orm import Session
from sqlalchemy import ( text )

class TotalItemQueryService:
    def __init__(self, db: Session):
        self.db = db

    def call(self) -> int:
        query_total_item = self.db.execute(text(
                "SELECT COUNT(*) " \
                "FROM inventories i "
            )).first()
        total_item = query_total_item[0] if query_total_item else 0
        return total_item