from src.models import ( Inventory, SalesDelivery )
from sqlalchemy.orm import joinedload, Session
from src.schemas import ( SalesDeliveryStatusEnum )
from typing import Optional, List
from datetime import datetime

class CreateInventoryService:
    def __init__(self, *, db: Session, sales_delivery: SalesDelivery):
        self.db = db
        self.sales_delivery = sales_delivery

    def call(self) -> List[Inventory]:
        inventories = []
        now = datetime.now()
    
        for delivery_line in self.sales_delivery.sales_delivery_lines:
            inventory = Inventory(
                out_stock=delivery_line.quantity,
                stock_date=now,
                component_id=delivery_line.component_id,
                resource_type='SalesDelivery',
                resource_id=self.sales_delivery.id,
                resource_line_type='SalesDeliveryLine',
                resource_line_id=delivery_line.id
            )
            inventories.append(inventory)

        return inventories