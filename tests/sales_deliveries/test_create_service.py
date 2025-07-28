import pytest
from tests.factories.component_factory import ComponentFactory
from tests.factories.cart_line_factory import CartLineFactory
from tests.factories.sales_invoice_factory import SalesInvoiceFactory
from tests.factories.sales_invoice_line_factory import SalesInvoiceLineFactory
from decimal import Decimal
from tests.conftest import (
    client,
    db_session,
    setup_factories,
    user_sean_ali,
    component_category_gpu,
    payment_method_bank_transfer
)
from src.models import (
    ComputerComponentSellPriceSetting,
    SalesDelivery
)
from sqlalchemy.orm import (
    object_session,
    joinedload
)
from src.api.api import create_sales_delivery_every_thirty_seconds

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

def test_create(db_session,
        sales_invoice,
        sales_invoice_2
    ):
    response = create_sales_delivery_every_thirty_seconds(db=db_session)

    assert response is None

    deliveries = db_session.query(SalesDelivery).all()
    assert len(deliveries) == 2

    delivery = deliveries[0]
    assert delivery.sales_invoice_id == sales_invoice.id
    assert delivery.sales_delivery_no == 'OUTBOUND-DELIVERY-00001'
    assert delivery.status == 0

    delivery_2 = deliveries[1]
    assert delivery_2.sales_invoice_id == sales_invoice_2.id
    assert delivery_2.sales_delivery_no == 'OUTBOUND-DELIVERY-00002'
    assert delivery_2.status == 0