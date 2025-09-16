from src.models import (
    Inventory
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
from tests.conftest import ( component_category_fan, component_liquid_cooling_fan_1, client, db_session, setup_factories )
from decimal import Decimal
from datetime import ( datetime, timedelta )

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
def purchase_invoice_2(component_category_fan, component_liquid_cooling_fan_1, component_fan_1):
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
def inbound_delivery_2(purchase_invoice_2):
    invoice_line = purchase_invoice_2.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice_2.purchase_invoice_lines[1]
    inbound_delivery = InboundDeliveryFactory(
        purchase_invoice_id=purchase_invoice_2.id,
        purchase_invoice_no=purchase_invoice_2.purchase_invoice_no,
        inbound_delivery_date=func.now(),
        inbound_delivery_reference='EK-OBD-00011',
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
def inventories_from_inbound_d2(inbound_delivery_2):
    inventories = []
    for inbound_line in inbound_delivery_2.inbound_delivery_lines:
        inventory = InventoryFactory(
            in_stock=inbound_line.received_quantity,
            stock_date=inbound_delivery_2.inbound_delivery_date,
            component_id=inbound_line.component_id,
            resource_line_id=inbound_line.id,
            resource_line_type='InboundDeliveryLine',
            resource_id=inbound_delivery_2.id,
            resource_type='InboundDelivery',
            buy_price=inbound_line.price_per_unit
        )
        inventories.append(inventory)

    return inventories

def test_empty_index(client):
    response = client.get("/api/report/inventory-movement")
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
            'report_headers': [{'text': 'Component Category'},
                                {'text': 'Component Name'},
                                {'text': 'Stock Date'},
                                {'text': 'Created At'},
                                {'text': 'Transaction Type'},
                                {'text': 'Transaction No.'},
                                {'text': 'Received By'},
                                {'text': 'In Stock'},
                                {'text': 'Out Stock'},
                                {'text': 'Final Moving Stock'},
                                {'text': 'Buy Price / Unit'}]
    }
    assert response.status_code == 200

def test_index(
        client,
        db_session,
        inbound_delivery_1,
        inbound_delivery_2,
        inventories_from_inbound_d1,
        inventories_from_inbound_d2
    ):
    db_session.commit()
    response = client.get("/api/report/inventory-movement")
    response_body = response.json()
    assert response.status_code == 200
    inventory_inbound_d1 = inventories_from_inbound_d1[0]
    assert response_body == {'paging': {'page': 1,
            'pagination': {'next_page_url': None,
                           'prev_page_url': None},
            'total_item': 4},
            'report_body': [[{'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.stock_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.created_at.strftime('%d %B %Y %H:%M:%S')},
                            {'cell_type': 'text', 'text': 'InboundDelivery'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no},
                            {'cell_type': 'text', 'text': 'Sean Ali'},
                            {'cell_type': 'quantity', 'text': '2'},
                            {'cell_type': 'quantity', 'text': '0'},
                            {'cell_type': 'quantity', 'text': '2'},
                            {'cell_type': 'money', 'text': '1500.00'}],
                            [{'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'text', 'text': 'CPU Liquid Cooling RGB'},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.stock_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.created_at.strftime('%d %B %Y %H:%M:%S')},
                            {'cell_type': 'text', 'text': 'InboundDelivery'},
                            {'cell_type': 'text', 'text': inbound_delivery_2.inbound_delivery_no},
                            {'cell_type': 'text', 'text': 'Sean Ali'},
                            {'cell_type': 'quantity', 'text': '2'},
                            {'cell_type': 'quantity', 'text': '0'},
                            {'cell_type': 'quantity', 'text': '4'},
                            {'cell_type': 'money', 'text': '1500.00'}],
                            [{'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.stock_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.created_at.strftime('%d %B %Y %H:%M:%S')},
                            {'cell_type': 'text', 'text': 'InboundDelivery'},
                            {'cell_type': 'text', 'text': inbound_delivery_1.inbound_delivery_no},
                            {'cell_type': 'text', 'text': 'Sean Ali'},
                            {'cell_type': 'quantity', 'text': '3'},
                            {'cell_type': 'quantity', 'text': '0'},
                            {'cell_type': 'quantity', 'text': '3'},
                            {'cell_type': 'money', 'text': '3300.00'}],
                            [{'cell_type': 'text', 'text': 'FAN'},
                            {'cell_type': 'text', 'text': 'CPU Noctua Fan'},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.stock_date.strftime('%d %B %Y')},
                            {'cell_type': 'text', 'text': inventory_inbound_d1.created_at.strftime('%d %B %Y %H:%M:%S')},
                            {'cell_type': 'text', 'text': 'InboundDelivery'},
                            {'cell_type': 'text', 'text': inbound_delivery_2.inbound_delivery_no},
                            {'cell_type': 'text', 'text': 'Sean Ali'},
                            {'cell_type': 'quantity', 'text': '3'},
                            {'cell_type': 'quantity', 'text': '0'},
                            {'cell_type': 'quantity', 'text': '6'},
                            {'cell_type': 'money', 'text': '3300.00'}]],
            'report_headers': [{'text': 'Component Category'},
                                {'text': 'Component Name'},
                                {'text': 'Stock Date'},
                                {'text': 'Created At'},
                                {'text': 'Transaction Type'},
                                {'text': 'Transaction No.'},
                                {'text': 'Received By'},
                                {'text': 'In Stock'},
                                {'text': 'Out Stock'},
                                {'text': 'Final Moving Stock'},
                                {'text': 'Buy Price / Unit'}]}
