from enum import IntEnum
from typing import Union

class NormalBalanceEnum(IntEnum):
    DEBIT = 0
    CREDIT = 1

    @classmethod
    def from_value(cls, value: Union[str, int, 'NormalBalanceEnum']) -> 'NormalBalanceEnum':
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            value_upper = value.upper()
            try:
                return cls[value_upper]
            except KeyError:
                if value_upper in ["0", "DEBIT"]:
                    return cls.DEBIT
                elif value_upper in ["1", "CREDIT"]:
                    return cls.CREDIT
            
            if isinstance(value, int):
                return cls(value)

            raise ValueError(
                f"Invalid normal balance: {value}"
                f"must be one of: {[e.name for e in cls]} or values {[e.value for e in cls]}"
            )