import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from tests.factories.user_factory import UserFactory
from tests.factories.component_factory import ComponentFactory
from tests.factories.cart_line_factory import CartLineFactory
from tests.factories.component_category_factory import ComponentCategoryFactory
from tests.factories.sales_quote_factory import SalesQuoteFactory
from tests.factories.sales_quote_line_factory import SalesQuoteLineFactory
from tests.factories.payment_method_factory import PaymentMethodFactory
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import ( client, db_session, setup_factories )
from utils.auth import create_access_token, create_refresh_token, decodeJWT, get_current_user
from src.models import (
    CartLine,
    ComputerComponentSellPriceSetting,
    SalesQuote,
    SalesQuoteLine,
    SalesInvoice,
    SalesInvoiceLine
)

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali")

@pytest.fixture
def component_category_gpu():
    return ComponentCategoryFactory(
        name="GPU",
        status=0
    )

@pytest.fixture
def component_gpu_4060(component_category_gpu, db_session):
    component_gpu = ComponentFactory(
        name="Zotac RTX 4060",
        product_code="rtx_4060",
        price=7000000,
        component_category_id=component_category_gpu.id,
        status=0
    )

    component_gpu.computer_component_sell_price_settings.append(
        ComputerComponentSellPriceSetting(
            day_type=0,
            price_per_unit=10000000,
            active=True
        )
    )

    db_session.commit()

    return component_gpu

@pytest.fixture
def component_gpu_4070(component_category_gpu, db_session):
    component_gpu = ComponentFactory(
        name="Zotac RTX 4070",
        product_code="rtx_4070",
        price=7000000,
        component_category_id=component_category_gpu.id,
        status=0
    )

    component_gpu.computer_component_sell_price_settings.append(
        ComputerComponentSellPriceSetting(
            day_type=0,
            price_per_unit=12000000,
            active=True
        )
    )

    db_session.commit()
    return component_gpu

@pytest.fixture
def cart_line_gpu_4060_sean_ali(user_sean_ali, component_gpu_4060):
    return CartLineFactory(
        customer_id=user_sean_ali.id,
        component_id=component_gpu_4060.id,
        quantity=1
    )

@pytest.fixture
def cart_line_gpu_4070_sean_ali(user_sean_ali, component_gpu_4070):
    return CartLineFactory(
        customer_id=user_sean_ali.id,
        component_id=component_gpu_4070.id,
        quantity=1
    )

@pytest.fixture
def payment_method_virtual_account():
    return PaymentMethodFactory(
        name="BBB Virtual Account"
    )

@pytest.fixture
def sales_quote(user_sean_ali,
                payment_method_virtual_account,
                cart_line_gpu_4070_sean_ali,
                cart_line_gpu_4060_sean_ali):
    sales_quote = SalesQuoteFactory(
        customer_id=user_sean_ali.id,
        customer_name=user_sean_ali.fullname,
        shipping_address='Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        payment_method_id=payment_method_virtual_account.id,
        payment_method_name=payment_method_virtual_account.name,
    )

    SalesQuoteLineFactory(
        sales_quote_id=sales_quote.id,
        component_id=cart_line_gpu_4070_sean_ali.component_id,
        quantity=cart_line_gpu_4070_sean_ali.quantity,
        price_per_unit=12000000,
        total_line_amount=12000000 * cart_line_gpu_4070_sean_ali.quantity
    )

    SalesQuoteLineFactory(
        sales_quote_id=sales_quote.id,
        component_id=cart_line_gpu_4060_sean_ali.component_id,
        quantity=cart_line_gpu_4060_sean_ali.quantity,
        price_per_unit=10000000,
        total_line_amount=10000000 * cart_line_gpu_4060_sean_ali.quantity
    )

    return sales_quote

def test_valid_pay(client, db_session, user_sean_ali, sales_quote):
    db_session.commit()

    param = { 'id': sales_quote.id }
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post("/api/sales-payment/virtual-account", headers=headers, json=param)
    assert response.status_code == 201

    response_body = response.json()
    assert response_body == 'sales invoice created'

    exist = db_session.query(SalesQuote).filter(SalesQuote.id == sales_quote.id).first()
    assert exist is None

    exist = db_session.query(SalesQuoteLine).filter(SalesQuoteLine.sales_quote_id == sales_quote.id).first()
    assert exist is None

    exist = db_session.query(SalesInvoice).filter(SalesInvoice.sales_quote_no == sales_quote.sales_quote_no).first()
    assert exist
