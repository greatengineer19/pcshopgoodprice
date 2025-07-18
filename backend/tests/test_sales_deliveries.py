import pytest
from sqlalchemy import select, desc, func, and_
from sqlalchemy.orm import joinedload
from tests.factories.component_factory import ComponentFactory
from tests.factories.cart_line_factory import CartLineFactory
from tests.factories.sales_invoice_factory import SalesInvoiceFactory
from tests.factories.sales_invoice_line_factory import SalesInvoiceLineFactory
from tests.factories.sales_delivery_factory import SalesDeliveryFactory
from tests.factories.sales_delivery_line_factory import SalesDeliveryLineFactory
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import (
    client,
    db_session,
    setup_factories,
    user_sean_ali,
    component_category_gpu,
    payment_method_bank_transfer
)
from utils.auth import ( create_access_token, create_refresh_token, decodeJWT, get_current_user )
from src.models import (
    ComputerComponentSellPriceSetting,
    Inventory
)
from src.schemas import SalesDeliveryStatusEnum

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
def sales_invoice(user_sean_ali,
                payment_method_bank_transfer,
                cart_line_gpu_4070_sean_ali):
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

    return sales_invoice

@pytest.fixture
def sales_invoice_2(user_sean_ali,
                payment_method_bank_transfer,
                cart_line_gpu_4060_sean_ali):
    sales_invoice = SalesInvoiceFactory(
        customer_id=user_sean_ali.id,
        customer_name=user_sean_ali.fullname,
        sales_quote_no='test_sales_quote 2',
        shipping_address='Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        payment_method_id=payment_method_bank_transfer.id,
        payment_method_name=payment_method_bank_transfer.name,
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

@pytest.fixture
def sales_delivery_2(sales_invoice_2):
    sales_delivery = SalesDeliveryFactory(
        sales_invoice_id=sales_invoice_2.id
    )

    for invoice_line in sales_invoice_2.sales_invoice_lines:
        SalesDeliveryLineFactory(
            sales_delivery_id=sales_delivery.id,
            component_id=invoice_line.component_id,
            quantity=invoice_line.quantity
        )

    return sales_delivery

def test_index(client, db_session, user_sean_ali, sales_delivery, sales_delivery_2):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get(f"/api/sales-deliveries", headers=headers)

    sales_delivery = db_session.merge(sales_delivery)
    db_session.refresh(sales_delivery)

    sales_delivery_2 = db_session.merge(sales_delivery_2)
    db_session.refresh(sales_delivery_2)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body == {
        'sales_deliveries': [
            {
                'created_at': sales_delivery.created_at.isoformat(),
                'customer_id': user_sean_ali.id,
                'customer_name': 'Sean Ali',
                'id': sales_delivery_2.id,
                'sales_delivery_lines': [{'component_id': sales_delivery_2.sales_delivery_lines[0].component_id,
                                            'component_name': 'Zotac RTX '
                                                            '4060',
                                            'created_at': sales_delivery.created_at.isoformat(),
                                            'id': sales_delivery_2.sales_delivery_lines[0].id,
                                            'quantity': '1.000000',
                                            'sales_delivery_id': sales_delivery_2.id,
                                            'updated_at': sales_delivery.created_at.isoformat()}],
                'sales_delivery_no': sales_delivery_2.sales_delivery_no,
                'sales_invoice_id': sales_delivery_2.sales_invoice_id,
                'shipping_address': 'Batam, 29461, Kepulauan Riau, '
                                    'Indonesia. 081890989098',
                'status': 'PROCESSING',
                'updated_at': sales_delivery.created_at.isoformat()
        },
        {
            'created_at': sales_delivery.created_at.isoformat(),
            'customer_id': user_sean_ali.id,
            'customer_name': 'Sean Ali',
            'id': sales_delivery.id,
            'sales_delivery_lines': [{'component_id': sales_delivery.sales_delivery_lines[0].component_id,
                                        'component_name': 'Zotac RTX '
                                                        '4070',
                                        'created_at': sales_delivery.created_at.isoformat(),
                                        'id': sales_delivery.sales_delivery_lines[0].id,
                                        'quantity': '1.000000',
                                        'sales_delivery_id': sales_delivery.id,
                                        'updated_at': sales_delivery.created_at.isoformat()}],
            'sales_delivery_no': sales_delivery.sales_delivery_no,
            'sales_invoice_id': sales_delivery.sales_invoice_id,
            'shipping_address': 'Batam, 29461, Kepulauan Riau, '
                                'Indonesia. 081890989098',
            'status': 'PROCESSING',
            'updated_at': sales_delivery.created_at.isoformat()
        }
        ]
    }

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


    assert response_body == {
        'created_at': sales_delivery.created_at.isoformat(),
        'customer_id': user_sean_ali.id,
        'customer_name': 'Sean Ali',
        'id': sales_delivery.id,
        'sales_delivery_lines': [{'component_id': sales_delivery.sales_delivery_lines[0].component_id,
                                'component_name': 'Zotac RTX 4070',
                                'created_at': sales_delivery.created_at.isoformat(),
                                'id': sales_delivery.sales_delivery_lines[0].id,
                                'quantity': '1.000000',
                                'sales_delivery_id': sales_delivery.id,
                                'updated_at': sales_delivery.created_at.isoformat()}],
        'sales_delivery_no': sales_delivery.sales_delivery_no,
        'sales_invoice_id': sales_delivery.sales_invoice_id,
        'shipping_address': 'Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        'status': 'PROCESSING',
        'updated_at': sales_delivery.created_at.isoformat()
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

    assert sales_delivery.status == SalesDeliveryStatusEnum(2).value

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

    assert sales_delivery.status == SalesDeliveryStatusEnum(1).value

    inventories = db_session.query(Inventory).filter(and_(Inventory.resource_type=="SalesDelivery", Inventory.resource_id==sales_delivery.id)).all()
    assert len(inventories) == 1

    inventory = inventories[0]
    assert inventory.buy_price is None
    assert inventory.resource_type == 'SalesDelivery'
    assert inventory.resource_line_type == 'SalesDeliveryLine'
    assert inventory.in_stock is None
    assert inventory.out_stock == Decimal('1.000000')

