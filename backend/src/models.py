from src.database import Base
from sqlalchemy import (
    text,
    Column,
    Integer,
    String,
    Text,
    DECIMAL,
    ARRAY,
    DateTime,
    Date,
    func,
    ForeignKey,
    Numeric,
    Index,
    Boolean
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, object_session
from typing import List
from decimal import Decimal
from datetime import datetime, date

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, unique=True, index=True, primary_key=True)
    fullname: Mapped[str] = mapped_column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    role = Column(Integer, nullable=False, server_default="0")
    hashed_password = Column(String)
    refresh_token = Column(String, unique=True, nullable=True)
    refresh_token_expiry_at = Column(DateTime, server_default=func.now(), nullable=False)

    cart_lines: Mapped["CartLine"] = relationship(
        back_populates="customer"
    )

    sales_quotes: Mapped["SalesQuote"] = relationship(
        back_populates="customer"
    )

    sales_invoices: Mapped["SalesInvoice"] = relationship(
        back_populates="customer"
    )

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

class ComputerComponentReview(Base):
    __tablename__ = "computer_component_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('computer_components.id'),
        nullable=False
    )
    user_fullname: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, server_default="0")
    comments: Mapped[str] = mapped_column(String, nullable=False)

    component: Mapped['ComputerComponent'] = relationship(
        "ComputerComponent", back_populates="computer_component_reviews"
    )

class ComputerComponentSellPriceSetting(Base):
    __tablename__ = "computer_component_sell_price_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    component_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('computer_components.id'),
        nullable=False
    )
    day_type: Mapped[int] = Column(Integer, nullable=False)
    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    component: Mapped['ComputerComponent'] = relationship(
        "ComputerComponent", back_populates="computer_component_sell_price_settings"
    )

class ComputerComponentCategory(Base):
    __tablename__ = "computer_component_categories"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    status = Column(Integer, nullable=False, server_default="0")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    computer_components: Mapped[List['ComputerComponent']] = relationship(
        "ComputerComponent", back_populates="component_category"
    )

class ComputerComponent(Base):
    __tablename__ = "computer_components"
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    product_code = Column(String, nullable=False, unique=True)
    images = Column(ARRAY(String))
    description = Column(Text) 
    component_category_id = Column(Integer, ForeignKey('computer_component_categories.id'), nullable=False)
    status = Column(Integer, nullable=False, server_default="0")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    component_category: Mapped['ComputerComponentCategory'] = relationship(
        "ComputerComponentCategory", back_populates="computer_components"
    )

    computer_component_sell_price_settings: Mapped[List['ComputerComponentSellPriceSetting']] = relationship(
        "ComputerComponentSellPriceSetting", back_populates="component",
        cascade="all, delete-orphan"
    )

    computer_component_reviews: Mapped[List['ComputerComponentReview']] = relationship(
        "ComputerComponentReview", back_populates="component",
        cascade="all, delete-orphan"
    )

    inventories: Mapped["Inventory"] = relationship(back_populates="component")
    cart_lines: Mapped["CartLine"] = relationship(back_populates="component")
    purchase_invoice_lines: Mapped["PurchaseInvoiceLine"] = relationship(back_populates="component")
    sales_quote_lines: Mapped["SalesQuoteLine"] = relationship(back_populates="component")
    sales_delivery_lines: Mapped["SalesDeliveryLine"] = relationship(back_populates="component")
    sales_invoice_lines: Mapped["SalesInvoiceLine"] = relationship(back_populates="component")
    inbound_delivery_lines: Mapped["InboundDeliveryLine"] = relationship(back_populates="component")

class PurchaseInvoice(Base):
    __tablename__ = "purchase_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_invoice_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    invoice_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expected_delivery_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    supplier_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    sum_total_line_amounts: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    purchase_invoice_lines: Mapped[List["PurchaseInvoiceLine"]] = relationship(
        back_populates="purchase_invoice",
        cascade="all, delete-orphan"
    )

    inbound_deliveries: Mapped[List["InboundDelivery"]] = relationship(
        back_populates="purchase_invoice",
        cascade="all, delete-orphan"
    )

class PurchaseInvoiceLine(Base):
    __tablename__ = "purchase_invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_invoice_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_invoices.id"),
        nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        ForeignKey("computer_components.id"),
        nullable=False
    )
    component_name: Mapped[str] = mapped_column(String, nullable=False)
    component_category_id: Mapped[int] = mapped_column(
        ForeignKey("computer_component_categories.id"),
        nullable=False
    )
    component_category_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    total_line_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    purchase_invoice: Mapped["PurchaseInvoice"] = relationship(
        back_populates="purchase_invoice_lines"
    )

    inbound_delivery_lines: Mapped[List["InboundDeliveryLine"]] = relationship(
        back_populates="purchase_invoice_line"
    )

    component: Mapped["ComputerComponent"] = relationship(
        back_populates="purchase_invoice_lines"
    )

class InboundDelivery(Base):
    __tablename__ = "inbound_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_invoice_id: Mapped[int] = mapped_column(
        ForeignKey('purchase_invoices.id'),
        nullable=False
    )
    purchase_invoice_no: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    inbound_delivery_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    inbound_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    inbound_delivery_reference: Mapped[str] = mapped_column(String, nullable=False)
    received_by: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    inbound_delivery_lines: Mapped[List["InboundDeliveryLine"]] = relationship(
        back_populates="inbound_delivery",
        cascade="all, delete-orphan"
    )

    inbound_delivery_attachments: Mapped[List["InboundDeliveryAttachment"]] = relationship(
        back_populates="inbound_delivery",
        cascade="all, delete-orphan"
    )

    purchase_invoice: Mapped["PurchaseInvoice"] = relationship(
        back_populates="inbound_deliveries"
    )

class InboundDeliveryLine(Base):
    __tablename__ = "inbound_delivery_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inbound_delivery_id: Mapped[int] = mapped_column(
        ForeignKey("inbound_deliveries.id"),
        nullable=False
    )
    purchase_invoice_line_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_invoice_lines.id"),
        nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        ForeignKey("computer_components.id"),
        nullable=False
    )
    component_name: Mapped[str] = mapped_column(String, nullable=False)
    component_category_id: Mapped[int] = mapped_column(
        ForeignKey("computer_component_categories.id"),
        nullable=False
    )
    component_category_name: Mapped[str] = mapped_column(String, nullable=False)
    expected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    received_quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    damaged_quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    total_line_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    inbound_delivery: Mapped["InboundDelivery"] = relationship(
        back_populates="inbound_delivery_lines"
    )

    purchase_invoice_line: Mapped[List["PurchaseInvoiceLine"]] = relationship(
        back_populates="inbound_delivery_lines"
    )

    component: Mapped["ComputerComponent"] = relationship(
        back_populates="inbound_delivery_lines"
    )

class InboundDeliveryAttachment(Base):
    __tablename__ = "inbound_delivery_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inbound_delivery_id: Mapped[int] = mapped_column(
        ForeignKey("inbound_deliveries.id"),
        nullable=False
    )
    file_s3_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    uploaded_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    @property
    def file_link(self) -> str:
        return getattr(self, "_file_link", None)

    @file_link.setter
    def file_link(self, value: str) -> None:
        self._file_link = value

    inbound_delivery: Mapped["InboundDelivery"] = relationship(
        back_populates="inbound_delivery_attachments"
    )

class Inventory(Base):
    __tablename__ = "inventories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    in_stock: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    out_stock: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    stock_date: Mapped[date] = mapped_column(Date, nullable=False)
    component_id: Mapped[int] = mapped_column(
        ForeignKey("computer_components.id"),
        nullable=False
    )
    resource_type = mapped_column(String, nullable=False)  # 'InboundDelivery' or 'OutboundDelivery'
    resource_id = mapped_column(Integer, nullable=False)
    resource_line_type = mapped_column(String, nullable=False)  # 'InboundDeliveryLine' or 'OutboundDeliveryLine'
    resource_line_id = mapped_column(Integer, nullable=False)
    buy_price: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    component: Mapped["ComputerComponent"] = relationship(
        back_populates="inventories"
    )

    __table_args__ = (
        Index('ix_resource_type_id', 'resource_type', 'resource_id'),
    )

    @property
    def resource(self):
        if self.resource_type == 'InboundDelivery':
            return object_session(self).get(InboundDelivery, self.resource_id)
        return None
    
    @property
    def resource_line(self):
        if self.resource_line_type == 'InboundDeliveryLine':
            return object_session(self).get(InboundDeliveryLine, self.resource_line_id)
        return None

class CartLine(Base):
    __tablename__ = "cart_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("computer_components.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    component: Mapped["ComputerComponent"] = relationship(
        back_populates="cart_lines"
    )

    customer: Mapped["User"] = relationship(
        back_populates="cart_lines"
    )

class SalesQuote(Base):
    __tablename__ = "sales_quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    sales_quote_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    sum_total_line_amounts: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    total_payable_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    shipping_address: Mapped[str] = mapped_column(String, nullable=False)
    payment_method_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('payment_methods.id'), nullable=False
    )
    payment_method_name: Mapped[str] = mapped_column(String, nullable=False)
    virtual_account_no: Mapped[str] = mapped_column(String, nullable=True)
    paylater_account_reference: Mapped[str] = mapped_column(String, nullable=True)
    credit_card_customer_name: Mapped[str] = mapped_column(String, nullable=True)
    credit_card_customer_address: Mapped[str] = mapped_column(String, nullable=True)
    credit_card_bank_name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    customer: Mapped["User"] = relationship(
        back_populates="sales_quotes"
    )

    payment_method: Mapped["PaymentMethod"] = relationship()

    sales_quote_lines: Mapped[List["SalesQuoteLine"]] = relationship(
        back_populates="sales_quote",
        cascade="all, delete-orphan"
    )

class SalesQuoteLine(Base):
    __tablename__ = "sales_quote_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sales_quote_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_quotes.id"), nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("computer_components.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    total_line_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    component: Mapped["ComputerComponent"] = relationship()
    sales_quote: Mapped["SalesQuote"] = relationship(
        back_populates="sales_quote_lines"
    )

class SalesInvoice(Base):
    __tablename__ = "sales_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id'), nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    sales_invoice_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    sales_quote_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    sum_total_line_amounts: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    total_payable_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    shipping_address: Mapped[str] = mapped_column(String, nullable=False)
    payment_method_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('payment_methods.id'), nullable=False
    )
    payment_method_name: Mapped[str] = mapped_column(String, nullable=False)
    virtual_account_no: Mapped[str] = mapped_column(String, nullable=True)
    paylater_account_reference: Mapped[str] = mapped_column(String, nullable=True)
    credit_card_customer_name: Mapped[str] = mapped_column(String, nullable=True)
    credit_card_customer_address: Mapped[str] = mapped_column(String, nullable=True)
    credit_card_bank_name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    customer: Mapped["User"] = relationship(
        back_populates="sales_invoices"
    )

    payment_method: Mapped["PaymentMethod"] = relationship()

    sales_invoice_lines: Mapped[List["SalesInvoiceLine"]] = relationship(
        back_populates="sales_invoice",
        cascade="all, delete-orphan"
    )

class SalesInvoiceLine(Base):
    __tablename__ = "sales_invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sales_invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_invoices.id"), nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("computer_components.id"), nullable=False
    )
    component_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    total_line_amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    component: Mapped["ComputerComponent"] = relationship()
    sales_invoice: Mapped["SalesInvoice"] = relationship(
        back_populates="sales_invoice_lines"
    )

class SalesDelivery(Base):
    __tablename__ = "sales_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    sales_invoice_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('sales_invoices.id'), nullable=False
    )
    sales_delivery_no: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    sales_delivery_lines: Mapped[List["SalesDeliveryLine"]] = relationship(
        back_populates="sales_delivery",
        cascade="all, delete-orphan"
    )

class SalesDeliveryLine(Base):
    __tablename__ = "sales_delivery_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sales_delivery_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales_deliveries.id"), nullable=False
    )
    component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("computer_components.id"), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6), nullable=False, default=Decimal("0.0")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    component: Mapped["ComputerComponent"] = relationship()
    sales_delivery: Mapped["SalesDelivery"] = relationship(
        back_populates="sales_delivery_lines"
    )
