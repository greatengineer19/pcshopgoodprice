from fastapi import HTTPException
from src.models import ( InboundDelivery )
from sqlalchemy.orm import joinedload, Session
from src.schemas import ( InboundDeliveryStatusEnum)
from decimal import Decimal
from src.api.s3_dependencies import ( bucket_name, s3_client )
from datetime import datetime, timedelta
from dateutil.parser import parse as datetime_parse

class ShowService:
    def __init__(self, db: Session):
        self.db = db

    def build_response(self, inbound_delivery_id: int):
        db = self.db

        inbound_delivery = (
            db.query(InboundDelivery)
            .options(
                joinedload(InboundDelivery.inbound_delivery_lines),
                joinedload(InboundDelivery.inbound_delivery_attachments)
            )
            .filter(InboundDelivery.id == inbound_delivery_id)
            .first()
        )

        if inbound_delivery is None:
            raise HTTPException(status_code=404, detail="Delivery not found")

        if inbound_delivery.inbound_delivery_date is not None:
            inbound_delivery.inbound_delivery_date = inbound_delivery.inbound_delivery_date.strftime("%Y-%m-%d %H:%M:%S")

        for attachment in inbound_delivery.inbound_delivery_attachments:
            attachment.file_link = self.create_presigned_url(attachment.file_s3_key)
            attachment.created_at = datetime_parse(attachment.created_at) + timedelta(hours=7)

        if inbound_delivery.inbound_delivery_date is not None:
            inbound_delivery.inbound_delivery_date = datetime.strptime(inbound_delivery.inbound_delivery_date, ("%Y-%m-%d %H:%M:%S"))
        inbound_delivery.status = InboundDeliveryStatusEnum(inbound_delivery.status).name
        inbound_delivery.created_at = datetime_parse(inbound_delivery.created_at) + timedelta(hours=7)

        return inbound_delivery
    
    def create_presigned_url(self, file_s3_key: str):
        return s3_client().generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name(), 'Key': file_s3_key },
            ExpiresIn=3600
        )