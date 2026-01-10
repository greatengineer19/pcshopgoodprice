from enum import IntEnum
from typing import Union

class CurrencyEnum(IntEnum):
    IDR = 0
    EUR = 1
    CAD = 2
    AUD = 3
    USD = 4

    @classmethod
    def from_value(cls, value: Union[str, int, 'CurrencyEnum']) -> 'CurrencyEnum':
        if isinstance(value, cls):
            return value
        
        if isinstance(value, str):
            value_upper = value.upper()
            try:
                return cls[value_upper]
            except KeyError:
                if value_upper in ["0", "IDR"]:
                    return cls.IDR
                elif value_upper in ["1", "EUR"]:
                    return cls.EUR
                elif value_upper in ["2", "CAD"]:
                    return cls.CAD
                elif value_upper in ["3", "AUD"]:
                    return cls.AUD
                elif value_upper in ["4", "USD"]:
                    return cls.USD
        
        if isinstance(value, int):
            return cls(value)
        
        raise ValueError(
            f"Invalid currency: {value}"
            f"Must be one of: {[e.name for e in cls]} or values {[e.value for e in cls]}"
        )

def parse_currency(value: Union[str, int, CurrencyEnum]) -> CurrencyEnum:
    if isinstance(value, CurrencyEnum):
        return value
    
    if isinstance(value, str):
        value_upper = value.upper()
        try:
            return CurrencyEnum[value_upper]
        except KeyError:
            if value_upper == "0" or value_upper == "USD":
                return CurrencyEnum.USD
            elif value_upper == "1" or value_upper == "EUR":
                return CurrencyEnum.EUR
