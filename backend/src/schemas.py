from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import (Dict, List, Optional, Union)
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from enum import Enum, IntEnum
from dateutil import parser

class UploadResponseSchema(BaseModel):
    status_code: int
    s3_key: str

class ListUploadResponseSchema(BaseModel):
    image_list: List[UploadResponseSchema]

class ComputerComponentCategorySchema(BaseModel):
    id: Optional[int] = None
    name: str
    status: int
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        from_attributes = True

class ComputerComponentBase(BaseModel):
    name: str
    product_code: str
    component_category_name: Optional[str] = None
    description: Optional[str] = None
    status: int

class ComputerComponentSellPriceSettingAsResponse(BaseModel):
    id: int
    component_id: int
    day_type: str
    price_per_unit: Decimal
    active: bool

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    def convert_day_type(cls, values):
        day_value = values.day_type
        if isinstance(day_value, int):
            try:
                values.day_type = DayTypeEnum(day_value).name
            except ValueError:
                values.day_type = f"UNKNOWN({day_value})"
        return values

class ComputerComponentAsResponse(ComputerComponentBase):
    id: int
    component_category_id: int
    computer_component_sell_price_settings: List[ComputerComponentSellPriceSettingAsResponse]
    images: Optional[List[str]] = None
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]

    class Config:
        from_attributes = True

class ComputerComponentCategoryAsResponse(BaseModel):
    id: int
    name: str

class ComputerComponentCategoryAsListResponse(BaseModel):
    computer_component_categories: List[ComputerComponentCategoryAsResponse]

class ComputerComponentAsListResponse(BaseModel):
    computer_components: List[ComputerComponentAsResponse]

class SellableProductResponse(ComputerComponentAsResponse):
    rating: float
    count_review_given: int
    sell_price: float

class ComputerComponentReview(BaseModel):
    id: int
    user_id: int
    component_id: int
    user_fullname: str
    rating: int
    comments: str
    created_at: Union[str, datetime]
    updated_at: Union[str, datetime]

class OneSellableProductResponse(SellableProductResponse):
    computer_component_reviews: List[ComputerComponentReview]

class SellableProductsInCategory(BaseModel):
    name: str
    components: List[SellableProductResponse]

class SellableProductsAsListResponse(BaseModel):
    sellable_products: Dict[int, SellableProductsInCategory]

class DayTypeEnum(IntEnum):
    default = 0
    monday = 1
    tuesday = 2
    wednesday = 3
    thursday = 4
    friday = 5
    saturday = 6
    sunday = 7

class ComputerComponentSellPriceSettingAsParams(BaseModel):
    id: Optional[int] = None
    component_id: Optional[int] = None
    day_type: str
    price_per_unit: Union[str, int]
    active: bool = True

    @field_validator('day_type')
    def validate_day_type(cls, v):
        try:
            return DayTypeEnum[v].value
        except KeyError:
            raise ValueError(f"Invalid day_type: {v}")

class ComputerComponentAsParams(ComputerComponentBase):
    id: Optional[int] = None # None because it is not needed on create
    images: Optional[List[str]] = None
    computer_component_sell_price_settings_attributes: List[ComputerComponentSellPriceSettingAsParams]

    class Config:
        extra = "ignore"

class StatusEnum(int, Enum):
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    CANCELLED = 3

class InboundDeliveryStatusEnum(int, Enum):
    DELIVERED = 0
    CANCELLED = 1

class PurchaseInvoiceLineBase(BaseModel):
    component_id: int
    component_name: str
    component_category_id: int
    component_category_name: str
    quantity: int
    price_per_unit: int

class PurchaseInvoiceLineAsResponse(PurchaseInvoiceLineBase):
    id: int
    total_line_amount: Decimal

class PurchaseInvoiceLineAsParams(PurchaseInvoiceLineBase):
    id: Optional[int] = None
    destroy: Optional[bool] = Field(default=False, alias="_destroy")

    class Config:
        extra = "ignore"
        validate_by_name = True

class PurchaseInvoiceBase(BaseModel):
    supplier_name: str
    expected_delivery_date: Optional[Union[datetime, str]]
    notes: Optional[str]

class DeliverablePurchaseInvoiceLine(BaseModel):
    id: int
    component_id: int
    component_name: str
    component_category_id: int
    component_category_name: str
    deliverable_quantity: int
    price_per_unit: Decimal

class DeliverablePurchaseInvoice(BaseModel):
    id: int
    purchase_invoice_no: str
    invoice_date: Union[datetime, str]
    supplier_name: str
    deliverable_invoice_lines: List[DeliverablePurchaseInvoiceLine]

class DeliverablePurchaseInvoicesList(BaseModel):
    purchase_invoices: List[DeliverablePurchaseInvoice]

class PurchaseInvoiceAsListResponse(PurchaseInvoiceBase):
    id: int
    purchase_invoice_no: str
    invoice_date: Optional[Union[datetime, str]]
    status: str
    sum_total_line_amounts: Decimal
    deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None,
            Decimal: lambda v: str(v)
        }

class PurchaseInvoicesList(BaseModel):
    purchase_invoices: List[PurchaseInvoiceAsListResponse]

class PurchaseInvoiceAsResponse(PurchaseInvoiceBase):
    id: int
    purchase_invoice_no: str
    invoice_date: Optional[Union[datetime, str]]
    status: str
    sum_total_line_amounts: Decimal
    deleted: bool
    purchase_invoice_lines: List[PurchaseInvoiceLineAsResponse]

    class Config:
        use_enum_values = True
    
class PurchaseInvoiceAsParams(PurchaseInvoiceBase):
    id: Optional[int] = None
    invoice_date: str
    purchase_invoice_lines_attributes: List[PurchaseInvoiceLineAsParams]
    destroy: Optional[bool] = Field(default=False, alias="_destroy")
    
    class Config:
        extra = "ignore"
        use_enum_values = True
        validate_by_name = True

class InboundDeliveryBase(BaseModel):
    purchase_invoice_no: str
    inbound_delivery_reference: str
    received_by: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class InboundDeliveryLineBase(BaseModel):
    purchase_invoice_line_id: int
    component_id: int
    component_name: str
    component_category_id: int
    component_category_name: str
    expected_quantity: int
    received_quantity: int
    damaged_quantity: int
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class InboundDeliveryAttachmentBase(BaseModel):
    file_s3_key: str
    uploaded_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class InboundDeliveryAsListResponse(InboundDeliveryBase):
    id: int
    inbound_delivery_no: str
    inbound_delivery_date: Optional[Union[datetime, str]]
    status: str
    deleted: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None,
            Decimal: lambda v: str(v)
        }

class InboundDeliveriesList(BaseModel):
    inbound_deliveries: List[InboundDeliveryAsListResponse]

class InboundDeliveryLineAsResponse(InboundDeliveryLineBase):
    id: int
    inbound_delivery_id: int
    price_per_unit: Decimal
    total_line_amount: Decimal
    deleted: bool

class InboundDeliveryAttachmentAsResponse(InboundDeliveryAttachmentBase):
    id: int
    inbound_delivery_id: int
    file_link: str

class InboundDeliveryAsResponse(InboundDeliveryBase):
    id: int
    inbound_delivery_no: str
    inbound_delivery_date: Optional[Union[datetime, str]]
    status: str
    deleted: bool
    inbound_delivery_lines: List[InboundDeliveryLineAsResponse]
    inbound_delivery_attachments: List[InboundDeliveryAttachmentAsResponse]

    class Config:
        use_enum_values = True

class InboundDeliveryLineAsParams(InboundDeliveryLineBase):
    id: Optional[int] = None
    price_per_unit: str
    destroy: Optional[bool] = Field(default=False, alias="_destroy")

    class Config:
        extra = "ignore"
        validate_by_name = True

class InboundDeliveryAttachmentAsParams(InboundDeliveryAttachmentBase):
    id: Optional[int] = None
    destroy: Optional[bool] = Field(default=False, alias="_destroy")

    class Config:
        extra = "ignore"
        use_enum_values = True
        validate_by_name = True

class InboundDeliveryAsParams(InboundDeliveryBase):
    id: Optional[int] = None
    purchase_invoice_id: int
    inbound_delivery_date: str
    inbound_delivery_reference: str
    received_by: str
    notes: Optional[str] = None
    inbound_delivery_lines_attributes: List[InboundDeliveryLineAsParams]
    inbound_delivery_attachments_attributes: List[InboundDeliveryAttachmentAsParams]
    destroy: Optional[bool] = Field(default=False, alias="_destroy")

    class Config:
        extra = "ignore"
        use_enum_values = True
        validate_by_name = True

class ReportHeader(BaseModel):
    text: str

class BodyCell(BaseModel):
    text: str
    cell_type: str

class ReportPurchaseInvoiceParams(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: Optional[int] = 1
    item_per_page: Optional[int] = 25
    component_name: Optional[str] = None
    component_category_id: Optional[int] = None
    invoice_status: Optional[int] = None
    keyword: Optional[str] = None

class ReportPagingPrevAndNext(BaseModel):
    prev_page_url: Optional[str]
    next_page_url: Optional[str]

class ReportPaging(BaseModel):
    page: int
    total_item: int
    pagination: ReportPagingPrevAndNext

class ReportResponse(BaseModel):
    report_headers: List[ReportHeader]
    report_body: List[List[BodyCell]]
    paging: ReportPaging

class CartLineResponse(BaseModel):
    id: int
    status: int
    customer_id: int
    component_id: int
    customer_name: str
    component_name: str
    images: Optional[List[str]] = None
    quantity: Decimal
    sell_price: Decimal
    created_at: datetime
    updated_at: datetime

class CartLinesResponse(BaseModel):
    cart: List[CartLineResponse]

class AddItemToCartParam(BaseModel):
    id: Optional[int] = None
    component_id: int
    quantity: Union[str, Decimal]

class CartLineAsSalesQuoteCreateParam(AddItemToCartParam):
    pass

class SalesQuoteBase(BaseModel):
    customer_id: int
    customer_name: str
    shipping_address: str
    payment_method_id: int
    payment_method_name: str
    virtual_account_no: Optional[str] = None
    paylater_account_reference: Optional[str] = None
    credit_card_customer_name: Optional[str] = None
    credit_card_customer_address: Optional[str] = None
    credit_card_bank_name: Optional[str] = None

class SalesQuoteCreateParam(SalesQuoteBase):
    id: Optional[int] = None
    cart_lines: List[CartLineAsSalesQuoteCreateParam]

class SalesQuoteLineAsResponse(BaseModel):
    id: int
    sales_quote_id: int
    component_id: int
    quantity: Decimal
    price_per_unit: Decimal
    total_line_amount: Decimal
    created_at: datetime
    updated_at: datetime

class SalesQuoteResponse(SalesQuoteBase):
    id: int
    sales_quote_no: str
    sum_total_line_amounts: Decimal
    total_payable_amount: Decimal
    created_at: datetime
    updated_at: datetime
    sales_quote_lines: List[SalesQuoteLineAsResponse]

class SalesQuoteLineModelForListResponse(BaseModel):
    id: int
    sales_quote_id: int
    component_id: int
    component_name: str
    quantity: Decimal
    price_per_unit: Decimal
    total_line_amount: Decimal
    created_at: datetime
    updated_at: datetime

class SalesQuoteModelForListResponse(SalesQuoteResponse):
    sales_quote_lines: List[SalesQuoteLineModelForListResponse]

class SalesQuoteList(BaseModel):
    sales_quotes: List[SalesQuoteResponse]

class SalesInvoiceLineAsResponse(BaseModel):
    id: int
    sales_invoice_id: int
    component_id: int
    component_name: str
    quantity: Decimal
    price_per_unit: Decimal
    total_line_amount: Decimal
    created_at: datetime
    updated_at: datetime

class SalesInvoiceResponse(SalesQuoteBase):
    id: int
    status: str
    sales_invoice_no: str
    sales_quote_no: str
    sum_total_line_amounts: Decimal
    total_payable_amount: Decimal
    created_at: datetime
    updated_at: datetime
    sales_invoice_lines: List[SalesInvoiceLineAsResponse]

class SalesInvoiceList(BaseModel):
    sales_invoices: List[SalesInvoiceResponse]

class SalesPaymentParam(BaseModel):
    id: int

class SalesDeliveryCreateParam(BaseModel):
    id: int

class SalesInvoiceStatusEnum(int, Enum):
    PENDING = 0
    COMPLETED = 1
    VOID = 2

class SalesDeliveryStatusEnum(int, Enum):
    PROCESSING = 0
    DELIVERED = 1
    VOID = 2

class SalesDeliveryLineAsResponse(BaseModel):
    id: int
    sales_delivery_id: int
    component_id: int
    quantity: Decimal
    created_at: datetime
    updated_at: datetime

class SalesDeliveryResponse(BaseModel):
    id: int
    status: str
    sales_invoice_id: int
    sales_delivery_no: str
    created_at: datetime
    updated_at: datetime
    sales_delivery_lines: List[SalesDeliveryLineAsResponse]

    class Config:
        from_attributes = True
    
    @model_validator(mode='before')
    def convert_status(cls, values):
        status = values.status
        if isinstance(status, int):
            try:
                values.status = SalesDeliveryStatusEnum(status).name
            except ValueError:
                values.status = f"UNKNOWN({status})"
        return values
    
class PaymentMethodReponse(BaseModel):
    id: int
    name: str
    
class PaymentMethodList(BaseModel):
    payment_methods: List[PaymentMethodReponse]

class UserRoleEnum(int, Enum):
    SELLER = 0
    BUYER = 1

class UserRoleParams(str, Enum):
    seller = "seller"
    buyer = "buyer"

class UserResponse(BaseModel):
    id: int
    fullname: str
    role: str

    @model_validator(mode='before')
    def convert_role(cls, values):
        role = values.get('role')
        if isinstance(role, int):
            try:
                values['role'] = UserRoleEnum(role).name.lower()
            except ValueError:
                values['role'] = f"UNKNOWN({role})"
        return values

class UserAPIResponse(BaseModel):
    user: Union[UserResponse, dict]
    access_token: str
    refresh_token: str

class UserParams(BaseModel):
    role: str

    @model_validator(mode='before')
    def convert_role(cls, values):
        role = values.role
        if isinstance(role, str):
            try:
                enum_role = UserRoleEnum[role.upper()]
                values["role"] = enum_role.name
            except KeyError:
                values["role"] = f"UNKNOWN({role})"
        return values