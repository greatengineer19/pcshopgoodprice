import pytest
from fastapi.testclient import TestClient
from src.api.api import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from src.database import Base
import inspect
import importlib
from pathlib import Path
from tests.factories import BaseFactory
from src.api.session_db import get_db
from tests.factories.component_factory import ComponentFactory
from tests.factories.component_category_factory import ComponentCategoryFactory
from tests.factories.computer_component_sell_price_setting_factory import ComputerComponentSellPriceSettingFactory
from tests.factories.computer_component_review_factory import ComputerComponentReviewFactory
from tests.factories.user_factory import UserFactory
from tests.factories.payment_method_factory import PaymentMethodFactory
from tests.factories.account_factory import AccountFactory
from tests.factories.payment_factory import PaymentFactory
from src.schemas import DayTypeEnum
import os


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["TESTING"] = "true"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali", role=0)

@pytest.fixture
def user_n3():
    return UserFactory(fullname="N3", role=1)

@pytest.fixture
def user_jason():
    return UserFactory(fullname="Jason", role=1)

@pytest.fixture
def payment_method_bank_transfer():
    return PaymentMethodFactory(
        name="BBB Bank Transfer"
    )

@pytest.fixture
def component_category_gpu():
    return ComponentCategoryFactory(
        name="GPU",
        status=0
    )

@pytest.fixture
def component_category_fan():
    return ComponentCategoryFactory(
        name="FAN",
        status=0
    )

@pytest.fixture
def component_category_peripherals():
    return ComponentCategoryFactory(
        name="Peripherals",
        status=0
    )

@pytest.fixture
def component_liquid_cooling_fan_1(component_category_fan):
    return ComponentFactory(
        name="CPU Liquid Cooling RGB",
        product_code="cpu_liquid_cooling_1",
        component_category_id=component_category_fan.id,
        status=0
    )

@pytest.fixture
def component_keyboard_logitech(component_category_peripherals):
    return ComponentFactory(
        name="Logitech G515 Lightspeed",
        product_code="g515_lightspeed",
        component_category_id=component_category_peripherals.id,
        status=0
    )

@pytest.fixture
def review_component_keyboard_logitech(component_keyboard_logitech, user_sean_ali):
    return ComputerComponentReviewFactory(
        user_id=user_sean_ali.id,
        component_id=component_keyboard_logitech.id,
        user_fullname=user_sean_ali.fullname,
        rating=5,
        comments="Good product, great service, but please improve courier tracking accuracy."
    )

@pytest.fixture
def review_component_liquid_fan(component_liquid_cooling_fan_1, user_jason):
    return ComputerComponentReviewFactory(
        user_id=user_jason.id,
        component_id=component_liquid_cooling_fan_1.id,
        user_fullname=user_jason.fullname,
        rating=4,
        comments="My first time buying from them, and I'm impressed. Product arrived early, seal intact, and it works great."
    )


@pytest.fixture
def sell_price_on_wednesday_of_keyboard_logitech(component_keyboard_logitech):
    return ComputerComponentSellPriceSettingFactory(
        component_id=component_keyboard_logitech.id,
        day_type=DayTypeEnum(3).value,
        active=True,
        price_per_unit=1600000
    )

@pytest.fixture
def sell_price_on_thursday_of_keyboard_logitech(component_keyboard_logitech):
    return ComputerComponentSellPriceSettingFactory(
        component_id=component_keyboard_logitech.id,
        day_type=DayTypeEnum(4).value,
        active=True,
        price_per_unit=1660000
    )

@pytest.fixture
def sell_price_default_of_keyboard_logitech(component_keyboard_logitech):
    return ComputerComponentSellPriceSettingFactory(
        component_id=component_keyboard_logitech.id,
        day_type=DayTypeEnum(0).value,
        active=True,
        price_per_unit=1550000
    )

@pytest.fixture
def sell_price_on_wednesday_of_liquid_fan(component_liquid_cooling_fan_1):
    return ComputerComponentSellPriceSettingFactory(
        component_id=component_liquid_cooling_fan_1.id,
        day_type=DayTypeEnum(3).value,
        active=True,
        price_per_unit=235000
    )

@pytest.fixture
def sell_price_on_thursday_of_liquid_fan(component_liquid_cooling_fan_1):
    return ComputerComponentSellPriceSettingFactory(
        component_id=component_liquid_cooling_fan_1.id,
        day_type=DayTypeEnum(4).value,
        active=True,
        price_per_unit=245000
    )

@pytest.fixture
def sell_price_default_of_liquid_fan(component_liquid_cooling_fan_1):
    return ComputerComponentSellPriceSettingFactory(
        component_id=component_liquid_cooling_fan_1.id,
        day_type=DayTypeEnum(0).value,
        active=True,
        price_per_unit=200000
    )

@pytest.fixture(scope="module")
def engine():
    DATABASE_URL = "postgresql+psycopg2://user00:chocolatecake@localhost:5433/user00"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))

    Base.metadata.create_all(engine)
    yield engine

    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))

    engine.dispose()

@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """This MUST run after db_session fixture"""
    from tests.factories.component_category_factory import ComponentCategoryFactory
    from tests.factories.component_factory import ComponentFactory
    from tests.factories.purchase_invoice_factory import PurchaseInvoiceFactory
    from tests.factories.purchase_invoice_line_factory import PurchaseInvoiceLineFactory
    from tests.factories.inbound_delivery_factory import InboundDeliveryFactory
    from tests.factories.inbound_delivery_line_factory import InboundDeliveryLineFactory
    from tests.factories.inbound_delivery_attachment_factory import InboundDeliveryAttachmentFactory
    from tests.factories.inventory_factory import InventoryFactory
    from tests.factories.user_factory import UserFactory
    from tests.factories.computer_component_review_factory import ComputerComponentReviewFactory
    from tests.factories.computer_component_sell_price_setting_factory import ComputerComponentSellPriceSettingFactory
    from tests.factories.cart_line_factory import CartLineFactory
    from tests.factories.sales_quote_factory import SalesQuoteFactory
    from tests.factories.sales_quote_line_factory import SalesQuoteLineFactory
    from tests.factories.payment_method_factory import PaymentMethodFactory
    from tests.factories.sales_invoice_factory import SalesInvoiceFactory
    from tests.factories.sales_delivery_factory import SalesDeliveryFactory
    from tests.factories.sales_invoice_line_factory import SalesInvoiceLineFactory
    from tests.factories.sales_delivery_line_factory import SalesDeliveryLineFactory
    from tests.factories.payment_factory import PaymentFactory
    from tests.factories.account_factory import AccountFactory

    print(f"\nSetting up factories with session: {id(db_session)}")

    # Set session on each factory class
    ComponentCategoryFactory._meta.sqlalchemy_session = db_session
    ComponentFactory._meta.sqlalchemy_session = db_session
    PurchaseInvoiceFactory._meta.sqlalchemy_session = db_session
    PurchaseInvoiceLineFactory._meta.sqlalchemy_session = db_session
    InboundDeliveryFactory._meta.sqlalchemy_session = db_session
    InboundDeliveryLineFactory._meta.sqlalchemy_session = db_session
    InboundDeliveryAttachmentFactory._meta.sqlalchemy_session = db_session
    InventoryFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session
    ComputerComponentReviewFactory._meta.sqlalchemy_session = db_session
    ComputerComponentSellPriceSettingFactory._meta.sqlalchemy_session = db_session
    CartLineFactory._meta.sqlalchemy_session = db_session
    SalesQuoteFactory._meta.sqlalchemy_session = db_session
    SalesQuoteLineFactory._meta.sqlalchemy_session = db_session
    PaymentMethodFactory._meta.sqlalchemy_session = db_session
    SalesInvoiceFactory._meta.sqlalchemy_session = db_session
    SalesDeliveryFactory._meta.sqlalchemy_session = db_session
    SalesInvoiceLineFactory._meta.sqlalchemy_session = db_session
    SalesDeliveryLineFactory._meta.sqlalchemy_session = db_session
    PaymentFactory._meta.sqlalchemy_session = db_session
    AccountFactory._meta.sqlalchemy_session = db_session

    factories = [
        ComponentCategoryFactory,
        ComponentFactory,
        PurchaseInvoiceFactory,
        PurchaseInvoiceLineFactory,
        InboundDeliveryFactory,
        InboundDeliveryLineFactory,
        InboundDeliveryAttachmentFactory,
        InventoryFactory,
        UserFactory,
        ComputerComponentReviewFactory,
        ComputerComponentSellPriceSettingFactory,
        CartLineFactory,
        SalesQuoteFactory,
        SalesQuoteLineFactory,
        PaymentMethodFactory,
        SalesInvoiceFactory,
        SalesInvoiceLineFactory,
        SalesDeliveryFactory,
        SalesDeliveryLineFactory,
        PaymentFactory,
        AccountFactory
    ]

    # Set persistence mode
    for factory in factories:
        factory._meta.sqlalchemy_session_persistence = "commit"

    print(f"[DEBUG] Current factory session: {ComponentCategoryFactory._meta.sqlalchemy_session} (id: {id(ComponentCategoryFactory._meta.sqlalchemy_session)})")
    yield

    # Clean up
    for factory in factories:
        factory._meta.sqlalchemy_session = None


