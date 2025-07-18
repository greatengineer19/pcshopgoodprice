import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from tests.factories.user_factory import UserFactory
from tests.factories.component_factory import ComponentFactory
from tests.factories.cart_line_factory import CartLineFactory
from tests.factories.component_category_factory import ComponentCategoryFactory
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import ( client, db_session, setup_factories )
from utils.auth import ( create_access_token )
from src.models import (
    CartLine,
    User
)

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali", username="admin_seller", role=0)

@pytest.fixture
def user_shinta_gemini():
    return UserFactory(fullname="Shinta Gemini", username="super_buyer", role=1)

def test_no_user_in_show_default(client):
    response = client.get(f"/api/user/show-default")
    assert response.status_code == 404

    result = response.json()
    assert result == {'detail': 'User not found'}

def test_show_default(client, user_sean_ali, user_shinta_gemini):
    response = client.get(f"/api/user/show-default")

    result = response.json()
    assert result['user'] == {'id': user_sean_ali.id, 'fullname': 'Sean Ali', 'role': 'seller'}
    assert result['access_token'] is not None
    assert result['refresh_token'] is not None

def test_no_credentials_and_no_user(client):
    response = client.get(f"/api/user?role=seller")
    assert response.status_code == 401

    result = response.json()
    assert result == {'detail': 'Not authenticated'}

def test_user_seller(client, db_session, user_sean_ali, user_shinta_gemini):
    db_session.commit()

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/user?role=seller", headers=headers)
    assert response.status_code == 200

    result = response.json()
    assert result['user'] == {'id': user_sean_ali.id, 'fullname': 'Sean Ali', 'role': 'seller'}
    assert result['access_token'] is not None
    assert result['refresh_token'] is not None

def test_user_buyer(client, db_session, user_sean_ali, user_shinta_gemini):
    db_session.commit()

    token = create_access_token(user_shinta_gemini.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/user?role=buyer", headers=headers)
    assert response.status_code == 200

    result = response.json()
    assert result['user'] == {'id': user_shinta_gemini.id, 'fullname': 'Shinta Gemini', 'role': 'buyer'}
    assert result['access_token'] is not None
    assert result['refresh_token'] is not None

def test_user_by_invalid_token(client, db_session, user_sean_ali, user_shinta_gemini):
    db_session.commit()

    token = "invalid"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/user", headers=headers)
    assert response.status_code == 200

    result = response.json()
    assert result['user'] == {'id': user_sean_ali.id, 'fullname': 'Sean Ali', 'role': 'seller'}
    assert result['access_token'] is not None
    assert result['refresh_token'] is not None