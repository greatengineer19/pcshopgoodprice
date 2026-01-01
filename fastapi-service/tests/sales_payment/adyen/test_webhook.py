import pytest
from sqlalchemy import select, desc, func
from tests.factories.user_factory import UserFactory
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import ( client, db_session, setup_factories )
from utils.password import secure_pwd

def test_notifications(client):
    return
    # response = client.post("/api/sales-payment/adyen/webhooks/notifications")

