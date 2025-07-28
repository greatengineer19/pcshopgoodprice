from src.models import ( PurchaseInvoice, InboundDelivery, Inventory )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( StatusEnum )

class CreateFromInboundDeliveryService:
    def __init__(self, db: Session):
        self.db = db

    def create_inventories(self, inbound_delivery: InboundDelivery):
        db = self.db

        for delivery_line in inbound_delivery.inbound_delivery_lines:
            inventory = Inventory(
                in_stock= delivery_line.received_quantity,
                stock_date=inbound_delivery.inbound_delivery_date,
                component_id=delivery_line.component_id,
                resource_id=inbound_delivery.id,
                resource_type='InboundDelivery',
                resource_line_id=delivery_line.id,
                resource_line_type='InboundDeliveryLine',
                buy_price=delivery_line.price_per_unit
            )
            db.add(inventory)

        db.commit()