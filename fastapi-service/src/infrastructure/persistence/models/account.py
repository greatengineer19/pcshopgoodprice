from src.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    account_code: Mapped[int] = mapped_column(Integer, nullable=False)
    account_name: Mapped[str] = mapped_column(String, nullable=False)
    account_type: Mapped[int] = mapped_column(Integer, nullable=False)
    subtype: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    normal_balance: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    tax_code_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    debit_payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        foreign_keys="Payment.debit_account_id",
        back_populates="debit_account"
    )
    
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        foreign_keys="Payment.account_id",
        back_populates="account"
    )