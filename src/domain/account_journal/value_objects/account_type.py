from enum import IntEnum
from typing import Union

class AccountTypeEnum(IntEnum):
    ASSET = 0
    LIABILITY = 1
    EQUITY = 2
    REVENUE = 3
    EXPENSE = 4

    @classmethod
    def from_value(cls, value: Union[str, int, 'AccountTypeEnum']) -> 'AccountTypeEnum':
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            value_upper = value.upper()
            try:
                return cls[value_upper]
            except KeyError:
                if value_upper in ["0", "ASSET"]:
                    return cls.ASSET
                elif value_upper in ["1", "LIABILITY"]:
                    return cls.LIABILITY
                elif value_upper in ["2", "EQUITY"]:
                    return cls.EQUITY
                elif value_upper in ["3", "REVENUE"]:
                    return cls.REVENUE
                elif value_upper in ["4", "EXPENSE"]:
                    return cls.EXPENSE
            
            if isinstance(value, int):
                return cls(value)

            raise ValueError(
                f"Invalid account type: {value}"
                f"must be one of: {[e.name for e in cls]} or values {[e.value for e in cls]}"
            )