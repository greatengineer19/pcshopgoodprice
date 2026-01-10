from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from ..value_objects.payment_amount import PaymentAmount
from ..value_objects.payment_method import PaymentMethod
from decimal import Decimal

@dataclass
class PaymentObjectIndex:
    id: int
    debit_account_id: int
    amount: Decimal
    payment_method: str
    currency: str
    created_at: datetime