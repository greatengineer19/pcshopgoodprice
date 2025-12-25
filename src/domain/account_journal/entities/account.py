from dataclasses import dataclass
from typing import Optional
from ..value_objects.normal_balance import NormalBalanceEnum
from ..value_objects.account_type import AccountTypeEnum
from datetime import datetime

@dataclass
class EntityAccount:
    id: Optional[int]
    account_code: int
    account_name: str
    account_type: AccountTypeEnum
    # current asset, fixed asset, leave 0 first
    subtype: int
    parent_id: Optional[int]
    # Like debit for Assets, credit for revenues, etc.
    normal_balance: NormalBalanceEnum
    is_active: bool
    tax_code_id: Optional[int]
    created_at: datetime
    updated_at: datetime