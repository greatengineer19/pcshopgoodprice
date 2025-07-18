from src.models import ( SalesDelivery )
from sqlalchemy.orm import Session
from src.schemas import ( SalesDeliveryStatusEnum )
from src.computer_components.image_service import ImageService

class ShowService:
    def __init__(self, *, db: Session, sales_delivery: SalesDelivery):
        self.db = db
        self.sales_delivery = sales_delivery

    def call(self):
        self.sales_delivery.status = SalesDeliveryStatusEnum(self.sales_delivery.status).name
        sales_invoice = self.sales_delivery.sales_invoice

        self.sales_delivery.customer_id = sales_invoice.customer_id
        self.sales_delivery.customer_name = sales_invoice.customer_name
        self.sales_delivery.shipping_address = sales_invoice.shipping_address

        image_service = ImageService()
        for delivery_line in self.sales_delivery.sales_delivery_lines:
            delivery_line.component_name = delivery_line.component.name
            delivery_line.images = image_service.presigned_url_generator(delivery_line.component)

        return self.sales_delivery