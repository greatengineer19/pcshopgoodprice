from src.models import ( ComputerComponent )
from datetime import datetime

class Service:
    def select_price(self, component: ComputerComponent) -> float:
        price_settings = component.computer_component_sell_price_settings
        weekday = datetime.now().isoweekday() or 7  # Returns 1-7 (Mon-Sun)

        default_price = next((price_setting.price_per_unit for price_setting in price_settings if price_setting.day_type == 0), 0)
        price = next(
            (sps.price_per_unit for sps in price_settings 
            if sps.day_type == weekday and sps.active is True),
            default_price
        )

        return price