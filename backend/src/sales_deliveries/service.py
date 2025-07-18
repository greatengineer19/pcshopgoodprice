from src.models import ( SalesDelivery )
from sqlalchemy.orm import Session
from sqlalchemy import ( text )
import re

class Service:
    def __init__(self, db: Session):
        self.db = db
        self.latest_delivery_no = 0

    def generate_latest_sales_delivery_no(self):
        last_no = self.db.execute(text(
                "SELECT sales_delivery_no " \
                "FROM sales_deliveries " \
                "ORDER BY id DESC LIMIT 1 " \
                "FOR UPDATE"
            )).first()
        
        if last_no and last_no[0]:
            match = re.search(r"OUTBOUND-DELIVERY-(\d+)", last_no[0])
            if match:
                last_number = int(match.group(1))
                self.latest_delivery_no = last_number + 1
            else:
                self.latest_delivery_no = 1
        else:
            self.latest_delivery_no = 1    
    
    def assign_sales_delivery_no(self, sales_delivery: SalesDelivery):
        sales_delivery.sales_delivery_no = f"OUTBOUND-DELIVERY-{self.latest_delivery_no:05d}"
        self.latest_delivery_no += 1

        return sales_delivery

