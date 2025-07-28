import pytest
from sqlalchemy import select, desc, func
from tests.factories.user_factory import UserFactory
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import ( client, db_session, setup_factories )
from utils.password import secure_pwd

def test_password_encoder():
    raw_password = '1234abcd'
    result = secure_pwd(raw_password)
    assert len(result) == 60 # bcrypted
    assert result != raw_password

