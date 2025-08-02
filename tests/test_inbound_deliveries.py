from src.models import (
    PurchaseInvoice,
    InboundDelivery,
    Inventory
)
from src.schemas import (
    InboundDeliveryLineAsParams,
    InboundDeliveryAsParams,
    InboundDeliveryAttachmentAsParams,
    PurchaseInvoiceStatusEnum
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
from datetime import datetime
from unittest.mock import patch, ANY, MagicMock, AsyncMock
from src.inbound_deliveries.show_service import ShowService

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
    response = client.get("/api/inbound-deliveries")
    response_body = response.json()

    assert response_body == {'inbound_deliveries': []}
    assert response.status_code == 200

def test_index(client, db_session, inbound_delivery_1):
    db_session.commit()

    response = client.get("/api/inbound-deliveries")
    response_body = response.json()
    assert response.status_code == 200
    inbound_deliveries = response_body['inbound_deliveries']
    assert len(inbound_deliveries) == 1
    
    inbound_delivery = inbound_deliveries[0]
    assert inbound_delivery == {
        'created_at': inbound_delivery_1.created_at,
        'deleted': False,
        'id': inbound_delivery_1.id,
        'inbound_delivery_date': inbound_delivery_1.inbound_delivery_date,
        'inbound_delivery_no': 'IBD-00001',
        'inbound_delivery_reference': 'EK-OBD-00001',
        'notes': 'Test Package',
        'purchase_invoice_no': inbound_delivery_1.purchase_invoice_no,
        'received_by': 'Sean Ali',
        'status': 'delivered',
        'updated_at': inbound_delivery_1.updated_at
    }

def test_show(client, db_session, inbound_delivery_1):
    db_session.commit()

    response = client.get(f"/api/inbound-deliveries/{inbound_delivery_1.id}")
    response_body = response.json()

    lines = inbound_delivery_1.inbound_delivery_lines
    noctua_fan = next((line for line in lines if line.component_name == 'CPU Noctua Fan'), None)
    liquid_cooling_rgb = next((line for line in lines if line.component_name == 'CPU Liquid Cooling RGB'), None)

    assert response_body == {
        'created_at': inbound_delivery_1.created_at.isoformat(),
        'deleted': False,
        'id': inbound_delivery_1.id,
        'inbound_delivery_attachments': [],
        'inbound_delivery_date': inbound_delivery_1.inbound_delivery_date.strftime("%Y-%m-%dT%H:%M:%S"),
        'inbound_delivery_lines': [{'component_category_id': noctua_fan.component_category_id,
                                    'component_category_name': 'FAN',
                                    'component_id': noctua_fan.component_id,
                                    'component_name': 'CPU Noctua Fan',
                                    'created_at': noctua_fan.created_at.isoformat(),
                                    'damaged_quantity': 0,
                                    'deleted': False,
                                    'expected_quantity': 3,
                                    'id': noctua_fan.id,
                                    'inbound_delivery_id': inbound_delivery_1.id,
                                    'notes': None,
                                    'price_per_unit': '3300.000000',
                                    'purchase_invoice_line_id': noctua_fan.purchase_invoice_line_id,
                                    'received_quantity': 3,
                                    'total_line_amount': '9900.000000',
                                    'updated_at': noctua_fan.updated_at.isoformat()},
                                    {'component_category_id': liquid_cooling_rgb.component_category_id,
                                    'component_category_name': 'FAN',
                                    'component_id': liquid_cooling_rgb.component_id,
                                    'component_name': 'CPU Liquid Cooling RGB',
                                    'created_at': liquid_cooling_rgb.created_at.isoformat(),
                                    'damaged_quantity': 0,
                                    'deleted': False,
                                    'expected_quantity': 2,
                                    'id': liquid_cooling_rgb.id,
                                    'inbound_delivery_id': inbound_delivery_1.id,
                                    'notes': None,
                                    'price_per_unit': '1500.000000',
                                    'purchase_invoice_line_id': liquid_cooling_rgb.purchase_invoice_line_id,
                                    'received_quantity': 2,
                                    'total_line_amount': '3000.000000',
                                    'updated_at': liquid_cooling_rgb.updated_at.isoformat()}],
        'inbound_delivery_no': inbound_delivery_1.inbound_delivery_no,
        'inbound_delivery_reference': inbound_delivery_1.inbound_delivery_reference,
        'notes': 'Test Package',
        'purchase_invoice_no': inbound_delivery_1.purchase_invoice_no,
        'received_by': 'Sean Ali',
        'status': 'DELIVERED',
        'updated_at': inbound_delivery_1.updated_at.isoformat()
    }

def test_deliverable_purchase_invoices(client, db_session, purchase_invoice_1):
    db_session.commit()
    response = client.get("/api/inbound-deliveries/deliverable-purchase-invoices")
    response_body = response.json()

    invoice_line = purchase_invoice_1.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice_1.purchase_invoice_lines[1]

    assert response_body == {
        'purchase_invoices': [
            {
                'deliverable_invoice_lines':   
                [
                    {
                        'component_category_id': invoice_line.component_category_id,
                        'component_category_name': 'FAN',
                        'component_id': invoice_line.component_id,
                        'component_name': 'CPU Liquid Cooling RGB',
                        'deliverable_quantity': 2,
                        'id': invoice_line.id,
                        'price_per_unit': '1500.000000'
                    },
                    {
                        'component_category_id': invoice_line_2.component_category_id,
                        'component_category_name': 'FAN',
                        'component_id': invoice_line_2.component_id,
                        'component_name': 'CPU Noctua Fan',
                        'deliverable_quantity': 3,
                        'id': invoice_line_2.id,
                        'price_per_unit': '3300.000000'
                    }
                ],
                'id': purchase_invoice_1.id,
                'invoice_date': purchase_invoice_1.invoice_date.isoformat(),
                'purchase_invoice_no': purchase_invoice_1.purchase_invoice_no,
                'supplier_name': 'Aftershock PC'
            }
        ]
    }

def test_deliverable_purchase_invoices_with_partial_deliverable_invoice(client, db_session, purchase_invoice_1, inbound_delivery_2_partial_deliver_invoice):
    db_session.commit()
    response = client.get("/api/inbound-deliveries/deliverable-purchase-invoices")
    response_body = response.json()

    invoice_line = purchase_invoice_1.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice_1.purchase_invoice_lines[1]
    assert response_body == {
        'purchase_invoices': [
            {
                'deliverable_invoice_lines':   
                [
                    {
                        'component_category_id': invoice_line.component_category_id,
                        'component_category_name': 'FAN',
                        'component_id': invoice_line.component_id,
                        'component_name': 'CPU Liquid Cooling RGB',
                        'deliverable_quantity': 1,
                        'id': invoice_line.id,
                        'price_per_unit': '1500.000000'
                    },
                    {
                        'component_category_id': invoice_line_2.component_category_id,
                        'component_category_name': 'FAN',
                        'component_id': invoice_line_2.component_id,
                        'component_name': 'CPU Noctua Fan',
                        'deliverable_quantity': 2,
                        'id': invoice_line_2.id,
                        'price_per_unit': '3300.000000'
                    }
                ],
                'id': purchase_invoice_1.id,
                'invoice_date': purchase_invoice_1.invoice_date.isoformat(),
                'purchase_invoice_no': purchase_invoice_1.purchase_invoice_no,
                'supplier_name': 'Aftershock PC'
            }
        ]
    }

def test_create(client, db_session, inbound_delivery_create_params_1):
    db_session.commit()

    mock_s3_url = "http://test-s3-url.com"
    with patch('src.inbound_deliveries.show_service.ShowService.create_presigned_url', return_value=mock_s3_url):
        response = client.post("/api/inbound-deliveries", json = inbound_delivery_create_params_1.dict())
        response_body = response.json()
    
    inbound_delivery_1 = db_session.query(InboundDelivery).order_by(desc(InboundDelivery.id)).first()
    lines = inbound_delivery_1.inbound_delivery_lines
    noctua_fan = next((line for line in lines if line.component_name == 'CPU Noctua Fan'), None)
    liquid_cooling_rgb = next((line for line in lines if line.component_name == 'CPU Liquid Cooling RGB'), None)

    attachment = inbound_delivery_1.inbound_delivery_attachments[0]

    assert response_body == {
        'created_at': inbound_delivery_1.created_at.isoformat(),
        'deleted': False,
        'id': inbound_delivery_1.id,
        'inbound_delivery_attachments': [
            {
                'created_at': attachment.created_at.isoformat(),
                'file_link': 'http://test-s3-url.com',
                'file_s3_key': '12345678123456781234567812345678_test.jpg',
                'id': attachment.id,
                'inbound_delivery_id': inbound_delivery_1.id,
                'updated_at': attachment.updated_at.isoformat(),
                'uploaded_by': 'Sean Ali'
            }],
        'inbound_delivery_date': inbound_delivery_1.inbound_delivery_date.strftime("%Y-%m-%dT%H:%M:%S"),
        'inbound_delivery_lines': [{'component_category_id': noctua_fan.component_category_id,
                                    'component_category_name': 'FAN',
                                    'component_id': noctua_fan.component_id,
                                    'component_name': 'CPU Noctua Fan',
                                    'created_at': noctua_fan.created_at.isoformat(),
                                    'damaged_quantity': 0,
                                    'deleted': False,
                                    'expected_quantity': 3,
                                    'id': noctua_fan.id,
                                    'inbound_delivery_id': inbound_delivery_1.id,
                                    'notes': None,
                                    'price_per_unit': '3300.000000',
                                    'purchase_invoice_line_id': noctua_fan.purchase_invoice_line_id,
                                    'received_quantity': 3,
                                    'total_line_amount': '9900.000000',
                                    'updated_at': noctua_fan.updated_at.isoformat()},
                                    {'component_category_id': liquid_cooling_rgb.component_category_id,
                                    'component_category_name': 'FAN',
                                    'component_id': liquid_cooling_rgb.component_id,
                                    'component_name': 'CPU Liquid Cooling RGB',
                                    'created_at': liquid_cooling_rgb.created_at.isoformat(),
                                    'damaged_quantity': 0,
                                    'deleted': False,
                                    'expected_quantity': 2,
                                    'id': liquid_cooling_rgb.id,
                                    'inbound_delivery_id': inbound_delivery_1.id,
                                    'notes': None,
                                    'price_per_unit': '1500.000000',
                                    'purchase_invoice_line_id': liquid_cooling_rgb.purchase_invoice_line_id,
                                    'received_quantity': 2,
                                    'total_line_amount': '3000.000000',
                                    'updated_at': liquid_cooling_rgb.updated_at.isoformat()}],
        'inbound_delivery_no': inbound_delivery_1.inbound_delivery_no,
        'inbound_delivery_reference': 'EK-OBD-00001',
        'notes': None,
        'purchase_invoice_no': inbound_delivery_1.purchase_invoice_no,
        'received_by': 'Sean Ali',
        'status': 'DELIVERED',
        'updated_at': inbound_delivery_1.updated_at.isoformat()
    }

    inventories = db_session.query(Inventory).filter(Inventory.resource_id == inbound_delivery_1.id, Inventory.resource_type == 'InboundDelivery').all()
    assert len(inventories) == 2
    
    inventory_1 = inventories[0]
    assert inventory_1.resource_type == 'InboundDelivery'
    assert inventory_1.resource_line_type == 'InboundDeliveryLine'
    assert inventory_1.buy_price is not None
    assert inventory_1.in_stock is not None
    assert inventory_1.out_stock is None
    assert inventory_1.resource_line_id is not None
    assert inventory_1.resource_id is not None

    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == inbound_delivery_1.purchase_invoice_id).first()
    assert purchase_invoice.status == PurchaseInvoiceStatusEnum.COMPLETED

def test_destroy(client, db_session, inbound_delivery_1, inventories_from_inbound_d1):
    db_session.commit()
    inbound_delivery_id = inbound_delivery_1.id
    inventory_ids = [inv.id for inv in inventories_from_inbound_d1]
    purchase_invoice_id = inbound_delivery_1.purchase_invoice_id

    response = client.delete(f"/api/inbound-deliveries/{inbound_delivery_id}")
    assert response.status_code == 204
    
    inbound_delivery = (
        db_session
            .query(InboundDelivery)
            .filter(InboundDelivery.id == inbound_delivery_id).first()
    )

    assert inbound_delivery is None

    inventories = (
        db_session
            .query(Inventory)
            .filter(Inventory.id.in_(inventory_ids))
            .all()
    )

    assert len(inventories) == 0

    purchase_invoice = db_session.query(PurchaseInvoice).filter(PurchaseInvoice.id == purchase_invoice_id).first()
    assert purchase_invoice.status == PurchaseInvoiceStatusEnum.PENDING
