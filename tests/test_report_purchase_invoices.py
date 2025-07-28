from src.models import (
    PurchaseInvoice,
    InboundDelivery,
    Inventory
)
from src.schemas import (
    InboundDeliveryLineAsParams,
    InboundDeliveryAsParams,
    InboundDeliveryStatusEnum,
    InboundDeliveryAttachmentAsParams,
    StatusEnum
)
import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from tests.factories.inbound_delivery_factory import InboundDeliveryFactory
from tests.factories.inbound_delivery_line_factory import InboundDeliveryLineFactory
from tests.factories.inbound_delivery_attachment_factory import InboundDeliveryAttachmentFactory
from tests.factories.purchase_invoice_factory import PurchaseInvoiceFactory
from tests.factories.purchase_invoice_line_factory import PurchaseInvoiceLineFactory
from tests.factories.component_factory import ComponentFactory
from tests.factories.component_category_factory import ComponentCategoryFactory
from tests.factories.inventory_factory import InventoryFactory
from tests.conftest import ( client, db_session, setup_factories )
from decimal import Decimal
from datetime import ( datetime, timedelta )
from unittest.mock import patch, ANY, MagicMock, AsyncMock

@pytest.fixture
def component_category_fan():
    category = ComponentCategoryFactory(
        name="FAN",
        status=0
    )
    return category

@pytest.fixture
def component_liquid_cooling_fan_1(component_category_fan):
    component = ComponentFactory(
        name="CPU Liquid Cooling RGB",
        product_code="cpu_liquid_cooling_1",
        component_category_id=component_category_fan.id,
        status=0
    )

    return component

@pytest.fixture
def component_fan_1(component_category_fan):
    component = ComponentFactory(
        name="CPU Noctua Fan",
        product_code="cpu_noctua_fan_1",
        component_category_id=component_category_fan.id,
        status=0
    )
    return component

@pytest.fixture
def component_cubegaming_fan_1(component_category_fan):
    component = ComponentFactory(
        name="CPU Cubegaming Fan",
        product_code="cpu_cubegaming_fan_1",
        component_category_id=component_category_fan.id,
        status=0
    )
    return component

@pytest.fixture
def purchase_invoice_1(component_category_fan, component_liquid_cooling_fan_1, component_fan_1):
    purchase_invoice = PurchaseInvoiceFactory(
        invoice_date=func.now(),
        notes="testing",
        supplier_name="Aftershock PC",
        purchase_invoice_lines=[
            PurchaseInvoiceLineFactory.build(
                component_id=component_liquid_cooling_fan_1.id,
                component_name=component_liquid_cooling_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=2,
                price_per_unit=1500,
                total_line_amount=3000
            ),
            PurchaseInvoiceLineFactory.build(
                component_id=component_fan_1.id,
                component_name=component_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=3,
                price_per_unit=3300,
                total_line_amount=9900
            )
        ]
    )

    return purchase_invoice

@pytest.fixture
def inbound_delivery_1(purchase_invoice_1):
    invoice_line = purchase_invoice_1.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice_1.purchase_invoice_lines[1]
    inbound_delivery = InboundDeliveryFactory(
        purchase_invoice_id=purchase_invoice_1.id,
        purchase_invoice_no=purchase_invoice_1.purchase_invoice_no,
        inbound_delivery_date=func.now(),
        inbound_delivery_reference='EK-OBD-00001',
        received_by='Sean Ali',
        notes='Test Package',
        inbound_delivery_lines=[
            InboundDeliveryLineFactory.build(
                purchase_invoice_line_id=invoice_line.id,
                component_id=invoice_line.component_id,
                component_name=invoice_line.component_name,
                component_category_id=invoice_line.component_category_id,
                component_category_name=invoice_line.component_category_name,
                expected_quantity=invoice_line.quantity,
                received_quantity=invoice_line.quantity,
                damaged_quantity=0,
                price_per_unit=invoice_line.price_per_unit,
                total_line_amount=invoice_line.total_line_amount
            ),
            InboundDeliveryLineFactory.build(
                purchase_invoice_line_id=invoice_line_2.id,
                component_id=invoice_line_2.component_id,
                component_name=invoice_line_2.component_name,
                component_category_id=invoice_line_2.component_category_id,
                component_category_name=invoice_line_2.component_category_name,
                expected_quantity=invoice_line_2.quantity,
                received_quantity=invoice_line_2.quantity,
                damaged_quantity=0,
                price_per_unit=invoice_line_2.price_per_unit,
                total_line_amount=invoice_line_2.total_line_amount
            )
        ]
    )

    return inbound_delivery

@pytest.fixture
def inbound_delivery_2_partial_deliver_invoice(purchase_invoice_1):
    invoice_line = purchase_invoice_1.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice_1.purchase_invoice_lines[1]
    inbound_delivery = InboundDeliveryFactory(
        purchase_invoice_id=purchase_invoice_1.id,
        purchase_invoice_no=purchase_invoice_1.purchase_invoice_no,
        inbound_delivery_date=func.now(),
        inbound_delivery_reference='EK-OBD-00001',
        received_by='Sean Ali',
        notes='Test Package',
        inbound_delivery_lines=[
            InboundDeliveryLineFactory.build(
                purchase_invoice_line_id=invoice_line.id,
                component_id=invoice_line.component_id,
                component_name=invoice_line.component_name,
                component_category_id=invoice_line.component_category_id,
                component_category_name=invoice_line.component_category_name,
                expected_quantity=invoice_line.quantity,
                received_quantity=1,
                damaged_quantity=0,
                price_per_unit=invoice_line.price_per_unit,
                total_line_amount=invoice_line.total_line_amount
            ),
            InboundDeliveryLineFactory.build(
                purchase_invoice_line_id=invoice_line_2.id,
                component_id=invoice_line_2.component_id,
                component_name=invoice_line_2.component_name,
                component_category_id=invoice_line_2.component_category_id,
                component_category_name=invoice_line_2.component_category_name,
                expected_quantity=invoice_line_2.quantity,
                received_quantity=1,
                damaged_quantity=0,
                price_per_unit=invoice_line_2.price_per_unit,
                total_line_amount=invoice_line_2.total_line_amount
            )
        ]
    )

    return inbound_delivery

@pytest.fixture
def inventories_from_inbound_d1(inbound_delivery_1):
    inventories = []
    for inbound_line in inbound_delivery_1.inbound_delivery_lines:
        inventory = InventoryFactory(
            in_stock=inbound_line.received_quantity,
            stock_date=inbound_delivery_1.inbound_delivery_date,
            component_id=inbound_line.component_id,
            resource_line_id=inbound_line.id,
            resource_line_type='InboundDeliveryLine',
            resource_id=inbound_delivery_1.id,
            resource_type='InboundDelivery',
            buy_price=inbound_line.price_per_unit
        )
        inventories.append(inventory)

    return inventories

@pytest.fixture
def inbound_delivery_create_params_1(purchase_invoice_1):
    invoice_line = purchase_invoice_1.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice_1.purchase_invoice_lines[1]

    params = InboundDeliveryAsParams(
        purchase_invoice_id = purchase_invoice_1.id,
        purchase_invoice_no=purchase_invoice_1.purchase_invoice_no,
        inbound_delivery_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        inbound_delivery_reference='EK-OBD-00001',
        received_by='Sean Ali',
        notes=None,
        inbound_delivery_lines_attributes=[
            InboundDeliveryLineAsParams(
                purchase_invoice_line_id=invoice_line.id,
                component_id=invoice_line.component_id,
                component_name=invoice_line.component_name,
                component_category_id=invoice_line.component_category_id,
                component_category_name=invoice_line.component_category_name,
                expected_quantity=invoice_line.quantity,
                received_quantity=invoice_line.quantity,
                damaged_quantity=0,
                price_per_unit=str(invoice_line.price_per_unit)
            ),
            InboundDeliveryLineAsParams(
                purchase_invoice_line_id=invoice_line_2.id,
                component_id=invoice_line_2.component_id,
                component_name=invoice_line_2.component_name,
                component_category_id=invoice_line_2.component_category_id,
                component_category_name=invoice_line_2.component_category_name,
                expected_quantity=invoice_line_2.quantity,
                received_quantity=invoice_line_2.quantity,
                damaged_quantity=0,
                price_per_unit=str(invoice_line_2.price_per_unit)
            )
        ],
        inbound_delivery_attachments_attributes=[
            InboundDeliveryAttachmentAsParams(
                file_s3_key='12345678123456781234567812345678_test.jpg',
                uploaded_by='Sean Ali'
            )
        ]
    )

    return params


def test_empty_index(client):
    response = client.get("/api/report/purchase-invoice")
    response_body = response.json()
    assert response_body == {
        'paging': {
                'page': 1,
                'pagination': {
                    'next_page_url': None,
                    'prev_page_url': None
                },
                'total_item': 0
            },
            'report_body': [],
            'report_headers': [
                {'text': 'Purchase Invoice No'},
                {'text': 'Invoice Date'},
                {'text': 'Component Name'},
                {'text': 'Category Name'},
                {'text': 'Quantity'},
                {'text': 'Price Per Unit'},
                {'text': 'Total Price'},
                {'text': 'Inbound Received Qty'},
                {'text': 'Inbound Damaged Qty'},
                {'text': 'Total Amount Received'},
                {'text': 'Inbound Delivery Dates'},
                {'text': 'Inbound Delivery No(s)'}
            ]
    }
    assert response.status_code == 200

def test_index(client, db_session, inbound_delivery_1):
    db_session.commit()

    response = client.get("/api/report/purchase-invoice")
    response_body = response.json()
    assert response.status_code == 200
    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()

    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}],
                            [{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'money', 'text': '3300.000000'},
                            {'cell_type': 'money', 'text': '9900.000000'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '9900.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}
    
def test_index_filter_start_date(client, db_session, inbound_delivery_1):
    db_session.commit()

    one_week_ago = datetime.now() - timedelta(weeks=1)
    response = client.get(f"/api/report/purchase-invoice?start_date={one_week_ago.strftime('%Y-%m-%d')}")
    response_body = response.json()
    assert response.status_code == 200
    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()

    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}],
                            [{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'money', 'text': '3300.000000'},
                            {'cell_type': 'money', 'text': '9900.000000'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '9900.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}

def test_index_filter_end_date(client, db_session, inbound_delivery_1):
    db_session.commit()

    next_week = datetime.now() + timedelta(weeks=1)
    response = client.get(f"/api/report/purchase-invoice?end_date={next_week.strftime('%Y-%m-%d')}")
    response_body = response.json()
    assert response.status_code == 200
    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()

    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}],
                            [{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'money', 'text': '3300.000000'},
                            {'cell_type': 'money', 'text': '9900.000000'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '9900.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}
    
def test_index_filter_status(client, db_session, inbound_delivery_1):
    db_session.commit()

    response = client.get(f"/api/report/purchase-invoice?invoice_status=3")
    response_body = response.json()
    assert response.status_code == 200

    assert response_body['report_body'] == []

def test_index_filter_keyword(client, db_session, inbound_delivery_1):
    db_session.commit()

    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()
    response = client.get(f"/api/report/purchase-invoice?keyword={purchase_invoice.purchase_invoice_no}")
    response_body = response.json()
    assert response.status_code == 200

    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}],
                            [{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'money', 'text': '3300.000000'},
                            {'cell_type': 'money', 'text': '9900.000000'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '9900.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}

def test_index_filter_component_name(client, db_session, inbound_delivery_1):
    db_session.commit()

    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()
    response = client.get(f"/api/report/purchase-invoice?component_name=liquid%20cooling")
    response_body = response.json()
    assert response.status_code == 200
    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}

def test_index_filter_component_category_id(client, db_session, inbound_delivery_1):
    db_session.commit()

    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()
    response = client.get(f"/api/report/purchase-invoice?component_category_id={purchase_invoice.purchase_invoice_lines[0].component_category_id}")
    response_body = response.json()
    assert response.status_code == 200
    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}],
                            [{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'money', 'text': '3300.000000'},
                            {'cell_type': 'money', 'text': '9900.000000'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '9900.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}
    
def test_index_all_filter_assigned_yet_empty(client, db_session, inbound_delivery_1):
    db_session.commit()

    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()
    response = client.get(f"/api/report/purchase-invoice?keyword=&invoice_status=&start_date=&end_date=&component_name=&component_category_id=&page=1")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': 'http://localhost:8000/api/report/purchase-invoice?page=2',
                           'prev_page_url': None},
            'total_item': 2},
            'report_body': [[{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'money', 'text': '1500.000000'},
                            {'cell_type': 'money', 'text': '3000.000000'},
                            {'cell_type': 'quantity', 'text': '2.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '3000.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}],
                            [{'cell_type': 'text', 'text': purchase_invoice.purchase_invoice_no},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'money', 'text': '3300.000000'},
                            {'cell_type': 'money', 'text': '9900.000000'},
                            {'cell_type': 'quantity', 'text': '3.000000'},
                            {'cell_type': 'quantity', 'text': '0.000000'},
                            {'cell_type': 'money', 'text': '9900.000000000000'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no}]],
            'report_headers': [{'text': 'Purchase Invoice No'},
                                {'text': 'Invoice Date'},
                                {'text': 'Component Name'},
                                {'text': 'Category Name'},
                                {'text': 'Quantity'},
                                {'text': 'Price Per Unit'},
                                {'text': 'Total Price'},
                                {'text': 'Inbound Received Qty'},
                                {'text': 'Inbound Damaged Qty'},
                                {'text': 'Total Amount Received'},
                                {'text': 'Inbound Delivery Dates'},
                                {'text': 'Inbound Delivery No(s)'}]}
