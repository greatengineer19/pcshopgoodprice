import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from src.tests.factories.user_factory import UserFactory
from src.tests.factories.component_factory import ComponentFactory
from src.tests.factories.cart_line_factory import CartLineFactory
from src.tests.factories.component_category_factory import ComponentCategoryFactory
from src.tests.factories.payment_method_factory import PaymentMethodFactory
from src.tests.factories.sales_invoice_factory import SalesInvoiceFactory
from src.tests.factories.sales_invoice_line_factory import SalesInvoiceLineFactory
from src.tests.factories.sales_delivery_factory import SalesDeliveryFactory
from src.tests.factories.sales_delivery_line_factory import SalesDeliveryLineFactory
from decimal import Decimal
from fastapi import HTTPException
from src.tests.conftest import ( client, db_session, setup_factories )
from utils.auth import ( create_access_token, create_refresh_token, decodeJWT, get_current_user )
from src.models import (
    CartLine,
    ComputerComponentSellPriceSetting,
    SalesQuote,
    SalesDelivery
)
from sqlalchemy.orm import object_session

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
def payment_method_bank_transfer():
    return PaymentMethodFactory(
        name="BBB Bank Transfer"
    )

@pytest.fixture
def sales_invoice(user_sean_ali,
                payment_method_bank_transfer,
                cart_line_gpu_4070_sean_ali,
                cart_line_gpu_4060_sean_ali):
    sales_invoice = SalesInvoiceFactory(
        customer_id=user_sean_ali.id,
        customer_name=user_sean_ali.fullname,
        sales_quote_no='test_sales_quote',
        shipping_address='Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        payment_method_id=payment_method_bank_transfer.id,
        payment_method_name=payment_method_bank_transfer.name,
    )

    SalesInvoiceLineFactory(
        sales_invoice_id=sales_invoice.id,
        component_id=cart_line_gpu_4070_sean_ali.component_id,
        component_name=cart_line_gpu_4070_sean_ali.component.name,
        quantity=cart_line_gpu_4070_sean_ali.quantity,
        price_per_unit=12000000,
        total_line_amount=12000000 * cart_line_gpu_4070_sean_ali.quantity
    )

    SalesInvoiceLineFactory(
        sales_invoice_id=sales_invoice.id,
        component_id=cart_line_gpu_4060_sean_ali.component_id,
        component_name=cart_line_gpu_4060_sean_ali.component.name,
        quantity=cart_line_gpu_4060_sean_ali.quantity,
        price_per_unit=10000000,
        total_line_amount=10000000 * cart_line_gpu_4060_sean_ali.quantity
    )

    return sales_invoice

@pytest.fixture
def sales_delivery(sales_invoice):
    sales_delivery = SalesDeliveryFactory(
        sales_invoice_id=sales_invoice.id
    )

    for invoice_line in sales_invoice.sales_invoice_lines:
        SalesDeliveryLineFactory(
            sales_delivery_id=sales_delivery.id,
            component_id=invoice_line.component_id,
            quantity=invoice_line.quantity
        )

    return sales_delivery

def test_show(client, db_session, user_sean_ali, sales_delivery):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get(f"/api/sales-deliveries/{sales_delivery.id}", headers=headers)
    assert response.status_code == 200

    response_body = response.json()
    
    sales_delivery = db_session.merge(sales_delivery)
    db_session.refresh(sales_delivery)
    delivery_line_1 = sales_delivery.sales_delivery_lines[0]
    delivery_line_2 = sales_delivery.sales_delivery_lines[1]
    assert response_body == {
        'created_at': sales_delivery.created_at.isoformat(),
        'id': sales_delivery.id,
        'sales_delivery_lines': [{'component_id': delivery_line_1.component_id,
                                'created_at': delivery_line_1.created_at.isoformat(),
                                'id': delivery_line_1.id,
                                'quantity': '1.000000',
                                'sales_delivery_id': delivery_line_1.sales_delivery_id,
                                'updated_at': delivery_line_1.updated_at.isoformat()},
                                {'component_id': delivery_line_2.component_id,
                                'created_at': delivery_line_2.created_at.isoformat(),
                                'id': delivery_line_2.id,
                                'quantity': '1.000000',
                                'sales_delivery_id': delivery_line_2.sales_delivery_id,
                                'updated_at': delivery_line_2.updated_at.isoformat()}],
        'sales_delivery_no': sales_delivery.sales_delivery_no,
        'sales_invoice_id': sales_delivery.sales_invoice_id,
        'status': 'PROCESSING',
        'updated_at': sales_delivery.updated_at.isoformat()
    }

def test_void(client, db_session, user_sean_ali, sales_delivery):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.patch(f"/api/sales-deliveries/{sales_delivery.id}/void", headers=headers)

    assert response.status_code == 200

    sales_delivery = db_session.merge(sales_delivery)
    db_session.refresh(sales_delivery)

    assert sales_delivery.status == 2

def test_fully_delivered(client, db_session, user_sean_ali, sales_delivery):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.patch(f"/api/sales-deliveries/{sales_delivery.id}/fully_delivered", headers=headers)

    assert response.status_code == 200

    sales_delivery = db_session.merge(sales_delivery)
    db_session.refresh(sales_delivery)

    assert sales_delivery.status == 1

def test_create(client, db_session, user_sean_ali, sales_invoice):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    param = {
        'id': sales_invoice.id
    }
    response = client.post(f"/api/sales-deliveries", headers=headers, json=param)
    assert response.status_code == 201

    delivery = db_session.query(SalesDelivery).order_by(desc(SalesDelivery.id)).first()
    assert delivery.sales_invoice_id == sales_invoice.id



