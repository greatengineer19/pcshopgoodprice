from src.report.row_builder import RowBuilder
from src.schemas import PurchaseInvoiceStatusEnum

class ResponseGeneratorService:
    def call(self, purchase_invoices, component_name, component_category_id):
        result = []

        for invoice in purchase_invoices:
            for invoice_line in invoice.purchase_invoice_lines:
                if component_name and (component_name.casefold() not in invoice_line.component_name.casefold()):
                    continue
                elif component_category_id and (int(component_category_id) != invoice_line.component_category_id):
                    continue
                result.append(self.build_row(invoice=invoice, invoice_line=invoice_line))

        return result
    
    def build_row(self, *, invoice, invoice_line):
        unique_delivery_dates = {}
        unique_delivery_nos = {}
        for ib_line in invoice_line.inbound_delivery_lines:
            inbound_delivery = ib_line.inbound_delivery
            unique_delivery_dates[inbound_delivery.inbound_delivery_date] = inbound_delivery.inbound_delivery_date
            unique_delivery_nos[inbound_delivery.inbound_delivery_no] = inbound_delivery.inbound_delivery_no
        delivery_nos = unique_delivery_nos.values()
        delivery_dates = unique_delivery_dates.values()

        total_received_qty = sum(ib_line.received_quantity for ib_line in invoice_line.inbound_delivery_lines)
        total_damaged_qty = sum(ib_line.damaged_quantity for ib_line in invoice_line.inbound_delivery_lines)
        total_amount_received = total_received_qty * invoice_line.price_per_unit
        inbound_delivery_dates = ", ".join({ delivery_date.strftime('%d %B %Y') for delivery_date in delivery_dates})
        inbound_delivery_nos = ", ".join({ delivery_no for delivery_no in delivery_nos})

        row_builder = RowBuilder()
        built_row = (
            row_builder
                .append_text(invoice.purchase_invoice_no)
                .append_text(invoice.invoice_date.strftime("%d %B %Y"))
                .append_text(invoice.supplier_name)
                .append_text(PurchaseInvoiceStatusEnum(invoice.status).name)
                .append_text(invoice_line.component_name)
                .append_text(invoice_line.component_category_name)
                .append_quantity(str(invoice_line.quantity))
                .append_money(str(invoice_line.price_per_unit))
                .append_money(str(invoice_line.total_line_amount))
                .append_quantity(str(total_received_qty))
                .append_quantity(str(total_damaged_qty))
                .append_money(str(total_amount_received))
                .append_text(inbound_delivery_dates)
                .append_text(inbound_delivery_nos)
                .build()
        )

        return built_row