import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from src.tests.factories.user_factory import UserFactory
from decimal import Decimal
from fastapi import HTTPException
from src.tests.conftest import ( client, db_session, setup_factories )
from utils.auth import create_access_token, create_refresh_token, decodeJWT, get_current_user

@pytest.fixture
def user_sean_ali():
    return UserFactory(fullname="Sean Ali")

def test_create_access_token(db_session, user_sean_ali):
    db_session.commit()

    result = create_access_token(user_sean_ali.id, 30)
    assert result.count('.') == 2 # ensure that JWT token has 3 parts separated by dot

def test_create_refresh_token(db_session, user_sean_ali):
    db_session.commit()

    result = create_refresh_token(user_sean_ali.id, 30)
    assert result.count('.') == 2 # ensure that JWT token has 3 parts separated by dot

def test_decode_jwt(db_session, user_sean_ali):
    db_session.commit()

    jwt = create_access_token(user_sean_ali.id, 30)
    decoded = decodeJWT(jwt)
    assert list(decoded.keys()) == ['exp', 'sub']

def test_get_current_user(db_session, user_sean_ali):
    db_session.commit()

    jwt = create_access_token(user_sean_ali.id, 30)
    result = get_current_user(jwt, db_session)
    assert result.fullname == 'Sean Ali'

def test_no_current_user(db_session, user_sean_ali):
    db_session.commit()

    jwt = create_access_token(user_sean_ali.id, -300000)
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(jwt, db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Invalid credentials'


