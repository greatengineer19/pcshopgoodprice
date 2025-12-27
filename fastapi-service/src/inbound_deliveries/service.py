from src.models import ( PurchaseInvoice, InboundDelivery )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re

class Service:
    def __init__(self, db: Session):
        self.db = db

    def generate_delivery_no(self, delivery: InboundDelivery):
        if delivery.inbound_delivery_no is not None:
            return delivery
        
        last_no = self.db.execute(text(
                "SELECT inbound_delivery_no " \
                "FROM inbound_deliveries " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()
        
        if last_no and last_no[0]:
            match = re.search(r"IBD-(\d+)", last_no[0])
            if match:
                last_number = int(match.group(1))
                next_number = last_number + 1
            else:
                next_number = 1
        else:
            next_number = 1

        delivery.inbound_delivery_no = f"IBD-{next_number:05d}"
        return delivery