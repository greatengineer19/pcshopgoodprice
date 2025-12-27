from src.database import Base
from sqlalchemy import ( DateTime, Column, Integer, Numeric, Boolean, String, func, ForeignKey )
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False
    )
    debit_account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False
    )
    currency: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[account_id],
        back_populates="payments"
    )

    debit_account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[debit_account_id],
        back_populates="payments"
    )