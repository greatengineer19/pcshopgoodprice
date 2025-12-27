import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from tests.factories.component_factory import ComponentFactory
from tests.factories.cart_line_factory import CartLineFactory
from tests.factories.sales_invoice_factory import SalesInvoiceFactory
from tests.factories.sales_invoice_line_factory import SalesInvoiceLineFactory
from tests.factories.sales_quote_factory import SalesQuoteFactory
from tests.factories.sales_quote_line_factory import SalesQuoteLineFactory
from decimal import Decimal
from tests.conftest import (
    client,
    db_session,
    setup_factories,
    user_sean_ali,
    payment_method_bank_transfer,
    component_category_gpu
)
from utils.auth import ( create_access_token, create_refresh_token, decodeJWT, get_current_user )
from src.models import (
    SalesInvoice,
    ComputerComponentSellPriceSetting,
    SalesQuote
)
from sqlalchemy.orm import object_session

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

@pytest.fixture
def sales_invoice(user_sean_ali,
                payment_method_bank_transfer,
                cart_line_gpu_4070_sean_ali,
                cart_line_gpu_4060_sean_ali,
                sales_quote):
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

def test_index(client, user_sean_ali, db_session, sales_invoice):
    db_session.commit()

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get(f"/api/sales-invoices", headers=headers)
    assert response.status_code == 200

    response_body = response.json()
    sales_invoice = db_session.query(SalesInvoice).order_by(desc(SalesInvoice.id)).first()
    line1 = sales_invoice.sales_invoice_lines[0]
    line2 = sales_invoice.sales_invoice_lines[1]

    assert response_body == { 'sales_invoices': [{
            'created_at': sales_invoice.created_at.isoformat(),
            'credit_card_bank_name': None,
            'credit_card_customer_address': None,
            'credit_card_customer_name': None,
            'customer_id': sales_invoice.customer_id,
            'customer_name': 'Sean Ali',
            'id': sales_invoice.id,
            'paylater_account_reference': None,
            'payment_method_id': sales_invoice.payment_method_id,
            'payment_method_name': 'BBB Bank Transfer',
            'sales_invoice_lines': [{'component_id': line1.component_id,
                                    'component_name': 'Zotac RTX 4070',
                                    'created_at': sales_invoice.created_at.isoformat(),
                                    'id': line1.id,
                                    'price_per_unit': '12000000.000000',
                                    'quantity': '1.000000',
                                    'images': [],
                                    'sales_invoice_id': sales_invoice.id,
                                    'total_line_amount': '12000000.000000',
                                    'updated_at': sales_invoice.created_at.isoformat()},
                                    {'component_id': line2.component_id,
                                    'component_name': 'Zotac RTX 4060',
                                    'created_at': sales_invoice.created_at.isoformat(),
                                    'id': line2.id,
                                    'price_per_unit': '10000000.000000',
                                    'quantity': '1.000000',
                                    'images': [],
                                    'sales_invoice_id': sales_invoice.id,
                                    'total_line_amount': '10000000.000000',
                                    'updated_at': sales_invoice.created_at.isoformat()}],
            'sales_invoice_no': sales_invoice.sales_invoice_no,
            'sales_quote_no': sales_invoice.sales_quote_no,
            'shipping_address': 'Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
            'status': 'PENDING',
            'sum_total_line_amounts': '0.000000',
            'total_payable_amount': '0.000000',
            'updated_at': sales_invoice.created_at.isoformat(),
            'virtual_account_no': None
        }]
    }

def test_create(client, user_sean_ali, db_session, sales_quote):
    db_session.commit()

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sales_quote_id = sales_quote.id
    params = {
        'id': None,
        'sales_quote_id': sales_quote_id,
        'sales_quote_no': sales_quote.sales_quote_no,
    }
    response = client.post(f"/api/sales-invoices", headers=headers, json = params)
    assert response.status_code == 201

    response_body = response.json()
    sales_invoice = db_session.query(SalesInvoice).order_by(desc(SalesInvoice.id)).first()
    line1 = sales_invoice.sales_invoice_lines[0]
    line2 = sales_invoice.sales_invoice_lines[1]

    assert response_body == {
        'created_at': sales_invoice.created_at.isoformat(),
        'credit_card_bank_name': None,
        'credit_card_customer_address': None,
        'credit_card_customer_name': None,
        'customer_id': sales_invoice.customer_id,
        'customer_name': 'Sean Ali',
        'id': sales_invoice.id,
        'paylater_account_reference': None,
        'payment_method_id': sales_invoice.payment_method_id,
        'payment_method_name': 'BBB Bank Transfer',
        'sales_invoice_lines': [{'component_id': line1.component_id,
                                'component_name': 'Zotac RTX 4070',
                                'created_at': sales_invoice.created_at.isoformat(),
                                'id': line1.id,
                                'price_per_unit': '12000000.000000',
                                'quantity': '1.000000',
                                'images': [],
                                'sales_invoice_id': sales_invoice.id,
                                'total_line_amount': '12000000.000000',
                                'updated_at': sales_invoice.created_at.isoformat()},
                                {'component_id': line2.component_id,
                                'component_name': 'Zotac RTX 4060',
                                'created_at': sales_invoice.created_at.isoformat(),
                                'id': line2.id,
                                'price_per_unit': '10000000.000000',
                                'quantity': '1.000000',
                                'images': [],
                                'sales_invoice_id': sales_invoice.id,
                                'total_line_amount': '10000000.000000',
                                'updated_at': sales_invoice.created_at.isoformat()}],
        'sales_invoice_no': sales_invoice.sales_invoice_no,
        'sales_quote_no': sales_invoice.sales_quote_no,
        'shipping_address': 'Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        'status': 'PENDING',
        'sum_total_line_amounts': '0.000000',
        'total_payable_amount': '0.000000',
        'updated_at': sales_invoice.created_at.isoformat(),
        'virtual_account_no': None
    }

def test_show(client, db_session, user_sean_ali, sales_invoice):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get(f"/api/sales-invoices/{sales_invoice.id}", headers=headers)
    assert response.status_code == 200

    response_body = response.json()
    
    sales_invoice = db_session.merge(sales_invoice)
    db_session.refresh(sales_invoice)
    invoice_line_1 = sales_invoice.sales_invoice_lines[0]
    invoice_line_2 = sales_invoice.sales_invoice_lines[1]

    assert response_body == {
        'created_at': sales_invoice.created_at.isoformat(),
        'id': sales_invoice.id,
        'shipping_address': 'Batam, 29461, Kepulauan Riau, Indonesia. 081890989098',
        'virtual_account_no': None,
        'credit_card_bank_name': None,
        'credit_card_customer_address': None,
        'credit_card_customer_name': None,
        'customer_id': user_sean_ali.id,
        'customer_name': 'Sean Ali',
        'paylater_account_reference': None,
        'payment_method_id': sales_invoice.payment_method_id,
        'payment_method_name': 'BBB Bank Transfer',
        'sales_invoice_lines': [
            {
                'component_id': invoice_line_1.component_id,
                'component_name': 'Zotac RTX 4070',
                'created_at': invoice_line_1.created_at.isoformat(),
                'id': invoice_line_1.id,
                'price_per_unit': '12000000.000000',
                'quantity': '1.000000',
                'images': [],
                'sales_invoice_id': sales_invoice.id,
                'total_line_amount': '12000000.000000',
                'updated_at': invoice_line_1.updated_at.isoformat()
            },
            {
                'component_id': invoice_line_2.component_id,
                'component_name': 'Zotac RTX 4060',
                'created_at': invoice_line_2.created_at.isoformat(),
                'id': invoice_line_2.id,
                'price_per_unit': '10000000.000000',
                'quantity': '1.000000',
                'images': [],
                'sales_invoice_id': invoice_line_2.sales_invoice_id,
                'total_line_amount': '10000000.000000',
                'updated_at': invoice_line_2.updated_at.isoformat()
            }
        ],
        'sales_invoice_no': sales_invoice.sales_invoice_no,
        'sales_quote_no': 'test_sales_quote',
        'status': 'PENDING',
        'sum_total_line_amounts': '0.000000',
        'total_payable_amount': '0.000000',
        'updated_at': sales_invoice.updated_at.isoformat()
    }

def test_void(client, user_sean_ali, db_session, sales_invoice):
    db_session.commit()
    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    sales_invoice_id = sales_invoice.id
    response = client.patch(f"/api/sales-invoices/{sales_invoice_id}/void", headers=headers)
    assert response.status_code == 200
    
    response_body = response.json()
    assert response_body['status'] == 'VOID'

