from src.report.row_builder import RowBuilder
from decimal import ROUND_HALF_UP, Decimal

class ResponseGeneratorService:
    def call(self, inventories, component_name, component_category_id):
        result = []
        current_component_id = None
        total_per_component = 0

        for inventory in inventories:
            if component_name and (component_name.casefold() not in inventory.component.name.casefold()):
                continue
            elif component_category_id and (int(component_category_id) != inventory.component.component_category_id):
                continue
            if current_component_id != inventory.component_id:
                total_per_component = 0
                current_component_id = inventory.component_id
            result.append(self.build_row(inventory=inventory, total_per_component=total_per_component))

        return result
    
    def build_row(self, *, inventory, total_per_component):
        in_stock = Decimal(inventory.in_stock or 0).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        out_stock = Decimal(inventory.out_stock or 0).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        total_per_component = total_per_component + in_stock - out_stock
        final_moving_stock = total_per_component

        buy_price = Decimal(inventory.buy_price or 0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        row_builder = RowBuilder()
        built_row = (
            row_builder
                .append_text(inventory.component.component_category.name)
                .append_text(inventory.component.name)
                .append_text(inventory.stock_date.strftime("%d %B %Y"))
                .append_text(inventory.created_at.strftime("%d %B %Y %H:%M:%S"))
                .append_text(inventory.resource_type)
                .append_text(inventory.transaction_no)
                .append_text(inventory.received_by)
                .append_text('Sean Ali')
                .append_quantity(str(in_stock))
                .append_quantity(str(out_stock))
                .append_quantity(str(final_moving_stock.quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
                .append_money(str(buy_price))
                .build()
        )

        return built_row