from pydantic import BaseModel, Field, field_validator, condecimal
from typing import Optional, Union

class PaymentRequestSchema(BaseModel):
    """Request schema for creating payment"""
    user_id: int = Field(..., gt=0, description="User ID must be positive")
    account_id: int = Field(..., gt=0, description="Account ID must be positive")
    amount: condecimal(ge=0, decimal_places=6, max_digits=20) = Field(
        ...,
        description="Amount with 6 decimal places, max 20 digits before decimal"
    )
    currency: str = Field(default="EUR", description="Currency (IDR, EUR, or 0, 1)")
    payment_method: str = Field(
        ...,
        description="Payment method (CASH, BCA_TRANSFER, BNI_TRANSFER or 0, 1, 2)"
    )
    description: Optional[str] = Field(None, max_length=255, description="Optional description")
    status_code: Optional[str] = Field(None, description="Optional status code")

    @field_validator('currency', mode='before')
    def validate_currency(cls, v):
        from src.domain.payment.value_objects.currency import CurrencyEnum
        if v is None:
            return "EUR"
        
        CurrencyEnum.from_value(v)
        return v
    
    @field_validator("payment_method", mode='before')
    def validate_payment_method(cls, v):
        from src.domain.payment.value_objects.payment_method import PaymentMethod
        if v is None:
            raise ValueError("payment_method is required")
        
        PaymentMethod.from_value(v)
        return v
    
    class Config:
        use_enum_values = True

class PaymentResponseSchema(BaseModel):
    payment_id: Union[str,int]
    currency: str
    payment_method: str
    message: str