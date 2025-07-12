from src.models import (
    PurchaseInvoice,
    InboundDelivery,
    InboundDeliveryLine,
    InboundDeliveryAttachment
)
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( InboundDeliveryStatusEnum, InboundDeliveryAsParams )
from src.inbound_deliveries.service import ( Service )
from decimal import Decimal

class BuildService:
    def __init__(self, db: Session):
        self.db = db

    def build(self, params: InboundDeliveryAsParams, invoice: PurchaseInvoice):
        inbound_delivery = InboundDelivery(
            purchase_invoice_id=params.purchase_invoice_id,
            purchase_invoice_no=invoice.purchase_invoice_no,
            inbound_delivery_date=params.inbound_delivery_date,
            inbound_delivery_reference=params.inbound_delivery_reference,
            received_by=params.received_by,
            notes=params.notes,
            status=InboundDeliveryStatusEnum.DELIVERED
        )

        inbound_delivery.inbound_delivery_lines = self.build_lines(params)
        inbound_delivery.inbound_delivery_attachments = self.build_attachments(params)
        numbering_service = Service(self.db)
        numbering_service.generate_delivery_no(inbound_delivery)

        return inbound_delivery

    def build_lines(self, params: InboundDeliveryAsParams):
        delivery_lines = []
        for param_line in params.inbound_delivery_lines_attributes:
            expected_quantity = Decimal(param_line.expected_quantity)
            received_quantity = Decimal(param_line.received_quantity)
            damaged_quantity = Decimal(param_line.damaged_quantity)
            price = Decimal(param_line.price_per_unit)
            total_line_amount = price * received_quantity

            delivery_line = InboundDeliveryLine(
                purchase_invoice_line_id=param_line.purchase_invoice_line_id,
                component_id=param_line.component_id,
                component_name=param_line.component_name,
                component_category_id=param_line.component_category_id,
                component_category_name=param_line.component_category_name,
                expected_quantity=expected_quantity,
                received_quantity=received_quantity,
                damaged_quantity=damaged_quantity,
                price_per_unit=price,
                total_line_amount=total_line_amount
            )

            delivery_lines.append(delivery_line)

        return delivery_lines
    
    def build_attachments(self, params: InboundDeliveryAsParams):
        attachment_lines = []
        for param_attachment in params.inbound_delivery_attachments_attributes:
            attachment_line = InboundDeliveryAttachment(
                uploaded_by=param_attachment.uploaded_by,
                file_s3_key=param_attachment.file_s3_key
            )
            attachment_lines.append(attachment_line)

        return attachment_lines