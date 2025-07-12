from src.models import (
    PurchaseInvoice
    )
from src.schemas import (
    PurchaseInvoiceLineAsParams,
    PurchaseInvoiceAsParams,
    StatusEnum
)
import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from src.tests.factories.purchase_invoice_factory import PurchaseInvoiceFactory
from src.tests.factories.purchase_invoice_line_factory import PurchaseInvoiceLineFactory
from src.tests.factories.component_factory import ComponentFactory
from src.tests.factories.component_category_factory import ComponentCategoryFactory
from src.tests.conftest import ( client, db_session, setup_factories )
from decimal import Decimal
from datetime import datetime
from fastapi.encoders import jsonable_encoder

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
def purchase_invoice_create_params_1(component_category_fan, component_liquid_cooling_fan_1, component_fan_1):
    params = PurchaseInvoiceAsParams(
        invoice_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        expected_delivery_date=None,
        notes=None,
        supplier_name="Enterkomputer Shop",
        status=StatusEnum.PENDING,
        purchase_invoice_lines_attributes=[
            PurchaseInvoiceLineAsParams(
                component_id=component_liquid_cooling_fan_1.id,
                component_name=component_liquid_cooling_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=5,
                price_per_unit='2350'
            ),
            PurchaseInvoiceLineAsParams(
                component_id=component_fan_1.id,
                component_name=component_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=3,
                price_per_unit='1350'
            )
        ]
    )

    return params

@pytest.fixture
def purchase_invoice_update_params_1(
        purchase_invoice_1,
        component_category_fan,
        component_cubegaming_fan_1,
        component_liquid_cooling_fan_1,
        component_fan_1
    ):
    invoice_line = next((invoice_line for invoice_line in purchase_invoice_1.purchase_invoice_lines if invoice_line.component_id == component_liquid_cooling_fan_1.id), None)
    invoice_line_2 = next((invoice_line for invoice_line in purchase_invoice_1.purchase_invoice_lines if invoice_line.component_id == component_fan_1.id), None)

    params = PurchaseInvoiceAsParams(
        id=purchase_invoice_1.id,
        supplier_name="Enterkomputer Shop",
        status=StatusEnum.PENDING,
        expected_delivery_date=None,
        notes=None,
        invoice_date=purchase_invoice_1.invoice_date.strftime('%Y-%m-%d %H:%M:%S'),
        purchase_invoice_lines_attributes=[
            PurchaseInvoiceLineAsParams(
                id=invoice_line.id,
                component_id=component_liquid_cooling_fan_1.id,
                component_name=component_liquid_cooling_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=5,
                price_per_unit='2350',
                _destroy=True
            ),
            PurchaseInvoiceLineAsParams(
                id=invoice_line_2.id,
                component_id=component_fan_1.id,
                component_name=component_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=3,
                price_per_unit='1350'
            ),
            PurchaseInvoiceLineAsParams(
                component_id=component_cubegaming_fan_1.id,
                component_name=component_cubegaming_fan_1.name,
                component_category_id=component_category_fan.id,
                component_category_name=component_category_fan.name,
                quantity=5,
                price_per_unit='775'
            )
        ]
    )

    return params

def test_empty_index(client):
    response = client.get("/api/purchase-invoices")
    response_body = response.json()

    assert response_body == {'purchase_invoices': []}
    assert response.status_code == 200

def test_index(client, purchase_invoice_1, db_session):
    db_session.commit()

    response = client.get("/api/purchase-invoices")
    response_body = response.json()
    assert response.status_code == 200

    purchase_invoices = response_body['purchase_invoices']
    assert len(purchase_invoices) == 1
    
    purchase_invoice = purchase_invoices[0]
    assert purchase_invoice['id'] == purchase_invoice_1.id
    assert purchase_invoice['deleted'] == False
    assert purchase_invoice['expected_delivery_date'] == None
    assert purchase_invoice['notes'] == 'testing'
    assert purchase_invoice['purchase_invoice_no'] == 'BUY-00001'
    assert purchase_invoice['status'] == 'pending'
    assert Decimal(purchase_invoice['sum_total_line_amounts']) == Decimal('12900.000000')
    assert purchase_invoice['supplier_name'] == 'Aftershock PC'

def test_show(client, db_session, purchase_invoice_1):
    db_session.commit()

    purchase_invoice = purchase_invoice_1
    response = client.get(f"/api/purchase-invoices/{purchase_invoice.id}")
    response_body = response.json()

    invoice_line = purchase_invoice.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice.purchase_invoice_lines[1]
    datetime_object = datetime.strptime(purchase_invoice.invoice_date, '%Y-%m-%d %H:%M:%S')

    formatted_date = datetime_object.strftime('%Y-%m-%d %H:%M:%S')

    assert response_body == {
            'deleted': False,
            'expected_delivery_date': None,
            'id': purchase_invoice.id,
            'invoice_date': formatted_date,
            'notes': 'testing',
            'purchase_invoice_lines': [
                {
                    'component_category_id': invoice_line.component_category_id,
                    'component_category_name': 'FAN',
                    'component_id': invoice_line.component_id,
                    'component_name': 'CPU Liquid Cooling RGB',
                    'id': invoice_line.id,
                    'price_per_unit': 1500,
                    'quantity': 2,
                    'total_line_amount': '3000.000000'
                },
                {
                    'component_category_id': invoice_line_2.component_category_id,
                    'component_category_name': 'FAN',
                    'component_id': invoice_line_2.component_id,
                    'component_name': 'CPU Noctua Fan',
                    'id': invoice_line_2.id,
                    'price_per_unit': 3300,
                    'quantity': 3,
                    'total_line_amount': '9900.000000'
                }
            ],
            'purchase_invoice_no': purchase_invoice.purchase_invoice_no,
            'status': 'PENDING',
            'sum_total_line_amounts': '12900.000000',
            'supplier_name': 'Aftershock PC'
        }

def test_create(client, db_session, purchase_invoice_create_params_1):
    db_session.commit()
    response = client.post("/api/purchase-invoices", json = purchase_invoice_create_params_1.dict())
    response_body = response.json()

    purchase_invoice = db_session.query(PurchaseInvoice).order_by(desc(PurchaseInvoice.id)).first()
    invoice_line = purchase_invoice.purchase_invoice_lines[0]
    invoice_line_2 = purchase_invoice.purchase_invoice_lines[1]
    assert response_body == {
        'deleted': False,
        'expected_delivery_date': None,
        'id': purchase_invoice.id,
        'invoice_date': purchase_invoice.invoice_date.strftime('%Y-%m-%d %H:%M:%S'),
        'notes': None,
        'purchase_invoice_lines': [{'component_category_id': invoice_line.component_category_id,
                                    'component_category_name': 'FAN',
                                    'component_id': invoice_line.component_id,
                                    'component_name': 'CPU Liquid Cooling RGB',
                                    'id': invoice_line.id,
                                    'price_per_unit': 2350,
                                    'quantity': 5,
                                    'total_line_amount': '11750.000000'},
                                    {'component_category_id': invoice_line_2.component_category_id,
                                    'component_category_name': 'FAN',
                                    'component_id': invoice_line_2.component_id,
                                    'component_name': 'CPU Noctua Fan',
                                    'id': invoice_line_2.id,
                                    'price_per_unit': 1350,
                                    'quantity': 3,
                                    'total_line_amount': '4050.000000'}],
        'purchase_invoice_no': purchase_invoice.purchase_invoice_no,
        'status': 'PENDING',
        'sum_total_line_amounts': '15800.000000',
        'supplier_name': 'Enterkomputer Shop'
    }

def test_update(client, db_session, purchase_invoice_update_params_1):
    db_session.commit()

    purchase_invoice = (
        db_session
            .query(PurchaseInvoice)
            .filter(PurchaseInvoice.id == purchase_invoice_update_params_1.id)
            .first()
    )

    old_amount = purchase_invoice.sum_total_line_amounts
    old_names = set()
    for invoice_line in purchase_invoice.purchase_invoice_lines:
        old_names.add(invoice_line.component_name)

    response = client.patch(f"/api/purchase-invoices/{purchase_invoice_update_params_1.id}", json = purchase_invoice_update_params_1.dict(by_alias=True))
    response_body = response.json()

    invoice_lines = response_body['purchase_invoice_lines']
    assert(len(invoice_lines)) == 2
    assert response_body['sum_total_line_amounts'] == '7925.000000'
    assert str(old_amount) == '12900.000000'

    new_names = set()
    for invoice_line in invoice_lines:
        new_names.add(invoice_line['component_name'])

    assert new_names != old_names


def test_destroy(client, db_session, purchase_invoice_1):
    db_session.commit()
    invoice_id = purchase_invoice_1.id

    response = client.delete(f"/api/purchase-invoices/{purchase_invoice_1.id}")
    assert response.status_code == 204
    
    purchase_invoice = (
        db_session
            .query(PurchaseInvoice)
            .filter(PurchaseInvoice.id == invoice_id).first()
    )

    assert purchase_invoice is None
