from enum import IntEnum
from typing import Union

class PaymentMethod(IntEnum):
    """Payment method value object"""

    CASH = 0
    BCA_TRANSFER = 1
    BNI_TRANSFER = 2

    @classmethod
    def from_value(cls, value: Union[str, int, 'PaymentMethod']) -> 'PaymentMethod':
        """Parse payment method from various input types"""
        if isinstance(value, cls):
            return value
        
        if isinstance(value, str):
            value_upper = value.upper()
            try:
                return cls[value_upper]
            except KeyError:
                if value_upper in ["0", "CASH"]:
                    return cls.CASH
                elif value_upper in ["1", "BCA", "BCA_TRANSFER"]:
                    return cls.BCA_TRANSFER
                elif value_upper in ["2", "BNI", "BNI_TRANSFER"]:
                    return cls.BNI_TRANSFER
                
        if isinstance(value, int):
            return cls(value)
        
        raise ValueError(
            f"Invalid payment method: {value}. "
            f"Must be one of: {[e.name for e in cls]} or values {[e.value for e in cls]}"
        )
