import pytest
from tests.factories.user_factory import UserFactory
from tests.factories.account_factory import AccountFactory
from tests.factories.payment_factory import PaymentFactory
from tests.conftest import (
    client,
    db_session,
    setup_factories,
    user_sean_ali,
    component_category_gpu
)
from utils.auth import create_access_token, create_refresh_token, decodeJWT, get_current_user
from src.domain.payment.commands.process_payment_command import ProcessPaymentCommand
from decimal import Decimal
from src.domain.payment.handlers.payment_command_handler import PaymentCommandHandler
from src.domain.payment.handlers.bulk_payment_command_handler import BulkPaymentCommandHandler
from unittest.mock import AsyncMock, patch
import httpx
from src.infrastructure.persistence.models.payment import Payment
from src.api.schemas.payment_schemas import PaymentRequestSchema
from src.api.routers.payment import process_bulk_payments_task
from src.infrastructure.persistence.models.import_payment_entry import ImportPaymentEntry
from sqlalchemy import func

@pytest.fixture
def fetch_token_sean_ali(user_sean_ali):
    return create_access_token(user_sean_ali.id, 30)

@pytest.fixture
def account_0(db_session):
    account = AccountFactory(
        account_code=200,
        account_name="Cash",
        account_type=0,
        subtype=0,
        parent_id=None,
        normal_balance=0,
        is_active=True,
        tax_code_id=None
    )

    db_session.add(account)
    db_session.commit()

    return account

@pytest.fixture
def mock_process_payment_command(user_sean_ali, account_0):
    return ProcessPaymentCommand(
        user_id=user_sean_ali.id,
        debit_account_id=account_0.id,
        amount=Decimal("1000000.0"),
        currency="IDR",
        payment_method="cash"
    )

@pytest.fixture
def payment_request_json(user_sean_ali, account_0):
    return {
        "user_id": user_sean_ali.id,
        "account_id": account_0.id,
        "amount": "50.0",
        "currency": "EUR",
        "payment_method": "CASH",
        "description": "Payment for 10 croissants"
    }

@pytest.fixture
def payment_1(user_sean_ali, account_0):
    return PaymentFactory(
        user_id=user_sean_ali.id,
        debit_account_id=account_0.id,
        account_id=account_0.id,
        amount=Decimal("1000000.0"),
        currency="IDR",
        payment_method="cash"
    )

@pytest.fixture
def payment_2(user_sean_ali, account_0):
    return PaymentFactory(
        user_id=user_sean_ali.id,
        debit_account_id=account_0.id,
        account_id=account_0.id,
        amount=Decimal("900000.0"),
        currency="IDR",
        payment_method="cash"
    )

def test_index(
    client,
    db_session,
    fetch_token_sean_ali,
    payment_1,
    payment_2
):
    db_session.commit()
    headers = { "Authorization": f"Bearer {fetch_token_sean_ali}" }

    response = client.get("/api/payments?page=1&item_per_page=50", headers=headers)
    assert response.status_code == 200
    assert len(response.json()['report_body']) == 2
    assert response.json()['report_body'][0]['id'] == payment_2.id
    assert response.json()['report_body'][1]['id'] == payment_1.id

@patch.object(BulkPaymentCommandHandler, 'handle_bulk_payments', new_callable=AsyncMock)
def test_process_bulk_payments_task(
    mock_handle_bulk,
    db_session
):
    db_session.commit()

    response = process_bulk_payments_task('1234567890', '1234567890', 10, [1,2], [1,2])

    payment_entry = db_session.query(ImportPaymentEntry).first()
    assert payment_entry is not None
    assert payment_entry.end_time is None
    assert payment_entry.start_time is not None
    assert payment_entry.total_payments == 10
    assert response == 'Done processing bulk payments'
    mock_handle_bulk.assert_called_once()

@patch.object(process_bulk_payments_task, 'delay', new_callable=AsyncMock)
def test_create_bulk_payment(
    mock_bulk_payment_job,
    client,
    db_session,
    fetch_token_sean_ali
):
    db_session.commit()
    headers = {
        "Authorization": f"Bearer {fetch_token_sean_ali}"
    }

    response = client.post("/api/payments/bulk_create", headers=headers, json={"total_payments": 10})
    assert response.status_code == 202
    assert response.json()['message'] == "Background job is processed"
    assert response.json()['status'] == "accepted"

    mock_bulk_payment_job.assert_called_once()


@patch.object(PaymentCommandHandler, '_validate_user', new_callable=AsyncMock)
@patch.object(PaymentCommandHandler, '_create_sales_journal', new_callable=AsyncMock)
def test_create_payment(
    mock_journal,
    mock_user,
    client,
    db_session,
    fetch_token_sean_ali,
    payment_request_json):
    db_session.commit()

    headers = {
        "Authorization": f"Bearer {fetch_token_sean_ali}"
    }
    response = client.post("/api/payments", headers=headers, json=payment_request_json)
    response_body = response.json()
    assert response_body['currency'] == 'EUR'
    assert response_body['payment_method'] == 'CASH'
    assert response_body['message'] == 'Payment is being processed'
    assert response.status_code == 201

    mock_journal.assert_called_once()
    mock_user.assert_called_once()
        
@patch.object(PaymentCommandHandler, '_validate_user', new_callable=AsyncMock)
@patch.object(PaymentCommandHandler, '_create_sales_journal', new_callable=AsyncMock, side_effect=httpx.HTTPError("Journal service unavailable"))
def test_create_payment_journal_fails(
    mock_journal,
    mock_user,
    client,
    db_session,
    fetch_token_sean_ali,
    payment_request_json
):
    db_session.commit()

    headers = {
        "Authorization": f"Bearer {fetch_token_sean_ali}"
    }
    response = client.post("/api/payments", headers=headers, json=payment_request_json)
    assert response.status_code == 500
    assert 'Payment processing failed: Journal service unavailable' in response.json()['detail']

    mock_journal.assert_called_once()
    mock_user.assert_called_once()
        

@patch.object(PaymentCommandHandler, '_validate_user', new_callable=AsyncMock)
@patch.object(PaymentCommandHandler, '_create_sales_journal', new_callable=AsyncMock, side_effect=httpx.TimeoutException("Request timeout"))
def test_create_payment_network_timeout(
    mock_journal,
    mock_user,
    client,
    db_session,
    fetch_token_sean_ali,
    payment_request_json
):
    db_session.commit()
    initial_count = db_session.query(Payment).count()

    assert initial_count == 0

    headers = {
        "Authorization": f"Bearer {fetch_token_sean_ali}"
    }
    response = client.post("/api/payments", headers=headers, json=payment_request_json)
    assert response.status_code == 500

    mock_journal.assert_called_once()
    mock_user.assert_called_once()

    final_count = db_session.query(Payment).count()
    assert final_count == initial_count