from src.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class ImportPaymentEntry(Base):
    __tablename__ = "import_payment_entries"

    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    request_uuid: Mapped[str] = mapped_column(String, nullable=False)
    total_payments: Mapped[int] = mapped_column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)