import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from src.tests.factories.user_factory import UserFactory
from src.tests.factories.component_factory import ComponentFactory
from src.tests.factories.cart_line_factory import CartLineFactory
from src.tests.factories.component_category_factory import ComponentCategoryFactory
from decimal import Decimal
from fastapi import HTTPException
from src.tests.conftest import ( client, db_session, setup_factories )
from utils.auth import create_access_token, create_refresh_token, decodeJWT, get_current_user
from src.models import (
    CartLine
)

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali")

@pytest.fixture
def component_category_gpu():
    return ComponentCategoryFactory(
        name="GPU",
        status=0
    )

@pytest.fixture
def component_gpu_4060(component_category_gpu):
    return ComponentFactory(
        name="Zotac RTX 4060",
        product_code="rtx_4060",
        price=7000000,
        component_category_id=component_category_gpu.id,
        status=0
    )

@pytest.fixture
def component_gpu_4070(component_category_gpu):
    return ComponentFactory(
        name="Zotac RTX 4070",
        product_code="rtx_4070",
        price=7000000,
        component_category_id=component_category_gpu.id,
        status=0
    )

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

def test_empty_index(client, db_session, user_sean_ali):
    db_session.commit()

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/cart", headers=headers)
    assert response.status_code == 200

def test_index_with_2_cart_lines(client, db_session, user_sean_ali, cart_line_gpu_4060_sean_ali, cart_line_gpu_4070_sean_ali):
    db_session.commit()
    gpu_4060_id = cart_line_gpu_4060_sean_ali.id
    gpu_4070_id = cart_line_gpu_4070_sean_ali.id

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/cart", headers=headers)
    response_body = response.json()

    gpu_4060 = db_session.query(CartLine).filter(CartLine.id == gpu_4060_id).first()
    gpu_4070 = db_session.query(CartLine).filter(CartLine.id == gpu_4070_id).first()

    assert response_body == {
        'cart': [
            {
                'component_id': gpu_4060.component_id,
                'component_name': gpu_4060.component.name,
                'created_at': gpu_4060.created_at.isoformat(),
                'customer_id': user_sean_ali.id,
                'customer_name': user_sean_ali.fullname,
                'id': gpu_4060.id,
                'quantity': '1.000000',
                'status': 0,
                'updated_at': gpu_4060.updated_at.isoformat()
            },
            {
                'component_id': gpu_4070.component_id,
                'component_name': gpu_4070.component.name,
                'created_at': gpu_4070.created_at.isoformat(),
                'customer_id': user_sean_ali.id,
                'customer_name': user_sean_ali.fullname,
                'id': gpu_4070.id,
                'quantity': '1.000000',
                'status': 0,
                'updated_at': gpu_4070.updated_at.isoformat()
            }
        ]
    }

def test_user_no_auth_index(client, db_session):
    db_session.commit()

    token = 'failed-token'
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/cart", headers=headers)
    assert response.status_code == 401

def test_add_new_item_to_cart(client, db_session, user_sean_ali, component_gpu_4060):
    db_session.commit()

    create_param = {
        'component_id': component_gpu_4060.id,
        'quantity': 2
    }

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.post("/api/cart/add-item", headers=headers, json=create_param)
    assert response.status_code == 200

    new_cart_line = db_session.query(CartLine).order_by(desc(CartLine.id)).first()
    assert new_cart_line.component_id == component_gpu_4060.id
    assert new_cart_line.quantity == 2

def test_add_existing_item_to_cart(client, db_session, user_sean_ali, cart_line_gpu_4060_sean_ali, component_gpu_4060):
    db_session.commit()

    create_param = {
        'component_id': component_gpu_4060.id,
        'quantity': 2
    }

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.post("/api/cart/add-item", headers=headers, json=create_param)
    assert response.status_code == 200
    new_cart_line = db_session.query(CartLine).order_by(desc(CartLine.id)).first()
    assert new_cart_line.component_id == component_gpu_4060.id
    assert new_cart_line.quantity == 3 # 1 + 2

def test_remove_cart_line(client, db_session, user_sean_ali, cart_line_gpu_4060_sean_ali, cart_line_gpu_4070_sean_ali):
    db_session.commit()

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.delete(f"/api/cart/remove-item/{cart_line_gpu_4060_sean_ali.id}", headers=headers)
    assert response.status_code == 204
    deleted_cart_line = db_session.query(CartLine).filter(CartLine.id == cart_line_gpu_4060_sean_ali.id).order_by(desc(CartLine.id)).first()
    assert deleted_cart_line is None