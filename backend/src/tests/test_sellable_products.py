import pytest
from src.tests.factories.component_factory import ComponentFactory
from src.tests.factories.component_category_factory import ComponentCategoryFactory
from src.tests.factories.computer_component_review_factory import ComputerComponentReviewFactory
from src.tests.factories.computer_component_sell_price_setting_factory import ComputerComponentSellPriceSettingFactory
from src.tests.factories.user_factory import UserFactory
from src.tests.conftest import ( client, db_session, setup_factories, component_category_fan )

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali")

@pytest.fixture
def user_n3():
    return UserFactory(fullname="N3")

@pytest.fixture
def user_jason():
    return UserFactory(fullname="Jason")

def test_empty_index(client):
    response = client.get("/api/sellable-products")
    response_body = response.json()
    assert response_body == {'sellable_products': {} }
    assert response.status_code == 200

def test_index(client, db_session, component_category_fan, user_sean_ali):
    db_session.commit()

    blue_fan = ComponentFactory(
        name="CPU Fan Blue",
        product_code="cpu_fan_blue",
        component_category_id=component_category_fan.id,
        status=0
    )
    red_fan = ComponentFactory(
        name="CPU Fan Red",
        product_code="cpu_fan_red",
        component_category_id=component_category_fan.id,
        status=0
    )

    for rating in [4,4,5]:
        for component_id in [blue_fan.id, red_fan.id]:
            ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=component_id
            )
    for component_id in [blue_fan.id, red_fan.id]:
        ComputerComponentSellPriceSettingFactory(
            component_id=component_id,
            day_type=0,
            active=True,
            price_per_unit=999
        )


    response = client.get("/api/sellable-products")
    response_body = response.json()

    assert response_body == {
        'sellable_products': {
            '0': {
                'components': [
                    {
                        'component_category_id': blue_fan.component_category_id,
                        'component_category_name': None,
                        'computer_component_sell_price_settings': [
                            {
                                'active': True,
                                'component_id': blue_fan.id,
                                'day_type': 'default',
                                'id': blue_fan.computer_component_sell_price_settings[0].id,
                                'price_per_unit': '999.000000'
                            }
                        ],
                        'count_review_given': 3,
                        'created_at': blue_fan.created_at.isoformat(),
                        'description': None,
                        'id': blue_fan.id,
                        'images': [],
                        'name': 'CPU Fan Blue',
                        'sell_price': 999.0,
                        'product_code': 'cpu_fan_blue',
                        'rating': 4.33,
                        'status': 0,
                        'updated_at': blue_fan.updated_at.isoformat()
                    },
                    {
                        'component_category_id': red_fan.component_category_id,
                        'component_category_name': None,
                        'computer_component_sell_price_settings': [
                            {
                                'active': True,
                                'component_id': red_fan.id,
                                'day_type': 'default',
                                'id': red_fan.computer_component_sell_price_settings[0].id,
                                'price_per_unit': '999.000000'
                            }
                        ],
                        'count_review_given': 3,
                        'created_at': red_fan.created_at.isoformat(),
                        'description': None,
                        'id': red_fan.id,
                        'images': [],
                        'name': 'CPU Fan Red',
                        'sell_price': 999.0,
                        'product_code': 'cpu_fan_red',
                        'rating': 4.33,
                        'status': 0,
                        'updated_at': red_fan.updated_at.isoformat()
                    }
                ],
                'name': 'FAN'
            }
        }
    }

def test_index_min_rating_beyond_4(client, db_session, component_category_fan, user_sean_ali):
    db_session.commit()

    blue_fan = ComponentFactory(
        name="CPU Fan Blue",
        product_code="cpu_fan_blue",
        component_category_id=component_category_fan.id,
        status=0
    )
    red_fan = ComponentFactory(
        name="CPU Fan Red",
        product_code="cpu_fan_red",
        component_category_id=component_category_fan.id,
        status=0
    )

    for rating in [4,4,5]:
        ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=blue_fan.id
            )

    for rating in [2,2,3]:
        ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=red_fan.id
            )  
            
    for component_id in [blue_fan.id, red_fan.id]:
        ComputerComponentSellPriceSettingFactory(
            component_id=component_id,
            day_type=0,
            active=True,
            price_per_unit=999
        )


    response = client.get(f"/api/sellable-products?min_rating=4")
    response_body = response.json()
    assert response_body == {
        'sellable_products': {
            '0': {
                'components': [
                    {
                        'component_category_id': blue_fan.component_category_id,
                        'component_category_name': None,
                        'computer_component_sell_price_settings': [
                            {
                                'active': True,
                                'component_id': blue_fan.id,
                                'day_type': 'default',
                                'id': blue_fan.computer_component_sell_price_settings[0].id,
                                'price_per_unit': '999.000000'
                            }
                        ],
                        'count_review_given': 3,
                        'created_at': blue_fan.created_at.isoformat(),
                        'description': None,
                        'id': blue_fan.id,
                        'images': [],
                        'name': 'CPU Fan Blue',
                        'sell_price': 999.0,
                        'product_code': 'cpu_fan_blue',
                        'rating': 4.33,
                        'status': 0,
                        'updated_at': blue_fan.updated_at.isoformat()
                    }
                ],
                'name': 'FAN'
            }
        }
    }

def test_index_component_category_ids(client, db_session, component_category_fan, user_sean_ali):
    db_session.commit()

    blue_fan = ComponentFactory(
        name="CPU Fan Blue",
        product_code="cpu_fan_blue",
        component_category_id=component_category_fan.id,
        status=0
    )
    red_fan = ComponentFactory(
        name="CPU Fan Red",
        product_code="cpu_fan_red",
        component_category_id=component_category_fan.id,
        status=0
    )

    for rating in [4,4,5]:
        ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=blue_fan.id
            )

    for rating in [2,2,3]:
        ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=red_fan.id
            )  
            
    for component_id in [blue_fan.id, red_fan.id]:
        ComputerComponentSellPriceSettingFactory(
            component_id=component_id,
            day_type=0,
            active=True,
            price_per_unit=999
        )

    response = client.get(f"/api/sellable-products?component_category_ids=9999,9998")
    response_body = response.json()
    assert response_body == {'sellable_products': {}}

def test_index_min_price(client, db_session, component_category_fan, user_sean_ali):
    db_session.commit()

    blue_fan = ComponentFactory(
        name="CPU Fan Blue",
        product_code="cpu_fan_blue",
        component_category_id=component_category_fan.id,
        status=0
    )
    red_fan = ComponentFactory(
        name="CPU Fan Red",
        product_code="cpu_fan_red",
        component_category_id=component_category_fan.id,
        status=0
    )

    for rating in [4,4,5]:
        ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=blue_fan.id
            )

    for rating in [2,2,3]:
        ComputerComponentReviewFactory(
                user_id=user_sean_ali.id,
                user_fullname=user_sean_ali.fullname,
                rating=rating,
                component_id=red_fan.id
            ) 
            
    ComputerComponentSellPriceSettingFactory(
        component_id=blue_fan.id,
        day_type=0,
        active=True,
        price_per_unit=300
    )

    ComputerComponentSellPriceSettingFactory(
        component_id=red_fan.id,
        day_type=0,
        active=True,
        price_per_unit=700
    )

    response = client.get(f"/api/sellable-products?start_price=699")
    response_body = response.json()

    assert response_body == {
        'sellable_products': {'0': {
            'components': [
                {'component_category_id': red_fan.component_category_id,
                'component_category_name': None,
                'computer_component_sell_price_settings': [
                    {
                        'active': True,
                        'component_id': red_fan.id,
                        'day_type': 'default',
                        'id': red_fan.computer_component_sell_price_settings[0].id,
                        'price_per_unit': '700.000000'
                    }],
                'count_review_given': 3,
                'created_at': red_fan.created_at.isoformat(),
                'description': None,
                'id': red_fan.id,
                'images': [],
                'name': red_fan.name,
                'product_code': 'cpu_fan_red',
                'rating': 2.33,
                'sell_price': 700.0,
                'status': 0,
                'updated_at': red_fan.updated_at.isoformat()}],
                'name': 'FAN'}
            }
    }

