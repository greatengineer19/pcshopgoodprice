from src.models import ( PurchaseInvoice, InboundDelivery, PurchaseInvoiceLine )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( event, desc, text )
import re
from src.schemas import ( StatusEnum, PurchaseInvoiceAsParams, PurchaseInvoiceLineAsParams )
from src.purchase_invoices.service import ( Service )
from decimal import Decimal
from fastapi import HTTPException

class UpdateService:
    def __init__(self, db: Session):
        self.db = db

    def call(self, purchase_invoice_id: int, params: PurchaseInvoiceAsParams):
        db = self.db
        purchase_invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == purchase_invoice_id).first()

        if not purchase_invoice:
            raise HTTPException(status_code=404, detail="Purchase invoice not found")

        # Update the purchase invoice
        for key, value in params.model_dump(exclude_unset=True).items():
            # Exclude fields that are handled separately (like lines_attributes)
            if key not in ["purchase_invoice_lines_attributes"]:
                setattr(purchase_invoice, key, value)

        service = Service(db)
        purchase_invoice.purchase_invoice_lines = self.build_lines(purchase_invoice, params)
        service.calculate_sum_total_line_amounts(purchase_invoice)
        return purchase_invoice
    
    def build_lines(self, purchase_invoice: PurchaseInvoice, params: PurchaseInvoiceAsParams):
        existing_invoice_lines = { line.id: line for line in purchase_invoice.purchase_invoice_lines }

        invoice_lines_to_keep = []
        for line_param in params.purchase_invoice_lines_attributes:
            if line_param.id:
                invoice_line = self.build_existing_line(line_param, existing_invoice_lines)
                if invoice_line is not None:
                    invoice_lines_to_keep.append(invoice_line)
            else:
                invoice_line = self.build_new_line(line_param)
                invoice_lines_to_keep.append(invoice_line)

        return invoice_lines_to_keep

    def build_existing_line(self, line_param: PurchaseInvoiceLineAsParams, existing_invoice_lines: dict):
        invoice_line = existing_invoice_lines.get(line_param.id)

        if not invoice_line:
            print(f"Warning: Line with ID {line_param.id} not found for update.")
            return None

        # Use model_dump to get the actual destroy value
        line_data = line_param.model_dump()

        if line_data.get('destroy', False):
            self.db.delete(invoice_line)
            return None

        quantity = Decimal(line_param.quantity)
        price = Decimal(line_param.price_per_unit)

        invoice_line.component_id = line_param.component_id
        invoice_line.component_name = line_param.component_name
        invoice_line.component_category_id = line_param.component_category_id
        invoice_line.component_category_name = line_param.component_category_name
        invoice_line.quantity = quantity
        invoice_line.price_per_unit = price
        invoice_line.total_line_amount = quantity * price
        return invoice_line
    
    def build_new_line(self, line_param: PurchaseInvoiceLineAsParams):
        quantity = Decimal(line_param.quantity)
        price = Decimal(line_param.price_per_unit)

        invoice_line = PurchaseInvoiceLine(
            component_id=line_param.component_id,
            component_name=line_param.component_name,
            component_category_id=line_param.component_category_id,
            component_category_name=line_param.component_category_name,
            quantity=quantity,
            price_per_unit=price,
            total_line_amount=quantity * price
        )
        return invoice_line    
