from src.models import ( PurchaseInvoice, InboundDelivery, PurchaseInvoiceLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( PurchaseInvoiceStatusEnum, PurchaseInvoiceAsParams )
from src.purchase_invoices.service import ( Service )
from decimal import Decimal

class BuildService:
    def __init__(self, db: Session):
        self.db = db

    def build(self, params: PurchaseInvoiceAsParams):
        purchase_invoice = PurchaseInvoice(
            invoice_date=params.invoice_date,
            expected_delivery_date=params.expected_delivery_date,
            notes=params.notes,
            supplier_name=params.supplier_name,
            status=PurchaseInvoiceStatusEnum.PENDING
        )

        purchase_invoice.purchase_invoice_lines = self.build_lines(params)
        service = Service(self.db)
        service.generate_invoice_no(purchase_invoice)
        service.calculate_sum_total_line_amounts(purchase_invoice)

        return purchase_invoice
    
    def build_lines(self, params: PurchaseInvoiceAsParams):
        invoice_lines = []
        for param_line in params.purchase_invoice_lines_attributes:
            quantity = Decimal(param_line.quantity)
            price = Decimal(param_line.price_per_unit)

            invoice_line = PurchaseInvoiceLine(
                component_id=param_line.component_id,
                component_name=param_line.component_name,
                component_category_id=param_line.component_category_id,
                component_category_name=param_line.component_category_name,
                quantity=quantity,
                price_per_unit=price,
                total_line_amount=quantity * price
            )

            invoice_lines.append(invoice_line)

        return invoice_lines

    
