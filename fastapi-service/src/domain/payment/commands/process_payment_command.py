from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class ProcessPaymentCommand:
    """Command to process a payment"""
    user_id: int
    debit_account_id: int
    amount: Decimal
    currency: str
    payment_method: str
    description: Optional[str] = None
    