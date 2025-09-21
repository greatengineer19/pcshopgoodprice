import pytest
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from decimal import Decimal
from fastapi import HTTPException
from tests.conftest import ( client, db_session, setup_factories, user_sean_ali )
from utils.auth import ( create_access_token )

def test_analyze(client, db_session, user_sean_ali):
    db_session.commit()

    token = create_access_token(user_sean_ali.id, 30)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/purchase_invoices_query_analysis", headers=headers)
    assert response.status_code == 200
    response_body = response.json()

    assert len(response_body['data']) == 11