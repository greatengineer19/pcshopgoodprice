from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from ..value_objects.payment_amount import PaymentAmount
from ..value_objects.payment_method import PaymentMethod
from ..entities.payment_object_index import PaymentObjectIndex
from typing import List

@dataclass
class PaymentIndex:
    item_per_page: int
    page: str
    report_body: List[PaymentObjectIndex]