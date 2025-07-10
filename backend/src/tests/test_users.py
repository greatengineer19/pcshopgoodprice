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
    CartLine,
    User
)

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali", role=0)

@pytest.fixture
def user_shinta_gemini():
    return UserFactory(fullname="Shinta Gemini", role=1)


def test_no_user(client):
    response = client.get(f"/api/user?role=seller")
    assert response.status_code == 200

    result = response.json()
    assert result == {'user': {}, 'access_token': '', 'refresh_token': ''}

def test_user_seller(client, db_session, user_sean_ali, user_shinta_gemini):
    db_session.commit()

    response = client.get(f"/api/user?role=seller")
    assert response.status_code == 200

    result = response.json()
    assert result['user'] == {'id': user_sean_ali.id, 'fullname': 'Sean Ali', 'role': 'seller'}
    assert result['access_token'] is not None
    assert result['refresh_token'] is not None

def test_user_buyer(client, db_session, user_sean_ali, user_shinta_gemini):
    db_session.commit()

    response = client.get(f"/api/user?role=buyer")
    assert response.status_code == 200

    result = response.json()
    assert result['user'] == {'id': user_shinta_gemini.id, 'fullname': 'Shinta Gemini', 'role': 'buyer'}
    assert result['access_token'] is not None
    assert result['refresh_token'] is not None