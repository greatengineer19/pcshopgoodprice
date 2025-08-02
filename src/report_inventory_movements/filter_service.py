from src.models import ( Inventory, ComputerComponent, ComputerComponentCategory )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from datetime import datetime

class FilterService:
    def __init__(
        self,
        *,
        db: Session,
        start_date,
        end_date,
        page,
        item_per_page,
        component_name,
        component_category_id,
        transaction_type,
        keyword):
        self.db = db
        start_date = start_date or None
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date is not None else None
        self.start_date = start_date

        end_date = end_date or None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date is not None else None
        self.end_date = end_date
        self.page = int(page)
        self.item_per_page = item_per_page
        self.component_name = component_name or None

        component_category_id = component_category_id or None
        component_category_id = int(component_category_id) if component_category_id is not None else None
        self.component_category_id = component_category_id

        self.transaction_type = transaction_type or None
        self.keyword = keyword or None

    def call(self):
        query = (
            self.db.query(Inventory.id)
                .join(Inventory.component)
                .join(ComputerComponent.component_category)
        )

        if self.start_date:
            query = query.filter(Inventory.stock_date >= self.start_date)
        if self.end_date:
            query = query.filter(Inventory.stock_date <= self.end_date)
        if self.transaction_type:
            query = query.filter(Inventory.resource_type == self.transaction_type)
        if self.keyword:
            query = query.filter(ComputerComponent.name.ilike(f"%{self.keyword}%"))
        if self.component_name:
            query = query.filter(ComputerComponent.name.ilike(f"%{self.component_name}%"))
        if self.component_category_id:
            query = query.filter(ComputerComponent.component_category_id == self.component_category_id)

        inventory_ids = [id[0] for id in query.all()]
        inventories = (
            self.db.query(Inventory)
                .join(Inventory.component)
                .join(ComputerComponent.component_category)
                .options(joinedload(Inventory.component)
                            .subqueryload(ComputerComponent.component_category))
                .filter(Inventory.id.in_(inventory_ids))
                .order_by(ComputerComponentCategory.name, ComputerComponent.name, Inventory.stock_date, Inventory.created_at)
                .offset((self.page - 1) * self.item_per_page)
                .limit(self.item_per_page)
        )

        return inventories
