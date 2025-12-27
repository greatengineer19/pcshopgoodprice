from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from ..value_objects.payment_amount import PaymentAmount
from ..value_objects.payment_method import PaymentMethod

@dataclass
class PaymentTransaction:
    """Payment transaction domain entity"""
    id: Optional[int]
    user_id: int
    debit_account_id: int
    amount: PaymentAmount
    payment_method: PaymentMethod
    status: str
    transaction_id: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def mark_as_processing(self):
        """Mark payment as processing"""
        self.status = "processing"

    def mark_as_completed(self, transaction_id: str):
        """Mark payment as completed"""
        self.status = "completed"
        self.transaction_id = transaction_id

    def mark_as_failed(self, reason: str):
        """Mark payment as failed"""
        self.status = "failed"
        self.description = reason