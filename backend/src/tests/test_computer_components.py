from src.models import (
    ComputerComponentCategory,
    ComputerComponent,
    User,
    ComputerComponentSellPriceSetting,
    ComputerComponentReview
    )
from src.schemas import (
    ComputerComponentAsResponse,
    ComputerComponentAsParams,
    ComputerComponentSellPriceSettingAsParams,
    DayTypeEnum
)
import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from src.tests.factories.component_factory import ComponentFactory
from src.tests.factories.component_category_factory import ComponentCategoryFactory
from decimal import Decimal
from fastapi import HTTPException
from src.tests.conftest import ( client, db_session, setup_factories, user_jason, user_n3, user_sean_ali )

@pytest.fixture
def component_category_fan():
    return ComponentCategoryFactory(
        name="FAN",
        status=0
    )

@pytest.fixture
def component_liquid_cooling_fan_1(component_category_fan):
    return ComponentFactory(
        name="CPU Liquid Cooling RGB",
        product_code="cpu_liquid_cooling_1",
        price=1,
        component_category_id=component_category_fan.id,
        status=0
    )

def test_empty_index(client):
    response = client.get("/api/computer-components")
    response_body = response.json()

    assert response_body == {'computer_components': []}
    assert response.status_code == 200

def test_index(client, db_session, component_category_fan):
    db_session.commit()

    blue_fan = ComponentFactory(
        name="CPU Fan Blue",
        product_code="cpu_fan_blue",
        price=1,
        component_category_id=component_category_fan.id,
        status=0
    )
    red_fan = ComponentFactory(
        name="CPU Fan Red",
        product_code="cpu_fan_red",
        price=1,
        component_category_id=component_category_fan.id,
        status=0
    )

    response = client.get("/api/computer-components")
    response_body = response.json()

    assert response_body == {
        'computer_components': 
        [
            {
                'component_category_id': blue_fan.component_category_id,
                'component_category_name': 'FAN',
                'created_at': blue_fan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'description': None,
                'computer_component_sell_price_settings':[],
                'id': blue_fan.id,
                'images': [],
                'name': 'CPU Fan Blue',
                'price': 1.0,
                'product_code': 'cpu_fan_blue',
                'status': 0,
                'stock': 0,
                'updated_at': blue_fan.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'component_category_id': red_fan.component_category_id,
                'component_category_name': 'FAN',
                'created_at': red_fan.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'description': None,
                'computer_component_sell_price_settings':[],
                'id': red_fan.id,
                'images': [],
                'name': 'CPU Fan Red',
                'price': 1.0,
                'product_code': 'cpu_fan_red',
                'status': 0,
                'stock': 0,
                'updated_at': red_fan.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
    }

def test_show(client, db_session, component_liquid_cooling_fan_1):
    db_session.commit()

    response = client.get(f"/api/computer-components/{component_liquid_cooling_fan_1.id}")
    response_body = response.json()
    assert response_body == {
        'component_category_id': component_liquid_cooling_fan_1.component_category_id,
        'component_category_name': None,
        'computer_component_sell_price_settings': [],
        'created_at': component_liquid_cooling_fan_1.created_at.isoformat(),
        'description': None,
        'id': component_liquid_cooling_fan_1.id,
        'images': None,
        'name': 'CPU Liquid Cooling RGB',
        'price': 1.0,
        'product_code': 'cpu_liquid_cooling_1',
        'status': 0,
        'stock': 0,
        'updated_at': component_liquid_cooling_fan_1.updated_at.isoformat()
    }
    
def test_create_no_category(client, db_session):
    params = ComputerComponentAsParams(
        id=None,
        image=None,
        component_category_name='Yikes',
        name="HDMI Cable 2.1b 1 meter",
        product_code="hdmi_cable",
        price=10,
        stock=0,
        description=None,
        status=0,
        computer_component_sell_price_settings_attributes=[]
    )

    response = client.post(f"/api/computer-components", json = params.model_dump())
    response_body = response.json()

    assert response.status_code == 404
    assert response_body == {'detail': 'Category not found'}

def test_create(client, db_session, component_category_fan, user_sean_ali, user_n3, user_jason):
    db_session.commit()

    component_category_fan.id # to declare category
    dup_category_fan = component_category_fan.__dict__.copy()
    params = {
            'id':None,
            'image':None,
            'component_category_name': dup_category_fan['name'],
            'name':"HDMI Cable 2.1b 1 meter",
            'product_code':"hdmi_cable",
            'price': 10,
            'stock': 0,
            'description': None,
            'status': 0,
            'computer_component_sell_price_settings_attributes': [
                {
                    'day_type' : 'default',
                    'price_per_unit' : '15'
                },
                {
                    'day_type' : 'monday',
                    'price_per_unit' : '16'
                },
                {
                    'day_type' : 'tuesday',
                    'price_per_unit' : '17'
                },
                {
                    'day_type' : 'wednesday',
                    'price_per_unit' : '18'
                },
                {
                    'day_type' : 'thursday',
                    'price_per_unit' : '19'
                },
                {
                    'day_type' : 'friday',
                    'price_per_unit' : '20'
                },
                {
                    'day_type' : 'saturday',
                    'price_per_unit' : '21'
                },
                {
                    'day_type' : 'sunday',
                    'price_per_unit' : '22'
                }
            ]
    }
    
    response = client.post(f"/api/computer-components", json = params)
    response_body = response.json()

    component_created = (
        db_session.query(ComputerComponent)
            .options(joinedload(ComputerComponent.computer_component_sell_price_settings))
            .order_by(desc(ComputerComponent.id))
            .first()
    )
    price_settings = component_created.computer_component_sell_price_settings
    assert response.status_code == 200
    assert response_body == {
        'component_category_id': component_created.component_category_id,
        'component_category_name': None,
        'created_at': component_created.created_at.isoformat(),
        'description': None,
        'id': component_created.id,
        'images': [],
        'name': 'HDMI Cable 2.1b 1 meter',
        'computer_component_sell_price_settings': [
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'default',
                'id': price_settings[0].id,
                'price_per_unit': '15.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'monday',
                'id': price_settings[1].id,
                'price_per_unit': '16.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'tuesday',
                'id': price_settings[2].id,
                'price_per_unit': '17.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'wednesday',
                'id': price_settings[3].id,
                'price_per_unit': '18.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'thursday',
                'id': price_settings[4].id,
                'price_per_unit': '19.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'friday',
                'id': price_settings[5].id,
                'price_per_unit': '20.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'saturday',
                'id': price_settings[6].id,
                'price_per_unit': '21.000000'},
            {'active': True,
                'component_id': component_created.id,
                'day_type': 'sunday',
                'id': price_settings[7].id,
                'price_per_unit': '22.000000'}
        ],
        'price': 10.0,
        'product_code': 'hdmi_cable',
        'status': 0,
        'stock': 0,
        'updated_at': component_created.updated_at.isoformat()
    }

    review_counts = db_session.query(func.count(ComputerComponentReview.id)).scalar()
    assert review_counts == 10

    price_settings = db_session.query(func.count(ComputerComponentSellPriceSetting.id)).scalar()
    assert price_settings == 8

def test_update_no_category(client, db_session, component_liquid_cooling_fan_1):
    db_session.commit()

    params = ComputerComponentAsParams(
            id=component_liquid_cooling_fan_1.id,
            image=None,
            component_category_name='Yikes',
            name="HDMI Cable 2.1b 1 meter",
            product_code="hdmi_cable",
            price=10,
            stock=0,
            description=None,
            status=0,
            computer_component_sell_price_settings_attributes=[]
        )
    
    response = client.patch(f"/api/computer-components/{component_liquid_cooling_fan_1.id}", json = params.model_dump())
    response_body = response.json()

    assert response_body == {'detail': 'Category not found'}
    assert response.status_code == 404

def test_update(client, db_session, component_liquid_cooling_fan_1, component_category_fan):
    db_session.commit()

    component_category_fan.id # to declare category
    dup_category_fan = component_category_fan.__dict__.copy()
    before_name = component_liquid_cooling_fan_1.name
    before_product_code = component_liquid_cooling_fan_1.product_code

    for day_type in [0,1,2,3,4,5,6,7]:
        component_liquid_cooling_fan_1.computer_component_sell_price_settings.append(
            ComputerComponentSellPriceSetting(
                day_type=day_type,
                price_per_unit=10,
                active=True
            )
        )
    
    db_session.commit()

    price_settings = component_liquid_cooling_fan_1.computer_component_sell_price_settings
    params = {
        'id':component_liquid_cooling_fan_1.id,
        'image':None,
        'component_category_name':dup_category_fan['name'],
        'name':"HDMI Cable 2.1b 1 meter",
        'product_code':"hdmi_cable",
        'price':10,
        'stock':0,
        'description':None,
        'status':0,
        'computer_component_sell_price_settings_attributes':[
            {
                'id': price_settings[0].id,
                'day_type': DayTypeEnum(price_settings[0].day_type).name,
                'active': price_settings[0].active,
                'price_per_unit': str(price_settings[0].price_per_unit)
            },
            {
                'id': price_settings[1].id,
                'day_type': DayTypeEnum(price_settings[1].day_type).name,
                'active': price_settings[1].active,
                'price_per_unit': str(price_settings[1].price_per_unit)
            },
            {
                'id': price_settings[2].id,
                'day_type': DayTypeEnum(price_settings[2].day_type).name,
                'active': price_settings[2].active,
                'price_per_unit': str(price_settings[2].price_per_unit)
            },
            {
                'id': price_settings[3].id,
                'day_type': DayTypeEnum(price_settings[3].day_type).name,
                'active': price_settings[3].active,
                'price_per_unit': str(price_settings[3].price_per_unit)
            },
            {
                'id': price_settings[4].id,
                'day_type': DayTypeEnum(price_settings[4].day_type).name,
                'active': price_settings[4].active,
                'price_per_unit': str(price_settings[4].price_per_unit)
            },
            {
                'id': price_settings[5].id,
                'day_type': DayTypeEnum(price_settings[5].day_type).name,
                'active': price_settings[5].active,
                'price_per_unit': str(price_settings[5].price_per_unit)
            },
            {
                'id': price_settings[6].id,
                'day_type': DayTypeEnum(price_settings[6].day_type).name,
                'active': price_settings[6].active,
                'price_per_unit': str(price_settings[6].price_per_unit)
            },
            {
                'id': price_settings[7].id,
                'day_type': DayTypeEnum(price_settings[7].day_type).name,
                'active': price_settings[7].active,
                'price_per_unit': str(price_settings[7].price_per_unit)
            }
        ]
    }
    
    response = client.patch(f"/api/computer-components/{component_liquid_cooling_fan_1.id}", json = params)
    response_body = response.json()

    assert response_body['name'] != before_name
    assert response_body['product_code'] != before_product_code

def test_destroy(client, db_session, component_liquid_cooling_fan_1):
    db_session.commit()

    response = client.delete(f"/api/computer-components/{component_liquid_cooling_fan_1.id}")
    assert response.status_code == 204

    component = db_session.query(ComputerComponent).filter(ComputerComponent.id == component_liquid_cooling_fan_1.id).first()
    assert component is None

