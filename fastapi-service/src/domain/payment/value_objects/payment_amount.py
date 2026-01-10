from decimal import Decimal
from dataclasses import dataclass
from .currency import CurrencyEnum

@dataclass(frozen=True)
class PaymentAmount:
    """Money value object with currency"""
    amount: Decimal
    currency: CurrencyEnum

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Payment amount cannot be negative")
        
    def __str__(self):
        return f"{self.amount} {self.currency.name}"