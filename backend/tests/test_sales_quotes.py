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
from tests.conftest import (
    client, db_session, setup_factories,
    user_sean_ali,
    component_category_gpu
    )
from utils.auth import create_access_token, create_refresh_token, decodeJWT, get_current_user
from src.models import (
    CartLine,
    ComputerComponentSellPriceSetting,
    SalesQuote
)

@pytest.fixture
def component_gpu_4060(component_category_gpu, db_session):
    component_gpu = ComponentFactory(
        name="Zotac RTX 4060",
        product_code="rtx_4060",
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
def sales_quote(user_sean_ali,
                payment_method_bank_transfer,
                cart_line_gpu_4070_sean_ali,
                cart_line_gpu_4060_sean_ali):
    sales_quote = SalesQuoteFactory(
        customer_id=user_sean_ali.id,
        customer_name=user_sean_ali.fullname,
        shipping_address='Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        payment_method_id=payment_method_bank_transfer.id,
        payment_method_name=payment_method_bank_transfer.name,
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

def test_create_existing_sales_quote(client, db_session, user_sean_ali, sales_quote):
    db_session.commit()

    qline1 = sales_quote.sales_quote_lines[0]
    qline2 = sales_quote.sales_quote_lines[1]
    param = {
        'id': None,
        'customer_id': user_sean_ali.id,
        'customer_name': sales_quote.customer_name,
        'shipping_address': sales_quote.shipping_address,
        'payment_method_id': sales_quote.payment_method_id,
        'payment_method_name': sales_quote.payment_method_name,
        'cart_lines': [
            {
                'id': None,
                'component_id': qline1.component_id,
                'quantity': str(qline1.quantity)
            },
            {
                'id': None,
                'component_id': qline2.component_id,
                'quantity': str(qline2.quantity)
            }
        ]
    }
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sales_quote
    response = client.post("/api/sales-quotes", headers=headers, json=param)
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['id'] == sales_quote.id

def test_show(client, user_sean_ali, db_session, sales_quote):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sales_quote_id = sales_quote.id
    response = client.get(f"/api/sales-quotes/{sales_quote_id}", headers=headers)
    assert response.status_code == 200

    response_body = response.json()
    sales_quote = db_session.query(SalesQuote).filter(SalesQuote.id == sales_quote_id).first()
    qline1 = sales_quote.sales_quote_lines[0]
    qline2 = sales_quote.sales_quote_lines[1]

    assert response_body == {
        'created_at': sales_quote.created_at.isoformat(),
        'credit_card_bank_name': None,
        'credit_card_customer_address': None,
        'credit_card_customer_name': None,
        'customer_id': user_sean_ali.id,
        'customer_name': 'Sean Ali',
        'id': sales_quote.id,
        'paylater_account_reference': None,
        'payment_method_id': sales_quote.payment_method_id,
        'payment_method_name': 'BBB Bank Transfer',
        'sales_quote_lines': [{'component_id': qline1.component_id,
                                'created_at': qline1.created_at.isoformat(),
                                'id': qline1.id,
                                'price_per_unit': '12000000.000000',
                                'quantity': '1.000000',
                                'sales_quote_id': sales_quote.id,
                                'total_line_amount': '12000000.000000',
                                'updated_at': qline1.updated_at.isoformat()},
                            {'component_id': qline2.component_id,
                                'created_at': qline2.created_at.isoformat(),
                                'id': qline2.id,
                                'price_per_unit': '10000000.000000',
                                'quantity': '1.000000',
                                'sales_quote_id': sales_quote.id,
                                'total_line_amount': '10000000.000000',
                                'updated_at': qline2.updated_at.isoformat()}],
        'sales_quote_no': sales_quote.sales_quote_no,
        'shipping_address': 'Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        'sum_total_line_amounts': '0.000000',
        'total_payable_amount': '0.000000',
        'updated_at': sales_quote.updated_at.isoformat(),
        'virtual_account_no': None
    }

def test_create_new_sales_quote(client,
                                db_session,
                                user_sean_ali,
                                payment_method_bank_transfer,
                                cart_line_gpu_4060_sean_ali,
                                cart_line_gpu_4070_sean_ali):
    db_session.commit()

    param = {
        'id': None,
        'customer_id': user_sean_ali.id,
        'customer_name': user_sean_ali.fullname,
        'shipping_address': 'Batam, 29461, Indonesia, 081890989098',
        'payment_method_id': payment_method_bank_transfer.id,
        'payment_method_name': payment_method_bank_transfer.name,
        'cart_lines': [
            {
                'id': None,
                'component_id': cart_line_gpu_4060_sean_ali.component_id,
                'quantity': str(cart_line_gpu_4060_sean_ali.quantity)
            },
            {
                'id': None,
                'component_id': cart_line_gpu_4070_sean_ali.component_id,
                'quantity': str(cart_line_gpu_4070_sean_ali.quantity)
            }
        ]
    }
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.post("/api/sales-quotes", headers=headers, json=param)
    assert response.status_code == 200

    response_body = response.json()
    sales_quote = db_session.query(SalesQuote).order_by(desc(SalesQuote.id)).first()
    qline1 = sales_quote.sales_quote_lines[0]
    qline2 = sales_quote.sales_quote_lines[1]
    assert response_body == {
        'created_at': sales_quote.created_at.isoformat(),
        'credit_card_bank_name': None,
        'credit_card_customer_address': None,
        'credit_card_customer_name': None,
        'customer_id': user_sean_ali.id,
        'customer_name': 'Sean Ali',
        'id': sales_quote.id,
        'paylater_account_reference': None,
        'payment_method_id': sales_quote.payment_method_id,
        'payment_method_name': 'BBB Bank Transfer',
        'sales_quote_lines': [{'component_id': qline1.component_id,
                                'created_at': qline1.created_at.isoformat(),
                                'id': qline1.id,
                                'price_per_unit': '10000000.000000',
                                'quantity': '1.000000',
                                'sales_quote_id': sales_quote.id,
                                'total_line_amount': '10000000.000000',
                                'updated_at': qline1.updated_at.isoformat()},
                            {'component_id': qline2.component_id,
                                'created_at': qline2.created_at.isoformat(),
                                'id': qline2.id,
                                'price_per_unit': '12000000.000000',
                                'quantity': '1.000000',
                                'sales_quote_id': sales_quote.id,
                                'total_line_amount': '12000000.000000',
                                'updated_at': qline2.updated_at.isoformat()}],
        'sales_quote_no': sales_quote.sales_quote_no,
        'shipping_address': 'Batam, 29461, Indonesia, 081890989098',
        'sum_total_line_amounts': '22000000.000000',
        'total_payable_amount': '22000000.000000',
        'updated_at': sales_quote.updated_at.isoformat(),
        'virtual_account_no': None
    }

def test_index(client, user_sean_ali, db_session, sales_quote):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sales_quote_id = sales_quote.id
    response = client.get(f"/api/sales-quotes", headers=headers)
    assert response.status_code == 200

    response_body = response.json()
    sales_quote = db_session.query(SalesQuote).filter(SalesQuote.id == sales_quote_id).first()
    qline1 = sales_quote.sales_quote_lines[0]
    qline2 = sales_quote.sales_quote_lines[1]

    assert response_body == {
        'sales_quotes': [
            {
                'created_at': sales_quote.created_at.isoformat(),
                'credit_card_bank_name': None,
                'credit_card_customer_address': None,
                'credit_card_customer_name': None,
                'customer_id': user_sean_ali.id,
                'customer_name': 'Sean Ali',
                'id': sales_quote.id,
                'paylater_account_reference': None,
                'payment_method_id': sales_quote.payment_method_id,
                'payment_method_name': 'BBB Bank Transfer',
                'sales_quote_lines': [{'component_id': qline1.component_id,
                                        'created_at': qline1.created_at.isoformat(),
                                        'id': qline1.id,
                                        'price_per_unit': '12000000.000000',
                                        'quantity': '1.000000',
                                        'sales_quote_id': sales_quote.id,
                                        'total_line_amount': '12000000.000000',
                                        'updated_at': qline1.updated_at.isoformat()},
                                    {'component_id': qline2.component_id,
                                        'created_at': qline2.created_at.isoformat(),
                                        'id': qline2.id,
                                        'price_per_unit': '10000000.000000',
                                        'quantity': '1.000000',
                                        'sales_quote_id': sales_quote.id,
                                        'total_line_amount': '10000000.000000',
                                        'updated_at': qline2.updated_at.isoformat()}],
                'sales_quote_no': sales_quote.sales_quote_no,
                'shipping_address': 'Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
                'sum_total_line_amounts': '0.000000',
                'total_payable_amount': '0.000000',
                'updated_at': sales_quote.updated_at.isoformat(),
                'virtual_account_no': None
            }
        ]
    }

def test_destroy(client, user_sean_ali, db_session, sales_quote):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sales_quote_id = sales_quote.id
    response = client.delete(f"/api/sales-quotes/{sales_quote_id}", headers=headers)

    assert response.status_code == 204
    sales_quote = db_session.query(SalesQuote).filter(SalesQuote.id == sales_quote_id).first()
    assert sales_quote is None
