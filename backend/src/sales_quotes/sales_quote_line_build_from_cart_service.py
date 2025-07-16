from src.models import ( CartLine, ComputerComponent, SalesQuoteLine, User )
from sqlalchemy.orm import joinedload, Session
from sqlalchemy import ( and_ )
from src.computer_components.service import Service

class SalesQuoteLineBuildFromCartService:
    def __init__(self, db: Session, user: User, sales_quote):
        self.db = db
        self.sales_quote = sales_quote
        self.user = user

    def build(self):
        cart_lines = (
            self.db
            .query(CartLine)
            .filter(and_(CartLine.customer_id == self.user.id))
            .order_by(CartLine.id)
            .all()
        )

        components = (
            self.db.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
            .filter(ComputerComponent.id.in_([p.component_id for p in cart_lines]))
        )

        components_dict = { component.id: component for component in components}

        for cart_line in cart_lines:
            component = components_dict[cart_line.component_id]
            price_service = Service()
            price = price_service.select_price(component)

            quote_line = SalesQuoteLine(
                component_id=cart_line.component_id,
                quantity=cart_line.quantity,
                price_per_unit=price,
                total_line_amount= price * cart_line.quantity
            )
            self.sales_quote.sales_quote_lines.append(quote_line)

        delete_query = CartLine.__table__.delete().where(CartLine.id.in_([cart_line.id for cart_line in cart_lines]))

        return self.sales_quote, delete_query
