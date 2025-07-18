from src.models import ( SalesInvoiceLine, SalesInvoice )
from sqlalchemy.orm import joinedload, Session
from src.schemas import ( SalesInvoiceStatusEnum )
from typing import Optional
from src.computer_components.image_service import ImageService

class ShowService:
    def __init__(self, *, db: Session, sales_quote_no: Optional[str], sales_invoice_id: Optional[int], user_id: int):
        self.db = db
        self.sales_invoice_id = sales_invoice_id or None
        self.user_id = user_id or None
        self.sales_quote_no = sales_quote_no

    def call(self):
        query = self.db.query(SalesInvoice).options(joinedload(SalesInvoice.sales_invoice_lines).subqueryload(SalesInvoiceLine.component))

        if self.sales_quote_no:
            check = query.filter(SalesInvoice.sales_quote_no == self.sales_quote_no).first()
            return check

        if self.sales_invoice_id:
            query = query.filter(SalesInvoice.id == self.sales_invoice_id)
        if self.user_id:
            query = query.filter(SalesInvoice.customer_id == self.user_id)
        query = query.first()
        image_service = ImageService()

        for invoice_line in query.sales_invoice_lines:
            invoice_line.images = image_service.presigned_url_generator(invoice_line.component)

        query.status = SalesInvoiceStatusEnum(query.status).name
        return query
